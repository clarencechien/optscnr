# Delta Radar (2308.TW) — 2026-08-10 05:01 UTC

## 總判定：🟡 YELLOW

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-06 YoY +55.4%, slope +5.94pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32 |
| M3 thai_shadow | 🟡 YELLOW | DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8% |
| M4 customs_flow | 🟢 GREEN | US 進口 HS850440 (TH+TW) 近3月 $1426.7M, YoY +41.0% |
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:6e(7m) / vr300_delay:15e(19m) / debt_financed_capex:12e / lc_psu_competition:0e |
| M6 peer_divergence | 🟡 YELLOW | cooling:3324領先+43pp |
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
  "window": "2026-04..2026-06",
  "rolling_value_usd_m": 1426.7,
  "rolling_yoy_pct": 41.0,
  "by_country": {
    "THAILAND": {
      "rolling_value_usd_m": 871.4,
      "rolling_yoy_pct": 30.6
    },
    "TAIWAN": {
      "rolling_value_usd_m": 555.3,
      "rolling_yoy_pct": 61.1
    }
  }
}
```

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 6,
    "vr300_delay": 15,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 7,
    "vr300_delay": 19,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 6,
      "mentions": 7,
      "gate": "absolute",
      "z": null,
      "denial": false
    },
    "vr300_delay": {
      "events": 15,
      "mentions": 19,
      "gate": "zscore",
      "z": -0.17,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 12,
      "mentions": 12,
      "gate": "zscore",
      "z": -0.94,
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
- [capex_cut] Apple’s AI Strategy: A Different Approach Amidst Hyperscaler Capex Slowdown - Dividend Earnings Report - po-news-eg.net
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia’s Kyber AI rack slips to 2028, and one circuit board is to blame - thenextweb.com
- [vr300_delay] Nvidia Kyber NVL144 Slips to 2028 as Physics, Not Software, Defeats the Backup Plan - Tech Times
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - Yahoo Finance
- [debt_financed_capex] The growing jitters over hyperscaler debt - Axios
- [debt_financed_capex] Will Moody's AI Debt Warning Trigger an AI Bubble Crash? - roddubitsky.substack.com

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
      "best_peer": "3324",
      "best_peer_3m_yoy": 90.9,
      "peer_lead_pp": 43.2,
      "status": "YELLOW",
      "peers_3m_yoy": {
        "3324": 90.9,
        "3017": 61.4
      }
    },
    "rack": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 47.7,
      "best_peer": "2382",
      "best_peer_3m_yoy": 109.5,
      "peer_lead_pp": 61.9,
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
- [cooling] 3324 3m YoY 90.9% vs 2308 47.7%（領先 +43pp）

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
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**70/70**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*