# Delta Radar (2308.TW) — 2026-09-03 07:22 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:3e / vr300_delay:18e(21m) / debt_financed_capex:12e(13m) / lc_psu_competition:0e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 3,
    "vr300_delay": 18,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 3,
    "vr300_delay": 21,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -1.65,
      "denial": false
    },
    "vr300_delay": {
      "events": 18,
      "mentions": 21,
      "gate": "zscore",
      "z": 1.54,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 12,
      "mentions": 13,
      "gate": "zscore",
      "z": -0.32,
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
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [capex_cut] 'The odd decouple': JPMorgan says the tech capex surge is masking a troubling slowdown in job growth - Business Insider
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] Jensen Huang Takes Stage at Morgan Stanley Roadshow: Quarterly Revenue Nears $100 Billion, Nvidia Denies Rubin Ultra Del
- [debt_financed_capex] AI Boom Triggers Tech Debt Binge - StartupHub.ai
- [debt_financed_capex] The growing jitters over hyperscaler debt - axios.com
- [debt_financed_capex] AI data center debt has climbed to the top of Wall Street's credit risk watchlist - Startup Fortune

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **5** 筆；state 已有 outcomes 的 entry：**95/95**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*