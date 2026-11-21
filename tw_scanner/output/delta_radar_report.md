# Delta Radar (2308.TW) — 2026-11-21 10:11 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（YELLOW）、價格 20 日 -44.6% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 30.0，3 年分位 69 → 46

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | capex_cut:3e / vr300_delay:8e(9m) / debt_financed_capex:11e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 3,
    "vr300_delay": 8,
    "debt_financed_capex": 11,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 3,
    "vr300_delay": 9,
    "debt_financed_capex": 11,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -1.05,
      "denial": false
    },
    "vr300_delay": {
      "events": 8,
      "mentions": 9,
      "gate": "zscore",
      "z": -0.8,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 11,
      "mentions": 11,
      "gate": "zscore",
      "z": 1.0,
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
- [debt_financed_capex] Will Oracle's Debt-Funded Data Center Buildout Weigh on the Stock Now? - Yahoo Finance
- [debt_financed_capex] AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch. - CNBC
- [debt_financed_capex] AI Debt Risks Mount: Why Borrowing by Meta, Alphabet, Microsoft and Oracle Worries Investors - TradingKey

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**171/171**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 18 / -13.80 | 3 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M2 | 30 / -10.60 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 25 / -8.21 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 43 / -9.17 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M5 | 60 / -7.40 | 65 / -10.55 | 51 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 35 / -7.23 | 5 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*