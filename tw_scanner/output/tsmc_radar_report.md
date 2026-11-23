# TSMC Radar (2330.TW) — 2026-11-23 14:51 UTC

## 總判定：🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（GREEN）、價格 20 日 -14.9% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 20.7，3 年分位 65 → 16

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-10 YoY +59.7%, slope +5.01pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +11.0% / FCF/淨利 1.46 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +17.6%（1 年第 42 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3666.0M, YoY +65.1% |
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:12e(15m) / n2_arizona_ramp:23e(28m) / cowos_capacity:7e / geopolitics:1e / hyperscaler_capex:3e |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 20.7（3 年第 16 百分位；20 日前第 65）；觀察 |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-10",
  "latest_yoy_pct": 59.7,
  "yoy_slope_pp_per_month": 5.01,
  "consecutive_decel_months": 0
}
```

### M2 bullwhip_health — 🟢 GREEN
```json
{
  "as_of": null,
  "contract_liab_qoq_pct": null,
  "inventory_qoq_pct": 11.0,
  "fcf_to_net_income": 1.46,
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
  "as_of": "2026-11-23",
  "premium_pct": 17.58,
  "percentile_1y": 41.7,
  "n": 370
}
```

### M4 customs_flow — 🟢 GREEN
```json
{
  "window": "2026-07..2026-09",
  "rolling_value_usd_m": 3666.0,
  "rolling_yoy_pct": 65.1,
  "by_country": {
    "TAIWAN": {
      "rolling_value_usd_m": 3666.0,
      "rolling_yoy_pct": 65.1
    }
  }
}
```

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "export_controls_tariffs": 12,
    "n2_arizona_ramp": 23,
    "cowos_capacity": 7,
    "geopolitics": 1,
    "hyperscaler_capex": 3
  },
  "mentions": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 28,
    "cowos_capacity": 7,
    "geopolitics": 1,
    "hyperscaler_capex": 3
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 12,
      "mentions": 15,
      "gate": "zscore",
      "z": -1.54,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 23,
      "mentions": 28,
      "gate": "zscore",
      "z": 0.8,
      "denial": true
    },
    "cowos_capacity": {
      "events": 7,
      "mentions": 7,
      "gate": "zscore",
      "z": 0.0,
      "denial": false
    },
    "geopolitics": {
      "events": 1,
      "mentions": 1,
      "gate": "zscore",
      "z": -1.38,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -0.67,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] Apple supplier TSMC cuts off China chip orders amid tighter export controls - AppleInsider
- [export_controls_tariffs] Chip supply chain warns of broader disruption from new US export controls - Nikkei Asia
- [export_controls_tariffs] TSMC and Samsung pause some chip shipments to China due to tighter US export controls - Digital Watch Observatory
- [n2_arizona_ramp] AMD Zen 6 Olympic Ridge Desktop CPUs Reportedly Slip Past Computex 2027 After A Switch To TSMC’s Performance-Focused N2X
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [cowos_capacity] [News] While TSMC’s CoWoS Faces Supply Shortage, Samsung Reportedly Secures NVIDIA’s 2.5D Advanced Packaging Order - Tre
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - The Motley Fool
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Will the next recession be caused by an AI capex cut-off? - InvestorDaily

### M6 peer_divergence — 🟢 GREEN
```json
{
  "groups": {
    "foundry_contrast": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 55.9,
      "best_peer": "2303",
      "best_peer_3m_yoy": 25.4,
      "peer_lead_pp": -30.5,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2303": 25.4
      }
    },
    "backend": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 55.9,
      "best_peer": "2383",
      "best_peer_3m_yoy": 167.3,
      "peer_lead_pp": 111.4,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3711": 46.1,
        "3037": 62.8,
        "2383": 167.3
      }
    },
    "asic_lead": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 55.9,
      "best_peer": "3661",
      "best_peer_3m_yoy": 428.5,
      "peer_lead_pp": 372.6,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3661": 428.5,
        "3443": 111.9
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
  "as_of": "2026-11-23",
  "per": 20.66,
  "per_pct": 16.4,
  "per_then": 27.65,
  "per_pct_then": 64.6,
  "pbr": 7.52,
  "dividend_yield": 1.08,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **7** 筆；state 已有 outcomes 的 entry：**75/75**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 17 / +2.38 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 14 / +1.95 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 13 / +2.05 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 16 / +2.91 | 23 / +1.67 | 40 | 累積中（GREEN n=16 < 30）；方向對 |
| M6 | 14 / +1.95 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*