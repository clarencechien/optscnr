# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-09-12 07:20 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-09-12

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-09-11）：本週無警報、預算未動 → 等（2026-09-18 再看）。
- 鋒面 ☀️ RISK_ON（本週未變）。
- 2308 前提 🟡 YELLOW；🔀 背離：前提健在（YELLOW）、價格 20 日 -14.1% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）
- 2330 前提 🟡 YELLOW；無背離（前提 YELLOW、價格 20 日 +0.6%）；PER 27.9，3 年分位 71 → 72
- 投降窗加碼歷史 8 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +0.71%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-09-11）：本週無警報、預算未動 → 等（2026-09-18 再看）
- 例行（對照）：**2026-10-06** 買 10,000 元（本月已買）
- 投降窗加碼：無
- 鋒面調節（假說）：RISK_ON ×1 = 10,000 元

自 2019-01-02 起 93 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 93 | 32.61 | +0.00% | +230.29% | +30.47% |
| 週檢查・月預算・投降窗即刻投入 | 92 | 32.83 | +0.67% | +228.05% | +30.90% |
| 定期定額＋投降窗加碼 | 101 | 32.84 | +0.71% | +227.93% | +30.62% |
| 定期定額＋鋒面調節 | 93 | 32.79 | +0.55% | +228.49% | +30.41% |
| 對照：一次投入 | 1 | 18.5 | -43.27% | +482.06% | +25.77% |

投降窗加碼 8 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 ☀️ **RISK_ON**（score -0.03，2026-09-11）；本週未變
- 分位數：外資現貨 73.8、大台Δ 35.7、散戶小台 28.2、融資Δ 13.5
- 本週投降警報：無

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-09-10）：🟡 YELLOW
- 🔀 背離：前提健在（YELLOW）、價格 20 日 -14.1% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）
  - 🟡 M1 revenue_acceleration：2026-08 YoY +34.9%, slope -2.90pp/月, 連續減速 2 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32
  - 🟡 M3 thai_shadow：DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8%
  - 🟢 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1399.9M, YoY +30.6%
  - 🟢 M5 narrative_triggers：capex_cut:4e(5m) / vr300_delay:18e(21m) / debt_financed_capex:12e(13m) / lc_psu_competition:0e
  - 🔴 M6 peer_divergence：cooling:3324領先+36pp
  - 🟢 M8 revision_velocity：下修 0/上修 0（樣本不足 <3，暫不評級）
- 回填樣本 78 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-09-12）：🟡 YELLOW
- 無背離（前提 YELLOW、價格 20 日 +0.6%）；PER 27.9，3 年分位 71 → 72
  - 🟢 M1 revenue_acceleration：2026-08 YoY +53.3%, slope +7.74pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9
  - 🟢 M3 adr_premium：ADR 溢價 +13.7%（1 年第 19 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3643.7M, YoY +58.0%
  - 🔴 M5 narrative_triggers：export_controls_tariffs:16e / n2_arizona_ramp:7e(8m) / cowos_capacity:8e / geopolitics:4e / hyperscaler_capex:4e(5m)
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 27.9（3 年第 72 百分位；20 日前第 71）；觀察
- 回填樣本 0 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | -14.52% | +273.60% | +156.90% | +129.11 |
| 2382 | 廣達 | 機櫃 | +1.53% | +177.50% | +137.20% | +37.29 |
| 2383 | 台光電 | CCL | -14.20% | +129.80% | +126.60% | +4.58 |
| 3443 | 創意 | ASIC | +10.77% | +111.00% | +124.40% | +3.65 |
| 3231 | 緯創 | 機櫃 | -5.35% | +166.50% | +93.70% | +56.32 |
| 3324 | 雙鴻 | 散熱 | +33.43% | +67.20% | +82.00% | +2.52 |
| 2345 | 智邦 | 網通 | -19.26% | +59.40% | +64.10% | -0.87 |
| 3017 | 奇鋐 | 散熱 | +2.95% | +54.30% | +59.30% | -5.89 |
| 2330 | 台積電 | 製造 | -0.59% | +53.30% | +55.30% | -7.27 |
| 2317 | 鴻海 | 機櫃 | -5.65% | +52.00% | +52.80% | -0.07 |
| 2308 | 台達電 | 電力 | -15.28% | +34.90% | +46.00% | -10.24 |
| 3037 | 欣興 | 載板 | -5.44% | +56.30% | +45.40% | +9.97 |
| 3711 | 日月光投控 | 封測 | -0.90% | +45.70% | +40.60% | +6.40 |
| 6669 | 緯穎 | 機櫃 | +6.47% | +50.40% | +39.80% | +10.28 |
| 2301 | 光寶科 | 電源 | +2.53% | +25.20% | +33.30% | -5.89 |
| 2454 | 聯發科 | IC設計 | +7.69% | +44.10% | +19.70% | +20.64 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：33 個月，籃子 +194.26% vs 0050 +105.04%，差 +89.22 pp；判準 可讀
月營收加速三分位 vs T+20 超額：累積中（回填 0 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-10-10（28 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-09-11
- ✅ DCA 帳本：最新 2026-09-11
- ✅ delta_radar：最新 2026-09-12
- ✅ tsmc_radar：最新 2026-09-12
- ✅ 賭場 sector：最新 2026-09-12

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-09-12T07:20:42+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-09-11

## 鋒面：☀️ **RISK_ON** 　(score -0.03)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`+62,307,690,123`，落在近一年第 **74** 百分位
- 外資大台淨倉 Δ：`-1,149`，落在近一年第 **36** 百分位（水位 -85,067 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+2,264`，落在近一年第 **28** 百分位
- 融資餘額變化：`-4,026,507,000`，落在近一年第 **13** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-09-12 07:20 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（YELLOW）、價格 20 日 -14.1% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | capex_cut:4e(5m) / vr300_delay:18e(21m) / debt_financed_capex:12e(13m) / lc_psu_competition:0e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 4,
    "vr300_delay": 18,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 5,
    "vr300_delay": 21,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 4,
      "mentions": 5,
      "gate": "zscore",
      "z": 0.84,
      "denial": false
    },
    "vr300_delay": {
      "events": 18,
      "mentions": 21,
      "gate": "zscore",
      "z": 0.46,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 12,
      "mentions": 13,
      "gate": "zscore",
      "z": -0.1,
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
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] Big Tech's AI Spending Spree Turns to Debt as Bond Sales Top 50% of Capex - finance.biggo.com
- [debt_financed_capex] AI Companies' Debt Now Equals 68% of New Long-Term U.S. Treasury Borrowing This Year, JPMorgan Finds - 24/7 Wall St.
- [debt_financed_capex] AI Boom Triggers Tech Debt Binge - StartupHub.ai

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**104/104**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 40 / -8.29 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M2 | 11 / -10.22 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 6 / +0.06 | 1 | 無法判定（狀態翻轉 1 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 26 / -7.34 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 27 / -2.49 | 40 / -9.86 | 32 | 累積中（GREEN n=27 < 30）；方向對 |
| M6 | 0 / — | 16 / -2.97 | 1 | 樣本不足（缺一側 cohort） |
| M8 | 16 / -2.97 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# TSMC Radar (2330.TW) — 2026-09-12 06:30 UTC

## 總判定：🟡 YELLOW

## 前提 vs 價格：無背離（前提 YELLOW、價格 20 日 +0.6%）；PER 27.9，3 年分位 71 → 72

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-08 YoY +53.3%, slope +7.74pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +13.7%（1 年第 19 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3643.7M, YoY +58.0% |
| M5 narrative_triggers | 🔴 RED | export_controls_tariffs:16e / n2_arizona_ramp:7e(8m) / cowos_capacity:8e / geopolitics:4e / hyperscaler_capex:4e(5m) |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 27.9（3 年第 72 百分位；20 日前第 71）；觀察 |

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
  "as_of": "2026-09-11",
  "premium_pct": 13.74,
  "percentile_1y": 18.6,
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

### M5 narrative_triggers — 🔴 RED
```json
{
  "events": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 7,
    "cowos_capacity": 8,
    "geopolitics": 4,
    "hyperscaler_capex": 4
  },
  "mentions": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 8,
    "cowos_capacity": 8,
    "geopolitics": 4,
    "hyperscaler_capex": 5
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 16,
      "mentions": 16,
      "gate": "absolute",
      "z": null,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 7,
      "mentions": 8,
      "gate": "absolute",
      "z": null,
      "denial": false
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "absolute",
      "z": null,
      "denial": true
    },
    "geopolitics": {
      "events": 4,
      "mentions": 4,
      "gate": "absolute",
      "z": null,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 4,
      "mentions": 5,
      "gate": "absolute",
      "z": null,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [export_controls_tariffs] Huawei's chip breakthrough makes the case that US export controls built the rival they were meant to stop - Startup Fort
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Intel and Samsung advance 2nm GAA, but yield gaps leave TSMC as the sole external supplier - digitimes
- [n2_arizona_ramp] Tech News:Samsung 2nm Chip Yield Surpasses 60%, Closing in on TSMC - LinkedIn
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - wccftech.com
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Medium
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
- [geopolitics] Ships Delay Sailing to Taiwan Port to Avoid China Military Drills - Caixin Global
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [hyperscaler_capex] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [hyperscaler_capex] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.

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
  "as_of": "2026-09-11",
  "per": 27.94,
  "per_pct": 71.8,
  "per_then": 27.76,
  "per_pct_then": 70.7,
  "pbr": 9.72,
  "dividend_yield": 0.91,
  "history_years": 3,
  "n": 735
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**2/2**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-09-11

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1869 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-10-06**（本月已買） · 純定期定額 10,000 元
- 投降窗加碼：無（近 5 個交易日無警報）
- 鋒面 RISK_ON → 調節規則本期 ×1 = 10,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-09-11）：本週無警報、預算未動 → 等（2026-09-18 再看）

## 視窗：full（2019-01-02 → 2026-09-11，93 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 93 | 930,000 | 28,521.02 | 32.61 | +0.00% | 3,071,714 | +230.29% | +30.47% |
| 週檢查・月預算・投降窗即刻投入 | 92 | 980,000 | 29,850.02 | 32.83 | +0.67% | 3,214,848 | +228.05% | +30.90% |
| 定期定額＋投降窗加碼 | 101 | 1,010,000 | 30,753.05 | 32.84 | +0.71% | 3,312,103 | +227.93% | +30.62% |
| 定期定額＋鋒面調節 | 93 | 1,015,000 | 30,958.32 | 32.79 | +0.55% | 3,334,211 | +228.49% | +30.41% |
| 對照：一次投入 | 1 | 930,000 | 50,261.25 | 18.50 | -43.27% | 5,413,137 | +482.06% | +25.77% |

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

## 視窗：last_12m（2025-09-11 → 2026-09-11，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,503.48 | 79.81 | +0.00% | 161,925 | +34.94% | +82.86% |
| 週檢查・月預算・投降窗即刻投入 | 12 | 140,000 | 1,814.46 | 77.16 | -3.32% | 195,417 | +39.58% | +87.03% |
| 定期定額＋投降窗加碼 | 14 | 140,000 | 1,707.82 | 81.98 | +2.72% | 183,932 | +31.38% | +83.64% |
| 定期定額＋鋒面調節 | 12 | 140,000 | 1,724.78 | 81.17 | +1.70% | 185,758 | +32.68% | +82.33% |
| 對照：一次投入 | 1 | 120,000 | 1,943.23 | 61.75 | -22.63% | 209,286 | +74.41% | +82.01% |

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

# 🎰 賭場 sector — AI 個股影子追蹤（2026-09-12）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 3650.0 | -13.3% | -14.5% | +273.6% | +156.9% | +129.1 |
| 2382 | 廣達 | 機櫃 | ✓ | 336.5 | +2.8% | +1.5% | +177.5% | +137.2% | +37.3 |
| 2383 | 台光電 | CCL | ✓ | 5365.0 | -13.0% | -14.2% | +129.8% | +126.6% | +4.6 |
| 3443 | 創意 | ASIC |  | 6120.0 | +12.0% | +10.8% | +111.0% | +124.4% | +3.6 |
| 3231 | 緯創 | 機櫃 | ✓ | 185.5 | -4.1% | -5.3% | +166.5% | +93.7% | +56.3 |
| 3324 | 雙鴻 | 散熱 |  | 1360.0 | +34.6% | +33.4% | +67.2% | +82.0% | +2.5 |
| 2345 | 智邦 | 網通 | ✓ | 1885.0 | -18.0% | -19.3% | +59.4% | +64.1% | -0.9 |
| 3017 | 奇鋐 | 散熱 | ✓ | 3370.0 | +4.2% | +3.0% | +54.3% | +59.3% | -5.9 |
| 2330 | 台積電 | 製造 | ✓ | 2410.0 | +0.6% | -0.6% | +53.3% | +55.3% | -7.3 |
| 2317 | 鴻海 | 機櫃 | ✓ | 248.0 | -4.4% | -5.7% | +52.0% | +52.8% | -0.1 |
| 2308 | 台達電 | 電力 | ✓ | 1620.0 | -14.1% | -15.3% | +34.9% | +46.0% | -10.2 |
| 3037 | 欣興 | 載板 | ✓ | 977.0 | -4.2% | -5.4% | +56.3% | +45.4% | +10.0 |
| 3711 | 日月光投控 | 封測 | ✓ | 618.0 | +0.3% | -0.9% | +45.7% | +40.6% | +6.4 |
| 6669 | 緯穎 | 機櫃 | ✓ | 2310.0 | +7.7% | +6.5% | +50.4% | +39.8% | +10.3 |
| 2301 | 光寶科 | 電源 | ✓ | 277.0 | +3.8% | +2.5% | +25.2% | +33.3% | -5.9 |
| 2454 | 聯發科 | IC設計 | ✓ | 4585.0 | +8.9% | +7.7% | +44.1% | +19.7% | +20.6 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 33 個月、投入 165,000 元（16 檔等權）
- 籃子市值 485,528（+194.3%）；0050 市值 338,313（+105.0%）；差 **+89.2 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 累積中（state 16 筆、已回填 T+20 0 筆）

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

