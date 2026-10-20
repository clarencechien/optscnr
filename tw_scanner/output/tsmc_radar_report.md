# TSMC Radar (2330.TW) — 2026-10-20 08:26 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 -0.8%）；PER 28.1，3 年分位 67 → 71

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:17e / n2_arizona_ramp:11e(12m) / cowos_capacity:4e / geopolitics:4e / hyperscaler_capex:6e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 17,
    "n2_arizona_ramp": 11,
    "cowos_capacity": 4,
    "geopolitics": 4,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 17,
    "n2_arizona_ramp": 12,
    "cowos_capacity": 4,
    "geopolitics": 4,
    "hyperscaler_capex": 6
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 17,
      "mentions": 17,
      "gate": "zscore",
      "z": 1.76,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 11,
      "mentions": 12,
      "gate": "zscore",
      "z": 1.15,
      "denial": false
    },
    "cowos_capacity": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": -0.34,
      "denial": false
    },
    "geopolitics": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": -0.14,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": 0.45,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] How Taiwan's New AI Chip Export Controls Could Affect China｜Industry｜2026-10-20｜web only - 天下雜誌
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [n2_arizona_ramp] DIGITIMES Insight: Microsoft Maia 300 leads 2nm race, TSMC's US strategy shifts, Intel EMIB-T faces yield challenge - di
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Tech News:Samsung 2nm Chip Yield Surpasses 60%, Closing in on TSMC - LinkedIn
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Medium
- [cowos_capacity] [News] While TSMC’s CoWoS Faces Supply Shortage, Samsung Reportedly Secures NVIDIA’s 2.5D Advanced Packaging Order - Tre
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] In the shadow of China’s military, Taiwan’s globally critical suppliers keep working - Automotive News
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **13** 筆；state 已有 outcomes 的 entry：**41/41**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 4 / +0.47 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 4 / +0.47 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 3 / +0.41 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 0 / — | 6 / +0.23 | 18 | 樣本不足（缺一側 cohort） |
| M6 | 4 / +0.47 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*