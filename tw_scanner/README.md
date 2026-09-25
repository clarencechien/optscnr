# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-09-25 08:45 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-09-25

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-09-25）：本月預算已於 2026-09-21 動用（月末例行），本月不再行動。
- 鋒面 ⛅ NEUTRAL（本週由 RISK_ON 轉入）。
- 2308 前提 🟡 YELLOW；無背離（前提 YELLOW、價格 20 日 +7.9%）；PER 60.5，3 年分位 79 → 84
- 2330 前提 🟢 GREEN；無背離（前提 GREEN、價格 20 日 +2.7%）；PER 29.0，3 年分位 73 → 79
- 投降窗加碼歷史 8 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +0.71%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-09-25）：本月預算已於 2026-09-21 動用（月末例行），本月不再行動
- 例行（對照）：**2026-10-06** 買 10,000 元（本月已買）
- 投降窗加碼：無
- 鋒面調節（假說）：NEUTRAL ×1 = 10,000 元

自 2019-01-02 起 93 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 93 | 32.61 | +0.00% | +244.71% | +31.31% |
| 週檢查・月預算・投降窗即刻投入 | 93 | 33.07 | +1.41% | +239.92% | +31.76% |
| 定期定額＋投降窗加碼 | 101 | 32.84 | +0.71% | +242.24% | +31.47% |
| 定期定額＋鋒面調節 | 93 | 32.79 | +0.55% | +242.83% | +31.26% |
| 對照：一次投入 | 1 | 18.5 | -43.27% | +507.46% | +26.33% |

投降窗加碼 8 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 ⛅ **NEUTRAL**（score +0.18，2026-09-24）；本週轉移：2026-09-23 RISK_ON→NEUTRAL
- 分位數：外資現貨 67.9、大台Δ 39.3、散戶小台 62.7、融資Δ 91.7
- 本週投降警報：無

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-09-24）：🟡 YELLOW
- 無背離（前提 YELLOW、價格 20 日 +7.9%）；PER 60.5，3 年分位 79 → 84
  - 🟡 M1 revenue_acceleration：2026-08 YoY +34.9%, slope -2.90pp/月, 連續減速 2 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32
  - 🟡 M3 thai_shadow：DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8%
  - 🟢 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1399.9M, YoY +30.6%
  - 🟢 M5 narrative_triggers：capex_cut:5e(6m) / vr300_delay:17e(21m) / debt_financed_capex:13e / lc_psu_competition:0e
  - 🔴 M6 peer_divergence：cooling:3324領先+36pp
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 60.5（3 年第 84 百分位；20 日前第 79）；觀察
- 回填樣本 89 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-09-24）：🟢 GREEN
- 無背離（前提 GREEN、價格 20 日 +2.7%）；PER 29.0，3 年分位 73 → 79
  - 🟢 M1 revenue_acceleration：2026-08 YoY +53.3%, slope +7.74pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9
  - 🟢 M3 adr_premium：ADR 溢價 +14.9%（1 年第 25 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3643.7M, YoY +58.0%
  - 🟡 M5 narrative_triggers：export_controls_tariffs:16e / n2_arizona_ramp:8e(10m) / cowos_capacity:7e / geopolitics:5e / hyperscaler_capex:5e(6m)
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 29.0（3 年第 79 百分位；20 日前第 73）；觀察
- 回填樣本 0 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | -8.57% | +273.60% | +156.90% | +129.11 |
| 2382 | 廣達 | 機櫃 | -4.49% | +177.50% | +137.20% | +37.29 |
| 2383 | 台光電 | CCL | -14.17% | +129.80% | +126.60% | +4.58 |
| 3443 | 創意 | ASIC | +38.01% | +111.00% | +124.40% | +3.65 |
| 3231 | 緯創 | 機櫃 | -3.20% | +166.50% | +93.70% | +56.32 |
| 3324 | 雙鴻 | 散熱 | +55.33% | +67.20% | +82.00% | +2.52 |
| 2345 | 智邦 | 網通 | -15.32% | +59.40% | +64.10% | -0.87 |
| 3017 | 奇鋐 | 散熱 | +0.45% | +54.30% | +59.30% | -5.89 |
| 2330 | 台積電 | 製造 | -3.29% | +53.30% | +55.30% | -7.27 |
| 2317 | 鴻海 | 機櫃 | -6.59% | +52.00% | +52.80% | -0.07 |
| 2308 | 台達電 | 電力 | +1.92% | +34.90% | +46.00% | -10.24 |
| 3037 | 欣興 | 載板 | -5.57% | +56.30% | +45.40% | +9.97 |
| 3711 | 日月光投控 | 封測 | +9.55% | +45.70% | +40.60% | +6.40 |
| 6669 | 緯穎 | 機櫃 | -12.89% | +50.40% | +39.80% | +10.28 |
| 2301 | 光寶科 | 電源 | -10.64% | +25.20% | +33.30% | -5.89 |
| 2454 | 聯發科 | IC設計 | +30.75% | +44.10% | +19.70% | +20.64 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：33 個月，籃子 +222.29% vs 0050 +113.99%，差 +108.30 pp；判準 可讀
月營收加速三分位 vs T+20 超額：累積中（回填 0 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-10-10（15 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-09-24
- ✅ DCA 帳本：最新 2026-09-24
- ✅ delta_radar：最新 2026-09-25
- ✅ tsmc_radar：最新 2026-09-25
- ✅ 賭場 sector：最新 2026-09-24

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-09-25T08:45:38+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-09-24

## 鋒面：⛅ **NEUTRAL** （昨日由 RISK_ON 轉入）　(score +0.18)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`+17,362,951,250`，落在近一年第 **68** 百分位
- 外資大台淨倉 Δ：`-947`，落在近一年第 **39** 百分位（水位 -77,031 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+7,415`，落在近一年第 **63** 百分位
- 融資餘額變化：`+8,735,569,000`，落在近一年第 **92** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-09-25 08:10 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 YELLOW、價格 20 日 +7.9%）；PER 60.5，3 年分位 79 → 84

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | capex_cut:5e(6m) / vr300_delay:17e(21m) / debt_financed_capex:13e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 5,
    "vr300_delay": 17,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 6,
    "vr300_delay": 21,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 5,
      "mentions": 6,
      "gate": "zscore",
      "z": 1.04,
      "denial": false
    },
    "vr300_delay": {
      "events": 17,
      "mentions": 21,
      "gate": "zscore",
      "z": -0.42,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 13,
      "mentions": 13,
      "gate": "zscore",
      "z": -0.71,
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
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 247wallst.com
- [capex_cut] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] AI Companies’ Debt Now Equals 68% of New Long-Term U.S. Treasury Borrowing This Year, JPMorgan Finds - Yahoo Finance
- [debt_financed_capex] Apollo Just Flashed Yellow on Hyperscaler Debt - Money Morning
- [debt_financed_capex] Big Tech's AI Spending Spree Turns to Debt as Bond Sales Top 50% of Capex - finance.biggo.com

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**120/120**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 44 / -7.97 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M2 | 15 / -8.78 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 10 / -1.89 | 1 | 無法判定（狀態翻轉 1 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 29 / -7.27 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 30 / -2.52 | 48 / -9.72 | 42 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 20 / -3.34 | 1 | 樣本不足（缺一側 cohort） |
| M8 | 20 / -3.34 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# TSMC Radar (2330.TW) — 2026-09-25 08:45 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +2.7%）；PER 29.0，3 年分位 73 → 79

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:16e / n2_arizona_ramp:8e(10m) / cowos_capacity:7e / geopolitics:5e / hyperscaler_capex:5e(6m) |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 8,
    "cowos_capacity": 7,
    "geopolitics": 5,
    "hyperscaler_capex": 5
  },
  "mentions": {
    "export_controls_tariffs": 16,
    "n2_arizona_ramp": 10,
    "cowos_capacity": 7,
    "geopolitics": 5,
    "hyperscaler_capex": 6
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 16,
      "mentions": 16,
      "gate": "zscore",
      "z": 0.23,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 8,
      "mentions": 10,
      "gate": "zscore",
      "z": -0.25,
      "denial": false
    },
    "cowos_capacity": {
      "events": 7,
      "mentions": 7,
      "gate": "zscore",
      "z": 0.3,
      "denial": true
    },
    "geopolitics": {
      "events": 5,
      "mentions": 5,
      "gate": "zscore",
      "z": 1.97,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 5,
      "mentions": 6,
      "gate": "zscore",
      "z": 1.26,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - businesskorea.co.kr
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - finance.biggo.com
- [n2_arizona_ramp] Samsung's Texas 2nm Fab Fully Booked; Yields Hit 80%, Closing In on TSMC - finance.biggo.com
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [cowos_capacity] TSMC's CoWoS Shortage Fuels Outsourcing Expansion, But Intel and Taiwan's OSATs Are Chasing Different Opportunities - Xe
- [geopolitics] China's president Xi Jinping calls Taiwan reunification "unstoppable" — military drills around the island escalate in ar
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] China Rings Taiwan With Live-Fire Drills, Tensions Spike - Modern Diplomacy
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [hyperscaler_capex] Market Brief: AI Infrastructure Trade Is Due For A Pause - Seeking Alpha

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **2** 筆；state 已有 outcomes 的 entry：**13/13**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-09-24

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1878 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-10-06**（本月已買） · 純定期定額 10,000 元
- 投降窗加碼：無（近 5 個交易日無警報）
- 鋒面 NEUTRAL → 調節規則本期 ×1 = 10,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-09-25）：本月預算已於 2026-09-21 動用（月末例行），本月不再行動

## 視窗：full（2019-01-02 → 2026-09-24，93 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 93 | 930,000 | 28,521.02 | 32.61 | +0.00% | 3,205,763 | +244.71% | +31.31% |
| 週檢查・月預算・投降窗即刻投入 | 93 | 990,000 | 29,939.75 | 33.07 | +1.41% | 3,365,228 | +239.92% | +31.76% |
| 定期定額＋投降窗加碼 | 101 | 1,010,000 | 30,753.05 | 32.84 | +0.71% | 3,456,642 | +242.24% | +31.47% |
| 定期定額＋鋒面調節 | 93 | 1,015,000 | 30,958.32 | 32.79 | +0.55% | 3,479,715 | +242.83% | +31.26% |
| 對照：一次投入 | 1 | 930,000 | 50,261.25 | 18.50 | -43.27% | 5,649,364 | +507.46% | +26.33% |

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

## 視窗：last_12m（2025-09-24 → 2026-09-24，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,503.48 | 79.81 | +0.00% | 168,991 | +40.83% | +89.95% |
| 週檢查・月預算・投降窗即刻投入 | 13 | 150,000 | 1,893.08 | 79.24 | -0.71% | 212,782 | +41.85% | +93.22% |
| 定期定額＋投降窗加碼 | 14 | 140,000 | 1,707.82 | 81.98 | +2.72% | 191,959 | +37.11% | +91.35% |
| 定期定額＋鋒面調節 | 12 | 140,000 | 1,724.78 | 81.17 | +1.70% | 193,865 | +38.47% | +89.76% |
| 對照：一次投入 | 1 | 120,000 | 1,943.23 | 61.75 | -22.63% | 218,419 | +82.02% | +86.09% |

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

# 🎰 賭場 sector — AI 個股影子追蹤（2026-09-24）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 3770.0 | -2.6% | -8.6% | +273.6% | +156.9% | +129.1 |
| 2382 | 廣達 | 機櫃 | ✓ | 338.5 | +1.5% | -4.5% | +177.5% | +137.2% | +37.3 |
| 2383 | 台光電 | CCL | ✓ | 5050.0 | -8.2% | -14.2% | +129.8% | +126.6% | +4.6 |
| 3443 | 創意 | ASIC |  | 8525.0 | +44.0% | +38.0% | +111.0% | +124.4% | +3.6 |
| 3231 | 緯創 | 機櫃 | ✓ | 184.5 | +2.8% | -3.2% | +166.5% | +93.7% | +56.3 |
| 3324 | 雙鴻 | 散熱 |  | 1710.0 | +61.3% | +55.3% | +67.2% | +82.0% | +2.5 |
| 2345 | 智邦 | 網通 | ✓ | 1895.0 | -9.3% | -15.3% | +59.4% | +64.1% | -0.9 |
| 3017 | 奇鋐 | 散熱 | ✓ | 3555.0 | +6.4% | +0.5% | +54.3% | +59.3% | -5.9 |
| 2330 | 台積電 | 製造 | ✓ | 2475.0 | +2.7% | -3.3% | +53.3% | +55.3% | -7.3 |
| 2317 | 鴻海 | 機櫃 | ✓ | 250.5 | -0.6% | -6.6% | +52.0% | +52.8% | -0.1 |
| 2308 | 台達電 | 電力 | ✓ | 1910.0 | +7.9% | +1.9% | +34.9% | +46.0% | -10.2 |
| 3037 | 欣興 | 載板 | ✓ | 1185.0 | +0.4% | -5.6% | +56.3% | +45.4% | +10.0 |
| 3711 | 日月光投控 | 封測 | ✓ | 699.0 | +15.5% | +9.6% | +45.7% | +40.6% | +6.4 |
| 6669 | 緯穎 | 機櫃 | ✓ | 2115.0 | -6.9% | -12.9% | +50.4% | +39.8% | +10.3 |
| 2301 | 光寶科 | 電源 | ✓ | 287.0 | -4.7% | -10.6% | +25.2% | +33.3% | -5.9 |
| 2454 | 聯發科 | IC設計 | ✓ | 5285.0 | +36.7% | +30.8% | +44.1% | +19.7% | +20.6 |

## 借券（只收資料，不是訊號）

> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。

| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |
|---|---|---|---|---|---|---|
| 3661 | 287 | -52.4% | 0 | 0.1 | 1.75%（93 筆） | 23 |
| 2382 | 60,404 | -31.0% | 1 | 4.1 | 1.50%（167 筆） | 51 |
| 2383 | 671 | +17.7% | 28 | 0.3 | 0.25%（79 筆） | 2 |
| 3443 | 1,943 | +98.4% | 94 | 1.1 | 1.00%（94 筆） | 174 |
| 3231 | 137,184 | -33.0% | 56 | 2.6 | 3.00%（149 筆） | 361 |
| 3324 | 2,546 | -47.6% | 48 | 0.5 | 6.00%（29 筆） | 205 |
| 2345 | 615 | -43.4% | 0 | 0.2 | 0.25%（71 筆） | 8 |
| 3017 | 1,827 | -30.6% | 30 | 0.6 | 0.78%（85 筆） | 65 |
| 2330 | 15,046 | -4.2% | 75 | 0.7 | 0.25%（185 筆） | 16 |
| 2317 | 40,483 | -28.3% | 16 | 1.3 | 0.30%（97 筆） | 409 |
| 2308 | 6,015 | -10.5% | 61 | 0.5 | 0.25%（106 筆） | 127 |
| 3037 | 2,942 | -32.1% | 0 | 0.1 | 0.38%（73 筆） | 769 |
| 3711 | 12,302 | -56.8% | 1 | 0.7 | 0.25%（113 筆） | 296 |
| 6669 | 13,696 | +36.4% | 96 | 2.7 | 16.00%（203 筆） | 1,109 |
| 2301 | 2,532 | -17.0% | 0 | 0.1 | 0.35%（83 筆） | 91 |
| 2454 | 4,648 | +0.0% | 86 | 0.5 | 0.25%（153 筆） | 76 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 33 個月、投入 165,000 元（16 檔等權）
- 籃子市值 531,777（+222.3%）；0050 市值 353,077（+114.0%）；差 **+108.3 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 累積中（state 160 筆、已回填 T+20 0 筆）

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

