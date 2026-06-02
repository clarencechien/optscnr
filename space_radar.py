"""
space_radar.py — SPCX (SpaceX) IPO 三池策略支援雷達

SpaceX 6/12 上市，代號 SPCX。這個 radar 不替你決定買什麼，
而是餵你三池策略各自需要的訊號：

【A 核心 DCA 池 60% / $120k】首筆市價確保上車 + 4 筆 limit 階梯，市值 >2.2T 斷路器
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

【v8.3 改動】對齊進場 SOP v8.3
- A 池改為「首筆市價確保上車 + 4 筆 limit 階梯」，calc_gtc_levels() 加 pool 參數共用
- PC ratio 訊號方向修正：PC 極端 AND IV 狂熱 → C 池凍結（不再慫恿進場）
- IV 改用相對分位（percentile），資料不足 fallback 絕對門檻
- 斷路器文案修正：擋未投完批次追高，不影響已建立部位
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
    # A 池：首筆市價 + 4 筆 limit 階梯（對齊 SOP v8.3）
    'a_pool_first_market': True,            # 首筆是否市價單（確保上車）
    'a_pool_anchors_t': [1.9, 1.8, 1.7, 1.6],  # 第 2–5 筆 limit 掛單市值錨
    'a_pool_limit_weights': [0.25, 0.25, 0.25, 0.25],  # 第 2–5 筆權重（佔 limit 部分）
    # B 池：單向下檔 GTC
    'b_pool_anchors_t': [1.5, 1.3, 1.1],
    'gtc_weights': [0.40, 0.35, 0.25],
    'greenshoe_off_day': 30,
    'lockup_floor_end_day': 180,
    'dca_deadline': '2026-07-03',           # A 池佈署截止日
    'pc_ratio_squeeze': 0.20,
    'pc_min_put_vol': 500,
    'iv_frenzy': 0.80,
    'iv_cooling': 0.60,
    'iv_calm': 0.50,
    'iv_stable_days': 3,
    'iv_pctile_frenzy': 80,                 # IV 分位 > 此值 = 狂熱（相對基準）
    'iv_pctile_calm': 40,                   # IV 分位 < 此值 = 冷卻
    'iv_pctile_min_samples': 10,            # 少於此樣本數，fallback 回絕對門檻
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
A_POOL_FIRST_MARKET = _CFG['a_pool_first_market']
A_POOL_ANCHORS_T = _CFG['a_pool_anchors_t']
A_POOL_LIMIT_WEIGHTS = _CFG['a_pool_limit_weights']
B_POOL_ANCHORS_T = _CFG['b_pool_anchors_t']
GTC_WEIGHTS = _CFG['gtc_weights']
GREENSHOE_OFF_DAY = _CFG['greenshoe_off_day']
LOCKUP_FLOOR_END_DAY = _CFG['lockup_floor_end_day']
DCA_DEADLINE = _CFG['dca_deadline']
PC_RATIO_SQUEEZE = _CFG['pc_ratio_squeeze']
PC_MIN_PUT_VOL = _CFG['pc_min_put_vol']
IV_PCTILE_FRENZY = _CFG['iv_pctile_frenzy']
IV_PCTILE_CALM = _CFG['iv_pctile_calm']
IV_PCTILE_MIN_SAMPLES = _CFG['iv_pctile_min_samples']

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

# Options 池 IV 門檻（絕對值，fallback 用）
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

    # 階段判定改用「相對分位」優先，fallback 絕對門檻
    iv_hot, _ = classify_iv(atm_iv)
    if iv_hot:
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


def get_iv_percentile(atm_iv):
    """用已累積的 IV 歷史，算當前 IV 的相對分位（0–100）

    回傳 (percentile, n_samples)；資料不足回 (None, n_samples)
    新股沒有 IV 歷史，絕對門檻（0.80）無基準，所以優先用相對分位。
    """
    if not os.path.exists(IV_HISTORY_PATH):
        return None, 0
    try:
        df = pd.read_csv(IV_HISTORY_PATH)
        ivs = df['atm_iv'].dropna()
        n = len(ivs)
        if n < IV_PCTILE_MIN_SAMPLES:
            return None, n
        # 當前 IV 在歷史分布中的百分位
        pctile = (ivs < atm_iv).sum() / n * 100
        return round(pctile, 1), n
    except Exception:
        return None, 0


def classify_iv(atm_iv):
    """判定 IV 是否「狂熱」。優先用相對分位，資料不足 fallback 絕對門檻。

    回傳 (is_hot: bool, label: str)
    """
    pctile, n = get_iv_percentile(atm_iv)
    if pctile is not None:
        # 用相對分位
        if pctile >= IV_PCTILE_FRENZY:
            return True, f"分位 {pctile:.0f}（自身歷史高檔，狂熱）"
        elif pctile <= IV_PCTILE_CALM:
            return False, f"分位 {pctile:.0f}（自身歷史低檔，冷卻）"
        else:
            return False, f"分位 {pctile:.0f}（中性）"
    else:
        # fallback：絕對門檻（樣本不足時）
        if atm_iv > IV_CONFIG['FRENZY']:
            return True, f"{atm_iv*100:.0f}%（絕對門檻，樣本不足 n={n}）"
        else:
            return False, f"{atm_iv*100:.0f}%（絕對門檻，樣本不足 n={n}）"


def calc_gtc_levels(pool='B'):
    """根據絕對市值反推 GTC 掛單價位，與開盤價/VWAP 完全無關

    price = 市值(兆) × 1000 / 總股數(十億)

    pool='A'：A 池 limit 階梯（第 2–5 筆，首筆市價另計），錨點 A_POOL_ANCHORS_T
    pool='B'：B 池下檔承接，錨點 B_POOL_ANCHORS_T
    """
    if pool == 'A':
        anchors = A_POOL_ANCHORS_T
        weights = A_POOL_LIMIT_WEIGHTS
    else:
        anchors = B_POOL_ANCHORS_T
        weights = GTC_WEIGHTS

    levels = []
    for mc_t, weight in zip(anchors, weights):
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

    # A 池佈署截止日提醒
    try:
        deadline_dt = datetime.strptime(DCA_DEADLINE, '%Y-%m-%d')
        days_to_deadline = (deadline_dt - datetime.now()).days
        if 0 <= days_to_deadline <= 21:
            notes.append(f"📊 A 池佈署截止日 {DCA_DEADLINE} 還剩 {days_to_deadline} 天 —— 截止後未投滿餘額併入 B 池")
        elif -3 <= days_to_deadline < 0:
            notes.append(f"⚠️ A 池佈署截止日已過（{DCA_DEADLINE}）—— 盤點：未投滿餘額依規則併入 B 池或凍結")
    except Exception:
        pass

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
    """檢查 IV 是否連續幾天冷卻（穩定）。

    優先：連續 STABLE_DAYS 天的 IV 分位都 <= IV_PCTILE_CALM
    fallback（樣本不足）：連續 STABLE_DAYS 天絕對值 < COOLING
    """
    if iv_df is None or len(iv_df) < IV_CONFIG['STABLE_DAYS']:
        return False

    recent = iv_df.tail(IV_CONFIG['STABLE_DAYS'])
    n_total = len(iv_df['atm_iv'].dropna())

    if n_total >= IV_PCTILE_MIN_SAMPLES:
        # 用相對分位：最近幾天每天的分位都要在冷卻線下
        ivs_all = iv_df['atm_iv'].dropna()
        for iv in recent['atm_iv']:
            pctile = (ivs_all < iv).sum() / len(ivs_all) * 100
            if pctile > IV_PCTILE_CALM:
                return False
        return True
    else:
        # fallback 絕對門檻
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
            # A 池投入進度（對齊 SOP：60% / total_capital）
            pool_a_target = TOTAL_CAPITAL * POOL_A_DCA_PCT
            result['pool_a_target'] = round(pool_a_target, 0)
            result['pool_a_filled_pct'] = round(total_cost / pool_a_target * 100, 1)

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


def generate_report(stage, price, atm_iv, pc_ratio, gtc_levels_a, gtc_levels_b,
                    iv_stable, dca_metrics, peers):
    """生成 markdown 報告（v8.3：A 池首筆市價+階梯 / PC 方向修正 / IV 分位）"""
    md = "\n## 🚀 SPCX 太空雷達 (v8.3)\n\n"

    # === 論點破壞檢查清單（每天強迫自我拷問）===
    md += "### 🛑 論點破壞檢查 (Narrative Breakers)\n"
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
        md += _render_pool_a_plan(gtc_levels_a, stage=0)
        md += _render_pool_b_plan(gtc_levels_b, price=None, stage=0)
        return md

    current_mc_t = price_to_mc_t(price)
    md += f"**SPCX 現價**：${price:.2f}　**即時預估市值**：{current_mc_t:.2f}T（以 {TOTAL_SHARES_B}B 股計）\n\n"

    # === 時間軸狀態（綠鞋撤除 / 鎖倉瀑布 / A 池截止日）===
    timeline_label, timeline_notes = get_timeline_status()
    md += f"**時間軸**：{timeline_label}\n"
    for note in timeline_notes:
        md += f"- {note}\n"
    md += "\n"

    # === DCA 斷路器（Hard Cap）—— 文案修正：擋未投完批次，不影響已建立部位 ===
    if current_mc_t > HARD_CAP_T:
        md += f"🚨 **【斷路器觸發】市值已突破 {HARD_CAP_T}T。**\n"
        md += f"→ A 池**未投完批次**與 B 池**停止掛新單/追高**。\n"
        md += f"→ **已建立的部位不受影響**（十年持股不下車，斷路器只擋新錢，不是叫你賣）。\n\n"
    elif current_mc_t > BUY_ZONE_TOP_T:
        md += f"🟠 市值 {current_mc_t:.2f}T 介於買區頂({BUY_ZONE_TOP_T}T)與上限({HARD_CAP_T}T)之間 —— 謹慎，接近停手線。\n\n"
    elif current_mc_t <= BUY_ZONE_ACCEL_T:
        md += f"🟢🟢 市值 {current_mc_t:.2f}T ≤ 加速買區({BUY_ZONE_ACCEL_T}T) —— A 池 limit 階梯可望成交。\n\n"
    else:
        md += f"🟢 市值位於買區內（≤{HARD_CAP_T}T），A 池依 SOP 分批佈署。\n\n"

    # === A 核心 DCA 池 ===
    md += _render_pool_a_plan(gtc_levels_a, stage=stage, price=price, dca_metrics=dca_metrics)

    # === B 地板預備池 ===
    md += _render_pool_b_plan(gtc_levels_b, price=price, stage=stage)

    # === C 機動/選擇權池（PC 方向修正 + IV 分位）===
    md += _render_pool_c(atm_iv, pc_ratio, iv_stable)

    # === 太空同游股 ===
    if peers:
        md += "### 🛰️ 太空同游股（觀察 SPCX 虹吸/受惠）\n\n"
        md += "| 標的 | 現價 | 30天 | 近期趨勢 | 定位 |\n"
        md += "|---|---|---|---|---|\n"
        for p in sorted(peers, key=lambda x: x['change_1m_pct'], reverse=True):
            md += f"| {p['ticker']} | ${p['price']:.2f} | {p['change_1m_pct']:+.1f}% | {p['recent_trend_pct']:+.1f}% | {p['desc']} |\n"
        md += "\n_虹吸觀察：SPCX 上市後，競爭型（ASTS/LUNR）可能被吸乾，利基型（RKLB/PL）可能受惠。_\n\n"

    return md


def _render_pool_a_plan(gtc_levels_a, stage, price=None, dca_metrics=None):
    """A 池：首筆市價 + 4 筆 limit 階梯（對齊 SOP v8.3）"""
    pool_a_amount = TOTAL_CAPITAL * POOL_A_DCA_PCT
    n_tranches = (1 if A_POOL_FIRST_MARKET else 0) + len(gtc_levels_a)
    tranche_amount = pool_a_amount / n_tranches if n_tranches else 0

    md = f"### 📊 A 核心 DCA 池 {POOL_A_DCA_PCT*100:.0f}%（${pool_a_amount:,.0f}）— 首筆市價 + limit 階梯\n\n"
    md += f"_計畫：上市首日第 1 筆市價確保上車；第 2–5 筆 GTC limit 掛好就忘。每筆約 ${tranche_amount:,.0f}。截止日 {DCA_DEADLINE}。_\n\n"
    md += "| 批次 | 類型 | 目標市值 | 掛單價 | 金額 | 狀態 |\n|---|---|---|---|---|---|\n"

    # 第 1 筆市價
    if A_POOL_FIRST_MARKET:
        if stage == 0:
            status1 = "上市首日執行"
        elif price is not None and price_to_mc_t(price) > HARD_CAP_T:
            status1 = "⚠️ >2.2T，改掛 2.2T limit"
        else:
            status1 = "✅ 首日市價（確保上車）"
        md += f"| 1 | 市價 | — | 開盤價 | ${tranche_amount:,.0f} | {status1} |\n"

    # 第 2–5 筆 limit
    for i, lv in enumerate(gtc_levels_a, start=2):
        alloc = pool_a_amount * (1 - (tranche_amount/pool_a_amount if A_POOL_FIRST_MARKET else 0)) * lv['weight'] \
            if A_POOL_FIRST_MARKET else pool_a_amount * lv['weight']
        # 上面這行為了精確；實務上每筆就是 tranche_amount，簡化顯示
        alloc = tranche_amount
        if stage == 0 or price is None:
            status = "待上市掛單"
        elif price <= lv['price']:
            status = "✅ 已觸發"
        else:
            dist = (price / lv['price'] - 1) * 100
            status = f"⏳ 還需跌 {dist:.1f}%"
        md += f"| {i} | limit | {lv['target_mc_t']:.2f}T | ${lv['price']:.2f} | ${alloc:,.0f} | {status} |\n"

    md += "\n"
    if stage == 0:
        md += f"_假設總股數 {TOTAL_SHARES_B}B。**6/11 定價後務必核對更新 config 的 total_shares_b。**_\n\n"

    # DCA 進度 + 7/3 截止提醒
    if dca_metrics and dca_metrics.get('avg_cost'):
        md += f"- 你的平均成本：**${dca_metrics['avg_cost']:.2f}**"
        md += f"（{dca_metrics['total_shares']} 股，投入 ${dca_metrics['total_invested']:,.0f}）\n"
        if dca_metrics.get('pool_a_filled_pct') is not None:
            md += f"- A 池佈署進度：**{dca_metrics['pool_a_filled_pct']:.0f}%**"
            md += f"（目標 ${dca_metrics['pool_a_target']:,.0f}）\n"
        md += f"- 現價：${dca_metrics['current_price']:.2f}"
        md += f"（未實現 {dca_metrics['unrealized_pnl_pct']:+.1f}%）\n"
        if dca_metrics.get('ma50'):
            md += f"- 50 日均線：${dca_metrics['ma50']:.2f}\n"
        md += f"\n_截止日 {DCA_DEADLINE} 未投滿 → 餘額併入 B 池（買區內）或凍結（>2.2T）。可能結果：核心倉 < 60%，這是紀律沒追高的代價。_\n\n"
    elif stage >= 1:
        md += f"- _尚未開始 DCA，或 spcx_dca_log.json 未維護_\n\n"

    return md


def _render_pool_b_plan(gtc_levels_b, price, stage):
    """B 池：單向下檔 GTC，掛到 180 天"""
    pool_b_amount = TOTAL_CAPITAL * POOL_B_FLOOR_PCT
    md = f"### 💰 B 地板預備池 {POOL_B_FLOOR_PCT*100:.0f}%（${pool_b_amount:,.0f}）— 絕對市值定錨 GTC\n\n"
    md += f"_掛單與開盤價無關，掛滿至第 {LOCKUP_FLOOR_END_DAY} 天（~12 月中）承接鎖倉瀑布。_\n\n"
    if not gtc_levels_b:
        return md
    md += "| 目標市值 | 掛單價 | 池內權重 | 分配金額 | 距現價 | 狀態 |\n"
    md += "|---|---|---|---|---|---|\n"
    for lv in gtc_levels_b:
        alloc = pool_b_amount * lv['weight']
        if stage == 0 or price is None:
            dist_str, status = "—", "待上市掛單"
        else:
            dist = (price / lv['price'] - 1) * 100
            dist_str = f"{dist:+.1f}%"
            status = "✅ 已觸發" if price <= lv['price'] else f"⏳ 還需跌 {dist:.1f}%"
        md += f"| {lv['target_mc_t']:.1f}T | ${lv['price']:.2f} | {lv['weight']*100:.0f}% | ${alloc:,.0f} | {dist_str} | {status} |\n"
    md += "\n"
    return md


def _render_pool_c(atm_iv, pc_ratio, iv_stable):
    """C 池：PC 方向修正（PC 極端 AND IV 狂熱 → 凍結）+ IV 相對分位"""
    pool_c_amount = TOTAL_CAPITAL * POOL_C_OPT_PCT
    md = f"### 🎰 C 機動/選擇權池 {POOL_C_OPT_PCT*100:.0f}%（${pool_c_amount:,.0f}）— IV 冷卻才放行\n\n"

    if atm_iv is None:
        md += "_選擇權尚未上市，IV 無法計算。Launch 期預設持現金。_\n\n"
        return md

    iv_hot, iv_label = classify_iv(atm_iv)
    iv_pct = atm_iv * 100

    # IV 狀態
    if iv_hot:
        md += f"ATM IV：🔥 **狂熱（{iv_pct:.0f}%｜{iv_label}）— IV crush 風險極高**\n\n"
    else:
        md += f"ATM IV：🟢 冷卻（{iv_pct:.0f}%｜{iv_label}）\n\n"

    # === PC ratio：方向修正。極端 PC 不再是「機會」，是配合 IV 判斷凍結 ===
    pc_extreme = (pc_ratio is not None and pc_ratio < PC_RATIO_SQUEEZE)

    if pc_ratio is not None:
        md += f"Put/Call Volume Ratio：{pc_ratio:.2f}　"
        if pc_extreme:
            md += f"（call 為 put 的 {1/pc_ratio:.1f} 倍，散戶 call 狂熱）\n\n"
        else:
            md += "（正常範圍）\n\n"
    else:
        md += "_Put 流動性不足，PC ratio 暫不計算（避免假警報）_\n\n"

    # === 綜合判定：C 池該不該動 ===
    if iv_hot and pc_extreme:
        md += "🚫 **C 池凍結（最高優先）**：IV 狂熱 + call 狂熱同時出現 = gamma 軋升的高 IV 環境。\n"
        md += "此刻買 call 是「最貴的價格 + 即將 IV crush」，方向對也會賠。**不進場、不參與、持現金。**\n\n"
    elif iv_hot:
        md += "🔴 **C 池禁止進場**：IV 仍在狂熱區，買 call 會被 IV crush 吃掉。持現金等冷卻。\n\n"
    elif iv_stable:
        md += "✅ **IV 已連續穩定冷卻** — C 池可開始評估：僅限深價內 LEAPS（≥2027、delta≈1），且需有市場未 price-in 的觀點。\n"
        md += "_禁令：不買近月/價外 call、任何時候不裸賣。_\n\n"
    else:
        md += f"⏳ IV 已非狂熱，但尚未連續 {IV_CONFIG['STABLE_DAYS']} 天穩定冷卻 — 繼續等，先別動。\n\n"

    return md


def main():
    print(f"🚀 啟動 SPCX 太空雷達 v8.3: {datetime.now().strftime('%Y-%m-%d')}")

    if not os.path.exists('data'):
        os.makedirs('data')

    # 偵測階段
    stage, price, atm_iv, pc_ratio = detect_stage()
    print(f"📍 目前階段：{stage}")

    # GTC 市值定錨：A、B 兩池都算，與開盤價無關
    gtc_levels_a = calc_gtc_levels(pool='A')
    gtc_levels_b = calc_gtc_levels(pool='B')
    print(f"⚓ A 池 limit 階梯（首筆市價 + 以下，總股數 {TOTAL_SHARES_B}B）：")
    for lv in gtc_levels_a:
        print(f"     {lv['target_mc_t']:.2f}T → ${lv['price']:.2f}")
    print(f"⚓ B 池下檔定錨：")
    for lv in gtc_levels_b:
        print(f"     {lv['target_mc_t']:.1f}T → ${lv['price']:.2f}（權重 {lv['weight']*100:.0f}%）")

    iv_stable = False
    dca_metrics = None

    if stage >= 1:
        print(f"💎 SPCX 現價：${price:.2f}（市值 {price_to_mc_t(price):.2f}T）")
        dca_metrics = calc_dca_metrics(price)
        if price_to_mc_t(price) > HARD_CAP_T:
            print(f"🚨 斷路器觸發：市值 > {HARD_CAP_T}T，A 池未投完批次 + B 池停止新單（已建立部位不動）")

    if stage >= 2 and atm_iv is not None:
        iv_hot, iv_label = classify_iv(atm_iv)
        print(f"🌡️  ATM IV：{atm_iv*100:.1f}%（{iv_label}）")
        if pc_ratio is not None:
            pc_extreme = pc_ratio < PC_RATIO_SQUEEZE
            print(f"   PC ratio：{pc_ratio:.2f}")
            if iv_hot and pc_extreme:
                print(f"   🚫 C 池凍結：IV 狂熱 + call 狂熱，IV crush 風險最高")
        iv_df = record_iv_history(atm_iv, price)
        iv_stable = check_iv_stable(iv_df)
        print(f"   IV 穩定冷卻：{'✅ 可評估 LEAPS' if iv_stable else '⏳ 尚未，持現金'}")

    # 太空同游股（任何階段都掃）
    print("🛰️  掃描太空同游股...")
    peers = scan_space_peers()
    print(f"   {len(peers)} 檔")

    # 生成報告
    md = generate_report(stage, price, atm_iv, pc_ratio, gtc_levels_a, gtc_levels_b,
                         iv_stable, dca_metrics, peers)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(md)

    # 寫 JSON
    output = {
        'updated_at': datetime.now().isoformat(),
        'version': 'v8.3',
        'stage': stage,
        'price': price,
        'market_cap_t': round(price_to_mc_t(price), 3) if price else None,
        'total_shares_b': TOTAL_SHARES_B,
        'hard_cap_t': HARD_CAP_T,
        'atm_iv': atm_iv,
        'iv_percentile': get_iv_percentile(atm_iv)[0] if atm_iv else None,
        'pc_ratio': pc_ratio,
        'c_pool_frozen': bool(atm_iv and classify_iv(atm_iv)[0]),
        'iv_stable': iv_stable,
        'gtc_levels_a': gtc_levels_a,
        'gtc_levels_b': gtc_levels_b,
        'dca_metrics': dca_metrics,
        'peers': peers,
    }
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n💾 已寫入 {OUTPUT_PATH}")
    print(f"💾 報告：{REPORT_PATH}")


if __name__ == "__main__":
    main()
