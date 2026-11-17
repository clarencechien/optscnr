# Delta Radar (2308.TW) — 2026-11-17 11:07 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（YELLOW）、價格 20 日 -35.5% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 33.6，3 年分位 71 → 56

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:3e / vr300_delay:10e(11m) / debt_financed_capex:10e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 3,
    "vr300_delay": 10,
    "debt_financed_capex": 10,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 3,
    "vr300_delay": 11,
    "debt_financed_capex": 10,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -1.37,
      "denial": false
    },
    "vr300_delay": {
      "events": 10,
      "mentions": 11,
      "gate": "zscore",
      "z": 2.47,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 10,
      "mentions": 10,
      "gate": "zscore",
      "z": -0.46,
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
- [capex_cut] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - The Motley Fool
- [capex_cut] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [capex_cut] Will the next recession be caused by an AI capex cut-off? - InvestorDaily
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] Will Oracle's Debt-Funded Data Center Buildout Weigh on the Stock Now? - TradingView
- [debt_financed_capex] AI Debt Risks Mount: Why Borrowing by Meta, Alphabet, Microsoft and Oracle Worries Investors - TradingKey
- [debt_financed_capex] AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch. - CNBC

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **5** 筆；state 已有 outcomes 的 entry：**168/168**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 17 / -13.30 | 3 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M2 | 29 / -10.19 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 24 / -7.62 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 42 / -8.86 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M5 | 58 / -6.90 | 65 / -10.55 | 50 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 34 / -6.79 | 5 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*