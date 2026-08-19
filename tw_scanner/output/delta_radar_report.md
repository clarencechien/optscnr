# Delta Radar (2308.TW) — 2026-08-19 03:24 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:7e / vr300_delay:14e(18m) / debt_financed_capex:12e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 7,
    "vr300_delay": 14,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 7,
    "vr300_delay": 18,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 7,
      "mentions": 7,
      "gate": "zscore",
      "z": 2.14,
      "denial": false
    },
    "vr300_delay": {
      "events": 14,
      "mentions": 18,
      "gate": "zscore",
      "z": 0.0,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 12,
      "mentions": 12,
      "gate": "zscore",
      "z": -1.48,
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
- [capex_cut] Will the next recession be caused by an AI capex cut-off? - investordaily.com.au
- [capex_cut] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - finance.yahoo.c
- [vr300_delay] Nvidia next-gen 'Kyber' AI rack delayed to 2028 on manufacturing snags: report (NVDA:NASDAQ) - Seeking Alpha
- [debt_financed_capex] AI infrastructure debt exceeds $236 billion in 2026, as tech giants shift to Wall Street financing. - KuCoin
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - finance.yahoo.com
- [debt_financed_capex] Tech companies’ AI debt surges as Oracle nears junk credit rating - en.cryptonomist.ch

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **6** 筆；state 已有 outcomes 的 entry：**84/84**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*