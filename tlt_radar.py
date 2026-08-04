"""
tlt_radar.py — TLT 全套避險訊號雷達

【v2.4 修正】（PATCH 2026-08-04：部分失敗仍輸出綠燈）
- 2026-08-03「模式 B」：價格抓成功（$82.25）但選擇權鏈失敗 → 三分項全 0 →
  「0/100 🟢 平靜」假綠燈，v2.2 的 nan 防線攔不住（沒有 nan）
- 修法：多層有效性檢查 tlt_data_is_valid()（價格/鏈存在性/OI 崩塌指紋/Skew 恰 0），
  任一層失敗 → 輸出「本區無效」報告（保留有效價格＋上次有效讀數），
  且不寫 history → 「本週已成功即跳過」不成立 → 每日排程持續重試
- 偵測的是「資料不存在」不是「分數為 0」——真平靜的三分項可以同時為 0（T5 防線）

【v2.2 修正】（2026-07-31 handoff P0-1：nan 綠燈事故）
- 7/27 抓取失敗 → current_price=nan → 三分項全 0 → 輸出「0/100 🟢平靜」
  整週被誤讀為「市場無避險需求」，與實際市況（油價破 $100、10Y 創高）完全相反。
- 修法：
  1. nan / 失敗防呆——任一關鍵值算不出來，一律視為抓取失敗，不輸出分數
  2. 抓取失敗自動重試 3 次（指數退避）
  3. 仍失敗 → 報告改寫「⚠️ 無資料」區塊（附上次成功讀數 + TLT現價/10Y 簡易 fallback），
     絕不輸出溫度燈號——「沒算到」不等於「平靜」
  4. 成功報告標示「擷取於 X 日，下次更新 X+7 日」，避免週間重複輸出被誤讀為連續確認

每週日跑一次，給出三個獨立訊號的綜合判斷：
1. Put 巨鯨：價外 Put 的 Notional 異常 + Vol/OI Ratio
2. IV Skew：Put IV vs Call IV 的偏斜程度（panic 指標）
3. OI 週比累積：對比上週快照，看 Put OI 是否在快速建倉

設計理念：
- 不是「找下一個 Put 來買」（那是 directional 樂透）
- 是「現在 TLT regime 對 Put 部位有沒有利」（給已有部位的人看 dashboard）
- 輸出綜合「避險溫度」(Hedging Temperature) 0-100 分

輸出：
- data/tlt_radar.json（給主 scanner 讀，但 TLT 不會進主 scanner，這份 JSON 純存檔）
- README.md 上方獨立區塊「📉 TLT 避險雷達」
- 用於追蹤週度演變
"""
import yfinance as yf
import pandas as pd
import json
import math
import os
import time
import logging
from datetime import datetime, timedelta

OUTPUT_PATH = "data/tlt_radar.json"
HISTORY_PATH = "data/tlt_radar_history.csv"

# 壓掉 yfinance 噪音
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# === 篩選參數 ===
CONFIG = {
    'TICKER': 'TLT',
    'MIN_NOTIONAL_WHALE': 500_000,      # 巨鯨單最小名目金額（$50 萬）
    'MIN_VOLUME_WHALE': 100,            # 巨鯨單最小成交量
    'PUT_OTM_PCT': 0.05,                # 價外 5%+ 才算避險買盤
    'MIN_OI_FOR_IV': 50,                # IV 計算要求最低 OI（過濾 stale quote）
}


def get_tlt_data():
    """抓 TLT 現價 + 完整選擇權鏈
    
    【v2 修正】
    舊版用 tk.options[:6] 抓前 6 個到期日，但 TLT 有週選會全部擠在近月
    新版改用智慧選擇：~30d / ~60d / ~90d / ~180d / ~365d / ~500d
    這樣 IV term structure 才能看出真實的時間結構
    """
    tk = yf.Ticker(CONFIG['TICKER'])
    
    try:
        # 現價（v2.2：dropna + nan 防呆——nan 流下去會變成「0/100 🟢平靜」的假訊號）
        hist = tk.history(period='5d')
        closes = hist['Close'].dropna()
        if closes.empty:
            print("❌ TLT 現價全為 nan / 無資料")
            return None, None
        current_price = float(closes.iloc[-1])

        # 過去 60 天波動範圍
        hist_60d = tk.history(period='3mo')
        price_60d_high = float(hist_60d['High'].dropna().max())
        price_60d_low = float(hist_60d['Low'].dropna().min())
        avg_volume = float(hist_60d['Volume'].dropna().mean())
        recent_volume = float(hist_60d['Volume'].dropna().tail(10).mean())

        # 任一關鍵值 nan / 非正數 → 一律當抓取失敗，不讓垃圾值流進計分
        for v in (current_price, price_60d_high, price_60d_low):
            if not v or v <= 0 or math.isnan(v):
                print("❌ TLT 價格資料含 nan / 異常值")
                return None, None

    except Exception as e:
        print(f"❌ 無法取得 TLT 現價：{e}")
        return None, None
    
    try:
        all_exps = tk.options
    except Exception as e:
        print(f"❌ 無法取得選擇權鏈：{e}")
        return None, None
    
    if not all_exps:
        return None, None
    
    # 智慧選擇代表性到期日（避開週選擠壓）
    today = datetime.now()
    # 加入 240 天讓 ~8 個月的 LEAPS（典型 hedge 配置）也能被覆蓋
    target_dtes = [30, 60, 90, 180, 240, 365, 500]
    
    expiry_dtes = []
    for exp in all_exps:
        try:
            exp_dt = datetime.strptime(exp, '%Y-%m-%d')
            dte = (exp_dt - today).days
            if dte >= 14:  # 跳過 14 天內到期（IV 太不穩）
                expiry_dtes.append((exp, dte))
        except Exception:
            continue
    
    if not expiry_dtes:
        return None, None
    
    selected_exps = []
    used = set()
    for target in target_dtes:
        closest = min(expiry_dtes, key=lambda x: abs(x[1] - target))
        if closest[0] not in used:
            selected_exps.append(closest[0])
            used.add(closest[0])
    
    print(f"🔍 選定代表性到期日（DTE）：")
    for exp in selected_exps:
        dte = next((d for e, d in expiry_dtes if e == exp), 0)
        print(f"     {exp} (DTE {dte})")
    
    all_chains = []
    for exp in selected_exps:
        try:
            opt = tk.option_chain(exp)
            calls = opt.calls.copy()
            puts = opt.puts.copy()
            calls['Type'] = 'Call'
            puts['Type'] = 'Put'
            chain = pd.concat([calls, puts], ignore_index=True)
            chain['Expiration'] = exp
            all_chains.append(chain)
        except Exception:
            continue
    
    if not all_chains:
        return None, None
    
    df = pd.concat(all_chains, ignore_index=True)
    # 確保數值欄位
    for col in ['volume', 'openInterest', 'lastPrice', 'impliedVolatility', 'strike']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 過濾 IV 異常值（太低代表 stale quote，太高代表流動性差）
    df_iv_clean = df.copy()
    # IV < 5% 或 > 200% 視為異常，標記但不刪
    df_iv_clean['IV_suspicious'] = (
        (df_iv_clean['impliedVolatility'] < 0.05) | 
        (df_iv_clean['impliedVolatility'] > 2.0)
    )
    
    # Notional value
    df_iv_clean['Notional'] = df_iv_clean['volume'] * df_iv_clean['lastPrice'] * 100
    df_iv_clean['VolOIRatio'] = df_iv_clean['volume'] / (df_iv_clean['openInterest'] + 1)
    
    meta = {
        'current_price': current_price,
        'price_60d_high': price_60d_high,
        'price_60d_low': price_60d_low,
        'avg_volume': avg_volume,
        'recent_volume': recent_volume,
        'distance_from_60d_low': (current_price / price_60d_low - 1) * 100,
        'distance_from_60d_high': (current_price / price_60d_high - 1) * 100,
    }
    
    return df_iv_clean, meta


# ==========================================
# 訊號 1：Put 巨鯨偵測
# ==========================================
def detect_put_whales(df, current_price):
    """找出真實的避險巨鯨買盤"""
    otm_threshold = current_price * (1 - CONFIG['PUT_OTM_PCT'])
    
    whales = df[
        (df['Type'] == 'Put') &
        (df['Notional'] > CONFIG['MIN_NOTIONAL_WHALE']) &
        (df['volume'] > CONFIG['MIN_VOLUME_WHALE']) &
        (df['strike'] < otm_threshold) &
        (df['strike'] > current_price * 0.7)  # 不要太極端的尾部，那是賣方 wing 配對
    ].sort_values(by='Notional', ascending=False)
    
    # 區分「新建倉」vs「平倉」
    # Vol > OI = 今日成交超過全部歷史持倉 = 高機率新建倉
    whales = whales.copy()
    whales['IsNewPosition'] = whales['VolOIRatio'] > 1.0
    
    return whales


# ==========================================
# 訊號 2：IV Skew 偵測
# ==========================================
def calc_iv_skew(df, current_price):
    """計算 Put-Call IV 偏斜
    
    【v2 修正】
    過濾 IV < 5% 的 stale quote
    過濾 IV > 200% 的雜訊
    要求至少 OI > 50 才採用（避免無流動性合約）
    
    回傳：
    - skew_summary: dict, 每個到期日的 skew 值
    - overall_skew: 整體加權平均 skew
    """
    skew_summary = {}
    
    for exp in df['Expiration'].unique():
        sub = df[df['Expiration'] == exp]
        
        # ATM IV（價內外各取 5%）
        atm_range = (current_price * 0.95, current_price * 1.05)
        atm_calls = sub[
            (sub['Type'] == 'Call') &
            (sub['strike'] >= atm_range[0]) & 
            (sub['strike'] <= atm_range[1]) &
            (sub['impliedVolatility'] >= 0.05) &  # 過濾異常低 IV
            (sub['impliedVolatility'] <= 2.0) &   # 過濾異常高 IV
            (sub['openInterest'] >= 50)            # 要求最低流動性
        ]
        
        # OTM Put（25-delta 大約價外 5-12%）
        otm_puts = sub[
            (sub['Type'] == 'Put') &
            (sub['strike'] >= current_price * 0.88) &
            (sub['strike'] <= current_price * 0.95) &
            (sub['impliedVolatility'] >= 0.05) &
            (sub['impliedVolatility'] <= 2.0) &
            (sub['openInterest'] >= 50)
        ]
        
        if len(atm_calls) == 0 or len(otm_puts) == 0:
            continue
        
        atm_call_iv = atm_calls['impliedVolatility'].mean()
        otm_put_iv = otm_puts['impliedVolatility'].mean()
        skew = otm_put_iv - atm_call_iv
        
        skew_summary[exp] = {
            'atm_call_iv': round(atm_call_iv * 100, 1),
            'otm_put_iv': round(otm_put_iv * 100, 1),
            'skew': round(skew * 100, 2),
            'atm_oi_total': int(atm_calls['openInterest'].sum()),
            'otm_put_oi_total': int(otm_puts['openInterest'].sum()),
        }
    
    if not skew_summary:
        return {}, 0.0
    
    skews = [v['skew'] for v in skew_summary.values()]
    overall_skew = sum(skews) / len(skews) / 100  # 轉回小數
    
    return skew_summary, overall_skew


# ==========================================
# 訊號 3：OI 週比累積
# ==========================================
def load_last_week_oi():
    """讀上週的快照，比對 OI 變化"""
    if not os.path.exists(HISTORY_PATH):
        return None
    try:
        hist = pd.read_csv(HISTORY_PATH)
        # 找最近一筆且超過 5 天前的紀錄
        hist['date'] = pd.to_datetime(hist['date'])
        cutoff = datetime.now() - timedelta(days=5)
        old_records = hist[hist['date'] < cutoff]
        if len(old_records) == 0:
            return None
        return old_records.iloc[-1].to_dict()
    except Exception:
        return None


def detect_oi_buildup(df):
    """偵測 Put OI 週度累積"""
    puts = df[df['Type'] == 'Put']
    
    # 分桶：近月 Put（DTE < 90）vs 遠月 Put（DTE > 90）
    today = datetime.now()
    
    near_term_oi = 0
    far_term_oi = 0
    
    for _, row in puts.iterrows():
        try:
            exp_dt = datetime.strptime(row['Expiration'], '%Y-%m-%d')
            dte = (exp_dt - today).days
            if dte < 90:
                near_term_oi += row['openInterest']
            else:
                far_term_oi += row['openInterest']
        except Exception:
            continue
    
    last_week = load_last_week_oi()
    
    if last_week is None:
        return {
            'near_term_oi_total': int(near_term_oi),
            'far_term_oi_total': int(far_term_oi),
            'near_term_change_pct': None,
            'far_term_change_pct': None,
            'has_baseline': False,
        }
    
    near_change = (near_term_oi / last_week.get('near_term_oi_total', near_term_oi) - 1) * 100
    far_change = (far_term_oi / last_week.get('far_term_oi_total', far_term_oi) - 1) * 100
    
    return {
        'near_term_oi_total': int(near_term_oi),
        'far_term_oi_total': int(far_term_oi),
        'near_term_change_pct': round(near_change, 1),
        'far_term_change_pct': round(far_change, 1),
        'has_baseline': True,
    }


# ==========================================
# 綜合避險溫度
# ==========================================
def calc_hedging_temperature(whales_df, overall_skew, oi_change):
    """三個訊號合成「避險溫度」(0-100)
    
    0-30   = 平靜（市場無壓力）
    30-50  = 中性
    50-70  = 緊張（適合維持避險）
    70-100 = 恐慌（可能是頂部訊號或可賣 Put 收 IV crush）
    """
    score = 0
    components = {}
    
    # === 訊號 1：Put 巨鯨（最多 30 分）===
    if len(whales_df) == 0:
        whale_score = 0
    else:
        new_position_whales = whales_df[whales_df['IsNewPosition']]
        # 每張新建倉巨鯨 5 分，最多 30 分
        whale_score = min(30, len(new_position_whales) * 5)
    components['whales'] = whale_score
    score += whale_score
    
    # === 訊號 2：IV Skew（最多 40 分）===
    if overall_skew < 0.02:
        skew_score = 0   # 沒有恐慌
    elif overall_skew < 0.05:
        skew_score = 15
    elif overall_skew < 0.08:
        skew_score = 25
    elif overall_skew < 0.12:
        skew_score = 35
    else:
        skew_score = 40  # 極端 panic
    components['skew'] = skew_score
    score += skew_score
    
    # === 訊號 3：OI 累積（最多 30 分）===
    if not oi_change['has_baseline']:
        oi_score = 0  # 第一次跑沒基準
    else:
        # 近月 + 遠月變化都納入
        near_chg = oi_change.get('near_term_change_pct') or 0
        far_chg = oi_change.get('far_term_change_pct') or 0
        avg_chg = (near_chg + far_chg) / 2
        
        if avg_chg < 5:
            oi_score = 0
        elif avg_chg < 15:
            oi_score = 10
        elif avg_chg < 30:
            oi_score = 20
        else:
            oi_score = 30
    components['oi_buildup'] = oi_score
    score += oi_score
    
    return min(100, score), components


def temperature_to_message(temp):
    """避險溫度轉敘述"""
    if temp < 20:
        return "🟢 平靜", "市場無明顯避險需求，TLT Put 部位可能 IV 被壓縮"
    elif temp < 40:
        return "🟡 中性", "正常波動範圍，沒有強烈訊號"
    elif temp < 60:
        return "🟠 升溫", "Put 端開始累積，留意趨勢延續"
    elif temp < 80:
        return "🔴 緊張", "明顯避險需求，Put 部位賠率改善（IV 有 carry）"
    else:
        return "🚨 恐慌", "可能接近頂部訊號，反向考慮賣 Put 收 IV crush"


# ==========================================
# 多層資料有效性檢查（v2.4，PATCH 2026-08-04：部分失敗仍輸出綠燈）
# ==========================================
def tlt_data_is_valid(meta, skew_summary, overall_skew, oi_change):
    """回傳 (是否有效, 失效原因)。任一層失敗即判定無效。

    背景：2026-08-03 出現「模式 B」部分失敗——價格與歷史抓成功（$82.25），
    選擇權鏈抓失敗（Skew 表 0 列、Skew 恰 0.00%、OI -100%/-99.9%）→
    三分項各自回 0 → 加總 0 → 輸出「0/100 🟢 平靜」假綠燈。
    v3.11 的 nan 防線攔不住（這次沒有 nan）。

    設計原則（patch §5）：偵測「資料不存在」，而不是「分數為 0」——
    真正平靜的市場三分項可能同時為 0（Put 巨鯨 0/30 尤其常見），
    用分數當判準會把「真平靜」誤判成「抓取失敗」，方向剛好相反。
    """
    # 層 1：價格 / 歷史（模式 A 指紋；get_tlt_data 已擋，這裡便宜地再驗一次）
    price = meta.get('current_price')
    if price is None or (isinstance(price, float) and math.isnan(price)) or price <= 0:
        return False, "TLT 價格抓取失敗"
    dist_low = meta.get('distance_from_60d_low')
    if dist_low is None or (isinstance(dist_low, float) and math.isnan(dist_low)):
        return False, "TLT 歷史資料抓取失敗"

    # 層 2：選擇權鏈存在性（模式 B 的主要指紋）
    if not skew_summary:
        return False, "TLT 選擇權鏈為空（IV Skew 表 0 列）"

    # 層 3：OI 崩塌指紋——TLT 未平倉量不可能歸零，-99% 以下必為鏈缺失
    if oi_change.get('has_baseline'):
        near = oi_change.get('near_term_change_pct')
        far = oi_change.get('far_term_change_pct')
        if (near is not None and near <= -99.0) or (far is not None and far <= -99.0):
            return False, f"TLT OI 變化異常（近月 {near}% / 遠月 {far}%，鏈缺失指紋）"

    # 層 4：Skew 恰為 0——真實 skew 幾乎不可能剛好 0.0000，此值等同「無資料」
    if overall_skew == 0.0:
        return False, "TLT IV Skew 為 0.00%（等同無資料）"

    return True, ""


def write_partial_invalid_report(reason, meta):
    """部分失敗時的渲染（patch §4.2）：
    1. 不顯示溫度/燈號/三分項（不得輸出 0/100 🟢）
    2. 顯示上次有效讀數（使用者才知道最後可信的 regime）
    3. 價格若有效仍顯示——$82.25 貼近 60 日低點本身有資訊，不連帶丟掉
    不寫 history → 「本週已成功」不成立 → 每日排程明天自動重試。
    """
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    last = load_last_good_reading()

    md = "\n## 📉 TLT 避險雷達\n\n"
    md += f"⚠️ **本區無效** — {reason}\n\n"
    md += f"擷取時間：{now_str}\n\n"
    if last:
        label, _ = temperature_to_message(last['temp'])
        md += f"上次有效讀數：{last['temp']}/100 {label}（{last['date']}）\n\n"
    price = meta.get('current_price')
    if price and not (isinstance(price, float) and math.isnan(price)):
        md += f"**今日 TLT 收盤**: ${price:.2f} "
        md += f"(距 60d 低 {meta['distance_from_60d_low']:+.1f}% / "
        md += f"距 60d 高 {meta['distance_from_60d_high']:.1f}%)\n"
        md += "_價格資料有效，可單獨參考；regime 分數本週無效（每日排程會自動重試）。_\n\n"

    with open("data/tlt_radar_report.md", 'w', encoding='utf-8') as f:
        f.write(md)

    output = {
        'updated_at': datetime.now().isoformat(),
        'status': 'partial_failure',
        'reason': reason,
        'tlt_price': price,
        'last_good': last,
    }
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"⚠️ 部分失敗（{reason}）——已寫「本區無效」報告，不記 history（明日自動重試）")


# ==========================================
# 抓取失敗報告（v2.2 P0-1）
# ==========================================
def load_last_good_reading():
    """從歷史 CSV 讀最後一次成功的溫度讀數，供失敗報告參考用"""
    if not os.path.exists(HISTORY_PATH):
        return None
    try:
        hist = pd.read_csv(HISTORY_PATH)
        if hist.empty:
            return None
        last = hist.iloc[-1]
        return {'date': str(last['date']), 'temp': int(last['hedging_temp'])}
    except Exception:
        return None


def fetch_fallback_snapshot():
    """簡易 fallback：只抓 TLT 現價 + 10Y 殖利率（^TNX），
    讓失敗報告至少留一點可判讀的外部錨點。抓不到就算了。"""
    fb = {}
    try:
        closes = yf.Ticker('TLT').history(period='5d')['Close'].dropna()
        if not closes.empty and not math.isnan(float(closes.iloc[-1])):
            fb['tlt_price'] = float(closes.iloc[-1])
    except Exception:
        pass
    try:
        tnx = yf.Ticker('^TNX').history(period='5d')['Close'].dropna()
        if not tnx.empty and not math.isnan(float(tnx.iloc[-1])):
            fb['us10y_pct'] = float(tnx.iloc[-1]) / 10.0  # ^TNX 報價 = 殖利率×10
    except Exception:
        pass
    return fb


def write_failure_report():
    """抓取失敗時：不輸出溫度、不輸出燈號——「沒算到」不等於「平靜」。
    報告改寫失敗聲明 + 上次成功讀數 + 簡易 fallback。"""
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    last = load_last_good_reading()
    fb = fetch_fallback_snapshot()

    md = "\n## 📉 TLT 避險雷達\n\n"
    md += f"⚠️ **無資料（抓取失敗於 {now_str}，已重試 3 次）**\n\n"
    md += "- 本次未輸出避險溫度——抓取失敗 ≠ 市場平靜，**請勿把本區當環境訊號**。\n"
    if last:
        md += f"- 上次成功讀數：{last['temp']}/100（擷取於 {last['date']}）｜僅供參考，非當前市況。\n"
    if 'tlt_price' in fb:
        md += f"- Fallback：TLT 現價 ${fb['tlt_price']:.2f}（簡易替代讀數，非完整訊號）\n"
    if 'us10y_pct' in fb:
        md += f"- Fallback：10Y 殖利率 {fb['us10y_pct']:.2f}%（簡易替代讀數，非完整訊號）\n"
    md += "- 替代判讀：改看 10Y 殖利率、油價、VIX 等外部資料。\n\n"

    with open("data/tlt_radar_report.md", 'w', encoding='utf-8') as f:
        f.write(md)

    output = {
        'updated_at': datetime.now().isoformat(),
        'status': 'fetch_failed',
        'last_good': last,
        'fallback': fb,
    }
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print("⚠️ 已寫入「無資料」失敗報告（不輸出溫度/燈號）")


# ==========================================
# 主程式
# ==========================================
def save_to_history(meta, oi_change, temp):
    """寫入週度歷史快照"""
    record = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'current_price': meta['current_price'],
        'near_term_oi_total': oi_change['near_term_oi_total'],
        'far_term_oi_total': oi_change['far_term_oi_total'],
        'hedging_temp': temp,
    }
    
    if os.path.exists(HISTORY_PATH):
        df_hist = pd.read_csv(HISTORY_PATH)
        df_hist = pd.concat([df_hist, pd.DataFrame([record])], ignore_index=True)
    else:
        df_hist = pd.DataFrame([record])
    
    df_hist.to_csv(HISTORY_PATH, index=False)


def generate_report(meta, whales, skew_summary, overall_skew, oi_change, temp, components):
    """生成 markdown 報告區塊（會被主 scanner 整合進 README）"""
    label, msg = temperature_to_message(temp)
    
    # v2.2：標示擷取日期——TLT 為週更設計，主 scanner 每天都會把這份報告貼進 README，
    # 沒標日期會被誤讀為「連續四天確認」。
    fetched_date = datetime.now().strftime('%Y-%m-%d')
    next_update = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    md = "\n## 📉 TLT 避險雷達\n\n"
    md += f"**避險溫度**: {temp}/100 {label} — {msg}\n"
    md += f"_（擷取於 {fetched_date}，下次更新 {next_update}；本雷達為週更，週間看到的都是同一份讀數）_\n\n"
    
    md += f"**TLT 現價**: ${meta['current_price']:.2f} "
    md += f"(距 60d 低 +{meta['distance_from_60d_low']:.1f}% / "
    md += f"距 60d 高 {meta['distance_from_60d_high']:.1f}%)\n\n"
    
    # 訊號分數拆解
    md += "### 訊號拆解\n\n"
    md += f"- 🐋 Put 巨鯨：{components['whales']}/30\n"
    md += f"- 📊 IV Skew：{components['skew']}/40（整體 Skew = {overall_skew*100:.2f}%）\n"
    md += f"- 📈 OI 累積：{components['oi_buildup']}/30"
    if oi_change['has_baseline']:
        md += f"（近月 {oi_change['near_term_change_pct']:+.1f}% / 遠月 {oi_change['far_term_change_pct']:+.1f}%）\n"
    else:
        md += "（首次跑，無基準）\n"
    md += "\n"
    
    # Skew Term Structure
    if skew_summary:
        md += "### IV Skew Term Structure\n\n"
        md += "_只採用 OI ≥ 50 的合約，過濾低流動性 stale quote_\n\n"
        md += "| 到期 | ATM Call IV | OTM Put IV | Skew | ATM OI | Put OI |\n"
        md += "|---|---|---|---|---|---|\n"
        for exp in sorted(skew_summary.keys())[:6]:
            s = skew_summary[exp]
            skew_marker = ""
            if s['skew'] > 8:
                skew_marker = " 🔴"
            elif s['skew'] > 5:
                skew_marker = " 🟠"
            elif s['skew'] < 0:
                skew_marker = " 🔵"
            md += f"| {exp} | {s['atm_call_iv']:.1f}% | {s['otm_put_iv']:.1f}% | {s['skew']:+.2f}%{skew_marker} | {s['atm_oi_total']:,} | {s['otm_put_oi_total']:,} |\n"
        md += "\n"
        
        # 額外提醒：如果某些到期日 ATM Call IV 異常低，可能是資料問題
        suspicious = [exp for exp, s in skew_summary.items() if s['atm_call_iv'] < 8]
        if suspicious:
            md += f"⚠️ **資料品質警告**：到期 {', '.join(suspicious[:3])} 的 ATM Call IV < 8%，可能是流動性差導致的 stale quote，這些 Skew 數字參考即可。\n\n"
    
    # Top 巨鯨單
    if len(whales) > 0:
        md += "### Top 5 Put 巨鯨單\n\n"
        md += "| 到期 | 履約 | 權利金 | Vol | OI | Vol/OI | Notional | 類型 |\n"
        md += "|---|---|---|---|---|---|---|---|\n"
        for _, row in whales.head(5).iterrows():
            position_type = "🆕 新建倉" if row['IsNewPosition'] else "📦 既有"
            md += f"| {row['Expiration']} | ${row['strike']:.0f} | ${row['lastPrice']:.2f} | "
            md += f"{int(row['volume']):,} | {int(row['openInterest']):,} | "
            md += f"{row['VolOIRatio']:.2f} | ${row['Notional']/1000:.0f}k | {position_type} |\n"
        md += "\n"
    else:
        md += "_今日無 Put 巨鯨單。_\n\n"
    
    return md


def week_already_succeeded():
    """v2.3：檢查本 ISO 週是否已有成功讀數（價格有效的 history 列）。

    設計（handoff #2 P0-1）：排程改每日跑，但「該週第一次成功抓取」後其餘日子跳過——
    不硬編週幾，週六失敗隔日自動再試，直到成功或該週結束。regime 計算仍是週更。
    """
    if not os.path.exists(HISTORY_PATH):
        return False
    try:
        hist = pd.read_csv(HISTORY_PATH)
        if hist.empty:
            return False
        last = hist.iloc[-1]
        price = pd.to_numeric(last.get('current_price'), errors='coerce')
        if pd.isna(price) or price <= 0:
            return False  # 最後一列是失敗殘留，不算成功
        last_date = datetime.strptime(str(last['date']), '%Y-%m-%d')
        now = datetime.now()
        return last_date.isocalendar()[:2] == now.isocalendar()[:2]
    except Exception:
        return False


def main():
    print(f"📉 TLT 避險雷達啟動: {datetime.now().strftime('%Y-%m-%d')}")

    if not os.path.exists('data'):
        os.makedirs('data')

    # v2.3：本週已成功 → 跳過（每日排程只是 retry 機制，regime 仍為週更）
    if week_already_succeeded():
        print("✅ 本週已有成功讀數，跳過（每日排程僅作為當週失敗的自動重試）")
        return

    # v2.2：retry 3 次（指數退避）——TLT 是週更，單點失敗會瞎掉一整週
    df, meta = None, None
    for attempt in range(3):
        df, meta = get_tlt_data()
        if df is not None and meta is not None:
            break
        wait = 2 ** (attempt + 1)
        print(f"⚠️ 第 {attempt + 1} 次抓取失敗，{wait}s 後重試...")
        time.sleep(wait)

    if df is None or meta is None:
        print("❌ 重試後仍無法取得 TLT 資料")
        write_failure_report()
        return
    
    print(f"💎 TLT 現價: ${meta['current_price']:.2f}")
    print(f"   60d 波動: ${meta['price_60d_low']:.2f} - ${meta['price_60d_high']:.2f}")
    
    # 三大訊號
    print("\n🔍 偵測 Put 巨鯨...")
    whales = detect_put_whales(df, meta['current_price'])
    print(f"   找到 {len(whales)} 張 Put 巨鯨單（其中 {sum(whales['IsNewPosition'])} 張為新建倉）")
    
    print("\n📊 計算 IV Skew...")
    skew_summary, overall_skew = calc_iv_skew(df, meta['current_price'])
    print(f"   整體 Skew: {overall_skew*100:.2f}%（{len(skew_summary)} 個到期日）")
    
    print("\n📈 偵測 OI 週度累積...")
    oi_change = detect_oi_buildup(df)
    if oi_change['has_baseline']:
        print(f"   近月 Put OI 週比: {oi_change['near_term_change_pct']:+.1f}%")
        print(f"   遠月 Put OI 週比: {oi_change['far_term_change_pct']:+.1f}%")
    else:
        print(f"   首次跑，無歷史基準（近月 OI 總計: {oi_change['near_term_oi_total']:,}）")
    
    # === v2.4：多層有效性檢查（部分失敗不得輸出溫度/燈號）===
    valid, reason = tlt_data_is_valid(meta, skew_summary, overall_skew, oi_change)
    if not valid:
        write_partial_invalid_report(reason, meta)
        return

    # 綜合溫度
    temp, components = calc_hedging_temperature(whales, overall_skew, oi_change)
    label, msg = temperature_to_message(temp)
    print(f"\n🌡️  避險溫度: {temp}/100 {label}")
    print(f"   {msg}")
    
    # 寫 JSON（給 main scanner 讀取）
    output = {
        'updated_at': datetime.now().isoformat(),
        'tlt_price': meta['current_price'],
        'hedging_temperature': temp,
        'components': components,
        'overall_skew_pct': round(overall_skew * 100, 2),
        'oi_change': oi_change,
        'whale_count': len(whales),
        'new_position_whales': int(sum(whales['IsNewPosition'])),
    }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    # 寫 markdown 報告（給 README 整合用）
    md = generate_report(meta, whales, skew_summary, overall_skew, oi_change, temp, components)
    with open("data/tlt_radar_report.md", 'w', encoding='utf-8') as f:
        f.write(md)
    
    # 寫歷史快照
    save_to_history(meta, oi_change, temp)
    
    print(f"\n💾 JSON 已寫入 {OUTPUT_PATH}")
    print(f"💾 Markdown 報告: data/tlt_radar_report.md")
    print(f"💾 歷史快照: {HISTORY_PATH}")


if __name__ == "__main__":
    main()
