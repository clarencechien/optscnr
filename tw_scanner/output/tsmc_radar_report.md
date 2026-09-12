# TSMC Radar (2330.TW) — 2026-09-12 06:08 UTC

## 總判定：🟡 YELLOW

## 前提 vs 價格：無背離（前提 YELLOW、價格 20 日 +0.6%）；PER 27.9，3 年分位 71 → 72

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-08 YoY +53.3%, slope +7.74pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +13.7%（1 年第 19 百分位；觀察） |
| M4 customs_flow | ⚪ NO_DATA | Census fetch failed after 2 tries |
| M5 narrative_triggers | 🔴 RED | export_controls_tariffs:16e / n2_arizona_ramp:7e(8m) / cowos_capacity:9e / geopolitics:4e / hyperscaler_capex:4e(5m) |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2308 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 27.9（3 年第 72 百分位；20 日前第 71）；觀察 |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-08",
  "latest_yoy_pct": 53.3,
  "yoy_slope_pp_per_month": 7.74,
  "consecutive_decel_months": 0
}
```

### M2 bullwhip_health — 🟢 GREEN
```json
{
  "as_of": null,
  "contract_liab_qoq_pct": null,
  "inventory_qoq_pct": 23.8,
  "fcf_to_net_income": 0.9,
  "accounts_used": {
    "contract": "",
    "inventory": "Inventories",
    "ocf": "CashFlowsFromOperatingActivities",
    "capex": "PropertyAndPlantAndEquipment",
    "net_income": "IncomeAfterTaxes"
  }
}
```

### M3 adr_premium — 🟢 GREEN
```json
{
  "as_of": "2026-09-11",
  "premium_pct": 13.74,
  "percentile_1y": 18.6,
  "n": 372
}
```

### M4 customs_flow — ⚪ NO_DATA
- raw/exception: Census non-JSON response: ''
- ⚠️ degraded: Census fetch failed after 2 tries

### M5 narrative_triggers — 🔴 RED
```json
{
  "events": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 7,
    "cowos_capacity": 9,
    "geopolitics": 4,
    "hyperscaler_capex": 4
  },
  "mentions": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 8,
    "cowos_capacity": 9,
    "geopolitics": 4,
    "hyperscaler_capex": 5
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
      "events": 9,
      "mentions": 9,
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
      "mentions": 5,
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
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Intel and Samsung advance 2nm GAA, but yield gaps leave TSMC as the sole external supplier - digitimes
- [n2_arizona_ramp] Tech News:Samsung 2nm Chip Yield Surpasses 60%, Closing in on TSMC - LinkedIn
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Medium
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
- [geopolitics] Ships Delay Sailing to Taiwan Port to Avoid China Military Drills - caixinglobal.com
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [hyperscaler_capex] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [hyperscaler_capex] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.

### M6 peer_divergence — 🟢 GREEN
```json
{
  "groups": {
    "foundry_contrast": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 55.3,
      "best_peer": "2303",
      "best_peer_3m_yoy": 24.2,
      "peer_lead_pp": -31.1,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2303": 24.2
      }
    },
    "backend": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 55.3,
      "best_peer": "2383",
      "best_peer_3m_yoy": 126.6,
      "peer_lead_pp": 71.4,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3711": 40.6,
        "3037": 45.4,
        "2383": 126.6
      }
    },
    "asic_lead": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 55.3,
      "best_peer": "3661",
      "best_peer_3m_yoy": 156.9,
      "peer_lead_pp": 101.6,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3661": 156.9,
        "3443": 124.4
      }
    }
  }
}
```

### M8 revision_velocity — ⚪ NO_DATA
```json
{
  "up_hits": 0,
  "down_hits": 0,
  "total": 0,
  "down_ratio": null
}
```

### M9 valuation — 🟢 GREEN
```json
{
  "as_of": "2026-09-11",
  "per": 27.94,
  "per_pct": 71.8,
  "per_then": 27.76,
  "per_pct_then": 70.7,
  "pbr": 9.72,
  "dividend_yield": 0.91,
  "history_years": 3,
  "n": 735
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**1/1**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*