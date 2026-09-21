# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-09-21 18:55 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-09-21

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-09-25）：本月預算已於 2026-09-21 動用（月末例行），本月不再行動。
- 鋒面 ☀️ RISK_ON（本週未變）。
- 2308 前提 🔴 RED；🔀 反向背離：前提轉紅、價格 20 日 +8.1% 未跌 —— 市場不買儀器的帳，或儀器誤判；PER 55.2，3 年分位 79 → 78
- 2330 前提 🟢 GREEN；無背離（前提 GREEN、價格 20 日 +4.4%）；PER 28.8，3 年分位 69 → 78
- 投降窗加碼歷史 8 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +0.71%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-09-25）：本月預算已於 2026-09-21 動用（月末例行），本月不再行動
- 例行（對照）：**2026-10-06** 買 10,000 元（本月已買）
- 投降窗加碼：無
- 鋒面調節（假說）：RISK_ON ×1 = 10,000 元

自 2019-01-02 起 93 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 93 | 32.61 | +0.00% | +241.49% | +31.13% |
| 週檢查・月預算・投降窗即刻投入 | 93 | 33.07 | +1.41% | +236.75% | +31.57% |
| 定期定額＋投降窗加碼 | 101 | 32.84 | +0.71% | +239.04% | +31.29% |
| 定期定額＋鋒面調節 | 93 | 32.79 | +0.55% | +239.63% | +31.07% |
| 對照：一次投入 | 1 | 18.5 | -43.27% | +501.78% | +26.21% |

投降窗加碼 8 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 ☀️ **RISK_ON**（score +0.63，2026-09-21）；本週未變
- 分位數：外資現貨 72.2、大台Δ 81.7、散戶小台 20.6、融資Δ 92.5
- 本週投降警報：無

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-09-21）：🔴 RED
- 🔀 反向背離：前提轉紅、價格 20 日 +8.1% 未跌 —— 市場不買儀器的帳，或儀器誤判；PER 55.2，3 年分位 79 → 78
  - 🟡 M1 revenue_acceleration：2026-08 YoY +34.9%, slope -2.90pp/月, 連續減速 2 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32
  - 🟡 M3 thai_shadow：DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8%
  - 🟢 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1399.9M, YoY +30.6%
  - 🔴 M5 narrative_triggers：capex_cut:5e(6m) / vr300_delay:18e(21m) / debt_financed_capex:15e / lc_psu_competition:0e
  - 🔴 M6 peer_divergence：cooling:3324領先+36pp
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 55.2（3 年第 78 百分位；20 日前第 79）；觀察
- 回填樣本 87 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-09-21）：🟢 GREEN
- 無背離（前提 GREEN、價格 20 日 +4.4%）；PER 28.8，3 年分位 69 → 78
  - 🟢 M1 revenue_acceleration：2026-08 YoY +53.3%, slope +7.74pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9
  - 🟢 M3 adr_premium：ADR 溢價 +11.2%（1 年第 8 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3643.7M, YoY +58.0%
  - 🟡 M5 narrative_triggers：export_controls_tariffs:15e / n2_arizona_ramp:7e(8m) / cowos_capacity:7e / geopolitics:4e / hyperscaler_capex:5e(6m)
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 28.8（3 年第 78 百分位；20 日前第 69）；觀察
- 回填樣本 0 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | -9.14% | +273.60% | +156.90% | +129.11 |
| 2382 | 廣達 | 機櫃 | -1.27% | +177.50% | +137.20% | +37.29 |
| 2383 | 台光電 | CCL | -17.12% | +129.80% | +126.60% | +4.58 |
| 3443 | 創意 | ASIC | +34.67% | +111.00% | +124.40% | +3.65 |
| 3231 | 緯創 | 機櫃 | -1.00% | +166.50% | +93.70% | +56.32 |
| 3324 | 雙鴻 | 散熱 | +42.48% | +67.20% | +82.00% | +2.52 |
| 2345 | 智邦 | 網通 | -18.38% | +59.40% | +64.10% | -0.87 |
| 3017 | 奇鋐 | 散熱 | +12.34% | +54.30% | +59.30% | -5.89 |
| 2330 | 台積電 | 製造 | -2.85% | +53.30% | +55.30% | -7.27 |
| 2317 | 鴻海 | 機櫃 | -4.60% | +52.00% | +52.80% | -0.07 |
| 2308 | 台達電 | 電力 | +0.80% | +34.90% | +46.00% | -10.24 |
| 3037 | 欣興 | 載板 | -12.39% | +56.30% | +45.40% | +9.97 |
| 3711 | 日月光投控 | 封測 | +4.72% | +45.70% | +40.60% | +6.40 |
| 6669 | 緯穎 | 機櫃 | -4.89% | +50.40% | +39.80% | +10.28 |
| 2301 | 光寶科 | 電源 | -6.75% | +25.20% | +33.30% | -5.89 |
| 2454 | 聯發科 | IC設計 | +25.80% | +44.10% | +19.70% | +20.64 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：33 個月，籃子 +205.86% vs 0050 +111.99%，差 +93.87 pp；判準 可讀
月營收加速三分位 vs T+20 超額：累積中（回填 0 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-10-10（19 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-09-21
- ✅ DCA 帳本：最新 2026-09-21
- ✅ delta_radar：最新 2026-09-21
- ✅ tsmc_radar：最新 2026-09-21
- ✅ 賭場 sector：最新 2026-09-21

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-09-21T18:55:41+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-09-21

## 鋒面：☀️ **RISK_ON** 　(score +0.63)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`+52,614,087,670`，落在近一年第 **72** 百分位
- 外資大台淨倉 Δ：`+2,029`，落在近一年第 **82** 百分位（水位 -74,081 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+969`，落在近一年第 **21** 百分位
- 融資餘額變化：`+8,998,298,000`，落在近一年第 **92** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

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

---

# TSMC Radar (2330.TW) — 2026-09-21 10:01 UTC

## 總判定：🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +4.4%）；PER 28.8，3 年分位 69 → 78

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-08 YoY +53.3%, slope +7.74pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +11.2%（1 年第 8 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3643.7M, YoY +58.0% |
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:15e / n2_arizona_ramp:7e(8m) / cowos_capacity:7e / geopolitics:4e / hyperscaler_capex:5e(6m) |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 28.8（3 年第 78 百分位；20 日前第 69）；觀察 |

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
  "as_of": "2026-09-21",
  "premium_pct": 11.17,
  "percentile_1y": 7.5,
  "n": 372
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

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 7,
    "cowos_capacity": 7,
    "geopolitics": 4,
    "hyperscaler_capex": 5
  },
  "mentions": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 8,
    "cowos_capacity": 7,
    "geopolitics": 4,
    "hyperscaler_capex": 6
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 15,
      "mentions": 15,
      "gate": "zscore",
      "z": -0.45,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 7,
      "mentions": 8,
      "gate": "zscore",
      "z": -0.93,
      "denial": false
    },
    "cowos_capacity": {
      "events": 7,
      "mentions": 7,
      "gate": "zscore",
      "z": -0.12,
      "denial": false
    },
    "geopolitics": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": 0.0,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 5,
      "mentions": 6,
      "gate": "absolute",
      "z": null,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [n2_arizona_ramp] Samsung and Qualcomm reopen 2nm talks as yield gap with TSMC narrows - CHOSUNBIZ - Chosunbiz
- [n2_arizona_ramp] Samsung's 2nm Yield Tops 50%, Restarts Qualcomm Talks; Snapdragon Summit May Decide Foundry Assignment - finance.biggo.c
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - finance.biggo.com
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Beth Kindig – Medium
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 247wallst.com
- [hyperscaler_capex] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha

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
      "best_peer_3m_yoy": 126.6,
      "peer_lead_pp": 71.4,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3711": 40.6,
        "3037": 45.4,
        "2383": 126.6
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
        "3443": 124.4
      }
    }
  }
}
```

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
  "as_of": "2026-09-21",
  "per": 28.75,
  "per_pct": 78.2,
  "per_then": 27.53,
  "per_pct_then": 68.8,
  "pbr": 10.0,
  "dividend_yield": 0.89,
  "history_years": 3,
  "n": 735
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **5** 筆；state 已有 outcomes 的 entry：**8/8**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-09-21

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1875 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-10-06**（本月已買） · 純定期定額 10,000 元
- 投降窗加碼：無（近 5 個交易日無警報）
- 鋒面 RISK_ON → 調節規則本期 ×1 = 10,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-09-25）：本月預算已於 2026-09-21 動用（月末例行），本月不再行動

## 視窗：full（2019-01-02 → 2026-09-21，93 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 93 | 930,000 | 28,521.02 | 32.61 | +0.00% | 3,175,815 | +241.49% | +31.13% |
| 週檢查・月預算・投降窗即刻投入 | 93 | 990,000 | 29,939.75 | 33.07 | +1.41% | 3,333,792 | +236.75% | +31.57% |
| 定期定額＋投降窗加碼 | 101 | 1,010,000 | 30,753.05 | 32.84 | +0.71% | 3,424,352 | +239.04% | +31.29% |
| 定期定額＋鋒面調節 | 93 | 1,015,000 | 30,958.32 | 32.79 | +0.55% | 3,447,209 | +239.63% | +31.07% |
| 對照：一次投入 | 1 | 930,000 | 50,261.25 | 18.50 | -43.27% | 5,596,590 | +501.78% | +26.21% |

加碼逐筆（跟「同一筆錢等到下一個例行買日」比；T+60 交易日）：

| 警報日 | 執行日 | 執行價 | 下一例行買日 | 例行價 | edge | T+60 |
|---|---|---|---|---|---|---|
| 2020-03-09 | 2020-03-10 | 21.575 | 2020-04-06 | 19.26 | -10.72% | +2.38% |
| 2020-03-19 | 2020-03-20 | 18.5 | 2020-04-06 | 19.26 | +4.12% | +20.27% |
| 2022-03-08 | 2022-03-09 | 33.125 | 2022-04-06 | 34.06 | +2.83% | -3.85% |
| 2024-04-22 | 2024-04-23 | 37.975 | 2024-05-06 | 39.80 | +4.81% | +25.48% |
| 2024-07-19 | 2024-07-22 | 45.175 | 2024-08-06 | 41.88 | -7.30% | +9.19% |
| 2024-08-05 | 2024-08-06 | 41.875 | 2024-09-06 | 43.69 | +4.33% | +15.61% |
| 2026-07-20 | 2026-07-21 | 102.5 | 2026-08-06 | 103.30 | +0.78% | — |
| 2026-07-29 | 2026-07-30 | 93.5 | 2026-08-06 | 103.30 | +10.48% | — |

加碼 edge 平均 +1.17%、勝率 75%（n=8）。正 = 警報日買比等到例行日買便宜。

## 視窗：last_12m（2025-09-22 → 2026-09-21，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,503.48 | 79.81 | +0.00% | 167,412 | +39.51% | +88.54% |
| 週檢查・月預算・投降窗即刻投入 | 13 | 150,000 | 1,893.08 | 79.24 | -0.71% | 210,794 | +40.53% | +91.85% |
| 定期定額＋投降窗加碼 | 14 | 140,000 | 1,707.82 | 81.98 | +2.72% | 190,165 | +35.83% | +89.82% |
| 定期定額＋鋒面調節 | 12 | 140,000 | 1,724.78 | 81.17 | +1.70% | 192,054 | +37.18% | +88.28% |
| 對照：一次投入 | 1 | 120,000 | 1,943.23 | 61.75 | -22.63% | 216,379 | +80.32% | +85.26% |

加碼逐筆（跟「同一筆錢等到下一個例行買日」比；T+60 交易日）：

| 警報日 | 執行日 | 執行價 | 下一例行買日 | 例行價 | edge | T+60 |
|---|---|---|---|---|---|---|
| 2026-07-20 | 2026-07-21 | 102.5 | 2026-08-06 | 103.30 | +0.78% | — |
| 2026-07-29 | 2026-07-30 | 93.5 | 2026-08-06 | 103.30 | +10.48% | — |

加碼 edge 平均 +5.63%、勝率 100%（n=2）。正 = 警報日買比等到例行日買便宜。

分割還原：2025-06-18 ×4（override）。

---
*dca_ledger — 規則影子帳本，等額假設。lump_sum 是對照不是策略（沒人一開始就有全部的錢）；regime_scaled 是待資料處決的假說。非投資建議。*

---

# 🎰 賭場 sector — AI 個股影子追蹤（2026-09-21）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 3665.0 | -1.9% | -9.1% | +273.6% | +156.9% | +129.1 |
| 2382 | 廣達 | 機櫃 | ✓ | 344.5 | +6.0% | -1.3% | +177.5% | +137.2% | +37.3 |
| 2383 | 台光電 | CCL | ✓ | 4895.0 | -9.8% | -17.1% | +129.8% | +126.6% | +4.6 |
| 3443 | 創意 | ASIC |  | 7615.0 | +41.9% | +34.7% | +111.0% | +124.4% | +3.6 |
| 3231 | 緯創 | 機櫃 | ✓ | 186.5 | +6.3% | -1.0% | +166.5% | +93.7% | +56.3 |
| 3324 | 雙鴻 | 散熱 |  | 1520.0 | +49.8% | +42.5% | +67.2% | +82.0% | +2.5 |
| 2345 | 智邦 | 網通 | ✓ | 1840.0 | -11.1% | -18.4% | +59.4% | +64.1% | -0.9 |
| 3017 | 奇鋐 | 散熱 | ✓ | 3415.0 | +19.6% | +12.3% | +54.3% | +59.3% | -5.9 |
| 2330 | 台積電 | 製造 | ✓ | 2480.0 | +4.4% | -2.9% | +53.3% | +55.3% | -7.3 |
| 2317 | 鴻海 | 機櫃 | ✓ | 250.0 | +2.7% | -4.6% | +52.0% | +52.8% | -0.1 |
| 2308 | 台達電 | 電力 | ✓ | 1875.0 | +8.1% | +0.8% | +34.9% | +46.0% | -10.2 |
| 3037 | 欣興 | 載板 | ✓ | 1020.0 | -5.1% | -12.4% | +56.3% | +45.4% | +10.0 |
| 3711 | 日月光投控 | 封測 | ✓ | 663.0 | +12.0% | +4.7% | +45.7% | +40.6% | +6.4 |
| 6669 | 緯穎 | 機櫃 | ✓ | 2150.0 | +2.4% | -4.9% | +50.4% | +39.8% | +10.3 |
| 2301 | 光寶科 | 電源 | ✓ | 288.5 | +0.5% | -6.8% | +25.2% | +33.3% | -5.9 |
| 2454 | 聯發科 | IC設計 | ✓ | 5010.0 | +33.1% | +25.8% | +44.1% | +19.7% | +20.6 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 33 個月、投入 165,000 元（16 檔等權）
- 籃子市值 504,667（+205.9%）；0050 市值 349,778（+112.0%）；差 **+93.9 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 累積中（state 112 筆、已回填 T+20 0 筆）

分割還原：0050 2025-06-18 ×4（override）、6669 2026-09-02 ×3（override）

---
*casino_tracker — 只收資料。名單不是訊號、籃子不是建議；期望值未證明前，這筆錢是娛樂預算。*

---

# tw_scanner 警報回測 — 警報後遠期報酬 vs 無條件基線

## capitulation — 觸發 14 日 / 8 個事件簇
| 水平 | 事件後中位數 | 事件後均值 | 基線中位數 | 命中率(同號) | n |
|---|---|---|---|---|---|
| 20日 | +8.72% | +7.31% | +2.17% | 75% | 8 |
| 60日 | +9.80% | +12.71% | +5.14% | 83% | 6 |

事件日列表: 2020-03-09, 2020-03-19, 2022-03-08, 2024-04-22, 2024-07-19, 2024-08-05, 2026-07-20, 2026-07-29

> 判讀準則：事件後分佈與基線無法分離 ⇒ 刪除該警報。儀器不留裝飾品。

---

