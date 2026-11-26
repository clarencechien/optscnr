# TSMC Radar (2330.TW) — 2026-11-26 12:18 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（GREEN）、價格 20 日 -11.2% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 20.7，3 年分位 65 → 16

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:10e(15m) / n2_arizona_ramp:22e(27m) / cowos_capacity:7e / geopolitics:2e / hyperscaler_capex:6e(7m) |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 10,
    "n2_arizona_ramp": 22,
    "cowos_capacity": 7,
    "geopolitics": 2,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 27,
    "cowos_capacity": 7,
    "geopolitics": 2,
    "hyperscaler_capex": 7
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 10,
      "mentions": 15,
      "gate": "zscore",
      "z": -3.48,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 22,
      "mentions": 27,
      "gate": "zscore",
      "z": 0.68,
      "denial": true
    },
    "cowos_capacity": {
      "events": 7,
      "mentions": 7,
      "gate": "zscore",
      "z": 0.2,
      "denial": false
    },
    "geopolitics": {
      "events": 2,
      "mentions": 2,
      "gate": "zscore",
      "z": -0.41,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 7,
      "gate": "zscore",
      "z": 1.9,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] Apple supplier TSMC cuts off China chip orders amid tighter export controls - AppleInsider
- [export_controls_tariffs] TSMC and Samsung pause some chip shipments to China due to tighter US export controls - Digital Watch Observatory
- [export_controls_tariffs] PRE-MARKET TAIWAN AND SINGAPORE STOCKS NEWS: TSMC (2330 TT) tightening restrictions on Chinese chip designers - Newsquaw
- [n2_arizona_ramp] AMD Zen 6 Olympic Ridge Desktop CPUs Reportedly Slip Past Computex 2027 After A Switch To TSMC’s Performance-Focused N2X
- [n2_arizona_ramp] Samsung and Qualcomm reopen 2nm talks as yield gap with TSMC narrows - Chosunbiz
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [cowos_capacity] [News] While TSMC’s CoWoS Faces Supply Shortage, Samsung Reportedly Secures NVIDIA’s 2.5D Advanced Packaging Order - Tre
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [geopolitics] China stages record drills designed to encircle Taiwan - Reuters
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - The Motley Fool
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] The AI trade is at a 'critical' crossroads as rising rates threaten a capex slowdown, AllianceBernstein says - Business 

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **9** 筆；state 已有 outcomes 的 entry：**78/78**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 19 / +2.41 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 16 / +2.04 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 15 / +2.14 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 17 / +2.87 | 29 / +1.95 | 42 | 累積中（GREEN n=17 < 30）；方向對 |
| M6 | 16 / +2.04 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*