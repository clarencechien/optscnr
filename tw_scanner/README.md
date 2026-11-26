# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-11-26 13:59 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-11-26

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-11-27）：本月預算已於 2026-11-09 動用（投降窗 ×2.0），本月不再行動。
- 鋒面 🌧️ DE_RISK（本週未變）。
- 2308 前提 🟡 YELLOW；🔀 背離：前提健在（YELLOW）、價格 20 日 -24.3% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 33.6，3 年分位 62 → 56
- 2330 前提 🟢 GREEN；🔀 背離：前提健在（GREEN）、價格 20 日 -11.2% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 21.8，3 年分位 69 → 24
- 投降窗加碼歷史 10 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +1.87%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-11-27）：本月預算已於 2026-11-09 動用（投降窗 ×2.0），本月不再行動
- 例行（對照）：**2026-12-06** 買 10,000 元（本月已買）
- 投降窗加碼：無
- 鋒面調節（假說）：DE_RISK ×1.5 = 15,000 元

自 2019-01-02 起 95 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 95 | 33.08 | +0.00% | +172.94% | +24.78% |
| 週檢查・月預算・投降窗即刻投入 | 95 | 33.73 | +1.96% | +167.72% | +25.07% |
| 定期定額＋投降窗加碼 | 105 | 33.7 | +1.87% | +167.94% | +24.88% |
| 定期定額＋鋒面調節 | 95 | 33.43 | +1.06% | +170.12% | +24.71% |
| 對照：一次投入 | 1 | 18.5 | -44.07% | +388.02% | +22.26% |

投降窗加碼 10 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 🌧️ **DE_RISK**（score -0.42，2026-11-25）；本週未變
- 分位數：外資現貨 3.6、大台Δ 19.0、散戶小台 10.3、融資Δ 4.4
- 本週投降警報：無
- 警報戰績（月更回測）：8 簇，20 日中位 +8.72% vs 基線 +2.20%、命中 75%

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-11-26）：🟡 YELLOW
- 🔀 背離：前提健在（YELLOW）、價格 20 日 -24.3% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 33.6，3 年分位 62 → 56
  - 🟢 M1 revenue_acceleration：2026-10 YoY +30.1%, slope -5.88pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74
  - 🟢 M3 thai_shadow：DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3%
  - 🟡 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1376.6M, YoY +19.9%
  - 🟢 M5 narrative_triggers：capex_cut:3e / vr300_delay:10e / debt_financed_capex:9e(10m) / lc_psu_competition:0e
  - 🟡 M6 peer_divergence：cooling:3324領先+18pp
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 33.6（3 年第 56 百分位；20 日前第 62）；觀察
- 回填樣本 151 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-11-26）：🟢 GREEN
- 🔀 背離：前提健在（GREEN）、價格 20 日 -11.2% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 21.8，3 年分位 69 → 24
  - 🟢 M1 revenue_acceleration：2026-10 YoY +59.7%, slope +5.01pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +11.0% / FCF/淨利 1.46
  - 🟢 M3 adr_premium：ADR 溢價 +5.2%（1 年第 1 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3666.0M, YoY +65.1%
  - 🟢 M5 narrative_triggers：export_controls_tariffs:10e(15m) / n2_arizona_ramp:22e(27m) / cowos_capacity:2e / geopolitics:2e / hyperscaler_capex:3e
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 21.8（3 年第 24 百分位；20 日前第 69）；觀察
- 回填樣本 50 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | +11.76% | +515.80% | +428.50% | +121.10 |
| 2383 | 台光電 | CCL | -16.34% | +203.10% | +167.30% | +36.61 |
| 3231 | 緯創 | 機櫃 | -4.96% | +117.60% | +123.70% | -24.46 |
| 2382 | 廣達 | 機櫃 | -4.02% | +104.00% | +119.40% | -36.75 |
| 3443 | 創意 | ASIC | -21.05% | +127.00% | +111.90% | +7.97 |
| 6669 | 緯穎 | 機櫃 | -9.78% | +80.90% | +77.10% | +15.29 |
| 2345 | 智邦 | 網通 | -1.84% | +91.20% | +72.20% | +15.87 |
| 3037 | 欣興 | 載板 | -29.93% | +67.60% | +62.80% | +5.68 |
| 2330 | 台積電 | 製造 | +5.55% | +59.70% | +55.90% | +3.19 |
| 3711 | 日月光投控 | 封測 | -12.89% | +47.10% | +46.10% | +0.73 |
| 2317 | 鴻海 | 機櫃 | -1.00% | +45.70% | +45.40% | -3.12 |
| 3324 | 雙鴻 | 散熱 | -27.50% | +44.70% | +45.10% | -11.21 |
| 3017 | 奇鋐 | 散熱 | -3.95% | +34.40% | +44.50% | -9.99 |
| 2308 | 台達電 | 電力 | -15.05% | +30.10% | +26.60% | -2.42 |
| 2301 | 光寶科 | 電源 | -10.83% | +32.00% | +26.50% | +3.40 |
| 2454 | 聯發科 | IC設計 | +2.96% | +5.80% | +17.30% | -19.16 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：35 個月，籃子 +105.07% vs 0050 +67.09%，差 +37.98 pp；判準 可讀
月營收加速三分位 vs T+20 超額：可讀（n 達門檻）（回填 464 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-12-10（14 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-11-25
- ✅ DCA 帳本：最新 2026-11-25
- ✅ delta_radar：最新 2026-11-26
- ✅ tsmc_radar：最新 2026-11-26
- ✅ 賭場 sector：最新 2026-11-25

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-11-26T13:59:27+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-11-25

## 鋒面：🌧️ **DE_RISK** 　(score -0.42)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`-1,224,107,948,543`，落在近一年第 **4** 百分位
- 外資大台淨倉 Δ：`-2,527`，落在近一年第 **19** 百分位（水位 -105,709 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+332`，落在近一年第 **10** 百分位
- 融資餘額變化：`-19,367,186,000`，落在近一年第 **4** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-11-26 13:08 UTC

## 總判定：🟡 YELLOW

## 🔀 前提 vs 價格：🔀 背離：前提健在（YELLOW）、價格 20 日 -24.3% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 33.6，3 年分位 62 → 56

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-10 YoY +30.1%, slope -5.88pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74 |
| M3 thai_shadow | 🟢 GREEN | DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3% |
| M4 customs_flow | 🟡 YELLOW | US 進口 HS850440 (TH+TW) 近3月 $1376.6M, YoY +19.9% |
| M5 narrative_triggers | 🟢 GREEN | capex_cut:3e / vr300_delay:10e / debt_financed_capex:9e(10m) / lc_psu_competition:0e |
| M6 peer_divergence | 🟡 YELLOW | cooling:3324領先+18pp |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 33.6（3 年第 56 百分位；20 日前第 62）；觀察 |

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
    "capex_cut": 3,
    "vr300_delay": 10,
    "debt_financed_capex": 9,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 3,
    "vr300_delay": 10,
    "debt_financed_capex": 10,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -0.69,
      "denial": false
    },
    "vr300_delay": {
      "events": 10,
      "mentions": 10,
      "gate": "zscore",
      "z": 1.01,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 9,
      "mentions": 10,
      "gate": "zscore",
      "z": -0.8,
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
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - Yahoo Finance
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
  "as_of": "2026-11-26",
  "per": 33.63,
  "per_pct": 56.0,
  "per_then": 44.44,
  "per_pct_then": 61.7,
  "pbr": 9.14,
  "dividend_yield": 1.04,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**175/175**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 21 / -14.06 | 3 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M2 | 33 / -11.05 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 28 / -10.89 | 27 / -8.93 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 46 / -9.59 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M5 | 65 / -8.10 | 65 / -10.55 | 53 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 38 / -7.89 | 5 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# TSMC Radar (2330.TW) — 2026-11-26 13:59 UTC

## 總判定：🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（GREEN）、價格 20 日 -11.2% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 21.8，3 年分位 69 → 24

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-10 YoY +59.7%, slope +5.01pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +11.0% / FCF/淨利 1.46 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +5.2%（1 年第 1 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3666.0M, YoY +65.1% |
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:10e(15m) / n2_arizona_ramp:22e(27m) / cowos_capacity:2e / geopolitics:2e / hyperscaler_capex:3e |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 21.8（3 年第 24 百分位；20 日前第 69）；觀察 |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-10",
  "latest_yoy_pct": 59.7,
  "yoy_slope_pp_per_month": 5.01,
  "consecutive_decel_months": 0
}
```

### M2 bullwhip_health — 🟢 GREEN
```json
{
  "as_of": null,
  "contract_liab_qoq_pct": null,
  "inventory_qoq_pct": 11.0,
  "fcf_to_net_income": 1.46,
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
  "as_of": "2026-11-26",
  "premium_pct": 5.18,
  "percentile_1y": 0.8,
  "n": 370
}
```

### M4 customs_flow — 🟢 GREEN
```json
{
  "window": "2026-07..2026-09",
  "rolling_value_usd_m": 3666.0,
  "rolling_yoy_pct": 65.1,
  "by_country": {
    "TAIWAN": {
      "rolling_value_usd_m": 3666.0,
      "rolling_yoy_pct": 65.1
    }
  }
}
```

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "export_controls_tariffs": 10,
    "n2_arizona_ramp": 22,
    "cowos_capacity": 2,
    "geopolitics": 2,
    "hyperscaler_capex": 3
  },
  "mentions": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 27,
    "cowos_capacity": 2,
    "geopolitics": 2,
    "hyperscaler_capex": 3
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 10,
      "mentions": 15,
      "gate": "zscore",
      "z": -2.24,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 22,
      "mentions": 27,
      "gate": "zscore",
      "z": 0.64,
      "denial": true
    },
    "cowos_capacity": {
      "events": 2,
      "mentions": 2,
      "gate": "zscore",
      "z": -2.49,
      "denial": false
    },
    "geopolitics": {
      "events": 2,
      "mentions": 2,
      "gate": "zscore",
      "z": -0.39,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -0.58,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] Apple supplier TSMC cuts off China chip orders amid tighter export controls - AppleInsider
- [export_controls_tariffs] TSMC and Samsung pause some chip shipments to China due to tighter US export controls - Digital Watch Observatory
- [export_controls_tariffs] PRE-MARKET TAIWAN AND SINGAPORE STOCKS NEWS: TSMC (2330 TT) tightening restrictions on Chinese chip designers - Newsquaw
- [n2_arizona_ramp] AMD Zen 6 Olympic Ridge Desktop CPUs Reportedly Slip Past Computex 2027 After A Switch To TSMC’s Performance-Focused N2X
- [n2_arizona_ramp] Samsung and Qualcomm reopen 2nm talks as yield gap with TSMC narrows - Chosunbiz
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [geopolitics] China stages record drills designed to encircle Taiwan - Reuters
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - The Motley Fool
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Will the next recession be caused by an AI capex cut-off? - InvestorDaily

### M6 peer_divergence — 🟢 GREEN
```json
{
  "groups": {
    "foundry_contrast": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 55.9,
      "best_peer": "2303",
      "best_peer_3m_yoy": 25.4,
      "peer_lead_pp": -30.5,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2303": 25.4
      }
    },
    "backend": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 55.9,
      "best_peer": "2383",
      "best_peer_3m_yoy": 167.3,
      "peer_lead_pp": 111.4,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3711": 46.1,
        "3037": 62.8,
        "2383": 167.3
      }
    },
    "asic_lead": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 55.9,
      "best_peer": "3661",
      "best_peer_3m_yoy": 428.5,
      "peer_lead_pp": 372.6,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3661": 428.5,
        "3443": 111.9
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
  "as_of": "2026-11-26",
  "per": 21.83,
  "per_pct": 23.6,
  "per_then": 27.99,
  "per_pct_then": 68.7,
  "pbr": 7.95,
  "dividend_yield": 1.03,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**79/79**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 19 / +2.41 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 16 / +2.04 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 15 / +2.14 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 17 / +2.87 | 29 / +1.95 | 43 | 累積中（GREEN n=17 < 30）；方向對 |
| M6 | 16 / +2.04 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-11-25

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1917 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-12-06**（本月已買） · 純定期定額 10,000 元
- 投降窗加碼：無（近 5 個交易日無警報）
- 鋒面 DE_RISK → 調節規則本期 ×1.5 = 15,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-11-27）：本月預算已於 2026-11-09 動用（投降窗 ×2.0），本月不再行動

## 視窗：full（2019-01-02 → 2026-11-25，95 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 95 | 950,000 | 28,714.80 | 33.08 | +0.00% | 2,592,946 | +172.94% | +24.78% |
| 週檢查・月預算・投降窗即刻投入 | 95 | 1,020,000 | 30,240.83 | 33.73 | +1.96% | 2,730,747 | +167.72% | +25.07% |
| 定期定額＋投降窗加碼 | 105 | 1,050,000 | 31,155.53 | 33.70 | +1.87% | 2,813,345 | +167.94% | +24.88% |
| 定期定額＋鋒面調節 | 95 | 1,045,000 | 31,260.12 | 33.43 | +1.06% | 2,822,788 | +170.12% | +24.71% |
| 對照：一次投入 | 1 | 950,000 | 51,342.14 | 18.50 | -44.07% | 4,636,195 | +388.02% | +22.26% |

加碼逐筆（跟「同一筆錢等到下一個例行買日」比；T+60 交易日）：

| 警報日 | 執行日 | 執行價 | 下一例行買日 | 例行價 | edge | T+60 |
|---|---|---|---|---|---|---|
| 2020-03-09 | 2020-03-10 | 21.575 | 2020-04-06 | 19.26 | -10.72% | +2.38% |
| 2020-03-19 | 2020-03-20 | 18.5 | 2020-04-06 | 19.26 | +4.12% | +20.27% |
| 2022-03-08 | 2022-03-09 | 33.125 | 2022-04-06 | 34.06 | +2.83% | -3.85% |
| 2024-04-22 | 2024-04-23 | 37.975 | 2024-05-06 | 39.80 | +4.81% | +25.48% |
| 2024-07-19 | 2024-07-22 | 45.175 | 2024-08-06 | 41.88 | -7.30% | +9.19% |
| 2024-08-05 | 2024-08-06 | 41.875 | 2024-09-06 | 43.69 | +4.33% | +15.61% |
| 2026-07-20 | 2026-07-21 | 102.5 | 2026-08-06 | 103.30 | +0.78% | +6.34% |
| 2026-07-29 | 2026-07-30 | 93.5 | 2026-08-06 | 103.30 | +10.48% | +14.71% |
| 2026-11-06 | 2026-11-09 | 97.45 | — | — | — | — |
| 2026-11-17 | 2026-11-18 | 94.1 | — | — | — | — |

加碼 edge 平均 +1.17%、勝率 75%（n=8）。正 = 警報日買比等到例行日買便宜。

## 視窗：last_12m（2025-11-25 → 2026-11-25，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,377.48 | 87.12 | +0.00% | 124,386 | +3.66% | +7.24% |
| 週檢查・月預算・投降窗即刻投入 | 13 | 160,000 | 1,855.14 | 86.25 | -1.00% | 167,519 | +4.70% | +9.86% |
| 定期定額＋投降窗加碼 | 16 | 160,000 | 1,790.53 | 89.36 | +2.57% | 161,684 | +1.05% | +2.47% |
| 定期定額＋鋒面調節 | 12 | 150,000 | 1,706.79 | 87.88 | +0.87% | 154,123 | +2.75% | +5.81% |
| 對照：一次投入 | 1 | 120,000 | 1,882.22 | 63.75 | -26.83% | 169,964 | +41.64% | +43.47% |

加碼逐筆（跟「同一筆錢等到下一個例行買日」比；T+60 交易日）：

| 警報日 | 執行日 | 執行價 | 下一例行買日 | 例行價 | edge | T+60 |
|---|---|---|---|---|---|---|
| 2026-07-20 | 2026-07-21 | 102.5 | 2026-08-06 | 103.30 | +0.78% | +6.34% |
| 2026-07-29 | 2026-07-30 | 93.5 | 2026-08-06 | 103.30 | +10.48% | +14.71% |
| 2026-11-06 | 2026-11-09 | 97.45 | — | — | — | — |
| 2026-11-17 | 2026-11-18 | 94.1 | — | — | — | — |

加碼 edge 平均 +5.63%、勝率 100%（n=2）。正 = 警報日買比等到例行日買便宜。

分割還原：2025-06-18 ×4（override）。

---
*dca_ledger — 規則影子帳本，等額假設。lump_sum 是對照不是策略（沒人一開始就有全部的錢）；regime_scaled 是待資料處決的假說。非投資建議。*

---

# 🎰 賭場 sector — AI 個股影子追蹤（2026-11-25）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 3605.0 | -5.1% | +11.8% | +515.8% | +428.5% | +121.1 |
| 2383 | 台光電 | CCL | ✓ | 3355.0 | -33.2% | -16.3% | +203.1% | +167.3% | +36.6 |
| 3231 | 緯創 | 機櫃 | ✓ | 152.0 | -21.9% | -5.0% | +117.6% | +123.7% | -24.5 |
| 2382 | 廣達 | 機櫃 | ✓ | 261.0 | -20.9% | -4.0% | +104.0% | +119.4% | -36.8 |
| 3443 | 創意 | ASIC |  | 5070.0 | -37.9% | -21.1% | +127.0% | +111.9% | +8.0 |
| 6669 | 緯穎 | 機櫃 | ✓ | 1430.0 | -26.7% | -9.8% | +80.9% | +77.1% | +15.3 |
| 2345 | 智邦 | 網通 | ✓ | 1475.0 | -18.7% | -1.8% | +91.2% | +72.2% | +15.9 |
| 3037 | 欣興 | 載板 | ✓ | 585.0 | -46.8% | -29.9% | +67.6% | +62.8% | +5.7 |
| 2330 | 台積電 | 製造 | ✓ | 2150.0 | -11.3% | +5.5% | +59.7% | +55.9% | +3.2 |
| 3711 | 日月光投控 | 封測 | ✓ | 488.0 | -29.8% | -12.9% | +47.1% | +46.1% | +0.7 |
| 2317 | 鴻海 | 機櫃 | ✓ | 206.5 | -17.9% | -1.0% | +45.7% | +45.4% | -3.1 |
| 3324 | 雙鴻 | 散熱 |  | 798.0 | -44.4% | -27.5% | +44.7% | +45.1% | -11.2 |
| 3017 | 奇鋐 | 散熱 | ✓ | 2545.0 | -20.8% | -4.0% | +34.4% | +44.5% | -10.0 |
| 2308 | 台達電 | 電力 | ✓ | 1055.0 | -31.9% | -15.1% | +30.1% | +26.6% | -2.4 |
| 2301 | 光寶科 | 電源 | ✓ | 189.0 | -27.7% | -10.8% | +32.0% | +26.5% | +3.4 |
| 2454 | 聯發科 | IC設計 | ✓ | 3645.0 | -13.9% | +3.0% | +5.8% | +17.3% | -19.2 |

## 借券（只收資料，不是訊號）

> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。

| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |
|---|---|---|---|---|---|---|
| 3661 | 1,303 | +288.3% | 28 | 0.4 | 1.00%（112 筆） | 39 |
| 2383 | 852 | +37.6% | 49 | 0.2 | 0.25%（91 筆） | 20 |
| 3231 | 32,141 | +11.0% | 8 | 1.1 | 0.70%（89 筆） | 114 |
| 2382 | 74,175 | +12.2% | 20 | 4.1 | 0.75%（145 筆） | 64 |
| 3443 | 1,896 | +83.8% | 98 | 0.6 | 0.75%（106 筆） | 46 |
| 6669 | 3,429 | -24.9% | 3 | 0.8 | 2.50%（167 筆） | 229 |
| 2345 | 833 | +32.3% | 15 | 0.2 | 0.25%（86 筆） | 7 |
| 3037 | 5,721 | +97.2% | 37 | 0.2 | 0.25%（78 筆） | 69 |
| 2330 | 17,286 | +11.3% | 94 | 0.3 | 0.18%（312 筆） | 46 |
| 3711 | 27,119 | +163.3% | 54 | 1.0 | 0.25%（138 筆） | 208 |
| 2317 | 105,924 | +36.1% | 87 | 2.0 | 0.25%（168 筆） | 556 |
| 3324 | 3,300 | -24.8% | 44 | 0.7 | 4.77%（63 筆） | 20 |
| 3017 | 3,356 | +40.3% | 73 | 0.9 | 0.50%（98 筆） | 17 |
| 2308 | 11,485 | -17.6% | 90 | 0.5 | 0.35%（141 筆） | 66 |
| 2301 | 6,144 | +167.4% | 26 | 0.3 | 0.35%（125 筆） | 21 |
| 2454 | 7,840 | +30.9% | 98 | 0.5 | 0.25%（181 筆） | 31 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 35 個月、投入 175,000 元（16 檔等權）
- 籃子市值 358,864（+105.1%）；0050 市值 292,404（+67.1%）；差 **+38.0 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 前三分之一 n=154 超額 -0.6%；後三分之一 n=154 超額 -7.3%；全部 -4.5%
- 狀態：可讀（n 達門檻）（state 768 筆、已回填 T+20 464 筆）

分割還原：0050 2025-06-18 ×4（override）、6669 2026-09-02 ×3（override）

---
*casino_tracker — 只收資料。名單不是訊號、籃子不是建議；期望值未證明前，這筆錢是娛樂預算。*

---

# tw_scanner 警報回測 — 警報後遠期報酬 vs 無條件基線

## capitulation — 觸發 14 日 / 8 個事件簇
| 水平 | 事件後中位數 | 事件後均值 | 基線中位數 | 命中率(同號) | n |
|---|---|---|---|---|---|
| 20日 | +8.72% | +7.31% | +2.20% | 75% | 8 |
| 60日 | +13.23% | +13.05% | +5.15% | 88% | 8 |

事件日列表: 2020-03-09, 2020-03-19, 2022-03-08, 2024-04-22, 2024-07-19, 2024-08-05, 2026-07-20, 2026-07-29

> 判讀準則：事件後分佈與基線無法分離 ⇒ 刪除該警報。儀器不留裝飾品。

---

