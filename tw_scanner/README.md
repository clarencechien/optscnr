# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-11-09 12:07 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-11-09

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-11-06）：本週有投降警報（2026-11-06）→ 下一交易日投入 20,000 元，當月不再行動。
- 鋒面 🥶 CAPITULATION（本週由 DE_RISK 轉入）。
- 2308 前提 🟡 YELLOW；🔀 背離：前提健在（YELLOW）、價格 20 日 -41.7% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 34.8，3 年分位 86 → 58
- 2330 前提 🟢 GREEN；🔀 背離：前提健在（GREEN）、價格 20 日 -17.4% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 26.0，3 年分位 85 → 49
- 投降窗加碼歷史 8 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +0.60%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-11-06）：本週有投降警報（2026-11-06）→ 下一交易日投入 20,000 元，當月不再行動
- 例行（對照）：**2026-11-06** 買 10,000 元
- 投降窗加碼：**待執行** 10,000 元
- 鋒面調節（假說）：CAPITULATION ×2 = 20,000 元

自 2019-01-02 起 95 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 95 | 33.08 | +0.00% | +179.59% | +25.67% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 33.29 | +0.63% | +177.83% | +25.99% |
| 定期定額＋投降窗加碼 | 103 | 33.28 | +0.60% | +177.92% | +25.78% |
| 定期定額＋鋒面調節 | 95 | 33.43 | +1.06% | +176.70% | +25.60% |
| 對照：一次投入 | 1 | 18.5 | -44.07% | +399.91% | +22.80% |

投降窗加碼 8 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 🥶 **CAPITULATION**（score -0.68，2026-11-06）；本週轉移：2026-11-04 DE_RISK→CAPITULATION
- 分位數：外資現貨 0.4、大台Δ 7.9、散戶小台 45.2、融資Δ 0.4
- 本週投降警報：2026-11-06
- 警報戰績（月更回測）：8 簇，20 日中位 +8.72% vs 基線 +2.20%、命中 75%

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-11-09）：🟡 YELLOW
- 🔀 背離：前提健在（YELLOW）、價格 20 日 -41.7% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 34.8，3 年分位 86 → 58
  - 🔴 M1 revenue_acceleration：2026-09 YoY +14.6%, slope -13.60pp/月, 連續減速 3 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74
  - 🟢 M3 thai_shadow：DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3%
  - 🟡 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1376.6M, YoY +19.9%
  - 🟢 M5 narrative_triggers：capex_cut:4e / vr300_delay:8e / debt_financed_capex:13e / lc_psu_competition:0e
  - 🟢 M6 peer_divergence：cohort 內 2308 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 34.8（3 年第 58 百分位；20 日前第 86）；觀察
- 回填樣本 132 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-11-05）：🟢 GREEN
- 🔀 背離：前提健在（GREEN）、價格 20 日 -17.4% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 26.0，3 年分位 85 → 49
  - 🟢 M1 revenue_acceleration：2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9
  - 🟢 M3 adr_premium：ADR 溢價 +16.3%（1 年第 34 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3666.0M, YoY +65.1%
  - 🟢 M5 narrative_triggers：export_controls_tariffs:11e(14m) / n2_arizona_ramp:20e(27m) / cowos_capacity:9e / geopolitics:1e / hyperscaler_capex:4e
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 1（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 26.0（3 年第 49 百分位；20 日前第 85）；觀察
- 回填樣本 26 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | -11.70% | +496.00% | +317.10% | +157.11 |
| 2383 | 台光電 | CCL | -15.68% | +203.10% | +167.30% | +36.61 |
| 2382 | 廣達 | 機櫃 | +7.71% | +76.70% | +128.50% | -27.31 |
| 3231 | 緯創 | 機櫃 | +5.03% | +117.60% | +123.70% | -24.46 |
| 3443 | 創意 | ASIC | -5.31% | +127.00% | +111.90% | +7.97 |
| 6669 | 緯穎 | 機櫃 | -11.50% | +80.90% | +77.10% | +15.29 |
| 2345 | 智邦 | 網通 | -16.96% | +91.20% | +72.20% | +15.87 |
| 3037 | 欣興 | 載板 | -23.90% | +67.60% | +62.80% | +5.68 |
| 3017 | 奇鋐 | 散熱 | -16.71% | +44.90% | +52.20% | -6.24 |
| 2330 | 台積電 | 製造 | +3.19% | +54.60% | +50.90% | +4.98 |
| 2317 | 鴻海 | 機櫃 | +8.30% | +45.70% | +45.40% | -3.12 |
| 3324 | 雙鴻 | 散熱 | -10.45% | +44.70% | +45.10% | -11.21 |
| 3711 | 日月光投控 | 封測 | -8.57% | +45.50% | +44.80% | +1.18 |
| 2308 | 台達電 | 電力 | -27.94% | +14.60% | +32.40% | -16.57 |
| 2301 | 光寶科 | 電源 | -13.18% | +22.10% | +28.30% | -7.73 |
| 2454 | 聯發科 | IC設計 | -10.50% | +2.00% | +19.40% | -5.09 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：35 個月，籃子 +118.17% vs 0050 +71.16%，差 +47.01 pp；判準 可讀
月營收加速三分位 vs T+20 超額：可讀（n 達門檻）（回填 256 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-11-10（1 天後）台股月營收公告截止（2330／2308 通常 10 日前後）
- 2026-12-10（31 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-11-06
- ✅ DCA 帳本：最新 2026-11-06
- ✅ delta_radar：最新 2026-11-09
- ✅ tsmc_radar：最新 2026-11-07
- ✅ 賭場 sector：最新 2026-11-06

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-11-09T12:07:15+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-11-06

## 鋒面：🥶 **CAPITULATION** 　(score -0.68)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`-1,608,491,452,137`，落在近一年第 **0** 百分位
- 外資大台淨倉 Δ：`-4,279`，落在近一年第 **8** 百分位（水位 -99,930 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+5,916`，落在近一年第 **45** 百分位
- 融資餘額變化：`-42,356,407,000`，落在近一年第 **0** 百分位

## 🚨 🥶 投降警報 — 歷史上此類尾部共現日為 DCA 加速窗口（見回測）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-11-09 12:07 UTC

## 總判定：🟡 YELLOW

## 🔀 前提 vs 價格：🔀 背離：前提健在（YELLOW）、價格 20 日 -41.7% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 34.8，3 年分位 86 → 58

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🔴 RED | 2026-09 YoY +14.6%, slope -13.60pp/月, 連續減速 3 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74 |
| M3 thai_shadow | 🟢 GREEN | DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3% |
| M4 customs_flow | 🟡 YELLOW | US 進口 HS850440 (TH+TW) 近3月 $1376.6M, YoY +19.9% |
| M5 narrative_triggers | 🟢 GREEN | capex_cut:4e / vr300_delay:8e / debt_financed_capex:13e / lc_psu_competition:0e |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2308 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 34.8（3 年第 58 百分位；20 日前第 86）；觀察 |

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
    "capex_cut": 4,
    "vr300_delay": 8,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 4,
    "vr300_delay": 8,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": -1.42,
      "denial": false
    },
    "vr300_delay": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": -1.19,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 13,
      "mentions": 13,
      "gate": "zscore",
      "z": 0.06,
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
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch. - CNBC
- [debt_financed_capex] Top hyperscalers likely to have more AI-linked debt than now known, S&P Global warns - Reuters
- [debt_financed_capex] Oracle's Negative Free Cash Flow Exposes the Uncomfortable Truth About AI's Financing Game - 24/7 Wall St.

### M6 peer_divergence — 🟢 GREEN
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
        "2301": 26.5,
        "6282": 34.8
      }
    },
    "cooling": {
      "direction": "peer_lead_risk",
      "delta_3m_yoy": 32.4,
      "best_peer": "3324",
      "best_peer_3m_yoy": 45.1,
      "peer_lead_pp": 12.6,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3324": 45.1,
        "3017": 44.5
      }
    },
    "rack": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 32.4,
      "best_peer": "2382",
      "best_peer_3m_yoy": 119.4,
      "peer_lead_pp": 86.9,
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
  "as_of": "2026-11-09",
  "per": 34.83,
  "per_pct": 58.2,
  "per_then": 63.34,
  "per_pct_then": 86.4,
  "pbr": 9.47,
  "dividend_yield": 1.0,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **4** 筆；state 已有 outcomes 的 entry：**157/157**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 11 / -8.85 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向對 |
| M2 | 26 / -8.93 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 21 / -5.68 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 39 / -7.91 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M5 | 53 / -5.57 | 61 / -9.82 | 47 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 31 / -5.40 | 4 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# TSMC Radar (2330.TW) — 2026-11-07 09:59 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（GREEN）、價格 20 日 -17.4% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 26.0，3 年分位 85 → 49

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:11e(14m) / n2_arizona_ramp:20e(27m) / cowos_capacity:9e / geopolitics:1e / hyperscaler_capex:4e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "export_controls_tariffs": 11,
    "n2_arizona_ramp": 20,
    "cowos_capacity": 9,
    "geopolitics": 1,
    "hyperscaler_capex": 4
  },
  "mentions": {
    "export_controls_tariffs": 14,
    "n2_arizona_ramp": 27,
    "cowos_capacity": 9,
    "geopolitics": 1,
    "hyperscaler_capex": 4
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 11,
      "mentions": 14,
      "gate": "zscore",
      "z": -1.69,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 20,
      "mentions": 27,
      "gate": "zscore",
      "z": 0.82,
      "denial": true
    },
    "cowos_capacity": {
      "events": 9,
      "mentions": 9,
      "gate": "zscore",
      "z": 1.37,
      "denial": false
    },
    "geopolitics": {
      "events": 1,
      "mentions": 1,
      "gate": "zscore",
      "z": -0.72,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": -0.93,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] TSMC is seeking chipmaking equipment that doesn't contain Chinese rare-earth magnets — asks suppliers to provide alterna
- [export_controls_tariffs] TSMC Seeks Rare-Earth-Free Factory Equipment as China’s Export Controls Threaten Chip Supply Chains - Tekedia
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC, report claim
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - The Motley Fool
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **2** 筆；state 已有 outcomes 的 entry：**59/59**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 9 / +1.24 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 9 / +1.24 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 8 / +1.32 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 8 / +1.98 | 17 / +1.14 | 30 | 累積中（GREEN n=8 < 30）；方向對 |
| M6 | 9 / +1.24 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-11-06

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1904 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-11-06** · 純定期定額 10,000 元
- 投降窗加碼：**待執行** 10000.0 元（警報日 2026-11-06）
- 鋒面 CAPITULATION → 調節規則本期 ×2 = 20,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-11-06）：本週有投降警報（2026-11-06）→ 下一交易日投入 20,000 元，當月不再行動

## 視窗：full（2019-01-02 → 2026-11-06，95 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 95 | 950,000 | 28,714.80 | 33.08 | +0.00% | 2,656,119 | +179.59% | +25.67% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 1,000,000 | 30,035.77 | 33.29 | +0.63% | 2,778,309 | +177.83% | +25.99% |
| 定期定額＋投降窗加碼 | 103 | 1,030,000 | 30,946.83 | 33.28 | +0.60% | 2,862,581 | +177.92% | +25.78% |
| 定期定額＋鋒面調節 | 95 | 1,045,000 | 31,260.12 | 33.43 | +1.06% | 2,891,561 | +176.70% | +25.60% |
| 對照：一次投入 | 1 | 950,000 | 51,342.14 | 18.50 | -44.07% | 4,749,148 | +399.91% | +22.80% |

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

加碼 edge 平均 +1.17%、勝率 75%（n=8）。正 = 警報日買比等到例行日買便宜。

## 視窗：last_12m（2025-11-06 → 2026-11-06，13 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 13 | 130,000 | 1,535.32 | 84.67 | +0.00% | 142,017 | +9.24% | +18.98% |
| 週檢查・月預算・投降窗即刻投入 | 12 | 140,000 | 1,640.60 | 85.33 | +0.78% | 151,755 | +8.40% | +17.12% |
| 定期定額＋投降窗加碼 | 15 | 150,000 | 1,739.66 | 86.22 | +1.83% | 160,919 | +7.28% | +15.83% |
| 定期定額＋鋒面調節 | 13 | 160,000 | 1,864.64 | 85.81 | +1.35% | 172,479 | +7.80% | +17.34% |
| 對照：一次投入 | 1 | 130,000 | 2,051.96 | 63.35 | -25.18% | 189,806 | +46.00% | +46.00% |

加碼逐筆（跟「同一筆錢等到下一個例行買日」比；T+60 交易日）：

| 警報日 | 執行日 | 執行價 | 下一例行買日 | 例行價 | edge | T+60 |
|---|---|---|---|---|---|---|
| 2026-07-20 | 2026-07-21 | 102.5 | 2026-08-06 | 103.30 | +0.78% | +6.34% |
| 2026-07-29 | 2026-07-30 | 93.5 | 2026-08-06 | 103.30 | +10.48% | +14.71% |

加碼 edge 平均 +5.63%、勝率 100%（n=2）。正 = 警報日買比等到例行日買便宜。

分割還原：2025-06-18 ×4（override）。

---
*dca_ledger — 規則影子帳本，等額假設。lump_sum 是對照不是策略（沒人一開始就有全部的錢）；regime_scaled 是待資料處決的假說。非投資建議。*

---

# 🎰 賭場 sector — AI 個股影子追蹤（2026-11-06）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 2830.0 | -32.3% | -11.7% | +496.0% | +317.1% | +157.1 |
| 2383 | 台光電 | CCL | ✓ | 3820.0 | -36.3% | -15.7% | +203.1% | +167.3% | +36.6 |
| 2382 | 廣達 | 機櫃 | ✓ | 290.5 | -12.9% | +7.7% | +76.7% | +128.5% | -27.3 |
| 3231 | 緯創 | 機櫃 | ✓ | 160.0 | -15.6% | +5.0% | +117.6% | +123.7% | -24.5 |
| 3443 | 創意 | ASIC |  | 6205.0 | -25.9% | -5.3% | +127.0% | +111.9% | +8.0 |
| 6669 | 緯穎 | 機櫃 | ✓ | 1555.0 | -32.1% | -11.5% | +80.9% | +77.1% | +15.3 |
| 2345 | 智邦 | 網通 | ✓ | 1280.0 | -37.6% | -17.0% | +91.2% | +72.2% | +15.9 |
| 3037 | 欣興 | 載板 | ✓ | 727.0 | -44.5% | -23.9% | +67.6% | +62.8% | +5.7 |
| 3017 | 奇鋐 | 散熱 | ✓ | 2310.0 | -37.3% | -16.7% | +44.9% | +52.2% | -6.2 |
| 2330 | 台積電 | 製造 | ✓ | 2135.0 | -17.4% | +3.2% | +54.6% | +50.9% | +5.0 |
| 2317 | 鴻海 | 機櫃 | ✓ | 224.5 | -12.3% | +8.3% | +45.7% | +45.4% | -3.1 |
| 3324 | 雙鴻 | 散熱 |  | 1055.0 | -31.1% | -10.4% | +44.7% | +45.1% | -11.2 |
| 3711 | 日月光投控 | 封測 | ✓ | 527.0 | -29.2% | -8.6% | +45.5% | +44.8% | +1.2 |
| 2308 | 台達電 | 電力 | ✓ | 1055.0 | -48.5% | -27.9% | +14.6% | +32.4% | -16.6 |
| 2301 | 光寶科 | 電源 | ✓ | 198.0 | -33.8% | -13.2% | +22.1% | +28.3% | -7.7 |
| 2454 | 聯發科 | IC設計 | ✓ | 3390.0 | -31.1% | -10.5% | +2.0% | +19.4% | -5.1 |

## 借券（只收資料，不是訊號）

> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。

| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |
|---|---|---|---|---|---|---|
| 3661 | 740 | +137.0% | 18 | 0.3 | 1.00%（66 筆） | 20 |
| 2383 | 735 | +23.1% | 40 | 0.2 | 0.18%（67 筆） | 92 |
| 2382 | 73,535 | +17.3% | 17 | 5.6 | 1.00%（139 筆） | 123 |
| 3231 | 34,439 | -43.1% | 4 | 0.9 | 0.50%（101 筆） | 377 |
| 3443 | 1,529 | -16.9% | 89 | 0.7 | 1.00%（96 筆） | 143 |
| 6669 | 3,829 | -71.5% | 2 | 0.7 | 6.50%（257 筆） | 233 |
| 2345 | 956 | +52.8% | 21 | 0.2 | 0.33%（66 筆） | 7 |
| 3037 | 4,974 | +69.1% | 22 | 0.2 | 0.22%（81 筆） | 545 |
| 3017 | 3,326 | +89.1% | 68 | 1.1 | 0.50%（64 筆） | 84 |
| 2330 | 20,182 | +51.2% | 100 | 0.5 | 0.25%（276 筆） | 75 |
| 2317 | 97,220 | +132.8% | 86 | 2.2 | 0.25%（184 筆） | 488 |
| 3324 | 4,222 | +37.4% | 55 | 1.1 | 5.00%（88 筆） | 33 |
| 3711 | 23,103 | +149.9% | 22 | 1.1 | 0.25%（104 筆） | 89 |
| 2308 | 13,210 | +122.8% | 96 | 0.8 | 0.25%（148 筆） | 30 |
| 2301 | 6,910 | +251.6% | 26 | 0.4 | 0.35%（100 筆） | 28 |
| 2454 | 6,211 | +16.3% | 97 | 0.6 | 0.25%（134 筆） | 39 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 35 個月、投入 175,000 元（16 檔等權）
- 籃子市值 381,802（+118.2%）；0050 市值 299,528（+71.2%）；差 **+47.0 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 前三分之一 n=85 超額 +1.4%；後三分之一 n=85 超額 -5.2%；全部 -2.5%
- 狀態：可讀（n 達門檻）（state 576 筆、已回填 T+20 256 筆）

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

