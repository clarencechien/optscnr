# TSMC Radar (2330.TW) — 2026-11-17 11:44 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟡 YELLOW

## 🔀 前提 vs 價格：🔀 背離：前提健在（GREEN）、價格 20 日 -10.3% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 22.5，3 年分位 72 → 27

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🔴 RED | export_controls_tariffs:15e(17m) / n2_arizona_ramp:21e(28m) / cowos_capacity:8e / geopolitics:3e / hyperscaler_capex:3e |

### M5 narrative_triggers — 🔴 RED
```json
{
  "events": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 21,
    "cowos_capacity": 8,
    "geopolitics": 3,
    "hyperscaler_capex": 3
  },
  "mentions": {
    "export_controls_tariffs": 17,
    "n2_arizona_ramp": 28,
    "cowos_capacity": 8,
    "geopolitics": 3,
    "hyperscaler_capex": 3
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 15,
      "mentions": 17,
      "gate": "zscore",
      "z": 2.21,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 21,
      "mentions": 28,
      "gate": "zscore",
      "z": -0.66,
      "denial": true
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": 0.0,
      "denial": false
    },
    "geopolitics": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": 2.66,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -1.15,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] TSMC is seeking chipmaking equipment that doesn't contain Chinese rare-earth magnets — asks suppliers to provide alterna
- [export_controls_tariffs] TSMC Seeks Rare-Earth-Free Factory Equipment as China’s Export Controls Threaten Chip Supply Chains - Tekedia
- [export_controls_tariffs] How Taiwan’s Chip Industry Navigates US Industrial Policy and Export Controls - Global Taiwan Institute
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [cowos_capacity] [News] While TSMC’s CoWoS Faces Supply Shortage, Samsung Reportedly Secures NVIDIA’s 2.5D Advanced Packaging Order - Tre
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [geopolitics] Could China Blockade Taiwan? Naval Drills Raise Fears of a Wider Indo-Pacific Crisis - Modern Diplomacy
- [geopolitics] China stages record drills designed to encircle Taiwan - Reuters
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - The Motley Fool
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Will the next recession be caused by an AI capex cut-off? - InvestorDaily

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **10** 筆；state 已有 outcomes 的 entry：**71/71**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 15 / +2.26 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 12 / +1.72 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 11 / +1.82 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 13 / +2.72 | 21 / +1.54 | 37 | 累積中（GREEN n=13 < 30）；方向對 |
| M6 | 12 / +1.72 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*