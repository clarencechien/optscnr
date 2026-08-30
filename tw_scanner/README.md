# 🇹🇼 台股雷達站（tw_scanner + delta_radar）

_README 由 build_readme.py 於 2026-08-30 08:28 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-08-28

## 鋒面：⛅ **NEUTRAL** 　(score +0.63)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`+371,209,677,957`，落在近一年第 **99** 百分位
- 外資大台淨倉 Δ：`+1,181`，落在近一年第 **69** 百分位（水位 -83,655 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+2,630`，落在近一年第 **31** 百分位
- 融資餘額變化：`+7,258,752,000`，落在近一年第 **88** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-08-30 08:28 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 ⚪ NO_DATA

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | ⚪ NO_DATA | all RSS feeds failed |

### M5 narrative_triggers — ⚪ NO_DATA
- feed capex_cut failed: HTTP Error 503: Service Unavailable
- feed vr300_delay failed: HTTP Error 503: Service Unavailable
- feed debt_financed_capex failed: HTTP Error 503: Service Unavailable
- feed lc_psu_competition failed: HTTP Error 503: Service Unavailable
- ⚠️ degraded: all RSS feeds failed

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **1** 筆；state 已有 outcomes 的 entry：**91/91**
- 遠期報酬視窗：T+5/10/20（2308 收盤）｜用 `--hit-rate` 看分模組 gate 有效性表

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*

---

# tw_scanner 警報回測 — 警報後遠期報酬 vs 無條件基線

## capitulation — 觸發 14 日 / 8 個事件簇
| 水平 | 事件後中位數 | 事件後均值 | 基線中位數 | 命中率(同號) | n |
|---|---|---|---|---|---|
| 20日 | +5.75% | +6.00% | +2.17% | 67% | 6 |
| 60日 | +9.80% | +12.71% | +5.14% | 83% | 6 |

事件日列表: 2020-03-09, 2020-03-19, 2022-03-08, 2024-04-22, 2024-07-19, 2024-08-05, 2026-07-20, 2026-07-29

> 判讀準則：事件後分佈與基線無法分離 ⇒ 刪除該警報。儀器不留裝飾品。

---

