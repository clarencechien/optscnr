# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-10-06 10:11 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-10-06

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-10-09）：本月預算已於 2026-10-05 動用（月末例行），本月不再行動。
- 鋒面 ⛅ NEUTRAL（本週未變）。
- 2308 前提 🟡 YELLOW；無背離（前提 YELLOW、價格 20 日 +12.3%）；PER 63.8，3 年分位 79 → 88
- 2330 前提 🟢 GREEN；無背離（前提 GREEN、價格 20 日 +7.3%）；PER 29.9，3 年分位 69 → 85
- 投降窗加碼歷史 8 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +0.71%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-10-09）：本月預算已於 2026-10-05 動用（月末例行），本月不再行動
- 例行（對照）：**2026-11-06** 買 10,000 元
- 投降窗加碼：無
- 鋒面調節（假說）：NEUTRAL ×1 = 10,000 元

自 2019-01-02 起 93 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 93 | 32.61 | +0.00% | +255.59% | +31.89% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 33.3 | +2.12% | +248.15% | +32.35% |
| 定期定額＋投降窗加碼 | 101 | 32.84 | +0.71% | +253.05% | +32.06% |
| 定期定額＋鋒面調節 | 93 | 32.79 | +0.55% | +253.66% | +31.84% |
| 對照：一次投入 | 1 | 18.5 | -43.27% | +526.64% | +26.73% |

投降窗加碼 8 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 ⛅ **NEUTRAL**（score +0.44，2026-10-05）；本週未變
- 分位數：外資現貨 82.1、大台Δ 90.1、散戶小台 4.4、融資Δ 20.2
- 本週投降警報：無
- 警報戰績（月更回測）：8 簇，20 日中位 +8.72% vs 基線 +2.19%、命中 75%

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-10-05）：🟡 YELLOW
- 無背離（前提 YELLOW、價格 20 日 +12.3%）；PER 63.8，3 年分位 79 → 88
  - 🟡 M1 revenue_acceleration：2026-08 YoY +34.9%, slope -2.90pp/月, 連續減速 2 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +17.3% / 存貨 QoQ +17.0% / FCF/淨利 1.32
  - 🟡 M3 thai_shadow：DELTA.BK 2026-06-30 營收 YoY +52.5%, GM 26.8%
  - 🟢 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1399.9M, YoY +30.6%
  - 🟢 M5 narrative_triggers：capex_cut:5e / vr300_delay:17e(21m) / debt_financed_capex:14e(15m) / lc_psu_competition:0e
  - 🔴 M6 peer_divergence：cooling:3324領先+36pp
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 63.8（3 年第 88 百分位；20 日前第 79）；觀察
- 回填樣本 97 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-10-05）：🟢 GREEN
- 無背離（前提 GREEN、價格 20 日 +7.3%）；PER 29.9，3 年分位 69 → 85
  - 🟢 M1 revenue_acceleration：2026-08 YoY +53.3%, slope +7.74pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9
  - 🟢 M3 adr_premium：ADR 溢價 +16.6%（1 年第 33 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3643.7M, YoY +58.0%
  - 🟢 M5 narrative_triggers：export_controls_tariffs:14e / n2_arizona_ramp:9e(11m) / cowos_capacity:8e / geopolitics:3e / hyperscaler_capex:5e
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：revision feed failed: HTTP Error 503: Service Unavailable
  - 🟢 M9 valuation：PER 29.9（3 年第 85 百分位；20 日前第 69）；觀察
- 回填樣本 0 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | -11.65% | +273.60% | +156.90% | +129.11 |
| 2383 | 台光電 | CCL | -1.43% | +168.90% | +142.70% | +19.74 |
| 2382 | 廣達 | 機櫃 | -10.37% | +177.50% | +137.20% | +37.29 |
| 3443 | 創意 | ASIC | +39.10% | +97.80% | +122.40% | -30.30 |
| 3231 | 緯創 | 機櫃 | -8.65% | +166.50% | +93.70% | +56.32 |
| 3324 | 雙鴻 | 散熱 | +5.63% | +67.20% | +82.00% | +2.52 |
| 2345 | 智邦 | 網通 | -9.90% | +59.40% | +64.10% | -0.87 |
| 3017 | 奇鋐 | 散熱 | -0.54% | +54.30% | +59.30% | -5.89 |
| 2330 | 台積電 | 製造 | -1.44% | +53.30% | +55.30% | -7.27 |
| 2317 | 鴻海 | 機櫃 | -6.55% | +38.40% | +48.20% | -7.89 |
| 2308 | 台達電 | 電力 | +4.74% | +34.90% | +46.00% | -10.24 |
| 3037 | 欣興 | 載板 | +34.37% | +56.30% | +45.40% | +9.97 |
| 3711 | 日月光投控 | 封測 | +16.80% | +45.70% | +40.60% | +6.40 |
| 6669 | 緯穎 | 機櫃 | -22.31% | +50.40% | +39.80% | +10.28 |
| 2301 | 光寶科 | 電源 | -9.51% | +25.20% | +33.30% | -5.89 |
| 2454 | 聯發科 | IC設計 | +9.83% | +44.10% | +19.70% | +20.64 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：33 個月，籃子 +237.24% vs 0050 +120.74%，差 +116.50 pp；判準 可讀
月營收加速三分位 vs T+20 超額：累積中（回填 0 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-10-10（4 天後）台股月營收公告截止（2330／2308 通常 10 日前後）
- 2026-11-10（35 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-10-05
- ✅ DCA 帳本：最新 2026-10-05
- ✅ delta_radar：最新 2026-10-06
- ✅ tsmc_radar：最新 2026-10-06
- ✅ 賭場 sector：最新 2026-10-05

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-10-06T10:11:07+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-10-05

## 鋒面：⛅ **NEUTRAL** 　(score +0.44)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`+167,523,804,118`，落在近一年第 **82** 百分位
- 外資大台淨倉 Δ：`+3,300`，落在近一年第 **90** 百分位（水位 -77,004 口僅供參考，不參與判讀）
- 散戶小台淨倉：`-2,690`，落在近一年第 **4** 百分位
- 融資餘額變化：`-1,752,701,000`，落在近一年第 **20** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-10-06 09:24 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 YELLOW、價格 20 日 +12.3%）；PER 63.8，3 年分位 79 → 88

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | capex_cut:5e / vr300_delay:17e(21m) / debt_financed_capex:14e(15m) / lc_psu_competition:0e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 5,
    "vr300_delay": 17,
    "debt_financed_capex": 14,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 5,
    "vr300_delay": 21,
    "debt_financed_capex": 15,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 5,
      "mentions": 5,
      "gate": "zscore",
      "z": 0.2,
      "denial": false
    },
    "vr300_delay": {
      "events": 17,
      "mentions": 21,
      "gate": "zscore",
      "z": 0.72,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 14,
      "mentions": 15,
      "gate": "zscore",
      "z": 1.37,
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
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] Tom Lee vs. AI Debt Trap: What Happens When 10-Year Bonds Fund 2-Year Microchips? - TradingView
- [debt_financed_capex] Oracle’s Negative Free Cash Flow Exposes the Uncomfortable Truth About AI’s Financing Game - AOL.com
- [debt_financed_capex] AI Companies’ Debt Now Equals 68% of New Long-Term U.S. Treasury Borrowing This Year, JPMorgan Finds - Yahoo Finance

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **8** 筆；state 已有 outcomes 的 entry：**131/131**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 46 / -7.58 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M2 | 17 / -7.63 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向對 |
| M3 | 27 / -10.89 | 12 / -1.41 | 1 | 無法判定（狀態翻轉 1 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 30 / -6.87 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 35 / -2.15 | 50 / -9.29 | 44 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 22 / -2.95 | 1 | 樣本不足（缺一側 cohort） |
| M8 | 22 / -2.95 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# TSMC Radar (2330.TW) — 2026-10-06 10:11 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 +7.3%）；PER 29.9，3 年分位 69 → 85

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | export_controls_tariffs:14e / n2_arizona_ramp:9e(11m) / cowos_capacity:8e / geopolitics:3e / hyperscaler_capex:5e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "export_controls_tariffs": 14,
    "n2_arizona_ramp": 9,
    "cowos_capacity": 8,
    "geopolitics": 3,
    "hyperscaler_capex": 5
  },
  "mentions": {
    "export_controls_tariffs": 14,
    "n2_arizona_ramp": 11,
    "cowos_capacity": 8,
    "geopolitics": 3,
    "hyperscaler_capex": 5
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 14,
      "mentions": 14,
      "gate": "zscore",
      "z": -0.97,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 9,
      "mentions": 11,
      "gate": "zscore",
      "z": -1.37,
      "denial": false
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": -0.77,
      "denial": true
    },
    "geopolitics": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -1.9,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 5,
      "mentions": 5,
      "gate": "zscore",
      "z": 0.32,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] Huawei chairman thanks the US for export restrictions on chips, says it supercharged China’s semiconductor industry — Wa
- [export_controls_tariffs] Key facts: TSMC to Invest Up to $265B in Arizona; Reviews Export Controls - TradingView
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC,... - Yahoo F
- [n2_arizona_ramp] Samsung's 2nm Yield Approaches 60%, Leveraging Tesla Orders to Challenge TSMC - finance.biggo.com
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [n2_arizona_ramp] Tech News:Samsung 2nm Chip Yield Surpasses 60%, Closing in on TSMC - LinkedIn
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [geopolitics] 'Strong punishment': China conducts biggest ‘blockade’ drills around Taiwan - The Times of India
- [geopolitics] Taiwan Pledges to Keep Advanced Chips From Chinese Military - Bloomberg.com
- [geopolitics] China’s planned military exercises near Taiwan may have another target: Japan - The Japan Times
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [hyperscaler_capex] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 247wallst.com
- [hyperscaler_capex] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 247wallst.com

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **8** 筆；state 已有 outcomes 的 entry：**26/26**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-10-05

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1883 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-11-06** · 純定期定額 10,000 元
- 投降窗加碼：無（近 5 個交易日無警報）
- 鋒面 NEUTRAL → 調節規則本期 ×1 = 10,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-10-09）：本月預算已於 2026-10-05 動用（月末例行），本月不再行動

## 視窗：full（2019-01-02 → 2026-10-05，93 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 93 | 930,000 | 28,521.02 | 32.61 | +0.00% | 3,307,012 | +255.59% | +31.89% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 1,000,000 | 30,025.97 | 33.30 | +2.12% | 3,481,511 | +248.15% | +32.35% |
| 定期定額＋投降窗加碼 | 101 | 1,010,000 | 30,753.05 | 32.84 | +0.71% | 3,565,816 | +253.05% | +32.06% |
| 定期定額＋鋒面調節 | 93 | 1,015,000 | 30,958.32 | 32.79 | +0.55% | 3,589,617 | +253.66% | +31.84% |
| 對照：一次投入 | 1 | 930,000 | 50,261.25 | 18.50 | -43.27% | 5,827,792 | +526.64% | +26.73% |

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

## 視窗：last_12m（2025-10-07 → 2026-10-05，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,503.48 | 79.81 | +0.00% | 174,328 | +45.27% | +93.77% |
| 週檢查・月預算・投降窗即刻投入 | 13 | 150,000 | 1,805.40 | 83.08 | +4.10% | 209,336 | +39.56% | +96.17% |
| 定期定額＋投降窗加碼 | 14 | 140,000 | 1,707.82 | 81.98 | +2.72% | 198,021 | +41.44% | +95.44% |
| 定期定額＋鋒面調節 | 12 | 140,000 | 1,724.78 | 81.17 | +1.70% | 199,988 | +42.85% | +93.74% |
| 對照：一次投入 | 1 | 120,000 | 1,943.23 | 61.75 | -22.63% | 225,318 | +87.76% | +88.42% |

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

# 🎰 賭場 sector — AI 個股影子追蹤（2026-10-05）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 3950.0 | -2.5% | -11.7% | +273.6% | +156.9% | +129.1 |
| 2383 | 台光電 | CCL | ✓ | 5700.0 | +7.8% | -1.4% | +168.9% | +142.7% | +19.7 |
| 2382 | 廣達 | 機櫃 | ✓ | 331.0 | -1.2% | -10.4% | +177.5% | +137.2% | +37.3 |
| 3443 | 創意 | ASIC |  | 8600.0 | +48.3% | +39.1% | +97.8% | +122.4% | -30.3 |
| 3231 | 緯創 | 機櫃 | ✓ | 189.5 | +0.5% | -8.7% | +166.5% | +93.7% | +56.3 |
| 3324 | 雙鴻 | 散熱 |  | 1550.0 | +14.8% | +5.6% | +67.2% | +82.0% | +2.5 |
| 2345 | 智邦 | 網通 | ✓ | 2075.0 | -0.7% | -9.9% | +59.4% | +64.1% | -0.9 |
| 3017 | 奇鋐 | 散熱 | ✓ | 3585.0 | +8.6% | -0.5% | +54.3% | +59.3% | -5.9 |
| 2330 | 台積電 | 製造 | ✓ | 2575.0 | +7.7% | -1.4% | +53.3% | +55.3% | -7.3 |
| 2317 | 鴻海 | 機櫃 | ✓ | 254.0 | +2.6% | -6.5% | +38.4% | +48.2% | -7.9 |
| 2308 | 台達電 | 電力 | ✓ | 2005.0 | +13.9% | +4.7% | +34.9% | +46.0% | -10.2 |
| 3037 | 欣興 | 載板 | ✓ | 1325.0 | +43.5% | +34.4% | +56.3% | +45.4% | +10.0 |
| 3711 | 日月光投控 | 封測 | ✓ | 742.0 | +26.0% | +16.8% | +45.7% | +40.6% | +6.4 |
| 6669 | 緯穎 | 機櫃 | ✓ | 2150.0 | -13.1% | -22.3% | +50.4% | +39.8% | +10.3 |
| 2301 | 光寶科 | 電源 | ✓ | 298.0 | -0.3% | -9.5% | +25.2% | +33.3% | -5.9 |
| 2454 | 聯發科 | IC設計 | ✓ | 5165.0 | +19.0% | +9.8% | +44.1% | +19.7% | +20.6 |

## 借券（只收資料，不是訊號）

> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。

| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |
|---|---|---|---|---|---|---|
| 3661 | 342 | +5.3% | 4 | 0.1 | 1.75%（87 筆） | 24 |
| 2383 | 541 | +3.6% | 11 | 0.3 | 0.25%（53 筆） | 20 |
| 2382 | 62,321 | -15.3% | 4 | 4.2 | 1.50%（138 筆） | 37 |
| 3443 | 1,767 | +48.4% | 90 | 1.1 | 1.00%（64 筆） | 163 |
| 3231 | 63,174 | -71.3% | 7 | 1.3 | 3.00%（119 筆） | 389 |
| 3324 | 3,027 | -5.7% | 56 | 0.8 | 5.00%（31 筆） | 81 |
| 2345 | 658 | -43.4% | 2 | 0.2 | 0.25%（49 筆） | 19 |
| 3017 | 1,773 | -27.3% | 29 | 0.6 | 0.75%（68 筆） | 47 |
| 2330 | 14,202 | -11.4% | 74 | 0.6 | 0.25%（197 筆） | 46 |
| 2317 | 39,903 | -25.5% | 14 | 1.2 | 0.30%（81 筆） | 428 |
| 2308 | 5,963 | -13.9% | 62 | 0.5 | 0.25%（98 筆） | 136 |
| 3037 | 2,787 | -37.3% | 0 | 0.2 | 0.38%（49 筆） | 616 |
| 3711 | 9,320 | -63.3% | 0 | 0.6 | 0.25%（91 筆） | 291 |
| 6669 | 13,165 | +14.5% | 95 | 3.5 | 16.00%（158 筆） | 1,084 |
| 2301 | 2,580 | -30.3% | 1 | 0.1 | 0.25%（58 筆） | 106 |
| 2454 | 4,828 | -8.1% | 88 | 0.6 | 0.25%（138 筆） | 58 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 33 個月、投入 165,000 元（16 檔等權）
- 籃子市值 556,452（+237.2%）；0050 市值 364,228（+120.7%）；差 **+116.5 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 累積中（state 240 筆、已回填 T+20 0 筆）

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

