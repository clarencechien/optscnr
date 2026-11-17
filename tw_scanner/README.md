# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-11-17 21:56 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-11-17

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-11-20）：本月預算已於 2026-11-09 動用（投降窗 ×2.0），本月不再行動。
- 鋒面 ⛅ NEUTRAL（本週由 CAPITULATION 轉入）。
- 2308 前提 🟡 YELLOW；🔀 背離：前提健在（YELLOW）、價格 20 日 -35.5% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 33.6，3 年分位 71 → 56
- 2330 前提 🟢 GREEN；🔀 背離：前提健在（GREEN）、價格 20 日 -10.3% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 22.5，3 年分位 72 → 27
- 投降窗加碼歷史 9 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +1.27%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-11-20）：本月預算已於 2026-11-09 動用（投降窗 ×2.0），本月不再行動
- 例行（對照）：**2026-12-06** 買 10,000 元（本月已買）
- 投降窗加碼：**待執行** 10,000 元
- 鋒面調節（假說）：NEUTRAL ×1 = 10,000 元

自 2019-01-02 起 95 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 95 | 33.08 | +0.00% | +184.13% | +25.89% |
| 週檢查・月預算・投降窗即刻投入 | 95 | 33.73 | +1.96% | +178.69% | +26.21% |
| 定期定額＋投降窗加碼 | 104 | 33.5 | +1.27% | +180.64% | +26.01% |
| 定期定額＋鋒面調節 | 95 | 33.43 | +1.06% | +181.19% | +25.83% |
| 對照：一次投入 | 1 | 18.5 | -44.07% | +408.02% | +22.95% |

投降窗加碼 9 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 ⛅ **NEUTRAL**（score -0.37，2026-11-17）；本週轉移：2026-11-12 CAPITULATION→NEUTRAL
- 分位數：外資現貨 4.4、大台Δ 40.1、散戶小台 23.0、融資Δ 4.4
- 本週投降警報：2026-11-17
- 警報戰績（月更回測）：8 簇，20 日中位 +8.72% vs 基線 +2.20%、命中 75%

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-11-16）：🟡 YELLOW
- 🔀 背離：前提健在（YELLOW）、價格 20 日 -35.5% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 33.6，3 年分位 71 → 56
  - 🟢 M1 revenue_acceleration：2026-10 YoY +30.1%, slope -5.88pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74
  - 🟢 M3 thai_shadow：DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3%
  - 🟡 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1376.6M, YoY +19.9%
  - 🟡 M5 narrative_triggers：capex_cut:3e / vr300_delay:10e(11m) / debt_financed_capex:10e / lc_psu_competition:0e
  - 🟡 M6 peer_divergence：cooling:3324領先+18pp
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 33.6（3 年第 56 百分位；20 日前第 71）；觀察
- 回填樣本 144 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-11-16）：🟢 GREEN
- 🔀 背離：前提健在（GREEN）、價格 20 日 -10.3% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 22.5，3 年分位 72 → 27
  - 🟢 M1 revenue_acceleration：2026-10 YoY +59.7%, slope +5.01pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +11.0% / FCF/淨利 1.46
  - 🟢 M3 adr_premium：ADR 溢價 +18.6%（1 年第 47 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3666.0M, YoY +65.1%
  - 🔴 M5 narrative_triggers：export_controls_tariffs:15e(17m) / n2_arizona_ramp:21e(28m) / cowos_capacity:8e / geopolitics:3e / hyperscaler_capex:3e
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 22.5（3 年第 27 百分位；20 日前第 72）；觀察
- 回填樣本 38 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | +11.32% | +515.80% | +428.50% | +121.10 |
| 2383 | 台光電 | CCL | -17.70% | +203.10% | +167.30% | +36.61 |
| 3231 | 緯創 | 機櫃 | -0.21% | +117.60% | +123.70% | -24.46 |
| 2382 | 廣達 | 機櫃 | -4.72% | +104.00% | +119.40% | -36.75 |
| 3443 | 創意 | ASIC | +7.01% | +127.00% | +111.90% | +7.97 |
| 6669 | 緯穎 | 機櫃 | -7.65% | +80.90% | +77.10% | +15.29 |
| 2345 | 智邦 | 網通 | -19.07% | +91.20% | +72.20% | +15.87 |
| 3037 | 欣興 | 載板 | -27.80% | +67.60% | +62.80% | +5.68 |
| 2330 | 台積電 | 製造 | +3.43% | +59.70% | +55.90% | +3.19 |
| 3711 | 日月光投控 | 封測 | -8.74% | +47.10% | +46.10% | +0.73 |
| 2317 | 鴻海 | 機櫃 | +3.51% | +45.70% | +45.40% | -3.12 |
| 3324 | 雙鴻 | 散熱 | -21.19% | +44.70% | +45.10% | -11.21 |
| 3017 | 奇鋐 | 散熱 | -11.73% | +34.40% | +44.50% | -9.99 |
| 2308 | 台達電 | 電力 | -21.71% | +30.10% | +26.60% | -2.42 |
| 2301 | 光寶科 | 電源 | -7.98% | +32.00% | +26.50% | +3.40 |
| 2454 | 聯發科 | IC設計 | +4.11% | +5.80% | +17.30% | -19.16 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：35 個月，籃子 +118.58% vs 0050 +73.93%，差 +44.65 pp；判準 可讀
月營收加速三分位 vs T+20 超額：可讀（n 達門檻）（回填 368 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-12-10（23 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-11-17
- ✅ DCA 帳本：最新 2026-11-17
- ✅ delta_radar：最新 2026-11-17
- ✅ tsmc_radar：最新 2026-11-17
- ✅ 賭場 sector：最新 2026-11-17

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-11-17T21:56:16+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-11-17

## 鋒面：⛅ **NEUTRAL** 　(score -0.37)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`-1,138,436,802,803`，落在近一年第 **4** 百分位
- 外資大台淨倉 Δ：`-1,109`，落在近一年第 **40** 百分位（水位 -97,896 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+3,029`，落在近一年第 **23** 百分位
- 融資餘額變化：`-15,776,760,000`，落在近一年第 **4** 百分位

## 🚨 🥶 投降警報 — 歷史上此類尾部共現日為 DCA 加速窗口（見回測）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-11-17 11:07 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 🔀 前提 vs 價格：🔀 背離：前提健在（YELLOW）、價格 20 日 -35.5% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 33.6，3 年分位 71 → 56

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:3e / vr300_delay:10e(11m) / debt_financed_capex:10e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "capex_cut": 3,
    "vr300_delay": 10,
    "debt_financed_capex": 10,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 3,
    "vr300_delay": 11,
    "debt_financed_capex": 10,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -1.37,
      "denial": false
    },
    "vr300_delay": {
      "events": 10,
      "mentions": 11,
      "gate": "zscore",
      "z": 2.47,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 10,
      "mentions": 10,
      "gate": "zscore",
      "z": -0.46,
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
- [debt_financed_capex] Will Oracle's Debt-Funded Data Center Buildout Weigh on the Stock Now? - TradingView
- [debt_financed_capex] AI Debt Risks Mount: Why Borrowing by Meta, Alphabet, Microsoft and Oracle Worries Investors - TradingKey
- [debt_financed_capex] AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch. - CNBC

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **5** 筆；state 已有 outcomes 的 entry：**168/168**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 17 / -13.30 | 3 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M2 | 29 / -10.19 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M3 | 27 / -10.89 | 24 / -7.62 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 42 / -8.86 | 0 / — | 1 | 樣本不足（缺一側 cohort） |
| M5 | 58 / -6.90 | 65 / -10.55 | 50 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 34 / -6.79 | 5 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# TSMC Radar (2330.TW) — 2026-11-17 11:44 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟡 YELLOW

## 🔀 前提 vs 價格：🔀 背離：前提健在（GREEN）、價格 20 日 -10.3% —— 跌的是估值不是基本面（或市場知道儀器不知道的事）；PER 22.5，3 年分位 72 → 27

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🔴 RED | export_controls_tariffs:15e(17m) / n2_arizona_ramp:21e(28m) / cowos_capacity:8e / geopolitics:3e / hyperscaler_capex:3e |

### M5 narrative_triggers — 🔴 RED
```json
{
  "events": {
    "export_controls_tariffs": 15,
    "n2_arizona_ramp": 21,
    "cowos_capacity": 8,
    "geopolitics": 3,
    "hyperscaler_capex": 3
  },
  "mentions": {
    "export_controls_tariffs": 17,
    "n2_arizona_ramp": 28,
    "cowos_capacity": 8,
    "geopolitics": 3,
    "hyperscaler_capex": 3
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 15,
      "mentions": 17,
      "gate": "zscore",
      "z": 2.21,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 21,
      "mentions": 28,
      "gate": "zscore",
      "z": -0.66,
      "denial": true
    },
    "cowos_capacity": {
      "events": 8,
      "mentions": 8,
      "gate": "zscore",
      "z": 0.0,
      "denial": false
    },
    "geopolitics": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": 2.66,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 3,
      "mentions": 3,
      "gate": "zscore",
      "z": -1.15,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] TSMC is seeking chipmaking equipment that doesn't contain Chinese rare-earth magnets — asks suppliers to provide alterna
- [export_controls_tariffs] TSMC Seeks Rare-Earth-Free Factory Equipment as China’s Export Controls Threaten Chip Supply Chains - Tekedia
- [export_controls_tariffs] How Taiwan’s Chip Industry Navigates US Industrial Policy and Export Controls - Global Taiwan Institute
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] TSMC Accelerates CoPoS Packaging to Replace CoWoS, as Glass Core Substrates Cut Costs 30% and Boost Wafer Utilization Pa
- [cowos_capacity] [News] While TSMC’s CoWoS Faces Supply Shortage, Samsung Reportedly Secures NVIDIA’s 2.5D Advanced Packaging Order - Tre
- [geopolitics] China’s Coast Guard Rehearses Blockade Tools as Taiwan Plans Counter-Drills - Tech Times
- [geopolitics] Could China Blockade Taiwan? Naval Drills Raise Fears of a Wider Indo-Pacific Crisis - Modern Diplomacy
- [geopolitics] China stages record drills designed to encircle Taiwan - Reuters
- [hyperscaler_capex] Tesla Isn’t a Hyperscaler. Why the AI Bears Are Misreading Its $5 Billion Capex Cut. - The Motley Fool
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Will the next recession be caused by an AI capex cut-off? - InvestorDaily

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **10** 筆；state 已有 outcomes 的 entry：**71/71**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 15 / +2.26 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 12 / +1.72 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 11 / +1.82 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 13 / +2.72 | 21 / +1.54 | 37 | 累積中（GREEN n=13 < 30）；方向對 |
| M6 | 12 / +1.72 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-11-17

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1911 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-12-06**（本月已買） · 純定期定額 10,000 元
- 投降窗加碼：**待執行** 10000.0 元（警報日 2026-11-17）
- 鋒面 NEUTRAL → 調節規則本期 ×1 = 10,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-11-20）：本月預算已於 2026-11-09 動用（投降窗 ×2.0），本月不再行動

## 視窗：full（2019-01-02 → 2026-11-17，95 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 95 | 950,000 | 28,714.80 | 33.08 | +0.00% | 2,699,191 | +184.13% | +25.89% |
| 週檢查・月預算・投降窗即刻投入 | 95 | 1,020,000 | 30,240.83 | 33.73 | +1.96% | 2,842,638 | +178.69% | +26.21% |
| 定期定額＋投降窗加碼 | 104 | 1,040,000 | 31,049.36 | 33.50 | +1.27% | 2,918,639 | +180.64% | +26.01% |
| 定期定額＋鋒面調節 | 95 | 1,045,000 | 31,260.12 | 33.43 | +1.06% | 2,938,451 | +181.19% | +25.83% |
| 對照：一次投入 | 1 | 950,000 | 51,342.14 | 18.50 | -44.07% | 4,826,161 | +408.02% | +22.95% |

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

加碼 edge 平均 +1.17%、勝率 75%（n=8）。正 = 警報日買比等到例行日買便宜。

## 視窗：last_12m（2025-11-17 → 2026-11-17，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,377.48 | 87.12 | +0.00% | 129,483 | +7.90% | +16.60% |
| 週檢查・月預算・投降窗即刻投入 | 13 | 160,000 | 1,865.78 | 85.75 | -1.57% | 175,383 | +9.61% | +21.35% |
| 定期定額＋投降窗加碼 | 15 | 150,000 | 1,684.35 | 89.06 | +2.23% | 158,329 | +5.55% | +13.09% |
| 定期定額＋鋒面調節 | 12 | 150,000 | 1,706.79 | 87.88 | +0.87% | 160,439 | +6.96% | +15.67% |
| 對照：一次投入 | 1 | 120,000 | 1,882.22 | 63.75 | -26.83% | 176,929 | +47.44% | +50.98% |

加碼逐筆（跟「同一筆錢等到下一個例行買日」比；T+60 交易日）：

| 警報日 | 執行日 | 執行價 | 下一例行買日 | 例行價 | edge | T+60 |
|---|---|---|---|---|---|---|
| 2026-07-20 | 2026-07-21 | 102.5 | 2026-08-06 | 103.30 | +0.78% | +6.34% |
| 2026-07-29 | 2026-07-30 | 93.5 | 2026-08-06 | 103.30 | +10.48% | +14.71% |
| 2026-11-06 | 2026-11-09 | 97.45 | — | — | — | — |

加碼 edge 平均 +5.63%、勝率 100%（n=2）。正 = 警報日買比等到例行日買便宜。

分割還原：2025-06-18 ×4（override）。

---
*dca_ledger — 規則影子帳本，等額假設。lump_sum 是對照不是策略（沒人一開始就有全部的錢）；regime_scaled 是待資料處決的假說。非投資建議。*

---

# 🎰 賭場 sector — AI 個股影子追蹤（2026-11-17）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 3595.0 | -2.4% | +11.3% | +515.8% | +428.5% | +121.1 |
| 2383 | 台光電 | CCL | ✓ | 3540.0 | -31.5% | -17.7% | +203.1% | +167.3% | +36.6 |
| 3231 | 緯創 | 機櫃 | ✓ | 157.0 | -14.0% | -0.2% | +117.6% | +123.7% | -24.5 |
| 2382 | 廣達 | 機櫃 | ✓ | 262.5 | -18.5% | -4.7% | +104.0% | +119.4% | -36.8 |
| 3443 | 創意 | ASIC |  | 6975.0 | -6.8% | +7.0% | +127.0% | +111.9% | +8.0 |
| 6669 | 緯穎 | 機櫃 | ✓ | 1450.0 | -21.4% | -7.7% | +80.9% | +77.1% | +15.3 |
| 2345 | 智邦 | 網通 | ✓ | 1330.0 | -32.8% | -19.1% | +91.2% | +72.2% | +15.9 |
| 3037 | 欣興 | 載板 | ✓ | 637.0 | -41.6% | -27.8% | +67.6% | +62.8% | +5.7 |
| 2330 | 台積電 | 製造 | ✓ | 2170.0 | -10.3% | +3.4% | +59.7% | +55.9% | +3.2 |
| 3711 | 日月光投控 | 封測 | ✓ | 520.0 | -22.5% | -8.7% | +47.1% | +46.1% | +0.7 |
| 2317 | 鴻海 | 機櫃 | ✓ | 219.0 | -10.2% | +3.5% | +45.7% | +45.4% | -3.1 |
| 3324 | 雙鴻 | 散熱 |  | 927.0 | -35.0% | -21.2% | +44.7% | +45.1% | -11.2 |
| 3017 | 奇鋐 | 散熱 | ✓ | 2470.0 | -25.5% | -11.7% | +34.4% | +44.5% | -10.0 |
| 2308 | 台達電 | 電力 | ✓ | 1055.0 | -35.5% | -21.7% | +30.1% | +26.6% | -2.4 |
| 2301 | 光寶科 | 電源 | ✓ | 207.0 | -21.7% | -8.0% | +32.0% | +26.5% | +3.4 |
| 2454 | 聯發科 | IC設計 | ✓ | 3840.0 | -9.7% | +4.1% | +5.8% | +17.3% | -19.2 |

## 借券（只收資料，不是訊號）

> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。

| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |
|---|---|---|---|---|---|---|
| 3661 | 1,050 | +157.0% | 23 | 0.4 | 1.00%（81 筆） | 50 |
| 2383 | 707 | -9.8% | 38 | 0.2 | 0.25%（79 筆） | 27 |
| 3231 | 29,918 | -18.7% | 2 | 0.8 | 0.50%（84 筆） | 471 |
| 2382 | 74,884 | +15.8% | 20 | 4.9 | 0.75%（125 筆） | 56 |
| 3443 | 1,875 | +32.1% | 97 | 0.7 | 0.75%（109 筆） | 143 |
| 6669 | 3,419 | -71.8% | 1 | 0.7 | 3.50%（224 筆） | 260 |
| 2345 | 1,098 | +47.4% | 26 | 0.2 | 0.25%（77 筆） | 11 |
| 3037 | 5,111 | +12.3% | 28 | 0.2 | 0.30%（72 筆） | 3,455 |
| 2330 | 24,116 | +86.8% | 100 | 0.6 | 0.22%（273 筆） | 36 |
| 3711 | 25,441 | +175.0% | 35 | 1.0 | 0.25%（120 筆） | 284 |
| 2317 | 102,005 | +23.8% | 86 | 2.2 | 0.25%（181 筆） | 431 |
| 3324 | 3,570 | -16.2% | 47 | 0.7 | 5.00%（70 筆） | 43 |
| 3017 | 3,136 | +79.1% | 66 | 1.0 | 0.47%（84 筆） | 13 |
| 2308 | 12,878 | +20.8% | 93 | 0.7 | 0.25%（147 筆） | 11 |
| 2301 | 6,973 | +129.1% | 27 | 0.4 | 0.35%（111 筆） | 129 |
| 2454 | 7,854 | +3.3% | 100 | 0.6 | 0.25%（167 筆） | 45 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 35 個月、投入 175,000 元（16 檔等權）
- 籃子市值 382,522（+118.6%）；0050 市值 304,385（+73.9%）；差 **+44.6 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 前三分之一 n=122 超額 +0.4%；後三分之一 n=122 超額 -7.1%；全部 -3.7%
- 狀態：可讀（n 達門檻）（state 672 筆、已回填 T+20 368 筆）

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

