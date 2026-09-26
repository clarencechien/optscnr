# Delta Radar (2308.TW) — 2026-09-26 08:00 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 ⚪ NO_DATA

## 前提 vs 價格：無背離（前提 YELLOW、價格 20 日 +7.9%）；PER 60.5，3 年分位 79 → 84

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | ⚪ NO_DATA | all RSS feeds failed |

### M5 narrative_triggers — ⚪ NO_DATA
- feed capex_cut failed: HTTP Error 503: Service Unavailable
- feed vr300_delay failed: HTTP Error 503: Service Unavailable
- feed debt_financed_capex failed: HTTP Error 503: Service Unavailable
- feed lc_psu_competition failed: HTTP Error 503: Service Unavailable
- ⚠️ degraded: all RSS feeds failed

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**121/121**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 44 / -7.97 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M2 | 15 / -8.78 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 10 / -1.89 | 1 | 無法判定（狀態翻轉 1 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 29 / -7.27 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 30 / -2.52 | 48 / -9.72 | 42 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 20 / -3.34 | 1 | 樣本不足（缺一側 cohort） |
| M8 | 20 / -3.34 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*