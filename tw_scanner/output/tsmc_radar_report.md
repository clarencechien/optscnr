# TSMC Radar (2330.TW) — 2026-10-30 09:55 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 -4.2%）；PER 28.0，3 年分位 77 → 70

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:12e(13m) / n2_arizona_ramp:19e(25m) / cowos_capacity:8e / geopolitics:1e / hyperscaler_capex:3e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 12,
    "n2_arizona_ramp": 19,
    "cowos_capacity": 8,
    "geopolitics": 1,
    "hyperscaler_capex": 3
  },
  "mentions": {
    "export_controls_tariffs": 13,
    "n2_arizona_ramp": 25,
    "cowos_capacity": 8,
    "geopolitics": 1,
    "hyperscaler_capex": 3
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 12,
      "mentions": 13,
      "gate": "zscore",
      "z": -1.09,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 19,
      "mentions": 25,
      "gate": "zscore",
      "z": 2.42,
      "denial": true
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": 1.47,
      "denial": false
    },
    "geopolitics": {
      "events": 1,
      "mentions": 1,
      "gate": "zscore",
      "z": -1.45,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -2.17,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] TSMC is seeking chipmaking equipment that doesn't contain Chinese rare-earth magnets — asks suppliers to provide alterna
- [export_controls_tariffs] How Taiwan’s Chip Industry Navigates US Industrial Policy and Export Controls - Global Taiwan Institute
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC, report claim
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Beth Kindig – Medium
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - Yahoo Finance
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **8** 筆；state 已有 outcomes 的 entry：**51/51**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 7 / +0.81 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 7 / +0.81 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 6 / +0.84 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 5 / +1.25 | 13 / +0.85 | 24 | 累積中（GREEN n=5 < 30）；方向對 |
| M6 | 7 / +0.81 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*