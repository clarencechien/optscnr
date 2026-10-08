# TSMC Radar (2330.TW) — 2026-10-08 11:26 UTC

## 總判定：🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +3.2%）；PER 29.6，3 年分位 77 → 83

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +18.3%（1 年第 44 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3675.7M, YoY +60.6% |
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:14e / n2_arizona_ramp:9e(10m) / cowos_capacity:7e / geopolitics:3e / hyperscaler_capex:6e |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 29.6（3 年第 83 百分位；20 日前第 77）；觀察 |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-09",
  "latest_yoy_pct": 54.6,
  "yoy_slope_pp_per_month": -4.41,
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
  "as_of": "2026-10-08",
  "premium_pct": 18.34,
  "percentile_1y": 43.5,
  "n": 371
}
```

### M4 customs_flow — 🟢 GREEN
```json
{
  "window": "2026-06..2026-08",
  "rolling_value_usd_m": 3675.7,
  "rolling_yoy_pct": 60.6,
  "by_country": {
    "TAIWAN": {
      "rolling_value_usd_m": 3675.7,
      "rolling_yoy_pct": 60.6
    }
  }
}
```

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "export_controls_tariffs": 14,
    "n2_arizona_ramp": 9,
    "cowos_capacity": 7,
    "geopolitics": 3,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 14,
    "n2_arizona_ramp": 10,
    "cowos_capacity": 7,
    "geopolitics": 3,
    "hyperscaler_capex": 6
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 14,
      "mentions": 14,
      "gate": "zscore",
      "z": -0.8,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 9,
      "mentions": 10,
      "gate": "zscore",
      "z": -1.16,
      "denial": false
    },
    "cowos_capacity": {
      "events": 7,
      "mentions": 7,
      "gate": "zscore",
      "z": -2.71,
      "denial": false
    },
    "geopolitics": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -1.45,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": 1.37,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [n2_arizona_ramp] Samsung's 2nm Yield Approaches 60%, Leveraging Tesla Orders to Challenge TSMC - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Tech News:Samsung 2nm Chip Yield Surpasses 60%, Closing in on TSMC - LinkedIn
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China’s planned military exercises near Taiwan may have another target: Japan - The Japan Times
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.

### M6 peer_divergence — 🟢 GREEN
```json
{
  "groups": {
    "foundry_contrast": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 50.9,
      "best_peer": "2303",
      "best_peer_3m_yoy": 25.6,
      "peer_lead_pp": -25.2,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2303": 25.6
      }
    },
    "backend": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 50.9,
      "best_peer": "2383",
      "best_peer_3m_yoy": 142.7,
      "peer_lead_pp": 91.8,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3711": 40.6,
        "3037": 45.4,
        "2383": 142.7
      }
    },
    "asic_lead": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 50.9,
      "best_peer": "3661",
      "best_peer_3m_yoy": 156.9,
      "peer_lead_pp": 106.0,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3661": 156.9,
        "3443": 122.4
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
  "as_of": "2026-10-08",
  "per": 29.56,
  "per_pct": 83.1,
  "per_then": 28.63,
  "per_pct_then": 77.1,
  "pbr": 10.28,
  "dividend_yield": 0.86,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **6** 筆；state 已有 outcomes 的 entry：**27/27**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*