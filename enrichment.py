"""
enrichment.py — 為 scanner 結果增加歷史脈絡與深度分析

提供兩個功能：
1. add_oi_delta(df): 為每張合約加上「過去 7 天 OI 變化」欄位
2. generate_deep_cards(df, top_n=5): 為 Top N 標的生成深度分析卡片
   - OI 累積變化（過去 7/14/30 天）
   - IV term structure（不同到期日的 IV 對比）

設計原則：
- 只用本地 data/*.csv 算 OI 變化（零 API 成本）
- 只對 Top N 標的呼叫 yfinance 抓 IV term structure
- 失敗時優雅降級（不中斷主 scanner）
"""
import os
import glob
import pandas as pd
import yfinance as yf
import time
import random
from datetime import datetime, timedelta

DATA_DIR = "data"


# ==========================================
# Part 1: OI Δ7d 欄位（讀本地 CSV）
# ==========================================
def load_historical_csv(days_back):
    """
    載入 N 天前的 CSV（如果該日剛好無數據，往前推一天再試）
    回傳 DataFrame 或 None
    """
    today = datetime.now()
    for offset in range(days_back, days_back + 3):  # 容忍 +0/+1/+2 天的偏移（週末沒交易）
        target_date = (today - timedelta(days=offset)).strftime('%Y-%m-%d')
        path = os.path.join(DATA_DIR, f"{target_date}.csv")
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                return df, target_date
            except Exception:
                continue
    return None, None


def add_oi_delta(df):
    """
    為 df 加上 'OI_d7' 欄位：當前 OI - 7 天前同合約的 OI
    
    比對 key：(Stock, Expiry, Strike)
    若找不到歷史紀錄，OI_d7 顯示為 OI 本身（代表「新增倉位」）
    """
    hist_df, hist_date = load_historical_csv(days_back=7)
    
    if hist_df is None:
        print("⚠️ 找不到 7 天前的 CSV，OI Δ7d 標示為「N/A」")
        df['OI_d7'] = None
        return df, None
    
    # 建立歷史 OI 查詢字典
    hist_lookup = {}
    for _, row in hist_df.iterrows():
        key = (row['Stock'], str(row['Expiry']), float(row['Strike']))
        hist_lookup[key] = int(row.get('OpenInterest', 0))
    
    # 計算 delta
    def get_delta(row):
        key = (row['Stock'], str(row['Expiry'])[:10], float(row['Strike']))
        prev_oi = hist_lookup.get(key)
        current_oi = int(row['OpenInterest'])
        if prev_oi is None:
            return current_oi  # 全新合約 → delta = 當前 OI
        return current_oi - prev_oi
    
    df['OI_d7'] = df.apply(get_delta, axis=1)
    return df, hist_date


def format_oi_delta(val):
    """格式化 OI delta 顯示：+1234 / -567 / N/A"""
    if val is None or pd.isna(val):
        return "N/A"
    val = int(val)
    if val > 0:
        return f"+{val:,}"
    elif val < 0:
        return f"{val:,}"
    else:
        return "0"


# ==========================================
# Part 2: Top N 標的深度卡片
# ==========================================
def get_top_tickers(df, top_n=5):
    """
    從 df 中挑出 Top N 標的（Score 加總最高的不同 ticker）
    避免同一個 ticker 出現多次
    """
    # 按 ticker 計算總分（排除 GAMBLE 區）
    valid = df[df['Action'] != 'GAMBLE'].copy()
    ticker_scores = valid.groupby('Stock').agg(
        total_score=('Score', 'sum'),
        max_score=('Score', 'max'),
        contract_count=('Score', 'count'),
        total_volume=('Volume', 'sum'),
    ).sort_values(by=['max_score', 'total_score'], ascending=[False, False])
    
    return ticker_scores.head(top_n).index.tolist()


def fetch_iv_term_structure(symbol):
    """
    抓取一個標的的 IV term structure
    回傳 dict: {expiry_date: atm_iv_pct}
    
    【v2 修正】
    舊版：抓前 6 個到期日 → 全擠在近月（週選太密）
    新版：智慧選擇不同時間範圍的到期日（近月/中月/遠月/LEAPS）
    """
    try:
        tk = yf.Ticker(symbol)
        info = tk.info
        spot = info.get('currentPrice') or info.get('regularMarketPrice')
        if not spot:
            hist = tk.history(period='5d')
            if len(hist) > 0:
                spot = hist['Close'].iloc[-1]
        if not spot:
            return None, None
        
        all_expiries = tk.options if tk.options else []
        if not all_expiries:
            return None, spot
        
        # 智慧選擇：依距離今日的天數，挑選代表性到期日
        # 目標：~14 天 / ~30 天 / ~60 天 / ~120 天 / ~250 天 / ~500 天
        today = datetime.now()
        target_dtes = [14, 30, 60, 120, 250, 500]
        
        # 計算每個 expiry 的 DTE
        expiry_dtes = []
        for exp in all_expiries:
            try:
                exp_dt = datetime.strptime(exp, '%Y-%m-%d')
                dte = (exp_dt - today).days
                if dte > 0:
                    expiry_dtes.append((exp, dte))
            except Exception:
                continue
        
        # 對每個目標 DTE，找最接近的實際到期日
        selected_expiries = []
        used = set()
        for target in target_dtes:
            if not expiry_dtes:
                break
            # 找離 target 最近的 expiry
            closest = min(expiry_dtes, key=lambda x: abs(x[1] - target))
            if closest[0] not in used:
                selected_expiries.append(closest[0])
                used.add(closest[0])
        
        # 對每個選定的到期日抓 ATM call IV
        term_structure = {}
        for exp in selected_expiries:
            try:
                chain = tk.option_chain(exp)
                calls = chain.calls
                if len(calls) == 0:
                    continue
                calls = calls.copy()
                calls['distance'] = (calls['strike'] - spot).abs()
                atm = calls.nsmallest(1, 'distance').iloc[0]
                iv = atm.get('impliedVolatility', 0) * 100
                if iv > 0:
                    term_structure[exp] = round(iv, 1)
                time.sleep(random.uniform(0.2, 0.4))
            except Exception:
                continue
        
        return term_structure, spot
    except Exception as e:
        print(f"  ⚠️ {symbol} IV 抓取失敗：{e}")
        return None, None


def calc_oi_accumulation(symbol, today_df):
    """
    計算該標的 Top 合約的 OI 累積變化（過去 7/14/30 天）
    
    【v2 修正】
    舊版：直接加總所有合約 OI → 因為 CSV 只記錄高分合約，加總沒意義
    新版：只看「同一支股票今天分數最高的 5 張合約」，比對歷史 CSV 裡的同合約 OI
    """
    result = {}
    
    # 取得該 ticker 今天分數最高的 5 張合約作為「代表合約」
    symbol_today = today_df[today_df['Stock'] == symbol].sort_values(
        by='Score', ascending=False
    ).head(5)
    
    if len(symbol_today) == 0:
        return {'d7': None, 'd14': None, 'd30': None}
    
    # 今天這 5 張合約的總 OI
    today_oi_sum = symbol_today['OpenInterest'].sum()
    
    # 建立合約 key 集合
    contract_keys = set()
    for _, row in symbol_today.iterrows():
        key = (row['Stock'], str(row['Expiry'])[:10], float(row['Strike']))
        contract_keys.add(key)
    
    for label, days in [('d7', 7), ('d14', 14), ('d30', 30)]:
        hist_df, _ = load_historical_csv(days_back=days)
        if hist_df is None:
            result[label] = None
            continue
        
        # 從歷史 CSV 找這 5 張合約對應的 OI
        prev_oi_sum = 0
        found_any = False
        for _, h_row in hist_df.iterrows():
            h_key = (h_row['Stock'], str(h_row['Expiry'])[:10], float(h_row['Strike']))
            if h_key in contract_keys:
                prev_oi_sum += int(h_row.get('OpenInterest', 0))
                found_any = True
        
        if found_any:
            result[label] = int(today_oi_sum - prev_oi_sum)
        else:
            # 如果歷史中完全沒這些合約，視為「全新建倉」
            result[label] = int(today_oi_sum)
    
    return result


def format_term_structure(term_structure):
    """把 IV term structure 格式化成易讀字串"""
    if not term_structure:
        return "*（無 IV 資料）*"
    
    items = []
    for exp, iv in sorted(term_structure.items()):
        # 簡化日期顯示
        try:
            dt = datetime.strptime(exp, '%Y-%m-%d')
            exp_short = dt.strftime('%b\'%y')  # May'26
        except Exception:
            exp_short = exp
        items.append(f"{exp_short}: {iv:.1f}%")
    
    return " / ".join(items)


def detect_iv_skew_signal(term_structure):
    """
    偵測 IV term structure 的訊號：
    - 短月 IV 特別高 → 短期事件預期（財報、新聞）
    - 中月 IV 特別高 → 該月有預期事件
    - 平緩 → 沒明顯事件
    """
    if not term_structure or len(term_structure) < 2:
        return ""
    
    sorted_items = sorted(term_structure.items())
    ivs = [iv for _, iv in sorted_items]
    
    max_iv = max(ivs)
    max_idx = ivs.index(max_iv)
    avg_iv = sum(ivs) / len(ivs)
    
    if max_iv > avg_iv * 1.15:
        if max_idx == 0:
            return f"⚡ 短月 IV 突出 ({max_iv:.0f}%)，市場預期近期有事件"
        elif max_idx == len(ivs) - 1:
            return f"📈 長月 IV 最高 ({max_iv:.0f}%)，長期不確定性高"
        else:
            peak_exp = sorted_items[max_idx][0]
            return f"🎯 IV 峰值在 {peak_exp} ({max_iv:.0f}%)，可能對應特定事件"
    return ""


def generate_deep_card(symbol, df, hist_date=None):
    """為單一標的生成深度分析卡片"""
    md = f"### 🎯 {symbol}\n\n"
    
    # 取得該標的的合約資料
    symbol_contracts = df[df['Stock'] == symbol].sort_values(by='Score', ascending=False)
    contract_count = len(symbol_contracts)
    total_vol = symbol_contracts['Volume'].sum()
    total_oi = symbol_contracts['OpenInterest'].sum()
    
    # === OI 累積變化（用合約級比對）===
    oi_changes = calc_oi_accumulation(symbol, df)
    
    md += "**📊 OI 累積建倉**\n\n"
    if any(v is not None for v in oi_changes.values()):
        parts = []
        for label, days in [('d7', '7 天'), ('d14', '14 天'), ('d30', '30 天')]:
            val = oi_changes.get(label)
            if val is not None:
                sign = '+' if val > 0 else ''
                parts.append(f"{days}: {sign}{val:,}")
            else:
                parts.append(f"{days}: N/A")
        md += "- " + " / ".join(parts) + "\n"
    else:
        md += "- *（歷史資料不足）*\n"
    md += f"- 今日掃描到 {contract_count} 條合約，總成交 {total_vol:,}，總 OI {total_oi:,}\n\n"
    
    # === IV Term Structure ===
    md += "**📈 IV Term Structure**\n\n"
    term_structure, spot = fetch_iv_term_structure(symbol)
    if term_structure:
        md += f"- 標的現價：${spot:.2f}\n"
        md += f"- IV 曲線：{format_term_structure(term_structure)}\n"
        signal = detect_iv_skew_signal(term_structure)
        if signal:
            md += f"- {signal}\n"
    else:
        md += "- *（IV 資料抓取失敗）*\n"
    md += "\n"
    
    # === Top 3 合約 ===
    md += "**🔝 Top 3 異動合約**\n\n"
    top3 = symbol_contracts.head(3)
    if len(top3) > 0:
        md += "| 到期 | 履約 | 價格 | OI | Vol | 標籤 | 分數 |\n"
        md += "|---|---|---|---|---|---|---|\n"
        for _, row in top3.iterrows():
            exp = str(row['Expiry'])[:10]
            md += f"| {exp} | ${row['Strike']:.0f} | ${row['Ask']:.2f} | {int(row['OpenInterest']):,} | {int(row['Volume']):,} | {row['Tags']} | {row['Score']} |\n"
    md += "\n"
    
    return md


def generate_deep_cards(df, top_n=5):
    """為 Top N 標的生成深度分析區塊"""
    top_tickers = get_top_tickers(df, top_n=top_n)
    if not top_tickers:
        return ""
    
    md = f"\n## 🔬 Top {len(top_tickers)} 標的深度分析\n\n"
    md += "> 結合本地 OI 歷史 + 即時 IV term structure，判斷是否真的在「累積建倉」、是否有「事件預期」\n\n"
    
    for symbol in top_tickers:
        print(f"  🔬 生成 {symbol} 深度卡片...", flush=True)
        try:
            card = generate_deep_card(symbol, df)
            md += card
        except Exception as e:
            md += f"### {symbol}\n*（生成失敗：{e}）*\n\n"
    
    return md
