# TSMC Radar (2330.TW) — 2026-09-23 08:30 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +3.5%）；PER 28.8，3 年分位 69 → 78

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:16e / n2_arizona_ramp:10e(12m) / cowos_capacity:6e / geopolitics:3e / hyperscaler_capex:4e(5m) |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 10,
    "cowos_capacity": 6,
    "geopolitics": 3,
    "hyperscaler_capex": 4
  },
  "mentions": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 12,
    "cowos_capacity": 6,
    "geopolitics": 3,
    "hyperscaler_capex": 5
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 16,
      "mentions": 16,
      "gate": "zscore",
      "z": 0.49,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 10,
      "mentions": 12,
      "gate": "zscore",
      "z": 1.45,
      "denial": false
    },
    "cowos_capacity": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": -1.12,
      "denial": true
    },
    "geopolitics": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -2.0,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 4,
      "mentions": 5,
      "gate": "zscore",
      "z": -0.5,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Intel and Samsung advance 2nm GAA, but yield gaps leave TSMC as the sole external supplier - digitimes
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - finance.biggo.com
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - wccftech.com
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
- [geopolitics] China’s planned military exercises near Taiwan may have another target: Japan - The Japan Times
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [hyperscaler_capex] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [hyperscaler_capex] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**10/10**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*