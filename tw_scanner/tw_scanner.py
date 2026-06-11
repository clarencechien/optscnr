#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tw_scanner.py v2 — 台股籌碼天氣台 (DCA weather station)
=========================================================
Spec (agreed 2026-06-11): NOT a D+1 direction caller. Chip data is
end-of-day disclosure with multi-week autocorrelation — daily timing
has no viable alpha path. What it CAN do:

  Tier 1  thermometer  — every feature reported as Δ + rolling percentile
                         vs its own history. No absolute thresholds, no drama.
  Tier 2  regime       — 5-state machine with hysteresis (flips on weekly
                         timescale): RISK_ON / NEUTRAL / DE_RISK /
                         CAPITULATION / OVERHEAT. Narrative is generated
                         from state TRANSITIONS only.
  Tier 3  tail alerts  — rare co-occurrence days (capitulation / overheat).
                         The only output with actionable meaning for a
                         DCA schedule (accelerate / decelerate windows).

  --backtest           — forward 20d/60d TAIEX return distribution after
                         each historical alert vs unconditional baseline.
                         If an alert doesn't separate from baseline, delete
                         it. Instruments carry no ornaments.

Features (all FinMind, multi-year backfill => percentiles calibrated day 1):
  f_spot_20d   foreign net buy, 20-day rolling sum (spot)
  tx_delta     foreign TX net OI, 1-day change   (hedge-book aware: we
               read the DELTA, never the level — level stayed 'extreme'
               through five weeks of record highs in May 2026)
  retail_mtx   -(institutional MTX net OI), level percentile + delta
  margin_chg   total margin balance daily change (unit-invariant via pct)

House rules: config-externalized, никогда crash (degrade to NO_DATA),
append-only state, --selftest fixtures, --dump-schema for live field audit.

Usage:
  python tw_scanner.py                     # daily briefing (uses cache)
  python tw_scanner.py --backfill          # force full history refetch
  python tw_scanner.py --backtest          # validate alerts vs baseline
  python tw_scanner.py --dump-schema       # print live FinMind columns
  python tw_scanner.py --selftest          # synthetic data, zero network
Env: FINMIND_TOKEN (optional, raises rate limits)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from typing import Optional

import pandas as pd
import numpy as np

GREEN, YELLOW, RED, NO_DATA = "GREEN", "YELLOW", "RED", "NO_DATA"
STATES = ["CAPITULATION", "DE_RISK", "NEUTRAL", "RISK_ON", "OVERHEAT"]
STATE_EMOJI = {"CAPITULATION": "🥶", "DE_RISK": "🌧️", "NEUTRAL": "⛅",
               "RISK_ON": "☀️", "OVERHEAT": "🔥", "UNCALIBRATED": "❔"}
UA = "tw-scanner/2.0 (+github.com/clarencechien/optscnr)"


# ----------------------------------------------------------------------------
# FinMind fetch + schema resolver
# ----------------------------------------------------------------------------

def finmind(dataset: str, cfg: dict, data_id: str = "",
            start: str = "2018-01-01") -> pd.DataFrame:
    params = {"dataset": dataset, "start_date": start}
    if data_id:
        params["data_id"] = data_id
    tok = os.environ.get("FINMIND_TOKEN", "")
    if tok:
        params["token"] = tok
    url = cfg["endpoints"]["finmind"] + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.loads(r.read().decode("utf-8"))
    df = pd.DataFrame(payload.get("data", []))
    if df.empty:
        raise RuntimeError(f"FinMind {dataset}({data_id}): empty "
                           f"(msg={payload.get('msg')!r})")
    return df


def col(df: pd.DataFrame, candidates: list[str], what: str) -> str:
    """Resolve a column from a priority-ordered candidate list."""
    for c in candidates:
        if c in df.columns:
            return c
    raise RuntimeError(f"none of {candidates} found for {what}; "
                       f"live columns = {list(df.columns)} — run --dump-schema "
                       f"and update config field candidates")


def rows_matching(df: pd.DataFrame, name_col: str, pattern: str) -> pd.DataFrame:
    return df[df[name_col].astype(str).str.contains(pattern, na=False, regex=True)]


# ----------------------------------------------------------------------------
# Raw series builders (one per feature; each isolated & cache-aware)
# ----------------------------------------------------------------------------

def fetch_spot_foreign(cfg: dict, start: str) -> pd.Series:
    """Daily foreign net buy on TWSE, in raw currency units."""
    fc = cfg["fields"]["spot_total_institution"]
    df = finmind(fc["dataset"], cfg, start=start)
    c_date = col(df, fc["date"], "spot date")
    c_name = col(df, fc["name"], "spot name")
    c_buy = col(df, fc["buy"], "spot buy")
    c_sell = col(df, fc["sell"], "spot sell")
    f = rows_matching(df, c_name, fc["foreign_pattern"]).copy()
    f["net"] = pd.to_numeric(f[c_buy], errors="coerce") - \
        pd.to_numeric(f[c_sell], errors="coerce")
    s = f.groupby(c_date)["net"].sum()
    s.index = pd.to_datetime(s.index)
    return s.sort_index().rename("f_spot")


def fetch_futures_net_oi(cfg: dict, start: str, product_key: str,
                         who_pattern: Optional[str]) -> pd.Series:
    """Net OI series for a futures product.
    who_pattern=None => sum ALL institutional rows (for retail inversion)."""
    fc = cfg["fields"]["futures_institution"]
    df = finmind(fc["dataset"], cfg, data_id=cfg["products"][product_key], start=start)
    c_date = col(df, fc["date"], "fut date")
    c_who = col(df, fc["who"], "fut investor")
    c_long = col(df, fc["long_oi"], "fut long OI")
    c_short = col(df, fc["short_oi"], "fut short OI")
    if who_pattern:
        df = rows_matching(df, c_who, who_pattern)
    else:
        # sum of the three institutional categories ONLY — guard against
        # FinMind ever adding a 'total' row (spot dataset already has one)
        df = rows_matching(df, c_who, fc.get("all_inst_pattern", "自營商|投信|外資"))
    df = df.copy()
    df["net_oi"] = pd.to_numeric(df[c_long], errors="coerce") - \
        pd.to_numeric(df[c_short], errors="coerce")
    s = df.groupby(c_date)["net_oi"].sum()
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def fetch_margin_change(cfg: dict, start: str) -> pd.Series:
    """Daily total margin balance CHANGE. Unit-agnostic by design — all
    downstream logic is percentile-based, so 元 vs 仟元 doesn't matter."""
    fc = cfg["fields"]["margin_total"]
    df = finmind(fc["dataset"], cfg, start=start)
    c_date = col(df, fc["date"], "margin date")
    c_today = col(df, fc["today"], "margin today balance")
    if fc.get("name") and any(c in df.columns for c in fc["name"]):
        c_name = col(df, fc["name"], "margin name")
        df = rows_matching(df, c_name, fc["margin_pattern"])
    df = df.copy()
    df["bal"] = pd.to_numeric(df[c_today], errors="coerce")
    s = df.groupby(c_date)["bal"].sum()
    s.index = pd.to_datetime(s.index)
    return s.sort_index().diff().rename("margin_chg")


def fetch_index_close(cfg: dict, start: str) -> pd.Series:
    """TAIEX close, for backtest forward returns. Tries candidates in order."""
    last_err = None
    for spec in cfg["fields"]["index_candidates"]:
        try:
            df = finmind(spec["dataset"], cfg, data_id=spec["data_id"], start=start)
            c_date = col(df, spec["date"], "index date")
            c_close = col(df, spec["close"], "index close")
            s = df.set_index(c_date)[c_close].astype(float)
            s.index = pd.to_datetime(s.index)
            return s.sort_index().rename("taiex")
        except Exception as e:
            last_err = e
    raise RuntimeError(f"all index candidates failed; last: {last_err}")


# ----------------------------------------------------------------------------
# Feature frame, percentiles, regime, alerts
# ----------------------------------------------------------------------------

def build_features(spot: pd.Series, tx_foreign: pd.Series,
                   mtx_inst: pd.Series, margin_chg: pd.Series,
                   cfg: dict) -> pd.DataFrame:
    p = cfg["thermometer"]
    f = pd.DataFrame(index=sorted(set(spot.index) | set(tx_foreign.index)))
    f["f_spot_20d"] = spot.reindex(f.index).rolling(p["spot_window_days"],
                                                    min_periods=5).sum()
    f["tx_level"] = tx_foreign.reindex(f.index)
    f["tx_delta"] = f["tx_level"].diff()
    f["retail_mtx"] = (-mtx_inst).reindex(f.index)
    f["retail_mtx_delta"] = f["retail_mtx"].diff()
    f["margin_chg"] = margin_chg.reindex(f.index)
    return f.dropna(how="all")


def add_percentiles(f: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    p = cfg["thermometer"]
    w, mp = p["percentile_window_days"], p["min_history_days"]

    def roll_pct(s: pd.Series) -> pd.Series:
        return s.rolling(w, min_periods=mp).rank(pct=True) * 100

    for c in ("f_spot_20d", "tx_delta", "retail_mtx", "margin_chg"):
        f[c + "_pct"] = roll_pct(f[c])
    return f


def regime_series(f: pd.DataFrame, cfg: dict) -> pd.Series:
    """Score-based 5-state machine with hysteresis.
    score = mean of risk-appetite-signed percentiles, rescaled to [-1, 1].
    A flip requires `confirm_days` consecutive closes in the new band."""
    r = cfg["regime"]
    # risk-appetite sign convention: + = risk-on behaviour
    comp = pd.DataFrame({
        "spot": f["f_spot_20d_pct"],          # foreign buying = risk-on
        "txd": f["tx_delta_pct"],             # covering shorts = risk-on
        "margin": f["margin_chg_pct"],        # leverage build = risk-on (→ overheat at tail)
        "retail": 100 - f["retail_mtx_pct"],  # retail crowding long = CONTRARIAN risk-off
    })
    score = (comp.mean(axis=1) - 50) / 50  # [-1, 1]

    bands = r["bands"]  # ordered thresholds
    def band_of(x: float) -> str:
        if np.isnan(x):
            return "UNCALIBRATED"
        if x <= bands["capitulation_max"]:
            return "CAPITULATION"
        if x <= bands["de_risk_max"]:
            return "DE_RISK"
        if x < bands["risk_on_min"]:
            return "NEUTRAL"
        if x < bands["overheat_min"]:
            return "RISK_ON"
        return "OVERHEAT"

    raw = score.apply(band_of)
    out, cur, pending, streak = [], "UNCALIBRATED", None, 0
    for b in raw:
        if b == cur or b == "UNCALIBRATED" and cur != "UNCALIBRATED":
            pending, streak = None, 0
        elif b == pending:
            streak += 1
            if streak >= r["confirm_days"]:
                cur, pending, streak = b, None, 0
        else:
            pending, streak = b, 1
            if cur == "UNCALIBRATED":   # first calibrated reading seeds state
                cur, pending, streak = b, None, 0
        out.append(cur)
    s = pd.Series(out, index=f.index, name="regime")
    s.loc[score.isna()] = "UNCALIBRATED"
    return s, score.rename("score")


def alert_series(f: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    a = cfg["alerts"]
    capit = ((f["f_spot_20d_pct"] <= a["capitulation"]["spot_pct_max"]) &
             (f["margin_chg_pct"] <= a["capitulation"]["margin_pct_max"]) &
             (f["retail_mtx_delta"] < 0))
    over = ((f["margin_chg_pct"] >= a["overheat"]["margin_pct_min"]) &
            (f["retail_mtx_pct"] >= a["overheat"]["retail_pct_min"]) &
            (f["f_spot_20d_pct"] >= a["overheat"]["spot_pct_min"]))
    return pd.DataFrame({"capitulation": capit.fillna(False),
                         "overheat": over.fillna(False)}, index=f.index)


# ----------------------------------------------------------------------------
# Backtest: do the alerts actually separate from baseline?
# ----------------------------------------------------------------------------

def backtest(f: pd.DataFrame, alerts: pd.DataFrame, taiex: pd.Series,
             cfg: dict) -> str:
    horizons = cfg["backtest"]["horizons_days"]
    px = taiex.reindex(f.index).ffill()
    lines = ["# tw_scanner 警報回測 — 警報後遠期報酬 vs 無條件基線", ""]
    fwd = {h: px.shift(-h) / px - 1 for h in horizons}
    for name in alerts.columns:
        days = alerts.index[alerts[name]]
        # de-cluster: keep first day of each episode (gap > 5 sessions)
        episodes = []
        for d in days:
            if not episodes or (f.index.get_loc(d) -
                                f.index.get_loc(episodes[-1])) > 5:
                episodes.append(d)
        lines.append(f"## {name} — 觸發 {len(days)} 日 / {len(episodes)} 個事件簇")
        if not episodes:
            lines.append("（歷史上未觸發——閾值可能過嚴，或樣本期太短）\n")
            continue
        lines.append("| 水平 | 事件後中位數 | 事件後均值 | 基線中位數 | 命中率(同號) | n |")
        lines.append("|---|---|---|---|---|---|")
        expect_sign = +1 if name == "capitulation" else -1
        for h in horizons:
            ev = fwd[h].reindex(episodes).dropna()
            base = fwd[h].dropna()
            if ev.empty:
                continue
            hit = (np.sign(ev) == expect_sign).mean()
            lines.append(
                f"| {h}日 | {ev.median():+.2%} | {ev.mean():+.2%} | "
                f"{base.median():+.2%} | {hit:.0%} | {len(ev)} |")
        lines.append("")
        lines.append(f"事件日列表: {', '.join(d.strftime('%Y-%m-%d') for d in episodes[-12:])}"
                     + ("（僅列最近12個）" if len(episodes) > 12 else ""))
        lines.append("")
    lines.append("> 判讀準則：事件後分佈與基線無法分離 ⇒ 刪除該警報。儀器不留裝飾品。")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Briefing renderer (the entire daily output: 溫度 / 鋒面 / 警報)
# ----------------------------------------------------------------------------

def render_briefing(f: pd.DataFrame, regime: pd.Series, score: pd.Series,
                    alerts: pd.DataFrame, cfg: dict) -> str:
    d = f.index[-1]
    row, pr = f.iloc[-1], regime.iloc[-1]
    prev_regime = regime.iloc[-2] if len(regime) > 1 else pr
    transition = "" if pr == prev_regime else f"（昨日由 {prev_regime} 轉入）"
    today_alerts = [c for c in alerts.columns if alerts.iloc[-1][c]]

    def t(v, pct, fmt="{:+,.0f}"):
        if pd.isna(v):
            return "⏳ 今日尚未公布（融資等資料約 21:00 揭露，屆時重跑補齊）"
        if pd.isna(pct):
            return f"`{fmt.format(v)}`（歷史不足，分位數未校準）"
        return f"`{fmt.format(v)}`，落在近一年第 **{pct:.0f}** 百分位"

    n_feat = int(4 - sum(pd.isna(row[c]) for c in
                         ("f_spot_20d", "tx_delta", "retail_mtx", "margin_chg")))
    feat_note = "" if n_feat == 4 else f"，以 {n_feat}/4 特徵計算"

    lines = [
        f"# 🌤️ 台股 DCA 天氣簡報 — {d.strftime('%Y-%m-%d')}",
        "",
        f"## 鋒面：{STATE_EMOJI.get(pr, '❔')} **{pr}** {transition}"
        f"　(score {score.iloc[-1]:+.2f}{feat_note})",
        "",
        "## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）",
        f"- 外資現貨 20 日累積：{t(row['f_spot_20d'], row['f_spot_20d_pct'])}",
        f"- 外資大台淨倉 Δ：{t(row['tx_delta'], row['tx_delta_pct'])}"
        f"（水位 {row['tx_level']:+,.0f} 口僅供參考，不參與判讀）",
        f"- 散戶小台淨倉：{t(row['retail_mtx'], row['retail_mtx_pct'])}",
        f"- 融資餘額變化：{t(row['margin_chg'], row['margin_chg_pct'])}",
        "",
    ]
    if today_alerts:
        for a in today_alerts:
            tag = ("🥶 投降警報 — 歷史上此類尾部共現日為 DCA 加速窗口（見回測）"
                   if a == "capitulation" else
                   "🔥 過熱警報 — 槓桿與散戶擁擠同步在尾部，DCA 減速參考")
            lines.append(f"## 🚨 {tag}")
    else:
        lines.append("## 警報：無（尾部共現條件未成立）")
    lines += [
        "",
        "---",
        "*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；"
        "敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*",
    ]
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Cache, state, selftest
# ----------------------------------------------------------------------------

def load_or_fetch(cfg: dict, backfill: bool, fetchers: dict) -> dict:
    cache_dir = cfg["cache_dir"]
    os.makedirs(cache_dir, exist_ok=True)
    out = {}
    for key, fn in fetchers.items():
        path = os.path.join(cache_dir, f"{key}.csv")
        if not backfill and os.path.exists(path):
            s = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]
            tail = (s.index[-1] - pd.Timedelta(days=5)).strftime("%Y-%m-%d")
            try:
                fresh = fn(tail)
                s = pd.concat([s[s.index < fresh.index.min()], fresh])
            except Exception as e:
                print(f"[warn] incremental fetch {key} failed ({e}); "
                      f"using cache only", file=sys.stderr)
        else:
            s = fn(cfg["history_start"])
        s.to_csv(path)
        out[key] = s
    return out


def append_state(path: str, entry: dict) -> None:
    hist = []
    if os.path.exists(path):
        try:
            hist = json.load(open(path, encoding="utf-8"))
        except Exception:
            hist = []
    hist.append(entry)
    json.dump(hist, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def synthetic_series(seed: int = 7) -> dict:
    """3y of plausible joint dynamics + an injected capitulation episode
    and an injected overheat episode, to verify alerts & regime flips."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-06-01", "2026-06-11")
    n = len(idx)
    risk = np.zeros(n)                                  # OU latent risk appetite
    for i in range(1, n):
        risk[i] = 0.97 * risk[i - 1] + rng.normal(0, 0.35)
    spot = pd.Series(rng.normal(0, 60e8, n) + risk * 25e8, idx)
    tx = pd.Series(np.cumsum(rng.normal(0, 1500, n) + risk * 120) - 30000, idx)
    mtx_inst = pd.Series(np.cumsum(rng.normal(0, 400, n)) - 3000, idx)
    margin_bal = pd.Series(3000e8 + np.cumsum(rng.normal(0, 15e8, n) + risk * 8e8), idx)
    px = pd.Series(18000 * np.exp(np.cumsum(rng.normal(0.0004, 0.011, n)
                                            + risk * 0.0012)), idx)
    # inject capitulation: 10 sessions of brutal selling + margin purge + retail flip
    a, b = n - 260, n - 250
    spot.iloc[a:b] -= 400e8
    margin_bal.iloc[a:b] -= np.cumsum(np.full(b - a, 120e8))
    mtx_inst.iloc[a:b] += 9000          # institutions long => retail net short
    px.iloc[a:] *= np.exp(np.linspace(0, 0.18, n - a))   # rebound after purge
    # inject overheat: euphoric leverage build
    c, e = n - 60, n - 50
    spot.iloc[c:e] += 350e8
    margin_bal.iloc[c:e] += np.cumsum(np.full(e - c, 100e8))
    mtx_inst.iloc[c:e] -= 12000         # institutions short => retail crowded long
    return {"spot": spot, "tx_foreign": tx, "mtx_inst": mtx_inst,
            "margin_chg": margin_bal.diff(), "taiex": px}


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="台股籌碼天氣台 v2")
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--config", default=os.path.join(here, "config",
                                                     "tw_scanner_config.json"))
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--backtest", action="store_true")
    ap.add_argument("--dump-schema", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    out_dir = args.output_dir or cfg.get("output_dir", "output")
    os.makedirs(out_dir, exist_ok=True)

    if args.dump_schema:
        for key, spec in [("spot", cfg["fields"]["spot_total_institution"]),
                          ("futures", cfg["fields"]["futures_institution"]),
                          ("margin", cfg["fields"]["margin_total"])]:
            try:
                did = cfg["products"]["tx"] if key == "futures" else ""
                df = finmind(spec["dataset"], cfg, data_id=did,
                             start=(dt.date.today() - dt.timedelta(days=14)).isoformat())
                print(f"\n===== {spec['dataset']} =====")
                print("columns:", list(df.columns))
                print(df.tail(4).to_string())
            except Exception as e:
                print(f"\n===== {key}: fetch failed: {e}")
        for spec in cfg["fields"]["index_candidates"]:
            try:
                df = finmind(spec["dataset"], cfg, data_id=spec["data_id"],
                             start=(dt.date.today() - dt.timedelta(days=14)).isoformat())
                print(f"\n===== {spec['dataset']}({spec['data_id']}) =====")
                print("columns:", list(df.columns))
                break
            except Exception as e:
                print(f"\n===== index candidate failed: {e}")
        return 0

    if args.selftest:
        raw = synthetic_series()
    else:
        fetchers = {
            "spot": lambda s: fetch_spot_foreign(cfg, s),
            "tx_foreign": lambda s: fetch_futures_net_oi(
                cfg, s, "tx", cfg["fields"]["futures_institution"]["foreign_pattern"]),
            "mtx_inst": lambda s: fetch_futures_net_oi(cfg, s, "mtx", None),
            "margin_chg": lambda s: fetch_margin_change(cfg, s),
            "taiex": lambda s: fetch_index_close(cfg, s),
        }
        raw = load_or_fetch(cfg, args.backfill, fetchers)

    f = build_features(raw["spot"], raw["tx_foreign"], raw["mtx_inst"],
                       raw["margin_chg"], cfg)
    f = add_percentiles(f, cfg)
    regime, score = regime_series(f, cfg)
    alerts = alert_series(f, cfg)

    if args.backtest:
        report = backtest(f, alerts, raw["taiex"], cfg)
        path = os.path.join(out_dir, "tw_scanner_backtest.md")
    else:
        report = render_briefing(f, regime, score, alerts, cfg)
        path = os.path.join(out_dir, "tw_scanner_briefing.md")
        append_state(os.path.join(out_dir, "tw_scanner_state.json"), {
            "date": str(f.index[-1].date()),
            "regime": regime.iloc[-1],
            "score": None if pd.isna(score.iloc[-1]) else round(float(score.iloc[-1]), 3),
            "alerts": [c for c in alerts.columns if alerts.iloc[-1][c]],
            "pcts": {c: (None if pd.isna(f.iloc[-1][c + "_pct"])
                         else round(float(f.iloc[-1][c + "_pct"]), 1))
                     for c in ("f_spot_20d", "tx_delta", "retail_mtx", "margin_chg")},
        })

    open(path, "w", encoding="utf-8").write(report)
    print(report)
    print(f"\n[written] {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
