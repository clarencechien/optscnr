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

UA = "delta-radar/1.0 (+github.com/clarencechien/optscnr)"


def http_get_json(url: str, timeout: int = 30) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def http_get_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def yoy(cur: float, prev: float) -> Optional[float]:
    if prev in (None, 0) or cur is None:
        return None
    return (cur - prev) / abs(prev) * 100.0


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
    params = {
        "get": "GEN_VAL_MO,CTY_CODE,CTY_NAME",
        "I_COMMODITY": c["hs_code"],
        "COMM_LVL": "HS6",
        "time": f"from {start}",
    }
    key = os.environ.get("CENSUS_API_KEY", "")
    if key:
        params["key"] = key
    url = cfg["endpoints"]["census"] + "?" + urllib.parse.urlencode(params)
    rows = http_get_json(url)  # first row is header
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

def _pick_account(rows: list[dict], patterns: list[str]) -> dict[str, float]:
    """FinMind statements come as long-format rows {'date','type','value'}.
    Account naming drifts between schema versions, so match by regex list."""
    out: dict[str, float] = {}
    pats = [re.compile(p, re.I) for p in patterns]
    for r in rows:
        t = str(r.get("type", ""))
        if any(p.search(t) for p in pats):
            out[r["date"]] = out.get(r["date"], 0.0) + float(r["value"])
    return out


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

    contract = _pick_account(bs, p["account_patterns"]["contract_liabilities"])
    inventory = _pick_account(bs, p["account_patterns"]["inventory"])
    ocf = _pick_account(cf, p["account_patterns"]["operating_cash_flow"])
    capex = _pick_account(cf, p["account_patterns"]["capex"])
    ni = _pick_account(inc, p["account_patterns"]["net_income"]) if inc else {}

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

    contract_qoq = yoy(c_now, c_prev) if c_prev else None  # reuse pct fn for QoQ
    inv_qoq = yoy(inv_now, inv_prev) if inv_prev else None

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
    }
    got_any = any(v is not None for k, v in res.metrics.items() if k != "as_of")
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
    rows = fetch(cfg, p["months_back"])
    if not rows:
        res.error = "empty Census response"
        return res
    monthly: dict[str, float] = {}
    for r in rows:
        monthly[r["time"]] = monthly.get(r["time"], 0.0) + r["value"]
    months = sorted(monthly)
    w = p["rolling_window_months"]
    if len(months) < 12 + w:
        res.error = f"only {len(months)} months — need {12 + w} for rolling YoY"
        return res
    cur = sum(monthly[m] for m in months[-w:])
    prv = sum(monthly[m] for m in months[-w - 12:-12])
    roll_yoy = yoy(cur, prv)
    res.metrics = {
        "window": f"{months[-w]}..{months[-1]}",
        "rolling_value_usd_m": round(cur / 1e6, 1),
        "rolling_yoy_pct": round(roll_yoy, 1) if roll_yoy is not None else None,
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

def run_m5(cfg: dict, fetch: Callable) -> ModuleResult:
    res = ModuleResult("M5 narrative_triggers")
    p = cfg["m5_narrative_triggers"]
    hits: dict[str, list[str]] = {b: [] for b in p["buckets"]}
    fetched_any = False
    for bucket, spec in p["buckets"].items():
        url = cfg["endpoints"]["gnews_rss"].format(
            query=urllib.parse.quote(spec["query"]))
        try:
            items = fetch(url)
            fetched_any = True
        except Exception as e:  # network per-feed failure shouldn't kill module
            res.notes.append(f"feed {bucket} failed: {e}")
            continue
        kw = [k.lower() for k in spec["keywords"]]
        for it in items[: p["max_items_per_feed"]]:
            text = (it["title"] + " " + it["summary"]).lower()
            if any(k in text for k in kw):
                hits[bucket].append(it["title"][:120])
    if not fetched_any:
        res.error = "all RSS feeds failed"
        return res
    counts = {b: len(v) for b, v in hits.items()}
    res.metrics = {"hits": counts}
    res.notes += [f"[{b}] {t}" for b, v in hits.items() for t in v[:3]]
    worst = GREEN
    for bucket, spec in p["buckets"].items():
        n = counts[bucket]
        if n >= spec["red_hits"]:
            worst = RED
        elif n >= spec["yellow_hits"] and SEVERITY[worst] < SEVERITY[YELLOW]:
            worst = YELLOW
    res.status = worst
    res.headline = " / ".join(f"{b}:{counts[b]}" for b in counts)
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


def render_report(results: list[ModuleResult], overall: str, cfg: dict) -> str:
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Delta Radar (2308.TW) — {now}",
        "",
        f"## 總判定：{EMOJI[overall]} {overall}",
        "",
        "GS 4500 劇本三大未驗證前提的機械化監控：FCF 轉回 (M2)、合約負債續航 (M2)、",
        "實體出貨上船 (M3/M4)，外加營收動能 (M1) 與敘事風險 (M5)。",
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
    lines.append("---")
    lines.append("*delta_radar — optscnr radar family. Shadow-mode instrument: "
                 "this is a measurement device, not a trade signal.*")
    return "\n".join(lines)


def append_state(results: list[ModuleResult], overall: str, path: str) -> None:
    entry = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        "overall": overall,
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
# Selftest fixtures (zero-network full pipeline)
# ----------------------------------------------------------------------------

def _fixtures() -> dict:
    def finmind_fake(dataset, data_id, start_date, cfg):
        if dataset == "TaiwanStockMonthRevenue":
            rows = []
            base = 40_000_000_000
            for i in range(30):
                y, m = divmod((2024 * 12 + 0) + i, 12)
                growth = 1.025 ** i  # compounding => accelerating YoY (healthy baseline)
                rows.append({"revenue_year": y, "revenue_month": m + 1,
                             "revenue": base * growth, "date": f"{y}-{m+1:02d}-10"})
            return rows
        if dataset == "TaiwanStockBalanceSheet":
            return [
                {"date": "2025-12-31", "type": "ContractLiabilitiesCurrent", "value": 30e9},
                {"date": "2026-03-31", "type": "ContractLiabilitiesCurrent", "value": 36e9},
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
    ap.add_argument("--modules", default="m1,m2,m3,m4,m5",
                    help="comma list, e.g. m1,m4")
    ap.add_argument("--selftest", action="store_true",
                    help="run full pipeline on bundled fixtures (no network)")
    ap.add_argument("--dump-accounts", action="store_true",
                    help="print distinct FinMind balance-sheet account names and exit")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    out_dir = args.output_dir or cfg.get("output_dir", "output")
    os.makedirs(out_dir, exist_ok=True)

    fx = _fixtures() if args.selftest else {
        "finmind": finmind_fetch, "quarterlies": yfinance_quarterlies,
        "census": census_fetch, "rss": rss_fetch,
    }

    if args.dump_accounts:
        rows = fx["finmind"]("TaiwanStockBalanceSheet", cfg["ticker_tw"],
                             (dt.date.today() - dt.timedelta(days=400)).isoformat(), cfg)
        for t in sorted({r.get("type", "") for r in rows}):
            print(t)
        return 0

    wanted = {m.strip().lower() for m in args.modules.split(",")}
    runners = {
        "m1": lambda: run_m1(cfg, fx["finmind"]),
        "m2": lambda: run_m2(cfg, fx["finmind"]),
        "m3": lambda: run_m3(cfg, fx["quarterlies"]),
        "m4": lambda: run_m4(cfg, fx["census"]),
        "m5": lambda: run_m5(cfg, fx["rss"]),
    }
    results: list[ModuleResult] = []
    for key in ("m1", "m2", "m3", "m4", "m5"):
        if key not in wanted:
            continue
        try:
            results.append(runners[key]())
        except Exception as e:  # absolute backstop — never crash the radar
            r = ModuleResult(f"{key.upper()} (crashed)")
            r.error = f"{type(e).__name__}: {e}"
            if os.environ.get("DELTA_RADAR_DEBUG"):
                traceback.print_exc()
            results.append(r)

    overall = aggregate(results, cfg)
    report = render_report(results, overall, cfg)
    report_path = os.path.join(out_dir, "delta_radar_report.md")
    state_path = os.path.join(out_dir, "delta_radar_state.json")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    append_state(results, overall, state_path)
    print(report)
    print(f"\n[written] {report_path}\n[written] {state_path}", file=sys.stderr)
    # exit code mirrors severity so CI can gate on it if desired (0 unless RED)
    return 1 if overall == RED and cfg["aggregation"].get("fail_ci_on_red") else 0


if __name__ == "__main__":
    sys.exit(main())
