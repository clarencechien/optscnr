#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tw_brief.py — 台股週報組裝器（tw_scanner + dca_ledger + delta_radar → 一頁）
==========================================================================
定位：DCA 0050 的人一週看一次的一頁。**週報不是日報**——鋒面以週翻轉、月營收每月 10 日、
0050 除息一年兩次、投降警報一年幾次；日報只在警報響時有內容。

零網路、零計算：只讀 output/ 裡各雷達已產出的檔，組成
  output/tw_brief.json   機器可讀（Cloudflare Worker /api/tw 讀這份）
  output/tw_weekly.md    人讀（build_readme.py 放在 tw_scanner/README.md 最上面）

缺哪份輸出就標 NO_DATA，不報錯（三支雷達各自排程，先跑的不該等後跑的）。
Usage:
  python tw_brief.py [--output-dir tw_scanner/output]
  python tw_brief.py --selftest
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_EMOJI = {"CAPITULATION": "🥶", "DE_RISK": "🌧️", "NEUTRAL": "⛅",
               "RISK_ON": "☀️", "OVERHEAT": "🔥", "UNCALIBRATED": "❔"}
LIGHT = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴", "NO_DATA": "⚪"}


def _load(path):
    if not os.path.exists(path):
        return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return None


def _age_days(iso: str | None, today: dt.date) -> int | None:
    if not iso:
        return None
    try:
        return (today - dt.date.fromisoformat(str(iso)[:10])).days
    except ValueError:
        return None


# ----------------------------------------------------------------------------
# 各段組裝（純資料 → dict）
# ----------------------------------------------------------------------------

def weather_section(state: list | None, backtest: dict | None, today: dt.date) -> dict:
    if not state:
        return {"status": "NO_DATA"}
    rows = sorted(state, key=lambda r: r["date"])
    last = rows[-1]
    week = rows[-5:]
    path = [{"date": r["date"], "regime": r["regime"], "score": r.get("score"),
             "alerts": r.get("alerts") or []} for r in week]
    transitions = [(a["date"], a["regime"], b["regime"]) for a, b in zip(week, week[1:])
                   if a["regime"] != b["regime"]]
    alert_days = [r["date"] for r in week if "capitulation" in (r.get("alerts") or [])]
    cap = ((backtest or {}).get("alerts") or {}).get("capitulation")
    return {
        "status": "OK", "as_of": last["date"], "age_days": _age_days(last["date"], today),
        "regime": last["regime"], "emoji": STATE_EMOJI.get(last["regime"], "❔"),
        "score": last.get("score"), "pcts": last.get("pcts") or {},
        "week_path": path, "week_transitions": [{"date": d, "from": a, "to": b} for d, a, b in transitions],
        "week_alert_days": alert_days,
        "capitulation_backtest": cap,
    }


def dca_section(led: dict | None, today: dt.date) -> dict:
    if not led or led.get("status") != "OK":
        return {"status": "NO_DATA", "reason": (led or {}).get("reason")}
    cur = led["current"]
    full = led["windows"].get("full") or {}
    l12 = led["windows"].get("last_12m") or {}

    def rules(w):
        return {k: {"label": v["label"], "n_buys": v["n_buys"], "invested": v["invested"],
                    "avg_cost": v["avg_cost"], "avg_cost_vs_plain_pct": v["avg_cost_vs_plain_pct"],
                    "return_pct": v["return_pct"], "xirr_pct": v["xirr_pct"], "n_boosts": v["n_boosts"]}
                for k, v in (w.get("rules") or {}).items()}
    boosts = full.get("boosts") or []
    edges = [b["edge_vs_next_regular_pct"] for b in boosts if b.get("edge_vs_next_regular_pct") is not None]
    return {
        "status": "OK", "as_of": led["prices_to"], "age_days": _age_days(led["prices_to"], today),
        "instrument": led["instrument"], "amount_twd": led["amount_twd"],
        "current": cur,
        "full": {"start": full.get("start"), "n_periods": full.get("n_periods"), "rules": rules(full),
                 "boost_n": len(boosts),
                 "boost_edge_mean_pct": round(sum(edges) / len(edges), 2) if edges else None,
                 "boost_edge_win_pct": round(100 * sum(e > 0 for e in edges) / len(edges)) if edges else None},
        "last_12m": {"start": l12.get("start"), "n_periods": l12.get("n_periods"), "rules": rules(l12)},
    }


def delta_section(state: list | None, today: dt.date) -> dict:
    if not state:
        return {"status": "NO_DATA"}
    last = state[-1]
    full = next((e for e in reversed(state) if str(e.get("overall")) in ("GREEN", "YELLOW", "RED")), None)
    # 各模組最新狀態：從最近的 run 往回找，每個模組取最後一次出現
    latest_mod: dict = {}
    for e in reversed(state):
        for m in e.get("modules", []):
            key = m["module"].split()[0]
            if key not in latest_mod:
                latest_mod[key] = {"module": m["module"], "status": m["status"],
                                   "headline": m.get("headline") or m.get("error") or "",
                                   "ts": e.get("ts")}
    scored = [e for e in state if (e.get("outcomes") or {}).get("t20_excess_pct") is not None]
    return {
        "status": "OK", "as_of": str(last.get("ts", ""))[:10], "age_days": _age_days(last.get("ts"), today),
        "last_overall": last.get("overall"), "last_modules_requested": last.get("modules_requested"),
        "full_overall": full.get("overall") if full else None,
        "full_ts": str(full.get("ts", ""))[:10] if full else None,
        "modules": [latest_mod[k] for k in sorted(latest_mod)],
        "divergence": last.get("divergence"),
        "scored_n": len(scored),
    }


def calendar_section(today: dt.date) -> list[dict]:
    """規則式日曆（不抓網路）：月營收公告截止（每月 10 日）、下個月 10 日；其餘由人補。"""
    out = []
    y, m = today.year, today.month
    for _ in range(2):
        d = dt.date(y, m, 10)
        if d >= today:
            out.append({"date": d.isoformat(), "what": "台股月營收公告截止（2330／2308 通常 10 日前後）",
                        "days": (d - today).days})
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out[:2]


def tldr(weather: dict, dca: dict, delta: dict) -> list[str]:
    L = []
    if dca.get("status") == "OK":
        c = dca["current"]
        wg = c.get("weekly_gate")
        if wg:
            L.append(f"週檢查（{wg['decision_date']}）：{wg['text']}。")
        elif c.get("boost_pending"):
            L.append(f"投降窗開著：規則 B 加碼 {c['boost_amount']:,.0f} 元待執行（警報日 {'、'.join(c['recent_alert_days'])}）。")
        else:
            L.append(f"本週照常：下一個例行買日 {c['next_regular_buy']}，{c['plain_amount']:,.0f} 元；無加碼窗。")
    if weather.get("status") == "OK":
        w = weather
        tr = w["week_transitions"]
        L.append(f"鋒面 {w['emoji']} {w['regime']}"
                 + (f"（本週由 {tr[-1]['from']} 轉入）" if tr else "（本週未變）") + "。")
    if delta.get("status") == "OK":
        dv = delta.get("divergence") or {}
        L.append(f"2308 前提 {LIGHT.get(delta.get('full_overall') or 'NO_DATA')} "
                 f"{delta.get('full_overall') or '尚無全模組判定'}；{dv.get('text') or '背離 NO_DATA'}")
    if dca.get("status") == "OK":
        f = dca["full"]
        b = f["rules"].get("capitulation_boost") or {}
        if f.get("boost_n"):
            L.append(f"投降窗加碼歷史 {f['boost_n']} 次：比等到例行日買平均便宜 {f['boost_edge_mean_pct']:+.2f}%"
                     f"、勝率 {f['boost_edge_win_pct']}%；平均成本 vs 純 DCA {b.get('avg_cost_vs_plain_pct'):+.2f}%。")
    return L or ["三支雷達都還沒有輸出。"]


def build_brief(out_dir: str, today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    state = _load(os.path.join(out_dir, "tw_scanner_state.json"))
    backtest = _load(os.path.join(out_dir, "tw_scanner_backtest.json"))
    led = _load(os.path.join(out_dir, "dca_ledger.json"))
    dstate = _load(os.path.join(out_dir, "delta_radar_state.json"))
    weather = weather_section(state, backtest, today)
    dca = dca_section(led, today)
    delta = delta_section(dstate, today)
    checks = []
    for name, sec, stale in (("天氣台", weather, 4), ("DCA 帳本", dca, 4), ("delta_radar", delta, 8)):
        if sec.get("status") != "OK":
            checks.append({"level": "bad", "label": f"{name} 無輸出", "text": f"{name}：NO_DATA（{sec.get('reason') or '缺輸出檔'}）"})
        elif sec.get("age_days") is not None and sec["age_days"] > stale:
            checks.append({"level": "warn", "label": f"{name} 過期", "text": f"{name}：最新資料 {sec['as_of']}，已 {sec['age_days']} 天"})
        else:
            checks.append({"level": "ok", "label": f"{name} 正常", "text": f"{name}：最新 {sec.get('as_of')}"})
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "today": today.isoformat(), "cadence": "weekly",
        "tldr": tldr(weather, dca, delta),
        "weather": weather, "dca": dca, "delta": delta,
        "calendar": calendar_section(today), "checks": checks,
        "note": "週報：規則影子帳本＋溫度計＋論點監控。沒有任何一行是買賣建議；曝險與部位由人管。",
    }


# ----------------------------------------------------------------------------
# 人讀版
# ----------------------------------------------------------------------------

def _pm(x, unit="%"):
    return "—" if x is None else f"{x:+.2f}{unit}"


def render_md(b: dict) -> str:
    w, d, dl = b["weather"], b["dca"], b["delta"]
    L = [f"# 📬 台股週報 — {b['today']}", "",
         "> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308 論點監控。"
         "**沒有任何一行是買賣建議；曝險與部位由人管。**", "",
         "## TL;DR", ""]
    L += [f"- {x}" for x in b["tldr"]]
    L += ["", "## 1. 本期機械指示（DCA 規則影子帳本）", ""]
    if d.get("status") == "OK":
        c = d["current"]
        wg = c.get("weekly_gate")
        if wg:
            L.append(f"- **週檢查・月預算**（決策日 {wg['decision_date']}）：{wg['text']}")
        L += [f"- 例行（對照）：**{c['next_regular_buy']}** 買 {c['plain_amount']:,.0f} 元{'（本月已買）' if c['this_month_bought'] else ''}",
              f"- 投降窗加碼：{'**待執行** ' + format(c['boost_amount'], ',.0f') + ' 元' if c['boost_pending'] else '無'}",
              f"- 鋒面調節（假說）：{c['regime']} ×{c['regime_multiplier']:g} = {c['regime_amount']:,.0f} 元",
              "", f"自 {d['full']['start']} 起 {d['full']['n_periods']} 期（等額假設）：", "",
              "| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |", "|---|---|---|---|---|---|"]
        for k, r in d["full"]["rules"].items():
            L.append(f"| {r['label']} | {r['n_buys']} | {r['avg_cost']} | {_pm(r['avg_cost_vs_plain_pct'])} "
                     f"| {_pm(r['return_pct'])} | {_pm(r['xirr_pct'])} |")
        f = d["full"]
        L.append("")
        L.append(f"投降窗加碼 {f['boost_n']} 次" + (f"：edge {_pm(f['boost_edge_mean_pct'])}、勝率 {f['boost_edge_win_pct']}%。" if f["boost_n"] else "。")
                 + " 明細見 `dca_ledger.md`。")
    else:
        L.append(f"NO_DATA：{d.get('reason') or '缺 dca_ledger.json'}")
    L += ["", "## 2. 天氣（籌碼溫度計）", ""]
    if w.get("status") == "OK":
        L.append(f"- 鋒面 {w['emoji']} **{w['regime']}**（score {w['score']:+.2f}，{w['as_of']}）"
                 + (f"；本週轉移：" + "、".join(f"{t['date']} {t['from']}→{t['to']}" for t in w["week_transitions"]) if w["week_transitions"] else "；本週未變"))
        p = w["pcts"]
        L.append(f"- 分位數：外資現貨 {p.get('f_spot_20d')}、大台Δ {p.get('tx_delta')}、散戶小台 {p.get('retail_mtx')}、融資Δ {p.get('margin_chg')}")
        L.append(f"- 本週投降警報：{'、'.join(w['week_alert_days']) if w['week_alert_days'] else '無'}")
        cap = w.get("capitulation_backtest")
        if cap:
            h20 = (cap.get("horizons") or {}).get("20d") or {}
            L.append(f"- 警報戰績（月更回測）：{cap['episodes']} 簇，20 日中位 {_pm(h20.get('median_pct'))} vs 基線 {_pm(h20.get('baseline_median_pct'))}、命中 {round((h20.get('hit_rate') or 0)*100)}%")
    else:
        L.append("NO_DATA")
    L += ["", "## 3. 2308 論點監控（delta_radar）", ""]
    if dl.get("status") == "OK":
        dv = dl.get("divergence") or {}
        L.append(f"- 前提（最近全模組 {dl.get('full_ts') or '—'}）：{LIGHT.get(dl.get('full_overall') or 'NO_DATA')} {dl.get('full_overall') or '尚無'}")
        L.append(f"- {dv.get('text') or '背離 NO_DATA'}")
        for m in dl["modules"]:
            L.append(f"  - {LIGHT.get(m['status'], '⚪')} {m['module']}：{m['headline']}")
        L.append(f"- 回填樣本 {dl['scored_n']} 筆（T+20 超額）；退役判準見 `delta_radar_report.md`")
    else:
        L.append("NO_DATA")
    L += ["", "## 4. 下週日曆", ""]
    L += [f"- {c['date']}（{c['days']} 天後）{c['what']}" for c in b["calendar"]] or ["- 無規則式事件"]
    L += ["", "## 5. 資料健康", ""]
    L += [f"- {'✅' if c['level']=='ok' else '⚠️' if c['level']=='warn' else '❌'} {c['text']}" for c in b["checks"]]
    L += ["", "---", f"*tw_brief — {b['note']} 產出 {b['generated_at']}*"]
    return "\n".join(L)


# ----------------------------------------------------------------------------
# selftest
# ----------------------------------------------------------------------------

def selftest() -> bool:
    out = tempfile.mkdtemp(prefix="tw_brief_selftest_")
    today = dt.date(2026, 9, 12)
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg, file=sys.stderr)
        ok = ok and bool(cond)

    # 全缺 → 不炸、全 NO_DATA
    b = build_brief(out, today)
    check(all(c["level"] == "bad" for c in b["checks"]) and "NO_DATA" in render_md(b), "三份都缺 → NO_DATA 不崩潰")
    # 造假資料
    json.dump([{"date": "2026-09-08", "regime": "DE_RISK", "score": -0.3, "alerts": [], "pcts": {"f_spot_20d": 10}},
               {"date": "2026-09-09", "regime": "DE_RISK", "score": -0.4, "alerts": ["capitulation"], "pcts": {"f_spot_20d": 4}},
               {"date": "2026-09-10", "regime": "CAPITULATION", "score": -0.6, "alerts": [], "pcts": {"f_spot_20d": 3}},
               {"date": "2026-09-11", "regime": "CAPITULATION", "score": -0.6, "alerts": [], "pcts": {"f_spot_20d": 3}}],
              open(os.path.join(out, "tw_scanner_state.json"), "w"))
    json.dump({"alerts": {"capitulation": {"episodes": 8, "horizons": {"20d": {"median_pct": 8.72, "baseline_median_pct": 2.17, "hit_rate": 0.75}}}}},
              open(os.path.join(out, "tw_scanner_backtest.json"), "w"))
    json.dump({"status": "OK", "instrument": "0050", "amount_twd": 10000, "prices_to": "2026-09-11",
               "current": {"as_of": "2026-09-11", "next_regular_buy": "2026-10-06", "this_month_bought": True,
                           "plain_amount": 10000, "boost_pending": True, "boost_amount": 10000,
                           "recent_alert_days": ["2026-09-09"], "regime": "CAPITULATION", "regime_multiplier": 2.0, "regime_amount": 20000,
                           "weekly_gate": {"decision_date": "2026-09-11", "month": "2026-09", "month_spent": False,
                                           "week_alert_days": ["2026-09-09"], "last_week_of_month": False,
                                           "action": "buy_boost", "amount": 20000,
                                           "text": "本週有投降警報（2026-09-09）→ 下一交易日投入 20,000 元，當月不再行動"}},
               "windows": {"full": {"start": "2019-01-02", "n_periods": 93,
                                    "rules": {"plain": {"label": "純定期定額", "n_buys": 93, "invested": 930000, "avg_cost": 82.2, "avg_cost_vs_plain_pct": 0.0, "return_pct": 100.5, "xirr_pct": 17.8, "n_boosts": 0},
                                              "capitulation_boost": {"label": "定期定額＋投降窗加碼", "n_buys": 96, "invested": 960000, "avg_cost": 81.8, "avg_cost_vs_plain_pct": -0.4, "return_pct": 101.3, "xirr_pct": 17.8, "n_boosts": 3}},
                                    "boosts": [{"edge_vs_next_regular_pct": 1.4}, {"edge_vs_next_regular_pct": 3.2}, {"edge_vs_next_regular_pct": -0.5}]},
                           "last_12m": {"start": "2025-09-11", "n_periods": 12, "rules": {}}}},
              open(os.path.join(out, "dca_ledger.json"), "w"))
    json.dump([{"ts": "2026-09-07T03:30:00+00:00", "overall": "YELLOW", "modules_requested": ["m1", "m2"],
                "modules": [{"module": "M1 revenue_acceleration", "status": "YELLOW", "headline": "減速"}],
                "outcomes": {"t20_excess_pct": -3.0}},
               {"ts": "2026-09-11T02:30:00+00:00", "overall": "PARTIAL(m5)", "modules_requested": ["m5"],
                "modules": [{"module": "M5 narrative_triggers", "status": "GREEN", "headline": "安靜"}],
                "divergence": {"flag": "premise_ok_price_down", "text": "🔀 背離：前提健在（YELLOW）、價格 20 日 -12.0%"}}],
              open(os.path.join(out, "delta_radar_state.json"), "w"))
    b = build_brief(out, today)
    md = render_md(b)
    check(b["weather"]["regime"] == "CAPITULATION" and b["weather"]["week_transitions"][0]["to"] == "CAPITULATION", "鋒面與本週轉移")
    check(b["weather"]["week_alert_days"] == ["2026-09-09"], "本週警報日")
    check(b["dca"]["full"]["boost_n"] == 3 and abs(b["dca"]["full"]["boost_edge_mean_pct"] - 1.37) < 0.01, "加碼 edge 摘要")
    check(b["delta"]["full_overall"] == "YELLOW" and b["delta"]["divergence"]["flag"] == "premise_ok_price_down", "2308 前提取最近全模組、背離取最新")
    check(b["tldr"][0].startswith("週檢查") and "當月不再行動" in b["tldr"][0], "TL;DR 首句是週檢查指示")
    check(all(c["level"] == "ok" for c in b["checks"]), "資料健康全綠")
    check("台股週報" in md and "本期機械指示" in md and "🔀" in md and "月營收" in md, "md 五段齊全")
    json.dump(b, open(os.path.join(out, "tw_brief.json"), "w"), ensure_ascii=False)
    open(os.path.join(out, "tw_weekly.md"), "w", encoding="utf-8").write(md)
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="台股週報組裝器")
    ap.add_argument("--output-dir", default=os.path.join(HERE, "output"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        ok = selftest()
        print(f"\n[selftest] {'ALL GREEN ✅' if ok else 'FAILED ❌'}", file=sys.stderr)
        return 0 if ok else 2
    b = build_brief(args.output_dir)
    md = render_md(b)
    json.dump(b, open(os.path.join(args.output_dir, "tw_brief.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(os.path.join(args.output_dir, "tw_weekly.md"), "w", encoding="utf-8").write(md)
    print(md)
    print(f"\n[written] {args.output_dir}/tw_brief.json, tw_weekly.md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
