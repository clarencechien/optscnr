"""
backfill_level.py — 一次性回填 spcx_options_history.csv 的判定欄

原 handoff（PLAN_2026-10_c_pool_alert §2.1）：`level` / `transition`。
patch 1（§3.5）：再加 `level_near` / `level_leaps` / `level_carry`（三條 gate 線各自會給的 level）、
`leaps_pctile` 等 leaps 欄、`min_carry_pct` 等 carry 欄、`gate_mode`、`carry_backfill_approx`。

重算邏輯直接用 spcx_options 的純函式（_iv_gate / evaluate_action_level / levels_by_mode / carry_of），不另寫一套：
- near：IV 序列＝spcx_iv_history.csv 截至當日（IV 歷史只增不改，截斷即重現當天 Sage 看到的分布）
- leaps：序列＝history 的 leaps_atm_iv 截至當日（Sage 上線起就有）
- carry：從 git 歷史逐 commit 抽當日 spcx_options.json 的 liquidity.detail（只有價差最窄前 5 名，
  算出的最小 carry 是近似值，標 carry_backfill_approx=True）；沒有 commit 的日子留空
- 觀點：viewpoint 的 updated 當生效日（之前 c4=False）
- level：按當時 config（gate_mode=near）＝ level_near；transition 從 level 序列算

驗證：--verify-git 把重算的 level 與 git 歷史裡每日 spcx_options.json 的 level 逐日比對（應零不符）。
用法：python spcx_radar/backfill_level.py [--dry-run] [--verify-git]
冪等：重跑結果相同；只動判定欄，其他欄位原樣。
"""
import argparse
import io
import json
import os
import subprocess
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import spcx_common  # noqa: E402
import spcx_options as so  # noqa: E402

REPO = os.path.dirname(HERE)
OPTIONS_JSON_REL = "spcx_radar/output/spcx_options.json"
HISTORY_REL = "spcx_radar/output/spcx_options_history.csv"
LEVEL_COLS = ["level", "transition", "leaps_pctile", "leaps_rel_calm", "leaps_abs_ok", "leaps_stable",
              "min_carry_pct", "carry_ok", "carry_stable", "gate_mode",
              "level_near", "level_leaps", "level_carry", "carry_backfill_approx"]


def viewpoint_effective_date():
    """讀 viewpoint 的 updated 當生效日；active 且信心達標才算。讀不到回 None（全程 c4=False）。"""
    try:
        vp = json.load(open(spcx_common.VIEWPOINT_PATH, encoding="utf-8"))
        if not vp.get("active") or int(vp.get("confidence", 0)) < so.VIEWPOINT_MIN_CONFIDENCE:
            return None
        if "（範例）" in vp.get("catalyst", "") or "（範例）" in vp.get("thesis", ""):
            return None
        return str(vp.get("updated", ""))[:10] or None
    except Exception:
        return None


def git_daily_options():
    """從 git 逐 commit 抽 {市場日: {level, price, detail}}。市場日＝該 commit 的 history 最後一列日期。"""
    try:
        shas = subprocess.check_output(["git", "log", "--format=%H", "--", OPTIONS_JSON_REL], cwd=REPO).decode().split()
    except Exception:
        return {}
    out = {}
    for sha in shas:
        try:
            j = json.loads(subprocess.check_output(["git", "show", f"{sha}:{OPTIONS_JSON_REL}"], cwd=REPO, stderr=subprocess.DEVNULL))
            csv_txt = subprocess.check_output(["git", "show", f"{sha}:{HISTORY_REL}"], cwd=REPO, stderr=subprocess.DEVNULL).decode()
        except subprocess.CalledProcessError:
            continue
        rows = list(pd.read_csv(io.StringIO(csv_txt))["date"].astype(str)) if csv_txt.strip() else []
        if not rows:
            continue
        d = max(rows)
        if d not in out:   # git log 由新到舊；同一市場日取最新的 commit
            out[d] = {"level": j.get("level"), "price": j.get("price"),
                      "detail": (j.get("liquidity") or {}).get("detail") or []}
    return out


def liquidity_from_row(row) -> dict:
    """用 history 已記的流動性欄重建 liquid 判定（與 get_liquidity_signal 同一組門檻）。"""
    total_int = int(row.get("total_int") or 0)
    total_vol = int(row.get("total_vol") or 0)
    usable = int(row.get("usable_strikes") or 0)
    return {"liquid": total_int >= so.LIQ_MIN_TOTAL_INT and total_vol >= so.LIQ_MIN_TOTAL_VOL and usable >= 1}


def backfill(dry_run=False, verify_git=False) -> pd.DataFrame:
    hist = pd.read_csv(spcx_common.OPTIONS_HISTORY_PATH).sort_values("date").reset_index(drop=True)
    hist["date"] = hist["date"].astype(str)
    iv_hist = pd.read_csv(spcx_common.IV_HISTORY_PATH)
    iv_hist["date"] = iv_hist["date"].astype(str)
    vp_date = viewpoint_effective_date()
    git_days = git_daily_options()
    print(f"viewpoint 生效日：{vp_date or '（無達標觀點，c4 全為 False）'}；git 可抽 {len(git_days)} 個市場日")

    cols = {c: [] for c in LEVEL_COLS}
    prev_level = None
    carry_prev = []   # 逐日 min_carry 序列（算 carry stable 用）
    for _, row in hist.iterrows():
        d = row["date"]
        atm_iv = row["atm_iv"] if pd.notna(row["atm_iv"]) else None
        near_series = [float(x) for x in iv_hist[iv_hist["date"] <= d]["atm_iv"].dropna()]
        iv_near = so._iv_gate(near_series, atm_iv, so.IV_PCTILE_CALM, so.IV_ABS_ACCEPTABLE, so.IV_STABLE_DAYS)
        leaps_iv = row.get("leaps_atm_iv")
        leaps_iv = float(leaps_iv) if pd.notna(leaps_iv) else None
        leaps_series = [float(x) for x in hist[hist["date"] <= d]["leaps_atm_iv"].dropna()]
        iv_leaps = so._iv_gate(leaps_series, leaps_iv, so.LEAPS_IV_PCTILE_CALM, so.LEAPS_IV_ABS_ACCEPTABLE, so.IV_STABLE_DAYS)
        # carry：git 裡當日的 detail（前 5 名近似）
        g = git_days.get(d)
        carry = {"min_carry_pct": None, "ok": False, "stable": False}
        approx = None
        if g and g["detail"] and g["price"]:
            vals = [c["carry_pct_annual"] for c in (so.carry_of(s, float(g["price"]), d) for s in g["detail"]) if c]
            if vals:
                mc = round(min(vals), 2)
                carry = {"min_carry_pct": mc, "ok": mc <= so.MAX_CARRY_PCT, "stable": False}
                recent = carry_prev[-(so.IV_STABLE_DAYS - 1):] if so.IV_STABLE_DAYS > 1 else []
                carry["stable"] = carry["ok"] and len(recent) >= so.IV_STABLE_DAYS - 1 and all(x <= so.MAX_CARRY_PCT for x in recent)
                approx = True
        carry_prev.append(carry["min_carry_pct"] if carry["min_carry_pct"] is not None else float("inf"))
        liq = liquidity_from_row(row)
        vp = {"passes": bool(vp_date and d >= vp_date)}
        levels = so.levels_by_mode(iv_near, liq, vp, iv_leaps, carry)
        level = levels["near"]   # 當時 config 一直是 near（＝現狀）
        transition = f"{prev_level}->{level}" if prev_level and prev_level != level else None
        prev_level = level
        for k, v in (("level", level), ("transition", transition), ("leaps_pctile", iv_leaps["pctile"]),
                     ("leaps_rel_calm", iv_leaps["rel_calm"]), ("leaps_abs_ok", iv_leaps["abs_acceptable"]),
                     ("leaps_stable", iv_leaps["stable"]), ("min_carry_pct", carry["min_carry_pct"]),
                     ("carry_ok", carry["ok"] if carry["min_carry_pct"] is not None else None),
                     ("carry_stable", carry["stable"] if carry["min_carry_pct"] is not None else None),
                     ("gate_mode", "near"), ("level_near", levels["near"]), ("level_leaps", levels["leaps"]),
                     ("level_carry", levels["carry"] if carry["min_carry_pct"] is not None else None),
                     ("carry_backfill_approx", approx)):
            cols[k].append(v)
    for k, v in cols.items():
        hist[k] = v

    # 摘要
    for m in ("level", "level_near", "level_leaps", "level_carry"):
        print(f"  {m:12s} L2={int((hist[m] == 'L2').sum()):3d}  L1={int((hist[m] == 'L1').sum()):3d}  L0={int((hist[m] == 'L0').sum()):3d}")
    print(f"  transition 非空 {int(hist['transition'].notna().sum())} 列；carry 有值 {int(hist['min_carry_pct'].notna().sum())} 列")
    segs, start, prev_d = [], None, None
    for d, lv in zip(hist["date"], hist["level"]):
        if lv == "L2" and start is None:
            start = d
        elif lv != "L2" and start is not None:
            segs.append((start, prev_d)); start = None
        prev_d = d
    if start is not None:
        segs.append((start, prev_d))
    print("  L2 段：" + "；".join(f"{s}→{e}" for s, e in segs))
    print("  轉換：" + "；".join(f"{d} {t}" for d, t in zip(hist["date"], hist["transition"]) if isinstance(t, str)))

    if verify_git:
        bad = [(d, g["level"], lv) for d, lv in zip(hist["date"], hist["level"])
               if (g := git_days.get(d)) and g["level"] in ("L0", "L1", "L2") and g["level"] != lv]
        print(f"  git 比對：{sum(1 for d in hist['date'] if d in git_days)} 日可比，不符 {len(bad)} 日 {bad[:10]}")

    if not dry_run:
        hist.to_csv(spcx_common.OPTIONS_HISTORY_PATH, index=False)
        print(f"💾 已寫回 {spcx_common.OPTIONS_HISTORY_PATH}")
    return hist


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify-git", action="store_true")
    args = ap.parse_args()
    backfill(dry_run=args.dry_run, verify_git=args.verify_git)
