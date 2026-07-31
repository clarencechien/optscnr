# delta_radar — 2308.TW 馬賽克驗證雷達

optscnr radar 家族成員（space_radar / unknown_radar 的兄弟模組）。
針對高盛 4500 目標價劇本的三個**未驗證前提**做機械化監控：

1. FCF/淨利缺口在 Q2/Q3 轉回（Q1 基準 0.43，Gate 0.6）
2. 合約負債續航（長鞭終端拉力）
3. 實體出貨真的在上船（泰子公司 + 美國海關雙重驗證）

> Shadow-mode instrument：這是測量儀器，不是交易訊號。

## 模組（v2「離散引擎」）

| 模組 | 訊號 | 資料源 | 頻率 |
|---|---|---|---|
| M1 | 月營收 YoY 的二階導數（斜率+連續減速） | FinMind `TaiwanStockMonthRevenue` | 月 |
| M2 | 合約負債 QoQ / 存貨 QoQ / FCF/淨利 | FinMind 三大報表 | 季 |
| M3 | DELTA.BK 營收 YoY + 毛利率（領先母公司約 2 天） | yfinance | 季 |
| M4 | 美國進口 HS 8504.40（泰+台）滾動 3 月 YoY | US Census Trade API | 月（落後 ~6 週） |
| M5 | RSS 敘事桶：capex 砍單 / VR300 延期 / 舉債擴張 / 水冷PSU競爭；**去重+z-score+否認上限** | Google News RSS | 即時 |
| **M6** | **跨供應商離散：cohort 內誰的斜率先變（power/cooling/rack）** | FinMind 月營收 | 月 |
| **M8** | **目標價修正 velocity：下修/上修方向比，連 2 次 run 偏空才升級** | Google News RSS | 即時 |

每模組輸出 🟢/🟡/🔴/⚪，總判定規則在 config `aggregation`。
任何模組失敗只降級為 ⚪ NO_DATA，永不讓整支雷達掛掉。
（M7 是背景回填任務，不出色燈；模組編號跳過 m7。）

**M5 v2 升級（BUG-2）**：
- **去重**：同一事件被 N 家媒體報導 = 1 event + N mentions（用標題 token 集近似合併）。
  z-score 用 event 數，mention 數留作強度參考。
- **z-score**：以 state.json 近 10 次 run 的各桶 event 數算 rolling mean/std，
  `z>1.5`→🟡、`z>2.5`→🔴。冷啟動（<5 筆歷史）fallback 現行絕對值。
- **否認偵測**：桶設 `denial_keywords`（quashes/denies/roadmap intact…），
  偵測到官方否認時狀態上限 🟡「爭議中」——被否認的傳聞是活爭議，不是確認的 🔴。
- 新桶 `lc_psu_competition`：對手（Lite-On/Acbel/Flex）水冷 PSU 認證/量產新聞。

**M4 by_country**：TH/TW 分列（僅記錄，判定仍用合計），看得到「泰國增/台灣減」的產地遷移。

**M6 離散面板**：台灣月營收強制公告是唯一的結構性資訊優勢（美國同業季報、台廠月報）。
M6 不看 2308 的 level，看 **cohort 內對手的 3 月平均 YoY 是否反超 2308**：
- `power`（光寶2301/Acbel6282）反超 = ASIC PSU 份額外溢先行訊號 → 升級
- `cooling`（雙鴻3324/AVC3017）反超 = sidecar→L2L 遷移、散熱故事打折 → 升級
- `rack`（鴻海2317/廣達2382/緯穎6669）= 下游拉貨 proxy，整鏈同向為 buildout confirm → **僅記錄不升級**

**M7 後果回填（非模組，背景任務）**：每次 run 後把 2308 的 T+5/10/20 遠期報酬回填到
每筆 state entry，讓 gate 有效性可回測（儀器畢業的前提）。`--hit-rate` 印出分模組報酬表。
每筆同時存 **raw 報酬**與 **超額報酬**（2308 − benchmark，預設 `0050`，同 T+N 交易日視窗）——
`--hit-rate` 主表顯示超額報酬、把市場 beta 單獨列一行當 context，避免下跌行情讓每個 cohort
都變負而看不出 gate 的相對預測力。**樣本不足的 cohort（如 M6/M8 剛上線）顯示 `—`：
M7 拒絕在 n 太小時評分，這是可信度的證據不是缺陷。**

## 快速開始（本機 / Actions）

```bash
pip install -r requirements.txt
python delta_radar.py                       # 全模組實跑（含 M6；跑完順帶 M7 回填）
python delta_radar.py --selftest            # 零網路 fixtures 驗證管線（含 M6/M7 斷言）
python delta_radar.py --modules m1,m6       # 只跑月頻模組（partial run 記為 PARTIAL）
python delta_radar.py --dump-accounts       # 印出 FinMind 實際科目名（調 M2 regex 用）
python delta_radar.py --hit-rate            # 分模組 T+N 超額報酬表（2308−benchmark；需已回填）
python delta_radar.py --backfill-only       # 只回填歷史 state 的 outcomes 不跑掃描
```

> **partial run 標記（BUG-1）**：非全模組的 run（如 daily m5-only）其 `overall` 記為
> `PARTIAL(<modules>)` 並附 `modules_requested`，回測時可過濾，不再污染 gate 有效性樣本。

## Colab 一格搞定

```python
!git clone https://github.com/clarencechien/optscnr.git -q
!pip install -r optscnr/delta_radar/requirements.txt -q
import os
# os.environ["FINMIND_TOKEN"] = "..."     # 選填，匿名可跑但限流
# os.environ["CENSUS_API_KEY"] = "..."    # 選填，無 key 每日 ~500 calls 夠用
!python optscnr/delta_radar/delta_radar.py \
    --config optscnr/delta_radar/config/delta_radar_config.json
```

Colab 沒有 cron——原型驗證完請靠本 repo 的 GitHub Actions
（`.github/workflows/delta_radar.yml`，週一/週四 10:30 台北時間）。

## 已知需要現場校準的點（唯一的 TODO）

**M2 的 FinMind 科目名**：合約負債在 FinMind schema 裡的確切 `type` 字串
未在離線環境驗證。首次實跑請先：

```bash
python delta_radar.py --dump-accounts | grep -i contract
```

把實際科目名補進 config 的 `m2_bullwhip_health.account_patterns`。
其餘四個模組的 API 介面均為穩定公開規格。

## Gate 設計依據（2026-06-11 校準）

- M1：5 月 YoY +43.7% 為當前水位；黃線 25%、紅線 10%，連續減速 2/3 個月觸發
- M2：Q1 FCF/淨利 = 88.4億/205.5億 = **0.43**（黃旗起點）；GREEN 需 ≥0.6
- M3：DELTA.BK Q1 +56.2%、GM 31.7%；GM 地板 27%
- M4：綠線 +20%（對應母公司 30%+ 成長扣除均價變動的保守折扣）
- M5：VR300/Kyber 延期是 210% CAGR 產品線的命門，1 hit 即黃

## 輸出

- `output/delta_radar_report.md` — 人讀報告
- `output/delta_radar_state.json` — append-only 歷史，每筆帶 `modules_requested`、
  M7 回填的 `outcomes`（T+5/10/20 raw + 超額報酬 vs benchmark），留給回測 gate 有效性

> `--selftest` 一律寫到臨時目錄，永不碰真實 state.json（避免 fixture 判定污染回測樣本）。
