# Delta Radar (2308.TW) — 2026-09-10 08:24 UTC

## 總判定：🟡 YELLOW

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟡 YELLOW | 2026-08 YoY +34.9%, slope -2.90pp/月, 連續減速 2 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32 |
| M3 thai_shadow | 🟡 YELLOW | DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8% |
| M4 customs_flow | 🟢 GREEN | US 進口 HS850440 (TH+TW) 近3月 $1399.9M, YoY +30.6% |
| M5 narrative_triggers | 🟢 GREEN | capex_cut:4e(5m) / vr300_delay:19e(22m) / debt_financed_capex:11e(12m) / lc_psu_competition:0e |
| M6 peer_divergence | 🔴 RED | cooling:3324領先+36pp |
| M8 revision_velocity | 🟢 GREEN | 下修 0/上修 0（樣本不足 <3，暫不評級） |

### M1 revenue_acceleration — 🟡 YELLOW
```json
{
  "latest_month": "2026-08",
  "latest_yoy_pct": 34.9,
  "yoy_slope_pp_per_month": -2.9,
  "consecutive_decel_months": 2
}
```

### M2 bullwhip_health — 🟢 GREEN
```json
{
  "as_of": "2026-06-30",
  "contract_liab_qoq_pct": 17.3,
  "inventory_qoq_pct": 17.0,
  "fcf_to_net_income": 1.32,
  "accounts_used": {
    "contract": "CurrentContractLiabilities",
    "inventory": "Inventories",
    "ocf": "CashFlowsFromOperatingActivities",
    "capex": "PropertyAndPlantAndEquipment",
    "net_income": "IncomeAfterTaxes"
  }
}
```

### M3 thai_shadow — 🟡 YELLOW
```json
{
  "latest_q": "2026-06-30",
  "rev_yoy_pct": 52.5,
  "gross_margin_pct": 26.8
}
```
- 泰子公司毛利率 26.8% 跌破 27.0% 地板

### M4 customs_flow — 🟢 GREEN
```json
{
  "window": "2026-05..2026-07",
  "rolling_value_usd_m": 1399.9,
  "rolling_yoy_pct": 30.6,
  "by_country": {
    "THAILAND": {
      "rolling_value_usd_m": 866.5,
      "rolling_yoy_pct": 22.9
    },
    "TAIWAN": {
      "rolling_value_usd_m": 533.4,
      "rolling_yoy_pct": 45.3
    }
  }
}
```

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 4,
    "vr300_delay": 19,
    "debt_financed_capex": 11,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 5,
    "vr300_delay": 22,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 4,
      "mentions": 5,
      "gate": "zscore",
      "z": 0.25,
      "denial": false
    },
    "vr300_delay": {
      "events": 19,
      "mentions": 22,
      "gate": "zscore",
      "z": 1.19,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 11,
      "mentions": 12,
      "gate": "zscore",
      "z": -1.27,
      "denial": false
    },
    "lc_psu_competition": {
      "events": 0,
      "mentions": 0,
      "gate": "absolute",
      "z": null,
      "denial": false
    }
  }
}
```
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] AI Boom Triggers Tech Debt Binge - StartupHub.ai
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - Yahoo Finance
- [debt_financed_capex] What the $489B AI Debt Wave Means for Treasury Risk - The Global Treasurer

### M6 peer_divergence — 🔴 RED
```json
{
  "groups": {
    "power": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 46.0,
      "best_peer": "2301",
      "best_peer_3m_yoy": 33.3,
      "peer_lead_pp": -12.8,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2301": 33.3,
        "6282": 32.3
      }
    },
    "cooling": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 46.0,
      "best_peer": "3324",
      "best_peer_3m_yoy": 82.0,
      "peer_lead_pp": 36.0,
      "status": "RED",
      "peers_3m_yoy": {
        "3324": 82.0,
        "3017": 59.3
      }
    },
    "rack": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 46.0,
      "best_peer": "2382",
      "best_peer_3m_yoy": 137.2,
      "peer_lead_pp": 91.2,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2317": 52.8,
        "2382": 137.2,
        "6669": 39.8
      }
    }
  }
}
```
- [cooling] 3324 3m YoY 82.0% vs 2308 46.0%（領先 +36pp）

### M8 revision_velocity — 🟢 GREEN
```json
{
  "up_hits": 0,
  "down_hits": 0,
  "total": 0,
  "down_ratio": null
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **8** 筆；state 已有 outcomes 的 entry：**100/100**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*