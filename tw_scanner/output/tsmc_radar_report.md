# TSMC Radar (2330.TW) — 2026-10-05 11:37 UTC

## 總判定：🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +7.7%）；PER 29.9，3 年分位 69 → 85

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-08 YoY +53.3%, slope +7.74pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +16.6%（1 年第 33 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3643.7M, YoY +58.0% |
| M5 narrative_triggers | ⚪ NO_DATA | all RSS feeds failed |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | revision feed failed: HTTP Error 503: Service Unavailable |
| M9 valuation（觀察） | 🟢 GREEN | PER 29.9（3 年第 85 百分位；20 日前第 69）；觀察 |

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
  "as_of": "2026-10-05",
  "premium_pct": 16.55,
  "percentile_1y": 32.8,
  "n": 370
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

### M5 narrative_triggers — ⚪ NO_DATA
- feed export_controls_tariffs failed: HTTP Error 503: Service Unavailable
- feed n2_arizona_ramp failed: HTTP Error 503: Service Unavailable
- feed cowos_capacity failed: HTTP Error 503: Service Unavailable
- feed geopolitics failed: HTTP Error 503: Service Unavailable
- feed hyperscaler_capex failed: HTTP Error 503: Service Unavailable
- ⚠️ degraded: all RSS feeds failed

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
      "best_peer_3m_yoy": 142.7,
      "peer_lead_pp": 87.4,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3711": 40.6,
        "3037": 45.4,
        "2383": 142.7
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
        "3443": 122.4
      }
    }
  }
}
```

### M8 revision_velocity — ⚪ NO_DATA
- ⚠️ degraded: revision feed failed: HTTP Error 503: Service Unavailable

### M9 valuation — 🟢 GREEN
```json
{
  "as_of": "2026-10-05",
  "per": 29.85,
  "per_pct": 85.2,
  "per_then": 27.7,
  "per_pct_then": 69.0,
  "pbr": 10.38,
  "dividend_yield": 0.85,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**25/25**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*