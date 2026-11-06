# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-11-06 09:52 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-11-06

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-11-06）：本週無警報、預算未動 → 等（2026-11-13 再看）。
- 鋒面 🥶 CAPITULATION（本週由 DE_RISK 轉入）。
- 2308 前提 🔴 RED；無背離（前提 RED、價格 20 日 -48.5%）；PER 33.9，3 年分位 87 → 58
- 2330 前提 🟢 GREEN；🔀 背離：前提健在（GREEN）、價格 20 日 -13.0% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 26.0，3 年分位 85 → 49
- 投降窗加碼歷史 8 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +0.67%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-11-06）：本週無警報、預算未動 → 等（2026-11-13 再看）
- 例行（對照）：**2026-12-06** 買 10,000 元
- 投降窗加碼：無
- 鋒面調節（假說）：CAPITULATION ×2 = 20,000 元

自 2019-01-02 起 94 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 94 | 32.86 | +0.00% | +195.65% | +26.90% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 33.29 | +1.31% | +191.80% | +27.25% |
| 定期定額＋投降窗加碼 | 102 | 33.08 | +0.67% | +193.72% | +27.02% |
| 定期定額＋鋒面調節 | 94 | 33.02 | +0.49% | +194.24% | +26.84% |
| 對照：一次投入 | 1 | 18.5 | -43.70% | +425.04% | +23.58% |

投降窗加碼 8 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 🥶 **CAPITULATION**（score -0.79，2026-11-05）；本週轉移：2026-11-04 DE_RISK→CAPITULATION
- 分位數：外資現貨 0.4、大台Δ 24.6、散戶小台 85.7、融資Δ 2.0
- 本週投降警報：無
- 警報戰績（月更回測）：8 簇，20 日中位 +8.72% vs 基線 +2.20%、命中 75%

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-11-05）：🔴 RED
- 無背離（前提 RED、價格 20 日 -48.5%）；PER 33.9，3 年分位 87 → 58
  - 🔴 M1 revenue_acceleration：2026-09 YoY +14.6%, slope -13.60pp/月, 連續減速 3 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74
  - 🟢 M3 thai_shadow：DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3%
  - 🟡 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1376.6M, YoY +19.9%
  - 🟢 M5 narrative_triggers：capex_cut:4e / vr300_delay:8e(9m) / debt_financed_capex:13e / lc_psu_competition:0e
  - 🔴 M6 peer_divergence：cooling:3324領先+37pp
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 33.9（3 年第 58 百分位；20 日前第 87）；觀察
- 回填樣本 131 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-11-05）：🟢 GREEN
- 🔀 背離：前提健在（GREEN）、價格 20 日 -13.0% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 26.0，3 年分位 85 → 49
  - 🟢 M1 revenue_acceleration：2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9
  - 🟢 M3 adr_premium：ADR 溢價 +16.3%（1 年第 34 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3666.0M, YoY +65.1%
  - 🟢 M5 narrative_triggers：export_controls_tariffs:13e(15m) / n2_arizona_ramp:19e(26m) / cowos_capacity:8e / geopolitics:1e / hyperscaler_capex:6e
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 1（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 26.0（3 年第 49 百分位；20 日前第 85）；觀察
- 回填樣本 25 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | -8.85% | +496.00% | +317.10% | +157.11 |
| 2383 | 台光電 | CCL | -11.86% | +203.10% | +167.30% | +36.61 |
| 2382 | 廣達 | 機櫃 | +6.84% | +76.70% | +128.50% | -27.31 |
| 3443 | 創意 | ASIC | -9.31% | +127.00% | +111.90% | +7.97 |
| 3231 | 緯創 | 機櫃 | +5.13% | +87.20% | +104.80% | +13.21 |
| 3324 | 雙鴻 | 散熱 | -8.31% | +23.20% | +69.00% | -46.74 |
| 2345 | 智邦 | 網通 | -17.28% | +66.10% | +65.70% | -2.78 |
| 6669 | 緯穎 | 機櫃 | -7.05% | +100.00% | +63.20% | +30.38 |
| 3037 | 欣興 | 載板 | -23.41% | +64.70% | +54.90% | +10.49 |
| 3017 | 奇鋐 | 散熱 | -12.24% | +44.90% | +52.20% | -6.24 |
| 2330 | 台積電 | 製造 | +3.20% | +54.60% | +50.90% | +4.98 |
| 2317 | 鴻海 | 機櫃 | +8.73% | +45.70% | +45.40% | -3.12 |
| 3711 | 日月光投控 | 封測 | -6.70% | +45.50% | +44.80% | +1.18 |
| 2308 | 台達電 | 電力 | -27.43% | +14.60% | +32.40% | -16.57 |
| 2301 | 光寶科 | 電源 | -12.82% | +22.10% | +28.30% | -7.73 |
| 2454 | 聯發科 | IC設計 | -16.80% | +2.00% | +19.40% | -5.09 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：34 個月，籃子 +136.79% vs 0050 +81.96%，差 +54.83 pp；判準 可讀
月營收加速三分位 vs T+20 超額：可讀（n 達門檻）（回填 240 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-11-10（4 天後）台股月營收公告截止（2330／2308 通常 10 日前後）
- 2026-12-10（34 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-11-05
- ✅ DCA 帳本：最新 2026-11-05
- ✅ delta_radar：最新 2026-11-06
- ✅ tsmc_radar：最新 2026-11-05
- ✅ 賭場 sector：最新 2026-11-05

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-11-06T09:52:14+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-11-05

## 鋒面：🥶 **CAPITULATION** （昨日由 DE_RISK 轉入）　(score -0.79)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`-1,523,960,544,488`，落在近一年第 **0** 百分位
- 外資大台淨倉 Δ：`-2,004`，落在近一年第 **25** 百分位（水位 -95,651 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+12,263`，落在近一年第 **86** 百分位
- 融資餘額變化：`-20,536,831,000`，落在近一年第 **2** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-11-06 09:52 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 RED、價格 20 日 -48.5%）；PER 33.9，3 年分位 87 → 58

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | capex_cut:4e / vr300_delay:8e(9m) / debt_financed_capex:13e / lc_psu_competition:0e |

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
    "vr300_delay": 9,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 4,
      "mentions": 4,
      "gate": "zscore",
      "z": -1.74,
      "denial": false
    },
    "vr300_delay": {
      "events": 8,
      "mentions": 9,
      "gate": "zscore",
      "z": -1.44,
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
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch. - CNBC
- [debt_financed_capex] AI Investment Returns Under Scrutiny in November 2026: Rising Debt and Big Tech's Cash Flow Concerns - KuCoin
- [debt_financed_capex] Top hyperscalers likely to have more AI-linked debt than now known, S&P Global warns - Reuters

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **3** 筆；state 已有 outcomes 的 entry：**156/156**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 11 / -8.85 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向對 |
| M2 | 26 / -8.93 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 21 / -5.68 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 39 / -7.91 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M5 | 53 / -5.57 | 60 / -9.55 | 47 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 31 / -5.40 | 3 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# TSMC Radar (2330.TW) — 2026-11-05 12:29 UTC

## 總判定：🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（GREEN）、價格 20 日 -13.0% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 26.0，3 年分位 85 → 49

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月 |
| M2 bullwhip_health | 🟢 GREEN | 合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9 |
| M3 adr_premium（觀察） | 🟢 GREEN | ADR 溢價 +16.3%（1 年第 34 百分位；觀察） |
| M4 customs_flow | 🟢 GREEN | US 進口 HS854231 (TH+TW) 近3月 $3666.0M, YoY +65.1% |
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:13e(15m) / n2_arizona_ramp:19e(26m) / cowos_capacity:8e / geopolitics:1e / hyperscaler_capex:6e |
| M6 peer_divergence | 🟢 GREEN | cohort 內 2330 未被對手顯著反超（離散在容忍帶內） |
| M8 revision_velocity | ⚪ NO_DATA | 下修 0/上修 1（樣本不足 <3，NO_DATA） |
| M9 valuation（觀察） | 🟢 GREEN | PER 26.0（3 年第 49 百分位；20 日前第 85）；觀察 |

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
  "as_of": "2026-11-05",
  "premium_pct": 16.32,
  "percentile_1y": 33.9,
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
    "export_controls_tariffs": 13,
    "n2_arizona_ramp": 19,
    "cowos_capacity": 8,
    "geopolitics": 1,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 26,
    "cowos_capacity": 8,
    "geopolitics": 1,
    "hyperscaler_capex": 6
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 13,
      "mentions": 15,
      "gate": "zscore",
      "z": -0.08,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 19,
      "mentions": 26,
      "gate": "zscore",
      "z": 0.85,
      "denial": true
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": 0.72,
      "denial": false
    },
    "geopolitics": {
      "events": 1,
      "mentions": 1,
      "gate": "zscore",
      "z": -0.94,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 6,
      "gate": "zscore",
      "z": 0.1,
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
- [cowos_capacity] [News] While TSMC’s CoWoS Faces Supply Shortage, Samsung Reportedly Secures NVIDIA’s 2.5D Advanced Packaging Order - Tre
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - The Motley Fool
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
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
      "best_peer_3m_yoy": 167.3,
      "peer_lead_pp": 116.4,
      "status": "GREEN",
      "peers_3m_yoy": {
        "3711": 44.8,
        "3037": 54.9,
        "2383": 167.3
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
        "3443": 111.9
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
  "as_of": "2026-11-05",
  "per": 25.96,
  "per_pct": 48.6,
  "per_then": 29.85,
  "per_pct_then": 84.8,
  "pbr": 9.03,
  "dividend_yield": 0.98,
  "history_years": 3,
  "n": 733
}
```

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **8** 筆；state 已有 outcomes 的 entry：**57/57**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 9 / +1.24 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 9 / +1.24 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 8 / +1.32 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 7 / +1.81 | 17 / +1.14 | 28 | 累積中（GREEN n=7 < 30）；方向對 |
| M6 | 9 / +1.24 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-11-05

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1903 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-12-06** · 純定期定額 10,000 元
- 投降窗加碼：無（近 5 個交易日無警報）
- 鋒面 CAPITULATION → 調節規則本期 ×2 = 20,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-11-06）：本週無警報、預算未動 → 等（2026-11-13 再看）

## 視窗：full（2019-01-02 → 2026-11-05，94 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 94 | 940,000 | 28,606.78 | 32.86 | +0.00% | 2,779,149 | +195.65% | +26.90% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 1,000,000 | 30,035.77 | 33.29 | +1.31% | 2,917,975 | +191.80% | +27.25% |
| 定期定額＋投降窗加碼 | 102 | 1,020,000 | 30,838.81 | 33.08 | +0.67% | 2,995,990 | +193.72% | +27.02% |
| 定期定額＋鋒面調節 | 94 | 1,025,000 | 31,044.08 | 33.02 | +0.49% | 3,015,933 | +194.24% | +26.84% |
| 對照：一次投入 | 1 | 940,000 | 50,801.69 | 18.50 | -43.70% | 4,935,384 | +425.04% | +23.58% |

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

## 視窗：last_12m（2025-11-05 → 2026-11-05，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,427.31 | 84.07 | +0.00% | 138,663 | +15.55% | +30.05% |
| 週檢查・月預算・投降窗即刻投入 | 12 | 140,000 | 1,640.60 | 85.33 | +1.50% | 159,384 | +13.85% | +28.83% |
| 定期定額＋投降窗加碼 | 14 | 140,000 | 1,631.64 | 85.80 | +2.06% | 158,514 | +13.22% | +27.46% |
| 定期定額＋鋒面調節 | 12 | 140,000 | 1,648.60 | 84.92 | +1.01% | 160,162 | +14.40% | +28.60% |
| 對照：一次投入 | 1 | 120,000 | 1,894.11 | 63.35 | -24.65% | 184,013 | +53.34% | +53.52% |

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

# 🎰 賭場 sector — AI 個股影子追蹤（2026-11-05）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 2960.0 | -25.1% | -8.8% | +496.0% | +317.1% | +157.1 |
| 2383 | 台光電 | CCL | ✓ | 4100.0 | -28.1% | -11.9% | +203.1% | +167.3% | +36.6 |
| 2382 | 廣達 | 機櫃 | ✓ | 300.0 | -9.4% | +6.8% | +76.7% | +128.5% | -27.3 |
| 3443 | 創意 | ASIC |  | 6405.0 | -25.5% | -9.3% | +127.0% | +111.9% | +8.0 |
| 3231 | 緯創 | 機櫃 | ✓ | 168.5 | -11.1% | +5.1% | +87.2% | +104.8% | +13.2 |
| 3324 | 雙鴻 | 散熱 |  | 1170.0 | -24.5% | -8.3% | +23.2% | +69.0% | -46.7 |
| 2345 | 智邦 | 網通 | ✓ | 1380.0 | -33.5% | -17.3% | +66.1% | +65.7% | -2.8 |
| 6669 | 緯穎 | 機櫃 | ✓ | 1650.0 | -23.3% | -7.0% | +100.0% | +63.2% | +30.4 |
| 3037 | 欣興 | 載板 | ✓ | 800.0 | -39.6% | -23.4% | +64.7% | +54.9% | +10.5 |
| 3017 | 奇鋐 | 散熱 | ✓ | 2565.0 | -28.4% | -12.2% | +44.9% | +52.2% | -6.2 |
| 2330 | 台積電 | 製造 | ✓ | 2240.0 | -13.0% | +3.2% | +54.6% | +50.9% | +5.0 |
| 2317 | 鴻海 | 機櫃 | ✓ | 235.0 | -7.5% | +8.7% | +45.7% | +45.4% | -3.1 |
| 3711 | 日月光投控 | 封測 | ✓ | 572.0 | -22.9% | -6.7% | +45.5% | +44.8% | +1.2 |
| 2308 | 台達電 | 電力 | ✓ | 1130.0 | -43.6% | -27.4% | +14.6% | +32.4% | -16.6 |
| 2301 | 光寶科 | 電源 | ✓ | 211.5 | -29.0% | -12.8% | +22.1% | +28.3% | -7.7 |
| 2454 | 聯發科 | IC設計 | ✓ | 3460.0 | -33.0% | -16.8% | +2.0% | +19.4% | -5.1 |

## 借券（只收資料，不是訊號）

> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。

| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |
|---|---|---|---|---|---|---|
| 3661 | 611 | +78.6% | 16 | 0.2 | 1.00%（61 筆） | 18 |
| 2383 | 756 | +39.7% | 40 | 0.2 | 0.18%（66 筆） | 122 |
| 2382 | 70,043 | +12.4% | 15 | 6.0 | 1.00%（125 筆） | 79 |
| 3443 | 1,507 | -14.7% | 88 | 0.7 | 1.00%（97 筆） | 222 |
| 3231 | 31,956 | -49.4% | 3 | 0.8 | 0.50%（104 筆） | 247 |
| 3324 | 4,222 | +39.5% | 55 | 1.1 | 5.00%（87 筆） | 79 |
| 2345 | 704 | +7.1% | 8 | 0.2 | 0.35%（61 筆） | 7 |
| 6669 | 3,749 | -71.5% | 1 | 0.7 | 6.50%（252 筆） | 231 |
| 3037 | 5,362 | +92.4% | 27 | 0.3 | 0.05%（78 筆） | 1,024 |
| 3017 | 3,242 | +82.8% | 68 | 1.1 | 0.50%（57 筆） | 18 |
| 2330 | 18,412 | +29.6% | 100 | 0.6 | 0.25%（271 筆） | 47 |
| 2317 | 89,651 | +124.7% | 85 | 2.0 | 0.25%（178 筆） | 553 |
| 3711 | 20,727 | +122.4% | 17 | 1.0 | 0.25%（96 筆） | 98 |
| 2308 | 13,466 | +125.8% | 98 | 0.9 | 0.25%（139 筆） | 51 |
| 2301 | 6,020 | +133.4% | 24 | 0.4 | 0.33%（90 筆） | 29 |
| 2454 | 5,826 | +20.7% | 92 | 0.6 | 0.25%（131 筆） | 51 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 34 個月、投入 170,000 元（16 檔等權）
- 籃子市值 402,541（+136.8%）；0050 市值 309,338（+82.0%）；差 **+54.8 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 前三分之一 n=80 超額 +1.7%；後三分之一 n=80 超額 -4.7%；全部 -2.0%
- 狀態：可讀（n 達門檻）（state 560 筆、已回填 T+20 240 筆）

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

