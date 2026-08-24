# Delta Radar (2308.TW) — 2026-08-24 04:13 UTC

## 總判定：🟡 YELLOW

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-07 YoY +47.7%, slope +1.28pp/月, 連續減速 1 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32 |
| M3 thai_shadow | 🟡 YELLOW | DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8% |
| M4 customs_flow | ⚪ NO_DATA | Census fetch failed after 2 tries |
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:6e / vr300_delay:16e(18m) / debt_financed_capex:11e / lc_psu_competition:0e |
| M6 peer_divergence | 🟡 YELLOW | cooling:3324領先+42pp |
| M8 revision_velocity | 🟢 GREEN | 下修 0/上修 0（樣本不足 <3，暫不評級） |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-07",
  "latest_yoy_pct": 47.7,
  "yoy_slope_pp_per_month": 1.28,
  "consecutive_decel_months": 1
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

### M4 customs_flow — ⚪ NO_DATA
- raw/exception: The read operation timed out
- ⚠️ degraded: Census fetch failed after 2 tries

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 6,
    "vr300_delay": 16,
    "debt_financed_capex": 11,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 6,
    "vr300_delay": 18,
    "debt_financed_capex": 11,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": -0.07,
      "denial": false
    },
    "vr300_delay": {
      "events": 16,
      "mentions": 18,
      "gate": "zscore",
      "z": 1.56,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 11,
      "mentions": 11,
      "gate": "zscore",
      "z": -3.02,
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
- [capex_cut] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [capex_cut] Will the next recession be caused by an AI capex cut-off? - investordaily.com.au
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] Jensen Huang Takes Stage at Morgan Stanley Roadshow: Quarterly Revenue Nears $100 Billion, Nvidia Denies Rubin Ultra Del
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - Yahoo Finance
- [debt_financed_capex] The growing jitters over hyperscaler debt - Axios
- [debt_financed_capex] After a nearly 1,000% surge, the AI debt orgy can’t last forever, while hidden borrowing has exploded to $1.65 trillion 

### M6 peer_divergence — 🟡 YELLOW
```json
{
  "groups": {
    "power": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 48.9,
      "best_peer": "2301",
      "best_peer_3m_yoy": 34.7,
      "peer_lead_pp": -14.2,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2301": 34.7,
        "6282": 32.3
      }
    },
    "cooling": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 48.9,
      "best_peer": "3324",
      "best_peer_3m_yoy": 90.9,
      "peer_lead_pp": 41.9,
      "status": "YELLOW",
      "peers_3m_yoy": {
        "3324": 90.9,
        "3017": 61.4
      }
    },
    "rack": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 48.9,
      "best_peer": "2382",
      "best_peer_3m_yoy": 109.5,
      "peer_lead_pp": 60.6,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2317": 48.6,
        "2382": 109.5,
        "6669": 29.1
      }
    }
  }
}
```
- [cooling] 3324 3m YoY 90.9% vs 2308 48.9%（領先 +42pp）

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
- 本次回填 **5** 筆；state 已有 outcomes 的 entry：**87/87**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*