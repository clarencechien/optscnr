# TSMC Radar (2330.TW) — 2026-10-04 09:42 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +4.8%）；PER 29.1，3 年分位 75 → 80

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:13e / n2_arizona_ramp:9e(11m) / cowos_capacity:9e / geopolitics:3e / hyperscaler_capex:6e(7m) |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 13,
    "n2_arizona_ramp": 9,
    "cowos_capacity": 9,
    "geopolitics": 3,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 13,
    "n2_arizona_ramp": 11,
    "cowos_capacity": 9,
    "geopolitics": 3,
    "hyperscaler_capex": 7
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 13,
      "mentions": 13,
      "gate": "zscore",
      "z": -3.0,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 9,
      "mentions": 11,
      "gate": "zscore",
      "z": -1.1,
      "denial": false
    },
    "cowos_capacity": {
      "events": 9,
      "mentions": 9,
      "gate": "zscore",
      "z": 1.16,
      "denial": true
    },
    "geopolitics": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -2.24,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 7,
      "gate": "zscore",
      "z": 1.69,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [n2_arizona_ramp] Samsung's 2nm Yield Approaches 60%, Leveraging Tesla Orders to Challenge TSMC - finance.biggo.com
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Tech News:Samsung 2nm Chip Yield Surpasses 60%, Closing in on TSMC - LinkedIn
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes.com
- [cowos_capacity] OCP APAC 2026: TSMC tackles CoWoS material risks while cutting 3DIC development cycle to one year - digitimes.com
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China’s planned military exercises near Taiwan may have another target: Japan - The Japan Times
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [hyperscaler_capex] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**23/23**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*