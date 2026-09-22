# TSMC Radar (2330.TW) — 2026-09-22 08:28 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +2.5%）；PER 28.8，3 年分位 69 → 78

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:15e / n2_arizona_ramp:6e(7m) / cowos_capacity:8e / geopolitics:4e / hyperscaler_capex:5e(6m) |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 6,
    "cowos_capacity": 8,
    "geopolitics": 4,
    "hyperscaler_capex": 5
  },
  "mentions": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 7,
    "cowos_capacity": 8,
    "geopolitics": 4,
    "hyperscaler_capex": 6
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 15,
      "mentions": 15,
      "gate": "zscore",
      "z": -0.42,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 6,
      "mentions": 7,
      "gate": "zscore",
      "z": -1.57,
      "denial": false
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": 0.78,
      "denial": true
    },
    "geopolitics": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": 0.0,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 5,
      "mentions": 6,
      "gate": "zscore",
      "z": 2.47,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [n2_arizona_ramp] Samsung and Qualcomm reopen 2nm talks as yield gap with TSMC narrows - CHOSUNBIZ - Chosunbiz
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - finance.biggo.com
- [n2_arizona_ramp] Samsung's 2nm Yield Tops 50%, Restarts Qualcomm Talks; Snapdragon Summit May Decide Foundry Assignment - finance.biggo.c
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [hyperscaler_capex] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **6** 筆；state 已有 outcomes 的 entry：**9/9**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*