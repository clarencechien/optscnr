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

輸出（2026-07-31 起集中在 spcx_radar/，路徑由 spcx_common 統一管理）：
- output/space_radar.json
- output/space_radar_report.md（由 build_readme.py 組進 spcx_radar/README.md）
- output/spcx_iv_history.csv（IV 時間序列）
- config/spcx_dca_log.json（你的 DCA 紀錄，手動維護）

可變參數：config/spcx_config.json（IPO 日期、股數、各池比例…全在這，改它不用動 code）

頻率：每天跑（IPO 後）

【v8.7 改動】（2026-07-31 整併進 spcx_radar/）
- 檔案搬進 spcx_radar/：config/（手動維護）與 output/（產出）分離，路徑統一由 spcx_common 管
- 與 spcx_options.py 重複的基礎函式（load_config / 現價 / ATM IV / 市值換算 / IV 分位）
  抽到 spcx_common.py，兩支模組共用一致介面
- 新增「A/B 池跟進手冊」區塊：A 池佈署近完成、B 池只剩日曆任務，
  把剩餘動作日曆化（GT90 重掛、解鎖日、180 天終點），8 月起重心移到 C 池（Option Sage）

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

import spcx_common

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# === 設定 ===
# 所有「6/11 才定案、可能變動」的參數都集中在 spcx_radar/config/spcx_config.json
# code 啟動時讀它；讀不到任一欄位就用下面的內建預設值（防呆）

CONFIG_PATH = spcx_common.CONFIG_PATH

# 內建預設值（config 讀不到時的 fallback）
_DEFAULTS = {
    'ticker': 'SPCX',
    'ipo_date': '2026-06-12',
    'pricing_date': '2026-06-11',
    'total_shares_b': 13.0,
    'ipo_price': None,
    'total_capital': 200_000,
    'pool_a_dca_pct': 0.60,
    'pool_b_floor_pct': 0.30,
    'pool_c_opt_pct': 0.10,
    'dca_tranches': 5,
    'hard_cap_t': 2.2,
    'buy_zone_top_t': 2.0,
    'buy_zone_accel_t': 1.75,
    # A 池：首筆「高限價單」(Firstrade 首日不收市價單) + 4 筆 limit 階梯
    'a_pool_first_market': False,           # Firstrade 首日不接受市價單，首筆改高限價單
    'a_pool_first_limit_price': 169.0,      # 首筆限價（2.2T 上限，最大化上車機率）
    'a_pool_first_shares_at': 135.0,        # 首筆股數用此價算（IPO 價，達標為主；非用限價算）
    'a_pool_anchors_t': [1.9, 1.8, 1.7, 1.6],  # 第 2–5 筆 limit 掛單市值錨
    'a_pool_limit_weights': [0.25, 0.25, 0.25, 0.25],  # 第 2–5 筆權重（佔 limit 部分）
    # B 池：單向下檔 GTC（Firstrade 最長 GT90，需每 90 天重掛）
    'b_pool_anchors_t': [1.5, 1.3, 1.1],
    'gtc_weights': [0.40, 0.35, 0.25],
    'gt90_relist_day': 90,                  # Firstrade GTC 最長 90 天，第 90 天提醒重掛
    'greenshoe_off_day': 30,
    'lockup_floor_end_day': 180,
    'vacuum_end_day': 45,                   # 真空期結束日（約對應 Q2 財報/首波解鎖）。此前 B 池基本不成交屬正常
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
    """讀 spcx_config.json（透過 spcx_common 統一載入），缺欄位用 _DEFAULTS 補。"""
    cfg = spcx_common.load_config(_DEFAULTS)
    print(f"📋 已讀取 spcx_config.json（IPO 日期：{cfg['ipo_date']}，股數：{cfg['total_shares_b']}B）")
    return cfg


# 載入 config，灌進 module-level 變數（其他函式沿用原本的名字，零改動）
_CFG = load_config()
TICKER = _CFG['ticker']
IPO_DATE = _CFG['ipo_date']
PRICING_DATE = _CFG['pricing_date']
TOTAL_SHARES_B = _CFG['total_shares_b']
IPO_PRICE = _CFG['ipo_price']
TOTAL_CAPITAL = _CFG['total_capital']
POOL_A_DCA_PCT = _CFG['pool_a_dca_pct']
POOL_B_FLOOR_PCT = _CFG['pool_b_floor_pct']
POOL_C_OPT_PCT = _CFG['pool_c_opt_pct']
DCA_TRANCHES = _CFG['dca_tranches']
HARD_CAP_T = _CFG['hard_cap_t']
BUY_ZONE_TOP_T = _CFG['buy_zone_top_t']
BUY_ZONE_ACCEL_T = _CFG['buy_zone_accel_t']
A_POOL_FIRST_MARKET = _CFG['a_pool_first_market']
A_POOL_FIRST_LIMIT_PRICE = _CFG['a_pool_first_limit_price']
A_POOL_FIRST_SHARES_AT = _CFG['a_pool_first_shares_at']
A_POOL_ANCHORS_T = _CFG['a_pool_anchors_t']
A_POOL_LIMIT_WEIGHTS = _CFG['a_pool_limit_weights']
B_POOL_ANCHORS_T = _CFG['b_pool_anchors_t']
GTC_WEIGHTS = _CFG['gtc_weights']
GREENSHOE_OFF_DAY = _CFG['greenshoe_off_day']
LOCKUP_FLOOR_END_DAY = _CFG['lockup_floor_end_day']
GT90_RELIST_DAY = _CFG['gt90_relist_day']
VACUUM_END_DAY = _CFG['vacuum_end_day']
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

IV_HISTORY_PATH = spcx_common.IV_HISTORY_PATH
DCA_LOG_PATH = spcx_common.DCA_LOG_PATH
OUTPUT_PATH = spcx_common.SPACE_RADAR_JSON
REPORT_PATH = spcx_common.SPACE_RADAR_REPORT


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

    # 試著抓價格（spcx_common：dropna + nan 防呆）
    current_price = spcx_common.get_price(tk)
    if current_price is None:
        return 0, None, None, None  # 還沒上市或無有效報價

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
    # 鏈選擇與 ATM IV 計算統一走 spcx_common（與 Option Sage 同一套，介面一致）
    _, calls, puts = spcx_common.get_atm_chain(tk, current_price, min_days=14)
    atm_iv = spcx_common.calc_atm_iv(calls, current_price)
    if atm_iv is None:
        return None, None

    try:
        # PC Ratio（軋空狂熱偵測）
        total_call_vol = float(calls['volume'].fillna(0).sum())
        total_put_vol = float(puts['volume'].fillna(0).sum()) if puts is not None and not puts.empty else 0

        # Put 流動性防呆：量太低不算（避免 0/大數 = 假警報）
        if total_put_vol < PC_MIN_PUT_VOL or total_call_vol < 1:
            pc_ratio = None
        else:
            pc_ratio = total_put_vol / total_call_vol
        return atm_iv, pc_ratio
    except Exception:
        return atm_iv, None


def get_iv_percentile(atm_iv):
    """當前 IV 的相對分位（spcx_common 統一實作）。
    新股沒有 IV 歷史，絕對門檻（0.80）無基準，所以優先用相對分位。"""
    return spcx_common.iv_percentile(atm_iv, IV_HISTORY_PATH, IV_PCTILE_MIN_SAMPLES)


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
    """根據絕對市值反推 GTC 掛單價位，並算出「股數 + 實際金額」(下單可直接照抄)

    限價 = 市值(兆) × 1000 / 總股數(十億)
    股數 = 該筆金額 ÷ 限價，取整數股（Firstrade 下單填的是股數，不是金額）

    pool='A'：A 池 limit 階梯（第 2–5 筆，首筆另計），錨點 A_POOL_ANCHORS_T
    pool='B'：B 池下檔承接，錨點 B_POOL_ANCHORS_T
    """
    if pool == 'A':
        anchors = A_POOL_ANCHORS_T
        weights = A_POOL_LIMIT_WEIGHTS
        pool_amount = TOTAL_CAPITAL * POOL_A_DCA_PCT
        # A 池每筆金額 = 池金額 / 5 筆（首筆 + 4 階梯）
        per_tranche = pool_amount / (len(anchors) + 1)
    else:
        anchors = B_POOL_ANCHORS_T
        weights = GTC_WEIGHTS
        pool_amount = TOTAL_CAPITAL * POOL_B_FLOOR_PCT

    levels = []
    for mc_t, weight in zip(anchors, weights):
        price = (mc_t * 1000) / TOTAL_SHARES_B
        # 該筆金額：A 池每筆均分；B 池按權重
        amount = per_tranche if pool == 'A' else pool_amount * weight
        shares = int(amount / price) if price > 0 else 0  # 取整數股
        actual = round(shares * price, 2)
        levels.append({
            'target_mc_t': mc_t,
            'price': round(price, 2),
            'weight': weight,
            'shares': shares,
            'actual_amount': actual,
        })
    return levels


def calc_a_first_tranche():
    """A 池首筆：高限價單（Firstrade 首日不收市價單）。
    限價 = A_POOL_FIRST_LIMIT_PRICE（2.2T 上限，最大化上車）
    股數 = 每筆金額 ÷ A_POOL_FIRST_SHARES_AT（用 IPO 價算，達標為主）
    """
    pool_amount = TOTAL_CAPITAL * POOL_A_DCA_PCT
    per_tranche = pool_amount / (len(A_POOL_ANCHORS_T) + 1)
    shares = int(per_tranche / A_POOL_FIRST_SHARES_AT) if A_POOL_FIRST_SHARES_AT else 0
    return {
        'limit_price': A_POOL_FIRST_LIMIT_PRICE,
        'shares_at': A_POOL_FIRST_SHARES_AT,
        'shares': shares,
        'budget': round(per_tranche, 2),
        'max_cost_if_filled_high': round(shares * A_POOL_FIRST_LIMIT_PRICE, 2),  # 若掛在上限成交的最壞金額
    }



def price_to_mc_t(price):
    """價格反推市值（兆）——spcx_common 統一實作"""
    return spcx_common.price_to_mc_t(price, TOTAL_SHARES_B)


def days_since_ipo():
    """距上市第幾天（上市前回負數）——spcx_common 統一實作"""
    return spcx_common.days_since_ipo(IPO_DATE)


def get_timeline_status():
    """根據距上市天數，回傳當前時間軸狀態 + 鎖倉瀑布提醒"""
    d = days_since_ipo()
    notes = []

    if d < 0:
        return f"上市前 {abs(d)} 天", []

    # 真空期 vs 解鎖期階段標示（決定 B 池該不該有期待）
    if d < VACUUM_END_DAY:
        notes.append(f"🌑 真空期（~第 {VACUUM_END_DAY} 天前）—— 可交易流通約 7%（IPO 新股 + directed share 5% 無鎖倉），B 池基本不會成交屬正常，但 directed share 持有人可賣、零星供給比零略多。前期靠等下跌建倉的路徑大概率走不通。")
        notes.append(f"📈 指數催化兩階段：夏天多指數（MSCI 第10交易日 / Nasdaq100 第15交易日 / Russell）+ 2027 S&P 500（最大一波，待獲利）。注意：納入日常是搶跑者出貨點，非追高時機。")
    else:
        notes.append(f"📉 解鎖期（已過第 {VACUUM_END_DAY} 天）—— B 池成交窗口開啟，但仍需有人『賣』才接得到（見下方惜售提醒）。")

    # A 池佈署截止日提醒
    try:
        deadline_dt = datetime.strptime(DCA_DEADLINE, '%Y-%m-%d')
        days_to_deadline = (deadline_dt - datetime.now()).days
        if 0 <= days_to_deadline <= 21:
            notes.append(f"📊 A 池佈署截止日 {DCA_DEADLINE} 還剩 {days_to_deadline} 天 —— 截止日未成交批次將市價補滿（保證 A 池佈署完，<2.2T 前提）")
        elif -3 <= days_to_deadline < 0:
            notes.append(f"⚠️ A 池佈署截止日已過（{DCA_DEADLINE}）—— 盤點：未成交批次市價補滿 A 池（<2.2T）；若已 >2.2T 則凍結餘額")
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
            notes.append(f"🔓 接近{desc}（注意：解鎖≠賣出。逾千員工組織 borrow-die 惜售，實際賣壓可能遠小於帳面解鎖量。B 池被動等，接不到是常態）")

    # B 池掛單期間提醒
    if 0 <= d <= LOCKUP_FLOOR_END_DAY:
        notes.append(f"📌 B 池 GTC 應掛滿至第 {LOCKUP_FLOOR_END_DAY} 天（~12 月中），目前第 {d} 天")
    elif d > LOCKUP_FLOOR_END_DAY:
        notes.append(f"✅ 已過第 {LOCKUP_FLOOR_END_DAY} 天，鎖倉瀑布跑完，主要供給壓力結束")

    # Firstrade GT90 重掛提醒（最長 90 天，撐不到 180 天）
    if abs(d - GT90_RELIST_DAY) <= 3:
        notes.append(f"🔁 接近第 {GT90_RELIST_DAY} 天：B 池 GT90 即將到期，需重掛第二批撐到第 {LOCKUP_FLOOR_END_DAY} 天（Firstrade 最長 GT90）")

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


def _render_followup_manual(dca_metrics):
    """A/B 池跟進手冊（v8.7，2026-07-31 起）

    背景判斷：A 池 7/1 截止已過、limit 階梯全數觸發（佈署 ~74%），只剩「補滿與否」
    一個人工決策；B 池 1.5T 錨已觸發，剩下是純日曆任務（GT90 重掛、180 天終點）。
    → A/B 從「進行中策略」轉為「跟進手冊」：把剩餘動作日曆化，8 月起重心移到
    C 池（Option Sage，見下方沉思者區塊與 PLAN_2026-08.md）。
    """
    d = days_since_ipo()
    ipo_dt = datetime.strptime(IPO_DATE, '%Y-%m-%d')

    def day_date(n):
        return (ipo_dt + timedelta(days=n)).strftime('%m/%d')

    md = "### 📒 A/B 池跟進手冊（剩餘動作日曆）\n\n"
    md += "_A/B 階段性佈署已近完成，以下是僅剩的人工動作。做完打勾，其餘時間不用想它們。_\n\n"
    md += "| 日期 | 天數 | 池 | 動作 | 狀態 |\n|---|---|---|---|---|\n"

    # A 池：補滿決策（唯一剩餘決策）
    fill_pct = dca_metrics.get('pool_a_filled_pct') if dca_metrics else None
    fill_str = f"目前 {fill_pct:.0f}%" if fill_pct is not None else "見上方 A 池表"
    md += (f"| 進行中 | — | A | 補滿決策：佈署未達 100%（{fill_str}）→ 買區內(<2.2T)限價補滿或明示放棄 | "
           f"{'✅ 已完成' if fill_pct is not None and fill_pct >= 100 else '⏳ 待決'} |\n")

    calendar = [
        (70,  'B', f"第 70 天解鎖 +7%（{day_date(70)}）——被動等，不動作"),
        (GT90_RELIST_DAY, 'B', f"**GT90 到期重掛**（{day_date(GT90_RELIST_DAY)}）——B 池未成交錨單全部重掛一次，撐到第 {LOCKUP_FLOOR_END_DAY} 天"),
        (105, 'B', f"第 105 天解鎖 +7%（{day_date(105)}）——被動等"),
        (120, 'B', f"第 120 天解鎖 +7%（{day_date(120)}）——被動等"),
        (135, 'B', f"第 135 天解鎖 +7%（{day_date(135)}）——被動等"),
        (LOCKUP_FLOOR_END_DAY, 'B', f"**第 {LOCKUP_FLOOR_END_DAY} 天瀑布終點**（{day_date(LOCKUP_FLOOR_END_DAY)}）——B 池任務結束，未成交餘額解編"),
    ]
    for day_n, pool, action in calendar:
        if d > day_n + 3:
            status = "✅ 已過"
        elif abs(d - day_n) <= 3:
            status = "🔔 **就是現在**"
        else:
            status = f"⏳ 還有 {day_n - d} 天"
        md += f"| {day_date(day_n)} | 第 {day_n} 天 | {pool} | {action} | {status} |\n"

    md += "\n_紀律不變：B 池接不到 = 沒崩 = 好事，絕不上調錨點追價；斷路器 >2.2T 擋一切新單。_\n\n"
    return md


def generate_report(stage, price, atm_iv, pc_ratio, gtc_levels_a, gtc_levels_b,
                    iv_stable, dca_metrics, peers):
    """生成 markdown 報告（v8.3：A 池首筆市價+階梯 / PC 方向修正 / IV 分位）"""
    md = "\n## 🚀 SPCX 太空雷達 (v8.7)\n\n"

    # === 論點破壞檢查清單（v8.6 兩級制：壞掉時照什麼表）===
    md += "### 🛑 論點破壞檢查 (Narrative Breakers) — 兩級制\n\n"
    md += "**Level 1（單一事件）→ 凍結新單、持倉不動、觀察一季：**\n"
    md += "- [ ] Starship 單次重大試飛失敗 / 里程碑延後（追蹤三里程碑：①首次真正入軌+真酬載 ②軌道燃料補加示範(目標 late 2026) ③V3 Starlink 首次實際部署）\n"
    md += "- [ ] Anthropic 或 Google 算力合約縮減（兩約皆 90 天可取消，是 xAI 板塊主要現金流）\n"
    md += "- [ ] Nasdaq 100 快速納入 (Fast-entry) 規則生變\n"
    md += "- [ ] SpaceX 與 Tesla/xAI 出現重大關聯交易疑慮或監管調查\n\n"
    md += "**Level 2（結構性破壞）→ 啟動有秩序減倉（反向 DCA），十年論點支點已斷：**\n"
    md += "- [ ] Starship 計畫實質放棄或無限期擱置（三里程碑連續失敗且無時程）\n"
    md += "- [ ] Starlink 用戶/營收連兩季 QoQ 轉負（成長引擎熄火）\n"
    md += "- [ ] Anthropic+Google 算力合約同時終止（xAI 外部現金流歸零）\n"
    md += "- [ ] Musk 喪失行為能力或離開（單一關鍵人風險）\n\n"
    md += "_「十年持股」的前提是「十年論點還活著」。Level 1 = 論點受傷，等它自證；Level 2 = 支點斷裂，不下車就從紀律變固執。_\n\n"

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

    # === A/B 池跟進手冊（v8.7：佈署近完成，剩餘動作日曆化）===
    md += _render_followup_manual(dca_metrics)

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
    """A 池：首筆高限價單(Firstrade 首日不收市價) + 4 筆 limit 階梯。表格含股數+實際金額。"""
    pool_a_amount = TOTAL_CAPITAL * POOL_A_DCA_PCT
    first = calc_a_first_tranche()

    md = f"### 📊 A 核心 DCA 池 {POOL_A_DCA_PCT*100:.0f}%（${pool_a_amount:,.0f}）— 首筆高限價 + limit 階梯\n\n"
    md += f"_Firstrade 首日不收市價單 → 首筆改「高限價 ${first['limit_price']:.0f}」(2.2T 上限) 最大化上車；股數用 IPO 價 ${first['shares_at']:.0f} 算（達標為主）。第 2–5 筆 limit 掛好就忘。截止日 {DCA_DEADLINE}。_\n\n"
    md += "| 批次 | 類型 | 目標市值 | 限價 | 股數 | 實際金額 | 狀態 |\n|---|---|---|---|---|---|---|\n"

    # 第 1 筆：高限價單
    if stage == 0:
        status1 = "上市首日掛限價"
    elif price is not None and price_to_mc_t(price) > HARD_CAP_T:
        status1 = "⚠️ >2.2T 斷路器，暫不掛"
    elif price is not None and price <= first['limit_price']:
        status1 = "✅ 限價內可成交（上車）"
    else:
        status1 = "⏳ 等回到限價內"
    md += f"| 1 | 限價(上車) | ≤2.2T | ${first['limit_price']:.2f} | {first['shares']} | ${first['budget']:,.0f}(預算) | {status1} |\n"

    # 第 2–5 筆 limit（含股數）
    for i, lv in enumerate(gtc_levels_a, start=2):
        if stage == 0 or price is None:
            status = "待上市掛單"
        elif price <= lv['price']:
            status = "✅ 已觸發"
        else:
            dist = (price / lv['price'] - 1) * 100
            status = f"⏳ 還需跌 {dist:.1f}%"
        md += f"| {i} | limit | {lv['target_mc_t']:.2f}T | ${lv['price']:.2f} | {lv['shares']} | ${lv['actual_amount']:,.0f} | {status} |\n"

    md += "\n"
    md += f"_⚠️ 首筆若真在 ${first['limit_price']:.0f} 成交，最壞金額 ${first['max_cost_if_filled_high']:,.0f}（超預算）——但那代表已近斷路器，本就該重評估。正常 ${first['shares_at']:.0f} 附近成交即達標。_\n"
    if stage == 0:
        md += f"_總股數 {TOTAL_SHARES_B}B、IPO 價 ${IPO_PRICE if IPO_PRICE else '未定'}。**6/11 定價通知確認後若有變，改 config 重算。**_\n"
    md += "\n"

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
        md += f"\n_截止日 {DCA_DEADLINE} 未投滿 → 未成交批次**限價補滿**（買區 <2.2T，掛高限價）或凍結（>2.2T）。目標：A 池保證佈署（上車優先）。_\n\n"
    elif stage >= 1:
        md += f"- _尚未開始 DCA，或 spcx_dca_log.json 未維護_\n\n"

    return md


def _render_pool_b_plan(gtc_levels_b, price, stage):
    """B 池：單向下檔 GTC，掛到 180 天"""
    pool_b_amount = TOTAL_CAPITAL * POOL_B_FLOOR_PCT
    md = f"### 💰 B 地板預備池 {POOL_B_FLOOR_PCT*100:.0f}%（${pool_b_amount:,.0f}）— 絕對市值定錨 GT90\n\n"
    md += f"_掛單與開盤價無關。Firstrade 最長 GT90（90天），故掛滿至第 {LOCKUP_FLOOR_END_DAY} 天需在第 {GT90_RELIST_DAY} 天重掛一次。_\n\n"
    if not gtc_levels_b:
        return md
    md += "| 目標市值 | 限價 | 股數 | 實際金額 | 距現價 | 狀態 |\n"
    md += "|---|---|---|---|---|---|\n"
    for lv in gtc_levels_b:
        if stage == 0 or price is None:
            dist_str, status = "—", "待上市掛單"
        else:
            dist = (price / lv['price'] - 1) * 100
            dist_str = f"{dist:+.1f}%"
            status = "✅ 已觸發" if price <= lv['price'] else f"⏳ 還需跌 {dist:.1f}%"
        md += f"| {lv['target_mc_t']:.1f}T | ${lv['price']:.2f} | {lv['shares']} | ${lv['actual_amount']:,.0f} | {dist_str} | {status} |\n"
    md += "\n"
    md += "> **B 池是後段武器，不是前期戰力。**\n"
    md += "> - 前期真空期幾乎不會成交（只有 IPO 新股流通、鎖倉未解）。\n"
    md += f"> - **Firstrade GT90 限制：第 {GT90_RELIST_DAY} 天 GT90 到期，需重掛第二批撐到第 {LOCKUP_FLOOR_END_DAY} 天。**\n"
    md += "> - 真正可能成交的窗口：**7 月底 Q2 財報+首波解鎖 → 秋季 Anthropic/OpenAI IPO 抽走資金 → 10 月底 Q3 大解鎖(+28%)**。\n"
    md += "> - 解鎖≠賣出：員工惜售(borrow-die)下，賣壓可能是溫水非海嘯，B 池可能整段不成交。\n"
    md += "> - **接不到 = 沒崩 = 好事**（你的 A 池十年倉在賺）。**絕不可因接不到而上調錨點追價**——那就破功了。\n\n"
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
    print(f"🚀 啟動 SPCX 太空雷達 v8.7: {datetime.now().strftime('%Y-%m-%d')}")
    spcx_common.ensure_dirs()

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
        'version': 'v8.7',
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
