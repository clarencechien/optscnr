# TSMC Radar (2330.TW) — 2026-10-29 10:57 UTC

## 總判定：🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 -2.4%）；PER 28.0，3 年分位 77 → 70

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +18.4%（1 年第 44 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3675.7M, YoY +60.6% |
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:12e(13m) / n2_arizona_ramp:18e(25m) / cowos_capacity:8e / geopolitics:1e / hyperscaler_capex:9e(10m) |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 1（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 28.0（3 年第 70 百分位；20 日前第 77）；觀察 |

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
  "as_of": "2026-10-29",
  "premium_pct": 18.42,
  "percentile_1y": 44.0,
  "n": 369
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

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 12,
    "n2_arizona_ramp": 18,
    "cowos_capacity": 8,
    "geopolitics": 1,
    "hyperscaler_capex": 9
  },
  "mentions": {
    "export_controls_tariffs": 13,
    "n2_arizona_ramp": 25,
    "cowos_capacity": 8,
    "geopolitics": 1,
    "hyperscaler_capex": 10
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 12,
      "mentions": 13,
      "gate": "zscore",
      "z": -1.31,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 18,
      "mentions": 25,
      "gate": "zscore",
      "z": 3.26,
      "denial": true
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": 1.79,
      "denial": false
    },
    "geopolitics": {
      "events": 1,
      "mentions": 1,
      "gate": "zscore",
      "z": -1.79,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 9,
      "mentions": 10,
      "gate": "zscore",
      "z": 1.92,
      "denial": false
    }
  }
}
```
- [n2_arizona_ramp] 官方否認偵測 → 上限 🟡（爭議中）
- [export_controls_tariffs] TSMC is seeking chipmaking equipment that doesn't contain Chinese rare-earth magnets — asks suppliers to provide alterna
- [export_controls_tariffs] TSMC Seeks Rare-Earth-Free Factory Equipment as China’s Export Controls Threaten Chip Supply Chains - Tekedia
- [export_controls_tariffs] How Taiwan’s Chip Industry Navigates US Industrial Policy and Export Controls - Global Taiwan Institute
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Intel and Samsung advance 2nm GAA, but yield gaps leave TSMC as the sole external supplier - digitimes
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Beth Kindig – Medium
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - Yahoo Finance
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review

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
        "3711": 44.8,
        "3037": 54.9,
        "2383": 142.7
      }
    },
    "asic_lead": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 50.9,
      "best_peer": "3661",
      "best_peer_3m_yoy": 317.1,
      "peer_lead_pp": 266.2,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3661": 317.1,
        "3443": 122.4
      }
    }
  }
}
```

### M8 revision_velocity — ⚪ NO_DATA
```json
{
  "up_hits": 1,
  "down_hits": 0,
  "total": 1,
  "down_ratio": 0.0
}
```

### M9 valuation — 🟢 GREEN
```json
{
  "as_of": "2026-10-29",
  "per": 27.99,
  "per_pct": 69.5,
  "per_then": 28.69,
  "per_pct_then": 77.2,
  "pbr": 9.74,
  "dividend_yield": 0.91,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**50/50**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 6 / +0.70 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 6 / +0.70 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 5 / +0.71 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 1 / +0.38 | 11 / +0.73 | 24 | 累積中（GREEN n=1 < 30）；方向反 |
| M6 | 6 / +0.70 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*