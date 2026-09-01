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


def days_since_ipo():
    return spcx_common.days_since_ipo(IPO_DATE)


# ============================================================
# 訊號 1：IV 水位（雙軌——相對分位 + 絕對值，兩個都報）
# ============================================================
def get_iv_signal(current_atm_iv):
    """雙軌 IV 判斷。沿用 space_radar 的 IV 歷史（唯讀）。

    回傳 dict：
      - atm_iv（絕對值）
      - pctile（相對分位，資料不足為 None）
      - n_samples
      - rel_calm（相對冷卻：分位 ≤ CALM）
      - abs_acceptable（絕對可接受：IV ≤ 嚴防線）
      - stable（最近 N 天都相對冷卻）
    關鍵：rel_calm 與 abs_acceptable 是兩件事。
      相對分位會說「78% 算冷卻」（比過自己 110% 高點），
      但絕對值 78% 對買 LEAPS 仍貴 → abs_acceptable=False 擋住。
    """
    result = {
        'atm_iv': current_atm_iv,
        'pctile': None,
        'n_samples': 0,
        'rel_calm': False,
        'abs_acceptable': False,
        'stable': False,
    }
    if current_atm_iv is None:
        return result

    # 絕對防線（嚴）：與相對分位完全獨立
    result['abs_acceptable'] = current_atm_iv <= IV_ABS_ACCEPTABLE

    # 相對分位（讀 space_radar 累積的 IV 歷史）
    if not os.path.exists(IV_HISTORY_PATH):
        return result
    try:
        df = pd.read_csv(IV_HISTORY_PATH)
        ivs = df['atm_iv'].dropna()
        n = len(ivs)
        result['n_samples'] = n
        if n >= IV_PCTILE_MIN_SAMPLES:
            pctile = (ivs < current_atm_iv).sum() / n * 100
            result['pctile'] = round(pctile, 1)
            result['rel_calm'] = pctile <= IV_PCTILE_CALM
            # 穩定：最近 N 天的分位都 ≤ CALM
            recent = df.tail(IV_STABLE_DAYS)
            if len(recent) >= IV_STABLE_DAYS:
                all_calm = True
                for iv in recent['atm_iv'].dropna():
                    p = (ivs < iv).sum() / n * 100
                    if p > IV_PCTILE_CALM:
                        all_calm = False
                        break
                result['stable'] = all_calm
    except Exception:
        pass
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
def evaluate_action_level(iv_sig, liq_sig, viewpoint_sig):
    """三層輸出判斷。L2 門檻刻意設極高。

    四條件硬性 AND（缺一不亮 L2）：
      1. IV 相對冷卻且穩定（rel_calm + stable）
      2. IV 絕對可接受（abs_acceptable，嚴防線）
      3. 流動性過關（liquid）
      4. 觀點信心達標（viewpoint passes）

    回傳 (level, reasons)：level ∈ {'L0','L1','L2'}
    """
    c1 = iv_sig['rel_calm'] and iv_sig['stable']
    c2 = iv_sig['abs_acceptable']
    c3 = liq_sig['liquid']
    c4 = viewpoint_sig['passes']

    conditions = {
        'IV 相對冷卻且穩定': c1,
        'IV 絕對可接受（≤防線）': c2,
        '流動性過關': c3,
        '觀點信心達標': c4,
    }
    passed = sum(conditions.values())

    if all(conditions.values()):
        return 'L2', conditions

    # L1：環境在變（流動性建立 OR IV 開始相對冷卻），但四條件未齊
    if c3 or iv_sig['rel_calm']:
        return 'L1', conditions

    # L0：靜默，還早
    return 'L0', conditions


# ============================================================
# 歷史記錄（本模組自己寫，唯一寫入者）
# ============================================================
def record_options_history(price, iv_sig, liq_sig, skew_sig, phase, record_date=None):
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
    }
    if os.path.exists(OPTIONS_HISTORY_PATH):
        df = pd.read_csv(OPTIONS_HISTORY_PATH)
        df = df[df['date'] != record['date']]
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    else:
        df = pd.DataFrame([record])
    df.to_csv(OPTIONS_HISTORY_PATH, index=False)
    return df


# ============================================================
# 報告生成（沉思者的聲音，三層）
# ============================================================
def generate_report(price, iv_sig, liq_sig, skew_sig, phase_code, phase_label,
                    viewpoint_sig, level, conditions):
    md = "\n## 🧘 SPCX Option Sage（C 池沉思者）\n\n"
    md += f"_回合制 D+1｜{datetime.now().strftime('%Y-%m-%d')}（上市第 {days_since_ipo()} 天）_\n\n"

    if price is None:
        md += "_選擇權市場尚未成形或無資料。本回合：靜默。睡。_\n\n"
        return md

    # 階段
    md += f"**選擇權市場結構**：{phase_label}\n\n"

    # 三訊號儀表
    md += "### 三結構訊號\n\n"
    # IV 雙軌
    iv_pct_str = f"{iv_sig['atm_iv']*100:.0f}%" if iv_sig['atm_iv'] else "—"
    pctile_str = f"分位 {iv_sig['pctile']:.0f}" if iv_sig['pctile'] is not None else f"分位無基準(n={iv_sig['n_samples']})"
    md += f"- **IV 水位（雙軌）**：{iv_pct_str}｜{pctile_str}\n"
    md += f"  - 相對冷卻（分位≤{IV_PCTILE_CALM}）：{'✅' if iv_sig['rel_calm'] else '❌'}"
    md += f"　絕對可接受（≤{IV_ABS_ACCEPTABLE*100:.0f}%嚴防線）：{'✅' if iv_sig['abs_acceptable'] else '❌'}"
    md += f"　連續穩定：{'✅' if iv_sig['stable'] else '❌'}\n"
    if iv_sig['rel_calm'] and not iv_sig['abs_acceptable']:
        md += f"  - ⚠️ **相對冷卻但絕對仍貴**：分位說便宜，但 {iv_pct_str} 對買 LEAPS 仍是貴保費。嚴防線擋住，正確。\n"
    # LEAPS 專屬 IV（sage_v0.2：C 池真正要買的東西的保費水位）
    if liq_sig.get('leaps_atm_iv') is not None:
        md += f"- **LEAPS IV（{liq_sig['leaps_iv_exp']}，最長天期）**：{liq_sig['leaps_atm_iv']*100:.0f}%"
        md += "（序列建立中，供未來 LEAPS gate 校準；近月 ATM IV 不能代表 LEAPS 保費）\n"
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
    md += "### 🎯 本回合判斷\n\n"
    if level == 'L2':
        md += "## 🟢🟢🟢 L2 — 就是這個\n\n"
        md += "**四條件全中。這是非常稀有的時刻——沉思者出手。**\n\n"
        for cond, ok in conditions.items():
            md += f"- {cond}：{'✅' if ok else '❌'}\n"
        md += "\n**但記住**：模組是 gate（門），不是 hand（手）。它只說「環境到了、四條件齊了」，\n"
        md += "**不建議買哪個 strike / 到期日**——具體下單仍是你手動決定。\n"
        md += "可用 strike 參考（價差最窄前幾名）：\n\n"
        for s in liq_sig['detail']:
            md += f"  - {s['exp']} ${s['strike']:.0f} call（INT {s['oi']}，價差 {s['spread_pct']*100:.1f}%，bid/ask {s['bid']}/{s['ask']}）\n"
        md += "\n_單次進場不超過 C 池一半，輸了不補。_\n\n"
    elif level == 'L1':
        md += "## 🟡 L1 — 觀察\n\n"
        md += "**環境在變，但四條件未齊。持續觀察，還不到出手。**\n\n"
        for cond, ok in conditions.items():
            md += f"- {cond}：{'✅' if ok else '❌'}\n"
        # 點出缺哪一條
        missing = [c for c, ok in conditions.items() if not ok]
        md += f"\n還缺：{'、'.join(missing)}。給方向感，不給行動。\n\n"
    else:
        md += "## ⚪ L0 — 靜默\n\n"
        md += "**機會存在，但現在不是時候。可以等。睡。**\n\n"
        md += f"（當前 {phase_code}。"
        if phase_code == 'P0':
            md += "選擇權市場還沒成形，買什麼都付最貴保費撞最寬價差。）\n\n"
        else:
            missing = [c for c, ok in conditions.items() if not ok]
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

    # 階段 + 出手判斷
    phase_code, phase_label = determine_phase(iv_sig, liq_sig, skew_sig)
    level, conditions = evaluate_action_level(iv_sig, liq_sig, viewpoint_sig)

    print(f"📍 階段：{phase_label}")
    print(f"   IV：{atm_iv*100:.0f}%" if atm_iv else "   IV：無資料", end="")
    if iv_sig['pctile'] is not None:
        print(f"（分位 {iv_sig['pctile']:.0f}）", end="")
    print(f"｜相對冷卻 {iv_sig['rel_calm']}｜絕對可接受 {iv_sig['abs_acceptable']}")
    print(f"   流動性：{'可下單' if liq_sig['liquid'] else '未達標'}"
          f"（INT {liq_sig['total_int']}，可用 strike {liq_sig['usable_strikes']}）")
    print(f"   skew：{skew_sig['skew_type']}")
    print(f"   觀點：{'有且達標' if viewpoint_sig['passes'] else ('有但信心不足' if viewpoint_sig['has_viewpoint'] else '未填')}")
    print(f"🎯 本回合：{level}")

    # 記錄歷史
    record_options_history(price, iv_sig, liq_sig, skew_sig, phase_code, record_date=str(market_date))

    # 報告
    md = generate_report(price, iv_sig, liq_sig, skew_sig, phase_code, phase_label,
                         viewpoint_sig, level, conditions)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(md)

    output = {
        'updated_at': datetime.now().isoformat(),
        'version': 'sage_v0.3',
        'days_since_ipo': d,
        'price': price,
        'phase': phase_code,
        'level': level,
        'iv': iv_sig,
        'liquidity': liq_sig,
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
