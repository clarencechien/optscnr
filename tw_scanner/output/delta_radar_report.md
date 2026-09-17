# Delta Radar (2308.TW) — 2026-09-17 07:58 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 YELLOW、價格 20 日 -3.4%）；PER 51.6，3 年分位 83 → 74

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:4e / vr300_delay:16e(21m) / debt_financed_capex:13e(14m) / lc_psu_competition:0e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 4,
    "vr300_delay": 16,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 4,
    "vr300_delay": 21,
    "debt_financed_capex": 14,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": 0.35,
      "denial": false
    },
    "vr300_delay": {
      "events": 16,
      "mentions": 21,
      "gate": "zscore",
      "z": -3.19,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 13,
      "mentions": 14,
      "gate": "zscore",
      "z": 2.25,
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
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - finance.yahoo.c
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] Apollo Warns Hyperscaler Debt Is Getting Riskier as AI Spending Strains Balance Sheets - finance.biggo.com
- [debt_financed_capex] AI Chips Are the Most Crowded Trade: Watch Their Customers’ Debt - TradingView
- [debt_financed_capex] AI Companies’ Debt Now Equals 68% of New Long-Term U.S. Treasury Borrowing This Year, JPMorgan Finds - Yahoo Finance

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **7** 筆；state 已有 outcomes 的 entry：**110/110**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 42 / -8.42 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M2 | 13 / -10.34 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 8 / -2.71 | 1 | 無法判定（狀態翻轉 1 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 28 / -7.60 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 28 / -2.92 | 46 / -10.03 | 35 | 累積中（GREEN n=28 < 30）；方向對 |
| M6 | 0 / — | 18 / -3.87 | 1 | 樣本不足（缺一側 cohort） |
| M8 | 18 / -3.87 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*