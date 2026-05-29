"""
space_radar.py — SPCX (SpaceX) IPO 三池策略支援雷達

SpaceX 6/12 上市，代號 SPCX。這個 radar 不替你決定買什麼，
而是餵你三池策略各自需要的訊號：

【A 核心 DCA 池 60% / $120k】依市值估值錨分批建倉（主力），市值 >2.2T 斷路器
【B 地板預備池 30% / $60k】GTC 掛 1.5T/1.3T/1.1T，承接鎖倉瀑布供給，掛到 12 月中
【C 機動/選擇權池 10% / $20k】IV 崩後才動 LEAPS，否則持現金

另外盯太空同游股（RKLB/ASTS/RDW...），看 SPCX 上市對它們的虹吸/受惠

階段機：
- 階段 0：SPCX 還沒上市 → 追 IPO 進度
- 階段 1：上市了但沒選擇權 → 記錄 VWAP 錨點 + 盯選擇權上市
- 階段 2：有選擇權但 IV 狂熱 → 累積 IV 歷史，options 池擋住
- 階段 3：IV 冷卻穩定 → options 池放行

輸出：
- data/space_radar.json
- data/space_radar_report.md（附到主 README）
- data/spcx_iv_history.csv（IV 時間序列）
- data/spcx_dca_log.json（你的 DCA 紀錄，手動維護）

可變參數：data/spcx_config.json（IPO 日期、股數、各池比例…全在這，改它不用動 code）

頻率：每天跑（IPO 後）

【v8.1 改動】
- 拔除首日 VWAP，改用絕對市值定錨（1.5T/1.3T/1.1T 反推掛單價）
- A 池加入 2.2T 斷路器（市值破頂禁止新資金）
- Options 池加 Gamma Squeeze 預警（PC ratio < 0.2）
- 報告開頭加論點破壞檢查清單（4 個黑天鵝條件）
"""
import yfinance as yf
import pandas as pd
import json
import os
import logging
from datetime import datetime, timedelta

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# === 設定 ===
# 所有「6/11 才定案、可能變動」的參數都集中在 data/spcx_config.json
# code 啟動時讀它；讀不到任一欄位就用下面的內建預設值（防呆）
# 6/11 定價後，只改 json，不用動 code

CONFIG_PATH = "data/spcx_config.json"

# 內建預設值（config 讀不到時的 fallback）
_DEFAULTS = {
    'ticker': 'SPCX',
    'ipo_date': '2026-06-12',
    'pricing_date': '2026-06-11',
    'total_shares_b': 13.0,
    'total_capital': 200_000,
    'pool_a_dca_pct': 0.60,
    'pool_b_floor_pct': 0.30,
    'pool_c_opt_pct': 0.10,
    'dca_tranches': 5,
    'hard_cap_t': 2.2,
    'buy_zone_top_t': 2.0,
    'buy_zone_accel_t': 1.75,
    'b_pool_anchors_t': [1.5, 1.3, 1.1],
    'gtc_weights': [0.40, 0.35, 0.25],
    'greenshoe_off_day': 30,
    'lockup_floor_end_day': 180,
    'pc_ratio_squeeze': 0.20,
    'pc_min_put_vol': 500,
    'iv_frenzy': 0.80,
    'iv_cooling': 0.60,
    'iv_calm': 0.50,
    'iv_stable_days': 3,
}


def load_config():
    """讀 spcx_config.json，缺欄位用 _DEFAULTS 補。讀不到整個檔也不會掛。"""
    cfg = dict(_DEFAULTS)
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                user_cfg = json.load(f)
            # 只覆蓋非 _ 開頭的 key（_ 開頭是註解）
            for k, v in user_cfg.items():
                if not k.startswith('_') and k in _DEFAULTS:
                    cfg[k] = v
            print(f"📋 已讀取 spcx_config.json（IPO 日期：{cfg['ipo_date']}，股數：{cfg['total_shares_b']}B）")
        else:
            print(f"⚠️ 找不到 {CONFIG_PATH}，使用內建預設值")
    except Exception as e:
        print(f"⚠️ config 讀取失敗（{e}），使用內建預設值")
    return cfg


# 載入 config，灌進 module-level 變數（其他函式沿用原本的名字，零改動）
_CFG = load_config()
TICKER = _CFG['ticker']
IPO_DATE = _CFG['ipo_date']
PRICING_DATE = _CFG['pricing_date']
TOTAL_SHARES_B = _CFG['total_shares_b']
TOTAL_CAPITAL = _CFG['total_capital']
POOL_A_DCA_PCT = _CFG['pool_a_dca_pct']
POOL_B_FLOOR_PCT = _CFG['pool_b_floor_pct']
POOL_C_OPT_PCT = _CFG['pool_c_opt_pct']
DCA_TRANCHES = _CFG['dca_tranches']
HARD_CAP_T = _CFG['hard_cap_t']
BUY_ZONE_TOP_T = _CFG['buy_zone_top_t']
BUY_ZONE_ACCEL_T = _CFG['buy_zone_accel_t']
B_POOL_ANCHORS_T = _CFG['b_pool_anchors_t']
GTC_WEIGHTS = _CFG['gtc_weights']
GREENSHOE_OFF_DAY = _CFG['greenshoe_off_day']
LOCKUP_FLOOR_END_DAY = _CFG['lockup_floor_end_day']
PC_RATIO_SQUEEZE = _CFG['pc_ratio_squeeze']
PC_MIN_PUT_VOL = _CFG['pc_min_put_vol']

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

# Options 池 IV 門檻
IV_CONFIG = {
    'FRENZY': _CFG['iv_frenzy'],      # IV > 此值 = 狂熱期，擋住
    'COOLING': _CFG['iv_cooling'],    # 此值以下 = 冷卻中
    'CALM': _CFG['iv_calm'],          # 此值以下 = 可評估
    'STABLE_DAYS': _CFG['iv_stable_days'],  # 連續幾天 < COOLING 才算「穩定」
}

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
        return 0, None, None, None
    
    tk = yf.Ticker(TICKER)
    
    # 試著抓價格
    try:
        hist = tk.history(period='5d')
        if len(hist) == 0:
            return 0, None, None, None  # 還沒上市
        current_price = float(hist['Close'].iloc[-1])
    except Exception:
        return 0, None, None, None
    
    # 防呆 2：驗證這真的是 SpaceX，不是同名 ETF
    try:
        info = tk.info
        long_name = info.get('longName', '') or info.get('shortName', '')
        if long_name and 'space exploration' not in long_name.lower() \
           and 'spacex' not in long_name.lower():
            print(f"⚠️ SPCX 報價對應的是「{long_name}」，不是 SpaceX，忽略")
            print(f"   （SpaceX 尚未上市或代號尚未生效）")
            return 0, None, None, None
    except Exception:
        return 0, None, None, None
    
    # 確認是真 SpaceX 了，檢查有沒有選擇權
    try:
        has_options = bool(tk.options)
    except Exception:
        has_options = False
    
    if not has_options:
        return 1, current_price, None, None  # 上市但無選擇權
    
    # 有選擇權，算 ATM IV + PC ratio
    atm_iv, pc_ratio = get_options_metrics(tk, current_price)
    
    if atm_iv is None:
        return 1, current_price, None, None
    
    if atm_iv > IV_CONFIG['FRENZY']:
        return 2, current_price, atm_iv, pc_ratio  # IV 狂熱
    else:
        return 3, current_price, atm_iv, pc_ratio  # IV 冷卻，可評估


def get_options_metrics(tk, current_price):
    """抓 ATM IV + Put/Call Volume Ratio（Gamma Squeeze 偵測）
    
    回傳 (atm_iv, pc_ratio)
    
    PC ratio bug 防呆：
    - SPCX 初期 Put 流動性差，total_put_vol 可能接近 0
    - 若 Put 量 < PC_MIN_PUT_VOL，pc_ratio 回 None（不可信，不觸發警報）
    """
    try:
        exps = tk.options
        if not exps:
            return None, None
        
        today = datetime.now()
        for exp in exps:
            exp_dt = datetime.strptime(exp, '%Y-%m-%d')
            if (exp_dt - today).days < 14:
                continue
            
            opt = tk.option_chain(exp)
            calls = opt.calls.copy()
            puts = opt.puts.copy()
            
            # ATM IV
            calls['dist'] = (calls['strike'] - current_price).abs()
            atm = calls.nsmallest(3, 'dist')
            atm_iv = float(atm['impliedVolatility'].mean())
            if atm_iv <= 0:
                continue
            
            # PC Ratio（軋空狂熱偵測）
            total_call_vol = float(calls['volume'].fillna(0).sum())
            total_put_vol = float(puts['volume'].fillna(0).sum()) if not puts.empty else 0
            
            # Put 流動性防呆：量太低不算（避免 0/大數 = 假警報）
            if total_put_vol < PC_MIN_PUT_VOL or total_call_vol < 1:
                pc_ratio = None
            else:
                pc_ratio = total_put_vol / total_call_vol
            
            return atm_iv, pc_ratio
        
        return None, None
    except Exception:
        return None, None


def calc_gtc_levels():
    """v8.1: 根據絕對市值反推 B 池 GTC 掛單價位，與開盤價/VWAP 完全無關
    
    價格 = 市值(兆) × 1000 / 總股數(十億)
    這樣不管 SPCX 開盤暴漲暴跌，你的掛單都定錨在「我認為值多少」
    """
    levels = []
    for mc_t, weight in zip(B_POOL_ANCHORS_T, GTC_WEIGHTS):
        price = (mc_t * 1000) / TOTAL_SHARES_B
        levels.append({
            'target_mc_t': mc_t,
            'price': round(price, 2),
            'weight': weight,
        })
    return levels


def price_to_mc_t(price):
    """價格反推市值（兆）"""
    return (price * TOTAL_SHARES_B) / 1000


def days_since_ipo():
    """距上市第幾天（上市前回負數）"""
    today = datetime.now()
    ipo_dt = datetime.strptime(IPO_DATE, '%Y-%m-%d')
    return (today - ipo_dt).days


def get_timeline_status():
    """根據距上市天數，回傳當前時間軸狀態 + 鎖倉瀑布提醒"""
    d = days_since_ipo()
    notes = []
    
    if d < 0:
        return f"上市前 {abs(d)} 天", []
    
    # 綠鞋撤除
    if d < GREENSHOE_OFF_DAY:
        notes.append(f"🟢 綠鞋/穩定操作仍在（投行撐盤地板，到第 {GREENSHOE_OFF_DAY} 天，還剩 {GREENSHOE_OFF_DAY - d} 天）")
    elif d < GREENSHOE_OFF_DAY + 5:
        notes.append(f"⚠️ 綠鞋剛撤除（~第 {GREENSHOE_OFF_DAY} 天）—— 投行撐盤消失，下檔少一層緩衝")
    
    # 鎖倉瀑布（180 天基準，日期隨上市平移）
    lockup_events = [
        (70, "第 70 天解鎖 +7%"),
        (90, "第 90 天解鎖 +7%"),
        (105, "第 105 天解鎖 +7%"),
        (120, "第 120 天解鎖 +7%"),
        (135, "第 135 天解鎖 +7%"),
        (180, "第 180 天 剩餘全部解鎖（瀑布終點，B 池任務完成）"),
    ]
    for day, desc in lockup_events:
        if abs(d - day) <= 3:  # 接近解鎖日（±3 天）
            notes.append(f"🔓 接近{desc}（供給高峰，B 池準備承接）")
    
    # B 池掛單期間提醒
    if 0 <= d <= LOCKUP_FLOOR_END_DAY:
        notes.append(f"📌 B 池 GTC 應掛滿至第 {LOCKUP_FLOOR_END_DAY} 天（~12 月中），目前第 {d} 天")
    elif d > LOCKUP_FLOOR_END_DAY:
        notes.append(f"✅ 已過第 {LOCKUP_FLOOR_END_DAY} 天，鎖倉瀑布跑完，主要供給壓力結束")
    
    return f"上市第 {d} 天", notes


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


def generate_report(stage, price, atm_iv, pc_ratio, gtc_levels, 
                    iv_stable, dca_metrics, peers):
    """生成 markdown 報告（v8.1：市值定錨 + 斷路器 + Gamma 預警 + 論點破壞清單）"""
    md = "\n## 🚀 SPCX 太空雷達 (v8.1)\n\n"
    
    # === 修正四：論點破壞檢查清單（每天強迫自我拷問）===
    md += "### 🛑 v8.1 論點破壞檢查 (Narrative Breakers)\n"
    md += "_若以下任一條件成立，全盤凍結新資金投入：_\n"
    md += "- [ ] Starship 重大試飛失敗或進度嚴重推遲\n"
    md += "- [ ] Starlink 用戶數/營收季增率轉負\n"
    md += "- [ ] Nasdaq 100 快速納入 (Fast-entry) 規則生變\n"
    md += "- [ ] SpaceX 與 Tesla/xAI 出現重大惡意關聯交易或監管調查\n\n"
    
    stage_names = {
        0: "階段 0：尚未上市（追 IPO 進度）",
        1: "階段 1：已上市，選擇權尚未推出",
        2: "階段 2：選擇權已上市，IV 狂熱期 🔥",
        3: "階段 3：IV 冷卻，可評估 ✅",
    }
    md += f"**目前階段**：{stage_names.get(stage, '未知')}\n\n"
    
    if stage == 0:
        md += f"SPCX 預計 {IPO_DATE} 掛牌（{PRICING_DATE} 訂價）。上市後本雷達自動啟動。\n\n"
        # 階段 0 也顯示 GTC 市值定錨（不依賴開盤價，現在就能算）
        if gtc_levels:
            md += "### 💰 B 池 GTC 市值定錨（不依賴開盤價，已就緒）\n\n"
            md += f"_假設總股數 {TOTAL_SHARES_B}B。6/11 定價後務必核對更新。_\n\n"
            md += "| 目標市值 | 掛單價 | 池內權重 |\n|---|---|---|\n"
            for lv in gtc_levels:
                md += f"| {lv['target_mc_t']:.1f}T | ${lv['price']:.2f} | {lv['weight']*100:.0f}% |\n"
            md += "\n"
        return md
    
    current_mc_t = price_to_mc_t(price)
    md += f"**SPCX 現價**：${price:.2f}　**即時預估市值**：{current_mc_t:.2f}T（以 {TOTAL_SHARES_B}B 股計）\n\n"
    
    # === 時間軸狀態（綠鞋撤除 / 鎖倉瀑布）===
    timeline_label, timeline_notes = get_timeline_status()
    md += f"**時間軸**：{timeline_label}\n"
    for note in timeline_notes:
        md += f"- {note}\n"
    md += "\n"
    
    # === 修正二：DCA 斷路器（Hard Cap）===
    if current_mc_t > HARD_CAP_T:
        md += f"🚨 **【斷路器觸發】市值已突破 {HARD_CAP_T}T 天花板！A 池（DCA）與 B 池（地板）嚴禁投入新資金！**\n\n"
    elif current_mc_t > BUY_ZONE_TOP_T:
        md += f"🟠 市值 {current_mc_t:.2f}T 介於買區頂({BUY_ZONE_TOP_T}T)與上限({HARD_CAP_T}T)之間 —— 謹慎，接近停手線。\n\n"
    elif current_mc_t <= BUY_ZONE_ACCEL_T:
        md += f"🟢🟢 市值 {current_mc_t:.2f}T ≤ 加速買區({BUY_ZONE_ACCEL_T}T) —— A 池可加速 DCA。\n\n"
    else:
        md += f"🟢 市值位於買區內（≤{HARD_CAP_T}T），A 池可依計畫分批 DCA。\n\n"
    
    # === B 地板預備池 30% / $60k（市值定錨 GTC）===
    pool_b_amount = TOTAL_CAPITAL * POOL_B_FLOOR_PCT
    md += f"### 💰 B 地板預備池 30%（${pool_b_amount:,.0f}）— 絕對市值定錨 GTC\n\n"
    md += f"_掛單與開盤價無關，掛滿至第 {LOCKUP_FLOOR_END_DAY} 天（~12 月中）承接鎖倉瀑布。_\n\n"
    if gtc_levels:
        md += "| 目標市值 | 掛單價 | 池內權重 | 分配金額 | 距現價 | 狀態 |\n"
        md += "|---|---|---|---|---|---|\n"
        for lv in gtc_levels:
            dist = (price / lv['price'] - 1) * 100
            alloc = pool_b_amount * lv['weight']
            if price <= lv['price']:
                status = "✅ 已觸發"
            else:
                status = f"⏳ 還需跌 {dist:.1f}%"
            md += f"| {lv['target_mc_t']:.1f}T | ${lv['price']:.2f} | {lv['weight']*100:.0f}% | ${alloc:,.0f} | {dist:+.1f}% | {status} |\n"
        md += "\n"
    
    # === C 機動/選擇權池 10% ===
    pool_c_amount = TOTAL_CAPITAL * POOL_C_OPT_PCT
    md += f"### 🎰 C 機動/選擇權池 10%（${pool_c_amount:,.0f}）— IV 冷卻 + Gamma 預警\n\n"
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
        
        # === 修正三：Gamma Squeeze 預警 ===
        if pc_ratio is not None:
            md += f"Put/Call Volume Ratio：{pc_ratio:.2f}　"
            if pc_ratio < PC_RATIO_SQUEEZE:
                md += f"⚠️ **極端軋空狂熱（Gamma Squeeze Warning），買 Call 是買 Put 的 {1/pc_ratio:.1f} 倍，造市商正在裸奔！**\n\n"
            else:
                md += "（正常範圍）\n\n"
        else:
            md += "_Put 流動性不足，PC ratio 暫不計算（避免假警報）_\n\n"
        
        if iv_stable:
            md += "✅ **IV 已連續穩定冷卻** — options 池可開始評估進場\n\n"
        else:
            md += f"⏳ IV 尚未連續 {IV_CONFIG['STABLE_DAYS']} 天穩定在 {IV_CONFIG['COOLING']*100:.0f}% 以下 — 繼續等\n\n"
    else:
        md += "_選擇權尚未上市，IV 無法計算_\n\n"
    
    # === A 核心 DCA 池 60% / $120k ===
    pool_a_amount = TOTAL_CAPITAL * POOL_A_DCA_PCT
    tranche_amount = pool_a_amount / DCA_TRANCHES
    md += f"### 📊 A 核心 DCA 池 60%（${pool_a_amount:,.0f}）— 純儀表板，無買賣訊號\n\n"
    md += f"_計畫：6/12→~7/3 分 {DCA_TRANCHES} 筆 × ${tranche_amount:,.0f}，依市值錨。市值 >{HARD_CAP_T}T 該筆跳過。_\n\n"
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
    print(f"🚀 啟動 SPCX 太空雷達 v8.1: {datetime.now().strftime('%Y-%m-%d')}")
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # 偵測階段
    stage, price, atm_iv, pc_ratio = detect_stage()
    print(f"📍 目前階段：{stage}")
    
    # GTC 市值定錨：與開盤價無關，任何階段都能算
    gtc_levels = calc_gtc_levels()
    print(f"⚓ B 池市值定錨（總股數 {TOTAL_SHARES_B}B）：")
    for lv in gtc_levels:
        print(f"     {lv['target_mc_t']:.1f}T → ${lv['price']:.2f}（權重 {lv['weight']*100:.0f}%）")
    
    iv_stable = False
    dca_metrics = None
    
    if stage >= 1:
        print(f"💎 SPCX 現價：${price:.2f}（市值 {price_to_mc_t(price):.2f}T）")
        dca_metrics = calc_dca_metrics(price)
        if price_to_mc_t(price) > HARD_CAP_T:
            print(f"🚨 斷路器觸發：市值 > {HARD_CAP_T}T，嚴禁新資金")
    
    if stage >= 2 and atm_iv is not None:
        print(f"🌡️  ATM IV：{atm_iv*100:.1f}%")
        if pc_ratio is not None:
            print(f"   PC ratio：{pc_ratio:.2f}" + 
                  (f" ⚠️ Gamma Squeeze 警告！" if pc_ratio < PC_RATIO_SQUEEZE else ""))
        iv_df = record_iv_history(atm_iv, price)
        iv_stable = check_iv_stable(iv_df)
        print(f"   IV 穩定冷卻：{'✅' if iv_stable else '⏳ 尚未'}")
    
    # 太空同游股（任何階段都掃）
    print("🛰️  掃描太空同游股...")
    peers = scan_space_peers()
    print(f"   {len(peers)} 檔")
    
    # 生成報告
    md = generate_report(stage, price, atm_iv, pc_ratio, gtc_levels,
                         iv_stable, dca_metrics, peers)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(md)
    
    # 寫 JSON
    output = {
        'updated_at': datetime.now().isoformat(),
        'stage': stage,
        'price': price,
        'market_cap_t': round(price_to_mc_t(price), 3) if price else None,
        'total_shares_b': TOTAL_SHARES_B,
        'hard_cap_t': HARD_CAP_T,
        'atm_iv': atm_iv,
        'pc_ratio': pc_ratio,
        'iv_stable': iv_stable,
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
