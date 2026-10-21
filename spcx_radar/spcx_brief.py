#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spcx_brief.py — SPCX C 池 brief 組裝器（space_radar + Option Sage + 人工回應 → 一份 JSON）
==========================================================================================
定位（PLAN_2026-10_c_pool_alert §二）：排程最後一步，把當天幾份輸出組成 brief 專用的
  output/spcx_brief.json   機器可讀（Cloudflare Worker /api/spcx 讀這份；brief 橫幅與 SPCX 分頁、dashboard 燈）

零網路、零判定：Sage 已經算完 level，這裡只做「L2 亮了幾天」「關門幾天」「人回應了沒」這類序列與時限計算。
缺哪份就標 NO_DATA，不報錯。

輸入：output/space_radar.json、output/spcx_options.json、output/spcx_options_history.csv、
      output/spcx_iv_history.csv、config/spcx_config.json、config/spcx_dca_log.json、
      config/spcx_c_viewpoint.json、config/spcx_c_decisions.json

Usage:
  python spcx_radar/spcx_brief.py
  python spcx_radar/spcx_brief.py --selftest
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RESPONSE_DEADLINE_TDAYS = 2     # L2 亮燈後幾個交易日內要有人工回應
BANNER_AFTER_CLOSE_TDAYS = 5    # L2 關門後橫幅還要顯示幾個交易日（brief 端用，這裡只給數字）
VIEWPOINT_STALE_DAYS = 60


def _load_json(path):
    if not os.path.exists(path):
        return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return None


def _load_csv(path):
    if not os.path.exists(path):
        return []
    try:
        return list(csv.DictReader(open(path, encoding="utf-8")))
    except Exception:
        return []


def _f(x):
    try:
        return None if x in (None, "", "nan") else float(x)
    except (TypeError, ValueError):
        return None


def _d(s):
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


def add_trading_days(d: dt.date, n: int) -> dt.date:
    """加 n 個交易日（週一到週五；不含美股假日——寬一天不影響「人在不在」這件事）。"""
    step = 1 if n >= 0 else -1
    while n != 0:
        d += dt.timedelta(days=step)
        if d.weekday() < 5:
            n -= step
    return d


def trading_days_between(a: dt.date, b: dt.date) -> int:
    """(a, b] 之間的週間日數；b < a 回負數。"""
    if b < a:
        return -trading_days_between(b, a)
    n, d = 0, a
    while d < b:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def carry_of(s: dict, price: float | None, market_date: dt.date) -> dict | None:
    """與 spcx_options.carry_of 同一公式（這裡不 import，避免 brief 吃到 yfinance 依賴）。"""
    try:
        exp = _d(s.get("exp"))
        bid, ask = _f(s.get("bid")), _f(s.get("ask"))
        if not exp or not price or bid is None or ask is None or bid <= 0 or ask <= 0:
            return None
        dte = (exp - market_date).days
        if dte <= 0:
            return None
        mid = (bid + ask) / 2
        intrinsic = max(price - float(s["strike"]), 0.0)
        extrinsic = mid - intrinsic
        if extrinsic < 0:
            return None
        return {"dte": dte, "mid": round(mid, 2), "intrinsic": round(intrinsic, 2), "extrinsic": round(extrinsic, 2),
                "carry_pct_annual": round(extrinsic / price / (dte / 365) * 100, 2)}
    except Exception:
        return None


# ----------------------------------------------------------------------------
# 序列計算
# ----------------------------------------------------------------------------

def level_sequence(hist: list[dict]) -> list[tuple[str, str]]:
    seq = [(r["date"], r.get("level") or "") for r in hist if r.get("date")]
    seq.sort()
    return [(d, lv) for d, lv in seq if lv in ("L0", "L1", "L2")]


def l2_stats(seq: list[tuple[str, str]], today: dt.date) -> dict:
    """從 level 序列算：目前連續 L2 天數、本段/最近一段 L2 起始、最後 L2 日、關門後幾個交易日。"""
    out = {"l2_streak_days": 0, "l2_start": None, "l2_last_date": None, "l2_days_since_close": None,
           "l2_segments": []}
    if not seq:
        return out
    segs, start, prev = [], None, None
    for d, lv in seq:
        if lv == "L2" and start is None:
            start = d
        elif lv != "L2" and start is not None:
            segs.append((start, prev)); start = None
        prev = d
    if start is not None:
        segs.append((start, prev))
    out["l2_segments"] = [{"start": s, "end": e, "days": sum(1 for d, lv in seq if s <= d <= e and lv == "L2")} for s, e in segs]
    if not segs:
        return out
    last_start, last_end = segs[-1]
    out["l2_last_date"] = last_end
    out["l2_start"] = last_start
    if seq[-1][1] == "L2":
        out["l2_streak_days"] = out["l2_segments"][-1]["days"]
        out["l2_days_since_close"] = 0
    else:
        out["l2_days_since_close"] = sum(1 for d, lv in seq if d > last_end)
    return out


def response_status(level: str | None, l2_start: str | None, decisions: dict | None, today: dt.date) -> dict:
    """PLAN §四：L2 → required；deadline＝本段 L2 起始日 + 2 個交易日；
    本段 l2_start 以後有 decision → answered；今天 ≤ deadline → pending；否則 overdue。非 L2 → n/a。"""
    out = {"required": False, "deadline": None, "status": "n/a", "last": None, "overdue_days": 0,
           "n_decisions": len((decisions or {}).get("decisions") or [])}
    decs = sorted((decisions or {}).get("decisions") or [], key=lambda x: str(x.get("date", "")))
    if decs:
        out["last"] = {k: decs[-1].get(k) for k in ("date", "l2_start", "action", "reason", "detail", "by")}
    if level != "L2" or not l2_start:
        return out
    start = _d(l2_start)
    deadline = add_trading_days(start, RESPONSE_DEADLINE_TDAYS)
    out["required"] = True
    out["deadline"] = deadline.isoformat()
    mine = [x for x in decs if str(x.get("l2_start") or x.get("date", "")) >= l2_start]
    if mine:
        out["status"] = "answered"
        out["last"] = {k: mine[-1].get(k) for k in ("date", "l2_start", "action", "reason", "detail", "by")}
    elif today <= deadline:
        out["status"] = "pending"
    else:
        out["status"] = "overdue"
        out["overdue_days"] = trading_days_between(deadline, today)
    return out


def positions_section(dca: dict | None, price: float | None, cfg: dict | None) -> dict:
    buys = [p for p in (dca or {}).get("purchases") or [] if _f(p.get("shares")) and _f(p.get("price"))]
    shares = sum(float(p["shares"]) for p in buys)
    cost = sum(float(p["shares"]) * float(p["price"]) for p in buys)
    avg = round(cost / shares, 2) if shares else None
    cfg = cfg or {}
    total_capital = _f(cfg.get("total_capital")) or 200000.0
    pool_c = round(total_capital * (_f(cfg.get("pool_c_opt_pct")) or 0.10))
    return {"shares": int(shares), "avg_cost": avg,
            "unrealized_pct": round((price / avg - 1) * 100, 1) if (avg and price) else None,
            "pool_c_cash": pool_c, "n_buys": len(buys)}


def sage_health(opts: dict | None, iv_hist: list[dict], opt_hist: list[dict], today: dt.date) -> dict:
    iv_dates = sorted({r["date"] for r in iv_hist if r.get("date")})
    opt_dates = {r["date"] for r in opt_hist if r.get("date")}
    recent = [d for d in iv_dates if _d(d) and (today - _d(d)).days <= 45]
    missed = [d for d in recent if d not in opt_dates]
    last_market = iv_dates[-1] if iv_dates else None
    # sage_v0.4 之前的 JSON 沒有 market_date：退回 history 最後一列（同一次 Sage 寫的）
    sage_md = (opts or {}).get("market_date") or (opt_hist[-1].get("date") if opt_hist else None)
    return {"last_run": (opts or {}).get("updated_at"), "market_date": sage_md,
            "ran_for_latest_market_day": bool(last_market and last_market in opt_dates),
            "latest_market_day": last_market, "missed_days": missed,
            "history_has_level": any(r.get("level") for r in opt_hist[-3:])}


# ----------------------------------------------------------------------------
# 組裝
# ----------------------------------------------------------------------------

def build_brief(base_dir: str, today: dt.date | None = None) -> dict:
    out_dir, cfg_dir = os.path.join(base_dir, "output"), os.path.join(base_dir, "config")
    radar = _load_json(os.path.join(out_dir, "space_radar.json"))
    opts = _load_json(os.path.join(out_dir, "spcx_options.json"))
    opt_hist = _load_csv(os.path.join(out_dir, "spcx_options_history.csv"))
    iv_hist = _load_csv(os.path.join(out_dir, "spcx_iv_history.csv"))
    cfg = _load_json(os.path.join(cfg_dir, "spcx_config.json"))
    dca = _load_json(os.path.join(cfg_dir, "spcx_dca_log.json"))
    vp = _load_json(os.path.join(cfg_dir, "spcx_c_viewpoint.json"))
    decisions = _load_json(os.path.join(cfg_dir, "spcx_c_decisions.json"))

    today = today or dt.date.today()
    market_date = _d((opts or {}).get("market_date")) or (_d(opt_hist[-1]["date"]) if opt_hist else None) or today
    price = _f((opts or {}).get("price")) or _f((radar or {}).get("price"))
    level = (opts or {}).get("level")
    seq = level_sequence(opt_hist)
    stats = l2_stats(seq, market_date)
    # history 最後一列若就是今天的市場日，level 以 Sage 的 JSON 為準（同一份）；序列算出的 prev 是前一市場日
    prev_level = next((lv for d, lv in reversed(seq) if d < market_date.isoformat()), None)
    resp = response_status(level, stats["l2_start"] if level == "L2" else None, decisions, today)

    liq = (opts or {}).get("liquidity") or {}
    strikes = []
    for s in liq.get("detail") or []:
        c = carry_of(s, price, market_date) if s.get("carry_pct_annual") is None else {
            k: s.get(k) for k in ("dte", "mid", "intrinsic", "extrinsic", "carry_pct_annual")}
        strikes.append({"exp": s.get("exp"), "strike": s.get("strike"), "bid": s.get("bid"), "ask": s.get("ask"),
                        "oi": s.get("oi"), "spread_pct": s.get("spread_pct"), **(c or {})})
    iv = (opts or {}).get("iv") or {}
    gates = (opts or {}).get("gates")
    if not gates:   # patch 前的 JSON：near 從 iv 區塊填；leaps／carry 用 backfill 寫進 history 同一市場日那列（沒有就 NO_DATA）
        hrow = next((r for r in reversed(opt_hist) if r.get("date") == market_date.isoformat()), None) or {}
        _b = lambda v: v in (True, "True")   # noqa: E731
        c = cfg or {}
        gates = {"near": {"value": iv.get("atm_iv"), "pctile": iv.get("pctile"), "rel_calm": _b(iv.get("rel_calm")),
                          "abs_acceptable": bool(iv.get("abs_acceptable")), "stable": bool(iv.get("stable")), "level": level,
                          "pctile_calm": c.get("opt_iv_pctile_calm", 40), "abs_gate": c.get("opt_iv_abs_acceptable", 0.55)},
                 "leaps": ({"value": _f(hrow.get("leaps_atm_iv")), "pctile": _f(hrow.get("leaps_pctile")), "rel_calm": _b(hrow.get("leaps_rel_calm")),
                            "abs_acceptable": _b(hrow.get("leaps_abs_ok")), "stable": _b(hrow.get("leaps_stable")), "level": hrow.get("level_leaps"),
                            "pctile_calm": c.get("opt_leaps_iv_pctile_calm", 40), "abs_gate": c.get("opt_leaps_iv_abs_acceptable", 0.55)}
                           if hrow.get("level_leaps") else {"status": "NO_DATA"}),
                 "carry": ({"min_carry_pct": _f(hrow.get("min_carry_pct")), "ok": _b(hrow.get("carry_ok")), "stable": _b(hrow.get("carry_stable")),
                            "level": hrow.get("level_carry"), "threshold": c.get("opt_max_carry_pct", 5.0), "approx": _b(hrow.get("carry_backfill_approx"))}
                           if hrow.get("level_carry") else {"status": "NO_DATA"})}
    vp_detail = ((opts or {}).get("viewpoint") or {}).get("detail") or {}
    vp_updated = _d(vp_detail.get("updated") or (vp or {}).get("updated"))
    vp_age = (today - vp_updated).days if vp_updated else None
    health = sage_health(opts, iv_hist, opt_hist, today)
    conds = (opts or {}).get("conditions") or {}
    cond_vals = list(conds.values())
    conditions = {
        "iv_gate_calm_stable": (cond_vals[0] in (True, "True")) if len(cond_vals) > 0 else None,
        "iv_gate_abs_ok": (cond_vals[1] in (True, "True")) if len(cond_vals) > 1 else None,
        "liquidity_ok": bool(liq.get("liquid")),
        "viewpoint_ok": bool(((opts or {}).get("viewpoint") or {}).get("passes")),
        "labels": list(conds.keys()),
    }

    # ---- checks ----
    checks = []
    # 文案原則（2026-10-21 擁有者要求）：dashboard 的詞要簡單明白——用綠燈／黃燈／灰燈，不講 gate、L2「就是這個」、關門這類黑話
    if not opts:
        checks.append({"level": "bad", "label": "沒有判定", "text": "判定程式沒有輸出（缺 spcx_options.json）"})
    elif not health["ran_for_latest_market_day"]:
        checks.append({"level": "bad", "label": "今天沒跑", "text": f"判定程式最後跑到 {health['market_date']}，IV 資料已經到 {health['latest_market_day']}，今天這天沒跑"})
    else:
        checks.append({"level": "ok", "label": "今天有跑", "text": f"判定程式今天有跑（市場日 {health['market_date']}），結果 {level}"})
    if health["missed_days"]:
        checks.append({"level": "warn", "label": f"漏跑 {len(health['missed_days'])} 天", "text": f"最近 45 天有 {len(health['missed_days'])} 個交易日沒跑：{'、'.join(health['missed_days'])}"})
    if opt_hist and not health["history_has_level"]:
        checks.append({"level": "warn", "label": "歷史缺判定欄", "text": "spcx_options_history.csv 最近幾列沒有 level 欄：backfill_level.py 還沒跑或判定程式版本舊"})
    if resp["status"] == "overdue":
        checks.append({"level": "bad", "label": "還沒回答", "text": f"綠燈從 {stats['l2_start']} 亮到現在，{resp['deadline']} 前該回答，已經晚了 {resp['overdue_days']} 個交易日"})
    elif resp["status"] == "pending":
        checks.append({"level": "warn", "label": "等你回答", "text": f"綠燈從 {stats['l2_start']} 亮起，{resp['deadline']} 前要回答：做、不做、還是再看"})
    elif resp["status"] == "answered":
        checks.append({"level": "ok", "label": "已回答", "text": f"這段綠燈已經回答：{resp['last']['date']} {resp['last']['action']}"})
    if vp_age is None:
        checks.append({"level": "warn", "label": "看法沒日期", "text": "你的看法（viewpoint）沒有寫更新日期"})
    elif vp_age > VIEWPOINT_STALE_DAYS:
        checks.append({"level": "warn", "label": "看法太舊", "text": f"你的看法是 {vp_updated} 寫的，已經 {vp_age} 天沒更新；燈亮時先想一下理由還成不成立"})
    else:
        checks.append({"level": "ok", "label": "看法還新", "text": f"你的看法 {vp_updated} 更新（{vp_age} 天前）"})
    if radar:
        checks.append({"level": "ok", "label": "雷達正常", "text": f"space_radar 有跑：市值 {radar.get('market_cap_t')}T、階段 {radar.get('stage')}"})
    else:
        checks.append({"level": "warn", "label": "雷達沒輸出", "text": "space_radar.json 缺"})

    # ---- 白話版 ----
    gm = (opts or {}).get("gate_mode", "near")
    near = gates.get("near") or {}
    iv_pct = f"{near['value']*100:.0f}%" if near.get("value") else "—"
    LV_WORD = {"L2": "綠燈", "L1": "黃燈", "L0": "灰燈"}
    GM_WORD = {"near": "近月 IV", "leaps": "長天期 IV", "carry": "借錢成本"}
    lv_word = lambda lv: f"{LV_WORD.get(lv, '—')}（{lv}）" if lv else "—"   # noqa: E731
    if not opts:
        do_line, items = "C 池：資料還沒到，不動。", []
    elif level == "L2":
        do_line = (f"C 池：🟢 綠燈（L2），已經亮了 {stats['l2_streak_days']} 天。"
                   + {"answered": "你已經回答過了。", "pending": f"{resp['deadline']} 前要回答：做、不做、還是再看。",
                      "overdue": f"回答已經晚了 {resp['overdue_days']} 天，先寫一筆，寫「不做」也算。"}.get(resp["status"], ""))
        items = [f"四個條件都過了：IV {iv_pct}、合約{'好買賣' if liq.get('liquid') else '不好買賣'}、你的看法信心 {((opts or {}).get('viewpoint') or {}).get('confidence')}/5。",
                 "燈亮只代表環境到了，不是叫你買。買哪一檔、買多少，自己決定，一次不超過 C 池的一半。",
                 "第 3 段列了好買賣的合約，和每一檔一年的持有成本。"]
    elif stats.get("l2_days_since_close") is not None and stats["l2_days_since_close"] <= BANNER_AFTER_CLOSE_TDAYS and stats.get("l2_last_date"):
        do_line = f"C 池：🟡 綠燈 {stats['l2_days_since_close']} 天前熄了（最後一天 {stats['l2_last_date']}），現在是{lv_word(level)}。"
        items = [f"為什麼熄：看第 1 段哪個條件變紅。IV 現在 {iv_pct}。",
                 "剛熄的燈常常會再亮，不用追，但要知道它剛亮過。"]
    else:
        do_line = (f"C 池：{'🟡 黃燈（L1）' if level == 'L1' else '⚪ 灰燈（L0）'}，不用做什麼。IV {iv_pct}"
                   + ("，等它回到 45–50%。" if level == "L1" else "。"))
        items = [f"現在用「{GM_WORD.get(gm, gm)}」這把尺。三把尺各自的結果：近月 IV {lv_word(gates.get('near', {}).get('level'))}／"
                 f"長天期 IV {lv_word(gates.get('leaps', {}).get('level'))}／借錢成本 {lv_word(gates.get('carry', {}).get('level'))}。"]
        if stats.get("l2_segments"):
            last = stats["l2_segments"][-1]
            items.append(f"上一次綠燈：{last['start']}→{last['end']}（{last['days']} 天）。")
    bad = sum(1 for c in checks if c["level"] == "bad")
    items.append(f"有 {bad} 項資料有問題，看最後一段。" if bad else "資料都正常。")

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "market_date": market_date.isoformat(), "today": today.isoformat(),
        "days_since_ipo": (opts or {}).get("days_since_ipo"), "price": price,
        "market_cap_t": (radar or {}).get("market_cap_t"),
        "c_pool": {
            "level": level, "level_prev": prev_level, "transition": (opts or {}).get("transition"),
            "gate_mode": gm, "gates": gates,
            "l2_streak_days": stats["l2_streak_days"], "l2_start": stats["l2_start"] if level == "L2" else None,
            "l2_last_date": stats["l2_last_date"], "l2_days_since_close": stats["l2_days_since_close"],
            "l2_segments": stats["l2_segments"],
            "conditions": conditions,
            "iv": {"atm": iv.get("atm_iv"), "pctile": iv.get("pctile"), "stable": bool(iv.get("stable")),
                   "leaps_atm": liq.get("leaps_atm_iv"), "leaps_exp": liq.get("leaps_iv_exp"),
                   "abs_gate": (gates.get("near") or {}).get("abs_gate", 0.55)},
            "liquidity": {"total_int": liq.get("total_int"), "usable_strikes": liq.get("usable_strikes"),
                          "best_spread_pct": liq.get("best_spread_pct"), "liquid": liq.get("liquid")},
            "skew": ((opts or {}).get("skew") or {}).get("skew_type"),
            "viewpoint": {"confidence": ((opts or {}).get("viewpoint") or {}).get("confidence"),
                          "catalyst": vp_detail.get("catalyst"), "thesis": vp_detail.get("thesis"),
                          "updated": vp_detail.get("updated"), "age_days": vp_age, "stale": bool(vp_age and vp_age > VIEWPOINT_STALE_DAYS)},
            "strikes": strikes,
            "response": resp,
        },
        "positions": positions_section(dca, price, cfg),
        "sage_health": health,
        "checks": checks,
        "do_line": do_line, "items": items,
        "note": "C 池 gate 不是 hand：brief 只轉發 Sage 的判定與可用 strike，不建議部位；回應紀錄在 config/spcx_c_decisions.json。",
    }


# ----------------------------------------------------------------------------
# selftest
# ----------------------------------------------------------------------------

def selftest() -> bool:
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg, file=sys.stderr)
        ok = ok and bool(cond)

    base = tempfile.mkdtemp(prefix="spcx_brief_selftest_")
    os.makedirs(os.path.join(base, "output")); os.makedirs(os.path.join(base, "config"))
    b = build_brief(base, dt.date(2026, 10, 21))
    check(b["c_pool"]["level"] is None and any(c["level"] == "bad" for c in b["checks"]) and "不動" in b["do_line"], "全缺 → NO_DATA 不崩潰")

    def hist_rows(levels):   # 2026-10-01 起每個週間日一列
        rows, d = [], dt.date(2026, 10, 1)
        for lv in levels:
            while d.weekday() >= 5:
                d += dt.timedelta(days=1)
            rows.append({"date": d.isoformat(), "level": lv, "atm_iv": "0.5", "leaps_atm_iv": "0.6"})
            d += dt.timedelta(days=1)
        return rows

    def write(levels, opts_level, decisions=None, vp_updated="2026-08-18"):
        rows = hist_rows(levels)
        with open(os.path.join(base, "output", "spcx_options_history.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        with open(os.path.join(base, "output", "spcx_iv_history.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["date", "price", "atm_iv"]); w.writeheader()
            w.writerows([{"date": r["date"], "price": "150", "atm_iv": "0.5"} for r in rows] + [{"date": "2026-10-09", "price": "150", "atm_iv": "0.5"}])
        md = rows[-1]["date"]
        json.dump({"updated_at": "2026-10-21T00:41:16", "market_date": md, "price": 147.96, "level": opts_level, "transition": None,
                   "gate_mode": "near", "days_since_ipo": 131,
                   "gates": {"near": {"value": 0.4851, "pctile": 17.1, "rel_calm": True, "abs_acceptable": True, "stable": True, "level": opts_level, "abs_gate": 0.55},
                             "leaps": {"value": 0.60, "pctile": 10.0, "rel_calm": True, "abs_acceptable": False, "stable": True, "level": "L1"},
                             "carry": {"min_carry_pct": 7.7, "ok": False, "stable": False, "threshold": 5.0, "level": "L1"}},
                   "iv": {"atm_iv": 0.4851, "pctile": 17.1, "stable": True},
                   "liquidity": {"liquid": True, "total_int": 1150288, "usable_strikes": 107, "best_spread_pct": 0.017, "leaps_atm_iv": 0.5951, "leaps_iv_exp": "2029-01-19",
                                 "detail": [{"exp": "2028-12-15", "strike": 100.0, "oi": 7703, "spread_pct": 0.017, "bid": 72.0, "ask": 73.25}]},
                   "skew": {"skew_type": "neutral"},
                   "viewpoint": {"confidence": 5, "passes": True, "detail": {"catalyst": "x", "thesis": "y", "updated": vp_updated}},
                   "conditions": {"IV 相對冷卻且穩定（near）": True, "IV 絕對可接受（≤防線）（near）": True, "流動性過關": True, "觀點信心達標": True}},
                  open(os.path.join(base, "output", "spcx_options.json"), "w"))
        json.dump({"decisions": decisions or []}, open(os.path.join(base, "config", "spcx_c_decisions.json"), "w"))
        json.dump({"purchases": [{"date": "2026-06-12", "shares": 100, "price": 150}, {"date": "2026-07-01", "shares": 100, "price": 140}]},
                  open(os.path.join(base, "config", "spcx_dca_log.json"), "w"))
        json.dump({"total_capital": 200000, "pool_c_opt_pct": 0.1}, open(os.path.join(base, "config", "spcx_config.json"), "w"))
        json.dump({"updated_at": "x", "market_cap_t": 1.95, "stage": 3, "price": 147.96}, open(os.path.join(base, "output", "space_radar.json"), "w"))
        return md

    # L2 第 3 個交易日、無回應 → overdue（10/1 四、10/2 五、10/5 一：L2 從 10/1 起，期限 10/5，今天 10/6）
    md = write(["L1", "L2", "L2", "L2", "L2"], "L2")          # 10/1 L1、10/2 L2、10/5 L2、10/6 L2、10/7 L2
    b = build_brief(base, dt.date(2026, 10, 7))
    cp = b["c_pool"]
    check(cp["l2_streak_days"] == 4 and cp["l2_start"] == "2026-10-02" and cp["l2_days_since_close"] == 0, f"連續 L2 天數＝4、起始 10/02（got {cp['l2_streak_days']}, {cp['l2_start']}）")
    check(cp["response"]["deadline"] == "2026-10-06" and cp["response"]["status"] == "overdue" and cp["response"]["overdue_days"] == 1, f"期限 10/06、逾期 1 日（got {cp['response']})")
    check(any(c['label'] == '還沒回答' and c['level'] == 'bad' for c in b["checks"]) and "晚了" in b["do_line"], "逾期 → 紅燈 + 白話版點名")
    check(cp["strikes"][0]["carry_pct_annual"] and abs(cp["strikes"][0]["carry_pct_annual"] - 7.7) < 0.4, f"strike carry 年化（got {cp['strikes'][0].get('carry_pct_annual')}）")
    check(b["positions"]["shares"] == 200 and b["positions"]["avg_cost"] == 145.0 and b["positions"]["pool_c_cash"] == 20000, "持倉與 C 池現金")
    check("2026-10-09" in b["sage_health"]["missed_days"], "IV 歷史有、Sage 沒跑的日子進 missed_days")
    # 有回應 → answered
    write(["L1", "L2", "L2", "L2", "L2"], "L2", decisions=[{"date": "2026-10-05", "l2_start": "2026-10-02", "action": "skip", "reason": "r", "by": "c"}])
    b = build_brief(base, dt.date(2026, 10, 7))
    check(b["c_pool"]["response"]["status"] == "answered" and b["c_pool"]["response"]["last"]["action"] == "skip", "有 decision → answered")
    # pending：L2 第一天
    write(["L1", "L1", "L1", "L1", "L2"], "L2")
    b = build_brief(base, dt.date(2026, 10, 7))
    check(b["c_pool"]["response"]["status"] == "pending" and b["c_pool"]["response"]["deadline"] == "2026-10-09", "L2 第一天 → pending、期限 +2 交易日")
    # 關門後 2 個交易日 → l2_days_since_close=2、橫幅黃
    write(["L2", "L2", "L2", "L1", "L1"], "L1")
    b = build_brief(base, dt.date(2026, 10, 7))
    check(b["c_pool"]["l2_days_since_close"] == 2 and b["c_pool"]["l2_last_date"] == "2026-10-05" and b["c_pool"]["response"]["status"] == "n/a" and "熄了" in b["do_line"], f"關門 2 個交易日（got {b['c_pool']['l2_days_since_close']}）")
    check(b["c_pool"]["l2_segments"][-1]["days"] == 3, "L2 段落天數")
    # 觀點過期
    write(["L1"] * 5, "L1", vp_updated="2026-06-01")
    b = build_brief(base, dt.date(2026, 10, 7))
    check(b["c_pool"]["viewpoint"]["stale"] and any(c["label"] == "看法太舊" for c in b["checks"]), "觀點 >60 天 → 標黃")
    shutil.rmtree(base, ignore_errors=True)
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="SPCX C 池 brief 組裝器")
    ap.add_argument("--base-dir", default=HERE)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        ok = selftest()
        print(f"\n[selftest] {'ALL GREEN ✅' if ok else 'FAILED ❌'}", file=sys.stderr)
        return 0 if ok else 2
    b = build_brief(args.base_dir)
    out = os.path.join(args.base_dir, "output", "spcx_brief.json")
    tmp = out + ".tmp"
    json.dump(b, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, out)
    print(f"🧾 {b['do_line']}")
    for c in b["checks"]:
        print(f"   {'✅' if c['level']=='ok' else '⚠️' if c['level']=='warn' else '❌' if c['level']=='bad' else 'ℹ️'} {c['text']}")
    print(f"[written] {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
