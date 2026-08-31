# Delta Radar (2308.TW) — 2026-08-31 08:48 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:4e / vr300_delay:16e(20m) / debt_financed_capex:14e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 4,
    "vr300_delay": 16,
    "debt_financed_capex": 14,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 4,
    "vr300_delay": 20,
    "debt_financed_capex": 14,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": -1.98,
      "denial": false
    },
    "vr300_delay": {
      "events": 16,
      "mentions": 20,
      "gate": "zscore",
      "z": 0.71,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 14,
      "mentions": 14,
      "gate": "zscore",
      "z": 1.74,
      "denial": false
    },
    "lc_psu_competition": {
      "events": 0,
      "mentions": 0,
      "gate": "absolute",
      "z": null,
      "denial": false
    }
  }
}
```
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [capex_cut] Will the next recession be caused by an AI capex cut-off? - investordaily.com.au
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] Nvidia’s Rubin Ultra delays raise 2028 risk for AI dominance - Ticker News
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - Yahoo Finance
- [debt_financed_capex] What the $489B AI Debt Wave Means for Treasury Risk - The Global Treasurer
- [debt_financed_capex] The growing jitters over hyperscaler debt - Axios

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **8** 筆；state 已有 outcomes 的 entry：**92/92**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*