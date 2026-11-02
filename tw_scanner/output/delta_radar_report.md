# Delta Radar (2308.TW) — 2026-11-02 11:41 UTC

## 總判定：🔴 RED

## 前提 vs 價格：無背離（前提 RED、價格 20 日 -28.3%）；PER 40.7，3 年分位 83 → 61

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🔴 RED | 2026-09 YoY +14.6%, slope -13.60pp/月, 連續減速 3 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74 |
| M3 thai_shadow | 🟢 GREEN | DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3% |
| M4 customs_flow | 🟢 GREEN | US 進口 HS850440 (TH+TW) 近3月 $1366.7M, YoY +22.4% |
| M5 narrative_triggers | 🟢 GREEN | capex_cut:6e(7m) / vr300_delay:8e(9m) / debt_financed_capex:11e(13m) / lc_psu_competition:0e |
| M6 peer_divergence | 🔴 RED | cooling:3324領先+37pp |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 40.7（3 年第 61 百分位；20 日前第 83）；觀察 |

### M1 revenue_acceleration — 🔴 RED
```json
{
  "latest_month": "2026-09",
  "latest_yoy_pct": 14.6,
  "yoy_slope_pp_per_month": -13.6,
  "consecutive_decel_months": 3
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

### M4 customs_flow — 🟢 GREEN
```json
{
  "window": "2026-06..2026-08",
  "rolling_value_usd_m": 1366.7,
  "rolling_yoy_pct": 22.4,
  "by_country": {
    "THAILAND": {
      "rolling_value_usd_m": 840.7,
      "rolling_yoy_pct": 11.8
    },
    "TAIWAN": {
      "rolling_value_usd_m": 526.0,
      "rolling_yoy_pct": 44.1
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
    "debt_financed_capex": 11,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 7,
    "vr300_delay": 9,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 6,
      "mentions": 7,
      "gate": "zscore",
      "z": -0.19,
      "denial": false
    },
    "vr300_delay": {
      "events": 8,
      "mentions": 9,
      "gate": "zscore",
      "z": -4.12,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 11,
      "mentions": 13,
      "gate": "zscore",
      "z": -1.56,
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
- [capex_cut] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch. - CNBC
- [debt_financed_capex] Top hyperscalers likely to have more AI-linked debt than now known, S&P Global warns - Reuters
- [debt_financed_capex] AI Debt Nears $500 Billion: Nvidia, Oracle & CoreWeave - I/O Fund

### M6 peer_divergence — 🔴 RED
```json
{
  "groups": {
    "power": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 32.4,
      "best_peer": "6282",
      "best_peer_3m_yoy": 34.8,
      "peer_lead_pp": 2.4,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2301": 28.3,
        "6282": 34.8
      }
    },
    "cooling": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 32.4,
      "best_peer": "3324",
      "best_peer_3m_yoy": 69.0,
      "peer_lead_pp": 36.6,
      "status": "RED",
      "peers_3m_yoy": {
        "3324": 69.0,
        "3017": 52.2
      }
    },
    "rack": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 32.4,
      "best_peer": "2382",
      "best_peer_3m_yoy": 128.5,
      "peer_lead_pp": 96.1,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2317": 48.2,
        "2382": 128.5,
        "6669": 63.2
      }
    }
  }
}
```
- [cooling] 3324 3m YoY 69.0% vs 2308 32.4%（領先 +37pp）

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
  "as_of": "2026-11-02",
  "per": 40.69,
  "per_pct": 61.1,
  "per_then": 60.15,
  "per_pct_then": 83.0,
  "pbr": 11.06,
  "dividend_yield": 0.86,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **3** 筆；state 已有 outcomes 的 entry：**153/153**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 9 / -5.28 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M2 | 24 / -7.59 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向對 |
| M3 | 27 / -10.89 | 19 / -3.66 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 37 / -6.99 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 49 / -3.85 | 59 / -9.34 | 47 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 29 / -4.05 | 3 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*