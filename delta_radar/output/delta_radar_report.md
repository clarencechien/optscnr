# Delta Radar (2308.TW) — 2026-07-11 05:25 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:2e / vr300_delay:15e(24m) / debt_financed_capex:17e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 2,
    "vr300_delay": 15,
    "debt_financed_capex": 17,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 2,
    "vr300_delay": 24,
    "debt_financed_capex": 17,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 2,
      "mentions": 2,
      "gate": "zscore",
      "z": -1.66,
      "denial": false
    },
    "vr300_delay": {
      "events": 15,
      "mentions": 24,
      "gate": "zscore",
      "z": 0.38,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 17,
      "mentions": 17,
      "gate": "zscore",
      "z": 2.12,
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
- [capex_cut] 'The odd decouple': JPMorgan says the tech capex surge is masking a troubling slowdown in job growth - Business Insider
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [vr300_delay] Nvidia's Kyber NVL144 reportedly pushed back more than a year, Asian suppliers drop - the-decoder.com
- [debt_financed_capex] Amazon’s $25 Billion Bond Sale: Is the AI-Debt Boom a Warning Sign or a Smart Way to Bankroll a Build-Out? - MarketWise
- [debt_financed_capex] Amazon Is Borrowing Another $25 Billion for AI, and Promises This Is the Last Time This Year - 24/7 Wall St.
- [debt_financed_capex] Oracle's AI spending blows past estimates, raising worries over growing debt - Reuters

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**38/38**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*