#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
splits.py — 股票分割／反分割的價格還原（tw_scanner 家族共用）
================================================================
FinMind `TaiwanStockPrice` 是**未還原**收盤：0050 在 2025-06-18 四拆一（188.65 → 47.57），
不還原的話分割前買到的單位少算四倍，整本帳全錯（2026-09-12 首跑實測）。

做法（保守、可審計）：
1. `detect_splits(series)`：相鄰兩個有效收盤的比率落在整數倍（2/3/4/5/8/10 或其倒數）±tol 內
   → 視為分割候選。單日 −60% 以上的崩盤在 ETF／大型股極罕見；即使誤判，報告會印出來讓人看。
2. `adjust(series, splits)`：分割日**之前**的價格除以 ratio（反分割乘），回傳新序列。
3. config 可 `override`（強制指定）與 `ignore`（宣告不是分割）。

零價（FinMind 停牌／缺值給 0）一律剔除，不參與偵測與計算。
"""
from __future__ import annotations

_INT_RATIOS = (2.0, 3.0, 4.0, 5.0, 8.0, 10.0)


def clean(series: dict) -> dict:
    """去掉 0／None／非數值。"""
    out = {}
    for d, v in (series or {}).items():
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if f > 0:
            out[d] = f
    return out


def detect_splits(series: dict, tol: float = 0.08, min_jump: float = 0.45) -> list[dict]:
    """→ [{"date": 分割生效日（第一個新價日）, "ratio": 4.0 或 0.25, "before": px, "after": px}]。"""
    s = clean(series)
    dates = sorted(s)
    out = []
    for a, b in zip(dates, dates[1:]):
        r = s[a] / s[b]
        if abs(r - 1) < min_jump and abs(1 / r - 1) < min_jump:
            continue
        for k in _INT_RATIOS:
            if abs(r / k - 1) <= tol:
                out.append({"date": b, "ratio": k, "before": s[a], "after": s[b]})
                break
            if abs(r * k - 1) <= tol:
                out.append({"date": b, "ratio": round(1 / k, 4), "before": s[a], "after": s[b]})
                break
    return out


def adjust(series: dict, splits: list[dict]) -> dict:
    """分割日之前的價格除以 ratio（多次分割累乘）。回傳新 dict，不改原物件。"""
    s = clean(series)
    for sp in sorted(splits, key=lambda x: x["date"]):
        d0, k = sp["date"], float(sp["ratio"])
        s = {d: (v / k if d < d0 else v) for d, v in s.items()}
    return s


def resolve(series: dict, cfg_splits: dict | None, ticker: str) -> tuple[dict, list[dict], list[str]]:
    """偵測 + override + ignore → (還原後序列, 採用的分割, 警告)。

    cfg_splits: {"override": {"0050": [{"date": "2025-06-18", "ratio": 4}]},
                 "ignore":   {"XXXX": ["2024-01-05"]}, "auto_detect": true}
    """
    cfg_splits = cfg_splits or {}
    warns: list[str] = []
    ov = (cfg_splits.get("override") or {}).get(ticker) or []
    ign = set((cfg_splits.get("ignore") or {}).get(ticker) or [])
    found = detect_splits(series) if cfg_splits.get("auto_detect", True) else []
    used = {sp["date"]: {"date": sp["date"], "ratio": float(sp["ratio"]), "source": "override"} for sp in ov}
    for sp in found:
        if sp["date"] in ign:
            continue
        if sp["date"] not in used:
            used[sp["date"]] = {**sp, "source": "auto"}
            warns.append(f"{ticker} {sp['date']} 偵測到疑似分割 ×{sp['ratio']:g}（{sp['before']}→{sp['after']}），已自動還原；"
                         "確認後請寫進 config splits.override（或 ignore）")
    splits = sorted(used.values(), key=lambda x: x["date"])
    return adjust(series, splits), splits, warns
