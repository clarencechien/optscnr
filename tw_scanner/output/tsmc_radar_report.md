# TSMC Radar (2330.TW) — 2026-09-17 09:30 UTC

## 總判定：🟡 YELLOW

## 前提 vs 價格：無背離（前提 YELLOW、價格 20 日 +2.1%）；PER 28.1，3 年分位 69 → 74

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-08 YoY +53.3%, slope +7.74pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +9.8%（1 年第 2 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3643.7M, YoY +58.0% |
| M5 narrative_triggers | 🔴 RED | export_controls_tariffs:17e / n2_arizona_ramp:10e / cowos_capacity:7e / geopolitics:4e / hyperscaler_capex:4e |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 28.1（3 年第 74 百分位；20 日前第 69）；觀察 |

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
  "as_of": "2026-09-17",
  "premium_pct": 9.84,
  "percentile_1y": 1.9,
  "n": 372
}
```

### M4 customs_flow — 🟢 GREEN
```json
{
  "window": "2026-05..2026-07",
  "rolling_value_usd_m": 3643.7,
  "rolling_yoy_pct": 58.0,
  "by_country": {
    "TAIWAN": {
      "rolling_value_usd_m": 3643.7,
      "rolling_yoy_pct": 58.0
    }
  }
}
```

### M5 narrative_triggers — 🔴 RED
```json
{
  "events": {
    "export_controls_tariffs": 17,
    "n2_arizona_ramp": 10,
    "cowos_capacity": 7,
    "geopolitics": 4,
    "hyperscaler_capex": 4
  },
  "mentions": {
    "export_controls_tariffs": 17,
    "n2_arizona_ramp": 10,
    "cowos_capacity": 7,
    "geopolitics": 4,
    "hyperscaler_capex": 4
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 17,
      "mentions": 17,
      "gate": "zscore",
      "z": 1.19,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 10,
      "mentions": 10,
      "gate": "zscore",
      "z": 2.68,
      "denial": false
    },
    "cowos_capacity": {
      "events": 7,
      "mentions": 7,
      "gate": "zscore",
      "z": 0.0,
      "denial": true
    },
    "geopolitics": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": -0.45,
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
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - tradingview.com
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [n2_arizona_ramp] Samsung's 2nm Yield Tops 50%, Restarts Qualcomm Talks; Snapdragon Summit May Decide Foundry Assignment - finance.biggo.c
- [n2_arizona_ramp] Samsung and Qualcomm reopen 2nm talks as yield gap with TSMC narrows - CHOSUNBIZ - biz.chosun.com
- [n2_arizona_ramp] Intel and Samsung advance 2nm GAA, but yield gaps leave TSMC as the sole external supplier - digitimes
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - beth-kindig.medium.com
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
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
  "as_of": "2026-09-17",
  "per": 28.11,
  "per_pct": 73.7,
  "per_then": 27.53,
  "per_pct_then": 69.0,
  "pbr": 9.78,
  "dividend_yield": 0.91,
  "history_years": 3,
  "n": 735
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**6/6**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*