# 🇹🇼 台股雷達站（tw_scanner + delta_radar）

_README 由 build_readme.py 於 2026-08-18 03:22 UTC 重組；兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_

> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)

---

# 🌤️ 台股 DCA 天氣簡報 — 2026-08-17

## 鋒面：⛅ **NEUTRAL** 　(score +0.32)

## 溫度計（全部為 Δ 與滾動分位數，無絕對閾值）
- 外資現貨 20 日累積：`+154,838,419,385`，落在近一年第 **86** 百分位
- 外資大台淨倉 Δ：`+1,705`，落在近一年第 **77** 百分位（水位 -83,474 口僅供參考，不參與判讀）
- 散戶小台淨倉：`+7,116`，落在近一年第 **63** 百分位
- 融資餘額變化：`+3,042,354,000`，落在近一年第 **64** 百分位

## 警報：無（尾部共現條件未成立）

---
*tw_scanner v2 — 天氣台，不是擇時機。狀態以週為單位翻轉；敘事僅由狀態轉移產生。本輸出為量化測量，非投資建議。*

---

# Delta Radar (2308.TW) — 2026-08-18 03:22 UTC

## 總判定：⚪ PARTIAL（僅跑 m5）｜模組色僅供參考 🟡 YELLOW

GS 4500 劇本前提的機械化監控：營收動能 (M1)、FCF/合約負債 (M2)、實體出貨 (M3/M4)、
敘事風險 (M5)、跨供應商離散 (M6)、目標價修正 velocity (M8)。
M7（後果回填，見報告末）為背景校準任務，不出色燈但每次 run 回填 2308 遠期報酬。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M5 narrative_triggers | 🔴 RED | capex_cut:7e(8m) / vr300_delay:15e(17m) / debt_financed_capex:13e / lc_psu_competition:0e |

### M5 narrative_triggers — 🔴 RED
```json
{
  "events": {
    "capex_cut": 7,
    "vr300_delay": 15,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "mentions": {
    "capex_cut": 8,
    "vr300_delay": 17,
    "debt_financed_capex": 13,
    "lc_psu_competition": 0
  },
  "scoring": {
    "capex_cut": {
      "events": 7,
      "mentions": 8,
      "gate": "zscore",
      "z": 3.33,
      "denial": false
    },
    "vr300_delay": {
      "events": 15,
      "mentions": 17,
      "gate": "zscore",
      "z": 0.89,
      "denial": true
    },
    "debt_financed_capex": {
      "events": 13,
      "mentions": 13,
      "gate": "zscore",
      "z": 0.33,
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
- [capex_cut] Will the next recession be caused by an AI capex cut-off? - investordaily.com.au
- [capex_cut] Investors Brace for Slowdown in Hyperscaler Spending Growth in AI - Global Banking & Finance Review
- [capex_cut] Marvell Drops 8% as AI Capex Slowdown Fears Weigh on Chips; Broadcom, AMD, and Intel Slide - 24/7 Wall St.
- [vr300_delay] Nvidia's Kyber rack for Rubin Ultra reportedly delayed to 2028, stopgap solution also axed due to customer pushback — An
- [vr300_delay] Nvidia next-gen 'Kyber' AI rack delayed to 2028 on manufacturing snags: report (NVDA:NASDAQ) - Seeking Alpha
- [vr300_delay] Jensen Huang Takes Stage at Morgan Stanley Roadshow: Quarterly Revenue Nears $100 Billion, Nvidia Denies Rubin Ultra Del
- [debt_financed_capex] AI infrastructure debt exceeds $236 billion in 2026, as tech giants shift to Wall Street financing. - KuCoin
- [debt_financed_capex] Tech companies’ AI debt surges as Oracle nears junk credit rating - The Cryptonomist
- [debt_financed_capex] After a nearly 1,000% surge, the AI debt orgy can’t last forever, while hidden borrowing has exploded to $1.65 trillion 

### M7 outcome_backfill — ⚙️ 背景校準（不出色燈）
- 本次回填 **11** 筆；state 已有 outcomes 的 entry：**83/83**
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

