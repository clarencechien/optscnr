"""
tlt_radar.py — TLT 全套避險訊號雷達

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
import os
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
        # 現價
        hist = tk.history(period='5d')
        current_price = float(hist['Close'].iloc[-1])
        
        # 過去 60 天波動範圍
        hist_60d = tk.history(period='3mo')
        price_60d_high = float(hist_60d['High'].max())
        price_60d_low = float(hist_60d['Low'].min())
        avg_volume = float(hist_60d['Volume'].mean())
        recent_volume = float(hist_60d['Volume'].tail(10).mean())
        
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
    
    md = "\n## 📉 TLT 避險雷達\n\n"
    md += f"**避險溫度**: {temp}/100 {label} — {msg}\n\n"
    
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


def main():
    print(f"📉 TLT 避險雷達啟動: {datetime.now().strftime('%Y-%m-%d')}")
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    df, meta = get_tlt_data()
    if df is None:
        print("❌ 無法取得 TLT 資料")
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
