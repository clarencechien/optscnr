import pandas as pd
import yfinance as yf
import requests
import os
import io
import time
import random
from datetime import datetime, timedelta

import json

from enrichment import (
    add_oi_delta, 
    format_oi_delta, 
    generate_deep_cards,
)

def load_auto_watch():
    """從 data/auto_watch.json 載入每週更新的候選池"""
    path = os.path.join(DATA_DIR, "auto_watch.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get('tickers', [])
    except Exception as e:
        print(f"⚠️ auto_watch 載入失敗：{e}")
        return []

def load_catalyst_today():
    """從 data/catalyst_today.json 載入今日催化劑股"""
    path = os.path.join(DATA_DIR, "catalyst_today.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get('tickers', [])
    except Exception as e:
        print(f"⚠️ catalyst 載入失敗：{e}")
        return []
        
# ==========================================
# 1. 設定與目標 (Configuration)
# ==========================================
DATA_DIR = "data"
GITHUB_USER = "clarencechien" 
REPO_NAME = "optscnr"      
BRANCH = "main"

TICKER_CATEGORIES = {
    'BIG_CAPS': ['TSLA', 'NVDA', 'AMD', 'MSFT', 'GOOG', 'MSTR', 'AAPL', 'IBIT', 'COIN', 'PLTR', 'SHOP', 'ANET', 'INTC'],
    'SMALL_CAPS': [
        'SMCI', 'OKLO', 'VST', 'RKLB', 'ASTS', 'IONQ', 'UPST', 'SOFI', 'DKNG', 
        'IREN', 'NBIS', 'NEWT', 'COSM', 'ACRV', 'U', 'PATH', 'ROKU', 'HOOD', 
        'TDOC', 'ZM', 'XYZ', 'OPEN', 'CRSP', 'NTLA', 'BEAM', 'PACB', 'TXG', 
        'VCYT', 'HIMS', 'KTOS', 'ONDS', 'LUNR', 'JOBY', 'ACHR', 'SMR', 'NNE', 'VRT', 'CRWV'
    ]
}

# TARGET_TICKERS = TICKER_CATEGORIES['BIG_CAPS'] + TICKER_CATEGORIES['SMALL_CAPS']

RULE_CONFIG = {
    'VOL_SPIKE_RATIO': 2.5,  # 點火倍數門檻
    'BIG_CAPS_THRESHOLD':  {'OI': 10000, 'VOL': 2500, 'PRICE': 30.0},
    'SMALL_CAPS_THRESHOLD': {'OI': 1500, 'VOL': 400, 'PRICE': 6.0}
}

# ==========================================
# 2. 資料抓取 (yfinance Engine)
# ==========================================
def get_target_dates():
    """生成理想的目標日期，後續會與 yfinance 真實存在的日期取交集"""
    dates = set()
    today = datetime.now()
    
    for i in range(2):
        target = today + timedelta(days=(4 - today.weekday() + 7*i) % 7)
        dates.add(target.strftime('%Y-%m-%d'))

    for i in range(6):
        first_day = (today.replace(day=1) + timedelta(days=32*i)).replace(day=1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)
        third_friday = first_friday + timedelta(days=14)
        if third_friday >= today:
            dates.add(third_friday.strftime('%Y-%m-%d'))

    for year in [today.year + 1, today.year + 2]:
        for month in [1, 6]:
            first_day = datetime(year, month, 1)
            first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)
            dates.add((first_friday + timedelta(days=14)).strftime('%Y-%m-%d'))

    return sorted(list(dates))

def fetch_yesterday_data_from_github():
    """
    優先讀本地歷史 CSV（最穩），fallback 到 GitHub raw
    """
    # 嘗試本地 1-5 天前的 CSV（週末/假日可能要往前找）
    for days_back in range(1, 6):
        target_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        local_path = os.path.join(DATA_DIR, f"{target_date}.csv")
        if os.path.exists(local_path):
            try:
                df = pd.read_csv(local_path)
                print(f"📅 從本地載入 {target_date} 的數據（{len(df)} 筆），啟動動能比對。")
                return df
            except Exception as e:
                print(f"⚠️ 本地 {target_date}.csv 讀取失敗：{e}")
                continue
    
    # 本地 latest.csv 試試
    local_latest = os.path.join(DATA_DIR, "latest.csv")
    if os.path.exists(local_latest):
        try:
            df = pd.read_csv(local_latest)
            print(f"📅 從本地載入 latest.csv（{len(df)} 筆），啟動動能比對。")
            return df
        except Exception:
            pass
    
    # 最後才走 GitHub raw（保留作為遠端 fallback）
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{DATA_DIR}/latest.csv"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            print("📅 從 GitHub raw 載入歷史數據，啟動動能比對。")
            return pd.read_csv(io.StringIO(res.text))
    except Exception:
        pass
    
    print("⚠️ 無法載入歷史數據，降級為盲測模式（所有合約都會缺「🚀點火」標籤）。")
    return None

# ==========================================
# 3. 規則引擎 (Rule Engine)
# ==========================================
def apply_rules(row, prev_data=None):
    tags = []
    action = "HOLD"
    score = 0
    
    symbol, price, oi, vol = row['Stock'], row['Ask'], row['OpenInterest'], row['Volume']
    expiry, strike = row['Expiry'], row['Strike']
    iv = row.get('IV', 0.0)
    dte = row.get('DTE', 0)
    
    cfg = RULE_CONFIG['SMALL_CAPS_THRESHOLD'] if symbol in TICKER_CATEGORIES['SMALL_CAPS'] else RULE_CONFIG['BIG_CAPS_THRESHOLD']
    p_limit = cfg['PRICE'] * (2.0 if dte > 180 else 1.0)
    
    # 基本防護：太貴或沒人玩的直接濾掉
    if price > p_limit or oi < (cfg['OI'] * 0.5):
        return "", "HOLD", 0

    is_gamble = (dte < 5)
    if is_gamble:
        tags.append("🎲末日結算")
        score -= 2

    # A: 莊家掃貨 (Vol/OI Ratio)
    vol_oi_ratio = vol / oi if oi > 0 else 0
    if vol_oi_ratio > 1.2 and vol > cfg['VOL']:
        tags.append("🚨異常掃貨")
        score += 5
        action = "STRONG_BUY"

    # B: 動能點火 (涵蓋新舊倉爆量)
    ignition = False
    if prev_data is not None and not prev_data.empty:
        prev_row = prev_data[(prev_data['Stock'] == symbol) & (prev_data['Expiry'] == expiry) & (prev_data['Strike'] == strike)]
        if not prev_row.empty:
            prev_vol = prev_row.iloc[0]['Volume']
            if prev_vol > 0 and (vol / prev_vol) >= RULE_CONFIG['VOL_SPIKE_RATIO']:
                tags.append(f"🚀點火({vol/prev_vol:.1f}x)")
                score += 3
                ignition = True
        else:
            if vol > cfg['VOL'] and vol > (oi * 0.2):
                tags.append("🆕新倉暴量")
                score += 3
                ignition = True
    else:
        if vol > cfg['VOL'] and vol > (oi * 0.2):
            tags.append("🚀突發暴量")
            score += 2
            ignition = True

    # C: IV 避險 (真實 IV 判斷)
    if iv > 150:
        tags.append("⚠️IV頂峰")
        score -= 3

    # D: 屬性標籤
    is_leaps = False
    is_smoke = False
    if dte > 300: 
        tags.append("🔭LEAPS"); score += 1; is_leaps = True
    elif price < 1.0: 
        tags.append("🚬菸屁股"); score += 1; is_smoke = True
        
    if oi > 30000: 
        tags.append("🔥萬人塚"); score += 2

    if action != "STRONG_BUY" and ignition and (is_leaps or is_smoke):
        action = "BUY_WATCH"
        score += 2

    if is_gamble and action in ["STRONG_BUY", "BUY_WATCH"]:
        action = "GAMBLE"

    return " ".join(tags), action, score

# ==========================================
# 4. 報表生成 (Report Generation)
# ==========================================
# ==========================================
# 4. 報表生成 (Report Generation)
# ==========================================
def generate_report(df):
    # === 新增：呼叫 enrichment ===
    print("\n🔬 開始計算 enrichment...")
    df, hist_date = add_oi_delta(df)
    print(f"  ✅ OI Δ7d 已計算 (vs {hist_date})")
    
    # 載入動態來源（用於來源標籤）
    auto_watch = set(load_auto_watch())
    catalyst = set(load_catalyst_today())
    
    def source_tag(symbol):
        if symbol in catalyst: return "📰催化劑"
        elif symbol in auto_watch: return "🔭候選"
        return ""
    
    md = "# 🚬 每日妖股獵殺報表 (Scanner 3.1 / yf Engine)\n\n"
    md += f"**掃描時間**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
    
    # 在最上方附上動態來源摘要
    if catalyst:
        md += f"**📰 今日催化劑股**: {', '.join(sorted(catalyst))}\n\n"
    if auto_watch:
        md += f"**🔭 本週候選池**: {', '.join(sorted(auto_watch))}\n\n"
    
    df['Expiry'] = pd.to_datetime(df['Expiry'])
    
    def format_view(sub_df):
        view = sub_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'OI_d7', 'Volume', 'IV', 'Tags', 'Score']].copy()
        view['Expiry'] = view['Expiry'].dt.strftime('%Y-%m-%d')
        view['IV'] = view['IV'].apply(lambda x: f"{x:.1f}%")
        # 新增：格式化 OI_d7
        view['OI_d7'] = view['OI_d7'].apply(format_oi_delta)
        view['Tags'] = view.apply(
            lambda r: f"{source_tag(r['Stock'])} {r['Tags']}".strip(),
            axis=1
        )
        view.columns = ['代號', '到期日', '履約價', '價格', '持倉(OI)', 'Δ7d', '成交(Vol)', 'IV', '標籤', '分數']
        return view

    md += "## 🏆 TL;DR 總結 (精選狙擊名單)\n"
    md += "> 策略：過濾掉結算日雜訊，直擊 Score >= 8 的核心異動。\n\n"
    tldr_df = df[(df['Score'] >= 8) & (df['Action'] != 'GAMBLE')].sort_values(by=['Score', 'Volume'], ascending=[False, False]).head(10)
    if not tldr_df.empty:
        md += format_view(tldr_df).to_markdown(index=False) + "\n\n"
    else:
        md += "*今日無高分狙擊標的。*\n\n"

    action_order = ['STRONG_BUY', 'BUY_WATCH', 'GAMBLE', 'HOLD']
    for action in action_order:
        sub_df = df[df['Action'] == action]
        if sub_df.empty: continue
            
        if action == 'STRONG_BUY' or action == 'BUY_WATCH':
            icon = "🚨" if action == 'STRONG_BUY' else "👀"
            title_action = "核彈級異動 (STRONG_BUY)" if action == 'STRONG_BUY' else "重點觀察 (BUY_WATCH)"
            md += f"## {icon} {title_action}\n\n"
            
            leaps_mask = sub_df['DTE'] > 120
            leaps_df = sub_df[leaps_mask].copy()
            short_df = sub_df[~leaps_mask].copy()
            
            if not leaps_df.empty:
                md += "### 🔭 遠期埋伏 (LEAPS > 120天)\n"
                md += "> 策略：時間換空間，跟隨聰明錢長期囤貨 (按分數與持倉排序)。\n\n"
                leaps_df = leaps_df.sort_values(by=['Score', 'OpenInterest'], ascending=[False, False])
                md += format_view(leaps_df).to_markdown(index=False) + "\n\n"

            if not short_df.empty:
                md += "### 🚀 短期波段 (Short Term < 120天)\n"
                md += "> 策略：波段點火，關注資金流向 (排除 DTE<5，按分數與成交排序)。\n\n"
                short_df = short_df.sort_values(by=['Score', 'Volume'], ascending=[False, False])
                md += format_view(short_df).to_markdown(index=False) + "\n\n"
                
        elif action == 'GAMBLE':
            md += f"## 🎲 末日賭博專區 (DTE < 5)\n"
            md += "> 警告：極端短線結算，高機率為造市商平倉雜訊，若要玩請當樂透買。\n\n"
            sub_df = sub_df.sort_values(by=['Volume'], ascending=[False]).head(15)
            md += format_view(sub_df).to_markdown(index=False) + "\n\n"
            
        else:
            md += f"## 🚬 常規雷達 (HOLD)\n"
            sub_df = sub_df.sort_values(by=['Score', 'Volume'], ascending=[False, False]).head(20)
            md += format_view(sub_df).to_markdown(index=False) + "\n\n"
            
    # === 新增：Top 5 深度卡片（放在報表最下方） ===
    print("\n🔬 開始生成深度卡片...")
    try:
        deep_section = generate_deep_cards(df, top_n=5)
        md += deep_section
    except Exception as e:
        print(f"  ⚠️ 深度卡片生成失敗：{e}")
        md += f"\n## 🔬 深度分析\n*（生成失敗：{e}）*\n"
                
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("📝 README.md 報表已生成。")
    
# ==========================================
# 5. 主執行程序 (Main)
# ==========================================
def main():
    print(f"🔥 啟動 Scanner 3.1 (yfinance Engine): {datetime.now().strftime('%Y-%m-%d')}")
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    # 載入動態清單
    auto_watch = load_auto_watch()
    catalyst = load_catalyst_today()
    
    # 合併並去重，保持順序（核心池優先）
    seen = set()
    target_tickers = []
    for t in (TICKER_CATEGORIES['BIG_CAPS'] 
              + TICKER_CATEGORIES['SMALL_CAPS'] 
              + auto_watch 
              + catalyst):
        if t not in seen:
            seen.add(t)
            target_tickers.append(t)
    
    print(f"🎯 核心池: {len(TICKER_CATEGORIES['BIG_CAPS']) + len(TICKER_CATEGORIES['SMALL_CAPS'])} 檔")
    print(f"🔭 自動候選: {len(auto_watch)} 檔")
    print(f"📰 催化劑: {len(catalyst)} 檔")
    print(f"🎯 掃描總數（去重後）: {len(target_tickers)} 檔")
    
    prev_df = fetch_yesterday_data_from_github()
    results = []
    target_dates = get_target_dates()
    
    for symbol in target_tickers:
        print(f"🔍 {symbol}...", end=" ", flush=True)
        
        try:
            tk = yf.Ticker(symbol)
            available_dates = tk.options
        except Exception:
            print("❌ (無法取得期權鏈)")
            continue
            
        if not available_dates:
            print("💨 (無期權)")
            continue

        # 核心優化：只抓取與標的可用日期重疊的目標日，省去大量 404 請求
        valid_target_dates = [d for d in target_dates if d in available_dates]
        found_any = False
        
        for d_str in valid_target_dates:
            try:
                # 取得該日期的 Call 期權鏈
                chain = tk.option_chain(d_str)
                df = chain.calls
                
                # yfinance 欄位映射
                rename_map = {
                    'strike': 'Strike',
                    'lastPrice': 'Ask', # yf 有時 ask 為 0，用 lastPrice 當參考基準最穩
                    'openInterest': 'OpenInterest',
                    'volume': 'Volume',
                    'impliedVolatility': 'IV'
                }
                
                df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
                
                # 確保數值型態
                for col in ['Ask', 'OpenInterest', 'Volume', 'Strike']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                # IV 轉回百分比 (yf 給的是小數，例如 1.25 -> 125%)
                if 'IV' in df.columns:
                    df['IV'] = pd.to_numeric(df['IV'], errors='coerce').fillna(0.0) * 100
                else:
                    df['IV'] = 0.0

                # 應用規則
                for _, row in df[df['OpenInterest'] > 500].iterrows():
                    dte = (datetime.strptime(d_str, "%Y-%m-%d") - datetime.now()).days
                    d_row = {
                        'Stock': symbol, 'Expiry': d_str, 'Strike': row['Strike'], 'Ask': row['Ask'], 
                        'OpenInterest': int(row['OpenInterest']), 'Volume': int(row['Volume']), 
                        'IV': row['IV'], 'DTE': dte
                    }
                    tags, action, score = apply_rules(d_row, prev_df)
                    if score > 0 or action != "HOLD":
                        d_row.update({'Tags': tags, 'Action': action, 'Score': score})
                        results.append(d_row)
                        found_any = True
                
                # 保護機制：強制停頓，避免被 Yahoo 封鎖
                time.sleep(random.uniform(0.3, 0.8))
                
            except Exception as e:
                pass
                
        print("✅" if found_any else "💨")

    if results:
        final_df = pd.DataFrame(results).sort_values(by=['Score', 'Volume'], ascending=[False, False])
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # from enrichment import add_oi_delta
        # final_df, _ = add_oi_delta(final_df)  # 提前計算
        
        final_df.to_csv(f"{DATA_DIR}/{today_str}.csv", index=False)
        final_df.to_csv(f"{DATA_DIR}/latest.csv", index=False)
        print(f"\n💾 數據已存檔 (共 {len(final_df)} 筆訊號)。")
        
        generate_report(final_df)
    else:
        print("\n💀 今日全軍覆沒，沒戲。")

if __name__ == "__main__":
    main()
