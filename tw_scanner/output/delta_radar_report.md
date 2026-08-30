# Delta Radar (2308.TW) — 2026-08-30 08:28 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 ⚪ NO_DATA

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

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
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**91/91**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*