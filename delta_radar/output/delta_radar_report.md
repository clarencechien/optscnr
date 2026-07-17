# Delta Radar (2308.TW) — 2026-07-17 05:26 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟡 YELLOW

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🔴 RED | capex_cut:6e / vr300_delay:13e(20m) / debt_financed_capex:16e / lc_psu_competition:0e |

### M5 narrative_triggers — 🔴 RED
```json
{
  "events": {
    "capex_cut": 6,
    "vr300_delay": 13,
    "debt_financed_capex": 16,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 6,
    "vr300_delay": 20,
    "debt_financed_capex": 16,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": 3.1,
      "denial": false
    },
    "vr300_delay": {
      "events": 13,
      "mentions": 20,
      "gate": "zscore",
      "z": 0.32,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 16,
      "mentions": 16,
      "gate": "zscore",
      "z": -1.21,
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
- [capex_cut] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [capex_cut] Can Sovereign AI Buffer Nvidia Against a Potential Hyperscaler Slowdown? - Trefis
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] NVDA Stock Climbs Over 1% — Nvidia Says Its AI ‘Roadmap Is Intact’ After Report Of Kyber Rack Delay - Stocktwits
- [vr300_delay] Nvidia's Vera Rubin Hardware Rollout May Be Slightly Delayed, But Analyst Still Expects a 62% Upside—Here - Benzinga
- [debt_financed_capex] Investors Are Growing Wary of AI-Related Debt - AOL.com
- [debt_financed_capex] Amazon’s $25 Billion Bond Sale: Is the AI-Debt Boom a Warning Sign or a Smart Way to Bankroll a Build-Out? - MarketWise
- [debt_financed_capex] Amazon Is Borrowing Another $25 Billion for AI, and Promises This Is the Last Time This Year - 24/7 Wall St.

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **4** 筆；state 已有 outcomes 的 entry：**48/48**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*