# TSMC Radar (2330.TW) — 2026-10-12 10:40 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +3.0%）；PER 29.6，3 年分位 77 → 83

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:15e / n2_arizona_ramp:11e(12m) / cowos_capacity:0e / geopolitics:4e / hyperscaler_capex:0e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 11,
    "cowos_capacity": 0,
    "geopolitics": 4,
    "hyperscaler_capex": 0
  },
  "mentions": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 12,
    "cowos_capacity": 0,
    "geopolitics": 4,
    "hyperscaler_capex": 0
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 15,
      "mentions": 15,
      "gate": "zscore",
      "z": 1.05,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 11,
      "mentions": 12,
      "gate": "zscore",
      "z": 1.16,
      "denial": false
    },
    "cowos_capacity": {
      "events": 0,
      "mentions": 0,
      "gate": "zscore",
      "z": -5.85,
      "denial": false
    },
    "geopolitics": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": 0.94,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 0,
      "mentions": 0,
      "gate": "zscore",
      "z": -10.29,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [n2_arizona_ramp] Samsung's 2nm Yield Approaches 60%, Leveraging Tesla Orders to Challenge TSMC - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Tech News:Samsung 2nm Chip Yield Surpasses 60%, Closing in on TSMC - LinkedIn
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **7** 筆；state 已有 outcomes 的 entry：**32/32**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*