# TSMC Radar (2330.TW) — 2026-09-13 08:15 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟡 YELLOW

## 前提 vs 價格：無背離（前提 YELLOW、價格 20 日 +0.6%）；PER 27.9，3 年分位 71 → 72

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🔴 RED | export_controls_tariffs:16e / n2_arizona_ramp:7e(8m) / cowos_capacity:6e / geopolitics:4e / hyperscaler_capex:4e |

### M5 narrative_triggers — 🔴 RED
```json
{
  "events": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 7,
    "cowos_capacity": 6,
    "geopolitics": 4,
    "hyperscaler_capex": 4
  },
  "mentions": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 8,
    "cowos_capacity": 6,
    "geopolitics": 4,
    "hyperscaler_capex": 4
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 16,
      "mentions": 16,
      "gate": "absolute",
      "z": null,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 7,
      "mentions": 8,
      "gate": "absolute",
      "z": null,
      "denial": false
    },
    "cowos_capacity": {
      "events": 6,
      "mentions": 6,
      "gate": "absolute",
      "z": null,
      "denial": true
    },
    "geopolitics": {
      "events": 4,
      "mentions": 4,
      "gate": "absolute",
      "z": null,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 4,
      "mentions": 4,
      "gate": "absolute",
      "z": null,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [export_controls_tariffs] Huawei's chip breakthrough makes the case that US export controls built the rival they were meant to stop - Startup Fort
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - finance.biggo.com
- [n2_arizona_ramp] Samsung and Qualcomm reopen 2nm talks as yield gap with TSMC narrows - CHOSUNBIZ - Chosunbiz
- [n2_arizona_ramp] Intel and Samsung advance 2nm GAA, but yield gaps leave TSMC as the sole external supplier - digitimes
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Medium
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
- [geopolitics] Ships Delay Sailing to Taiwan Port to Avoid China Military Drills - Caixin Global
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 247wallst.com
- [hyperscaler_capex] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [hyperscaler_capex] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 247wallst.com

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**3/3**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*