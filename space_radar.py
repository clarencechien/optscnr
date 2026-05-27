"""
space_radar.py — SPCX (SpaceX) IPO 三池策略支援雷達

SpaceX 6/12 上市，代號 SPCX。這個 radar 不替你決定買什麼，
而是餵你三池策略各自需要的訊號：

【40% GTC 池】首日 VWAP 當錨點，追蹤 -5%/-15%/-25% 掛單距離
【10% Options 池】IV 冷卻溫度計，IV 狂熱期擋住，冷卻後才放行
【50% DCA 池】純儀表板：成本線 + 均線，不給任何買賣訊號

另外盯太空同游股（RKLB/ASTS/RDW...），看 SPCX 上市對它們的虹吸/受惠

階段機：
- 階段 0：SPCX 還沒上市 → 追 IPO 進度
- 階段 1：上市了但沒選擇權 → 記錄 VWAP 錨點 + 盯選擇權上市
- 階段 2：有選擇權但 IV 狂熱 → 累積 IV 歷史，options 池擋住
- 階段 3：IV 冷卻穩定 → options 池放行

輸出：
- data/space_radar.json
- data/space_radar_report.md（附到主 README）
- data/spcx_vwap_anchor.json（首日 VWAP，算一次存著）
- data/spcx_iv_history.csv（IV 時間序列）
- data/spcx_dca_log.json（你的 DCA 紀錄，手動維護）

頻率：每天跑（IPO 後）
"""
import yfinance as yf
import pandas as pd
import json
import os
import logging
from datetime import datetime, timedelta

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# === 設定 ===
TICKER = "SPCX"
IPO_DATE = "2026-06-12"          # 預期掛牌日
PRICING_DATE = "2026-06-11"      # 訂價日

# 太空同游股（觀察 SPCX 上市的虹吸/受惠效應）
SPACE_PEERS = {
    'RKLB': 'Rocket Lab（小型發射，互補型）',
    'ASTS': 'AST SpaceMobile（衛星直連，競爭型）',
    'RDW':  'Redwire（太空製造，部分競爭）',
    'PL':   'Planet Labs（衛星影像，利基）',
    'LUNR': 'Intuitive Machines（登月，部分競爭）',
    'SPIR': 'Spire Global（衛星數據，利基）',
    'BKSY': 'BlackSky（衛星影像，利基）',
}

# IPO proxy 標的（上市後可能 unwind）
IPO_PROXIES = {
    'XOVR': 'ERShares（持有 SpaceX SPV，>40% 部位）',
    'DXYZ': 'Destiny Tech100（SpaceX proxy，溢價交易）',
}

# GTC 池設定
GTC_LEVELS = [-0.05, -0.15, -0.25]   # 三檔掛單
GTC_WEIGHTS = [0.40, 0.35, 0.25]      # 各檔資金比例（總和 40% 池內分配）

# Options 池 IV 門檻
IV_CONFIG = {
    'FRENZY': 0.80,      # IV > 80% = 狂熱期，擋住
    'COOLING': 0.60,     # 60-80% = 冷卻中，觀察
    'CALM': 0.50,        # < 50% = 可評估
    'STABLE_DAYS': 3,    # 連續幾天 < COOLING 才算「穩定」
}

VWAP_ANCHOR_PATH = "data/spcx_vwap_anchor.json"
IV_HISTORY_PATH = "data/spcx_iv_history.csv"
DCA_LOG_PATH = "data/spcx_dca_log.json"
OUTPUT_PATH = "data/space_radar.json"
REPORT_PATH = "data/space_radar_report.md"


def detect_stage():
    """偵測目前在哪個階段
    
    【重要防呆】SPCX 這個代號在 SpaceX 上市前，是一檔叫
    "SPAC and New Issue ETF" 的舊 ETF 在用（已改名 SPCK 但 yfinance 有殘留）。
    所以 IPO 日期（6/12）之前，絕不相信任何 SPCX 報價。
    """
    # 防呆 1：還沒到 IPO 日期，直接回階段 0
    today = datetime.now()
    ipo_dt = datetime.strptime(IPO_DATE, '%Y-%m-%d')
    if today < ipo_dt:
        days_to_ipo = (ipo_dt - today).days
        print(f"⏳ 距 SPCX 上市還有 {days_to_ipo} 天（{IPO_DATE}），維持階段 0")
        print(f"   （註：IPO 前 SPCX 報價是同名舊 ETF，不可信，已忽略）")
        return 0, None, None
    
    tk = yf.Ticker(TICKER)
    
    # 試著抓價格
    try:
        hist = tk.history(period='5d')
        if len(hist) == 0:
            return 0, None, None  # 還沒上市
        current_price = float(hist['Close'].iloc[-1])
    except Exception:
        return 0, None, None
    
    # 防呆 2：驗證這真的是 SpaceX，不是同名 ETF
    # SpaceX 市值兆級，股價不可能是 $22 這種 ETF 價位
    # 用市值或公司名驗證
    try:
        info = tk.info
        long_name = info.get('longName', '') or info.get('shortName', '')
        # SpaceX 的名字應該包含 Space Exploration 或 SpaceX
        if long_name and 'space exploration' not in long_name.lower() \
           and 'spacex' not in long_name.lower():
            print(f"⚠️ SPCX 報價對應的是「{long_name}」，不是 SpaceX，忽略")
            print(f"   （SpaceX 尚未上市或代號尚未生效）")
            return 0, None, None
    except Exception:
        # 抓不到 info，保守起見當還沒上市
        return 0, None, None
    
    # 確認是真 SpaceX 了，檢查有沒有選擇權
    try:
        has_options = bool(tk.options)
    except Exception:
        has_options = False
    
    if not has_options:
        return 1, current_price, None  # 上市但無選擇權
    
    # 有選擇權，算 ATM IV
    atm_iv = get_atm_iv(tk, current_price)
    
    if atm_iv is None:
        return 1, current_price, None
    
    if atm_iv > IV_CONFIG['FRENZY']:
        return 2, current_price, atm_iv  # IV 狂熱
    else:
        return 3, current_price, atm_iv  # IV 冷卻，可評估


def get_atm_iv(tk, current_price):
    """抓最近月份的 ATM IV"""
    try:
        exps = tk.options
        if not exps:
            return None
        # 用第一個有意義的到期日（>14 天）
        today = datetime.now()
        for exp in exps:
            exp_dt = datetime.strptime(exp, '%Y-%m-%d')
            dte = (exp_dt - today).days
            if dte < 14:
                continue
            opt = tk.option_chain(exp)
            calls = opt.calls
            # ATM = 最接近現價的 strike
            calls = calls.copy()
            calls['dist'] = (calls['strike'] - current_price).abs()
            atm = calls.nsmallest(3, 'dist')
            iv = atm['impliedVolatility'].mean()
            if iv > 0:
                return float(iv)
        return None
    except Exception:
        return None


def get_first_day_vwap():
    """算 SPCX 首日 VWAP，存成錨點（只算一次）"""
    if os.path.exists(VWAP_ANCHOR_PATH):
        with open(VWAP_ANCHOR_PATH) as f:
            return json.load(f)
    
    tk = yf.Ticker(TICKER)
    try:
        # 抓首日分鐘資料算 VWAP
        hist = tk.history(period='5d', interval='1d')
        if len(hist) == 0:
            return None
        
        # 首日 = 上市第一天
        first_day = hist.iloc[0]
        # 簡化版 VWAP：用 (H+L+C)/3 當代理
        vwap = (first_day['High'] + first_day['Low'] + first_day['Close']) / 3
        
        anchor = {
            'first_day_date': hist.index[0].strftime('%Y-%m-%d'),
            'first_day_vwap': round(float(vwap), 2),
            'first_day_high': round(float(first_day['High']), 2),
            'first_day_low': round(float(first_day['Low']), 2),
            'first_day_close': round(float(first_day['Close']), 2),
            'computed_at': datetime.now().isoformat(),
        }
        
        with open(VWAP_ANCHOR_PATH, 'w') as f:
            json.dump(anchor, f, indent=2)
        
        return anchor
    except Exception as e:
        print(f"⚠️ VWAP 計算失敗：{e}")
        return None


def calc_gtc_levels(vwap):
    """根據首日 VWAP 算出三檔 GTC 掛單價位"""
    levels = []
    for pct, weight in zip(GTC_LEVELS, GTC_WEIGHTS):
        price = vwap * (1 + pct)
        levels.append({
            'pct': pct,
            'price': round(price, 2),
            'weight': weight,
        })
    return levels


def record_iv_history(atm_iv, current_price):
    """記錄 IV 時間序列"""
    record = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'price': round(current_price, 2),
        'atm_iv': round(atm_iv, 4),
    }
    
    if os.path.exists(IV_HISTORY_PATH):
        df = pd.read_csv(IV_HISTORY_PATH)
        # 同一天只記一次
        df = df[df['date'] != record['date']]
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    else:
        df = pd.DataFrame([record])
    
    df.to_csv(IV_HISTORY_PATH, index=False)
    return df


def check_iv_stable(iv_df):
    """檢查 IV 是否連續幾天 < COOLING（穩定冷卻）"""
    if iv_df is None or len(iv_df) < IV_CONFIG['STABLE_DAYS']:
        return False
    
    recent = iv_df.tail(IV_CONFIG['STABLE_DAYS'])
    return all(recent['atm_iv'] < IV_CONFIG['COOLING'])


def load_dca_log():
    """讀 DCA 紀錄（手動維護的 json）"""
    if not os.path.exists(DCA_LOG_PATH):
        return None
    try:
        with open(DCA_LOG_PATH) as f:
            return json.load(f)
    except Exception:
        return None


def calc_dca_metrics(current_price):
    """算 DCA 成本線 + 均線（純儀表板，不給訊號）"""
    dca_log = load_dca_log()
    
    tk = yf.Ticker(TICKER)
    ma50 = ma200 = None
    try:
        hist = tk.history(period='1y')
        if len(hist) >= 50:
            ma50 = round(float(hist['Close'].tail(50).mean()), 2)
        if len(hist) >= 200:
            ma200 = round(float(hist['Close'].tail(200).mean()), 2)
    except Exception:
        pass
    
    result = {
        'ma50': ma50,
        'ma200': ma200,
        'current_price': round(current_price, 2),
    }
    
    if dca_log and dca_log.get('purchases'):
        purchases = dca_log['purchases']
        total_shares = sum(p['shares'] for p in purchases)
        total_cost = sum(p['shares'] * p['price'] for p in purchases)
        if total_shares > 0:
            avg_cost = total_cost / total_shares
            result['avg_cost'] = round(avg_cost, 2)
            result['total_shares'] = total_shares
            result['total_invested'] = round(total_cost, 2)
            result['current_value'] = round(total_shares * current_price, 2)
            result['unrealized_pnl_pct'] = round((current_price / avg_cost - 1) * 100, 1)
    
    return result


def scan_space_peers():
    """掃太空同游股，看相對 SPCX 的表現"""
    peers_data = []
    for ticker, desc in SPACE_PEERS.items():
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period='1mo')
            if len(hist) < 5:
                continue
            current = float(hist['Close'].iloc[-1])
            month_ago = float(hist['Close'].iloc[0])
            change_1m = (current / month_ago - 1) * 100
            
            # 近 5 日 vs 前期
            recent5 = float(hist['Close'].tail(5).mean())
            prev = float(hist['Close'].head(len(hist)-5).mean()) if len(hist) > 5 else recent5
            change_5d_trend = (recent5 / prev - 1) * 100 if prev else 0
            
            peers_data.append({
                'ticker': ticker,
                'desc': desc,
                'price': round(current, 2),
                'change_1m_pct': round(change_1m, 1),
                'recent_trend_pct': round(change_5d_trend, 1),
            })
        except Exception:
            continue
    
    return peers_data


def generate_report(stage, price, atm_iv, vwap_anchor, gtc_levels, 
                    iv_stable, dca_metrics, peers):
    """生成 markdown 報告"""
    md = "\n## 🚀 SPCX 太空雷達\n\n"
    
    stage_names = {
        0: "階段 0：尚未上市（追 IPO 進度）",
        1: "階段 1：已上市，選擇權尚未推出",
        2: "階段 2：選擇權已上市，IV 狂熱期 🔥",
        3: "階段 3：IV 冷卻，可評估 ✅",
    }
    md += f"**目前階段**：{stage_names.get(stage, '未知')}\n\n"
    
    if stage == 0:
        md += f"SPCX 預計 {IPO_DATE} 掛牌（{PRICING_DATE} 訂價）。上市後本雷達自動啟動。\n\n"
        return md
    
    md += f"**SPCX 現價**：${price:.2f}\n\n"
    
    # === 40% GTC 池 ===
    md += "### 💰 40% GTC 池（首日 VWAP 錨點）\n\n"
    if vwap_anchor:
        md += f"首日 VWAP 錨點：**${vwap_anchor['first_day_vwap']:.2f}** "
        md += f"（{vwap_anchor['first_day_date']}，高 ${vwap_anchor['first_day_high']:.2f} / 低 ${vwap_anchor['first_day_low']:.2f}）\n\n"
        
        if gtc_levels:
            md += "| 檔位 | 掛單價 | 池內權重 | 距現價 | 狀態 |\n"
            md += "|---|---|---|---|---|\n"
            for lv in gtc_levels:
                dist = (price / lv['price'] - 1) * 100
                if price <= lv['price']:
                    status = "✅ 已觸發"
                else:
                    status = f"⏳ 還需跌 {dist:.1f}%"
                md += f"| {lv['pct']*100:.0f}% | ${lv['price']:.2f} | {lv['weight']*100:.0f}% | {dist:+.1f}% | {status} |\n"
            md += "\n"
    else:
        md += "_首日 VWAP 尚未計算（需等上市首日收盤）_\n\n"
    
    # === 10% Options 池 ===
    md += "### 🎰 10% Options 池（IV 冷卻溫度計）\n\n"
    if atm_iv is not None:
        iv_pct = atm_iv * 100
        if atm_iv > IV_CONFIG['FRENZY']:
            iv_status = f"🔥 **狂熱（{iv_pct:.0f}%）— 勿進，IV crush 風險極高**"
        elif atm_iv > IV_CONFIG['COOLING']:
            iv_status = f"🟠 冷卻中（{iv_pct:.0f}%）— 觀察，還太貴"
        elif atm_iv > IV_CONFIG['CALM']:
            iv_status = f"🟡 接近合理（{iv_pct:.0f}%）— 開始留意"
        else:
            iv_status = f"🟢 合理（{iv_pct:.0f}%）— 可評估 directional bet"
        md += f"ATM IV：{iv_status}\n\n"
        
        if iv_stable:
            md += "✅ **IV 已連續穩定冷卻** — options 池可開始評估進場\n\n"
        else:
            md += f"⏳ IV 尚未連續 {IV_CONFIG['STABLE_DAYS']} 天穩定在 {IV_CONFIG['COOLING']*100:.0f}% 以下 — 繼續等\n\n"
    else:
        md += "_選擇權尚未上市，IV 無法計算_\n\n"
    
    # === 50% DCA 池 ===
    md += "### 📊 50% DCA 池（純儀表板，無買賣訊號）\n\n"
    if dca_metrics:
        if dca_metrics.get('avg_cost'):
            md += f"- 你的平均成本：**${dca_metrics['avg_cost']:.2f}**"
            md += f"（{dca_metrics['total_shares']} 股，投入 ${dca_metrics['total_invested']:,.0f}）\n"
            md += f"- 現價：${dca_metrics['current_price']:.2f}"
            md += f"（未實現 {dca_metrics['unrealized_pnl_pct']:+.1f}%）\n"
        else:
            md += "- _尚未開始 DCA，或 spcx_dca_log.json 未維護_\n"
        if dca_metrics.get('ma50'):
            md += f"- SPCX 50 日均線：${dca_metrics['ma50']:.2f}\n"
        if dca_metrics.get('ma200'):
            md += f"- SPCX 200 日均線：${dca_metrics['ma200']:.2f}\n"
        else:
            md += "- 200 日均線：_上市未滿 200 天，尚無_\n"
        md += "\n_提醒：DCA 的力量來自機械化。均線只供事後確認，不作為加減碼依據。_\n\n"
    
    # === 太空同游股 ===
    if peers:
        md += "### 🛰️ 太空同游股（觀察 SPCX 虹吸/受惠）\n\n"
        md += "| 標的 | 現價 | 30天 | 近期趨勢 | 定位 |\n"
        md += "|---|---|---|---|---|\n"
        for p in sorted(peers, key=lambda x: x['change_1m_pct'], reverse=True):
            md += f"| {p['ticker']} | ${p['price']:.2f} | {p['change_1m_pct']:+.1f}% | {p['recent_trend_pct']:+.1f}% | {p['desc']} |\n"
        md += "\n_虹吸觀察：SPCX 上市後，競爭型（ASTS/LUNR）可能被吸乾，利基型（RKLB/PL）可能受惠。_\n\n"
    
    return md


def main():
    print(f"🚀 啟動 SPCX 太空雷達: {datetime.now().strftime('%Y-%m-%d')}")
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # 偵測階段
    stage, price, atm_iv = detect_stage()
    print(f"📍 目前階段：{stage}")
    
    vwap_anchor = None
    gtc_levels = None
    iv_stable = False
    dca_metrics = None
    
    if stage >= 1:
        print(f"💎 SPCX 現價：${price:.2f}")
        # 算首日 VWAP 錨點
        vwap_anchor = get_first_day_vwap()
        if vwap_anchor:
            print(f"⚓ 首日 VWAP 錨點：${vwap_anchor['first_day_vwap']:.2f}")
            gtc_levels = calc_gtc_levels(vwap_anchor['first_day_vwap'])
        # DCA 儀表板
        dca_metrics = calc_dca_metrics(price)
    
    if stage >= 2 and atm_iv is not None:
        print(f"🌡️  ATM IV：{atm_iv*100:.1f}%")
        iv_df = record_iv_history(atm_iv, price)
        iv_stable = check_iv_stable(iv_df)
        print(f"   IV 穩定冷卻：{'✅' if iv_stable else '⏳ 尚未'}")
    
    # 太空同游股（任何階段都掃，IPO 前就能觀察）
    print("🛰️  掃描太空同游股...")
    peers = scan_space_peers()
    print(f"   {len(peers)} 檔")
    
    # 生成報告
    md = generate_report(stage, price, atm_iv, vwap_anchor, gtc_levels,
                         iv_stable, dca_metrics, peers)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(md)
    
    # 寫 JSON
    output = {
        'updated_at': datetime.now().isoformat(),
        'stage': stage,
        'price': price,
        'atm_iv': atm_iv,
        'iv_stable': iv_stable,
        'vwap_anchor': vwap_anchor,
        'gtc_levels': gtc_levels,
        'dca_metrics': dca_metrics,
        'peers': peers,
    }
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n💾 已寫入 {OUTPUT_PATH}")
    print(f"💾 報告：{REPORT_PATH}")


if __name__ == "__main__":
    main()
