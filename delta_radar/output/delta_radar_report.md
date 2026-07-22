# Delta Radar (2308.TW) — 2026-07-22 05:33 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | capex_cut:5e / vr300_delay:12e(22m) / debt_financed_capex:17e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 5,
    "vr300_delay": 12,
    "debt_financed_capex": 17,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 5,
    "vr300_delay": 22,
    "debt_financed_capex": 17,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 5,
      "mentions": 5,
      "gate": "zscore",
      "z": 0.96,
      "denial": false
    },
    "vr300_delay": {
      "events": 12,
      "mentions": 22,
      "gate": "zscore",
      "z": -0.63,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 17,
      "mentions": 17,
      "gate": "zscore",
      "z": 1.17,
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
- [capex_cut] Apple’s AI Strategy: A Different Approach Amidst Hyperscaler Capex Slowdown - SaaS Earnings Trends - dars.gov.et
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [vr300_delay] Nvidia CEO Says Vera Rubin Is in Production, Denies Delay - WinBuzzer
- [vr300_delay] Nvidia's Kyber NVL144 reportedly pushed back more than a year, Asian suppliers drop - the-decoder.com
- [debt_financed_capex] Goldman Sachs Warns on AI’s Debt Tsunami — Is This the End of the AI Boom? - 24/7 Wall St.
- [debt_financed_capex] Oracle stock sinks as AI spending fuels debt fears - MSN
- [debt_financed_capex] Amazon’s $25 Billion Bond Sale: Is the AI-Debt Boom a Warning Sign or a Smart Way to Bankroll a Build-Out? - MarketWise

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **6** 筆；state 已有 outcomes 的 entry：**52/52**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*