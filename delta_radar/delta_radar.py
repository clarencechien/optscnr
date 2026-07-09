#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
delta_radar.py — 2308.TW (Delta Electronics) mosaic verification radar
======================================================================
Part of the optscnr radar family (space_radar / unknown_radar siblings).

Five signal modules, each emitting GREEN / YELLOW / RED / NO_DATA:

  M1  revenue_acceleration   TWSE monthly revenue, YoY + 2nd-order slope     (FinMind)
  M2  bullwhip_health        Contract liabilities, inventory, FCF/NI ratio   (FinMind)
  M3  thai_shadow            DELTA.BK quarterly rev/margin as leading proxy  (yfinance)
  M4  customs_flow           US imports HS 8504.40 from TH+TW, rolling YoY   (US Census API)
  M5  narrative_triggers     RSS keyword buckets: capex cuts / VR300 delay / (Google News RSS)
                             debt-financed-capex "shoeshine boy" signals

Design rules (house style):
  * ALL thresholds / endpoints / keywords externalized to config JSON.
  * No module failure ever crashes the run — degrade to NO_DATA and report it.
  * Output: markdown report + append-only JSON state (history for backtests).
  * --selftest runs the full pipeline on bundled fixtures with zero network.

Env vars (all optional):
  FINMIND_TOKEN   raises FinMind rate limits (anonymous works, slowly)
  CENSUS_API_KEY  raises Census limits (keyless ~500 calls/day is plenty)

Usage:
  python delta_radar.py --config config/delta_radar_config.json
  python delta_radar.py --selftest
  python delta_radar.py --modules m1,m4
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile
import time
import traceback
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Optional

# ----------------------------------------------------------------------------
# Constants & tiny utilities
# ----------------------------------------------------------------------------

GREEN, YELLOW, RED, NO_DATA = "GREEN", "YELLOW", "RED", "NO_DATA"
SEVERITY = {GREEN: 0, NO_DATA: 1, YELLOW: 2, RED: 3}
EMOJI = {GREEN: "🟢", YELLOW: "🟡", RED: "🔴", NO_DATA: "⚪"}

# Canonical module order + the "full run" definition (BUG-1 partial detection).
# A run covering exactly this set produces a real overall verdict; anything
# narrower is recorded as PARTIAL(...). Extend here when adding modules.
# (m7 is the outcome-backfill background task, not a status-emitting module.)
MODULE_ORDER = ("m1", "m2", "m3", "m4", "m5", "m6", "m8")

UA = "delta-radar/1.0 (+github.com/clarencechien/optscnr)"


def http_get_json(url: str, timeout: int = 30) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def http_get_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def pct_change(cur: float, prev: float) -> Optional[float]:
    """Signed percent change of cur vs prev; None if undefined.

    Semantic-neutral core. Use `yoy` alias for year-over-year comparisons,
    call `pct_change` directly for QoQ / sequential deltas (BUG-5: M2's QoQ
    previously borrowed `yoy()`, which read as YoY at the call site)."""
    if prev in (None, 0) or cur is None:
        return None
    return (cur - prev) / abs(prev) * 100.0


# YoY is just a percent change over a 12-month-apart pair — same math, clearer name.
yoy = pct_change


def fmt_pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x:+.1f}%"


@dataclass
class ModuleResult:
    module: str
    status: str = NO_DATA
    headline: str = ""
    metrics: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)
    error: Optional[str] = None


# ----------------------------------------------------------------------------
# Data fetchers (each isolated so --selftest can inject fixtures)
# ----------------------------------------------------------------------------

def finmind_fetch(dataset: str, data_id: str, start_date: str, cfg: dict) -> list[dict]:
    base = cfg["endpoints"]["finmind"]
    params = {"dataset": dataset, "data_id": data_id, "start_date": start_date}
    token = os.environ.get("FINMIND_TOKEN", "")
    if token:
        params["token"] = token
    url = base + "?" + urllib.parse.urlencode(params)
    payload = http_get_json(url)
    if payload.get("status") not in (200, "200") and payload.get("msg") not in ("success",):
        # FinMind returns {"msg": "success", "status": 200, "data": [...]}
        if not payload.get("data"):
            raise RuntimeError(f"FinMind {dataset}: {payload.get('msg')}")
    return payload.get("data", [])


def census_fetch(cfg: dict, months_back: int) -> list[dict]:
    """US Census timeseries imports by HS6, monthly GEN_VAL_MO per country."""
    c = cfg["m4_customs_flow"]
    today = dt.date.today()
    start = (today.replace(day=1) - dt.timedelta(days=31 * months_back)).strftime("%Y-%m")
    params: list[tuple] = [
        ("get", "GEN_VAL_MO,CTY_CODE,CTY_NAME"),
        ("I_COMMODITY", c["hs_code"]),
        ("COMM_LVL", "HS6"),
        ("time", f"from {start}"),
    ]
    # server-side country filter (repeated param) — shrinks payload massively
    for code in c["country_codes"].values():
        params.append(("CTY_CODE", str(code)))
    key = os.environ.get("CENSUS_API_KEY", "")
    if key:
        params.append(("key", key))
    url = cfg["endpoints"]["census"] + "?" + urllib.parse.urlencode(params)
    raw = http_get_text(url)
    try:
        rows = json.loads(raw)  # first row is header
    except json.JSONDecodeError:
        raise RuntimeError(f"Census non-JSON response: {raw[:300]!r}")
    header, body = rows[0], rows[1:]
    idx = {h: i for i, h in enumerate(header)}
    wanted = set(str(x) for x in c["country_codes"].values())
    out = []
    for r in body:
        if str(r[idx["CTY_CODE"]]) in wanted:
            out.append({
                "time": r[idx["time"]],
                "country": r[idx["CTY_NAME"]],
                "value": float(r[idx["GEN_VAL_MO"]]),
            })
    return out


def yfinance_quarterlies(ticker: str) -> dict:
    """Returns {'revenue': {period: value}, 'gross_profit': {...}, 'net_income': {...}}"""
    import yfinance as yf  # optional dep; ImportError handled by caller
    t = yf.Ticker(ticker)
    df = t.quarterly_income_stmt  # rows = line items, cols = period timestamps
    out: dict[str, dict] = {"revenue": {}, "gross_profit": {}, "net_income": {}}
    name_map = {
        "Total Revenue": "revenue",
        "Gross Profit": "gross_profit",
        "Net Income": "net_income",
    }
    for row_name, key in name_map.items():
        if row_name in df.index:
            for col, val in df.loc[row_name].items():
                if val == val:  # not NaN
                    out[key][str(col.date())] = float(val)
    return out


def rss_fetch(url: str) -> list[dict]:
    """Minimal stdlib RSS reader: returns [{'title','summary','date'}]."""
    xml_text = http_get_text(url)
    root = ET.fromstring(xml_text)
    items = []
    for it in root.iter("item"):
        items.append({
            "title": (it.findtext("title") or "").strip(),
            "summary": re.sub(r"<[^>]+>", " ", it.findtext("description") or "")[:400],
            "date": (it.findtext("pubDate") or "").strip(),
        })
    return items


# ----------------------------------------------------------------------------
# M1 — monthly revenue acceleration
# ----------------------------------------------------------------------------

def run_m1(cfg: dict, fetch: Callable) -> ModuleResult:
    res = ModuleResult("M1 revenue_acceleration")
    p = cfg["m1_revenue_acceleration"]
    start = (dt.date.today() - dt.timedelta(days=900)).isoformat()
    rows = fetch("TaiwanStockMonthRevenue", cfg["ticker_tw"], start, cfg)
    if not rows:
        res.error = "empty FinMind response"
        return res
    # rows: [{'date','stock_id','revenue','revenue_month','revenue_year'}, ...]
    series = {}
    for r in rows:
        key = (int(r["revenue_year"]), int(r["revenue_month"]))
        series[key] = float(r["revenue"])
    keys = sorted(series)
    yoys = []
    for (y, m) in keys:
        prev = series.get((y - 1, m))
        v = yoy(series[(y, m)], prev)
        if v is not None:
            yoys.append(((y, m), v))
    if len(yoys) < p["slope_window"] + 1:
        res.error = "insufficient history for slope"
        return res
    latest_key, latest_yoy = yoys[-1]
    window = [v for _, v in yoys[-(p["slope_window"] + 1):]]
    slope = (window[-1] - window[0]) / p["slope_window"]  # pp per month
    consec_decel = 0
    for i in range(len(yoys) - 1, 0, -1):
        if yoys[i][1] < yoys[i - 1][1]:
            consec_decel += 1
        else:
            break
    res.metrics = {
        "latest_month": f"{latest_key[0]}-{latest_key[1]:02d}",
        "latest_yoy_pct": round(latest_yoy, 1),
        "yoy_slope_pp_per_month": round(slope, 2),
        "consecutive_decel_months": consec_decel,
    }
    if latest_yoy < p["red_yoy_floor_pct"] or (
        slope < p["red_slope_floor_pp"] and consec_decel >= p["red_consec_decel"]
    ):
        res.status = RED
    elif latest_yoy < p["yellow_yoy_floor_pct"] or consec_decel >= p["yellow_consec_decel"]:
        res.status = YELLOW
    else:
        res.status = GREEN
    res.headline = (
        f"{res.metrics['latest_month']} YoY {fmt_pct(latest_yoy)}, "
        f"slope {slope:+.2f}pp/月, 連續減速 {consec_decel} 個月"
    )
    return res


# ----------------------------------------------------------------------------
# M2 — bullwhip health (contract liabilities / inventory / FCF quality)
# ----------------------------------------------------------------------------

def _pick_account(rows: list[dict], patterns: list[str]) -> tuple[dict[str, float], str]:
    """FinMind statements come as long-format rows {'date','type','value'}.

    Rules learned from live schema (2026-06-11 dump):
      * '<Name>_per' rows are percent-of-total — always excluded.
      * Never sum across DIFFERENT account types; pick exactly one type,
        by pattern priority order (first regex that matches anything wins).
    Returns ({date: value}, chosen_type)."""
    rows = [r for r in rows if not str(r.get("type", "")).endswith("_per")]
    for pat in patterns:
        rx = re.compile(pat, re.I)
        candidates = sorted({str(r["type"]) for r in rows if rx.search(str(r["type"]))})
        if not candidates:
            continue
        chosen = candidates[0]
        out: dict[str, float] = {}
        for r in rows:
            if str(r["type"]) == chosen:
                out[r["date"]] = float(r["value"])
        return out, chosen
    return {}, ""


def run_m2(cfg: dict, fetch: Callable) -> ModuleResult:
    res = ModuleResult("M2 bullwhip_health")
    p = cfg["m2_bullwhip_health"]
    start = (dt.date.today() - dt.timedelta(days=900)).isoformat()
    bs = fetch("TaiwanStockBalanceSheet", cfg["ticker_tw"], start, cfg)
    cf = fetch("TaiwanStockCashFlowsStatement", cfg["ticker_tw"], start, cfg)
    inc = fetch("TaiwanStockFinancialStatements", cfg["ticker_tw"], start, cfg)
    if not bs or not cf:
        res.error = "empty FinMind statements"
        return res

    contract, t_c = _pick_account(bs, p["account_patterns"]["contract_liabilities"])
    inventory, t_i = _pick_account(bs, p["account_patterns"]["inventory"])
    ocf, t_o = _pick_account(cf, p["account_patterns"]["operating_cash_flow"])
    capex, t_x = _pick_account(cf, p["account_patterns"]["capex"])
    ni, t_n = _pick_account(inc, p["account_patterns"]["net_income"]) if inc else ({}, "")

    def latest_two(d: dict) -> tuple:
        ks = sorted(d)
        if len(ks) >= 2:
            return ks[-1], d[ks[-1]], d[ks[-2]]
        if len(ks) == 1:
            return ks[-1], d[ks[-1]], None
        return None, None, None

    cdate, c_now, c_prev = latest_two(contract)
    _, inv_now, inv_prev = latest_two(inventory)
    flags = []

    contract_qoq = pct_change(c_now, c_prev) if c_prev else None
    inv_qoq = pct_change(inv_now, inv_prev) if inv_prev else None

    fcf_ni = None
    if ocf and ni:
        common = sorted(set(ocf) & set(ni))
        if common:
            d = common[-1]
            fcf = ocf[d] - abs(capex.get(d, 0.0))
            if ni[d]:
                fcf_ni = fcf / ni[d]

    res.metrics = {
        "as_of": cdate,
        "contract_liab_qoq_pct": None if contract_qoq is None else round(contract_qoq, 1),
        "inventory_qoq_pct": None if inv_qoq is None else round(inv_qoq, 1),
        "fcf_to_net_income": None if fcf_ni is None else round(fcf_ni, 2),
        "accounts_used": {"contract": t_c, "inventory": t_i,
                          "ocf": t_o, "capex": t_x, "net_income": t_n},
    }
    # BUG-4 sanity: net income must not resolve to an equity/balance-sheet account.
    # If pattern priority ever drifts back onto an Equity* type, the FCF/NI ratio is
    # silently wrong — surface it as a note so a human catches the schema change.
    if t_n and re.search(r"equity", t_n, re.I):
        res.notes.append(f"⚠️ net_income 命中疑似權益科目 '{t_n}'：FCF/淨利 可能失真，"
                         f"請跑 --dump-accounts 核對並修 config account_patterns.net_income")

    got_any = any(res.metrics[k] is not None for k in
                  ("contract_liab_qoq_pct", "inventory_qoq_pct", "fcf_to_net_income"))
    if not got_any:
        res.error = ("no account matched — adjust m2_bullwhip_health.account_patterns "
                     "to the live FinMind schema (run with --dump-accounts to inspect)")
        return res

    score = 0
    if contract_qoq is not None:
        if contract_qoq >= p["contract_qoq_green_pct"]:
            score += 1
        elif contract_qoq < p["contract_qoq_red_pct"]:
            score -= 1
            flags.append("合約負債轉降：終端拉力減弱")
    if fcf_ni is not None:
        if fcf_ni >= p["fcf_ni_green"]:
            score += 1
        elif fcf_ni < p["fcf_ni_red"]:
            score -= 1
            flags.append("FCF/淨利惡化：獲利品質缺口擴大")
    if inv_qoq is not None and contract_qoq is not None:
        if inv_qoq > p["inventory_runaway_pct"] and contract_qoq < 0:
            score -= 1
            flags.append("存貨增but合約負債降：長鞭反轉徵兆")

    res.status = GREEN if score >= 1 else (RED if score <= -1 else YELLOW)
    if res.status == GREEN and fcf_ni is not None and fcf_ni < p["fcf_ni_green"]:
        res.status = YELLOW  # earnings-quality gap caps the grade until conversion proven
        flags.append(f"FCF/淨利 {fcf_ni:.2f} 未達 {p['fcf_ni_green']}：等待營運資金轉回")
    res.notes = flags
    res.headline = (
        f"合約負債 QoQ {fmt_pct(contract_qoq)} / 存貨 QoQ {fmt_pct(inv_qoq)} / "
        f"FCF/淨利 {res.metrics['fcf_to_net_income']}"
    )
    return res


# ----------------------------------------------------------------------------
# M3 — Thai subsidiary shadow (DELTA.BK)
# ----------------------------------------------------------------------------

def run_m3(cfg: dict, quarterlies: Callable) -> ModuleResult:
    res = ModuleResult("M3 thai_shadow")
    p = cfg["m3_thai_shadow"]
    try:
        data = quarterlies(cfg["ticker_th"])
    except ImportError:
        res.error = "yfinance not installed (pip install yfinance)"
        return res
    rev = data.get("revenue", {})
    if len(rev) < 5:
        # yfinance only exposes ~4-5 quarters; YoY needs 5
        res.error = f"only {len(rev)} quarters of DELTA.BK revenue available"
        if len(rev) >= 2:
            ks = sorted(rev)
            qoq = yoy(rev[ks[-1]], rev[ks[-2]])
            res.metrics = {"latest_q": ks[-1], "rev_qoq_pct": round(qoq, 1) if qoq else None}
        return res
    ks = sorted(rev)
    latest, yoy_v = ks[-1], yoy(rev[ks[-1]], rev[ks[-5]])
    gm = None
    gp = data.get("gross_profit", {})
    if latest in gp and rev[latest]:
        gm = gp[latest] / rev[latest] * 100.0
    res.metrics = {"latest_q": latest,
                   "rev_yoy_pct": round(yoy_v, 1) if yoy_v is not None else None,
                   "gross_margin_pct": round(gm, 1) if gm is not None else None}
    if yoy_v is None:
        res.error = "could not compute YoY"
        return res
    if yoy_v >= p["green_rev_yoy_pct"]:
        res.status = GREEN
    elif yoy_v >= p["yellow_rev_yoy_pct"]:
        res.status = YELLOW
    else:
        res.status = RED
    if gm is not None and gm < p["gm_floor_pct"]:
        res.status = max(res.status, YELLOW, key=lambda s: SEVERITY[s])
        res.notes.append(f"泰子公司毛利率 {gm:.1f}% 跌破 {p['gm_floor_pct']}% 地板")
    res.headline = f"DELTA.BK {latest} 營收 YoY {fmt_pct(yoy_v)}, GM {res.metrics['gross_margin_pct']}%"
    return res


# ----------------------------------------------------------------------------
# M4 — customs physical flow (US imports HS 8504.40 from TH + TW)
# ----------------------------------------------------------------------------

def run_m4(cfg: dict, fetch: Callable) -> ModuleResult:
    res = ModuleResult("M4 customs_flow")
    p = cfg["m4_customs_flow"]
    # BUG-3: Census intermittently returns an HTML maintenance/rate-limit page
    # instead of JSON. Retry once with backoff, then degrade to NO_DATA (never
    # crash the radar). Record the raw prefix so a human can diagnose.
    retries = p.get("retries", 1)
    backoff_s = p.get("retry_backoff_s", 30)
    rows = None
    last_err = None
    for attempt in range(retries + 1):
        try:
            rows = fetch(cfg, p["months_back"])
            last_err = None
            break
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff_s)
    if last_err is not None:
        res.error = f"Census fetch failed after {retries + 1} tr{'ies' if retries else 'y'}"
        res.notes.append(f"raw/exception: {str(last_err)[:120]}")
        return res  # status stays NO_DATA — degraded, not crashed
    if not rows:
        res.error = "empty Census response"
        return res
    monthly: dict[str, float] = {}
    by_country_monthly: dict[str, dict[str, float]] = {}
    for r in rows:
        monthly[r["time"]] = monthly.get(r["time"], 0.0) + r["value"]
        cty = r.get("country", "?")
        by_country_monthly.setdefault(cty, {})[r["time"]] = \
            by_country_monthly.setdefault(cty, {}).get(r["time"], 0.0) + r["value"]
    months = sorted(monthly)
    w = p["rolling_window_months"]
    if len(months) < 12 + w:
        res.error = f"only {len(months)} months — need {12 + w} for rolling YoY"
        return res
    cur = sum(monthly[m] for m in months[-w:])
    prv = sum(monthly[m] for m in months[-w - 12:-12])
    roll_yoy = yoy(cur, prv)
    # by_country: record only (judgment stays on the aggregate). Surfaces
    # production-migration tells (Thailand up / Taiwan down) that the sum hides.
    by_country: dict[str, dict] = {}
    for cty, mseries in by_country_monthly.items():
        if len(mseries) < 12 + w:
            continue
        cm = sorted(mseries)
        c_cur = sum(mseries[m] for m in cm[-w:])
        c_prv = sum(mseries[m] for m in cm[-w - 12:-12])
        c_yoy = yoy(c_cur, c_prv)
        by_country[cty] = {"rolling_value_usd_m": round(c_cur / 1e6, 1),
                           "rolling_yoy_pct": round(c_yoy, 1) if c_yoy is not None else None}
    res.metrics = {
        "window": f"{months[-w]}..{months[-1]}",
        "rolling_value_usd_m": round(cur / 1e6, 1),
        "rolling_yoy_pct": round(roll_yoy, 1) if roll_yoy is not None else None,
        "by_country": by_country,
    }
    if roll_yoy is None:
        res.error = "zero base period"
        return res
    if roll_yoy >= p["green_yoy_pct"]:
        res.status = GREEN
    elif roll_yoy >= p["yellow_yoy_pct"]:
        res.status = YELLOW
    else:
        res.status = RED
    res.headline = (f"US 進口 HS{p['hs_code']} (TH+TW) 近{w}月 "
                    f"${res.metrics['rolling_value_usd_m']}M, YoY {fmt_pct(roll_yoy)}")
    return res


# ----------------------------------------------------------------------------
# M5 — narrative triggers (RSS keyword buckets)
# ----------------------------------------------------------------------------

_MEDIA_SUFFIX = re.compile(r"\s[-|–—]\s[^-|–—]{1,40}$")  # " - Reuters", " | Tom's Hardware"


def _normalize_title(title: str) -> str:
    """Lowercase, drop trailing media name, strip punctuation → dedup key."""
    t = _MEDIA_SUFFIX.sub("", title or "")
    t = re.sub(r"[^a-z0-9 ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def _dedup_events(titles: list[str]) -> tuple[list[str], int]:
    """Near-dup collapse: same event reported by N outlets = 1 event, N mentions.

    Keyed on the token set of the normalized title (order/outlet independent).
    Returns (representative_titles, mention_count)."""
    seen: dict[frozenset, str] = {}
    for t in titles:
        key = frozenset(_normalize_title(t).split())
        if not key:
            continue
        # merge into an existing event if token sets substantially overlap
        matched = None
        for k in seen:
            inter = len(key & k)
            if inter and inter >= 0.6 * min(len(key), len(k)):
                matched = k
                break
        if matched is None:
            seen[key] = t
    return list(seen.values()), len(titles)


def _m5_baseline(history: list, bucket: str) -> tuple[Optional[float], Optional[float], int]:
    """Rolling mean/std of a bucket's event count over recent M5 runs in state.

    Prefers the new `events` metric; falls back to legacy `hits` counts so the
    baseline works during the transition. Returns (mean, std, n_samples)."""
    vals: list[float] = []
    for e in history[-11:]:  # last ~10 prior runs
        for m in e.get("modules", []):
            if _module_short(m.get("module", "")) != "M5":
                continue
            met = m.get("metrics", {}) or {}
            ev = (met.get("events") or {}).get(bucket)
            if ev is None:
                ev = (met.get("hits") or {}).get(bucket)
            if ev is not None:
                vals.append(float(ev))
    if len(vals) < 2:
        return None, None, len(vals)
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
    return mean, var ** 0.5, len(vals)


def run_m5(cfg: dict, fetch: Callable, history: Optional[list] = None) -> ModuleResult:
    """RSS narrative buckets with (v2) event dedup, z-score gating, denial cap.

    BUG-2: absolute hit thresholds誤觸 on natural news-volume swings. We now
    dedup near-dup reports into events, and score each bucket by its z-score
    vs the bucket's own rolling baseline in state.json. Cold start (<min
    samples) falls back to absolute event thresholds. An official denial of a
    rumor caps the bucket at YELLOW ('爭議中') — a denied rumor is a live
    dispute, not a confirmed RED."""
    res = ModuleResult("M5 narrative_triggers")
    p = cfg["m5_narrative_triggers"]
    history = history or []
    z_yellow = p.get("z_yellow", 1.5)
    z_red = p.get("z_red", 2.5)
    min_samples = p.get("z_min_samples", 5)

    events: dict[str, int] = {}
    mentions: dict[str, int] = {}
    denials: dict[str, bool] = {}
    reps: dict[str, list[str]] = {}
    fetched_any = False
    for bucket, spec in p["buckets"].items():
        url = cfg["endpoints"]["gnews_rss"].format(query=urllib.parse.quote(spec["query"]))
        try:
            items = fetch(url)
            fetched_any = True
        except Exception as e:  # per-feed network failure shouldn't kill the module
            res.notes.append(f"feed {bucket} failed: {e}")
            continue
        kw = [k.lower() for k in spec["keywords"]]
        must = [m.lower() for m in spec.get("must_include", [])]
        deny_kw = [d.lower() for d in spec.get("denial_keywords", [])]
        raw_titles: list[str] = []
        denial_found = False
        for it in items[: p["max_items_per_feed"]]:
            text = (it["title"] + " " + it["summary"]).lower()
            if must and not any(m in text for m in must):
                continue  # hard topical filter — e.g. consumer-GPU delay noise
            if any(k in text for k in kw):
                raw_titles.append(it["title"][:120])
                if deny_kw and any(d in text for d in deny_kw):
                    denial_found = True
        ev_titles, n_mentions = _dedup_events(raw_titles)
        events[bucket] = len(ev_titles)
        mentions[bucket] = n_mentions
        denials[bucket] = denial_found
        reps[bucket] = ev_titles

    if not fetched_any:
        res.error = "all RSS feeds failed"
        return res

    # Per-bucket status: z-score when baseline available, else absolute events.
    worst = GREEN
    bucket_status: dict[str, str] = {}
    scoring: dict[str, dict] = {}
    for bucket, spec in p["buckets"].items():
        n_ev = events.get(bucket, 0)
        mean, std, n_s = _m5_baseline(history, bucket)
        used = "absolute"
        z = None
        st = GREEN
        if n_s >= min_samples and std and std > 0:
            used = "zscore"
            z = (n_ev - mean) / std
            if z >= z_red:
                st = RED
            elif z >= z_yellow:
                st = YELLOW
        else:
            if n_ev >= spec["red_hits"]:
                st = RED
            elif n_ev >= spec["yellow_hits"]:
                st = YELLOW
        # denial cap: a rumor officially denied is a live dispute, not a RED
        if denials.get(bucket) and SEVERITY[st] > SEVERITY[YELLOW]:
            st = YELLOW
            res.notes.append(f"[{bucket}] 官方否認偵測 → 上限 🟡（爭議中）")
        bucket_status[bucket] = st
        scoring[bucket] = {"events": n_ev, "mentions": mentions.get(bucket, 0),
                           "gate": used, "z": None if z is None else round(z, 2),
                           "denial": denials.get(bucket, False)}
        if SEVERITY[st] > SEVERITY[worst]:
            worst = st

    res.status = worst
    res.metrics = {"events": events, "mentions": mentions, "scoring": scoring}
    res.notes += [f"[{b}] {t}" for b in reps for t in reps[b][:3]]
    res.headline = " / ".join(
        f"{b}:{events[b]}e" + (f"({mentions[b]}m)" if mentions[b] != events[b] else "")
        for b in events)
    return res


# ----------------------------------------------------------------------------
# M6 — peer divergence (cross-supplier relative-momentum panel)
# ----------------------------------------------------------------------------

def _monthly_yoy(rows: list[dict]) -> dict[tuple, float]:
    """FinMind monthly-revenue rows → {(year, month): YoY%}. Empty if unusable."""
    series: dict[tuple, float] = {}
    for r in rows:
        try:
            series[(int(r["revenue_year"]), int(r["revenue_month"]))] = float(r["revenue"])
        except (KeyError, TypeError, ValueError):
            continue
    out: dict[tuple, float] = {}
    for (y, m), v in series.items():
        prev = series.get((y - 1, m))
        yv = yoy(v, prev)
        if yv is not None:
            out[(y, m)] = yv
    return out


def _avg3_at(yoy_map: dict[tuple, float], months: list[tuple], end_idx: int) -> Optional[float]:
    """3-month average YoY ending at months[end_idx]; None if any of the 3 missing."""
    if end_idx < 2:
        return None
    window = months[end_idx - 2: end_idx + 1]
    vals = [yoy_map[mk] for mk in window if mk in yoy_map]
    return sum(vals) / 3.0 if len(vals) == 3 else None


def run_m6(cfg: dict, fetch: Callable) -> ModuleResult:
    """Cohort relative-momentum: we trade the divergence, not the level.

    Taiwan's mandatory monthly-revenue disclosure is the structural edge — we
    see who in a supplier cohort inflects first, a month+ before US peers report.
    For each group we compute 3-month-average YoY per member and the gap of the
    best competitor over 2308. Direction decides escalation:
      * peer_lead_risk (power/cooling): a peer pulling ahead of 2308 is a
        share-loss tell → escalate.
      * cohort_confirm (rack): the chain moving together is a pull-through
        confirm, not a warning → reported, never escalates on its own.
    The instrument reports divergence; a human judges what it means."""
    res = ModuleResult("M6 peer_divergence")
    p = cfg["m6_peer_divergence"]
    delta_id = cfg["ticker_tw"]
    start = (dt.date.today() - dt.timedelta(days=900)).isoformat()

    # Fetch each distinct member once (cohorts overlap on 2308).
    member_ids = {mid for grp in p["cohort"].values() for mid in grp["members"]}
    yoy_by_id: dict[str, dict[tuple, float]] = {}
    for mid in sorted(member_ids):
        try:
            yoy_by_id[mid] = _monthly_yoy(fetch("TaiwanStockMonthRevenue", mid, start, cfg))
        except Exception as e:
            res.notes.append(f"fetch {mid} failed: {str(e)[:80]}")
            yoy_by_id[mid] = {}

    if not yoy_by_id.get(delta_id):
        res.error = "no monthly-revenue history for 2308"
        return res

    consec = p.get("red_requires_consec_months", 2)
    group_out: dict[str, dict] = {}
    worst = GREEN
    for gname, grp in p["cohort"].items():
        direction = grp.get("direction", "peer_lead_risk")
        peers = [m for m in grp["members"] if m != delta_id]
        d_yoy = yoy_by_id.get(delta_id, {})
        # month endpoints where 2308 has a full 3m window
        months = sorted(d_yoy)
        if len(months) < 3:
            group_out[gname] = {"status": NO_DATA, "note": "2308 history <3 months"}
            continue
        delta_3m = _avg3_at(d_yoy, months, len(months) - 1)
        peer_3m: dict[str, Optional[float]] = {}
        for pid in peers:
            pm = sorted(yoy_by_id.get(pid, {}))
            # align peer's own latest full 3m window
            peer_3m[pid] = _avg3_at(yoy_by_id.get(pid, {}), pm, len(pm) - 1) if len(pm) >= 3 else None
        live_peers = {k: v for k, v in peer_3m.items() if v is not None}
        if delta_3m is None or not live_peers:
            group_out[gname] = {"status": NO_DATA, "note": "insufficient peer/2308 3m data",
                                "delta_3m_yoy": None if delta_3m is None else round(delta_3m, 1)}
            continue
        best_pid = max(live_peers, key=live_peers.get)
        gap_pp = live_peers[best_pid] - delta_3m  # positive = peer ahead of 2308

        gstatus = GREEN
        if direction == "peer_lead_risk":
            if gap_pp >= p["divergence_red_pp"]:
                # RED requires the gap to persist over the last `consec` month-ends
                lead_series = []
                for i in range(len(months) - 1, -1, -1):
                    d3 = _avg3_at(d_yoy, months, i)
                    if d3 is None:
                        break
                    # best peer 3m at the same endpoint
                    bp = None
                    mk = months[i]
                    for pid in peers:
                        pmm = sorted(yoy_by_id.get(pid, {}))
                        if mk in yoy_by_id.get(pid, {}):
                            j = pmm.index(mk)
                            v = _avg3_at(yoy_by_id.get(pid, {}), pmm, j)
                            if v is not None:
                                bp = v if bp is None else max(bp, v)
                    if bp is None:
                        break
                    lead_series.append(bp - d3)
                    if len(lead_series) >= consec:
                        break
                if len(lead_series) >= consec and all(x >= p["divergence_red_pp"] for x in lead_series[:consec]):
                    gstatus = RED
                else:
                    gstatus = YELLOW  # gap present but not yet persistent
            elif gap_pp >= p["divergence_yellow_pp"]:
                gstatus = YELLOW
        # cohort_confirm groups stay GREEN (informational); still reported below.

        group_out[gname] = {
            "direction": direction,
            "delta_3m_yoy": round(delta_3m, 1),
            "best_peer": best_pid,
            "best_peer_3m_yoy": round(live_peers[best_pid], 1),
            "peer_lead_pp": round(gap_pp, 1),
            "status": gstatus,
            "peers_3m_yoy": {k: round(v, 1) for k, v in live_peers.items()},
        }
        if SEVERITY[gstatus] > SEVERITY[worst]:
            worst = gstatus

    live_groups = [g for g in group_out.values() if g.get("status") != NO_DATA]
    if not live_groups:
        res.error = "no cohort group had sufficient data"
        res.metrics = {"groups": group_out}
        return res

    res.status = worst
    res.metrics = {"groups": group_out}
    escalated = [f"{gn}:{gd['best_peer']}領先{gd['peer_lead_pp']:+.0f}pp"
                 for gn, gd in group_out.items()
                 if gd.get("status") in (YELLOW, RED) and gd.get("direction") == "peer_lead_risk"]
    res.headline = ("；".join(escalated) if escalated
                    else "cohort 內 2308 未被對手顯著反超（離散在容忍帶內）")
    for gn, gd in group_out.items():
        if gd.get("status") in (YELLOW, RED):
            res.notes.append(f"[{gn}] {gd['best_peer']} 3m YoY {gd['best_peer_3m_yoy']}% "
                             f"vs 2308 {gd['delta_3m_yoy']}%（領先 {gd['peer_lead_pp']:+.0f}pp）")
    return res


# ----------------------------------------------------------------------------
# M8 — analyst revision velocity (target-price up/down direction from RSS)
# ----------------------------------------------------------------------------

def _last_module_metric(history: list, mod_short: str) -> dict:
    """Most recent metrics dict for a module across state history ({} if none)."""
    for e in reversed(history or []):
        for m in e.get("modules", []):
            if _module_short(m.get("module", "")) == mod_short:
                return m.get("metrics", {}) or {}
    return {}


def run_m8(cfg: dict, fetch: Callable, history: Optional[list] = None) -> ModuleResult:
    """Consensus revision velocity: we can't get sell-side decks, but we can
    count the direction/frequency of target-price revisions. The inflection
    matters more than the level. Low-tech RSS version (no target numbers —
    unreliable in headlines — only up/down direction). A single down-heavy run
    is not enough: escalation to YELLOW requires two consecutive elevated runs
    (state-backed consec gate) so one noisy day doesn't flip the light."""
    res = ModuleResult("M8 revision_velocity")
    p = cfg["m8_revision_velocity"]
    history = history or []
    url = cfg["endpoints"]["gnews_rss"].format(query=urllib.parse.quote(p["query"]))
    try:
        items = fetch(url)
    except Exception as e:
        res.error = f"revision feed failed: {str(e)[:100]}"
        return res
    up_kw = [k.lower() for k in p["up_keywords"]]
    down_kw = [k.lower() for k in p["down_keywords"]]
    up, down = 0, 0
    up_t, down_t = [], []
    for it in items[: p.get("max_items", 40)]:
        text = (it["title"] + " " + it.get("summary", "")).lower()
        mu = any(k in text for k in up_kw)
        md = any(k in text for k in down_kw)
        if md and not mu:
            down += 1
            down_t.append(it["title"][:120])
        elif mu and not md:
            up += 1
            up_t.append(it["title"][:120])
        # ambiguous (both / neither) → skip
    total = up + down
    down_ratio = (down / total) if total else None
    res.metrics = {"up_hits": up, "down_hits": down, "total": total,
                   "down_ratio": None if down_ratio is None else round(down_ratio, 2)}

    if total < p.get("min_total", 3):
        res.status = GREEN
        res.headline = f"下修 {down}/上修 {up}（樣本不足 <{p.get('min_total', 3)}，暫不評級）"
        return res

    yellow_ratio = p.get("yellow_down_ratio", 0.6)
    elevated = down_ratio >= yellow_ratio
    prev = _last_module_metric(history, "M8")
    prev_ratio = prev.get("down_ratio")
    prev_elevated = prev_ratio is not None and prev_ratio >= yellow_ratio

    if elevated and (prev_elevated or not p.get("require_consec", True)):
        res.status = YELLOW
        res.notes.append(f"下修佔比 {down_ratio:.0%} 連 2 次 run 偏高 → 共識轉向徵兆")
    elif elevated:
        res.status = GREEN
        res.notes.append(f"下修佔比 {down_ratio:.0%} 偏高，但單次；待下一 run 確認才升級")
    else:
        res.status = GREEN
    res.notes += [f"[down] {t}" for t in down_t[:3]]
    res.headline = f"目標價 下修 {down}/上修 {up}（下修佔比 {down_ratio:.0%}）"
    return res


# ----------------------------------------------------------------------------
# Aggregation, report, state
# ----------------------------------------------------------------------------

def aggregate(results: list[ModuleResult], cfg: dict) -> str:
    live = [r for r in results if r.status != NO_DATA]
    if not live:
        return NO_DATA
    reds = sum(1 for r in live if r.status == RED)
    yellows = sum(1 for r in live if r.status == YELLOW)
    a = cfg["aggregation"]
    if reds >= a["overall_red_min_reds"]:
        return RED
    if reds >= 1 or yellows >= a["overall_yellow_min_yellows"]:
        return YELLOW
    return GREEN


def render_report(results: list[ModuleResult], overall: str, cfg: dict,
                  partial_modules: Optional[list[str]] = None,
                  m7: Optional[dict] = None) -> str:
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if partial_modules:
        # BUG-1: a partial run has no real overall verdict — show the module
        # colour only as reference, clearly flagged, never as a总判定.
        verdict_line = (f"## 總判定：⚪ PARTIAL（僅跑 {','.join(partial_modules)}）"
                        f"｜模組色僅供參考 {EMOJI.get(overall, '')} {overall}")
    else:
        verdict_line = f"## 總判定：{EMOJI[overall]} {overall}"
    lines = [
        f"# Delta Radar (2308.TW) — {now}",
        "",
        verdict_line,
        "",
        "GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、",
        "敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。",
        "M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。",
        "",
        "| 模組 | 狀態 | 摘要 |",
        "|---|---|---|",
    ]
    for r in results:
        head = r.headline or (r.error or "")
        lines.append(f"| {r.module} | {EMOJI[r.status]} {r.status} | {head} |")
    lines.append("")
    for r in results:
        lines.append(f"### {r.module} — {EMOJI[r.status]} {r.status}")
        if r.metrics:
            lines.append("```json")
            lines.append(json.dumps(r.metrics, ensure_ascii=False, indent=2))
            lines.append("```")
        for n in r.notes:
            lines.append(f"- {n}")
        if r.error:
            lines.append(f"- ⚠️ degraded: {r.error}")
        lines.append("")

    # M7 is a background task, not a status module — but it must be VISIBLE so a
    # reader can confirm outcome backfill ran (and check the accumulating sample).
    lines.append("### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）")
    if m7 is None:
        lines.append("- 本次未執行（--modules 未含掃描主流程或 M7 停用）")
    elif m7.get("error"):
        lines.append(f"- ⚠️ 本次回填降級：{m7['error']}")
        lines.append("- （不影響掃描；FinMind 價格暫時抓不到，下次 run 會補）")
    else:
        lines.append(f"- 本次回填 **{m7.get('changed', 0)}** 筆；"
                     f"state 已有 outcomes 的 entry：**{m7.get('scored', 0)}/{m7.get('total', 0)}**")
        lines.append(f"- 遠期報酬視窗：T+{'/'.join(str(h) for h in m7.get('horizons', []))}"
                     f"（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表")
    lines.append("")

    lines.append("---")
    lines.append("*delta_radar — optscnr radar family. Shadow-mode instrument: "
                 "this is a measurement device, not a trade signal.*")
    return "\n".join(lines)


def append_state(results: list[ModuleResult], overall: str, path: str,
                 modules_requested: list[str]) -> None:
    entry = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        "overall": overall,
        "modules_requested": sorted(modules_requested),
        "modules": [asdict(r) for r in results],
    }
    history = []
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------------------
# M7 — outcome backfill (T+5/10/20 forward returns onto past state entries)
# ----------------------------------------------------------------------------

def _price_close_series(rows: list[dict]) -> list[tuple]:
    """FinMind TaiwanStockPrice rows → sorted [(date_str, close_float)]."""
    out = []
    for r in rows:
        d = r.get("date")
        c = r.get("close", r.get("Close"))
        if d is None or c is None:
            continue
        try:
            out.append((str(d), float(c)))
        except (TypeError, ValueError):
            continue
    out.sort(key=lambda x: x[0])
    return out


def _forward_return_pct(series: list[tuple], entry_date: str, n: int) -> Optional[float]:
    """Return % from the first trading close on/after entry_date to n trading days later."""
    dates = [d for d, _ in series]
    # first trading day index with date >= entry_date
    t0 = next((i for i, d in enumerate(dates) if d >= entry_date), None)
    if t0 is None or t0 + n >= len(series):
        return None
    base = series[t0][1]
    fut = series[t0 + n][1]
    if base == 0:
        return None
    return round((fut - base) / base * 100.0, 2)


def backfill_outcomes(cfg: dict, state_path: str, fetch: Callable) -> int:
    """Backfill T+N forward returns onto every state entry. Idempotent.

    delta_radar's whole point is to become falsifiable: without knowing what
    happened to 2308 after each verdict, gate effectiveness can never be
    backtested and the instrument never graduates.

    Stores BOTH the raw 2308 return and the market-adjusted excess return
    (2308 − benchmark over the same T+N window). Excess is the number that
    matters: absolute returns are dominated by market beta (a down month makes
    every cohort look bad regardless of gate quality); the excess strips that
    common drift so a gate's *relative* predictive power can surface.
    Returns the number of entries whose outcomes changed this run."""
    if not os.path.exists(state_path):
        return 0
    with open(state_path, encoding="utf-8") as f:
        history = json.load(f)
    if not history:
        return 0
    m7 = cfg.get("m7_outcome_backfill", {})
    horizons = m7.get("horizons", [5, 10, 20])
    bench_id = m7.get("benchmark", "0050")
    entry_dates = [e["ts"][:10] for e in history if e.get("ts")]
    start = (dt.date.fromisoformat(min(entry_dates)) - dt.timedelta(days=15)).isoformat()
    rows = fetch("TaiwanStockPrice", cfg["ticker_tw"], start, cfg)
    series = _price_close_series(rows)
    if not series:
        raise RuntimeError("empty/again-unusable TaiwanStockPrice response")
    # Benchmark for excess return. Same TWSE calendar → same trading-day index.
    # Failure to fetch it must NOT lose the raw returns — degrade excess to None.
    bench_series: list[tuple] = []
    try:
        bench_series = _price_close_series(fetch("TaiwanStockPrice", bench_id, start, cfg))
    except Exception:
        bench_series = []

    changed = 0
    for e in history:
        ed = e.get("ts", "")[:10]
        if not ed:
            continue
        prev = e.get("outcomes") or {}
        outcomes = {"entry_date": ed, "benchmark": bench_id}
        # entry close = first trading close on/after entry date
        dates = [d for d, _ in series]
        t0 = next((i for i, d in enumerate(dates) if d >= ed), None)
        outcomes["entry_close"] = series[t0][1] if t0 is not None else None
        for n in horizons:
            stock_ret = _forward_return_pct(series, ed, n)
            outcomes[f"t{n}_ret_pct"] = stock_ret
            bench_ret = _forward_return_pct(bench_series, ed, n) if bench_series else None
            outcomes[f"t{n}_excess_pct"] = (
                None if stock_ret is None or bench_ret is None
                else round(stock_ret - bench_ret, 2))
        # only count as changed if any value actually differs (idempotent)
        if {k: prev.get(k) for k in outcomes} != outcomes:
            e["outcomes"] = outcomes
            changed += 1
        elif "outcomes" not in e:
            e["outcomes"] = outcomes
    if changed:
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    return changed


def _module_short(name: str) -> str:
    """'M5 narrative_triggers' -> 'M5'."""
    return name.split()[0] if name else name


def print_hit_rate(cfg: dict, state_path: str) -> int:
    """Per-(module, status) EXCESS-return table (2308 − benchmark).

    Leads with market-adjusted excess so beta doesn't pollute every cohort;
    the raw market drift is shown once as context, not folded into each row."""
    if not os.path.exists(state_path):
        print("no state file")
        return 1
    with open(state_path, encoding="utf-8") as f:
        history = json.load(f)
    m7 = cfg.get("m7_outcome_backfill", {})
    horizons = m7.get("horizons", [5, 10, 20])
    bench_id = m7.get("benchmark", "0050")
    scored = [e for e in history if e.get("outcomes")]
    if not scored:
        print("no entries have outcomes yet — run the radar (or backfill) first")
        return 1

    def avg(vals):
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    def cell(a):
        return f"{a:+.2f}" if a is not None else "—"

    has_excess = any(e["outcomes"].get(f"t{horizons[0]}_excess_pct") is not None
                     or any(e["outcomes"].get(f"t{n}_excess_pct") is not None for n in horizons)
                     for e in scored)
    metric = "excess_pct" if has_excess else "ret_pct"

    # cohorts keyed by "M5=RED" etc; a module contributes its own status per entry
    cohorts: dict[str, list] = {}
    for e in scored:
        for m in e.get("modules", []):
            key = f"{_module_short(m['module'])}={m['status']}"
            cohorts.setdefault(key, []).append(e["outcomes"])

    col = "超額%" if has_excess else "絕對%"
    hz_hdr = " | ".join(f"T+{n} {col}" for n in horizons)
    label = f"EXCESS vs {bench_id}" if has_excess else "ABSOLUTE (no benchmark yet — re-backfill on next run)"
    print(f"\n# delta_radar hit-rate — {label} — {len(scored)} scored entries\n")
    if has_excess:
        # market drift context: raw 2308 vs raw benchmark, shown once
        raw2308 = {n: avg([e["outcomes"].get(f"t{n}_ret_pct") for e in scored]) for n in horizons}
        drift = {n: avg([(e["outcomes"].get(f"t{n}_ret_pct") or 0) - (e["outcomes"].get(f"t{n}_excess_pct") or 0)
                         for e in scored if e["outcomes"].get(f"t{n}_excess_pct") is not None])
                 for n in horizons}
        print("_市場基準同期漂移（beta，看一次即可，不再污染下表每格）："
              + " ｜ ".join(f"T+{n} {bench_id} {cell(drift[n])} / 2308絕對 {cell(raw2308[n])}" for n in horizons)
              + "_\n")
    print(f"| cohort | n | {hz_hdr} |")
    print("|---|---|" + "---|" * len(horizons))
    base = {n: avg([e["outcomes"].get(f"t{n}_{metric}") for e in scored]) for n in horizons}
    print(f"| **baseline (all)** | {len(scored)} | "
          + " | ".join(cell(base[n]) for n in horizons) + " |")
    for key in sorted(cohorts):
        rowset = cohorts[key]
        cells = " | ".join(cell(avg([o.get(f"t{n}_{metric}") for o in rowset])) for n in horizons)
        print(f"| {key} | {len(rowset)} | {cells} |")
    print(f"\n_超額報酬 = 2308 − {bench_id}（同 T+N 交易日視窗），已抽掉市場 beta。"
          "shadow-mode instrument：校準 gate 有效性，非交易訊號。"
          "n 小、單一行情時只讀方向不讀精度。_")
    return 0


# ----------------------------------------------------------------------------
# Selftest fixtures (zero-network full pipeline)
# ----------------------------------------------------------------------------

def _fixtures() -> dict:
    # Per-ticker monthly growth rate → constant YoY = (r**12 - 1). Chosen so:
    #   2308 YoY ~+34.5% (M1 GREEN); Lite-On(2301) ~+51% leads 2308 by ~16pp
    #   → M6 power group YELLOW (exercises the peer-lead escalation path).
    _MREV_GROWTH = {"2308": 1.025, "2301": 1.035, "6282": 1.020,
                    "3324": 1.028, "3017": 1.026,
                    "2317": 1.030, "2382": 1.029, "6669": 1.031}

    def finmind_fake(dataset, data_id, start_date, cfg):
        if dataset == "TaiwanStockMonthRevenue":
            rows = []
            base = 40_000_000_000
            r = _MREV_GROWTH.get(str(data_id), 1.025)
            for i in range(30):
                y, m = divmod((2024 * 12 + 0) + i, 12)
                rows.append({"revenue_year": y, "revenue_month": m + 1,
                             "revenue": base * (r ** i), "date": f"{y}-{m+1:02d}-10"})
            return rows
        if dataset == "TaiwanStockPrice":
            # deterministic daily series, weekdays only, from 2026-05-01.
            # 2308 +1%/day, benchmark(0050) +0.5%/day → non-trivial excess so the
            # M7 excess-return path is exercised: t5 excess ≈ 5.10 − 2.53 = +2.57%.
            per_day = 1.005 if str(data_id) != cfg.get("ticker_tw", "2308") else 1.01
            rows = []
            d = dt.date(2026, 5, 1)
            close = 300.0
            while d <= dt.date(2026, 8, 31):
                if d.weekday() < 5:  # Mon-Fri
                    rows.append({"date": d.isoformat(), "close": round(close, 2)})
                    close *= per_day
                d += dt.timedelta(days=1)
            return rows
        if dataset == "TaiwanStockBalanceSheet":
            return [
                {"date": "2025-12-31", "type": "CurrentContractLiabilities", "value": 30e9},
                {"date": "2026-03-31", "type": "CurrentContractLiabilities", "value": 36e9},
                {"date": "2026-03-31", "type": "CurrentContractLiabilities_per", "value": 4.2},
                {"date": "2026-03-31", "type": "Inventories_per", "value": 13.9},
                {"date": "2025-12-31", "type": "Inventories", "value": 105e9},
                {"date": "2026-03-31", "type": "Inventories", "value": 119.1e9},
            ]
        if dataset == "TaiwanStockCashFlowsStatement":
            return [
                {"date": "2026-03-31", "type": "CashFlowsFromOperatingActivities", "value": 19.93e9},
                {"date": "2026-03-31", "type": "AcquisitionOfPropertyPlantAndEquipment", "value": -11.1e9},
            ]
        if dataset == "TaiwanStockFinancialStatements":
            return [{"date": "2026-03-31", "type": "IncomeAfterTaxes", "value": 20.55e9}]
        return []

    def quarterlies_fake(ticker):
        return {
            "revenue": {"2025-03-31": 39.3e9, "2025-06-30": 45.0e9, "2025-09-30": 52.0e9,
                        "2025-12-31": 58.0e9, "2026-03-31": 61.38e9},
            "gross_profit": {"2026-03-31": 19.466e9},
            "net_income": {"2026-03-31": 9.08e9},
        }

    def census_fake(cfg, months_back):
        rows = []
        for i in range(28):
            y, m = divmod(2024 * 12 + i, 12)
            for cname, mult in (("THAILAND", 1.0), ("TAIWAN", 0.4)):
                rows.append({"time": f"{y}-{m+1:02d}", "country": cname,
                             "value": 250e6 * mult * (1 + 0.04 * i)})
        return rows

    def rss_fake(url):
        q = urllib.parse.unquote(url).lower()
        if "kyber" in q or "rubin" in q or "vr300" in q:
            # M5 vr300 bucket: 4 near-dup delay reports (→ 1 event, 4 mentions)
            # + 1 official denial (→ separate event, triggers 爭議中 cap).
            return [
                {"title": "Nvidia Kyber rack for Rubin Ultra delayed to 2028", "summary": "", "date": ""},
                {"title": "Nvidia delays Kyber AI rack to 2028 over PCB issues - Tom's Hardware", "summary": "", "date": ""},
                {"title": "Report: Nvidia Kyber Rubin Ultra rack pushed to 2028", "summary": "", "date": ""},
                {"title": "Kyber rack for Rubin Ultra delayed to 2028, stopgap axed - DigiTimes", "summary": "", "date": ""},
                {"title": "NVIDIA quashes Rubin and Kyber rack delay rumors", "summary": "roadmap intact", "date": ""},
            ]
        if "目標價" in q or "評等" in q:
            # M8 revision feed: down-heavy (3 down / 1 up → down_ratio 0.75).
            return [
                {"title": "外資下修台達電目標價至 400 元", "summary": "", "date": ""},
                {"title": "某券商調降台達電評等至中立", "summary": "", "date": ""},
                {"title": "台達電遭調降目標價", "summary": "", "date": ""},
                {"title": "分析師上修台達電目標價", "summary": "", "date": ""},
            ]
        # capex_cut / debt_financed_capex / lc_psu → benign (0 hits)
        return [{"title": "Hyperscaler reaffirms record capex for AI buildout",
                 "summary": "capital expenditure guidance raised", "date": ""}]

    return {"finmind": finmind_fake, "quarterlies": quarterlies_fake,
            "census": census_fake, "rss": rss_fake}


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Delta Electronics (2308.TW) mosaic radar")
    ap.add_argument("--config", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config", "delta_radar_config.json"))
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--modules", default="m1,m2,m3,m4,m5,m6,m8",
                    help="comma list, e.g. m1,m4")
    ap.add_argument("--selftest", action="store_true",
                    help="run full pipeline on bundled fixtures (no network)")
    ap.add_argument("--dump-accounts", action="store_true",
                    help="print distinct FinMind balance-sheet account names and exit")
    ap.add_argument("--hit-rate", action="store_true",
                    help="print per-module T+N forward-return table from state and exit")
    ap.add_argument("--backfill-only", action="store_true",
                    help="only backfill T+N outcomes onto existing state, then exit")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    # --selftest must NOT touch the real state.json / report — fixture verdicts
    # would corrupt the append-only backtest sample. Route output to a throwaway
    # temp dir. (The report is still printed to stdout so the run is observable.)
    if args.selftest:
        out_dir = tempfile.mkdtemp(prefix="delta_radar_selftest_")
    else:
        out_dir = args.output_dir or cfg.get("output_dir", "output")
    os.makedirs(out_dir, exist_ok=True)

    fx = _fixtures() if args.selftest else {
        "finmind": finmind_fetch, "quarterlies": yfinance_quarterlies,
        "census": census_fetch, "rss": rss_fetch,
    }

    if args.dump_accounts:
        start = (dt.date.today() - dt.timedelta(days=400)).isoformat()
        for ds in ("TaiwanStockBalanceSheet",
                   "TaiwanStockCashFlowsStatement",
                   "TaiwanStockFinancialStatements"):
            print(f"\n===== {ds} =====")
            try:
                rows = fx["finmind"](ds, cfg["ticker_tw"], start, cfg)
                for t in sorted({r.get("type", "") for r in rows}):
                    print(t)
            except Exception as e:
                print(f"(fetch failed: {e})")
        return 0

    real_state = os.path.join(
        args.output_dir or cfg.get("output_dir", "output"), "delta_radar_state.json")

    if args.hit_rate:
        return print_hit_rate(cfg, real_state)

    if args.backfill_only:
        n = backfill_outcomes(cfg, real_state, fx["finmind"])
        print(f"backfilled outcomes on {n} entries", file=sys.stderr)
        return 0

    # M5 z-score and M8 consec gate read prior runs from the SAME state file we
    # append to (out_dir). In --selftest out_dir is a fresh temp dir → cold start,
    # keeping the selftest hermetic (never reads the real backtest history).
    state_path = os.path.join(out_dir, "delta_radar_state.json")
    prior_history: list = []
    if os.path.exists(state_path):
        try:
            with open(state_path, encoding="utf-8") as f:
                prior_history = json.load(f)
        except Exception:
            prior_history = []

    wanted = {m.strip().lower() for m in args.modules.split(",")}
    runners = {
        "m1": lambda: run_m1(cfg, fx["finmind"]),
        "m2": lambda: run_m2(cfg, fx["finmind"]),
        "m3": lambda: run_m3(cfg, fx["quarterlies"]),
        "m4": lambda: run_m4(cfg, fx["census"]),
        "m5": lambda: run_m5(cfg, fx["rss"], prior_history),
        "m6": lambda: run_m6(cfg, fx["finmind"]),
        "m8": lambda: run_m8(cfg, fx["rss"], prior_history),
    }
    ran_keys: list[str] = []
    results: list[ModuleResult] = []
    for key in MODULE_ORDER:
        if key not in wanted:
            continue
        ran_keys.append(key)
        try:
            results.append(runners[key]())
        except Exception as e:  # absolute backstop — never crash the radar
            r = ModuleResult(f"{key.upper()} (crashed)")
            r.error = f"{type(e).__name__}: {e}"
            if os.environ.get("DELTA_RADAR_DEBUG"):
                traceback.print_exc()
            results.append(r)

    overall = aggregate(results, cfg)
    # BUG-1: only a run covering every module yields a real overall verdict.
    # Anything narrower is tagged PARTIAL(...) so backtests can filter it out.
    is_partial = set(ran_keys) != set(MODULE_ORDER)
    state_overall = (f"PARTIAL({','.join(ran_keys)})" if is_partial else overall)
    report_path = os.path.join(out_dir, "delta_radar_report.md")
    append_state(results, state_overall, state_path, ran_keys)

    # M7: after each run, backfill T+5/10/20 outcomes onto past entries (runs
    # BEFORE render so the report can surface it). Never crashes the run.
    # In --selftest, exercise on fixture prices against the throwaway state.
    m7_cfg = cfg.get("m7_outcome_backfill", {})
    m7_summary: Optional[dict] = None
    if m7_cfg.get("enabled", True):
        fetch = fx["finmind"] if args.selftest else finmind_fetch
        try:
            changed = backfill_outcomes(cfg, state_path, fetch)
            with open(state_path, encoding="utf-8") as f:
                hist = json.load(f)
            scored = sum(1 for e in hist if e.get("outcomes"))
            m7_summary = {"changed": changed, "scored": scored, "total": len(hist),
                          "horizons": m7_cfg.get("horizons", [5, 10, 20])}
            print(f"[m7] backfilled {changed} entries ({scored}/{len(hist)} scored)",
                  file=sys.stderr)
        except Exception as e:
            m7_summary = {"error": f"{type(e).__name__}: {e}"}
            print(f"[m7] backfill skipped: {type(e).__name__}: {e}", file=sys.stderr)

    report = render_report(results, overall, cfg,
                           partial_modules=ran_keys if is_partial else None,
                           m7=m7_summary)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n[written] {report_path}\n[written] {state_path}", file=sys.stderr)

    if args.selftest:
        ok = _selftest_assertions(results, state_path, cfg, fx)
        print(f"\n[selftest] {'ALL GREEN ✅' if ok else 'FAILED ❌'}", file=sys.stderr)
        return 0 if ok else 2

    # exit code mirrors severity so CI can gate on it if desired (0 unless RED)
    return 1 if overall == RED and cfg["aggregation"].get("fail_ci_on_red") else 0


def _selftest_assertions(results: list[ModuleResult], state_path: str,
                         cfg: dict, fx: dict) -> bool:
    """Fixture-level checks so `--selftest` fails loudly on regressions."""
    checks: list[tuple] = []
    by_mod = {_module_short(r.module): r for r in results}

    # M6: Lite-On(2301) leads 2308 by ~16pp in the power group → YELLOW, flagged.
    m6 = by_mod.get("M6")
    power = (m6.metrics.get("groups", {}).get("power", {}) if m6 and m6.metrics else {})
    checks.append(("M6 present", m6 is not None))
    checks.append(("M6 status YELLOW", bool(m6) and m6.status == YELLOW))
    checks.append(("M6 power peer-lead >= yellow", power.get("peer_lead_pp", 0) >= 15.0))
    checks.append(("M6 rack does not escalate",
                   (m6.metrics.get("groups", {}).get("rack", {}).get("status") if m6 and m6.metrics else None)
                   in (GREEN, NO_DATA, None)))

    # M7: 2308 +1%/day → t5 raw≈+5.1, t20 raw≈+22.02. Benchmark(0050) +0.5%/day
    # → t5 excess≈5.10−2.53=+2.57, t20 excess≈22.02−10.49=+11.53.
    try:
        with open(state_path, encoding="utf-8") as f:
            last = json.load(f)[-1]
        oc = last.get("outcomes", {})
        checks.append(("M7 outcomes written", bool(oc)))
        checks.append(("M7 t5 raw ~ +5.1%", oc.get("t5_ret_pct") is not None and abs(oc["t5_ret_pct"] - 5.10) < 0.2))
        checks.append(("M7 t20 raw ~ +22.0%", oc.get("t20_ret_pct") is not None and abs(oc["t20_ret_pct"] - 22.02) < 0.3))
        checks.append(("M7 t5 excess ~ +2.57%", oc.get("t5_excess_pct") is not None and abs(oc["t5_excess_pct"] - 2.57) < 0.2))
        checks.append(("M7 t20 excess ~ +11.5%", oc.get("t20_excess_pct") is not None and abs(oc["t20_excess_pct"] - 11.53) < 0.3))
        checks.append(("M7 records benchmark id", oc.get("benchmark") == "0050"))
    except Exception as e:
        checks.append((f"M7 state readable ({e})", False))

    # M5 (in pipeline, cold-start baseline → absolute): vr300 bucket dedups 4
    # near-dup delays to 1 event + a denial event, and the denial caps at YELLOW.
    m5 = by_mod.get("M5")
    sc = (m5.metrics.get("scoring", {}).get("vr300_delay", {}) if m5 and m5.metrics else {})
    checks.append(("M5 present", m5 is not None))
    checks.append(("M5 dedup: mentions > events", sc.get("mentions", 0) > sc.get("events", 0)))
    checks.append(("M5 denial detected", sc.get("denial") is True))
    checks.append(("M5 status capped at YELLOW", bool(m5) and m5.status == YELLOW))

    # M5 z-score path: a spike (events=2) vs a low baseline (mean~0.5) should
    # engage the z-score gate and escalate. Baseline needs non-zero variance.
    lowbase = [{"modules": [{"module": "M5 x", "metrics": {"events": {"vr300_delay": v}}}]}
               for v in (0, 1, 0, 1, 0, 1)]
    m5z = run_m5(cfg, fx["rss"], lowbase)
    zsc = m5z.metrics.get("scoring", {}).get("vr300_delay", {})
    checks.append(("M5 z-score gate engaged", zsc.get("gate") == "zscore"))
    checks.append(("M5 z-score escalates on spike", m5z.status in (YELLOW, RED)))

    # M8 cold start: down-heavy single run stays GREEN (awaits confirmation).
    m8 = by_mod.get("M8")
    checks.append(("M8 present", m8 is not None))
    checks.append(("M8 down_ratio ~0.75",
                   bool(m8) and m8.metrics.get("down_ratio") is not None
                   and abs(m8.metrics["down_ratio"] - 0.75) < 0.01))
    checks.append(("M8 cold-start not escalated", bool(m8) and m8.status == GREEN))

    # M8 consec gate: with a prior elevated run in history → YELLOW.
    prior = [{"modules": [{"module": "M8 revision_velocity", "metrics": {"down_ratio": 0.8}}]}]
    m8c = run_m8(cfg, fx["rss"], prior)
    checks.append(("M8 escalates on 2nd consecutive down-heavy run", m8c.status == YELLOW))

    ok = True
    for name, passed in checks:
        print(f"[selftest]   {'✓' if passed else '✗'} {name}", file=sys.stderr)
        ok = ok and passed
    return ok


if __name__ == "__main__":
    sys.exit(main())
