# TSMC Radar (2330.TW) — 2026-11-10 13:37 UTC

## 總判定：⚪ PARTIAL（僅跑 m1）｜模組色僅供參考 🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（GREEN）、價格 20 日 -10.4% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 25.9，3 年分位 85 → 48

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-10 YoY +59.7%, slope +5.01pp/月, 連續減速 0 個月 |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-10",
  "latest_yoy_pct": 59.7,
  "yoy_slope_pp_per_month": 5.01,
  "consecutive_decel_months": 0
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**62/62**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 10 / +1.41 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 10 / +1.41 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 9 / +1.49 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 9 / +2.08 | 17 / +1.14 | 31 | 累積中（GREEN n=9 < 30）；方向對 |
| M6 | 10 / +1.41 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*