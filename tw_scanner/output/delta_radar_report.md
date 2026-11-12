# Delta Radar (2308.TW) — 2026-11-12 11:50 UTC

## 總判定：🟡 YELLOW

## 🔀 前提 vs 價格：🔀 背離：前提健在（YELLOW）、價格 20 日 -30.1% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 37.2，3 年分位 77 → 59

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-10 YoY +30.1%, slope -5.88pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74 |
| M3 thai_shadow | 🟢 GREEN | DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3% |
| M4 customs_flow | 🟡 YELLOW | US 進口 HS850440 (TH+TW) 近3月 $1376.6M, YoY +19.9% |
| M5 narrative_triggers | 🟢 GREEN | capex_cut:6e / vr300_delay:8e / debt_financed_capex:10e(11m) / lc_psu_competition:0e |
| M6 peer_divergence | 🟡 YELLOW | cooling:3324領先+18pp |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 37.2（3 年第 59 百分位；20 日前第 77）；觀察 |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-10",
  "latest_yoy_pct": 30.1,
  "yoy_slope_pp_per_month": -5.88,
  "consecutive_decel_months": 0
}
```

### M2 bullwhip_health — 🟢 GREEN
```json
{
  "as_of": "2026-09-30",
  "contract_liab_qoq_pct": 35.3,
  "inventory_qoq_pct": 20.7,
  "fcf_to_net_income": 1.74,
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
  "latest_q": "2026-09-30",
  "rev_yoy_pct": 42.4,
  "gross_margin_pct": 27.3
}
```

### M4 customs_flow — 🟡 YELLOW
```json
{
  "window": "2026-07..2026-09",
  "rolling_value_usd_m": 1376.6,
  "rolling_yoy_pct": 19.9,
  "by_country": {
    "THAILAND": {
      "rolling_value_usd_m": 881.2,
      "rolling_yoy_pct": 15.2
    },
    "TAIWAN": {
      "rolling_value_usd_m": 495.4,
      "rolling_yoy_pct": 29.3
    }
  }
}
```

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 6,
    "vr300_delay": 8,
    "debt_financed_capex": 10,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 6,
    "vr300_delay": 8,
    "debt_financed_capex": 11,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": 0.65,
      "denial": false
    },
    "vr300_delay": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": -0.32,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 10,
      "mentions": 11,
      "gate": "zscore",
      "z": -1.76,
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
- [capex_cut] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - The Motley Fool
- [capex_cut] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [capex_cut] Will the next recession be caused by an AI capex cut-off? - InvestorDaily
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch. - CNBC
- [debt_financed_capex] Top hyperscalers likely to have more AI-linked debt than now known, S&P Global warns - Reuters
- [debt_financed_capex] Oracle's Negative Free Cash Flow Exposes the Uncomfortable Truth About AI's Financing Game - 24/7 Wall St.

### M6 peer_divergence — 🟡 YELLOW
```json
{
  "groups": {
    "power": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 26.6,
      "best_peer": "6282",
      "best_peer_3m_yoy": 31.5,
      "peer_lead_pp": 4.9,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2301": 26.5,
        "6282": 31.5
      }
    },
    "cooling": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 26.6,
      "best_peer": "3324",
      "best_peer_3m_yoy": 45.1,
      "peer_lead_pp": 18.5,
      "status": "YELLOW",
      "peers_3m_yoy": {
        "3324": 45.1,
        "3017": 44.5
      }
    },
    "rack": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 26.6,
      "best_peer": "2382",
      "best_peer_3m_yoy": 119.4,
      "peer_lead_pp": 92.8,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2317": 45.4,
        "2382": 119.4,
        "6669": 77.1
      }
    }
  }
}
```
- [cooling] 3324 3m YoY 45.1% vs 2308 26.6%（領先 +18pp）

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
  "as_of": "2026-11-12",
  "per": 37.24,
  "per_pct": 58.9,
  "per_then": 56.49,
  "per_pct_then": 77.0,
  "pbr": 10.12,
  "dividend_yield": 0.94,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**163/163**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 16 / -12.89 | 3 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M2 | 28 / -9.85 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 23 / -7.09 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 41 / -8.59 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M5 | 56 / -6.40 | 65 / -10.55 | 47 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 33 / -6.39 | 5 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*