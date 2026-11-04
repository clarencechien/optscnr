# TSMC Radar (2330.TW) — 2026-11-04 10:48 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 -9.6%）；PER 27.0，3 年分位 77 → 58

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:14e(16m) / n2_arizona_ramp:20e(27m) / cowos_capacity:8e / geopolitics:2e / hyperscaler_capex:6e(7m) |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "export_controls_tariffs": 14,
    "n2_arizona_ramp": 20,
    "cowos_capacity": 8,
    "geopolitics": 2,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 27,
    "cowos_capacity": 8,
    "geopolitics": 2,
    "hyperscaler_capex": 7
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 14,
      "mentions": 16,
      "gate": "zscore",
      "z": 0.91,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 20,
      "mentions": 27,
      "gate": "zscore",
      "z": 1.26,
      "denial": true
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": 0.87,
      "denial": false
    },
    "geopolitics": {
      "events": 2,
      "mentions": 2,
      "gate": "zscore",
      "z": 0.19,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 7,
      "gate": "zscore",
      "z": 0.0,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] TSMC is seeking chipmaking equipment that doesn't contain Chinese rare-earth magnets — asks suppliers to provide alterna
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC, report claim
- [export_controls_tariffs] How Taiwan’s Chip Industry Navigates US Industrial Policy and Export Controls - Global Taiwan Institute
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [cowos_capacity] [News] While TSMC’s CoWoS Faces Supply Shortage, Samsung Reportedly Secures NVIDIA’s 2.5D Advanced Packaging Order - Tre
- [geopolitics] In the shadow of China’s military, Taiwan’s globally critical suppliers keep working - Automotive News
- [geopolitics] China’s planned military exercises near Taiwan may have another target: Japan - The Japan Times
- [hyperscaler_capex] Why Tesla's $5 billion capex cut isn't the warning sign AI stock bears think it is - Yahoo Finance
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **5** 筆；state 已有 outcomes 的 entry：**56/56**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 8 / +1.00 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 8 / +1.00 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 7 / +1.05 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 5 / +1.25 | 16 / +1.02 | 28 | 累積中（GREEN n=5 < 30）；方向對 |
| M6 | 8 / +1.00 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*