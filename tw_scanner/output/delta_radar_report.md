# Delta Radar (2308.TW) — 2026-08-11 05:36 UTC

## 總判定：⚪ PARTIAL（僅跑 m1）｜模組色僅供參考 🟢 GREEN

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-07 YoY +47.7%, slope +1.28pp/月, 連續減速 1 個月 |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-07",
  "latest_yoy_pct": 47.7,
  "yoy_slope_pp_per_month": 1.28,
  "consecutive_decel_months": 1
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**73/73**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*