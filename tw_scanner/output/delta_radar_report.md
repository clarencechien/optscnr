# Delta Radar (2308.TW) — 2026-09-21 09:17 UTC

## 總判定：🔴 RED

## 🔀 前提 vs 價格：🔀 反向背離：前提轉紅、價格 20 日 +8.1% 未跌 —— 市場不買儀器的帳，或儀器誤判；PER 55.2，3 年分位 79 → 78

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟡 YELLOW | 2026-08 YoY +34.9%, slope -2.90pp/月, 連續減速 2 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32 |
| M3 thai_shadow | 🟡 YELLOW | DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8% |
| M4 customs_flow | 🟢 GREEN | US 進口 HS850440 (TH+TW) 近3月 $1399.9M, YoY +30.6% |
| M5 narrative_triggers | 🔴 RED | capex_cut:5e(6m) / vr300_delay:18e(21m) / debt_financed_capex:15e / lc_psu_competition:0e |
| M6 peer_divergence | 🔴 RED | cooling:3324領先+36pp |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 55.2（3 年第 78 百分位；20 日前第 79）；觀察 |

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

### M5 narrative_triggers — 🔴 RED
```json
{
  "events": {
    "capex_cut": 5,
    "vr300_delay": 18,
    "debt_financed_capex": 15,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 6,
    "vr300_delay": 21,
    "debt_financed_capex": 15,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 5,
      "mentions": 6,
      "gate": "zscore",
      "z": 2.85,
      "denial": false
    },
    "vr300_delay": {
      "events": 18,
      "mentions": 21,
      "gate": "zscore",
      "z": 0.19,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 15,
      "mentions": 15,
      "gate": "zscore",
      "z": 1.54,
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
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - finance.yahoo.c
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] Apollo Just Flashed Yellow on Hyperscaler Debt - Money Morning
- [debt_financed_capex] Apollo Warns Hyperscaler Debt Is Getting Riskier as AI Spending Strains Balance Sheets - finance.biggo.com
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - finance.yahoo.com

### M6 peer_divergence — 🔴 RED
```json
{
  "groups": {
    "power": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 46.0,
      "best_peer": "6282",
      "best_peer_3m_yoy": 36.4,
      "peer_lead_pp": -9.6,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2301": 33.3,
        "6282": 36.4
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
  "as_of": "2026-09-18",
  "per": 55.22,
  "per_pct": 78.2,
  "per_then": 55.7,
  "per_pct_then": 79.4,
  "pbr": 15.34,
  "dividend_yield": 0.67,
  "history_years": 3,
  "n": 734
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**115/115**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 43 / -8.20 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M2 | 14 / -9.54 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 9 / -2.32 | 1 | 無法判定（狀態翻轉 1 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 28 / -7.60 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 28 / -2.92 | 48 / -9.72 | 38 | 累積中（GREEN n=28 < 30）；方向對 |
| M6 | 0 / — | 19 / -3.62 | 1 | 樣本不足（缺一側 cohort） |
| M8 | 19 / -3.62 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*