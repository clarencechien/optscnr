# TSMC Radar (2330.TW) — 2026-10-19 10:00 UTC

## 總判定：🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +1.7%）；PER 28.1，3 年分位 67 → 71

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +10.6%（1 年第 5 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3675.7M, YoY +60.6% |
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:16e / n2_arizona_ramp:10e(11m) / cowos_capacity:4e / geopolitics:5e / hyperscaler_capex:6e |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 28.1（3 年第 71 百分位；20 日前第 67）；觀察 |

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
  "as_of": "2026-10-19",
  "premium_pct": 10.55,
  "percentile_1y": 5.1,
  "n": 370
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
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 10,
    "cowos_capacity": 4,
    "geopolitics": 5,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 11,
    "cowos_capacity": 4,
    "geopolitics": 5,
    "hyperscaler_capex": 6
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 16,
      "mentions": 16,
      "gate": "zscore",
      "z": 0.68,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 10,
      "mentions": 11,
      "gate": "zscore",
      "z": 0.0,
      "denial": false
    },
    "cowos_capacity": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": -0.37,
      "denial": false
    },
    "geopolitics": {
      "events": 5,
      "mentions": 5,
      "gate": "zscore",
      "z": 1.32,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": 0.48,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [n2_arizona_ramp] DIGITIMES Insight: Microsoft Maia 300 leads 2nm race, TSMC's US strategy shifts, Intel EMIB-T faces yield challenge - di
- [n2_arizona_ramp] Samsung's 2nm Yield Approaches 60%, Leveraging Tesla Orders to Challenge TSMC - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Medium
- [cowos_capacity] [News] While TSMC’s CoWoS Faces Supply Shortage, Samsung Reportedly Secures NVIDIA’s 2.5D Advanced Packaging Order - Tre
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
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
  "up_hits": 0,
  "down_hits": 0,
  "total": 0,
  "down_ratio": null
}
```

### M9 valuation — 🟢 GREEN
```json
{
  "as_of": "2026-10-19",
  "per": 28.05,
  "per_pct": 70.7,
  "per_then": 27.59,
  "per_pct_then": 66.8,
  "pbr": 9.76,
  "dividend_yield": 0.91,
  "history_years": 3,
  "n": 734
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**40/40**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 3 / +0.65 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 3 / +0.65 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 2 / +0.65 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 0 / — | 5 / +0.30 | 17 | 樣本不足（缺一側 cohort） |
| M6 | 3 / +0.65 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*