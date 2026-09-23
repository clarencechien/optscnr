#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
casino_tracker.py — 賭場 sector：台股 AI 個股影子追蹤器（先收資料，不做規則）
==============================================================================
定位（2026-09-12 使用者拍板）：拉斯維加斯小部位。**這裡沒有訊號、沒有期望值宣稱。**
它做三件事，全部只記錄：
  1. 每個交易日對名單裡每檔記特徵：收盤、20 日報酬、對 0050 超額、月營收 YoY / 3 月均 / 斜率。
  2. 回填 T+5/10/20 個股報酬與對 0050 超額（append-only state，之後才能問「月營收加速有沒有用」）。
  3. 影子 DCA：每月固定金額等權買整籃（零股），同一筆錢對照買 0050。
  4. 借券欄位（2026-09-23 加，只收資料）：借券賣出餘額、20 日變化、一年分位、回補天數、借券費率、融券餘額。
     台灣大型股借券多為避險／套利，不等於看空；這裡只記，不做規則、不進判準。

判準寫死在 config `verdict_rule`；未達門檻前報告一律印「累積中」。
資料源 FinMind（TaiwanStockPrice / TaiwanStockMonthRevenue / TaiwanDailyShortSaleBalances / TaiwanStockSecuritiesLending），
快取進版控；抓不到用快取、快取沒有 → NO_DATA（借券缺值只讓借券欄位為空，不影響其他特徵）。
Usage:
  python casino_tracker.py [--output-dir tw_scanner/output] [--no-fetch]
  python casino_tracker.py --selftest
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
from splits import resolve as resolve_splits  # noqa: E402


# ----------------------------------------------------------------------------
# 快取（增量、冪等）
# ----------------------------------------------------------------------------

def _load(path):
    if not os.path.exists(path):
        return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return None


def _save(path, obj):
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False)


def _finmind_df(dataset: str, data_id: str, start: str):
    from tw_scanner import finmind
    tw_cfg = json.load(open(os.path.join(HERE, "config", "tw_scanner_config.json"), encoding="utf-8"))
    return finmind(dataset, tw_cfg, data_id=data_id, start=start)


def fetch_prices(cfg: dict, ticker: str, start: str) -> dict:
    df = _finmind_df(cfg["prices"]["dataset"], ticker, start)
    c_close = "close" if "close" in df.columns else "Close"
    out = {}
    for d, c in zip(df["date"], df[c_close]):
        try:
            out[str(d)[:10]] = float(c)
        except (TypeError, ValueError):
            pass
    return out


def fetch_revenue(cfg: dict, ticker: str, start: str) -> dict:
    """→ {"YYYY-MM": revenue}（revenue_year/revenue_month 是營收所屬月）。"""
    df = _finmind_df(cfg["revenue"]["dataset"], ticker, start)
    out = {}
    for _, r in df.iterrows():
        try:
            out[f"{int(r['revenue_year']):04d}-{int(r['revenue_month']):02d}"] = float(r["revenue"])
        except (TypeError, ValueError, KeyError):
            pass
    return out


def update_caches(cfg: dict, out_dir: str, fetch: bool, fetch_px=fetch_prices, fetch_rev=fetch_revenue):
    """回 (prices{ticker:{date:close}}, revenue{ticker:{ym:rev}}, warnings[])。"""
    px_path = os.path.join(out_dir, cfg["prices"]["cache"])
    rv_path = os.path.join(out_dir, cfg["revenue"]["cache"])
    prices = (_load(px_path) or {}).get("data") or {}
    revenue = (_load(rv_path) or {}).get("data") or {}
    warns = []
    if not fetch:
        return prices, revenue, (["--no-fetch"] if not prices else [])
    tickers = [u["ticker"] for u in cfg["universe"]] + [cfg["benchmark"]]
    # 0050 若 dca_ledger 已有快取，直接借用（省 FinMind 額度、序列一致）
    dca = _load(os.path.join(out_dir, "dca_prices.json"))
    if dca and dca.get("instrument") == cfg["benchmark"] and dca.get("closes"):
        prices.setdefault(cfg["benchmark"], {}).update({k: float(v) for k, v in dca["closes"].items()})
    for t in tickers:
        have = prices.get(t) or {}
        tail = ((dt.date.fromisoformat(max(have)) - dt.timedelta(days=cfg["prices"]["refetch_tail_days"])).isoformat()
                if have else cfg["history_start"])
        try:
            have.update(fetch_px(cfg, t, tail))
            prices[t] = have
        except Exception as e:
            warns.append(f"price {t}: {type(e).__name__}: {e}")
        if t == cfg["benchmark"]:
            continue
        hr = revenue.get(t) or {}
        if hr:
            last = max(hr)
            y, m = int(last[:4]), int(last[5:7]) - int(cfg["revenue"]["refetch_months"])
            while m <= 0:
                y, m = y - 1, m + 12
            rstart = f"{y:04d}-{m:02d}-01"
        else:
            rstart = (dt.date.fromisoformat(cfg["history_start"]) - dt.timedelta(days=400)).isoformat()
        try:
            hr.update(fetch_rev(cfg, t, rstart))
            revenue[t] = hr
        except Exception as e:
            warns.append(f"revenue {t}: {type(e).__name__}: {e}")
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    _save(px_path, {"updated_at": now, "data": prices})
    _save(rv_path, {"updated_at": now, "data": revenue})
    return prices, revenue, warns


# ----------------------------------------------------------------------------
# 借券（只收資料）：快取 casino_sbl.json = {ticker: {"bal": {date: {sbl, margin_short}}, "vol": {date: shares},
#                                                   "fee": {date: [fee_rate...]}}}；股數皆為「股」（未分割還原）
# ----------------------------------------------------------------------------

def fetch_sbl(cfg: dict, ticker: str, start: str) -> dict:
    """→ {"bal": {date: {"sbl": 借券賣出餘額股, "margin_short": 融券餘額股}}, "vol": {date: 成交股數}, "fee": {date: [費率%]}}。
    三個來源各自失敗各自降級（空 dict），整檔全空才丟例外。"""
    sc = cfg["sbl"]
    out = {"bal": {}, "vol": {}, "fee": {}}
    errs = []
    try:
        df = _finmind_df(sc["balance_dataset"], ticker, start)
        for _, r in df.iterrows():
            try:
                out["bal"][str(r["date"])[:10]] = {"sbl": float(r["SBLShortSalesCurrentDayBalance"]),
                                                    "margin_short": float(r["MarginShortSalesCurrentDayBalance"])}
            except (TypeError, ValueError, KeyError):
                pass
    except Exception as e:
        errs.append(f"balance {type(e).__name__}: {e}")
    try:
        df = _finmind_df(cfg["prices"]["dataset"], ticker, start)
        vc = "Trading_Volume" if "Trading_Volume" in df.columns else None
        if vc:
            for d, v in zip(df["date"], df[vc]):
                try:
                    out["vol"][str(d)[:10]] = float(v)
                except (TypeError, ValueError):
                    pass
    except Exception as e:
        errs.append(f"volume {type(e).__name__}: {e}")
    fee_start = max(start, (dt.date.today() - dt.timedelta(days=int(sc["fee_lookback_days"]))).isoformat())
    try:
        df = _finmind_df(sc["lending_dataset"], ticker, fee_start)
        for _, r in df.iterrows():
            try:
                out["fee"].setdefault(str(r["date"])[:10], []).append(float(r["fee_rate"]))
            except (TypeError, ValueError, KeyError):
                pass
    except Exception as e:
        # 借券成交明細在某些日子／標的本來就是空的（沒人借）——不當錯誤，只記
        if "empty" not in str(e):
            errs.append(f"lending {type(e).__name__}: {e}")
    if not out["bal"] and not out["vol"]:
        raise RuntimeError("; ".join(errs) or "no data")
    return out


def update_sbl_cache(cfg: dict, out_dir: str, fetch: bool, fetch_fn=fetch_sbl) -> tuple[dict, list[str]]:
    path = os.path.join(out_dir, cfg["sbl"]["cache"])
    data = (_load(path) or {}).get("data") or {}
    if not fetch:
        return data, []
    warns = []
    for u in cfg["universe"]:
        t = u["ticker"]
        have = data.get(t) or {"bal": {}, "vol": {}, "fee": {}}
        last = max(have["bal"]) if have.get("bal") else None
        start = ((dt.date.fromisoformat(last) - dt.timedelta(days=int(cfg["sbl"]["refetch_tail_days"]))).isoformat()
                 if last else cfg["sbl"]["history_start"])
        try:
            new = fetch_fn(cfg, t, start)
            for k in ("bal", "vol", "fee"):
                have.setdefault(k, {}).update(new.get(k) or {})
            data[t] = have
        except Exception as e:
            warns.append(f"借券 {t}: {type(e).__name__}: {e}")
    _save(path, {"updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "data": data})
    return data, warns


def _share_factor(splits: list[dict], ticker: str, date: str) -> float:
    """股數類序列的分割還原係數：分割日之前的股數 ×ratio（與價格 ÷ratio 對稱）。"""
    f = 1.0
    for sp in splits or []:
        if sp.get("ticker") == ticker and date < sp["date"]:
            f *= float(sp["ratio"])
    return f


def _series_jumps_at(series: list[tuple], split: dict) -> bool:
    """股數序列在分割日有沒有真的跳 ×ratio（資料是原始股數）還是平順（資料已是同一單位）。

    2026-09-23 實測：成交量（TaiwanStockPrice）是原始股數，分割日跳 ×ratio；但借券賣出餘額
    （TaiwanDailyShortSaleBalances）在緯穎 2026-09-02 三拆一當天「前日餘額」=前一天餘額、調整 0、額度也沒跳，
    整段序列已是同一單位——若照 config 再 ×3 會把 20 日變化算成 −51%（實為 +46%）。
    0050 2025-06-18 則是分割前借券全數了結（餘額 0）後重來。所以逐次看資料：分割前後比值在對數上
    較接近 ratio → 原始股數、要換算；較接近 1 或分割前為 0 → 不換算。"""
    k = float(split["ratio"])
    before = next((v for d, v in reversed(series) if d < split["date"]), None)
    after = next((v for d, v in series if d >= split["date"]), None)
    if not before or not after or before <= 0 or after <= 0:
        return False
    r = math.log(after / before)
    return abs(r - math.log(k)) < abs(r)


def sbl_features(entry: Optional[dict], today: str, splits: list[dict], ticker: str, cfg: dict) -> dict:
    """借券欄位（純函數）。缺資料 → 各欄 None。股數先依分割還原再比較。"""
    sc = cfg["sbl"]
    empty = {"sbl_date": None, "sbl_lots": None, "sbl_chg20_pct": None, "sbl_pctile_1y": None,
             "sbl_days_to_cover": None, "sbl_fee_median_pct": None, "sbl_fee_n": 0, "margin_short_lots": None}
    if not entry or not entry.get("bal"):
        return empty
    bal = sorted((d, v) for d, v in entry["bal"].items() if d <= today)
    if not bal:
        return empty
    # 借券餘額：只對「資料在分割日真的有跳」的那幾次分割換算（見 _series_jumps_at）；融券只報當日水位，不需換算
    raw_sbl = [(d, v["sbl"]) for d, v in bal]
    sbl_splits = [sp for sp in (splits or []) if sp.get("ticker") == ticker and _series_jumps_at(raw_sbl, sp)]
    adj = [(d, v["sbl"] * _share_factor(sbl_splits, ticker, d), v["margin_short"]) for d, v in bal]
    d0, sbl0, ms0 = adj[-1]
    w = int(cfg["features"]["return_window_sessions"])
    chg = None
    if len(adj) > w and adj[-1 - w][1] > 0:
        chg = round((sbl0 / adj[-1 - w][1] - 1) * 100, 1)
    win = [x[1] for x in adj[-int(sc["pctile_window_sessions"]):]]
    pct = round(sum(v <= sbl0 for v in win) / len(win) * 100) if len(win) >= int(sc["pctile_min_sessions"]) else None
    vols = [v * _share_factor(splits, ticker, d) for d, v in sorted((entry.get("vol") or {}).items()) if d <= d0][-w:]
    dtc = round(sbl0 / (sum(vols) / len(vols)), 2) if len(vols) >= min(w, 10) and sum(vols) > 0 else None
    since = (dt.date.fromisoformat(d0) - dt.timedelta(days=int(sc["fee_window_days"]))).isoformat()
    fees = sorted(f for d, fs in (entry.get("fee") or {}).items() if since < d <= d0 for f in fs)
    med = None
    if fees:
        n = len(fees)
        med = round(fees[n // 2] if n % 2 else (fees[n // 2 - 1] + fees[n // 2]) / 2, 3)
    return {"sbl_date": d0, "sbl_lots": round(sbl0 / 1000, 1), "sbl_chg20_pct": chg, "sbl_pctile_1y": pct,
            "sbl_days_to_cover": dtc, "sbl_fee_median_pct": med, "sbl_fee_n": len(fees),
            "margin_short_lots": round(ms0 / 1000, 1)}


# ----------------------------------------------------------------------------
# 特徵（純函數）
# ----------------------------------------------------------------------------

def _ret(series: list[tuple], i: int, n: int) -> Optional[float]:
    if i - n < 0 or series[i - n][1] in (None, 0):
        return None
    return round((series[i][1] / series[i - n][1] - 1) * 100, 2)


def revenue_features(rev: dict, k: int) -> dict:
    """最新月 YoY、k 月均 YoY、YoY 斜率（pp/月，近 k 月線性）。資料缺 → None。"""
    if not rev:
        return {"latest_month": None, "yoy_pct": None, "yoy_avg_pct": None, "yoy_slope_pp": None}
    months = sorted(rev)
    yoy = {}
    for ym in months:
        y, m = int(ym[:4]), int(ym[5:7])
        prev = f"{y-1:04d}-{m:02d}"
        if rev.get(prev):
            yoy[ym] = (rev[ym] / rev[prev] - 1) * 100
    if not yoy:
        return {"latest_month": months[-1], "yoy_pct": None, "yoy_avg_pct": None, "yoy_slope_pp": None}
    ms = sorted(yoy)[-k:]
    vals = [yoy[m] for m in ms]
    slope = None
    if len(vals) >= 2:
        n = len(vals)
        xm, ym_ = (n - 1) / 2, sum(vals) / n
        slope = sum((i - xm) * (v - ym_) for i, v in enumerate(vals)) / sum((i - xm) ** 2 for i in range(n))
    return {"latest_month": ms[-1], "yoy_pct": round(vals[-1], 1),
            "yoy_avg_pct": round(sum(vals) / len(vals), 1),
            "yoy_slope_pp": None if slope is None else round(slope, 2)}


def adjust_all(cfg: dict, prices: dict) -> tuple[dict, list[dict], list[str]]:
    """每檔（含基準）分割還原；回 (還原後 prices, 採用的分割清單, 警告)。零價一律剔除。"""
    out, used, warns = {}, [], []
    for t, ser in (prices or {}).items():
        adj, sp, w = resolve_splits(ser, cfg.get("splits"), t)
        out[t] = adj
        used += [{"ticker": t, **s} for s in sp]
        warns += w
    return out, used, warns


def repair_features(cfg: dict, state_path: str, prices: dict) -> int:
    """用還原後價格重算 state 裡的衍生欄位（ret/excess）。

    這些欄位是價格的推導物，不是預測；分割未還原造成的錯值屬機械性錯誤，
    同 CONTEXT §六「資料還原不是竄改」。只改有差的欄位，回傳筆數。
    """
    hist = _load(state_path) or []
    if not hist:
        return 0
    w = int(cfg["features"]["return_window_sessions"])
    bench = sorted((prices.get(cfg["benchmark"]) or {}).items())
    changed = 0
    for e in hist:
        ser = sorted((prices.get(e["ticker"]) or {}).items())
        i = next((j for j in range(len(ser) - 1, -1, -1) if ser[j][0] <= e["date"]), None)
        if i is None:
            continue
        r = _ret(ser, i, w)
        bi = next((j for j in range(len(bench) - 1, -1, -1) if bench[j][0] <= e["date"]), None)
        b = _ret(bench, bi, w) if bi is not None else None
        new = {f"ret{w}_pct": r, f"excess{w}_pct": None if r is None or b is None else round(r - b, 2),
               "close": ser[i][1]}
        if any(e.get(k) != v for k, v in new.items()):
            e.update(new)
            e["features_repaired"] = True
            changed += 1
    if changed:
        _save(state_path, hist)
    return changed


def scan(cfg: dict, prices: dict, revenue: dict, today: str, sbl: Optional[dict] = None) -> list[dict]:
    """每檔一筆（今天或之前最後一個交易日）。缺價格 → 該檔 NO_DATA 一筆。"""
    w = int(cfg["features"]["return_window_sessions"])
    k = int(cfg["features"]["revenue_avg_months"])
    bench = sorted((d, c) for d, c in (prices.get(cfg["benchmark"]) or {}).items() if d <= today)
    rows = []
    for u in cfg["universe"]:
        t = u["ticker"]
        ser = sorted((d, c) for d, c in (prices.get(t) or {}).items() if d <= today)
        if not ser:
            rows.append({"ticker": t, "name": u["name"], "bucket": u["bucket"], "date": today,
                         "status": "NO_DATA", "reason": "no price"})
            continue
        d, close = ser[-1]
        i = len(ser) - 1
        r20 = _ret(ser, i, w)
        bi = next((j for j in range(len(bench) - 1, -1, -1) if bench[j][0] <= d), None)
        b20 = _ret(bench, bi, w) if bi is not None else None
        rows.append({"ticker": t, "name": u["name"], "bucket": u["bucket"], "in_0050": u.get("in_0050"),
                     "date": d, "status": "OK", "close": close,
                     f"ret{w}_pct": r20,
                     f"excess{w}_pct": None if r20 is None or b20 is None else round(r20 - b20, 2),
                     **revenue_features(revenue.get(t) or {}, k),
                     **sbl_features((sbl or {}).get(t), d, cfg.get("_splits_used") or [], t, cfg)})
    return rows


# ----------------------------------------------------------------------------
# state（append-only）+ 回填
# ----------------------------------------------------------------------------

def append_scan(state_path: str, rows: list[dict]) -> int:
    hist = _load(state_path) or []
    seen = {(e["ticker"], e["date"]) for e in hist}
    added = 0
    for r in rows:
        if r.get("status") != "OK" or (r["ticker"], r["date"]) in seen:
            continue
        hist.append({**r, "outcomes": {}})
        added += 1
    if added:
        _save(state_path, hist)
    return added


def _fwd(series: list[tuple], date: str, n: int) -> Optional[float]:
    dates = [d for d, _ in series]
    i = next((j for j, d in enumerate(dates) if d >= date), None)
    if i is None or i + n >= len(series) or not series[i][1]:
        return None
    return round((series[i + n][1] / series[i][1] - 1) * 100, 2)


def backfill(state_path: str, prices: dict, bench_id: str, horizons: list[int]) -> int:
    hist = _load(state_path) or []
    bench = sorted((prices.get(bench_id) or {}).items())
    changed = 0
    for e in hist:
        ser = sorted((prices.get(e["ticker"]) or {}).items())
        o = dict(e.get("outcomes") or {})
        for n in horizons:
            if o.get(f"t{n}_ret_pct") is not None:
                continue
            r = _fwd(ser, e["date"], n)
            b = _fwd(bench, e["date"], n)
            if r is not None:
                o[f"t{n}_ret_pct"] = r
                o[f"t{n}_excess_pct"] = None if b is None else round(r - b, 2)
                changed += 1
        e["outcomes"] = o
    if changed:
        _save(state_path, hist)
    return changed


def tercile_table(hist: list[dict], horizon: int, min_n: int) -> dict:
    """月營收 3 月均 YoY 前／後三分之一 vs 全部：T+h 超額均值（只印，不裁決）。"""
    key = f"t{horizon}_excess_pct"
    rows = [e for e in hist if (e.get("outcomes") or {}).get(key) is not None and e.get("yoy_avg_pct") is not None]
    if len(rows) < 3:
        return {"n": len(rows), "status": "累積中"}
    rows.sort(key=lambda e: e["yoy_avg_pct"])
    k = len(rows) // 3
    lo, hi = rows[:k], rows[-k:]

    def avg(xs):
        return round(sum(e["outcomes"][key] for e in xs) / len(xs), 2) if xs else None
    ok = len(lo) >= min_n and len(hi) >= min_n
    return {"n": len(rows), "horizon": horizon,
            "top_tercile": {"n": len(hi), "excess_avg": avg(hi)},
            "bottom_tercile": {"n": len(lo), "excess_avg": avg(lo)},
            "all_avg": avg(rows),
            "status": ("可讀（n 達門檻）" if ok else f"累積中（每側需 n≥{min_n}）")}


# ----------------------------------------------------------------------------
# 影子 DCA：等權籃子 vs 同一筆錢買 0050
# ----------------------------------------------------------------------------

def shadow_dca(cfg: dict, prices: dict, today: str) -> dict:
    sd = cfg["shadow_dca"]
    bench_id = cfg["benchmark"]
    tickers = [u["ticker"] for u in cfg["universe"] if prices.get(u["ticker"])]
    if not tickers or not prices.get(bench_id):
        return {"status": "NO_DATA"}
    all_dates = sorted(set().union(*[set(prices[t]) for t in tickers]) | set(prices[bench_id]))
    all_dates = [d for d in all_dates if cfg["history_start"] <= d <= today]
    if not all_dates:
        return {"status": "NO_DATA"}
    fee = sd["fee_rate"] * sd.get("fee_discount", 1.0)
    amt = float(sd["amount_twd_month"])
    # 買日：每月 buy_day 後第一個所有標的都有價的交易日
    y, m = int(all_dates[0][:4]), int(all_dates[0][5:7])
    buys = []
    end = dt.date.fromisoformat(today)
    while dt.date(y, m, 1) <= end:
        target = f"{y:04d}-{m:02d}-{sd['buy_day_of_month']:02d}"
        d = next((x for x in all_dates if x >= target and all(x in prices[t] for t in tickers) and x in prices[bench_id]), None)
        if d and d[:7] == f"{y:04d}-{m:02d}":
            buys.append(d)
        m += 1
        if m > 12:
            y, m = y + 1, 1
    units = {t: 0.0 for t in tickers}
    bench_units = 0.0
    invested = 0.0
    for d in buys:
        per = amt / len(tickers)
        for t in tickers:
            units[t] += per * (1 - fee) / prices[t][d]
        bench_units += amt * (1 - fee) / prices[bench_id][d]
        invested += amt
    last = {t: prices[t][max(k for k in prices[t] if k <= today)] for t in tickers}
    bl = prices[bench_id][max(k for k in prices[bench_id] if k <= today)]
    value = sum(units[t] * last[t] for t in tickers)
    bvalue = bench_units * bl
    per_ticker = {t: round((units[t] * last[t]) / (invested / len(tickers)) * 100 - 100, 1) for t in tickers} if invested else {}
    return {"status": "OK", "n_months": len(buys), "first_buy": buys[0] if buys else None,
            "last_buy": buys[-1] if buys else None, "invested": round(invested, 0),
            "basket_value": round(value, 0), "basket_return_pct": round((value / invested - 1) * 100, 2) if invested else None,
            "bench_value": round(bvalue, 0), "bench_return_pct": round((bvalue / invested - 1) * 100, 2) if invested else None,
            "basket_minus_bench_pp": round((value - bvalue) / invested * 100, 2) if invested else None,
            "per_ticker_return_pct": per_ticker, "n_tickers": len(tickers)}


# ----------------------------------------------------------------------------
# 報告
# ----------------------------------------------------------------------------

def _f(x, u="", s=True):
    return "—" if x is None else (f"{x:+.1f}{u}" if s else f"{x:.1f}{u}")


def build_summary(cfg: dict, rows: list[dict], hist: list[dict], dca: dict, warns: list[str], today: str) -> dict:
    vr = cfg["verdict_rule"]
    ok_rows = [r for r in rows if r.get("status") == "OK"]
    ok_rows.sort(key=lambda r: (r.get("yoy_avg_pct") is None, -(r.get("yoy_avg_pct") or 0)))
    basket_ok = dca.get("status") == "OK" and dca.get("n_months", 0) >= vr["min_months_basket"]
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "today": today, "benchmark": cfg["benchmark"], "n_universe": len(cfg["universe"]),
        "splits": cfg.get("_splits_used") or [],
        "rows": ok_rows, "no_data": [r for r in rows if r.get("status") != "OK"],
        "state_n": len(hist), "scored_n": sum(1 for e in hist if (e.get("outcomes") or {}).get("t20_excess_pct") is not None),
        "tercile_t20": tercile_table(hist, 20, vr["min_n_per_tercile"]),
        "shadow_dca": dca,
        "verdict": {"basket": ("可讀" if basket_ok else f"累積中（需 ≥{vr['min_months_basket']} 個月，現 {dca.get('n_months', 0)}）"),
                    "rule": vr["_note"]},
        "warnings": warns,
        "note": "賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。",
    }


def render_md(s: dict) -> str:
    L = [f"# 🎰 賭場 sector — AI 個股影子追蹤（{s['today']}）", "",
         f"> {s['note']} 基準 {s['benchmark']}。判準：{s['verdict']['rule']}", ""]
    L += ["| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in s["rows"]:
        L.append(f"| {r['ticker']} | {r['name']} | {r['bucket']} | {'✓' if r.get('in_0050') else ''} | {r['close']} "
                 f"| {_f(r.get('ret20_pct'), '%')} | {_f(r.get('excess20_pct'), '%')} | {_f(r.get('yoy_pct'), '%')} "
                 f"| {_f(r.get('yoy_avg_pct'), '%')} | {_f(r.get('yoy_slope_pp'))} |")
    if s["no_data"]:
        L.append("")
        L.append("NO_DATA：" + "、".join(f"{r['ticker']}（{r.get('reason')}）" for r in s["no_data"]))
    if any(r.get("sbl_lots") is not None for r in s["rows"]):
        L += ["", "## 借券（只收資料，不是訊號）", "",
              "> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。"
              "較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。", "",
              "| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |",
              "|---|---|---|---|---|---|---|"]
        for r in s["rows"]:
            if r.get("sbl_lots") is None:
                continue
            fee = "—" if r.get("sbl_fee_median_pct") is None else f"{r['sbl_fee_median_pct']:.2f}%（{r['sbl_fee_n']} 筆）"
            pct = "—" if r.get("sbl_pctile_1y") is None else str(r["sbl_pctile_1y"])
            dtc = "—" if r.get("sbl_days_to_cover") is None else f"{r['sbl_days_to_cover']:.1f}"
            ms = "—" if r.get("margin_short_lots") is None else f"{r['margin_short_lots']:,.0f}"
            L.append(f"| {r['ticker']} | {r['sbl_lots']:,.0f} | {_f(r.get('sbl_chg20_pct'), '%')} | {pct} | {dtc} | {fee} | {ms} |")
    d = s["shadow_dca"]
    L += ["", "## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050", ""]
    if d.get("status") == "OK":
        L += [f"- {d['first_buy']} 起 {d['n_months']} 個月、投入 {d['invested']:,.0f} 元（{d['n_tickers']} 檔等權）",
              f"- 籃子市值 {d['basket_value']:,.0f}（{_f(d['basket_return_pct'], '%')}）；0050 市值 {d['bench_value']:,.0f}（{_f(d['bench_return_pct'], '%')}）；差 **{_f(d['basket_minus_bench_pp'], ' pp')}**",
              f"- 判準狀態：{s['verdict']['basket']}"]
    else:
        L.append("NO_DATA")
    t = s["tercile_t20"]
    L += ["", "## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）", ""]
    if t.get("horizon"):
        L += [f"- 前三分之一 n={t['top_tercile']['n']} 超額 {_f(t['top_tercile']['excess_avg'], '%')}；"
              f"後三分之一 n={t['bottom_tercile']['n']} 超額 {_f(t['bottom_tercile']['excess_avg'], '%')}；全部 {_f(t['all_avg'], '%')}",
              f"- 狀態：{t['status']}（state {s['state_n']} 筆、已回填 T+20 {s['scored_n']} 筆）"]
    else:
        L.append(f"- 累積中（state {s['state_n']} 筆、已回填 T+20 {s['scored_n']} 筆）")
    if s.get("splits"):
        L += ["", "分割還原：" + "、".join(f"{x['ticker']} {x['date']} ×{x['ratio']:g}（{x['source']}）" for x in s["splits"])]
    if s["warnings"]:
        L += ["", "警告／降級：", ""] + [f"- ⚠️ {w}" for w in s["warnings"]]
    L += ["", "---", "*casino_tracker — 只收資料。名單不是訊號、籃子不是建議；期望值未證明前，這筆錢是娛樂預算。*"]
    return "\n".join(L)


# ----------------------------------------------------------------------------
# selftest
# ----------------------------------------------------------------------------

def _fixtures(cfg: dict):
    import random
    rnd = random.Random(5)
    tickers = [u["ticker"] for u in cfg["universe"]] + [cfg["benchmark"]]
    prices, revenue = {}, {}
    for t in tickers:
        px = 100.0 + rnd.random() * 500
        d = dt.date(2024, 1, 2)
        ser = {}
        drift = 0.0006 if t != cfg["benchmark"] else 0.0004
        while d <= dt.date(2026, 9, 11):
            if d.weekday() < 5:
                px *= math.exp(rnd.gauss(drift, 0.015))
                ser[d.isoformat()] = round(px, 2)
                if t == cfg["benchmark"] and d.isoformat() >= "2025-06-18":
                    ser[d.isoformat()] = round(px / 4, 2)     # 合成 0050 四拆一（未還原資料的樣子）
                if t == "2330" and d.isoformat() >= "2026-08-05":
                    ser[d.isoformat()] = round(px / 4, 2)     # 合成個股四拆一，落在 20 日窗內（測 state 修復）
            d += dt.timedelta(days=1)
        prices[t] = ser
        if t != cfg["benchmark"]:
            g = 1.0 + rnd.random() * 0.04
            base = 1e9
            revenue[t] = {f"{2023 + (i // 12):04d}-{(i % 12) + 1:02d}": base * (g ** i) for i in range(0, 32)}
    return prices, revenue


def _sbl_fixtures(cfg: dict, prices: dict) -> dict:
    """合成借券資料：股數未還原（2330 在 2026-08-05 四拆一後股數 ×4），費率只放在 2308 最近幾天。"""
    import random
    rnd = random.Random(11)
    out = {}
    for u in cfg["universe"]:
        t = u["ticker"]
        bal, vol, fee = {}, {}, {}
        base = 5e6 + rnd.random() * 5e6
        for d in sorted(prices.get(t) or {}):
            if d < cfg["sbl"]["history_start"]:
                continue
            base *= math.exp(rnd.gauss(0, 0.01))
            k = 4.0 if (t == "2330" and d >= "2026-08-05") else 1.0
            bal[d] = {"sbl": round(base * k), "margin_short": round(base * 0.01 * k)}
            vol[d] = round(base * 1.5 * k)
        if t == "2308":
            fee = {"2026-08-13": [0.2, 0.3], "2026-08-14": [0.5], "2026-01-02": [9.9]}
        out[t] = {"bal": bal, "vol": vol, "fee": fee}
    return out


def selftest(cfg: dict) -> bool:
    out = tempfile.mkdtemp(prefix="casino_selftest_")
    prices, revenue = _fixtures(cfg)
    ok = True

    def check(c, msg):
        nonlocal ok
        print(("  ✅ " if c else "  ❌ ") + msg, file=sys.stderr)
        ok = ok and bool(c)

    today = "2026-08-15"
    raw_prices = prices
    prices, used, warns_sp = adjust_all(cfg, prices)
    check(any(u["ticker"] == cfg["benchmark"] and u["ratio"] == 4.0 for u in used), "基準的合成四拆一被還原")
    rows = scan(cfg, prices, revenue, today)
    check(len(rows) == len(cfg["universe"]) and all(r["status"] == "OK" for r in rows), "每檔一筆特徵")
    check(all(r["yoy_pct"] is not None and r["yoy_slope_pp"] is not None for r in rows), "月營收 YoY / 斜率有值")
    sp = os.path.join(out, "casino_state.json")
    n1 = append_scan(sp, rows)
    n2 = append_scan(sp, rows)
    check(n1 == len(rows) and n2 == 0, "state append-only、同日冪等")
    ch = backfill(sp, prices, cfg["benchmark"], cfg["outcomes"]["horizons"])
    hist = _load(sp)
    check(ch == len(rows) * 3 and all(hist[0]["outcomes"].get(f"t{n}_excess_pct") is not None for n in (5, 10, 20)),
          "T+5/10/20 回填含對 0050 超額")
    check(backfill(sp, prices, cfg["benchmark"], cfg["outcomes"]["horizons"]) == 0, "回填冪等")
    d = shadow_dca(cfg, prices, today)
    check(d["status"] == "OK" and d["n_months"] >= 30 and d["basket_minus_bench_pp"] is not None, f"影子 DCA {d.get('n_months')} 個月、有對照差")
    d_raw = shadow_dca(cfg, raw_prices, today)
    check(d_raw["bench_return_pct"] < d["bench_return_pct"] - 30, f"未還原 vs 還原：基準報酬差距明顯（{d_raw['bench_return_pct']} vs {d['bench_return_pct']}）")
    # repair：用原始價寫進 state 的衍生欄位，還原後重算應被修正
    sp2 = os.path.join(out, "casino_state_raw.json")
    append_scan(sp2, scan(cfg, raw_prices, revenue, today))
    n_rep = repair_features(cfg, sp2, prices)
    check(n_rep > 0 and all(e.get("features_repaired") for e in _load(sp2) if e["ticker"] == "2330"), f"state 衍生欄位修復 {n_rep} 筆")
    s = build_summary(cfg, rows, hist, d, [], today)
    check(s["tercile_t20"]["status"].startswith("累積中"), "三分位表未達門檻 → 累積中")
    md = render_md(s)
    check("賭場 sector" in md and "影子 DCA" in md and "累積中" in md, "報告段落齊全")
    # 借券欄位（只收資料）
    sbl_fx = _sbl_fixtures(cfg, prices)
    cfg_s = {**cfg, "_splits_used": used}
    rows_s = scan(cfg_s, prices, revenue, today, sbl_fx)
    r30 = next(r for r in rows_s if r["ticker"] == "2330")
    r08 = next(r for r in rows_s if r["ticker"] == "2308")
    check(r08["sbl_lots"] is not None and r08["sbl_pctile_1y"] is not None and r08["sbl_days_to_cover"] is not None
          and r08["margin_short_lots"] is not None, f"借券欄位有值（2308 餘額 {r08['sbl_lots']} 張、分位 {r08['sbl_pctile_1y']}、回補 {r08['sbl_days_to_cover']} 天）")
    check(r08["sbl_fee_median_pct"] == 0.3 and r08["sbl_fee_n"] == 3, f"費率取窗內中位數（{r08['sbl_fee_median_pct']}，{r08['sbl_fee_n']} 筆）")
    check(r30["sbl_chg20_pct"] is not None and abs(r30["sbl_chg20_pct"]) < 30,
          f"2330 股數依四拆一還原：20 日變化 {r30['sbl_chg20_pct']}%（未還原會是 +300% 上下）")
    raw30 = sbl_features(sbl_fx["2330"], today, [], "2330", cfg)
    check(raw30["sbl_chg20_pct"] is not None and raw30["sbl_chg20_pct"] > 200, f"對照：不還原時 20 日變化 {raw30['sbl_chg20_pct']}%")
    # 資料已是同一單位（分割日沒跳）→ 不可再換算；原始股數（有跳）→ 要換算
    days_ = [f"2026-08-{i:02d}" for i in range(3, 29) if dt.date(2026, 8, i).weekday() < 5]
    flat = {"bal": {d: {"sbl": 1e7 * (1.01 ** i), "margin_short": 0} for i, d in enumerate(days_)},
            "vol": {d: (1e6 if d < "2026-08-17" else 3e6) for d in days_}, "fee": {}}
    jump = {"bal": {d: {"sbl": 1e7 * (1.01 ** i) * (3 if d >= "2026-08-17" else 1), "margin_short": 0} for i, d in enumerate(days_)},
            "vol": flat["vol"], "fee": {}}
    sp_ = [{"ticker": "X", "date": "2026-08-17", "ratio": 3.0, "source": "override"}]
    cfg_w = {**cfg, "features": {**cfg["features"], "return_window_sessions": 15}}
    f_flat = sbl_features(flat, "2026-08-28", sp_, "X", cfg_w)
    f_jump = sbl_features(jump, "2026-08-28", sp_, "X", cfg_w)
    check(f_flat["sbl_chg20_pct"] is not None and 10 < f_flat["sbl_chg20_pct"] < 20,
          f"借券序列分割日沒跳 → 不換算（變化 {f_flat['sbl_chg20_pct']}%；誤乘會是 −60% 上下）")
    check(f_jump["sbl_chg20_pct"] is not None and 10 < f_jump["sbl_chg20_pct"] < 20,
          f"借券序列分割日跳 ×3 → 換算（變化 {f_jump['sbl_chg20_pct']}%）")
    last_j = jump["bal"][days_[-1]]["sbl"]
    check(f_jump["sbl_days_to_cover"] == round(last_j / 3e6, 2),
          f"成交量一律依分割還原：分割前量 ×3 後均量 300 萬股（回補 {f_jump['sbl_days_to_cover']} 天；不還原會是 {round(last_j / ((5 * 1e6 + 10 * 3e6) / 15), 2)}）")
    no_sbl = [r for r in scan(cfg_s, prices, revenue, today, {}) if r["ticker"] == "2308"][0]
    check(no_sbl["sbl_lots"] is None and no_sbl["yoy_pct"] is not None and no_sbl["status"] == "OK",
          "沒有借券資料 → 只有借券欄位為空，其他特徵照常")
    calls = []
    def fake_fetch(c, t, start):
        calls.append((t, start))
        if t == "3324":
            raise RuntimeError("boom")
        return {k: {d: v for d, v in sbl_fx.get(t, sbl_fx["2308"])[k].items() if d >= start} for k in ("bal", "vol", "fee")}
    data1, w1 = update_sbl_cache(cfg, out, True, fake_fetch)
    first_starts = {t: st for t, st in calls}
    calls.clear()
    data2, w2 = update_sbl_cache(cfg, out, True, fake_fetch)
    check(any("3324" in w for w in w1) and "3324" not in data1 and len(data1) == len(cfg["universe"]) - 1,
          "單檔抓失敗 → 警告、其餘照常")
    check(all(st > first_starts[t] for t, st in calls if t != "3324"), "第二次只抓尾巴（增量）")
    check(json.dumps(data1, sort_keys=True) == json.dumps(data2, sort_keys=True), "重抓冪等")
    md_s = render_md(build_summary(cfg_s, rows_s, hist, d, [], today))
    check("借券（只收資料" in md_s and "| 2308 |" in md_s.split("借券（只收資料")[1], "報告有借券表")
    check("借券（只收資料" not in md, "沒有借券資料時報告不印空表")
    # NO_DATA 路徑
    rows_nd = scan(cfg, {}, {}, today)
    check(all(r["status"] == "NO_DATA" for r in rows_nd) and shadow_dca(cfg, {}, today)["status"] == "NO_DATA", "無價格 → NO_DATA 不崩潰")
    open(os.path.join(out, "casino_report.md"), "w", encoding="utf-8").write(md)
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="賭場 sector：AI 個股影子追蹤器")
    ap.add_argument("--config", default=os.path.join(HERE, "config", "casino_config.json"))
    ap.add_argument("--output-dir", default=os.path.join(HERE, "output"))
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    cfg = json.load(open(args.config, encoding="utf-8"))
    if args.selftest:
        ok = selftest(cfg)
        print(f"\n[selftest] {'ALL GREEN ✅' if ok else 'FAILED ❌'}", file=sys.stderr)
        return 0 if ok else 2
    os.makedirs(args.output_dir, exist_ok=True)
    prices, revenue, warns = update_caches(cfg, args.output_dir, fetch=not args.no_fetch)
    prices, splits_used, split_warns = adjust_all(cfg, prices)   # 分割還原（快取存原始價，計算用還原價）
    cfg["_splits_used"] = splits_used
    warns = split_warns + warns
    today = dt.date.today().isoformat()
    sp = os.path.join(args.output_dir, "casino_state.json")
    repaired = repair_features(cfg, sp, prices)
    if repaired:
        print(f"[casino] 用還原後價格重算 {repaired} 筆 state 衍生欄位", file=sys.stderr)
    sbl, sbl_warns = update_sbl_cache(cfg, args.output_dir, fetch=not args.no_fetch)
    warns += sbl_warns
    rows = scan(cfg, prices, revenue, today, sbl)
    added = append_scan(sp, rows)
    filled = backfill(sp, prices, cfg["benchmark"], cfg["outcomes"]["horizons"])
    hist = _load(sp) or []
    dca = shadow_dca(cfg, prices, today)
    s = build_summary(cfg, rows, hist, dca, warns, today)
    md = render_md(s)
    open(os.path.join(args.output_dir, "casino_report.md"), "w", encoding="utf-8").write(md)
    _save(os.path.join(args.output_dir, "casino_brief.json"), s)
    print(md)
    print(f"\n[casino] scan +{added}、回填 {filled}；written casino_report.md / casino_brief.json / casino_state.json / {cfg['sbl']['cache']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
