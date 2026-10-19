# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-10-19 10:00 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-10-19

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-10-16）：本週無警報、預算未動 → 等（2026-10-23 再看）。
- 鋒面 ☀️ RISK_ON（本週未變）。
- 2308 前提 🔴 RED；無背離（前提 RED、價格 20 日 -4.1%）；PER 52.2，3 年分位 77 → 72
- 2330 前提 🟢 GREEN；無背離（前提 GREEN、價格 20 日 +1.7%）；PER 28.1，3 年分位 67 → 71
- 投降窗加碼歷史 8 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +0.67%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-10-16）：本週無警報、預算未動 → 等（2026-10-23 再看）
- 例行（對照）：**2026-11-06** 買 10,000 元（本月已買）
- 投降窗加碼：無
- 鋒面調節（假說）：RISK_ON ×1 = 10,000 元

自 2019-01-02 起 94 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 94 | 32.86 | +0.00% | +231.72% | +30.12% |
| 週檢查・月預算・投降窗即刻投入 | 93 | 33.07 | +0.64% | +229.64% | +30.54% |
| 定期定額＋投降窗加碼 | 102 | 33.08 | +0.67% | +229.55% | +30.27% |
| 定期定額＋鋒面調節 | 94 | 33.02 | +0.49% | +230.13% | +30.06% |
| 對照：一次投入 | 1 | 18.5 | -43.70% | +489.08% | +25.61% |

投降窗加碼 8 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 ☀️ **RISK_ON**（score -0.24，2026-10-16）；本週未變
- 分位數：外資現貨 16.3、大台Δ 94.0、散戶小台 84.1、融資Δ 25.4
- 本週投降警報：無
- 警報戰績（月更回測）：8 簇，20 日中位 +8.72% vs 基線 +2.19%、命中 75%

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-10-19）：🔴 RED
- 無背離（前提 RED、價格 20 日 -4.1%）；PER 52.2，3 年分位 77 → 72
  - 🔴 M1 revenue_acceleration：2026-09 YoY +14.6%, slope -13.60pp/月, 連續減速 3 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32
  - 🟡 M3 thai_shadow：DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8%
  - 🟢 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1366.7M, YoY +22.4%
  - 🟢 M5 narrative_triggers：capex_cut:6e / vr300_delay:17e(22m) / debt_financed_capex:13e(14m) / lc_psu_competition:0e
  - 🔴 M6 peer_divergence：cooling:3324領先+37pp
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 52.2（3 年第 72 百分位；20 日前第 77）；觀察
- 回填樣本 109 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-10-19）：🟢 GREEN
- 無背離（前提 GREEN、價格 20 日 +1.7%）；PER 28.1，3 年分位 67 → 71
  - 🟢 M1 revenue_acceleration：2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9
  - 🟢 M3 adr_premium：ADR 溢價 +10.6%（1 年第 5 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3675.7M, YoY +60.6%
  - 🟢 M5 narrative_triggers：export_controls_tariffs:16e / n2_arizona_ramp:10e(11m) / cowos_capacity:4e / geopolitics:5e / hyperscaler_capex:6e
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 28.1（3 年第 71 百分位；20 日前第 67）；觀察
- 回填樣本 5 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | +7.25% | +496.00% | +317.10% | +157.11 |
| 2383 | 台光電 | CCL | -1.61% | +168.90% | +142.70% | +19.74 |
| 2382 | 廣達 | 機櫃 | -5.89% | +76.70% | +128.50% | -27.31 |
| 3443 | 創意 | ASIC | +21.35% | +97.80% | +122.40% | -30.30 |
| 3231 | 緯創 | 機櫃 | -2.59% | +87.20% | +104.80% | +13.21 |
| 3324 | 雙鴻 | 散熱 | +10.51% | +23.20% | +69.00% | -46.74 |
| 2345 | 智邦 | 網通 | +5.02% | +66.10% | +65.70% | -2.78 |
| 6669 | 緯穎 | 機櫃 | -22.89% | +100.00% | +63.20% | +30.38 |
| 3037 | 欣興 | 載板 | +12.03% | +64.70% | +54.90% | +10.49 |
| 3017 | 奇鋐 | 散熱 | +3.83% | +44.90% | +52.20% | -6.24 |
| 2330 | 台積電 | 製造 | -1.12% | +54.60% | +50.90% | +4.98 |
| 2317 | 鴻海 | 機櫃 | -3.60% | +38.40% | +48.20% | -7.89 |
| 3711 | 日月光投控 | 封測 | +10.75% | +45.50% | +44.80% | +1.18 |
| 2308 | 台達電 | 電力 | -4.69% | +14.60% | +32.40% | -16.57 |
| 2301 | 光寶科 | 電源 | -6.06% | +22.10% | +28.30% | -7.73 |
| 2454 | 聯發科 | IC設計 | -6.65% | +2.00% | +19.40% | -5.09 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：34 個月，籃子 +192.91% vs 0050 +104.16%，差 +88.76 pp；判準 可讀
月營收加速三分位 vs T+20 超額：累積中（每側需 n≥30）（回填 48 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-11-10（22 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-10-16
- ✅ DCA 帳本：最新 2026-10-16
- ✅ delta_radar：最新 2026-10-19
- ✅ tsmc_radar：最新 2026-10-19
- ✅ 賭場 sector：最新 2026-10-16

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-10-19T10:00:50+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-10-16

## 鋒面：☀️ **RISK_ON** 　(score -0.24)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`-465,704,922,321`，落在近一年第 **16** 百分位
- 外資大台淨倉 Δ：`+3,907`，落在近一年第 **94** 百分位（水位 -93,675 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+11,123`，落在近一年第 **84** 百分位
- 融資餘額變化：`-820,967,000`，落在近一年第 **25** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-10-19 09:18 UTC

## 總判定：🔴 RED

## 前提 vs 價格：無背離（前提 RED、價格 20 日 -4.1%）；PER 52.2，3 年分位 77 → 72

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🔴 RED | 2026-09 YoY +14.6%, slope -13.60pp/月, 連續減速 3 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32 |
| M3 thai_shadow | 🟡 YELLOW | DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8% |
| M4 customs_flow | 🟢 GREEN | US 進口 HS850440 (TH+TW) 近3月 $1366.7M, YoY +22.4% |
| M5 narrative_triggers | 🟢 GREEN | capex_cut:6e / vr300_delay:17e(22m) / debt_financed_capex:13e(14m) / lc_psu_competition:0e |
| M6 peer_divergence | 🔴 RED | cooling:3324領先+37pp |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 52.2（3 年第 72 百分位；20 日前第 77）；觀察 |

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
    "vr300_delay": 17,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 6,
    "vr300_delay": 22,
    "debt_financed_capex": 14,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": 0.48,
      "denial": false
    },
    "vr300_delay": {
      "events": 17,
      "mentions": 22,
      "gate": "zscore",
      "z": 0.13,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 13,
      "mentions": 14,
      "gate": "zscore",
      "z": 0.02,
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
- [capex_cut] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [capex_cut] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] Oracle Courts Apollo and Goldman for AI Chip Financing as Debt Tops $169 Billion - TIKR.com
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - Yahoo Finance
- [debt_financed_capex] The AI Buildout Needs a Lot of Money— Enter Debt (and Financial Engineering) - Carson Group

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
  "as_of": "2026-10-19",
  "per": 52.2,
  "per_pct": 72.0,
  "per_then": 54.42,
  "per_pct_then": 76.9,
  "pbr": 14.5,
  "dividend_yield": 0.71,
  "history_years": 3,
  "n": 734
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **9** 筆；state 已有 outcomes 的 entry：**145/145**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 5 / +1.75 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M2 | 20 / -6.30 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向對 |
| M3 | 27 / -10.89 | 15 / -0.88 | 1 | 無法判定（狀態翻轉 1 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 33 / -6.14 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 43 / -1.61 | 51 / -9.13 | 47 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 25 / -2.45 | 3 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# TSMC Radar (2330.TW) — 2026-10-19 10:00 UTC

## 總判定：🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +1.7%）；PER 28.1，3 年分位 67 → 71

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +10.6%（1 年第 5 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3675.7M, YoY +60.6% |
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:16e / n2_arizona_ramp:10e(11m) / cowos_capacity:4e / geopolitics:5e / hyperscaler_capex:6e |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 0（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 28.1（3 年第 71 百分位；20 日前第 67）；觀察 |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-09",
  "latest_yoy_pct": 54.6,
  "yoy_slope_pp_per_month": -4.41,
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
  "as_of": "2026-10-19",
  "premium_pct": 10.55,
  "percentile_1y": 5.1,
  "n": 370
}
```

### M4 customs_flow — 🟢 GREEN
```json
{
  "window": "2026-06..2026-08",
  "rolling_value_usd_m": 3675.7,
  "rolling_yoy_pct": 60.6,
  "by_country": {
    "TAIWAN": {
      "rolling_value_usd_m": 3675.7,
      "rolling_yoy_pct": 60.6
    }
  }
}
```

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 10,
    "cowos_capacity": 4,
    "geopolitics": 5,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 11,
    "cowos_capacity": 4,
    "geopolitics": 5,
    "hyperscaler_capex": 6
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 16,
      "mentions": 16,
      "gate": "zscore",
      "z": 0.68,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 10,
      "mentions": 11,
      "gate": "zscore",
      "z": 0.0,
      "denial": false
    },
    "cowos_capacity": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": -0.37,
      "denial": false
    },
    "geopolitics": {
      "events": 5,
      "mentions": 5,
      "gate": "zscore",
      "z": 1.32,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": 0.48,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [n2_arizona_ramp] DIGITIMES Insight: Microsoft Maia 300 leads 2nm race, TSMC's US strategy shifts, Intel EMIB-T faces yield challenge - di
- [n2_arizona_ramp] Samsung's 2nm Yield Approaches 60%, Leveraging Tesla Orders to Challenge TSMC - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Medium
- [cowos_capacity] [News] While TSMC’s CoWoS Faces Supply Shortage, Samsung Reportedly Secures NVIDIA’s 2.5D Advanced Packaging Order - Tre
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.

### M6 peer_divergence — 🟢 GREEN
```json
{
  "groups": {
    "foundry_contrast": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 50.9,
      "best_peer": "2303",
      "best_peer_3m_yoy": 25.6,
      "peer_lead_pp": -25.2,
      "status": "GREEN",
      "peers_3m_yoy": {
        "2303": 25.6
      }
    },
    "backend": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 50.9,
      "best_peer": "2383",
      "best_peer_3m_yoy": 142.7,
      "peer_lead_pp": 91.8,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3711": 44.8,
        "3037": 54.9,
        "2383": 142.7
      }
    },
    "asic_lead": {
      "direction": "cohort_confirm",
      "delta_3m_yoy": 50.9,
      "best_peer": "3661",
      "best_peer_3m_yoy": 317.1,
      "peer_lead_pp": 266.2,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3661": 317.1,
        "3443": 122.4
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
  "as_of": "2026-10-19",
  "per": 28.05,
  "per_pct": 70.7,
  "per_then": 27.59,
  "per_pct_then": 66.8,
  "pbr": 9.76,
  "dividend_yield": 0.91,
  "history_years": 3,
  "n": 734
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**40/40**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 3 / +0.65 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 3 / +0.65 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 2 / +0.65 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 0 / — | 5 / +0.30 | 17 | 樣本不足（缺一側 cohort） |
| M6 | 3 / +0.65 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-10-16

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1891 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-11-06**（本月已買） · 純定期定額 10,000 元
- 投降窗加碼：無（近 5 個交易日無警報）
- 鋒面 RISK_ON → 調節規則本期 ×1 = 10,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-10-16）：本週無警報、預算未動 → 等（2026-10-23 再看）

## 視窗：full（2019-01-02 → 2026-10-16，94 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 94 | 940,000 | 28,606.78 | 32.86 | +0.00% | 3,118,139 | +231.72% | +30.12% |
| 週檢查・月預算・投降窗即刻投入 | 93 | 990,000 | 29,939.79 | 33.07 | +0.64% | 3,263,438 | +229.64% | +30.54% |
| 定期定額＋投降窗加碼 | 102 | 1,020,000 | 30,838.81 | 33.08 | +0.67% | 3,361,430 | +229.55% | +30.27% |
| 定期定額＋鋒面調節 | 94 | 1,025,000 | 31,044.08 | 33.02 | +0.49% | 3,383,805 | +230.13% | +30.06% |
| 對照：一次投入 | 1 | 940,000 | 50,801.69 | 18.50 | -43.70% | 5,537,385 | +489.08% | +25.61% |

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
| 2026-07-29 | 2026-07-30 | 93.5 | 2026-08-06 | 103.30 | +10.48% | — |

加碼 edge 平均 +1.17%、勝率 75%（n=8）。正 = 警報日買比等到例行日買便宜。

## 視窗：last_12m（2025-10-16 → 2026-10-16，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,427.31 | 84.07 | +0.00% | 155,576 | +29.65% | +67.13% |
| 週檢查・月預算・投降窗即刻投入 | 12 | 140,000 | 1,708.33 | 81.95 | -2.52% | 186,208 | +33.01% | +68.97% |
| 定期定額＋投降窗加碼 | 14 | 140,000 | 1,631.64 | 85.80 | +2.06% | 177,849 | +27.04% | +66.76% |
| 定期定額＋鋒面調節 | 12 | 140,000 | 1,648.60 | 84.92 | +1.01% | 179,698 | +28.36% | +66.30% |
| 對照：一次投入 | 1 | 120,000 | 1,894.11 | 63.35 | -24.65% | 206,458 | +72.05% | +77.84% |

加碼逐筆（跟「同一筆錢等到下一個例行買日」比；T+60 交易日）：

| 警報日 | 執行日 | 執行價 | 下一例行買日 | 例行價 | edge | T+60 |
|---|---|---|---|---|---|---|
| 2026-07-20 | 2026-07-21 | 102.5 | 2026-08-06 | 103.30 | +0.78% | +6.34% |
| 2026-07-29 | 2026-07-30 | 93.5 | 2026-08-06 | 103.30 | +10.48% | — |

加碼 edge 平均 +5.63%、勝率 100%（n=2）。正 = 警報日買比等到例行日買便宜。

分割還原：2025-06-18 ×4（override）。

---
*dca_ledger — 規則影子帳本，等額假設。lump_sum 是對照不是策略（沒人一開始就有全部的錢）；regime_scaled 是待資料處決的假說。非投資建議。*

---

# 🎰 賭場 sector — AI 個股影子追蹤（2026-10-16）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 3685.0 | +9.8% | +7.2% | +496.0% | +317.1% | +157.1 |
| 2383 | 台光電 | CCL | ✓ | 5165.0 | +1.0% | -1.6% | +168.9% | +142.7% | +19.7 |
| 2382 | 廣達 | 機櫃 | ✓ | 322.0 | -3.3% | -5.9% | +76.7% | +128.5% | -27.3 |
| 3443 | 創意 | ASIC |  | 7480.0 | +23.9% | +21.4% | +97.8% | +122.4% | -30.3 |
| 3231 | 緯創 | 機櫃 | ✓ | 182.5 | +0.0% | -2.6% | +87.2% | +104.8% | +13.2 |
| 3324 | 雙鴻 | 散熱 |  | 1425.0 | +13.1% | +10.5% | +23.2% | +69.0% | -46.7 |
| 2345 | 智邦 | 網通 | ✓ | 1980.0 | +7.6% | +5.0% | +66.1% | +65.7% | -2.8 |
| 6669 | 緯穎 | 機櫃 | ✓ | 1845.0 | -20.3% | -22.9% | +100.0% | +63.2% | +30.4 |
| 3037 | 欣興 | 載板 | ✓ | 1090.0 | +14.6% | +12.0% | +64.7% | +54.9% | +10.5 |
| 3017 | 奇鋐 | 散熱 | ✓ | 3315.0 | +6.4% | +3.8% | +44.9% | +52.2% | -6.2 |
| 2330 | 台積電 | 製造 | ✓ | 2420.0 | +1.5% | -1.1% | +54.6% | +50.9% | +5.0 |
| 2317 | 鴻海 | 機櫃 | ✓ | 244.0 | -1.0% | -3.6% | +38.4% | +48.2% | -7.9 |
| 3711 | 日月光投控 | 封測 | ✓ | 671.0 | +13.3% | +10.8% | +45.5% | +44.8% | +1.2 |
| 2308 | 台達電 | 電力 | ✓ | 1635.0 | -2.1% | -4.7% | +14.6% | +32.4% | -16.6 |
| 2301 | 光寶科 | 電源 | ✓ | 264.5 | -3.5% | -6.1% | +22.1% | +28.3% | -7.7 |
| 2454 | 聯發科 | IC設計 | ✓ | 4250.0 | -4.1% | -6.7% | +2.0% | +19.4% | -5.1 |

## 借券（只收資料，不是訊號）

> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。

| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |
|---|---|---|---|---|---|---|
| 3661 | 408 | -66.4% | 7 | 0.1 | 1.25%（45 筆） | 24 |
| 2383 | 784 | +60.0% | 38 | 0.3 | 0.03%（45 筆） | 6 |
| 2382 | 64,656 | -4.5% | 7 | 5.1 | 1.38%（152 筆） | 115 |
| 3443 | 1,419 | +26.4% | 80 | 0.9 | 1.00%（75 筆） | 237 |
| 3231 | 36,798 | -85.0% | 2 | 1.0 | 1.10%（87 筆） | 385 |
| 3324 | 4,259 | +45.8% | 60 | 1.0 | 5.00%（61 筆） | 67 |
| 2345 | 745 | -12.9% | 8 | 0.2 | 0.40%（38 筆） | 4 |
| 6669 | 12,126 | -16.9% | 89 | 2.6 | 16.00%（177 筆） | 488 |
| 3037 | 4,552 | -0.3% | 15 | 0.3 | 0.01%（47 筆） | 281 |
| 3017 | 1,751 | +9.0% | 30 | 0.6 | 0.63%（61 筆） | 40 |
| 2330 | 12,912 | -22.3% | 72 | 0.5 | 0.25%（265 筆） | 9 |
| 2317 | 82,417 | +102.2% | 83 | 2.1 | 0.25%（106 筆） | 424 |
| 3711 | 9,252 | -56.8% | 2 | 0.6 | 0.25%（68 筆） | 170 |
| 2308 | 10,663 | +37.7% | 100 | 0.9 | 0.25%（105 筆） | 33 |
| 2301 | 3,044 | -22.6% | 4 | 0.2 | 0.35%（44 筆） | 66 |
| 2454 | 7,605 | +54.0% | 100 | 0.9 | 0.25%（114 筆） | 20 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 34 個月、投入 170,000 元（16 檔等權）
- 籃子市值 497,955（+192.9%）；0050 市值 347,070（+104.2%）；差 **+88.8 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 前三分之一 n=16 超額 +3.0%；後三分之一 n=16 超額 -1.0%；全部 +0.4%
- 狀態：累積中（每側需 n≥30）（state 368 筆、已回填 T+20 48 筆）

分割還原：0050 2025-06-18 ×4（override）、6669 2026-09-02 ×3（override）

---
*casino_tracker — 只收資料。名單不是訊號、籃子不是建議；期望值未證明前，這筆錢是娛樂預算。*

---

# tw_scanner 警報回測 — 警報後遠期報酬 vs 無條件基線

## capitulation — 觸發 14 日 / 8 個事件簇
| 水平 | 事件後中位數 | 事件後均值 | 基線中位數 | 命中率(同號) | n |
|---|---|---|---|---|---|
| 20日 | +8.72% | +7.31% | +2.19% | 75% | 8 |
| 60日 | +9.80% | +12.71% | +5.03% | 83% | 6 |

事件日列表: 2020-03-09, 2020-03-19, 2022-03-08, 2024-04-22, 2024-07-19, 2024-08-05, 2026-07-20, 2026-07-29

> 判讀準則：事件後分佈與基線無法分離 ⇒ 刪除該警報。儀器不留裝飾品。

---

