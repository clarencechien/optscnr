# 🇹🇼 台股雷達站（tw_scanner + delta_radar）

_README 由 build_readme.py 於 2026-08-03 06:42 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-07-31

## 鋒面：🥶 **CAPITULATION** 　(score -0.14)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`-682,255,821,452`，落在近一年第 **9** 百分位
- 外資大台淨倉 Δ：`-1,498`，落在近一年第 **30** 百分位（水位 -82,515 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+7,387`，落在近一年第 **67** 百分位
- 融資餘額變化：`+13,595,477,000`，落在近一年第 **99** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-08-03 06:42 UTC

## 總判定：🟡 YELLOW

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-06 YoY +55.4%, slope +5.94pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32 |
| M3 thai_shadow | 🟡 YELLOW | DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8% |
| M4 customs_flow | 🟢 GREEN | US 進口 HS850440 (TH+TW) 近3月 $1360.1M, YoY +50.5% |
| M5 narrative_triggers | 🟢 GREEN | capex_cut:5e(6m) / vr300_delay:16e(22m) / debt_financed_capex:13e / lc_psu_competition:0e |
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
    "capex_cut": 5,
    "vr300_delay": 16,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 6,
    "vr300_delay": 22,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 5,
      "mentions": 6,
      "gate": "zscore",
      "z": -0.45,
      "denial": false
    },
    "vr300_delay": {
      "events": 16,
      "mentions": 22,
      "gate": "zscore",
      "z": 0.0,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 13,
      "mentions": 13,
      "gate": "zscore",
      "z": -0.82,
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
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [vr300_delay] Nvidia Says 'Our Roadmap Remains Intact' After Kyber AI Server Delay Report, Jim Cramer Says 'Buy' While - Benzinga
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - Yahoo Finance
- [debt_financed_capex] Will Moody's AI Debt Warning Trigger an AI Bubble Crash? - roddubitsky.substack.com
- [debt_financed_capex] AI data center debt has climbed to the top of Wall Street's credit risk watchlist - Startup Fortune

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
- 本次回填 **11** 筆；state 已有 outcomes 的 entry：**65/65**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# tw_scanner 警報回測 — 警報後遠期報酬 vs 無條件基線

## capitulation — 觸發 14 日 / 8 個事件簇
| 水平 | 事件後中位數 | 事件後均值 | 基線中位數 | 命中率(同號) | n |
|---|---|---|---|---|---|
| 20日 | +5.75% | +6.00% | +2.17% | 67% | 6 |
| 60日 | +9.80% | +12.71% | +5.14% | 83% | 6 |

事件日列表: 2020-03-09, 2020-03-19, 2022-03-08, 2024-04-22, 2024-07-19, 2024-08-05, 2026-07-20, 2026-07-29

> 判讀準則：事件後分佈與基線無法分離 ⇒ 刪除該警報。儀器不留裝飾品。

---

