"""
spcx_options.py — SPCX Option Sage（C 池的沉思者）

定位：C 池的進場環境 gate。回合制（D+1）跑，大部分時間勸你等，
只在四條件全中、最有把握、非常不容錯過時，才亮那一盞「就是這個」的燈。

重劍無鋒，大巧不工。湯姆熊（optscnr）是獨孤九劍——料敵機先、主動出擊、冒險；
這邊是降龍十八掌——招式人盡皆知，但大部分時間沉穩不發，
時機與內力的純度決定那一掌，寧可一年不出手，不出錯手。

身份邊界（釘死，防長歪）：
- 是：選擇權市場「結構分期」監控 + C 池環境 gate
- 不是：選擇權訊號產生器（不建議 strike / 到期日 / 進場時機）
- 不是：湯姆熊的選擇權版（湯姆熊找爆發，這邊等純度）
- 不碰 A/B 池（那是 space_radar 的事）

執行模式：回合制 D+1，每個交易日收盤後跑一次，當作桌遊的一個回合。
不追即時報價、不盤中盯盤（這本身就是紀律）。

與 space_radar.py 的關係：
- 獨立檔，自己跑
- 共用 spcx_config.json（單一真相來源，唯讀）
- 唯讀 spcx_iv_history.csv（space_radar 是唯一寫入者，避免打架）
- 自己另記 spcx_options_history.csv（選擇權結構時序）

輸出三層（絕大部分回合停在 L0/L1，L2 極稀有）：
- L0 靜默/提醒：機會存在，但現在不是時候，睡
- L1 觀察：環境在變，持續觀察，還不到
- L2 出手：四條件全中，就是這個（門檻刻意設極高，可能整年不亮）

可變參數：spcx_config.json（沿用 space_radar 的 config，新增 options_* 欄位）
頻率：每個交易日收盤後跑一次（D+1）

【sage_v0.2 改動】（2026-07-31，8 月 C 池預備。詳見 PLAN_2026-08.md）
- 整併進 spcx_radar/：路徑與共用函式（config/現價/ATM IV/分位）統一走 spcx_common
- 開始記錄 LEAPS 專屬 IV（最長天期 LEAPS 的 ATM IV）：
  近月 ATM IV 不能代表 LEAPS 保費，等 IV 崩了才開始記就沒有基準了——
  在崩之前先把序列建起來，是 C 池專用模組此刻存在的主要理由
- viewpoint 範例偵測：觀點欄還是「（範例）」字樣時明確警示「未填真觀點」，
  不讓範例文字漲信心後誤觸 gate
- gates 全部不動（嚴防線 55%、四條件 AND 不放寬）
"""
import yfinance as yf
import pandas as pd
import json
import os
import logging
from datetime import datetime, timedelta

import spcx_common

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# === 共用 space_radar 的 config（單一真相來源，路徑統一由 spcx_common 管）===
CONFIG_PATH = spcx_common.CONFIG_PATH
IV_HISTORY_PATH = spcx_common.IV_HISTORY_PATH            # 唯讀（space_radar 寫）
OPTIONS_HISTORY_PATH = spcx_common.OPTIONS_HISTORY_PATH  # 本模組自己寫
VIEWPOINT_PATH = spcx_common.VIEWPOINT_PATH              # 觀點欄位（user 手動填）
OUTPUT_PATH = spcx_common.OPTIONS_JSON
REPORT_PATH = spcx_common.OPTIONS_REPORT

# 本模組專屬的預設值（嚴起點，全部可在 config 覆蓋）
_OPTION_DEFAULTS = {
    'ticker': 'SPCX',
    'ipo_date': '2026-06-12',
    'total_shares_b': 13.16,
    # --- IV gate（決定一：嚴防線）---
    'opt_iv_pctile_calm': 40,        # IV 分位 ≤ 此值 = 相對冷卻（沿用 space_radar 精神）
    'opt_iv_abs_acceptable': 0.55,   # 【嚴防線】絕對 IV ≤ 55% 才算「絕對可接受」
    'opt_iv_stable_days': 3,         # 連續幾天都滿足才算穩定
    'opt_iv_pctile_min_samples': 10, # IV 歷史少於此，分位不可信
    # --- 流動性 gate（決定二：保守起點，可校準）---
    'opt_liq_min_total_int': 500,    # LEAPS 鏈 INT 總和門檻
    'opt_liq_min_strike_int': 50,    # 單一可用 strike 的 INT 門檻
    'opt_liq_max_spread_pct': 0.08,  # bid-ask 價差佔中價 ≤ 8%
    'opt_liq_min_total_vol': 100,    # LEAPS 鏈成交量總和門檻
    # --- LEAPS 定義 ---
    'opt_leaps_min_days': 365,       # 到期 ≥ 365 天才算 LEAPS（深價內長天期）
    'opt_leaps_min_year': 2027,      # 或到期年份 ≥ 2027
    'opt_deep_itm_delta': 0.80,      # delta ≥ 此值才算「深價內」（用 moneyness 近似）
    'opt_deep_itm_moneyness': 0.85,  # strike ≤ 現價 × 此值 = 深價內（delta 抓不到時的近似）
    # --- 觀點 gate（決定三：信心分數）---
    'opt_viewpoint_min_confidence': 4,  # 【嚴起點】觀點信心 ≥ 4（滿分 5）才算 gate 通過
    # --- gate 模式（PLAN_2026-10 patch 1：三條線並算，只有這個決定 L2；預設 near＝現狀）---
    'opt_gate_mode': 'near',             # near / leaps / carry
    'opt_leaps_iv_pctile_calm': 40,      # leaps 模式：LEAPS IV 分位 ≤ 此值
    'opt_leaps_iv_abs_acceptable': 0.55, # leaps 模式：LEAPS IV 絕對值 ≤ 此值
    'opt_max_carry_pct': 5.0,            # carry 模式：深價內 LEAPS 外在價值年化 % ≤ 此值
}


def load_config():
    """讀 spcx_config.json + 補本模組預設值（spcx_common 統一載入）。
    共用 space_radar 的基礎參數（股數等），加上 options 專屬閾值。
    """
    cfg = spcx_common.load_config(
        _OPTION_DEFAULTS, extra_passthrough_keys=('ticker', 'ipo_date', 'total_shares_b'))
    print(f"📋 已讀取 config（股數 {cfg['total_shares_b']}B）"
          f"｜IV 嚴防線 ≤{cfg['opt_iv_abs_acceptable']*100:.0f}%"
          f"｜觀點信心門檻 {cfg['opt_viewpoint_min_confidence']}/5")
    return cfg


_CFG = load_config()
TICKER = _CFG['ticker']
IPO_DATE = _CFG['ipo_date']
TOTAL_SHARES_B = _CFG['total_shares_b']
IV_PCTILE_CALM = _CFG['opt_iv_pctile_calm']
IV_ABS_ACCEPTABLE = _CFG['opt_iv_abs_acceptable']
IV_STABLE_DAYS = _CFG['opt_iv_stable_days']
IV_PCTILE_MIN_SAMPLES = _CFG['opt_iv_pctile_min_samples']
LIQ_MIN_TOTAL_INT = _CFG['opt_liq_min_total_int']
LIQ_MIN_STRIKE_INT = _CFG['opt_liq_min_strike_int']
LIQ_MAX_SPREAD_PCT = _CFG['opt_liq_max_spread_pct']
LIQ_MIN_TOTAL_VOL = _CFG['opt_liq_min_total_vol']
LEAPS_MIN_DAYS = _CFG['opt_leaps_min_days']
LEAPS_MIN_YEAR = _CFG['opt_leaps_min_year']
DEEP_ITM_MONEYNESS = _CFG['opt_deep_itm_moneyness']
VIEWPOINT_MIN_CONFIDENCE = _CFG['opt_viewpoint_min_confidence']
GATE_MODE = str(_CFG['opt_gate_mode']).lower() if str(_CFG['opt_gate_mode']).lower() in ('near', 'leaps', 'carry') else 'near'
LEAPS_IV_PCTILE_CALM = _CFG['opt_leaps_iv_pctile_calm']
LEAPS_IV_ABS_ACCEPTABLE = _CFG['opt_leaps_iv_abs_acceptable']
MAX_CARRY_PCT = _CFG['opt_max_carry_pct']
GATE_MODES = ('near', 'leaps', 'carry')


def days_since_ipo():
    return spcx_common.days_since_ipo(IPO_DATE)


# ============================================================
# 訊號 1：IV 水位（雙軌——相對分位 + 絕對值，兩個都報）
# ============================================================
def _iv_gate(series, current_iv, pctile_calm, abs_ok, stable_days, min_samples=None):
    """泛化的 IV gate（patch 1）：輸入一條 IV 序列（已含當前值、舊→新）與當前值，
    回傳 {atm_iv, pctile, n_samples, rel_calm, abs_acceptable, stable}。
    near 與 leaps 兩種模式只差序列來源與閾值。純函式，回填可直接餵截斷後的序列。"""
    min_samples = IV_PCTILE_MIN_SAMPLES if min_samples is None else min_samples
    result = {'atm_iv': current_iv, 'pctile': None, 'n_samples': 0,
              'rel_calm': False, 'abs_acceptable': False, 'stable': False}
    if current_iv is None:
        return result
    result['abs_acceptable'] = current_iv <= abs_ok     # 絕對防線（嚴）：與相對分位完全獨立
    ivs = [float(x) for x in (series or []) if x is not None and not pd.isna(x)]
    n = len(ivs)
    result['n_samples'] = n
    if n >= min_samples:
        s = pd.Series(ivs)
        pctile = float((s < current_iv).sum()) / n * 100
        result['pctile'] = round(pctile, 1)
        result['rel_calm'] = pctile <= pctile_calm
        # 穩定：最近 N 個值的分位都 ≤ calm（序列尾端含當前值）
        recent = ivs[-stable_days:]
        if len(recent) >= stable_days:
            result['stable'] = all(float((s < iv).sum()) / n * 100 <= pctile_calm for iv in recent)
    return result


def _load_series(path, col, before_date=None):
    """讀 history 某欄成 list（舊→新）；before_date 給了就只取日期 < 它的列（回填／leaps 用）。"""
    if not os.path.exists(path):
        return []
    try:
        df = pd.read_csv(path)
        if col not in df.columns:
            return []
        if before_date is not None and 'date' in df.columns:
            df = df[df['date'].astype(str) < str(before_date)]
        return [float(x) for x in df.sort_values('date')[col].dropna()] if 'date' in df.columns \
            else [float(x) for x in df[col].dropna()]
    except Exception:
        return []


def get_iv_signal(current_atm_iv):
    """near 模式（現狀）：近月 ATM IV 對 space_radar 的 spcx_iv_history.csv（唯讀）算分位。
    關鍵：rel_calm 與 abs_acceptable 是兩件事——分位會說「78% 算冷卻」，絕對值 78% 仍貴。
    IV 歷史檔由 space_radar 先寫、已含今天，所以序列直接用整檔。"""
    return _iv_gate(_load_series(IV_HISTORY_PATH, 'atm_iv'), current_atm_iv,
                    IV_PCTILE_CALM, IV_ABS_ACCEPTABLE, IV_STABLE_DAYS)


def get_leaps_iv_signal(current_leaps_iv, market_date=None):
    """leaps 模式：同一套邏輯，輸入換成最長天期 LEAPS 的 ATM IV，分位對 Sage 自己的
    spcx_options_history.csv 的 leaps_atm_iv 序列算。history 還沒寫今天，所以序列＝舊列＋當前值。"""
    series = _load_series(OPTIONS_HISTORY_PATH, 'leaps_atm_iv', before_date=market_date) + \
        ([current_leaps_iv] if current_leaps_iv is not None else [])
    return _iv_gate(series, current_leaps_iv, LEAPS_IV_PCTILE_CALM, LEAPS_IV_ABS_ACCEPTABLE, IV_STABLE_DAYS)


# ============================================================
# 訊號 1c：隱含融資成本（carry 模式，patch 1）
# ============================================================
def carry_of(strike_row, price, market_date):
    """單一深價內 strike 的 carry：extrinsic / price / (DTE/365) × 100。
    深價內 LEAPS 的真實成本是外在價值不是 IV；這是「用 LEAPS 借錢持股」的隱含年利率。
    回傳 dict（含 dte / intrinsic / extrinsic / carry_pct_annual），DTE ≤ 0 或資料不足回 None。"""
    try:
        exp_dt = datetime.strptime(str(strike_row['exp'])[:10], '%Y-%m-%d').date()
        md = market_date if hasattr(market_date, 'year') else datetime.strptime(str(market_date)[:10], '%Y-%m-%d').date()
        dte = (exp_dt - md).days
        bid, ask = float(strike_row['bid']), float(strike_row['ask'])
        if dte <= 0 or bid <= 0 or ask <= 0 or not price:
            return None
        mid = (bid + ask) / 2
        intrinsic = max(price - float(strike_row['strike']), 0.0)
        extrinsic = mid - intrinsic
        if extrinsic < 0:
            # 中價低於內在價值＝報價過期或套利假象（10/15 回填看到 -1.9%），不能當「便宜」計入
            return None
        return {'dte': dte, 'mid': round(mid, 2), 'intrinsic': round(intrinsic, 2),
                'extrinsic': round(extrinsic, 2),
                'carry_pct_annual': round(extrinsic / price / (dte / 365) * 100, 2)}
    except Exception:
        return None


def get_carry_signal(liq_sig, price, market_date):
    """對所有深價內可用 strike（liq_sig['usable_all']，不只報告的前 5 名）算 carry，取最小。
    gate = 最小 carry ≤ MAX_CARRY_PCT 且連續 IV_STABLE_DAYS 天（穩定看 history 的 min_carry_pct）。
    順手把 carry 欄位寫進 liq_sig['detail'] 的每筆（brief 原樣轉發，不另算）。"""
    result = {'min_carry_pct': None, 'best_strike': None, 'ok': False, 'stable': False,
              'threshold': MAX_CARRY_PCT, 'n_strikes': 0}
    best = None
    for s in liq_sig.get('usable_all') or liq_sig.get('detail') or []:
        c = carry_of(s, price, market_date)
        if c is None:
            continue
        result['n_strikes'] += 1
        if best is None or c['carry_pct_annual'] < best['carry_pct_annual']:
            best = {**s, **c}
    for s in liq_sig.get('detail') or []:
        c = carry_of(s, price, market_date)
        if c:
            s.update(c)
    if best is None:
        return result
    result['min_carry_pct'] = best['carry_pct_annual']
    result['best_strike'] = {k: best[k] for k in ('exp', 'strike', 'bid', 'ask', 'oi', 'dte', 'intrinsic', 'extrinsic', 'carry_pct_annual')}
    result['ok'] = best['carry_pct_annual'] <= MAX_CARRY_PCT
    prev = _load_series(OPTIONS_HISTORY_PATH, 'min_carry_pct', before_date=market_date)
    recent = prev[-(IV_STABLE_DAYS - 1):] if IV_STABLE_DAYS > 1 else []
    result['stable'] = result['ok'] and len(recent) >= IV_STABLE_DAYS - 1 and all(x <= MAX_CARRY_PCT for x in recent)
    return result


# ============================================================
# 訊號 2：流動性深度（新增——C 池能不能「下單」的真 gate）
# ============================================================
def get_liquidity_signal(tk, current_price):
    """抓 LEAPS 鏈的流動性深度。這是 space_radar 沒有、但你親自發現最關鍵的 gate。

    回傳 dict：
      - has_leaps（有沒有 ≥2027 / ≥365天 的到期）
      - total_int（LEAPS 鏈 INT 總和）
      - total_vol
      - usable_strikes（深價內 + INT 足 + 價差窄的 strike 數）
      - best_spread_pct（最好的價差佔比）
      - liquid（三門檻都過 = 可下單）
      - detail（給報告用的可用 strike 清單）
    """
    result = {
        'has_leaps': False, 'total_int': 0, 'total_vol': 0,
        'usable_strikes': 0, 'best_spread_pct': None, 'liquid': False,
        'detail': [],
        # sage_v0.2：LEAPS 專屬 IV（最長天期 LEAPS 的 ATM IV）。
        # 近月 ATM IV 不能代表 LEAPS 保費——C 池買的是 LEAPS，gate 的基準也該是 LEAPS 的序列。
        'leaps_atm_iv': None, 'leaps_iv_exp': None,
    }
    try:
        exps = tk.options
    except Exception:
        exps = None
    if not exps:
        return result

    today = datetime.now()
    # 找符合 LEAPS 定義的到期日（≥365天 或 年份≥2027）
    leaps_exps = []
    for exp in exps:
        try:
            exp_dt = datetime.strptime(exp, '%Y-%m-%d')
        except Exception:
            continue
        days = (exp_dt - today).days
        if days >= LEAPS_MIN_DAYS or exp_dt.year >= LEAPS_MIN_YEAR:
            leaps_exps.append((exp, exp_dt, days))

    if not leaps_exps:
        return result
    result['has_leaps'] = True

    total_int = 0
    total_vol = 0
    usable = []
    best_spread = None

    # 深價內門檻：strike ≤ 現價 × moneyness
    deep_itm_strike_max = current_price * DEEP_ITM_MONEYNESS

    # 最長天期的 LEAPS 到期日（LEAPS IV 序列的取樣點，固定取最遠端以保持序列一致性）
    longest_exp = max(leaps_exps, key=lambda x: x[2])[0]

    for exp, exp_dt, days in leaps_exps:
        try:
            calls = tk.option_chain(exp).calls.copy()
        except Exception:
            continue
        if calls.empty:
            continue

        total_int += int(calls['openInterest'].fillna(0).sum())
        total_vol += int(calls['volume'].fillna(0).sum())

        # sage_v0.2：記錄最長天期 LEAPS 的 ATM IV（與 spcx_common.calc_atm_iv 同一套算法）
        if exp == longest_exp:
            leaps_iv = spcx_common.calc_atm_iv(calls, current_price)
            if leaps_iv is not None:
                result['leaps_atm_iv'] = round(leaps_iv, 4)
                result['leaps_iv_exp'] = exp

        # 只看深價內 call（C 池的工具：delta≈1 的長天期）
        deep = calls[calls['strike'] <= deep_itm_strike_max].copy()
        for _, row in deep.iterrows():
            bid = row.get('bid', 0) or 0
            ask = row.get('ask', 0) or 0
            oi = int(row.get('openInterest', 0) or 0)
            if bid <= 0 or ask <= 0:
                continue
            mid = (bid + ask) / 2
            spread_pct = (ask - bid) / mid if mid > 0 else 1.0
            if best_spread is None or spread_pct < best_spread:
                best_spread = spread_pct
            # 可用 strike：INT 足 + 價差窄
            if oi >= LIQ_MIN_STRIKE_INT and spread_pct <= LIQ_MAX_SPREAD_PCT:
                usable.append({
                    'exp': exp, 'strike': float(row['strike']),
                    'oi': oi, 'spread_pct': round(spread_pct, 3),
                    'bid': round(bid, 2), 'ask': round(ask, 2),
                })

    result['total_int'] = total_int
    result['total_vol'] = total_vol
    result['usable_strikes'] = len(usable)
    result['best_spread_pct'] = round(best_spread, 3) if best_spread is not None else None
    result['detail'] = sorted(usable, key=lambda x: x['spread_pct'])[:5]
    # patch 1：carry 要看全部深價內可用 strike，不只報告的前 5 名（不進報告，只給 get_carry_signal）
    result['usable_all'] = sorted(usable, key=lambda x: x['spread_pct'])

    # 流動性過關：總 INT + 總量 + 至少一個可用 strike
    result['liquid'] = (
        total_int >= LIQ_MIN_TOTAL_INT and
        total_vol >= LIQ_MIN_TOTAL_VOL and
        len(usable) >= 1
    )
    return result


# ============================================================
# 訊號 3：skew 方向（市場在恐慌什麼）
# ============================================================
def get_skew_signal(tk, current_price):
    """算 call skew vs put skew。用近月（流動性最好）的 OTM call IV vs OTM put IV。

    回傳 dict：
      - skew_type: 'call'（單邊狂熱）/ 'put'（避險恐慌）/ 'neutral' / None
      - call_iv, put_iv（等距 OTM）
      - pc_vol_ratio（put/call 成交量比，輔助）
    """
    result = {'skew_type': None, 'call_iv': None, 'put_iv': None, 'pc_vol_ratio': None}
    try:
        exps = tk.options
    except Exception:
        exps = None
    if not exps:
        return result

    today = datetime.now()
    # 找最近、但 ≥14 天的到期（避免快到期的雜訊）
    target_exp = None
    for exp in exps:
        try:
            exp_dt = datetime.strptime(exp, '%Y-%m-%d')
        except Exception:
            continue
        if (exp_dt - today).days >= 14:
            target_exp = exp
            break
    if target_exp is None:
        return result

    try:
        chain = tk.option_chain(target_exp)
        calls, puts = chain.calls.copy(), chain.puts.copy()
    except Exception:
        return result
    if calls.empty or puts.empty:
        return result

    # 等距 OTM：call 取現價 ×1.1 附近，put 取現價 ×0.9 附近
    otm_call_strike = current_price * 1.10
    otm_put_strike = current_price * 0.90
    try:
        c_row = calls.iloc[(calls['strike'] - otm_call_strike).abs().argsort()[:1]]
        p_row = puts.iloc[(puts['strike'] - otm_put_strike).abs().argsort()[:1]]
        call_iv = float(c_row['impliedVolatility'].iloc[0])
        put_iv = float(p_row['impliedVolatility'].iloc[0])
        result['call_iv'] = round(call_iv, 3)
        result['put_iv'] = round(put_iv, 3)
        # skew 判定：差距 > 10% 相對才算明顯偏向
        if call_iv > put_iv * 1.10:
            result['skew_type'] = 'call'
        elif put_iv > call_iv * 1.10:
            result['skew_type'] = 'put'
        else:
            result['skew_type'] = 'neutral'
    except Exception:
        pass

    # PC volume ratio（輔助）
    try:
        cv = float(calls['volume'].fillna(0).sum())
        pv = float(puts['volume'].fillna(0).sum())
        if cv >= 1 and pv >= 1:
            result['pc_vol_ratio'] = round(pv / cv, 3)
    except Exception:
        pass
    return result


# ============================================================
# 階段判斷（三訊號組合 → P0/P1/P2）
# ============================================================
def determine_phase(iv_sig, liq_sig, skew_sig):
    """組合三訊號判斷選擇權市場結構分期。

    P0 真空狂熱：IV 虛高（無基準或分位高）+ 流動性極淺 + call skew
    P1 流動性建立：IV 開始有基準、回落中 + 流動性建立中
    P2 解鎖供給：IV 再升（真實 event）+ 流動性已建立 + 可能 put skew

    回傳 (phase_code, phase_label)
    """
    has_basis = iv_sig['pctile'] is not None
    liquid = liq_sig['liquid']
    leaps = liq_sig['has_leaps']

    # P0：流動性還沒建立（最硬的判據）
    if not leaps or liq_sig['total_int'] < LIQ_MIN_TOTAL_INT:
        return 'P0', 'P0 真空狂熱期（流動性未建立，連市場都還沒成形）'

    # 流動性建立了，看 IV 性質決定 P1/P2
    if skew_sig['skew_type'] == 'put':
        # put skew = 避險恐慌 = 解鎖供給期特徵
        return 'P2', 'P2 解鎖供給期（流動性已建立，put skew 顯示避險恐慌）'

    if liquid and iv_sig['rel_calm']:
        return 'P1', 'P1 流動性建立期（IV 回落 + 流動性建立，可能的進場窗）'

    # 流動性有了但 IV 還高
    return 'P1', 'P1 流動性建立期（流動性建立中，IV 尚未冷卻）'


# ============================================================
# 觀點 gate（決定三：信心分數，user 手動填）
# ============================================================
def get_viewpoint_signal():
    """讀 user 手動填的觀點檔。模組不自己生觀點，只檢查有沒有 + 信心夠不夠。

    spcx_c_viewpoint.json 範例：
    {
      "active": true,
      "catalyst": "2027 S&P 500 納入前的獲利驗證",
      "thesis": "市場低估 Q3 Starlink ARPU 提升速度",
      "confidence": 4,
      "updated": "2026-08-15"
    }
    回傳 dict：has_viewpoint, confidence, passes（信心 ≥ 門檻）, detail
    """
    result = {'has_viewpoint': False, 'confidence': 0, 'passes': False, 'detail': None,
              'is_placeholder': False}
    if not os.path.exists(VIEWPOINT_PATH):
        return result
    try:
        with open(VIEWPOINT_PATH) as f:
            vp = json.load(f)
        if not vp.get('active'):
            return result
        conf = int(vp.get('confidence', 0))
        catalyst = vp.get('catalyst', '')
        thesis = vp.get('thesis', '')
        # sage_v0.2：範例偵測——欄位還是「（範例）」字樣 = 真觀點未填。
        # 防的是：日後把 confidence 改上去卻忘了換文字，讓範例誤觸 gate。
        placeholder = ('（範例）' in catalyst) or ('（範例）' in thesis)
        result['has_viewpoint'] = True
        result['confidence'] = conf
        result['is_placeholder'] = placeholder
        result['passes'] = (conf >= VIEWPOINT_MIN_CONFIDENCE) and not placeholder
        result['detail'] = {
            'catalyst': catalyst,
            'thesis': thesis,
            'updated': vp.get('updated', ''),
        }
    except Exception:
        pass
    return result


# ============================================================
# 出手判斷（L2：四條件硬性 AND，缺一不亮）
# ============================================================
def evaluate_action_level(iv_sig, liq_sig, viewpoint_sig, iv_leaps=None, carry=None, gate_mode=None):
    """三層輸出判斷。L2 門檻刻意設極高。

    四條件硬性 AND（缺一不亮 L2）：
      1. IV 相對冷卻且穩定（rel_calm + stable）
      2. IV 絕對可接受（abs_acceptable，嚴防線）
      3. 流動性過關（liquid）
      4. 觀點信心達標（viewpoint passes）
    patch 1：前兩條由 gate_mode 決定量哪把尺（near=近月 ATM IV／leaps=LEAPS IV／carry=隱含融資成本），
    後兩條不變。conditions 的 key 帶模式名，報告才看得出用的是哪條。

    回傳 (level, conditions)：level ∈ {'L0','L1','L2'}
    """
    mode = (gate_mode or GATE_MODE)
    empty = {'rel_calm': False, 'stable': False, 'abs_acceptable': False}
    gates = {
        'near': ((iv_sig['rel_calm'] and iv_sig['stable']), iv_sig['abs_acceptable'], 'IV 相對冷卻且穩定', 'IV 絕對可接受（≤防線）'),
        'leaps': (((iv_leaps or empty)['rel_calm'] and (iv_leaps or empty)['stable']), (iv_leaps or empty)['abs_acceptable'],
                  'LEAPS IV 相對冷卻且穩定', 'LEAPS IV 絕對可接受（≤防線）'),
        'carry': (bool((carry or {}).get('stable')), bool((carry or {}).get('ok')),
                  '隱含融資成本連續達標', '隱含融資成本 ≤ 門檻'),
    }
    if mode not in gates:
        mode = 'near'
    c1, c2, k1, k2 = gates[mode]
    c3 = liq_sig['liquid']
    c4 = viewpoint_sig['passes']

    conditions = {
        f'{k1}（{mode}）': c1,
        f'{k2}（{mode}）': c2,
        '流動性過關': c3,
        '觀點信心達標': c4,
    }

    if all(conditions.values()):
        return 'L2', conditions

    # L1：環境在變（流動性建立 OR 該模式的「相對冷卻」），但四條件未齊
    rel = iv_sig['rel_calm'] if mode == 'near' else ((iv_leaps or empty)['rel_calm'] if mode == 'leaps' else bool((carry or {}).get('ok')))
    if c3 or rel:
        return 'L1', conditions

    # L0：靜默，還早
    return 'L0', conditions


def levels_by_mode(iv_sig, liq_sig, viewpoint_sig, iv_leaps, carry):
    """三種 gate 模式各自會給的 level（不管 config 指哪個）——12/9 復盤的關鍵欄。"""
    return {m: evaluate_action_level(iv_sig, liq_sig, viewpoint_sig, iv_leaps, carry, gate_mode=m)[0]
            for m in GATE_MODES}


# ============================================================
# 歷史記錄（本模組自己寫，唯一寫入者）
# ============================================================
def record_options_history(price, iv_sig, liq_sig, skew_sig, phase, record_date=None,
                           level=None, iv_leaps=None, carry=None, levels=None, gate_mode=None):
    """結構時序（本模組唯一寫入者）。

    2026-10-21（PLAN_2026-10_c_pool_alert）：加 `level` 與 `transition` 兩欄。
    9/4–10/15 L2 亮了 21 個交易日沒人看到，事後要證明亮過得翻 git——判定從此進 history。
    transition：與 history 最後一筆（日期早於本筆）的 level 比，不同就記 "L1->L2" 這種字串，否則空。
    patch 1：加三條 gate 線的欄位（leaps_* / min_carry_pct / carry_* / gate_mode / level_near|leaps|carry），
    12/9 復盤直接 groupby 看三條線各亮了幾天、分歧在哪。
    """
    iv_leaps = iv_leaps or {}
    carry = carry or {}
    levels = levels or {}
    record = {
        'date': (record_date or datetime.now().strftime('%Y-%m-%d')),
        'price': round(price, 2) if price else None,
        'atm_iv': iv_sig['atm_iv'],
        'iv_pctile': iv_sig['pctile'],
        # sage_v0.2：LEAPS 專屬 IV 序列（在 IV 崩之前先建基準）
        'leaps_atm_iv': liq_sig.get('leaps_atm_iv'),
        'leaps_iv_exp': liq_sig.get('leaps_iv_exp'),
        'total_int': liq_sig['total_int'],
        'total_vol': liq_sig['total_vol'],
        'usable_strikes': liq_sig['usable_strikes'],
        'best_spread_pct': liq_sig['best_spread_pct'],
        'skew_type': skew_sig['skew_type'],
        'phase': phase,
        'level': level,
        'transition': None,
        'leaps_pctile': iv_leaps.get('pctile'),
        'leaps_rel_calm': iv_leaps.get('rel_calm'),
        'leaps_abs_ok': iv_leaps.get('abs_acceptable'),
        'leaps_stable': iv_leaps.get('stable'),
        'min_carry_pct': carry.get('min_carry_pct'),
        'carry_ok': carry.get('ok'),
        'carry_stable': carry.get('stable'),
        'gate_mode': gate_mode or GATE_MODE,
        'level_near': levels.get('near'),
        'level_leaps': levels.get('leaps'),
        'level_carry': levels.get('carry'),
    }
    if os.path.exists(OPTIONS_HISTORY_PATH):
        df = pd.read_csv(OPTIONS_HISTORY_PATH)
        df = df[df['date'] != record['date']]
        prev = df[df['date'] < record['date']].sort_values('date')
        if level is not None and 'level' in prev.columns and len(prev):
            prev_level = prev['level'].dropna()
            prev_level = str(prev_level.iloc[-1]) if len(prev_level) else None
            if prev_level and prev_level != level:
                record['transition'] = f"{prev_level}->{level}"
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True).sort_values('date')
    else:
        df = pd.DataFrame([record])
    df.to_csv(OPTIONS_HISTORY_PATH, index=False)
    return df


# ============================================================
# 報告生成（沉思者的聲音，三層）
# ============================================================
def generate_report(price, iv_sig, liq_sig, skew_sig, phase_code, phase_label,
                    viewpoint_sig, level, conditions, iv_leaps=None, carry=None, levels=None):
    iv_leaps = iv_leaps or {}
    carry = carry or {}
    levels = levels or {}
    md = "\n## 🧘 SPCX Option Sage（C 池沉思者）\n\n"
    md += f"_回合制 D+1｜{datetime.now().strftime('%Y-%m-%d')}（上市第 {days_since_ipo()} 天）_\n\n"

    if price is None:
        md += "_選擇權市場尚未成形或無資料。本回合：靜默。睡。_\n\n"
        return md

    # 階段
    md += f"**選擇權市場結構**：{phase_label}\n\n"

    # 三訊號儀表
    md += "### 三結構訊號\n\n"
    ok = lambda b: '✅' if b else '❌'
    # patch 1：三條 gate 線並列（現行 gate 加粗），分歧本身就是 12/9 要看的證據
    def _iv_line(name, mode, sig):
        cur = f"{sig['atm_iv']*100:.0f}%" if sig.get('atm_iv') else "—"
        pct = f"分位 {sig['pctile']:.0f}" if sig.get('pctile') is not None else f"分位無基準(n={sig.get('n_samples', 0)})"
        label = f"**{name}（{mode}｜現行 gate）**" if GATE_MODE == mode else f"{name}（{mode}）"
        return (f"- {label}：{cur}｜{pct}｜相對冷卻 {ok(sig.get('rel_calm'))} 絕對 {ok(sig.get('abs_acceptable'))}"
                f" 穩定 {ok(sig.get('stable'))}｜單獨判定 {levels.get(mode, '—')}\n")
    md += _iv_line("IV 水位", "near", iv_sig)
    md += _iv_line("LEAPS IV", "leaps", {**iv_leaps, 'atm_iv': liq_sig.get('leaps_atm_iv')})
    bs = carry.get('best_strike') or {}
    clabel = "**隱含融資成本（carry｜現行 gate）**" if GATE_MODE == 'carry' else "隱含融資成本（carry）"
    if carry.get('min_carry_pct') is not None:
        md += (f"- {clabel}：{carry['min_carry_pct']:.1f}%/年（{bs.get('exp')} ${bs.get('strike', 0):.0f}C，外在 {bs.get('extrinsic')}）"
               f"｜門檻 {carry.get('threshold', MAX_CARRY_PCT):.1f}%｜{ok(carry.get('ok'))} 連續 {ok(carry.get('stable'))}｜單獨判定 {levels.get('carry', '—')}\n")
    else:
        md += f"- {clabel}：無可用深價內 strike，無法計算\n"
    if iv_sig['rel_calm'] and not iv_sig['abs_acceptable']:
        md += f"  - ⚠️ **相對冷卻但絕對仍貴**：分位說便宜，但近月 IV 對買 LEAPS 仍是貴保費。嚴防線擋住，正確。\n"
    if levels and len(set(levels.values())) > 1:
        md += f"  - 🔀 **三條線分歧**：near {levels.get('near')}／leaps {levels.get('leaps')}／carry {levels.get('carry')}。深價內 LEAPS 的真實成本是外在價值，不是近月 IV——12/9 復盤用 history 的 level_* 欄選尺。\n"
    # 流動性
    md += f"- **流動性深度**：{'✅ 可下單' if liq_sig['liquid'] else '❌ 未達標'}"
    md += f"（LEAPS INT 總和 {liq_sig['total_int']}/門檻{LIQ_MIN_TOTAL_INT}"
    md += f"，可用 strike {liq_sig['usable_strikes']} 個"
    if liq_sig['best_spread_pct'] is not None:
        md += f"，最佳價差 {liq_sig['best_spread_pct']*100:.1f}%"
    md += ")\n"
    if liq_sig['has_leaps'] and not liq_sig['liquid']:
        md += f"  - ⚠️ LEAPS 已掛出但流動性不足（INT 太低/價差太寬）——市場剛開張，報價可能失真，不能碰。\n"
    # skew
    skew_map = {'call': 'call skew（單邊買 call 狂熱）', 'put': 'put skew（避險恐慌）',
                'neutral': '中性', None: '無資料'}
    md += f"- **skew 方向**：{skew_map.get(skew_sig['skew_type'])}"
    if skew_sig['call_iv'] and skew_sig['put_iv']:
        md += f"（OTM call IV {skew_sig['call_iv']*100:.0f}% vs put IV {skew_sig['put_iv']*100:.0f}%）"
    md += "\n\n"

    # 觀點
    md += "### 觀點 gate（你手動填）\n\n"
    if viewpoint_sig['has_viewpoint']:
        d = viewpoint_sig['detail']
        md += f"- 催化劑：{d['catalyst']}\n- 論點：{d['thesis']}\n"
        md += f"- 信心：{viewpoint_sig['confidence']}/5"
        md += f"（門檻 {VIEWPOINT_MIN_CONFIDENCE}）：{'✅ 達標' if viewpoint_sig['passes'] else '❌ 未達標'}\n"
        if viewpoint_sig.get('is_placeholder'):
            md += ("- ⚠️ **觀點欄還是「（範例）」文字——真觀點未填**。"
                   "範例不會通過 gate（即使信心改到 4+）。8 月功課：填真觀點或明示放棄 C 池。\n")
        md += "\n"
    else:
        md += f"- _尚未填入觀點（config/spcx_c_viewpoint.json）。沒有觀點 = L2 永遠不會亮。_\n\n"

    # === 三層輸出 ===
    md += f"### 🎯 本回合判斷（gate: {GATE_MODE}）\n\n"
    if level == 'L2':
        md += "## 🟢🟢🟢 L2 — 就是這個\n\n"
        md += "**四條件全中。這是非常稀有的時刻——沉思者出手。**\n\n"
        for cond, ok_ in conditions.items():
            md += f"- {cond}：{'✅' if ok_ else '❌'}\n"
        md += "\n**但記住**：模組是 gate（門），不是 hand（手）。它只說「環境到了、四條件齊了」，\n"
        md += "**不建議買哪個 strike / 到期日**——具體下單仍是你手動決定。\n"
        md += "**回應 SOP**：2 個交易日內在 `config/spcx_c_decisions.json` 記一筆 act 或 skip（PLAYBOOK「C 池 L2 回應 SOP」）。\n"
        md += "可用 strike 參考（價差最窄前幾名；carry＝外在價值年化，跟 SGOV 殖利率比）：\n\n"
        for s in liq_sig['detail']:
            md += f"  - {s['exp']} ${s['strike']:.0f} call（INT {s['oi']}，價差 {s['spread_pct']*100:.1f}%，bid/ask {s['bid']}/{s['ask']}"
            md += f"，carry {s['carry_pct_annual']:.1f}%/年" if s.get('carry_pct_annual') is not None else ""
            md += "）\n"
        md += "\n_單次進場不超過 C 池一半，輸了不補。_\n\n"
    elif level == 'L1':
        md += "## 🟡 L1 — 觀察\n\n"
        md += "**環境在變，但四條件未齊。持續觀察，還不到出手。**\n\n"
        for cond, ok_ in conditions.items():
            md += f"- {cond}：{'✅' if ok_ else '❌'}\n"
        # 點出缺哪一條
        missing = [c for c, ok_ in conditions.items() if not ok_]
        md += f"\n還缺：{'、'.join(missing)}。給方向感，不給行動。\n\n"
    else:
        md += "## ⚪ L0 — 靜默\n\n"
        md += "**機會存在，但現在不是時候。可以等。睡。**\n\n"
        md += f"（當前 {phase_code}。"
        if phase_code == 'P0':
            md += "選擇權市場還沒成形，買什麼都付最貴保費撞最寬價差。）\n\n"
        else:
            missing = [c for c, ok_ in conditions.items() if not ok_]
            md += f"距出手還缺：{'、'.join(missing)}。）\n\n"

    md += "---\n_重劍無鋒，大巧不工。寧可一年不出手，不出錯手。_\n\n"
    return md


def main():
    print(f"🧘 SPCX Option Sage（C 池沉思者）D+1: {datetime.now().strftime('%Y-%m-%d')}")

    spcx_common.ensure_dirs()

    # sage_v0.3：美股新鮮度防呆（同 space_radar v8.8——休市殘留不記歷史）
    fresh, market_date = spcx_common.market_freshness()
    if not fresh:
        print(f"🛑 美股休市時段（最後交易日 {market_date}）——跳過，避免殘留寫進結構歷史")
        return

    d = days_since_ipo()
    if d < 0:
        print(f"⏳ 距上市還有 {abs(d)} 天，選擇權市場未開，靜默")
        md = "\n## 🧘 SPCX Option Sage\n\n_選擇權市場未開，靜默。_\n"
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write(md)
        return

    tk = yf.Ticker(TICKER)
    # 抓現價（spcx_common：dropna + nan 防呆）
    price = spcx_common.get_price(tk)
    if price is None:
        print("⚠️ 無現價，靜默")
        return

    print(f"💎 現價 ${price:.2f}（市值 {spcx_common.price_to_mc_t(price, TOTAL_SHARES_B):.2f}T）")

    # 抓 ATM IV（與 space_radar 同走 spcx_common，同一條鏈同一套算法）
    _, calls, _ = spcx_common.get_atm_chain(tk, price, min_days=14)
    atm_iv = spcx_common.calc_atm_iv(calls, price)

    # 三訊號
    iv_sig = get_iv_signal(atm_iv)
    liq_sig = get_liquidity_signal(tk, price)
    skew_sig = get_skew_signal(tk, price)
    viewpoint_sig = get_viewpoint_signal()
    # patch 1：另外兩條 gate 線（都算都記，只有 GATE_MODE 那條決定 level）
    iv_leaps = get_leaps_iv_signal(liq_sig.get('leaps_atm_iv'), market_date=str(market_date))
    carry = get_carry_signal(liq_sig, price, market_date)

    # 階段 + 出手判斷
    phase_code, phase_label = determine_phase(iv_sig, liq_sig, skew_sig)
    level, conditions = evaluate_action_level(iv_sig, liq_sig, viewpoint_sig, iv_leaps, carry)
    levels = levels_by_mode(iv_sig, liq_sig, viewpoint_sig, iv_leaps, carry)

    print(f"📍 階段：{phase_label}")
    print(f"   IV：{atm_iv*100:.0f}%" if atm_iv else "   IV：無資料", end="")
    if iv_sig['pctile'] is not None:
        print(f"（分位 {iv_sig['pctile']:.0f}）", end="")
    print(f"｜相對冷卻 {iv_sig['rel_calm']}｜絕對可接受 {iv_sig['abs_acceptable']}")
    print(f"   LEAPS IV：{(liq_sig.get('leaps_atm_iv') or 0)*100:.0f}%（分位 {iv_leaps['pctile']}）｜carry 最小 {carry['min_carry_pct']}%/年")
    print(f"   流動性：{'可下單' if liq_sig['liquid'] else '未達標'}"
          f"（INT {liq_sig['total_int']}，可用 strike {liq_sig['usable_strikes']}）")
    print(f"   skew：{skew_sig['skew_type']}")
    print(f"   觀點：{'有且達標' if viewpoint_sig['passes'] else ('有但信心不足' if viewpoint_sig['has_viewpoint'] else '未填')}")
    print(f"🎯 本回合：{level}（gate {GATE_MODE}；三條線 {levels}）")

    # 記錄歷史（判定算完才記：level / transition / 三條線一起進 history）
    hist_df = record_options_history(price, iv_sig, liq_sig, skew_sig, phase_code,
                                     record_date=str(market_date), level=level,
                                     iv_leaps=iv_leaps, carry=carry, levels=levels, gate_mode=GATE_MODE)
    try:
        transition = hist_df.loc[hist_df['date'] == str(market_date), 'transition'].iloc[-1]
        transition = None if pd.isna(transition) else str(transition)
    except Exception:
        transition = None
    if transition:
        print(f"🔔 判定轉換：{transition}")

    # 報告
    md = generate_report(price, iv_sig, liq_sig, skew_sig, phase_code, phase_label,
                         viewpoint_sig, level, conditions, iv_leaps=iv_leaps, carry=carry, levels=levels)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(md)

    liq_out = {k: v for k, v in liq_sig.items() if k != 'usable_all'}   # usable_all 只給 carry 用，不進 JSON
    output = {
        'updated_at': datetime.now().isoformat(),
        'version': 'sage_v0.4',
        'market_date': str(market_date),
        'days_since_ipo': d,
        'price': price,
        'phase': phase_code,
        'level': level,
        'transition': transition,
        'gate_mode': GATE_MODE,
        'gates': {
            'near': {**{k: iv_sig[k] for k in ('pctile', 'rel_calm', 'abs_acceptable', 'stable', 'n_samples')},
                     'value': iv_sig['atm_iv'], 'ok': bool(iv_sig['rel_calm'] and iv_sig['stable'] and iv_sig['abs_acceptable']),
                     'level': levels['near'], 'pctile_calm': IV_PCTILE_CALM, 'abs_gate': IV_ABS_ACCEPTABLE},
            'leaps': {**{k: iv_leaps[k] for k in ('pctile', 'rel_calm', 'abs_acceptable', 'stable', 'n_samples')},
                      'value': liq_sig.get('leaps_atm_iv'), 'exp': liq_sig.get('leaps_iv_exp'),
                      'ok': bool(iv_leaps['rel_calm'] and iv_leaps['stable'] and iv_leaps['abs_acceptable']),
                      'level': levels['leaps'], 'pctile_calm': LEAPS_IV_PCTILE_CALM, 'abs_gate': LEAPS_IV_ABS_ACCEPTABLE},
            'carry': {**carry, 'level': levels['carry']},
        },
        'iv': iv_sig,
        'liquidity': liq_out,
        'skew': skew_sig,
        'viewpoint': viewpoint_sig,
        'conditions': conditions,
    }
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n💾 {OUTPUT_PATH}")
    print(f"💾 {REPORT_PATH}")


if __name__ == "__main__":
    main()
