# Delta Radar (2308.TW) — 2026-07-09 06:40 UTC

## 總判定：🟡 YELLOW

GS 4500 劇本三大未驗證前提的機械化監控：FCF 轉回 (M2)、合約負債續航 (M2)、
實體出貨上船 (M3/M4)，外加營收動能 (M1) 與敘事風險 (M5)。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-05 YoY +43.7%, slope +4.22pp/月, 連續減速 1 個月 |
| M2 bullwhip_health | 🟡 YELLOW | 合約負債 QoQ +7.4% / 存貨 QoQ +17.4% / FCF/淨利 0.37 |
| M3 thai_shadow | 🟢 GREEN | DELTA.BK 2026-03-31 營收 YoY +47.0%, GM 31.7% |
| M4 customs_flow | 🟢 GREEN | US 進口 HS850440 (TH+TW) 近3月 $1360.1M, YoY +50.5% |
| M5 narrative_triggers | 🟢 GREEN | capex_cut:3e / vr300_delay:15e(25m) / debt_financed_capex:16e / lc_psu_competition:0e |
| M6 peer_divergence | 🟡 YELLOW | cooling:3017領先+24pp |
| M8 revision_velocity | 🟢 GREEN | 下修 0/上修 0（樣本不足 <3，暫不評級） |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-05",
  "latest_yoy_pct": 43.7,
  "yoy_slope_pp_per_month": 4.22,
  "consecutive_decel_months": 1
}
```

### M2 bullwhip_health — 🟡 YELLOW
```json
{
  "as_of": "2026-03-31",
  "contract_liab_qoq_pct": 7.4,
  "inventory_qoq_pct": 17.4,
  "fcf_to_net_income": 0.37,
  "accounts_used": {
    "contract": "CurrentContractLiabilities",
    "inventory": "Inventories",
    "ocf": "CashFlowsFromOperatingActivities",
    "capex": "PropertyAndPlantAndEquipment",
    "net_income": "IncomeAfterTaxes"
  }
}
```

### M3 thai_shadow — 🟢 GREEN
```json
{
  "latest_q": "2026-03-31",
  "rev_yoy_pct": 47.0,
  "gross_margin_pct": 31.7
}
```

### M4 customs_flow — 🟢 GREEN
```json
{
  "window": "2026-03..2026-05",
  "rolling_value_usd_m": 1360.1,
  "rolling_yoy_pct": 50.5,
  "by_country": {
    "THAILAND": {
      "rolling_value_usd_m": 871.7,
      "rolling_yoy_pct": 48.6
    },
    "TAIWAN": {
      "rolling_value_usd_m": 488.4,
      "rolling_yoy_pct": 54.0
    }
  }
}
```

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 3,
    "vr300_delay": 15,
    "debt_financed_capex": 16,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 3,
    "vr300_delay": 25,
    "debt_financed_capex": 16,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -2.92,
      "denial": false
    },
    "vr300_delay": {
      "events": 15,
      "mentions": 25,
      "gate": "zscore",
      "z": 1.32,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 16,
      "mentions": 16,
      "gate": "zscore",
      "z": 0.69,
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
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due for a Pause - Investing.com
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [capex_cut] 'The odd decouple': JPMorgan says the tech capex surge is masking a troubling slowdown in job growth - Business Insider
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [vr300_delay] Nvidia's Kyber NVL144 reportedly pushed back more than a year, Asian suppliers drop - the-decoder.com
- [debt_financed_capex] Forget the AI bubble. The IMF says the real threat is the mountain of debt behind it — and 60% of planned data centers h
- [debt_financed_capex] Amazon Is Borrowing Another $25 Billion for AI, and Promises This Is the Last Time This Year - 24/7 Wall St.
- [debt_financed_capex] Oracle's AI spending blows past estimates, raising worries over growing debt - Reuters

### M6 peer_divergence — 🟡 YELLOW
```json
{
  "groups": {
    "power": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 41.7,
      "best_peer": "6282",
      "best_peer_3m_yoy": 26.0,
      "peer_lead_pp": -15.7,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2301": 25.8,
        "6282": 26.0
      }
    },
    "cooling": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 41.7,
      "best_peer": "3017",
      "best_peer_3m_yoy": 66.1,
      "peer_lead_pp": 24.4,
      "status": "YELLOW",
      "peers_3m_yoy": {
        "3324": 65.6,
        "3017": 66.1
      }
    },
    "rack": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 41.7,
      "best_peer": "2382",
      "best_peer_3m_yoy": 106.0,
      "peer_lead_pp": 64.3,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2317": 40.5,
        "2382": 106.0,
        "6669": 25.9
      }
    }
  }
}
```
- [cooling] 3017 3m YoY 66.1% vs 2308 41.7%（領先 +24pp）

### M8 revision_velocity — 🟢 GREEN
```json
{
  "up_hits": 0,
  "down_hits": 0,
  "total": 0,
  "down_ratio": null
}
```

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*