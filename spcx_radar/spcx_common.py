"""
spcx_common.py — spcx_radar 家族共用介面（2026-07-31 整併）

space_radar.py（A/B 池 + 階段機）與 spcx_options.py（Option Sage，C 池 gate）
原本各自複製了同一批基礎函式：config 載入、上市天數、現價抓取、ATM IV 計算、
市值換算、IV 分位。整併進 spcx_radar/ 時抽到這裡，兩支模組共用一致介面。

原則：
- 這裡只放「兩支都用、行為必須一致」的東西；各模組的閾值與判斷邏輯留在各模組
- 路徑全部以本檔所在目錄為基準（spcx_radar/），從任何 CWD 跑都對
- config/ = 手動維護輸入（spcx_config / dca_log / viewpoint）
- output/ = 程式產出（json、history csv、報告）
"""
import json
import math
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(HERE, "config")
OUTPUT_DIR = os.path.join(HERE, "output")

CONFIG_PATH = os.path.join(CONFIG_DIR, "spcx_config.json")
DCA_LOG_PATH = os.path.join(CONFIG_DIR, "spcx_dca_log.json")
VIEWPOINT_PATH = os.path.join(CONFIG_DIR, "spcx_c_viewpoint.json")

IV_HISTORY_PATH = os.path.join(OUTPUT_DIR, "spcx_iv_history.csv")           # space_radar 唯一寫入者
OPTIONS_HISTORY_PATH = os.path.join(OUTPUT_DIR, "spcx_options_history.csv")  # option sage 唯一寫入者
SPACE_RADAR_JSON = os.path.join(OUTPUT_DIR, "space_radar.json")
SPACE_RADAR_REPORT = os.path.join(OUTPUT_DIR, "space_radar_report.md")
OPTIONS_JSON = os.path.join(OUTPUT_DIR, "spcx_options.json")
OPTIONS_REPORT = os.path.join(OUTPUT_DIR, "spcx_options_report.md")
README_PATH = os.path.join(HERE, "README.md")


def ensure_dirs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_config(defaults, extra_passthrough_keys=()):
    """讀 spcx_config.json，只覆蓋 defaults 裡存在的 key（_ 開頭為註解，跳過）。
    extra_passthrough_keys：不在 defaults 裡但仍要帶出的基礎欄位（如 sage 借用股數）。
    讀不到整個檔也不會掛（防呆，沿用 space_radar 三層防呆設計）。
    """
    cfg = dict(defaults)
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                user_cfg = json.load(f)
            for k, v in user_cfg.items():
                if k.startswith('_'):
                    continue
                if k in defaults or k in extra_passthrough_keys:
                    cfg[k] = v
        else:
            print(f"⚠️ 找不到 {CONFIG_PATH}，使用內建預設值")
    except Exception as e:
        print(f"⚠️ config 讀取失敗（{e}），使用內建預設值")
    return cfg


def days_since_ipo(ipo_date_str):
    """距上市第幾天（上市前回負數）"""
    ipo_dt = datetime.strptime(ipo_date_str, '%Y-%m-%d')
    return (datetime.now() - ipo_dt).days


def get_price(tk):
    """抓現價：5 日收盤取最後一筆有效值。nan / 空值一律回 None（不讓垃圾值流下去）。"""
    try:
        hist = tk.history(period='5d')
        closes = hist['Close'].dropna()
        if closes.empty:
            return None
        price = float(closes.iloc[-1])
        if not price or price <= 0 or math.isnan(price):
            return None
        return price
    except Exception:
        return None


def price_to_mc_t(price, total_shares_b):
    """價格 → 市值（兆）。市值 = 價格 × 股數(B) / 1000"""
    return (price * total_shares_b) / 1000


def get_atm_chain(tk, current_price, min_days=14):
    """回傳第一個「距今 ≥ min_days」到期日的 (exp, calls, puts)。
    兩支模組的 ATM IV / PC ratio / skew 都以這條鏈為基礎，抓不到回 (None, None, None)。
    """
    try:
        exps = tk.options
        if not exps:
            return None, None, None
        today = datetime.now()
        for exp in exps:
            try:
                exp_dt = datetime.strptime(exp, '%Y-%m-%d')
            except Exception:
                continue
            if (exp_dt - today).days < min_days:
                continue
            opt = tk.option_chain(exp)
            return exp, opt.calls.copy(), opt.puts.copy()
        return None, None, None
    except Exception:
        return None, None, None


def calc_atm_iv(calls, current_price):
    """ATM IV：取距現價最近 3 檔 call 的 IV 平均（兩支模組原本各寫一份的同一段邏輯）。
    無效（<=0 / nan）回 None。"""
    try:
        if calls is None or calls.empty:
            return None
        calls = calls.copy()
        calls['dist'] = (calls['strike'] - current_price).abs()
        atm = calls.nsmallest(3, 'dist')
        iv = float(atm['impliedVolatility'].mean())
        if iv <= 0 or math.isnan(iv):
            return None
        return iv
    except Exception:
        return None


def iv_percentile(current_iv, history_csv=IV_HISTORY_PATH, min_samples=10):
    """當前 IV 在自身歷史分布中的百分位。回傳 (pctile, n)；樣本不足回 (None, n)。"""
    import pandas as pd
    if current_iv is None or not os.path.exists(history_csv):
        return None, 0
    try:
        df = pd.read_csv(history_csv)
        ivs = df['atm_iv'].dropna()
        n = len(ivs)
        if n < min_samples:
            return None, n
        return round((ivs < current_iv).sum() / n * 100, 1), n
    except Exception:
        return None, 0
