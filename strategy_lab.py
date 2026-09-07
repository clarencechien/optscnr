"""
strategy_lab.py — 策略矩陣 shadow 回測 + 結構候選 + 賣點（PLAN_2026-09_strategy_dashboard.md 第 1–3 節）

被誰用：
- main.py：算 structural_pass / 綁定策略 / 賣點，寫進報表「🎯 結構候選」與 data/dashboard/candidates_*.json
- shadow_tracer.py：每天重算「分類 × 出場政策」矩陣 → data/strategy_matrix.json + SHADOWLOG 一節

預先登記（2026-09-08 凍結三個月，見 PLAN 第 3 節）：
- 分類邊界：權利金 $1.5 / $3；DTE 20 / 45 / 120；IV 50
- 三策略：A 死抱到末點；B 2x 賣半＋末點；C 分類綁定（樂透∧IV<50 死抱、實彈 4 口階梯 2/4/8、其餘 -50% 停＋2x 半）
- 結構候選（規則 B）：Score≥8、非 GAMBLE、DTE 21–120、IV<50、OTM<25%、Δ7d>0。只加欄位不改分。
- 矩陣每格 n≥30 才標「可用」，否則「累積中」。

所有函式純計算、零網路；市場資料由呼叫端傳入。
"""
from datetime import datetime, timedelta

PREREG_DATE = "2026-09-08"
TIER_EDGES = (1.5, 3.0)          # 樂透 <1.5 / 中間 1.5–3 / 實彈 ≥3
DTE_EDGES = (20, 45, 120)        # ≤20 / 21–45 / 46–120 / >120
IV_EDGE = 50.0
MATRIX_MIN_N = 30
COST_FACTOR = 0.925 / 1.075      # 買 ask+7.5%、賣 bid-7.5% ≈ ×0.86（真實價差進 schema v2 後取代）


# ---------------------------------------------------------------- 分類
def tier_of(price):
    if price is None:
        return None
    if price < TIER_EDGES[0]:
        return "lottery"
    if price < TIER_EDGES[1]:
        return "mid"
    return "heavy"


TIER_LABEL = {"lottery": "樂透<1.5", "mid": "中間1.5-3", "heavy": "實彈>3"}


def dte_bucket(dte):
    if dte is None:
        return None
    if dte <= DTE_EDGES[0]:
        return "≤20"
    if dte <= DTE_EDGES[1]:
        return "21-45"
    if dte <= DTE_EDGES[2]:
        return "46-120"
    return ">120"


def iv_bucket(iv):
    if iv is None:
        return None
    return "IV<50" if iv < IV_EDGE else "IV≥50"


def structural_pass(score, action, dte, iv, otm_pct, oi_d7):
    """規則 B（預先登記）。otm_pct 為 % 數（25 = 25%）。任一輸入缺 → False。"""
    try:
        return (int(score) >= 8 and str(action) != "GAMBLE"
                and 21 <= int(dte) <= 120 and float(iv) < IV_EDGE
                and float(otm_pct) < 25.0 and float(oi_d7) > 0)
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------- 綁定策略 + 賣點
def bound_strategy(price, iv):
    """策略 C 的分類綁定。回傳 code 與可讀標籤。"""
    t = tier_of(price)
    if t == "lottery" and iv is not None and iv < IV_EDGE:
        return {"code": "A_HOLD", "label": "死抱到末點（樂透∧IV<50）"}
    if t == "heavy":
        return {"code": "C_LADDER4", "label": "4口階梯 2/4/8x + 1口 runner（實彈）"}
    return {"code": "C_STOP_HALF", "label": "-50% 停損 + 2x 賣半 + 末點（中間 / IV≥50）"}


def sell_points(price, expiry_str, strategy_code):
    """把綁定策略換成具體賣點（dashboard 顯示用；不是下單指令）。
    末點 = 到期前 21 天（出場手冊 DTE 21）。"""
    try:
        exp = datetime.strptime(str(expiry_str)[:10], "%Y-%m-%d")
        exit_by = (exp - timedelta(days=21)).strftime("%Y-%m-%d")
    except Exception:
        exit_by = None
    p = float(price)
    if strategy_code == "A_HOLD":
        return {"take_profit": [], "stop": None, "exit_by": exit_by,
                "note": "不設停損、不賣半；DTE 21 全出"}
    if strategy_code == "C_LADDER4":
        return {"take_profit": [round(p * 2, 2), round(p * 4, 2), round(p * 8, 2)], "stop": None,
                "exit_by": exit_by, "note": "4 口：三口掛 2/4/8x 限價，最後一口 DTE 21 出"}
    return {"take_profit": [round(p * 2, 2)], "stop": round(p * 0.5, 2), "exit_by": exit_by,
            "note": "2 口：碰 -50% 全出；碰 2x 賣一口，餘一口 DTE 21 出"}


# ---------------------------------------------------------------- 三點路徑 + 出場政策
def multiples(sig):
    """成熟信號（t5/t10/t20 三點都有價）的倍數序列；否則 None。"""
    entry = sig.get("entry_price") or 0
    if entry <= 0:
        return None
    out = []
    for k in ("t5", "t10", "t20"):
        r = sig.get(k)
        if not r or r.get("opt_price") is None:
            return None
        out.append(r["opt_price"] / entry)
    return out


def pol_hold(m, sig=None):
    return m[-1]


def pol_half(m, sig=None, th=2.0):
    return (th + m[-1]) / 2 if max(m) >= th else m[-1]


def pol_half3(m, sig=None):
    return pol_half(m, sig, 3.0)


def pol_rungs(m, sig=None, th=(2, 4, 8)):
    fired = [t for t in th if max(m) >= t]
    return (sum(fired) + (len(th) - len(fired)) * m[-1] + m[-1]) / (len(th) + 1)


def pol_stop_half(m, sig=None, stop=0.5, th=2.0):
    for x in m:
        if x >= th:
            return (th + m[-1]) / 2
        if x <= stop:
            return stop
    return m[-1]


def pol_bound(m, sig):
    code = bound_strategy(sig.get("entry_price"), sig.get("entry_iv"))["code"]
    if code == "A_HOLD":
        return pol_hold(m)
    if code == "C_LADDER4":
        return pol_rungs(m)
    return pol_stop_half(m)


POLICIES = {
    "A_hold": pol_hold,
    "B_half2x": pol_half,
    "C_bound": pol_bound,
    "half3x": pol_half3,
    "rungs248": pol_rungs,
    "stop_half": pol_stop_half,
}
POLICY_LABEL = {"A_hold": "A 死抱", "B_half2x": "B 2x賣半", "C_bound": "C 分類綁定",
                "half3x": "3x賣半", "rungs248": "4口2/4/8", "stop_half": "-50%停+2x半"}


# ---------------------------------------------------------------- 矩陣
def _dte_of(sig):
    try:
        return (datetime.strptime(sig["expiry"], "%Y-%m-%d")
                - datetime.strptime(sig["snapshot_date"], "%Y-%m-%d")).days
    except Exception:
        return None


def _otm_of(sig):
    spot = sig.get("entry_spot") or 0
    if spot <= 0:
        return None
    return (sig["strike"] / spot - 1) * 100


def sig_structural_pass(sig):
    """舊信號沒有 structural_pass 欄時即時推導（規則 B 用的欄位快照裡都有）。"""
    if sig.get("structural_pass") is not None:
        return bool(sig["structural_pass"])
    return structural_pass(sig.get("score"), "TLDR", _dte_of(sig), sig.get("entry_iv"),
                           _otm_of(sig), sig.get("oi_d7"))


def _event(sig):
    return f"{sig['ticker']}_{sig['snapshot_date']}"


def _summ(rows):
    """一組成熟信號 → n / 事件數 / 命中 / 各政策 EV / 事件等權 EV"""
    if not rows:
        return None
    n = len(rows)
    events = {}
    hits = 0
    pol_sum = {p: 0.0 for p in POLICIES}
    pol_evt = {p: {} for p in POLICIES}
    for sig, m in rows:
        if max(m) >= 2:
            hits += 1
        e = _event(sig)
        events[e] = events.get(e, 0) + 1
        for p, fn in POLICIES.items():
            v = fn(m, sig)
            pol_sum[p] += v
            pol_evt[p].setdefault(e, []).append(v)
    out = {"n": n, "events": len(events), "hit": round(hits / n, 3)}
    out["ev"] = {p: round(pol_sum[p] / n, 3) for p in POLICIES}
    out["ev_event_weighted"] = {
        p: round(sum(sum(v) / len(v) for v in pol_evt[p].values()) / len(events), 3) for p in POLICIES}
    out["best"] = max(POLICIES, key=lambda p: out["ev"][p])
    return out


def compute_matrix(all_signals):
    """全部月份的信號 → 矩陣 JSON（可直接 dump）。"""
    mature = [(s, m) for s in all_signals if (m := multiples(s)) is not None]
    cells = []
    for ivb in ("IV<50", "IV≥50"):
        for tier in ("lottery", "mid", "heavy"):
            for dteb in ("≤20", "21-45", "46-120", ">120"):
                rows = [(s, m) for s, m in mature
                        if iv_bucket(s.get("entry_iv")) == ivb and tier_of(s.get("entry_price")) == tier
                        and dte_bucket(_dte_of(s)) == dteb]
                summ = _summ(rows)
                cells.append({"iv": ivb, "tier": tier, "tier_label": TIER_LABEL[tier], "dte": dteb,
                              **(summ or {"n": 0, "events": 0}),
                              "status": ("可用" if summ and summ["n"] >= MATRIX_MIN_N
                                         else ("累積中" if summ else "無樣本"))})
    # 整體 + 規則 B + 逐月（三策略）
    def cohort(rows):
        return _summ(rows) or {"n": 0}
    rule_b = [(s, m) for s, m in mature if sig_structural_pass(s)]
    months = sorted({s["snapshot_date"][:7] for s, _ in mature})
    monthly = {}
    for mo in months:
        rows = [(s, m) for s, m in mature if s["snapshot_date"].startswith(mo)]
        summ = _summ(rows)
        monthly[mo] = {p: summ["ev_event_weighted"][p] for p in ("A_hold", "B_half2x", "C_bound")} if summ else {}
        monthly[mo]["n"] = len(rows)
    # 出樣本（預先登記日之後）
    oos = [(s, m) for s, m in mature if s["snapshot_date"] >= PREREG_DATE]
    oos_b = [(s, m) for s, m in oos if sig_structural_pass(s)]
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        "prereg_date": PREREG_DATE,
        "cost_factor": round(COST_FACTOR, 3),
        "min_n": MATRIX_MIN_N,
        "n_signals": len(all_signals), "n_mature": len(mature),
        "overall": cohort(mature), "rule_b": cohort(rule_b),
        "oos_all": cohort(oos), "oos_rule_b": cohort(oos_b),
        "monthly": monthly,
        "cells": cells,
        "policy_label": POLICY_LABEL,
    }


def render_matrix_md(mx):
    """給 SHADOWLOG 的一節（精簡版：三策略 + 矩陣主表）。"""
    md = "## 🧭 策略矩陣 shadow（預先登記 %s，三個月不改）\n\n" % mx["prereg_date"]
    md += ("> A 死抱 / B 2x賣半 / C 分類綁定（樂透∧IV<50 死抱；實彈 4口階梯；其餘 -50%%停+2x半）。"
           "EV＝等權平均倍數、未扣價差（×%.2f 為扣價差估計）；成熟＝T+5/10/20 三點都有價。"
           "完整 JSON：`data/strategy_matrix.json`\n\n" % mx["cost_factor"])
    md += "| 樣本 | n / 事件 | 命中 | A 死抱 | B 2x賣半 | C 分類綁定 |\n|---|---|---|---|---|---|\n"
    for name, key in (("全部成熟", "overall"), ("規則 B", "rule_b"),
                      ("出樣本（≥%s）" % mx["prereg_date"], "oos_all"), ("出樣本 規則 B", "oos_rule_b")):
        c = mx[key]
        if c.get("n", 0) == 0:
            md += f"| {name} | 0 | — | — | — | — |\n"
        else:
            md += (f"| {name} | {c['n']} / {c['events']} | {c['hit']:.0%} | {c['ev']['A_hold']:.2f} "
                   f"| {c['ev']['B_half2x']:.2f} | {c['ev']['C_bound']:.2f} |\n")
    md += "\n逐月（事件等權）：" + "；".join(
        f"{mo} n={v.get('n',0)} A {v.get('A_hold','—')} / B {v.get('B_half2x','—')} / C {v.get('C_bound','—')}"
        for mo, v in mx["monthly"].items()) + "\n\n"
    md += "| 分類 | n/事件 | 命中 | 死抱 | 2x半 | 3x半 | 4口階梯 | 停+2x半 | 最佳 | 狀態 |\n|---|---|---|---|---|---|---|---|---|---|\n"
    for c in mx["cells"]:
        if c["n"] == 0:
            continue
        ev = c["ev"]
        md += (f"| {c['iv']} {c['tier_label']} {c['dte']} | {c['n']}/{c['events']} | {c['hit']:.0%} "
               f"| {ev['A_hold']:.2f} | {ev['B_half2x']:.2f} | {ev['half3x']:.2f} | {ev['rungs248']:.2f} "
               f"| {ev['stop_half']:.2f} | {POLICY_LABEL[c['best']]} | {c['status']} |\n")
    md += ("\n_「累積中」＝n<%d，數字只是佔位；「可用」也僅為樣本內描述。100 筆出樣本前不改任何綁定。_\n\n"
           % mx["min_n"])
    return md
