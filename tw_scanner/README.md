# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-10-30 08:58 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-10-30

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-10-30）：本月預算已於 2026-10-27 動用（月末例行），本月不再行動。
- 鋒面 🌧️ DE_RISK（本週未變）。
- 2308 前提 🔴 RED；無背離（前提 RED、價格 20 日 -27.2%）；PER 44.4，3 年分位 84 → 63
- 2330 前提 🟢 GREEN；無背離（前提 GREEN、價格 20 日 -2.4%）；PER 28.0，3 年分位 77 → 70
- 投降窗加碼歷史 8 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +0.67%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-10-30）：本月預算已於 2026-10-27 動用（月末例行），本月不再行動
- 例行（對照）：**2026-11-06** 買 10,000 元（本月已買）
- 投降窗加碼：無
- 鋒面調節（假說）：DE_RISK ×1.5 = 15,000 元

自 2019-01-02 起 94 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 94 | 32.86 | +0.00% | +226.39% | +29.48% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 33.3 | +1.34% | +222.11% | +29.89% |
| 定期定額＋投降窗加碼 | 102 | 33.08 | +0.67% | +224.26% | +29.63% |
| 定期定額＋鋒面調節 | 94 | 33.02 | +0.49% | +224.83% | +29.42% |
| 對照：一次投入 | 1 | 18.5 | -43.70% | +479.63% | +25.22% |

投降窗加碼 8 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 🌧️ **DE_RISK**（score -0.69，2026-10-29）；本週未變
- 分位數：外資現貨 2.0、大台Δ 6.7、散戶小台 89.3、融資Δ 42.1
- 本週投降警報：無
- 警報戰績（月更回測）：8 簇，20 日中位 +8.72% vs 基線 +2.19%、命中 75%

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-10-29）：🔴 RED
- 無背離（前提 RED、價格 20 日 -27.2%）；PER 44.4，3 年分位 84 → 63
  - 🔴 M1 revenue_acceleration：2026-09 YoY +14.6%, slope -13.60pp/月, 連續減速 3 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74
  - 🟢 M3 thai_shadow：DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3%
  - 🟢 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1366.7M, YoY +22.4%
  - 🟢 M5 narrative_triggers：capex_cut:7e(8m) / vr300_delay:13e(18m) / debt_financed_capex:12e(14m) / lc_psu_competition:0e
  - 🔴 M6 peer_divergence：cooling:3324領先+37pp
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 44.4（3 年第 63 百分位；20 日前第 84）；觀察
- 回填樣本 124 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-10-29）：🟢 GREEN
- 無背離（前提 GREEN、價格 20 日 -2.4%）；PER 28.0，3 年分位 77 → 70
  - 🟢 M1 revenue_acceleration：2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9
  - 🟢 M3 adr_premium：ADR 溢價 +18.4%（1 年第 44 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3675.7M, YoY +60.6%
  - 🟡 M5 narrative_triggers：export_controls_tariffs:12e(13m) / n2_arizona_ramp:18e(25m) / cowos_capacity:8e / geopolitics:1e / hyperscaler_capex:9e(10m)
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 1（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 28.0（3 年第 70 百分位；20 日前第 77）；觀察
- 回填樣本 12 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | +2.19% | +496.00% | +317.10% | +157.11 |
| 2383 | 台光電 | CCL | +3.79% | +168.90% | +142.70% | +19.74 |
| 2382 | 廣達 | 機櫃 | -1.48% | +76.70% | +128.50% | -27.31 |
| 3443 | 創意 | ASIC | -5.80% | +97.80% | +122.40% | -30.30 |
| 3231 | 緯創 | 機櫃 | +6.75% | +87.20% | +104.80% | +13.21 |
| 3324 | 雙鴻 | 散熱 | -9.75% | +23.20% | +69.00% | -46.74 |
| 2345 | 智邦 | 網通 | -2.81% | +66.10% | +65.70% | -2.78 |
| 6669 | 緯穎 | 機櫃 | -6.29% | +100.00% | +63.20% | +30.38 |
| 3037 | 欣興 | 載板 | -7.66% | +64.70% | +54.90% | +10.49 |
| 3017 | 奇鋐 | 散熱 | -8.08% | +44.90% | +52.20% | -6.24 |
| 2330 | 台積電 | 製造 | +2.16% | +54.60% | +50.90% | +4.98 |
| 2317 | 鴻海 | 機櫃 | +3.58% | +38.40% | +48.20% | -7.89 |
| 3711 | 日月光投控 | 封測 | +2.29% | +45.50% | +44.80% | +1.18 |
| 2308 | 台達電 | 電力 | -17.93% | +14.60% | +32.40% | -16.57 |
| 2301 | 光寶科 | 電源 | -7.62% | +22.10% | +28.30% | -7.73 |
| 2454 | 聯發科 | IC設計 | -18.88% | +2.00% | +19.40% | -5.09 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：34 個月，籃子 +185.12% vs 0050 +100.88%，差 +84.24 pp；判準 可讀
月營收加速三分位 vs T+20 超額：可讀（n 達門檻）（回填 160 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-11-10（11 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-10-29
- ✅ DCA 帳本：最新 2026-10-29
- ✅ delta_radar：最新 2026-10-30
- ✅ tsmc_radar：最新 2026-10-29
- ✅ 賭場 sector：最新 2026-10-29

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-10-30T08:58:57+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-10-29

## 鋒面：🌧️ **DE_RISK** 　(score -0.69)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`-913,575,570,971`，落在近一年第 **2** 百分位
- 外資大台淨倉 Δ：`-4,605`，落在近一年第 **7** 百分位（水位 -89,522 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+12,913`，落在近一年第 **89** 百分位
- 融資餘額變化：`+1,611,296,000`，落在近一年第 **42** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-10-30 08:58 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 RED、價格 20 日 -27.2%）；PER 44.4，3 年分位 84 → 63

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | capex_cut:7e(8m) / vr300_delay:13e(18m) / debt_financed_capex:12e(14m) / lc_psu_competition:0e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 7,
    "vr300_delay": 13,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 8,
    "vr300_delay": 18,
    "debt_financed_capex": 14,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 7,
      "mentions": 8,
      "gate": "zscore",
      "z": 0.54,
      "denial": false
    },
    "vr300_delay": {
      "events": 13,
      "mentions": 18,
      "gate": "zscore",
      "z": -1.83,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 12,
      "mentions": 14,
      "gate": "zscore",
      "z": -1.07,
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
- [capex_cut] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - Yahoo Finance
- [capex_cut] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [capex_cut] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch. - CNBC
- [debt_financed_capex] Microsoft Returns to Bond Market to Raise at Least $25 Billion in First Major Debt Sale in Nine Years to Fund AI Infrast
- [debt_financed_capex] Top hyperscalers likely to have more AI-linked debt than now known, S&P Global warns - Reuters

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **6** 筆；state 已有 outcomes 的 entry：**152/152**
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

---

# TSMC Radar (2330.TW) — 2026-10-29 10:57 UTC

## 總判定：🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 -2.4%）；PER 28.0，3 年分位 77 → 70

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +18.4%（1 年第 44 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3675.7M, YoY +60.6% |
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:12e(13m) / n2_arizona_ramp:18e(25m) / cowos_capacity:8e / geopolitics:1e / hyperscaler_capex:9e(10m) |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 1（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 28.0（3 年第 70 百分位；20 日前第 77）；觀察 |

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
  "as_of": "2026-10-29",
  "premium_pct": 18.42,
  "percentile_1y": 44.0,
  "n": 369
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

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 12,
    "n2_arizona_ramp": 18,
    "cowos_capacity": 8,
    "geopolitics": 1,
    "hyperscaler_capex": 9
  },
  "mentions": {
    "export_controls_tariffs": 13,
    "n2_arizona_ramp": 25,
    "cowos_capacity": 8,
    "geopolitics": 1,
    "hyperscaler_capex": 10
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 12,
      "mentions": 13,
      "gate": "zscore",
      "z": -1.31,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 18,
      "mentions": 25,
      "gate": "zscore",
      "z": 3.26,
      "denial": true
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": 1.79,
      "denial": false
    },
    "geopolitics": {
      "events": 1,
      "mentions": 1,
      "gate": "zscore",
      "z": -1.79,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 9,
      "mentions": 10,
      "gate": "zscore",
      "z": 1.92,
      "denial": false
    }
  }
}
```
- [n2_arizona_ramp] 官方否認偵測 → 上限 🟡（爭議中）
- [export_controls_tariffs] TSMC is seeking chipmaking equipment that doesn't contain Chinese rare-earth magnets — asks suppliers to provide alterna
- [export_controls_tariffs] TSMC Seeks Rare-Earth-Free Factory Equipment as China’s Export Controls Threaten Chip Supply Chains - Tekedia
- [export_controls_tariffs] How Taiwan’s Chip Industry Navigates US Industrial Policy and Export Controls - Global Taiwan Institute
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Intel and Samsung advance 2nm GAA, but yield gaps leave TSMC as the sole external supplier - digitimes
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Beth Kindig – Medium
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - Yahoo Finance
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review

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
  "up_hits": 1,
  "down_hits": 0,
  "total": 1,
  "down_ratio": 0.0
}
```

### M9 valuation — 🟢 GREEN
```json
{
  "as_of": "2026-10-29",
  "per": 27.99,
  "per_pct": 69.5,
  "per_then": 28.69,
  "per_pct_then": 77.2,
  "pbr": 9.74,
  "dividend_yield": 0.91,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**50/50**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 6 / +0.70 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 6 / +0.70 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 5 / +0.71 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 1 / +0.38 | 11 / +0.73 | 24 | 累積中（GREEN n=1 < 30）；方向反 |
| M6 | 6 / +0.70 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-10-29

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1898 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-11-06**（本月已買） · 純定期定額 10,000 元
- 投降窗加碼：無（近 5 個交易日無警報）
- 鋒面 DE_RISK → 調節規則本期 ×1.5 = 15,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-10-30）：本月預算已於 2026-10-27 動用（月末例行），本月不再行動

## 視窗：full（2019-01-02 → 2026-10-29，94 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 94 | 940,000 | 28,606.78 | 32.86 | +0.00% | 3,068,077 | +226.39% | +29.48% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 1,000,000 | 30,033.52 | 33.30 | +1.34% | 3,221,095 | +222.11% | +29.89% |
| 定期定額＋投降窗加碼 | 102 | 1,020,000 | 30,838.81 | 33.08 | +0.67% | 3,307,462 | +224.26% | +29.63% |
| 定期定額＋鋒面調節 | 94 | 1,025,000 | 31,044.08 | 33.02 | +0.49% | 3,329,478 | +224.83% | +29.42% |
| 對照：一次投入 | 1 | 940,000 | 50,801.69 | 18.50 | -43.70% | 5,448,482 | +479.63% | +25.22% |

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

## 視窗：last_12m（2025-10-29 → 2026-10-29，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,427.31 | 84.07 | +0.00% | 153,079 | +27.57% | +57.14% |
| 週檢查・月預算・投降窗即刻投入 | 13 | 150,000 | 1,796.87 | 83.48 | -0.70% | 192,715 | +28.48% | +59.51% |
| 定期定額＋投降窗加碼 | 14 | 140,000 | 1,631.64 | 85.80 | +2.06% | 174,994 | +25.00% | +56.12% |
| 定期定額＋鋒面調節 | 12 | 140,000 | 1,648.60 | 84.92 | +1.01% | 176,813 | +26.29% | +56.16% |
| 對照：一次投入 | 1 | 120,000 | 1,894.11 | 63.35 | -24.65% | 203,144 | +69.29% | +71.30% |

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

# 🎰 賭場 sector — AI 個股影子追蹤（2026-10-29）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 3680.0 | -2.4% | +2.2% | +496.0% | +317.1% | +157.1 |
| 2383 | 台光電 | CCL | ✓ | 5010.0 | -0.8% | +3.8% | +168.9% | +142.7% | +19.7 |
| 2382 | 廣達 | 機櫃 | ✓ | 318.0 | -6.1% | -1.5% | +76.7% | +128.5% | -27.3 |
| 3443 | 創意 | ASIC |  | 7640.0 | -10.4% | -5.8% | +97.8% | +122.4% | -30.3 |
| 3231 | 緯創 | 機櫃 | ✓ | 188.5 | +2.2% | +6.8% | +87.2% | +104.8% | +13.2 |
| 3324 | 雙鴻 | 散熱 |  | 1465.0 | -14.3% | -9.8% | +23.2% | +69.0% | -46.7 |
| 2345 | 智邦 | 網通 | ✓ | 1755.0 | -7.4% | -2.8% | +66.1% | +65.7% | -2.8 |
| 6669 | 緯穎 | 機櫃 | ✓ | 1885.0 | -10.9% | -6.3% | +100.0% | +63.2% | +30.4 |
| 3037 | 欣興 | 載板 | ✓ | 1040.0 | -12.2% | -7.7% | +64.7% | +54.9% | +10.5 |
| 3017 | 奇鋐 | 散熱 | ✓ | 3105.0 | -12.7% | -8.1% | +44.9% | +52.2% | -6.2 |
| 2330 | 台積電 | 製造 | ✓ | 2415.0 | -2.4% | +2.2% | +54.6% | +50.9% | +5.0 |
| 2317 | 鴻海 | 機櫃 | ✓ | 248.0 | -1.0% | +3.6% | +38.4% | +48.2% | -7.9 |
| 3711 | 日月光投控 | 封測 | ✓ | 683.0 | -2.3% | +2.3% | +45.5% | +44.8% | +1.2 |
| 2308 | 台達電 | 電力 | ✓ | 1480.0 | -22.5% | -17.9% | +14.6% | +32.4% | -16.6 |
| 2301 | 光寶科 | 電源 | ✓ | 252.0 | -12.2% | -7.6% | +22.1% | +28.3% | -7.7 |
| 2454 | 聯發科 | IC設計 | ✓ | 4045.0 | -23.5% | -18.9% | +2.0% | +19.4% | -5.1 |

## 借券（只收資料，不是訊號）

> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。

| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |
|---|---|---|---|---|---|---|
| 3661 | 404 | +40.7% | 7 | 0.2 | 0.80%（37 筆） | 17 |
| 2383 | 640 | -4.6% | 30 | 0.2 | 0.01%（54 筆） | 12 |
| 2382 | 69,610 | +15.2% | 13 | 6.0 | 1.00%（118 筆） | 38 |
| 3443 | 974 | -49.9% | 49 | 0.7 | 1.00%（68 筆） | 241 |
| 3231 | 30,136 | -78.0% | 1 | 0.8 | 0.50%（95 筆） | 485 |
| 3324 | 4,433 | +74.1% | 61 | 1.2 | 5.00%（78 筆） | 50 |
| 2345 | 618 | +0.5% | 3 | 0.1 | 0.39%（40 筆） | 5 |
| 6669 | 4,381 | -68.0% | 7 | 0.9 | 12.00%（247 筆） | 234 |
| 3037 | 3,196 | +8.6% | 8 | 0.2 | 0.03%（59 筆） | 266 |
| 3017 | 2,293 | +25.5% | 46 | 0.7 | 0.50%（47 筆） | 9 |
| 2330 | 15,668 | +4.1% | 85 | 0.6 | 0.25%（238 筆） | 16 |
| 2317 | 76,132 | +88.1% | 73 | 1.8 | 0.25%（148 筆） | 469 |
| 3711 | 10,555 | -14.2% | 6 | 0.7 | 0.25%（66 筆） | 174 |
| 2308 | 13,338 | +121.7% | 99 | 1.1 | 0.25%（120 筆） | 285 |
| 2301 | 3,116 | +23.1% | 8 | 0.2 | 0.25%（59 筆） | 32 |
| 2454 | 5,866 | +26.2% | 93 | 0.7 | 0.25%（116 筆） | 23 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 34 個月、投入 170,000 元（16 檔等權）
- 籃子市值 484,703（+185.1%）；0050 市值 341,498（+100.9%）；差 **+84.2 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 前三分之一 n=53 超額 +2.6%；後三分之一 n=53 超額 -2.6%；全部 -0.5%
- 狀態：可讀（n 達門檻）（state 480 筆、已回填 T+20 160 筆）

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

