#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dca_ledger.py — DCA 規則影子帳本（tw_scanner 家族）
=====================================================
回答一個問題：**tw_scanner 的訊號，對「定期定額買 0050 的人」值多少？**
單位是你的錢（平均成本、每萬元買到幾單位、XIRR），不是 TAIEX 20 日中位數。

五條規則同時跑、只記錄不建議（等額假設；不記真實部位、不記損益）：
  plain               每月固定日買固定金額
  weekly_gate         每週檢查、月預算：本週有投降警報且本月未動 → 翌日投入 m×amount，
                      當月不再行動；到當月最後決策週仍未動 → 翌日投入 amount（同一筆月預算，
                      只是換時點；加碼部分是額外資金）
  capitulation_boost  plain ＋ 投降警報翌日加買 (m−1)×amount（額外資金）
  regime_scaled       plain × 鋒面倍數（假說，預期無效，放進來給資料處決）
  lump_sum            對照：plain 總投入第一天一次投入（DCA 的機會成本）

資料源：
  tw_scanner_history.json  全序列 regime / alerts（tw_scanner.py 每次簡報導出）
  dca_prices.json          0050 收盤快取（FinMind TaiwanStockPrice；增量、進版控）

House rules：閾值外部化；抓不到就用快取、快取也沒就 NO_DATA 不猜；--selftest 零網路。
Usage:
  python dca_ledger.py                      # 更新價格快取 → 重算帳本 → 寫 md + json
  python dca_ledger.py --no-fetch           # 只用快取（離線）
  python dca_ledger.py --selftest           # 合成資料，寫到臨時目錄
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import sys
import tempfile
from typing import Optional

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


# ----------------------------------------------------------------------------
# 價格快取（增量、冪等）
# ----------------------------------------------------------------------------

def load_prices(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        d = json.load(open(path, encoding="utf-8"))
        return {k: float(v) for k, v in (d.get("closes") or {}).items()}
    except Exception:
        return {}


def save_prices(path: str, instrument: str, closes: dict) -> None:
    json.dump({"instrument": instrument,
               "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "n": len(closes), "closes": dict(sorted(closes.items()))},
              open(path, "w", encoding="utf-8"), ensure_ascii=False)


def fetch_prices_finmind(cfg: dict, start: str) -> dict:
    """FinMind TaiwanStockPrice → {date: close}。失敗丟例外，呼叫端決定降級。"""
    from tw_scanner import finmind  # 同資料夾；endpoints 借 tw_scanner_config
    tw_cfg = json.load(open(os.path.join(HERE, "config", "tw_scanner_config.json"),
                            encoding="utf-8"))
    df = finmind(cfg["prices"]["dataset"], tw_cfg, data_id=cfg["instrument"], start=start)
    c_date = "date"
    c_close = "close" if "close" in df.columns else "Close"
    out = {}
    for d, c in zip(df[c_date], df[c_close]):
        try:
            out[str(d)[:10]] = float(c)
        except (TypeError, ValueError):
            continue
    return out


def update_prices(cfg: dict, path: str, fetch: bool) -> tuple[dict, Optional[str]]:
    """回 (closes, warning)。有網路：從快取尾巴前 N 天增量抓；沒有：快取原樣。"""
    closes = load_prices(path)
    if not fetch:
        return closes, None if closes else "no cache and --no-fetch"
    if closes:
        tail = (dt.date.fromisoformat(max(closes)) -
                dt.timedelta(days=cfg["prices"].get("refetch_tail_days", 7))).isoformat()
    else:
        tail = cfg["history_start"]
    try:
        fresh = fetch_prices_finmind(cfg, tail)
    except Exception as e:
        return closes, f"price fetch failed ({type(e).__name__}: {e}); cache only"
    closes.update(fresh)
    save_prices(path, cfg["instrument"], closes)
    return closes, None


# ----------------------------------------------------------------------------
# 帳本核心（純函數）
# ----------------------------------------------------------------------------

def _next_trading_on_or_after(dates: list[str], target: str) -> Optional[str]:
    i = _bisect_left(dates, target)
    return dates[i] if i < len(dates) else None


def _bisect_left(a: list, x) -> int:
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def schedule_dates(dates: list[str], start: str, end: str, day: int, period: str) -> list[str]:
    """每期買日：每月 `day` 日（含）之後第一個交易日。biweekly = 每月 day 與 day+14。"""
    out = []
    y, m = int(start[:4]), int(start[5:7])
    end_d = dt.date.fromisoformat(end)
    while dt.date(y, m, 1) <= end_d:
        anchors = [day] if period == "monthly" else [day, day + 14]
        for a in anchors:
            a = min(a, 28)
            t = _next_trading_on_or_after(dates, f"{y:04d}-{m:02d}-{a:02d}")
            if t and t <= end and t >= start and (not out or t > out[-1]):
                out.append(t)
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def fee_of(amount: float, fees: dict) -> float:
    f = amount * fees["fee_rate"] * fees.get("fee_discount", 1.0)
    return max(f, fees.get("min_fee_twd", 0.0))


def alert_episodes(history_rows: list[dict], name: str, gap: int) -> list[str]:
    """警報日 → 事件簇首日（同 tw_scanner backtest 的去簇：交易日間隔 > gap 才算新簇）。"""
    days = [i for i, r in enumerate(history_rows) if name in (r.get("alerts") or [])]
    eps = []
    for i in days:
        if not eps or (i - eps[-1]) > gap:
            eps.append(i)
    return [history_rows[i]["date"] for i in eps]


def decision_days(dates: list[str], start: str, end: str, weekday: int) -> list[str]:
    """每週決策日：該週 `weekday`（0=一）當天或之前最後一個交易日（週五休市就用週四）。"""
    out = []
    d = dt.date.fromisoformat(start)
    d += dt.timedelta(days=(weekday - d.weekday()) % 7)
    end_d = dt.date.fromisoformat(end)
    while d <= end_d:
        i = _bisect_left(dates, d.isoformat())
        if i < len(dates) and dates[i] == d.isoformat():
            t = dates[i]
        elif i > 0:
            t = dates[i - 1]
        else:
            t = None
        if t and t >= start and (not out or t > out[-1]):
            out.append(t)
        d += dt.timedelta(days=7)
    return out


def weekly_gate_plan(cfg: dict, dates: list[str], history_rows: list[dict],
                     start: str, end: str) -> list[dict]:
    """週檢查・月預算規則 → [{decision_date, exec_date, mult, reason, alert_dates}]。

    每個決策日 d（週末看資料）：本月預算已動 → 略過；
    本週（上個決策日之後到 d）有投降警報 → 下一交易日投入 multiplier×amount，當月不再行動；
    否則若 d 是當月最後一個決策日 → 下一交易日投入 amount（純例行）。
    執行日跨到下個月也算「決策當月」的預算。
    """
    r = cfg["rules"]["weekly_gate"]
    dd = decision_days(dates, start, end, int(r.get("decision_weekday", 4)))
    alert_dates = [row["date"] for row in history_rows if "capitulation" in (row.get("alerts") or [])]
    plan, spent = [], set()
    prev = None
    for k, d in enumerate(dd):
        month = d[:7]
        last_of_month = (k + 1 == len(dd)) or dd[k + 1][:7] != month
        i = _bisect_left(dates, d)
        j = i + 1 if i < len(dates) and dates[i] == d else i
        exec_date = dates[j] if j < len(dates) and dates[j] <= end else None
        if month in spent or exec_date is None:
            prev = d
            continue
        week_alerts = [a for a in alert_dates if (prev is None or a > prev) and a <= d]
        if week_alerts:
            plan.append({"decision_date": d, "exec_date": exec_date, "mult": float(r["multiplier"]),
                         "reason": "alert", "alert_dates": week_alerts})
            spent.add(month)
        elif last_of_month:
            plan.append({"decision_date": d, "exec_date": exec_date, "mult": 1.0,
                         "reason": "month_end", "alert_dates": []})
            spent.add(month)
        prev = d
    return plan


def regime_at(history_rows: list[dict], date: str) -> str:
    """買日的鋒面：history 裡 ≤ date 的最後一筆（買日必是交易日，通常剛好命中）。"""
    best = "UNCALIBRATED"
    for r in history_rows:
        if r["date"] <= date:
            best = r.get("regime") or best
        else:
            break
    return best


def xirr(cashflows: list[tuple[str, float]]) -> Optional[float]:
    """年化內部報酬率（bisection）。cashflows [(date, amount)]，投入為負、期末市值為正。"""
    if len(cashflows) < 2:
        return None
    t0 = dt.date.fromisoformat(cashflows[0][0])
    ts = [((dt.date.fromisoformat(d) - t0).days / 365.0, a) for d, a in cashflows]

    def npv(r):
        return sum(a / ((1 + r) ** t) for t, a in ts)
    lo, hi = -0.99, 10.0
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < 1e-6:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


def run_rule(name: str, cfg: dict, dates: list[str], closes: dict,
             history_rows: list[dict], start: str, end: str) -> dict:
    """單一規則 → {contributions, summary}。contributions: [{date, amount, fee, price, units, kind}]。"""
    rules, fees = cfg["rules"], cfg["fees"]
    amount = float(cfg["amount_twd"])
    sched = schedule_dates(dates, start, end, cfg["buy_day_of_month"], cfg.get("period", "monthly"))
    contribs: list[dict] = []

    def buy(date: str, amt: float, kind: str, extra: Optional[dict] = None):
        px = closes[date]
        f = fee_of(amt, fees)
        units = (amt - f) / px
        contribs.append({"date": date, "amount": round(amt, 2), "fee": round(f, 2),
                         "price": px, "units": units, "kind": kind, **(extra or {})})

    if name == "plain":
        for d in sched:
            buy(d, amount, "regular")
    elif name == "capitulation_boost":
        r = rules["capitulation_boost"]
        for d in sched:
            buy(d, amount, "regular")
        for ep in alert_episodes(history_rows, "capitulation", r.get("episode_gap_sessions", 5)):
            if ep < start or ep > end:
                continue
            i = _bisect_left(dates, ep)
            # 警報收盤後才知道 → 下一個交易日收盤執行
            j = i + 1 if i < len(dates) and dates[i] == ep else i
            if j >= len(dates) or dates[j] > end:
                continue
            buy(dates[j], amount * (r["multiplier"] - 1.0), "boost", {"alert_date": ep})
    elif name == "weekly_gate":
        for p in weekly_gate_plan(cfg, dates, history_rows, start, end):
            buy(p["exec_date"], amount * p["mult"], "boost" if p["reason"] == "alert" else "regular",
                {"decision_date": p["decision_date"], "reason": p["reason"],
                 "alert_date": (p["alert_dates"][-1] if p["alert_dates"] else None)})
    elif name == "regime_scaled":
        mult = rules["regime_scaled"]["multipliers"]
        for d in sched:
            reg = regime_at(history_rows, d)
            buy(d, amount * float(mult.get(reg, 1.0)), "regular", {"regime": reg})
    elif name == "lump_sum":
        if sched:
            buy(sched[0], amount * len(sched), "lump")
    else:
        raise ValueError(name)
    return {"contributions": contribs, "summary": summarize(contribs, dates, closes, end)}


def summarize(contribs: list[dict], dates: list[str], closes: dict, end: str) -> dict:
    if not contribs:
        return {"n_buys": 0, "invested": 0.0, "units": 0.0, "avg_cost": None,
                "final_value": None, "return_pct": None, "xirr_pct": None}
    invested = sum(c["amount"] for c in contribs)
    units = sum(c["units"] for c in contribs)
    last_date = dates[_bisect_left(dates, end) - 1] if _bisect_left(dates, end) < len(dates) and dates[_bisect_left(dates, end)] != end else end
    last_px = closes[last_date]
    value = units * last_px
    cfs = [(c["date"], -c["amount"]) for c in contribs] + [(last_date, value)]
    r = xirr(sorted(cfs))
    return {"n_buys": len(contribs), "invested": round(invested, 0),
            "units": round(units, 4), "avg_cost": round(invested / units, 2),
            "final_value": round(value, 0),
            "return_pct": round((value / invested - 1) * 100, 2),
            "xirr_pct": None if r is None else round(r * 100, 2),
            "as_of": last_date, "last_price": last_px}


def evaluate_boosts(contribs: list[dict], dates: list[str], closes: dict,
                    sched: list[str], fwd: int) -> list[dict]:
    """每筆加碼：跟「同一筆錢等到下一個例行買日」比（edge），與 T+fwd 交易日報酬。"""
    out = []
    for c in contribs:
        if c["kind"] != "boost":
            continue
        nxt = next((d for d in sched if d > c["date"]), None)
        i = _bisect_left(dates, c["date"])
        t_fwd = dates[i + fwd] if i + fwd < len(dates) else None
        out.append({
            "alert_date": c.get("alert_date"), "exec_date": c["date"], "price": c["price"],
            "amount": c["amount"],
            "next_regular_date": nxt, "next_regular_price": closes.get(nxt) if nxt else None,
            "edge_vs_next_regular_pct": (round((closes[nxt] / c["price"] - 1) * 100, 2)
                                         if nxt else None),
            f"t{fwd}_pct": (round((closes[t_fwd] / c["price"] - 1) * 100, 2) if t_fwd else None),
        })
    return out


def current_period(cfg: dict, dates: list[str], closes: dict, history_rows: list[dict]) -> dict:
    """本期機械指示（給週報）：下一個例行買日、目前鋒面倍數、近 5 個交易日有無投降警報。"""
    today = dates[-1]
    y, m = int(today[:4]), int(today[5:7])
    day = cfg["buy_day_of_month"]
    this = _next_trading_on_or_after(dates, f"{y:04d}-{m:02d}-{day:02d}")
    if this is None or this < today:
        m2, y2 = (m + 1, y) if m < 12 else (1, y + 1)
        nxt_target = f"{y2:04d}-{m2:02d}-{day:02d}"
        nxt = _next_trading_on_or_after(dates, nxt_target) or nxt_target
        done_this_month = this is not None and this < today
    else:
        nxt, done_this_month = this, False
    reg = regime_at(history_rows, today)
    mult = cfg["rules"]["regime_scaled"]["multipliers"].get(reg, 1.0)
    recent = history_rows[-5:]
    alert_days = [r["date"] for r in recent if "capitulation" in (r.get("alerts") or [])]
    amt = float(cfg["amount_twd"])
    return {
        "as_of": today, "last_price": closes[today], "regime": reg,
        "next_regular_buy": nxt, "this_month_bought": done_this_month,
        "plain_amount": amt,
        "boost_pending": bool(alert_days),
        "boost_amount": amt * (cfg["rules"]["capitulation_boost"]["multiplier"] - 1.0),
        "recent_alert_days": alert_days,
        "regime_multiplier": mult, "regime_amount": amt * mult,
    }


def weekly_gate_status(cfg: dict, dates: list[str], history_rows: list[dict],
                       contribs: list[dict]) -> dict:
    """本週的週檢查指示：本月動了沒、本週有沒有警報、這週是不是當月最後決策週。"""
    r = cfg["rules"]["weekly_gate"]
    today = dates[-1]
    month = today[:7]
    spent = [c for c in contribs if c.get("decision_date", "")[:7] == month]
    wd = int(r.get("decision_weekday", 4))
    t = dt.date.fromisoformat(today)
    this_dec = t + dt.timedelta(days=(wd - t.weekday()) % 7)      # 本週決策日（含今天）
    prev_dec = this_dec - dt.timedelta(days=7)
    week_alerts = [row["date"] for row in history_rows
                   if "capitulation" in (row.get("alerts") or [])
                   and prev_dec.isoformat() < row["date"] <= today]
    next_dec = this_dec + dt.timedelta(days=7)
    last_week_of_month = next_dec.strftime("%Y-%m") != this_dec.strftime("%Y-%m")
    amt = float(cfg["amount_twd"])
    if spent:
        c = spent[-1]
        action, amount = "none", 0.0
        text = f"本月預算已於 {c['date']} 動用（{'投降窗 ×' + str(r['multiplier']) if c['kind']=='boost' else '月末例行'}），本月不再行動"
    elif week_alerts:
        action, amount = "buy_boost", amt * float(r["multiplier"])
        text = f"本週有投降警報（{'、'.join(week_alerts)}）→ 下一交易日投入 {amount:,.0f} 元，當月不再行動"
    elif last_week_of_month:
        action, amount = "buy_plain", amt
        text = f"本週是當月最後決策週且預算未動 → 下一交易日投入 {amount:,.0f} 元"
    else:
        action, amount = "wait", 0.0
        text = f"本週無警報、預算未動 → 等（{next_dec.isoformat()} 再看）"
    return {"decision_date": this_dec.isoformat(), "month": month, "month_spent": bool(spent),
            "week_alert_days": week_alerts, "last_week_of_month": last_week_of_month,
            "action": action, "amount": amount, "text": text}


def build_ledger(cfg: dict, closes: dict, history: dict) -> dict:
    dates = sorted(d for d in closes if d >= cfg["history_start"])
    rows = sorted((history.get("rows") or []), key=lambda r: r["date"])
    if not dates:
        return {"status": "NO_DATA", "reason": "no prices"}
    if not rows:
        return {"status": "NO_DATA", "reason": "no tw_scanner history"}
    end = dates[-1]
    windows = {}
    for wname, months in cfg.get("windows", {"full": None}).items():
        if wname.startswith("_"):
            continue
        if months is None:
            start = max(cfg["history_start"], dates[0])
        else:
            e = dt.date.fromisoformat(end)
            y, m = e.year, e.month - int(months)
            while m <= 0:
                y, m = y - 1, m + 12
            start = _next_trading_on_or_after(dates, f"{y:04d}-{m:02d}-{e.day:02d}") or dates[0]
        rules_out = {}
        for name, rc in cfg["rules"].items():
            if name.startswith("_") or not rc.get("enabled", True):
                continue
            rules_out[name] = run_rule(name, cfg, dates, closes, rows, start, end)
        sched = schedule_dates(dates, start, end, cfg["buy_day_of_month"], cfg.get("period", "monthly"))
        boosts = (evaluate_boosts(rules_out["capitulation_boost"]["contributions"], dates, closes,
                                  sched, cfg["boost_eval"]["forward_sessions"])
                  if "capitulation_boost" in rules_out else [])
        gate_boosts = (evaluate_boosts(rules_out["weekly_gate"]["contributions"], dates, closes,
                                       sched, cfg["boost_eval"]["forward_sessions"])
                       if "weekly_gate" in rules_out else [])
        plain = rules_out.get("plain", {}).get("summary") or {}
        comp = {}
        for name, r in rules_out.items():
            s = r["summary"]
            comp[name] = {**s, "label": cfg["rules"][name].get("label", name),
                          "avg_cost_vs_plain_pct": (round((s["avg_cost"] / plain["avg_cost"] - 1) * 100, 2)
                                                    if s.get("avg_cost") and plain.get("avg_cost") else None),
                          "n_boosts": sum(1 for c in r["contributions"] if c["kind"] == "boost")}
        windows[wname] = {"start": start, "end": end, "n_periods": len(sched),
                          "rules": comp, "boosts": boosts, "gate_boosts": gate_boosts}
    current = current_period(cfg, dates, closes, rows)
    if "weekly_gate" in (windows.get("full") or {}).get("rules", {}):
        full_contribs = run_rule("weekly_gate", cfg, dates, closes, rows,
                                 windows["full"]["start"], end)["contributions"]
        current["weekly_gate"] = weekly_gate_status(cfg, dates, rows, full_contribs)
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "status": "OK", "instrument": cfg["instrument"], "amount_twd": cfg["amount_twd"],
        "period": cfg.get("period", "monthly"), "buy_day_of_month": cfg["buy_day_of_month"],
        "prices_from": dates[0], "prices_to": end, "history_rows": len(rows),
        "history_from": rows[0]["date"], "history_to": rows[-1]["date"],
        "current": current,
        "windows": windows,
        "note": "規則影子帳本：等額假設、不記真實部位。lump_sum 是對照不是策略；regime_scaled 是待處決的假說。非投資建議。",
    }


# ----------------------------------------------------------------------------
# 報告
# ----------------------------------------------------------------------------

def _f(x, unit="", digits=2, signed=False):
    if x is None:
        return "—"
    s = f"{x:+,.{digits}f}" if signed else f"{x:,.{digits}f}"
    return s + unit


def render_md(led: dict, cfg: dict) -> str:
    if led.get("status") != "OK":
        return (f"# 💰 DCA 規則影子帳本（{cfg['instrument']}）\n\n"
                f"NO_DATA：{led.get('reason')}。\n")
    cur = led["current"]
    L = [f"# 💰 DCA 規則影子帳本（{led['instrument']}）— 至 {led['prices_to']}", "",
         f"每月 {led['buy_day_of_month']} 日後首個交易日買 {led['amount_twd']:,} 元；價格 {led['prices_from']} 起、"
         f"鋒面/警報序列 {led['history_from']} 起（{led['history_rows']} 日）。等額假設、不記真實部位。", "",
         "## 本期（機械指示，不是建議）", "",
         f"- 下一個例行買日：**{cur['next_regular_buy']}**"
         f"{'（本月已買）' if cur['this_month_bought'] else ''} · 純定期定額 {cur['plain_amount']:,.0f} 元",
         f"- 投降窗加碼：{'**待執行** ' + str(cur['boost_amount']) + ' 元（警報日 ' + '、'.join(cur['recent_alert_days']) + '）' if cur['boost_pending'] else '無（近 5 個交易日無警報）'}",
         f"- 鋒面 {cur['regime']} → 調節規則本期 ×{cur['regime_multiplier']:g} = {cur['regime_amount']:,.0f} 元（假說，待處決）",
         ]
    wg = cur.get("weekly_gate")
    if wg:
        L.append(f"- **週檢查・月預算**（決策日 {wg['decision_date']}）：{wg['text']}")
    L.append("")
    for wname, w in led["windows"].items():
        L += [f"## 視窗：{wname}（{w['start']} → {w['end']}，{w['n_periods']} 期）", "",
              "| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |",
              "|---|---|---|---|---|---|---|---|---|"]
        for name, s in w["rules"].items():
            L.append(f"| {s['label']} | {s['n_buys']} | {_f(s['invested'], digits=0)} | {_f(s['units'], digits=2)} "
                     f"| {_f(s['avg_cost'])} | {_f(s['avg_cost_vs_plain_pct'], '%', signed=True)} "
                     f"| {_f(s['final_value'], digits=0)} | {_f(s['return_pct'], '%', signed=True)} "
                     f"| {_f(s['xirr_pct'], '%', signed=True)} |")
        L.append("")
        if w["boosts"]:
            fwd = cfg["boost_eval"]["forward_sessions"]
            L += [f"加碼逐筆（跟「同一筆錢等到下一個例行買日」比；T+{fwd} 交易日）：", "",
                  f"| 警報日 | 執行日 | 執行價 | 下一例行買日 | 例行價 | edge | T+{fwd} |", "|---|---|---|---|---|---|---|"]
            for b in w["boosts"]:
                L.append(f"| {b['alert_date']} | {b['exec_date']} | {b['price']} | {b['next_regular_date'] or '—'} "
                         f"| {_f(b['next_regular_price'])} | {_f(b['edge_vs_next_regular_pct'], '%', signed=True)} "
                         f"| {_f(b[f't{fwd}_pct'], '%', signed=True)} |")
            edges = [b["edge_vs_next_regular_pct"] for b in w["boosts"] if b["edge_vs_next_regular_pct"] is not None]
            if edges:
                L.append("")
                L.append(f"加碼 edge 平均 {sum(edges)/len(edges):+.2f}%、勝率 {100*sum(e>0 for e in edges)/len(edges):.0f}%（n={len(edges)}）"
                         "。正 = 警報日買比等到例行日買便宜。")
            L.append("")
        else:
            L += ["此視窗內無投降警報，加碼規則 = 純定期定額。", ""]
    L += ["---", "*dca_ledger — 規則影子帳本，等額假設。lump_sum 是對照不是策略（沒人一開始就有全部的錢）；"
          "regime_scaled 是待資料處決的假說。非投資建議。*"]
    return "\n".join(L)


# ----------------------------------------------------------------------------
# selftest（零網路）
# ----------------------------------------------------------------------------

def _synthetic(seed: int = 3) -> tuple[dict, dict]:
    import random
    rnd = random.Random(seed)
    closes, rows = {}, []
    d, px = dt.date(2019, 1, 2), 80.0
    i = 0
    while d <= dt.date(2026, 9, 11):
        if d.weekday() < 5:
            px *= math.exp(rnd.gauss(0.0004, 0.012))
            ds = d.isoformat()
            closes[ds] = round(px, 2)
            alerts = ["capitulation"] if i in (300, 301, 302, 900, 1500) else []
            reg = "CAPITULATION" if 295 <= i <= 310 else ("DE_RISK" if i % 40 < 10 else "NEUTRAL")
            rows.append({"date": ds, "regime": reg, "score": 0.0, "alerts": alerts, "pcts": {}})
            i += 1
        d += dt.timedelta(days=1)
    return closes, {"rows": rows}


def led_full_contribs(cfg, closes, hist):
    dates = sorted(d for d in closes if d >= cfg["history_start"])
    rows = sorted(hist["rows"], key=lambda r: r["date"])
    return run_rule("weekly_gate", cfg, dates, closes, rows, dates[0], dates[-1])["contributions"]


def selftest(cfg: dict, out_dir: str) -> bool:
    closes, hist = _synthetic()
    led = build_ledger(cfg, closes, hist)
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg, file=sys.stderr)
        ok = ok and bool(cond)

    full = led["windows"]["full"]
    r = full["rules"]
    check(led["status"] == "OK", "ledger built")
    check(r["plain"]["n_buys"] == full["n_periods"] > 80, f"plain 每期一買（{r['plain']['n_buys']} 期）")
    check(r["capitulation_boost"]["n_boosts"] == 3, f"投降簇去簇後 3 次加碼（實得 {r['capitulation_boost']['n_boosts']}）")
    check(abs(r["lump_sum"]["invested"] - r["plain"]["invested"]) < 1, "lump_sum 投入 = plain 投入")
    check(r["capitulation_boost"]["invested"] > r["plain"]["invested"], "加碼是額外資金")
    check(all(s["xirr_pct"] is not None for s in r.values()), "XIRR 全部可解")
    check(len(full["boosts"]) == 3 and all(b["exec_date"] > b["alert_date"] for b in full["boosts"]),
          "加碼在警報翌日執行")
    wg = r["weekly_gate"]
    months = {c["decision_date"][:7] for c in led_full_contribs(cfg, closes, hist)}
    check(wg["n_buys"] == len(months) and wg["n_buys"] >= 90, f"週檢查規則每月恰一次（{wg['n_buys']} 月）")
    check(wg["n_boosts"] == 3, f"週檢查規則 3 個警報月投入 ×2（實得 {wg['n_boosts']}）")
    check(led["current"]["weekly_gate"]["action"] in ("wait", "buy_plain", "buy_boost", "none"), "本週指示有效")
    check(led["windows"]["last_12m"]["n_periods"] in (12, 13), "近 12 月視窗 12–13 期")
    check(led["current"]["next_regular_buy"] >= led["current"]["as_of"], "本期指示：下一買日在今天之後")
    md = render_md(led, cfg)
    open(os.path.join(out_dir, "dca_ledger.md"), "w", encoding="utf-8").write(md)
    json.dump(led, open(os.path.join(out_dir, "dca_ledger.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    check("本期" in md and "加碼逐筆" in md, "報告含本期指示與加碼逐筆")
    # NO_DATA 路徑
    nd = build_ledger(cfg, {}, hist)
    check(nd["status"] == "NO_DATA" and "NO_DATA" in render_md(nd, cfg), "無價格 → NO_DATA 不崩潰")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="DCA 規則影子帳本")
    ap.add_argument("--config", default=os.path.join(HERE, "config", "dca_ledger_config.json"))
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--no-fetch", action="store_true", help="不連 FinMind，只用價格快取")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    cfg = json.load(open(args.config, encoding="utf-8"))
    out_dir = args.output_dir or os.path.join(HERE, "output")
    if args.selftest:
        out_dir = tempfile.mkdtemp(prefix="dca_ledger_selftest_")
        ok = selftest(cfg, out_dir)
        print(f"\n[selftest] {'ALL GREEN ✅' if ok else 'FAILED ❌'} ({out_dir})", file=sys.stderr)
        return 0 if ok else 2
    os.makedirs(out_dir, exist_ok=True)

    closes, warn = update_prices(cfg, os.path.join(out_dir, cfg["prices"]["cache"]),
                                 fetch=not args.no_fetch)
    if warn:
        print(f"[warn] {warn}", file=sys.stderr)
    hist_path = os.path.join(out_dir, "tw_scanner_history.json")
    history = json.load(open(hist_path, encoding="utf-8")) if os.path.exists(hist_path) else {}
    if not history:
        # 過渡：history 尚未導出時退用 state.json（只有 2026-06-11 起）
        sp = os.path.join(out_dir, "tw_scanner_state.json")
        if os.path.exists(sp):
            history = {"rows": json.load(open(sp, encoding="utf-8"))}
            print("[warn] tw_scanner_history.json 缺，退用 state.json（2026-06-11 起）", file=sys.stderr)

    led = build_ledger(cfg, closes, history)
    md = render_md(led, cfg)
    open(os.path.join(out_dir, "dca_ledger.md"), "w", encoding="utf-8").write(md)
    json.dump(led, open(os.path.join(out_dir, "dca_ledger.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(md)
    print(f"\n[written] {out_dir}/dca_ledger.md, dca_ledger.json", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
