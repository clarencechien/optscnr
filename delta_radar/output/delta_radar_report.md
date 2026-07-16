# Delta Radar (2308.TW) — 2026-07-16 05:58 UTC

## 總判定：🟡 YELLOW

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-06 YoY +55.4%, slope +5.94pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟡 YELLOW | 合約負債 QoQ +7.4% / 存貨 QoQ +17.4% / FCF/淨利 0.37 |
| M3 thai_shadow | 🟢 GREEN | DELTA.BK 2026-03-31 營收 YoY +47.0%, GM 31.7% |
| M4 customs_flow | 🟢 GREEN | US 進口 HS850440 (TH+TW) 近3月 $1360.1M, YoY +50.5% |
| M5 narrative_triggers | 🟢 GREEN | capex_cut:4e / vr300_delay:12e(19m) / debt_financed_capex:16e / lc_psu_competition:0e |
| M6 peer_divergence | 🟡 YELLOW | cooling:3017領先+18pp |
| M8 revision_velocity | 🟢 GREEN | 下修 0/上修 0（樣本不足 <3，暫不評級） |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-06",
  "latest_yoy_pct": 55.4,
  "yoy_slope_pp_per_month": 5.94,
  "consecutive_decel_months": 0
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
    "capex_cut": 4,
    "vr300_delay": 12,
    "debt_financed_capex": 16,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 4,
    "vr300_delay": 19,
    "debt_financed_capex": 16,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": 1.08,
      "denial": false
    },
    "vr300_delay": {
      "events": 12,
      "mentions": 19,
      "gate": "zscore",
      "z": -0.69,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 16,
      "mentions": 16,
      "gate": "zscore",
      "z": -1.21,
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
- [capex_cut] Can Sovereign AI Buffer Nvidia Against a Potential Hyperscaler Slowdown? - Trefis
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] NVDA Stock Climbs Over 1% — Nvidia Says Its AI ‘Roadmap Is Intact’ After Report Of Kyber Rack Delay - Stocktwits
- [vr300_delay] Huang Renxun Takes the Stage in Tokyo to Refute Nvidia Vera Rubin Chip Delay Rumors - finance.biggo.com
- [debt_financed_capex] Amazon’s $25 Billion Bond Sale: Is the AI-Debt Boom a Warning Sign or a Smart Way to Bankroll a Build-Out? - MarketWise
- [debt_financed_capex] Amazon Is Borrowing Another $25 Billion for AI, and Promises This Is the Last Time This Year - 24/7 Wall St.
- [debt_financed_capex] Oracle's AI spending blows past estimates, raising worries over growing debt - Reuters

### M6 peer_divergence — 🟡 YELLOW
```json
{
  "groups": {
    "power": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 47.7,
      "best_peer": "2301",
      "best_peer_3m_yoy": 30.3,
      "peer_lead_pp": -17.3,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2301": 30.3,
        "6282": 29.7
      }
    },
    "cooling": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 47.7,
      "best_peer": "3017",
      "best_peer_3m_yoy": 66.1,
      "peer_lead_pp": 18.5,
      "status": "YELLOW",
      "peers_3m_yoy": {
        "3324": 65.6,
        "3017": 66.1
      }
    },
    "rack": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 47.7,
      "best_peer": "2382",
      "best_peer_3m_yoy": 106.0,
      "peer_lead_pp": 58.3,
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
- [cooling] 3017 3m YoY 66.1% vs 2308 47.7%（領先 +18pp）

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
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**47/47**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*