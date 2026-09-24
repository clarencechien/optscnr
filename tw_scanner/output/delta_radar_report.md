# Delta Radar (2308.TW) — 2026-09-24 07:48 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 🔀 前提 vs 價格：🔀 反向背離：前提轉紅、價格 20 日 +7.9% 未跌 —— 市場不買儀器的帳，或儀器誤判；PER 55.2，3 年分位 79 → 78

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:5e(6m) / vr300_delay:18e(22m) / debt_financed_capex:16e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 5,
    "vr300_delay": 18,
    "debt_financed_capex": 16,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 6,
    "vr300_delay": 22,
    "debt_financed_capex": 16,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 5,
      "mentions": 6,
      "gate": "zscore",
      "z": 1.56,
      "denial": false
    },
    "vr300_delay": {
      "events": 18,
      "mentions": 22,
      "gate": "zscore",
      "z": 0.49,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 16,
      "mentions": 16,
      "gate": "zscore",
      "z": 1.4,
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
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] AI Companies’ Debt Now Equals 68% of New Long-Term U.S. Treasury Borrowing This Year, JPMorgan Finds - Yahoo Finance
- [debt_financed_capex] Apollo Just Flashed Yellow on Hyperscaler Debt - Money Morning
- [debt_financed_capex] The "debt black hole" behind the AI boom: $1.2 trillion external financing may be needed in the next five years - Bitget

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **6** 筆；state 已有 outcomes 的 entry：**118/118**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 44 / -7.97 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M2 | 15 / -8.78 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 10 / -1.89 | 1 | 無法判定（狀態翻轉 1 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 29 / -7.27 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 30 / -2.52 | 48 / -9.72 | 41 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 20 / -3.34 | 1 | 樣本不足（缺一側 cohort） |
| M8 | 20 / -3.34 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*