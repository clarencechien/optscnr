# TSMC Radar (2330.TW) — 2026-10-25 08:20 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 -3.8%）；PER 28.1，3 年分位 76 → 70

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:14e / n2_arizona_ramp:17e(25m) / cowos_capacity:7e / geopolitics:2e / hyperscaler_capex:6e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 14,
    "n2_arizona_ramp": 17,
    "cowos_capacity": 7,
    "geopolitics": 2,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 14,
    "n2_arizona_ramp": 25,
    "cowos_capacity": 7,
    "geopolitics": 2,
    "hyperscaler_capex": 6
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 14,
      "mentions": 14,
      "gate": "zscore",
      "z": -0.54,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 17,
      "mentions": 25,
      "gate": "zscore",
      "z": 11.07,
      "denial": true
    },
    "cowos_capacity": {
      "events": 7,
      "mentions": 7,
      "gate": "zscore",
      "z": 1.77,
      "denial": false
    },
    "geopolitics": {
      "events": 2,
      "mentions": 2,
      "gate": "zscore",
      "z": -2.52,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": -0.45,
      "denial": false
    }
  }
}
```
- [n2_arizona_ramp] 官方否認偵測 → 上限 🟡（爭議中）
- [export_controls_tariffs] TSMC is seeking chipmaking equipment that doesn't contain Chinese rare-earth magnets — asks suppliers to provide alterna
- [export_controls_tariffs] TSMC Seeks Rare-Earth-Free Factory Equipment as China’s Export Controls Threaten Chip Supply Chains - Tekedia
- [export_controls_tariffs] How Taiwan's New AI Chip Export Controls Could Affect China｜Industry｜2026-10-20｜web only - 天下雜誌
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Tech News:Samsung 2nm Chip Yield Surpasses 60%, Closing in on TSMC - LinkedIn
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Medium
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [hyperscaler_capex] Why Tesla's $5 billion capex cut isn't the warning sign AI stock bears think it is - Yahoo Finance
- [hyperscaler_capex] The AI trade is at a 'critical' crossroads as rising rates threaten a capex slowdown, AllianceBernstein says - Business 
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**46/46**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 5 / +0.41 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 5 / +0.41 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 4 / +0.35 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 0 / — | 8 / +0.19 | 22 | 樣本不足（缺一側 cohort） |
| M6 | 5 / +0.41 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*