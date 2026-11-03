# 🇹🇼 台股雷達站（週報 + tw_scanner + delta_radar + tsmc_radar + DCA 影子帳本 + 賭場 sector）

_README 由 build_readme.py 於 2026-11-03 10:45 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜[MANUAL_dca_ledger.md](MANUAL_dca_ledger.md)（含賭場 sector）｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 📬 台股週報 — 2026-11-03

> 給定期定額買 0050 的人，一週看一次。規則影子帳本＋籌碼溫度計＋2308／2330 論點監控＋賭場 sector。**沒有任何一行是買賣建議；曝險與部位由人管。**

## TL;DR

- 週檢查（2026-11-06）：本週無警報、預算未動 → 等（2026-11-13 再看）。
- 鋒面 🌧️ DE_RISK（本週未變）。
- 2308 前提 🔴 RED；無背離（前提 RED、價格 20 日 -33.3%）；PER 40.7，3 年分位 83 → 61
- 2330 前提 🟢 GREEN；無背離（前提 GREEN、價格 20 日 -8.6%）；PER 27.0，3 年分位 77 → 58
- 投降窗加碼歷史 8 次：比等到例行日買平均便宜 +1.17%、勝率 75%；平均成本 vs 純 DCA +0.67%。

## 1. 本期機械指示（DCA 規則影子帳本）

- **週檢查・月預算**（決策日 2026-11-06）：本週無警報、預算未動 → 等（2026-11-13 再看）
- 例行（對照）：**2026-12-06** 買 10,000 元
- 投降窗加碼：無
- 鋒面調節（假說）：DE_RISK ×1.5 = 15,000 元

自 2019-01-02 起 94 期（等額假設）：

| 規則 | 買次 | 平均成本 | vs 純 DCA | 報酬 | XIRR |
|---|---|---|---|---|---|
| 純定期定額 | 94 | 32.86 | +0.00% | +216.80% | +28.67% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 33.29 | +1.31% | +212.67% | +29.06% |
| 定期定額＋投降窗加碼 | 102 | 33.08 | +0.67% | +214.74% | +28.81% |
| 定期定額＋鋒面調節 | 94 | 33.02 | +0.49% | +215.29% | +28.61% |
| 對照：一次投入 | 1 | 18.5 | -43.70% | +462.60% | +24.70% |

投降窗加碼 8 次：edge +1.17%、勝率 75%。 明細見 `dca_ledger.md`。

## 2. 天氣（籌碼溫度計）

- 鋒面 🌧️ **DE_RISK**（score -0.19，2026-11-02）；本週未變
- 分位數：外資現貨 0.4、大台Δ 88.1、散戶小台 53.2、融資Δ 27.0
- 本週投降警報：無
- 警報戰績（月更回測）：8 簇，20 日中位 +8.72% vs 基線 +2.20%、命中 75%

## 3. 論點監控（2308 delta_radar／2330 tsmc_radar）

### 2308
- 前提（最近全模組 2026-11-02）：🔴 RED
- 無背離（前提 RED、價格 20 日 -33.3%）；PER 40.7，3 年分位 83 → 61
  - 🔴 M1 revenue_acceleration：2026-09 YoY +14.6%, slope -13.60pp/月, 連續減速 3 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ +35.3% / 存貨 QoQ +20.7% / FCF/淨利 1.74
  - 🟢 M3 thai_shadow：DELTA.BK 2026-09-30 營收 YoY +42.4%, GM 27.3%
  - 🟢 M4 customs_flow：US 進口 HS850440 (TH+TW) 近3月 $1366.7M, YoY +22.4%
  - 🟢 M5 narrative_triggers：capex_cut:6e(7m) / vr300_delay:8e(9m) / debt_financed_capex:12e / lc_psu_competition:0e
  - 🔴 M6 peer_divergence：cooling:3324領先+37pp
  - ⚪ M8 revision_velocity：下修 0/上修 0（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 40.7（3 年第 61 百分位；20 日前第 83）；觀察
- 回填樣本 126 筆（T+20 超額）；退役判準見 `delta_radar_report.md`

### 2330
- 前提（最近全模組 2026-11-02）：🟢 GREEN
- 無背離（前提 GREEN、價格 20 日 -8.6%）；PER 27.0，3 年分位 77 → 58
  - 🟢 M1 revenue_acceleration：2026-09 YoY +54.6%, slope -4.41pp/月, 連續減速 0 個月
  - 🟢 M2 bullwhip_health：合約負債 QoQ n/a / 存貨 QoQ +23.8% / FCF/淨利 0.9
  - 🟢 M3 adr_premium：ADR 溢價 +13.5%（1 年第 20 百分位；觀察）
  - 🟢 M4 customs_flow：US 進口 HS854231 (TH+TW) 近3月 $3675.7M, YoY +60.6%
  - 🟡 M5 narrative_triggers：export_controls_tariffs:11e(12m) / n2_arizona_ramp:20e(27m) / cowos_capacity:7e / geopolitics:2e / hyperscaler_capex:6e(7m)
  - 🟢 M6 peer_divergence：cohort 內 2330 未被對手顯著反超（離散在容忍帶內）
  - ⚪ M8 revision_velocity：下修 0/上修 1（樣本不足 <3，NO_DATA）
  - 🟢 M9 valuation：PER 27.0（3 年第 58 百分位；20 日前第 77）；觀察
- 回填樣本 20 筆（T+20 超額）；退役判準見 `tsmc_radar_report.md`


## 4. 賭場 sector（AI 個股，只收資料）

| 代號 | 名稱 | 桶 | 20 日 vs 0050 | 月營收 YoY | 3 月均 | 斜率 |
|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC | -2.12% | +496.00% | +317.10% | +157.11 |
| 2383 | 台光電 | CCL | +2.44% | +168.90% | +142.70% | +19.74 |
| 2382 | 廣達 | 機櫃 | +2.45% | +76.70% | +128.50% | -27.31 |
| 3443 | 創意 | ASIC | -2.29% | +97.80% | +122.40% | -30.30 |
| 3231 | 緯創 | 機櫃 | +5.47% | +87.20% | +104.80% | +13.21 |
| 3324 | 雙鴻 | 散熱 | -1.72% | +23.20% | +69.00% | -46.74 |
| 2345 | 智邦 | 網通 | -1.91% | +66.10% | +65.70% | -2.78 |
| 6669 | 緯穎 | 機櫃 | -5.82% | +100.00% | +63.20% | +30.38 |
| 3037 | 欣興 | 載板 | -8.05% | +64.70% | +54.90% | +10.49 |
| 3017 | 奇鋐 | 散熱 | -3.82% | +44.90% | +52.20% | -6.24 |
| 2330 | 台積電 | 製造 | +1.05% | +54.60% | +50.90% | +4.98 |
| 2317 | 鴻海 | 機櫃 | +6.90% | +38.40% | +48.20% | -7.89 |
| 3711 | 日月光投控 | 封測 | +2.97% | +45.50% | +44.80% | +1.18 |
| 2308 | 台達電 | 電力 | -21.21% | +14.60% | +32.40% | -16.57 |
| 2301 | 光寶科 | 電源 | -5.78% | +22.10% | +28.30% | -7.73 |
| 2454 | 聯發科 | IC設計 | -12.21% | +2.00% | +19.40% | -5.09 |

影子 DCA（每月等權買整籃 vs 同筆錢買 0050）：34 個月，籃子 +173.45% vs 0050 +94.98%，差 +78.47 pp；判準 可讀
月營收加速三分位 vs T+20 超額：可讀（n 達門檻）（回填 192 筆）。明細 `casino_report.md`。
*賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。*

## 5. 下週日曆

- 2026-11-10（7 天後）台股月營收公告截止（2330／2308 通常 10 日前後）
- 2026-12-10（37 天後）台股月營收公告截止（2330／2308 通常 10 日前後）

## 6. 資料健康

- ✅ 天氣台：最新 2026-11-02
- ✅ DCA 帳本：最新 2026-11-02
- ✅ delta_radar：最新 2026-11-03
- ✅ tsmc_radar：最新 2026-11-03
- ✅ 賭場 sector：最新 2026-11-02

---
*tw_brief — 週報：規則影子帳本＋溫度計＋2308／2330 論點監控＋賭場 sector。沒有任何一行是買賣建議；曝險與部位由人管。 產出 2026-11-03T10:45:32+00:00*

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-11-02

## 鋒面：🌧️ **DE_RISK** 　(score -0.19)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`-1,067,837,631,138`，落在近一年第 **0** 百分位
- 外資大台淨倉 Δ：`+2,862`，落在近一年第 **88** 百分位（水位 -89,379 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+6,899`，落在近一年第 **53** 百分位
- 融資餘額變化：`-768,521,000`，落在近一年第 **27** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-11-03 10:03 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 RED、價格 20 日 -33.3%）；PER 40.7，3 年分位 83 → 61

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟢 GREEN | capex_cut:6e(7m) / vr300_delay:8e(9m) / debt_financed_capex:12e / lc_psu_competition:0e |

### M5 narrative_triggers — 🟢 GREEN
```json
{
  "events": {
    "capex_cut": 6,
    "vr300_delay": 8,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 7,
    "vr300_delay": 9,
    "debt_financed_capex": 12,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 6,
      "mentions": 7,
      "gate": "zscore",
      "z": -0.27,
      "denial": false
    },
    "vr300_delay": {
      "events": 8,
      "mentions": 9,
      "gate": "zscore",
      "z": -2.39,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 12,
      "mentions": 12,
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
- [capex_cut] Why Tesla's $5 billion capex cut isn't the warning sign AI stock bears think it is - Yahoo Finance
- [capex_cut] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [capex_cut] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia CEO Jensen Huang Dismisses Vera Rubin Hardware Delay Report, Affirms 'Giant' Production Volumes - Yahoo Finance
- [vr300_delay] NVIDIA Quashes Rubin & Kyber Rack Delay Rumors, Says “Chip Roadmap Is Intact” - Wccftech
- [debt_financed_capex] AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch. - CNBC
- [debt_financed_capex] Top hyperscalers likely to have more AI-linked debt than now known, S&P Global warns - Reuters
- [debt_financed_capex] Big Tech will fund more than a third of its AI investments with debt in 2027, Goldman Sachs predicts - Yahoo Finance

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **7** 筆；state 已有 outcomes 的 entry：**154/154**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-10-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 47 / -7.38 | 10 / -7.00 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M2 | 25 / -8.19 | 22 / -8.24 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向對 |
| M3 | 27 / -10.89 | 20 / -4.60 | 2 | 無法判定（狀態翻轉 2 次 < 3；cohort 等於兩段日曆時間）；方向反 |
| M4 | 38 / -7.40 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 49 / -3.85 | 60 / -9.55 | 47 | 通過最低檢驗：GREEN 優於 YELLOW/RED |
| M6 | 0 / — | 30 / -4.66 | 3 | 樣本不足（缺一側 cohort） |
| M8 | 24 / -2.50 | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# TSMC Radar (2330.TW) — 2026-11-03 10:45 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟢 GREEN

## 前提 vs 價格：無背離（前提 GREEN、價格 20 日 -8.6%）；PER 27.0，3 年分位 77 → 58

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2330 遠期報酬。觀察模組（M3 ADR／M9 估值）不進總判定。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🟡 YELLOW | export_controls_tariffs:11e(12m) / n2_arizona_ramp:20e(27m) / cowos_capacity:7e / geopolitics:2e / hyperscaler_capex:6e(7m) |

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "events": {
    "export_controls_tariffs": 11,
    "n2_arizona_ramp": 20,
    "cowos_capacity": 7,
    "geopolitics": 2,
    "hyperscaler_capex": 6
  },
  "mentions": {
    "export_controls_tariffs": 12,
    "n2_arizona_ramp": 27,
    "cowos_capacity": 7,
    "geopolitics": 2,
    "hyperscaler_capex": 7
  },
  "scoring": {
    "export_controls_tariffs": {
      "events": 11,
      "mentions": 12,
      "gate": "zscore",
      "z": -2.5,
      "denial": false
    },
    "n2_arizona_ramp": {
      "events": 20,
      "mentions": 27,
      "gate": "zscore",
      "z": 1.56,
      "denial": true
    },
    "cowos_capacity": {
      "events": 7,
      "mentions": 7,
      "gate": "zscore",
      "z": 0.0,
      "denial": false
    },
    "geopolitics": {
      "events": 2,
      "mentions": 2,
      "gate": "zscore",
      "z": -0.07,
      "denial": false
    },
    "hyperscaler_capex": {
      "events": 6,
      "mentions": 7,
      "gate": "zscore",
      "z": -0.05,
      "denial": false
    }
  }
}
```
- [export_controls_tariffs] TSMC Weighs Rare-Earth-Free Motors Amid China's Export Controls, Moves to Diversify Supply Chain [Taiwan Chip News] - 아시
- [export_controls_tariffs] How Taiwan's New AI Chip Export Controls Could Affect China｜Industry｜2026-10-20｜web only - 天下雜誌
- [export_controls_tariffs] China is considering export controls on AI technologies, including banning local companies from using TSMC, report claim
- [n2_arizona_ramp] [News] Samsung 2nm Yields Reportedly at ~55%, Below Mass Production Threshold; Qualcomm May Opt for TSMC - TrendForce
- [n2_arizona_ramp] Samsung's 2nm Yield Recovers to 55%... Qualcomm Return Hinges on Sept. 22 Summit - BigGo Finance
- [n2_arizona_ramp] Qualcomm Weighs TSMC Shift As Samsung 2nm Yield Slips - Businesskorea
- [cowos_capacity] Report: TSMC to Double CoWoS Capacity by 2028 as AI Chip Shortage Spills Over to Rivals - Wccftech
- [cowos_capacity] Intel vs TSMC: How CoWoS Constraints Could Benefit Intel Foundry - Beth Kindig – Medium
- [cowos_capacity] TSMC CoWoS shortage drives SK Hynix-Intel 2.5D push - digitimes
- [geopolitics] In the shadow of China’s military, Taiwan’s globally critical suppliers keep working - Automotive News
- [geopolitics] China’s planned military exercises near Taiwan may have another target: Japan - The Japan Times
- [hyperscaler_capex] Why Tesla's $5 billion capex cut isn't the warning sign AI stock bears think it is - Yahoo Finance
- [hyperscaler_capex] The AI Capex Wall: Why Financing Constraints Will Trigger A Slowdown - Seeking Alpha
- [hyperscaler_capex] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **8** 筆；state 已有 outcomes 的 entry：**55/55**
- 遠期報酬視窗：T+5/10/20（2330 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

### 退役判準（自動計算，判決是人下的；覆核日 2026-12-31）
| 模組 | GREEN n / T+20 超額 | YELLOW+RED n / 超額 | 狀態翻轉 | 判準 |
|---|---|---|---|---|
| M1 | 8 / +1.00 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M2 | 8 / +1.00 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M4 | 7 / +1.05 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M5 | 5 / +1.25 | 15 / +0.96 | 27 | 累積中（GREEN n=5 < 30）；方向對 |
| M6 | 8 / +1.00 | 0 / — | 0 | 樣本不足（缺一側 cohort） |
| M8 | 0 / — | 0 / — | 0 | 樣本不足（缺一側 cohort） |

_n 是「該狀態的天數」不是獨立樣本：狀態幾乎不翻的模組，cohort 比較等於比兩段日曆時間。翻轉 < 3 次一律「無法判定」。_

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# 💰 DCA 規則影子帳本（0050）— 至 2026-11-02

每月 6 日後首個交易日買 10,000 元；價格 2019-01-02 起、鋒面/警報序列 2019-01-02 起（1900 日）。等額假設、不記真實部位。

## 本期（機械指示，不是建議）

- 下一個例行買日：**2026-12-06** · 純定期定額 10,000 元
- 投降窗加碼：無（近 5 個交易日無警報）
- 鋒面 DE_RISK → 調節規則本期 ×1.5 = 15,000 元（假說，待處決）
- **週檢查・月預算**（決策日 2026-11-06）：本週無警報、預算未動 → 等（2026-11-13 再看）

## 視窗：full（2019-01-02 → 2026-11-02，94 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 94 | 940,000 | 28,606.78 | 32.86 | +0.00% | 2,977,966 | +216.80% | +28.67% |
| 週檢查・月預算・投降窗即刻投入 | 94 | 1,000,000 | 30,035.77 | 33.29 | +1.31% | 3,126,724 | +212.67% | +29.06% |
| 定期定額＋投降窗加碼 | 102 | 1,020,000 | 30,838.81 | 33.08 | +0.67% | 3,210,320 | +214.74% | +28.81% |
| 定期定額＋鋒面調節 | 94 | 1,025,000 | 31,044.08 | 33.02 | +0.49% | 3,231,689 | +215.29% | +28.61% |
| 對照：一次投入 | 1 | 940,000 | 50,801.69 | 18.50 | -43.70% | 5,288,456 | +462.60% | +24.70% |

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

## 視窗：last_12m（2025-11-03 → 2026-11-02，12 期）

| 規則 | 買次 | 投入 | 單位 | 平均成本 | vs 純 DCA | 期末市值 | 報酬 | XIRR |
|---|---|---|---|---|---|---|---|---|
| 純定期定額 | 12 | 120,000 | 1,427.31 | 84.07 | +0.00% | 148,583 | +23.82% | +47.77% |
| 週檢查・月預算・投降窗即刻投入 | 12 | 140,000 | 1,640.60 | 85.33 | +1.50% | 170,786 | +21.99% | +47.63% |
| 定期定額＋投降窗加碼 | 14 | 140,000 | 1,631.64 | 85.80 | +2.06% | 169,854 | +21.32% | +46.17% |
| 定期定額＋鋒面調節 | 12 | 140,000 | 1,648.60 | 84.92 | +1.01% | 171,620 | +22.59% | +46.62% |
| 對照：一次投入 | 1 | 120,000 | 1,894.11 | 63.35 | -24.65% | 197,177 | +64.31% | +65.22% |

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

# 🎰 賭場 sector — AI 個股影子追蹤（2026-11-02）

> 賭場 sector：小部位、預算固定、名單是人挑的、沒有訊號、期望值未證明。只收資料。 基準 0050。判準：先寫死：籃子 DCA 對 0050 DCA 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」的 T+20 超額各 n≥30 才准下結論。之前一律「累積中」。

| 代號 | 名稱 | 桶 | 0050 | 收盤 | 20 日 | vs 0050 | 月營收 YoY | 3 月均 | 斜率 pp/月 |
|---|---|---|---|---|---|---|---|---|---|
| 3661 | 世芯-KY | ASIC |  | 3395.0 | -9.2% | -2.1% | +496.0% | +317.1% | +157.1 |
| 2383 | 台光電 | CCL | ✓ | 4705.0 | -4.7% | +2.4% | +168.9% | +142.7% | +19.7 |
| 2382 | 廣達 | 機櫃 | ✓ | 318.0 | -4.7% | +2.5% | +76.7% | +128.5% | -27.3 |
| 3443 | 創意 | ASIC |  | 7285.0 | -9.4% | -2.3% | +97.8% | +122.4% | -30.3 |
| 3231 | 緯創 | 機櫃 | ✓ | 181.5 | -1.6% | +5.5% | +87.2% | +104.8% | +13.2 |
| 3324 | 雙鴻 | 散熱 |  | 1395.0 | -8.8% | -1.7% | +23.2% | +69.0% | -46.7 |
| 2345 | 智邦 | 網通 | ✓ | 1615.0 | -9.0% | -1.9% | +66.1% | +65.7% | -2.8 |
| 6669 | 緯穎 | 機櫃 | ✓ | 1820.0 | -12.9% | -5.8% | +100.0% | +63.2% | +30.4 |
| 3037 | 欣興 | 載板 | ✓ | 997.0 | -15.2% | -8.1% | +64.7% | +54.9% | +10.5 |
| 3017 | 奇鋐 | 散熱 | ✓ | 3060.0 | -10.9% | -3.8% | +44.9% | +52.2% | -6.2 |
| 2330 | 台積電 | 製造 | ✓ | 2330.0 | -6.0% | +1.1% | +54.6% | +50.9% | +5.0 |
| 2317 | 鴻海 | 機櫃 | ✓ | 251.0 | -0.2% | +6.9% | +38.4% | +48.2% | -7.9 |
| 3711 | 日月光投控 | 封測 | ✓ | 674.0 | -4.1% | +3.0% | +45.5% | +44.8% | +1.2 |
| 2308 | 台達電 | 電力 | ✓ | 1355.0 | -28.3% | -21.2% | +14.6% | +32.4% | -16.6 |
| 2301 | 光寶科 | 電源 | ✓ | 243.5 | -12.9% | -5.8% | +22.1% | +28.3% | -7.7 |
| 2454 | 聯發科 | IC設計 | ✓ | 3970.0 | -19.3% | -12.2% | +2.0% | +19.4% | -5.1 |

## 借券（只收資料，不是訊號）

> 台灣大型股的借券賣出多為避險／套利（ETF 造市、權證、可轉債、ADR 套利），不等於看空。較有意義的組合是「餘額暴增＋費率跳升＋找不到避險理由」。這裡只記，不做規則。

| 代號 | 借券賣出餘額（張） | 20 日變化 | 一年分位 | 回補天數 | 費率中位 | 融券（張） |
|---|---|---|---|---|---|---|
| 3661 | 391 | +42.6% | 8 | 0.2 | 0.80%（44 筆） | 18 |
| 2383 | 644 | +24.3% | 32 | 0.2 | 0.02%（51 筆） | 20 |
| 2382 | 70,040 | +18.2% | 14 | 6.0 | 1.00%（121 筆） | 47 |
| 3443 | 1,156 | -35.7% | 75 | 0.7 | 1.00%（78 筆） | 218 |
| 3231 | 31,220 | -57.5% | 2 | 0.8 | 0.50%（101 筆） | 368 |
| 3324 | 4,129 | +57.7% | 55 | 1.2 | 5.00%（81 筆） | 72 |
| 2345 | 627 | +1.5% | 5 | 0.1 | 0.39%（46 筆） | 1 |
| 6669 | 4,162 | -67.8% | 4 | 0.8 | 10.00%（249 筆） | 233 |
| 3037 | 3,618 | +15.1% | 9 | 0.2 | 0.05%（65 筆） | 365 |
| 3017 | 2,466 | +26.3% | 52 | 0.8 | 0.50%（43 筆） | 31 |
| 2330 | 16,102 | +10.2% | 94 | 0.6 | 0.25%（231 筆） | 13 |
| 2317 | 77,792 | +90.6% | 77 | 1.8 | 0.25%（144 筆） | 506 |
| 3711 | 12,459 | +0.4% | 10 | 0.7 | 0.25%（74 筆） | 195 |
| 2308 | 13,156 | +123.8% | 98 | 1.0 | 0.25%（124 筆） | 131 |
| 2301 | 4,112 | +26.2% | 21 | 0.3 | 0.28%（70 筆） | 444 |
| 2454 | 5,238 | +16.8% | 88 | 0.6 | 0.25%（118 筆） | 22 |

## 影子 DCA：每月等權買整籃 vs 同一筆錢買 0050

- 2024-01-08 起 34 個月、投入 170,000 元（16 檔等權）
- 籃子市值 464,859（+173.4%）；0050 市值 331,468（+95.0%）；差 **+78.5 pp**
- 判準狀態：可讀

## 月營收 3 月均 YoY 三分位 vs T+20 對 0050 超額（只印不裁決）

- 前三分之一 n=64 超額 +2.3%；後三分之一 n=64 超額 -3.3%；全部 -1.0%
- 狀態：可讀（n 達門檻）（state 512 筆、已回填 T+20 192 筆）

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

