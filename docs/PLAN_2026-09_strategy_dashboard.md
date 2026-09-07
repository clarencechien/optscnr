# PLAN — 策略矩陣 shadow 回測 + Cloudflare cron/dashboard（2026-09-08）

> 觸發：cron 又壞（GitHub 排程連續第三週不可靠）＋ 兩份方法論審計（Claude 09-07、GPT 09-07）
> 原則：**先用數字回答能回答的，回答不了的進 tracker 跑幾個月，不猜。**
> 本文件同時是規格與預先登記書——第三節的策略定義與判準寫下後三個月不動。

---

## 0. 一頁結論

1. 現在就能回答的：**出場政策該跟分類綁定，不是一套打天下。** 三個月成熟資料顯示樂透價位（<$1.5）死抱贏過 2x 賣半；實彈（>$3）用階梯贏過死抱；中間價位三種政策打平、樣本不足。IV≥50 的樂透票哪種政策都賠。
2. 回答不了的：每一格 n<15 的組合（中間價位全部、IV≥50 的短天期）、以及**T+20 之後「剩餘半倉抱到 DTE 21」的下場**——現在只有三個檢查點，沒有路徑資料。
3. 要做的東西分兩層：**量尺修復＋每日路徑紀錄**（沒有它，三個月後還是猜）；**Cloudflare 第二鬧鐘＋dashboard**（讓候選、LLM 判讀、賣點、三策略 shadow 結果每天自動累積並可視）。

---

## 1. 現在算得出來的數字（2026-06 ~ 08，三個檢查點齊全的 579 筆／357 事件）

口徑：EV＝等權平均倍數、未扣價差（扣 15% 來回價差 ×0.86）；命中＝T+5/10/20 任一 ≥2x；
「事件」＝標的-日去重。**全部是樣本內、正漂移季度、集中在 5 個事件——讀方向不讀精度。**

### 1.1 三個候選策略（A/B 是你問的兩個，C 是我提的第三個）

| 策略 | 定義 |
|---|---|
| **A 死抱** | 買入後不動，抱到末檢查點（≈ DTE 21 前後） |
| **B 2x 賣半** | 任一檢查點 ≥2x 時賣半口（credit 2.0），剩半口抱到末點 |
| **C 分類綁定** | 樂透（<$1.5）且 IV<50 → 死抱；實彈（>$3）→ 4 口階梯 2/4/8x＋1 口 runner；其餘（中間價位、或 IV≥50）→ -50% 停損 + 2x 賣半 |

| 樣本 | n / 事件 | A 死抱 | B 2x賣半 | C 分類綁定 | 逐月（事件等權）A / B / C |
|---|---|---|---|---|---|
| 全部 | 579 / 357 | 1.17 | 1.10 | **1.20** | 6月 1.92/1.52/1.93；7月 1.02/1.01/1.05；8月 1.02/0.92/1.05 |
| 規則 B 篩後（含 Δ7d>0，與程式一致） | 111 / 93 | 1.77 | 1.47 | **1.81** | 6月 4.13/2.88/4.16；7月 1.29/1.22/1.31；8月 2.15/1.53/2.13 |

- C 三個月都不輸 A、B，但 C 是**看完矩陣才定義的**（樣本內），真實優勢要打折；它的價值是「一個可預先登記的假說」，不是結論。
- B（你現在的規則）三個月都墊底：2x 賣半是保險，保費 ≈ 0.1–0.3x EV。命中票 51% 峰值在 T+20、66% 到 T+20 仍 ≥2x——贏家一直跑，2x 太早。
- 三者的中位數都 <1（0.84–0.88）：**六成的票賠錢，平均靠每月一兩個事件**。這是遊戲的形狀，任何出場政策都改不了。

### 1.2 分類 × 政策矩陣（決定「誰該綁哪種出場」）

EV 欄依序：死抱 / 2x 賣半 / 3x 賣半 / 4 口 2-4-8 / -50% 停+2x 半。⚠＝n<15，數字只是佔位，**進 tracker**。

| 分類 | n/事件 | 命中 | 死抱 | 2x半 | 3x半 | 4口階梯 | 停+2x半 | 目前最佳 | 狀態 |
|---|---|---|---|---|---|---|---|---|---|
| IV<50 樂透 DTE21-45 | 30/28 | 40% | **3.30** | 2.20 | 2.40 | 2.18 | 1.83 | 死抱 | 可用（排除 IBIT 後 1.94/1.45，中位 0.55） |
| IV<50 樂透 46-120 | 78/66 | 22% | 1.06 | 1.03 | 1.04 | 1.04 | 1.06 | 打平 | 可用：無差異 |
| IV<50 樂透 >120 | 58/47 | 19% | **1.41** | 1.34 | 1.39 | 1.38 | 1.35 | 死抱 | 可用 |
| IV<50 中間 21-45 | 9/8 | 0% | 1.01 | 1.01 | 1.01 | 1.01 | 1.10 | — | ⚠ tracker |
| IV<50 中間 46-120 | 9/9 | 22% | 1.27 | 1.17 | 1.23 | 1.22 | 1.22 | — | ⚠ tracker |
| IV<50 中間 >120 | 5/4 | 20% | 1.49 | 1.48 | 1.49 | 1.48 | 1.48 | — | ⚠ tracker |
| IV<50 實彈 21-45 | 17/14 | 53% | 1.67 | 1.58 | 1.78 | **1.90** | 1.54 | 4口階梯 | 可用（n 邊緣） |
| IV<50 實彈 46-120 | 34/19 | 32% | 0.86 | 0.96 | 0.86 | 0.92 | **0.99** | 停損 | 全部 <1 |
| IV<50 實彈 >120 | 38/26 | 11% | 1.09 | 1.12 | 1.12 | 1.10 | 1.12 | 打平 | 可用：無差異 |
| IV≥50 樂透 21-45 | 14/12 | 21% | 0.27 | 0.39 | 0.46 | 0.46 | **0.70** | 停損 | ⚠ 但方向一致：**別玩** |
| IV≥50 樂透 46-120 | 64/56 | 11% | 0.75 | 0.76 | 0.75 | 0.75 | **0.82** | 停損 | 可用：全部 <1 |
| IV≥50 樂透 >120 | 128/103 | 14% | 1.08 | 1.03 | 1.07 | 1.06 | 1.04 | 死抱 | 可用：打平 |
| IV≥50 中間（三格） | 9–23 | 13–43% | 0.72–1.17 | | | | 停損略優 | — | ⚠ tracker |
| IV≥50 實彈 21-45 | 7/7 | 14% | 0.79 | 0.71 | 0.78 | 0.75 | 0.79 | — | ⚠ tracker |
| IV≥50 實彈 46-120 | 18/18 | 22% | **1.42** | 1.36 | 1.40 | 1.39 | 1.38 | 死抱 | 可用（n 邊緣） |
| IV≥50 實彈 >120 | 24/24 | 4% | 0.83 | 0.82 | 0.83 | 0.82 | 0.84 | — | 全部 <1 |

矩陣說的三句話：
1. **IV 是第一道閘門**：IV≥50 除了實彈 46-120 一格，其餘沒有一格 EV>1.1。「先選 IV<50」比任何出場政策都值錢。
2. **樂透 ＝ 死抱**：三個 DTE 桶死抱都是最佳或打平；-50% 停損在樂透 21-45 是最差（那些票先跌破一半再翻倍）。你原本「免費籌碼、接受全損」的直覺對。
3. **實彈 ＝ 階梯**：唯一「賣掉一部分比死抱好」的價位；貴的票回吐傷得起，分批出場有價值。中間價位：**現在沒答案**，三格加起來 23 筆。

### 1.3 你的其他問題（數字）

- **4 口成本**：規則 B 候選 4 口中位 $464；70% 候選 4 口 ≤$1,000、56% ≤$600；每個信號日中位 3 筆候選。4 口不加 EV（4 口 2/4/8 ＝ 1.59 vs 2 口 2x 半 1.57），買到的是 runner。
- **整體能否 2x**：三點完美預知上界 2.59x（規則 B 樂透）；可執行政策最高是死抱 1.97x 但中位 0.94。扣價差與樣本內收縮後合理預期 **1.1–1.4x**，好季度可能 2x。平滑的 2x 在資料裡不存在。
- **剩餘半倉抱到 DTE 21**：T+20 內是對的（移動停利 30% 回吐反而 -0.14x）。**T+20 之後沒有任何資料**——這是 tracker 第一項。

---

## 2. Tracker（回答不了的，跑幾個月再答）

每格判準：**n ≥ 30 且 ≥ 2 個月方向一致**才從 ⚠ 變「可用」；未達標前矩陣該格顯示佔位數字＋「累積中」。
累積速度：成熟樣本每月約 130–410 筆（依行情），中間價位每月約 20–40 筆 → 中間價位各格約需 **3–5 個月**。

| # | 問題 | 需要的資料 | 現有 n | 目標 | 預估 |
|---|---|---|---|---|---|
| T1 | 剩餘半倉「抱到 DTE 21」vs「T+20 出」哪個好？ | **每日路徑**（T+20 後到到期） | 0 | 50 個命中事件 | 需先上路徑紀錄，之後 2–3 個月 |
| T2 | 中間價位（$1.5–3）綁哪種出場？ | 矩陣中間三格 | 23 | 每格 30 | 3–5 個月 |
| T3 | 樂透 IV≥50 21-45 真的別玩？ | 該格 | 14 | 30 | 2 個月 |
| T4 | 實彈 21-45 階梯優勢是否成立？ | 該格 | 17 | 30 | 2 個月 |
| T5 | 策略 C 出樣本 EV | 2026-09-08 起新信號 | 0 | 100 筆 T+20 成熟 | 2–3 個月（含 P0 結構候選判準） |
| T6 | 「選標的」有沒有 edge？ | **對照組**（全 universe 的 20 日漲幅） | 0 | 100 個標的-日 | 需先上對照組紀錄，之後 2 個月 |
| T7 | 扣真實價差後的 EV | **bid/ask 快照** | 0 | 3 個月 | 需先上 schema v2 |
| T8 | LLM 三題問卷答對率／候選命中率 | **decisions log** | 0 | 60 個交易日 | dashboard 上線後 3 個月 |
| T9 | 第一階梯 2x→3x 是否穩定較好 | 路徑資料（T1 同源） | 樣本內 +0.1x | 與 T1 同 | 與 T1 同 |

**T1/T6/T7/T8 現在是 0 不是因為樣本少，是因為沒在記。** 這四項是第 4 節的建置理由。

---

## 3. 預先登記（2026-09-08 凍結，三個月不改）

- 策略定義：A/B/C 如 1.1；C 的分類邊界 $1.5 / $3 / IV 50 / 4 口階梯 2-4-8。
- 結構候選（規則 B）：分數 ≥8、DTE 21–120、IV<50、OTM<25%、Δ7d>0；只加標籤與欄位 `structural_pass`，**不改分數**。
- 判準（沿用 Claude 審計第 7 節）：100 筆出樣本 T+20 成熟後——
  - 策略 C（或 A）在規則 B 候選上 EV ≥1.25x 且命中 ≥25% → 成立，第③層閒錢按規則機械執行、size 固定
  - 1.05–1.25x → 只留 DTE 21–45 子集再測 50 筆
  - <1.05x → 樣本內過擬合，退回純觀察
- 對照組判準：上榜組 20 日漲 >10% 比例 − universe 同期比例 < 5 個百分點 → 停止「選標的」層的努力，scanner 定位改為合約結構篩子。
- **100 筆前改任何門檻，本文件作廢。**

---

## 4. 建置：量尺修復 + 路徑紀錄 + Cloudflare 第二鬧鐘/dashboard

### 4.1 Python 側（留在 GitHub Actions，不搬）

| # | 項目 | 做什麼 | 回答 tracker |
|---|---|---|---|
| P0-a | **schema v2 快照** | 快照多存 `last_price / bid / ask / quote_at / underlying_at`；舊欄位不動不改名（`entry_price` 保留，另加 `entry_ask`） | T7 |
| P0-b | **每日路徑紀錄** | `shadow_tracer` 對所有未到期高分信號每天記 `path[]`（date, last, bid, ask, spot），直到到期或 T+60；append-only | T1, T9 |
| P0-c | 結構候選區塊 | `main.py` 新增「🎯 結構候選」表（規則 B，DTE 21–45 優先）＋ `structural_pass` 欄；`shadow_tracer` 加 cohort 表 | T5 |
| P0-d | 三策略 shadow 表 | `shadow_tracer` 每天重算 1.1/1.2 的矩陣，輸出 `data/strategy_matrix.json`（含每格 n、狀態 可用/累積中）＋ SHADOWLOG 一節 | T2–T4 |
| P0-e | 量尺修語義 | `🆕新倉暴量` → `first_seen_in_feed`（顯示文字可留）；OI Δ7d 缺歷史存 null + `oi_delta_status`；tags 拆 `features[]` / `warnings[]` 結構欄 | 讓 T5 的 cohort 不再被顯示文字破壞 |
| P1 | 對照組 | 每日對全 universe 記 spot；tracer 回填 T+5/10/20 spot | T6 |
| P1 | 賣點欄位 | 每個候選依綁定策略預算出「賣點」：2x/3x 價、4 口階梯價、末點日（DTE 21 日期）→ `sell_points` 進候選 JSON | dashboard 顯示 |

### 4.2 Cloudflare 側（免費額度足夠；Python 零改動；**獨立資料夾 `cloudflare/`，只靠 dashboard Git 連動部署**）

```
cloudflare/                      ← Worker 專用資料夾，repo 其餘部分與它無關
├── wrangler.toml                ← 全部設定：workers_dev=false、preview_urls=false、cron、assets、vars
├── package.json                 ← 只有 wrangler devDependency（Workers Builds 用）
├── src/index.js                 ← scheduled()=第二鬧鐘；fetch()=/api/* + 靜態 dashboard
├── public/index.html            ← dashboard（Worker static assets 供檔，不另開 Pages 專案）
├── .dev.vars.example / .gitignore
└── README.md                    ← dashboard 一次性設定步驟
```

**部署**：Cloudflare dashboard → Workers & Pages → Create → **Import a repository** → 選本 repo →
Root directory `cloudflare`、Build command 空、Deploy command `npx wrangler deploy`、只部署 `main`。
之後 push `main` 即自動部署；secrets（`GITHUB_TOKEN`、之後的 `LLM_API_KEY`）在 dashboard 的
Variables and Secrets 設定，不進 git。**`*.workers.dev` 與 Preview URLs 關閉**；dashboard 網頁走
Custom domain（`wrangler.toml` 的 `[[routes]]` 解開填自己的網域）——沒網域時 cron 照跑、只是沒網頁。

```
┌ Worker scheduled()（第二鬧鐘：23:05 UTC 平日 + 00:35 UTC 跨日再查一次）──────┐
│ 1. GitHub API：22:00 UTC 之後 scanner.yml 有無任何 run？沒有 → workflow_dispatch  │
│ 2.（第 5 批）等 main 出現 data/dashboard/candidates_<市場日>.json                  │
│ 3.（第 5 批）組 prompt（第 5 節 v4 短版）→ 呼叫 LLM → GitHub API commit          │
│              data/decisions/<市場日>.json                                         │
└──────────────────────────────────────────────────────────────────────────────────┘
┌ Worker fetch()（同一個 Worker；靜態 dashboard 讀 raw.githubusercontent 的 JSON）──┐
│ 排程健康：各 workflow 近 36 小時觸發 vs 排定（已實作：/api/health）＋「立即補發」鈕  │
│ 今日候選：結構候選 + 綁定策略 + 賣點 + LLM 三題答案 + 狀態碼（第 4 批）             │
│ History：三策略 shadow 矩陣（1.2 的表，每格 n/EV/狀態，自動更新）（第 4 批）        │
│ Decisions：逐日 LLM 回答 log（prompt 版本、模型、答案、事後結果回填）（第 5 批）    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

- 資料主權在 git（append-only 審計）；dashboard 直接讀 raw.githubusercontent 的 JSON，**不需要 R2**
  （之後若 raw CDN 快取延遲惱人，再加 R2 當讀取快取，可隨時從 git 重建）。
- PAT：fine-grained、只授權本 repo，Actions read+write（補發）、Contents read（第 5 批寫 decisions 時改 write）。
- LLM 回答 log 格式（`data/decisions/<市場日>.json`）：`{prompt_version, model, decided_at, candidates:[{signal_id, strategy, sell_points, q_event, q_gap, q_delta, status}], raw_answer}`；事後由 tracer 回填 `outcome`，**不回寫當時答案**。

### 4.3 Dashboard「History」區要長什麼樣

就是 1.2 的矩陣，每格三個數字：`n / EV / 狀態`，加一列「策略 C 出樣本累計（T5）」。每格狀態機：`累積中(n<30)` → `可用` → `已驗證(出樣本)`。
另加一張「策略 vs 月份」小表（1.1 的逐月），讓「單月反轉」一眼可見——防止再用單月改規則。

---

## 5. 貼給 LLM 的 prompt 要怎麼調（v4 骨架，<5KB，第 4.2 步驟 3 用）

```
你是 optscnr 研究判讀員。輸入是今日「結構候選」清單（已過 DTE/IV/OTM 篩），
每張已附綁定策略與賣點。你的工作只有三題，不做可玩/跳過的最終判斷：
(a) 到期日前有無「排定」事件？答日期＋來源；答不出寫「未確認」
(b) 最近 5 個交易日有無 >8% 跳空？方向？
(c) Δ7d 是否為正、oi_delta_status 是否為 confirmed？
輸出 JSON：每張 {signal_id, a, b, c, note}；不填假機率、不編勝率。
候選為零時輸出「今日無結構候選」，不補名額。
```

拿掉：體檢卡十格、十二條淘汰物種、「其他模型不同意即跳過」、「IBIT 連續出現警覺」（資料反向）。
七月判例搬去 `docs/CASEBOOK_2026-07.md`。

---

## 6. 施工順序與驗收

| 批 | 內容 | 驗收 |
|---|---|---|
| 1（**已實作 2026-09-08**） | P0-a schema v2（`entry_bid/entry_ask/last_trade_at/quote_at`）、P0-b 路徑紀錄（`shadow_tracer.record_paths` → `path[]`）、P0-d 矩陣（`strategy_lab.compute_matrix` → `data/strategy_matrix.json` + SHADOWLOG「🧭 策略矩陣」節） | 明日 SHADOWLOG 出現矩陣節；`path[]` 開始累積 |
| 2（**已實作 2026-09-08**） | P0-c 結構候選（`strategy_lab.structural_pass`、README「🎯 結構候選」、快照 `structural_pass`、SHADOWLOG cohort 表）、P1 賣點（`strategy_lab.sell_points`）、候選 JSON（`data/dashboard/candidates_<市場日>.json` + `latest.json`） | README 出現 🎯 區塊；`data/dashboard/candidates_*.json` 每日產出 |
| 3（**已建骨架**） | `cloudflare/` 第二鬧鐘 + `/api/health` + 排程健康頁（不接 LLM）；擁有者在 CF dashboard 連 repo、設 `GITHUB_TOKEN`、（選）自訂網域 | 排程延遲 >65 分鐘時 Worker 補發；`/api/health` 看得到各 workflow 觸發時間 |
| 4（**已實作**，等第 1-2 批資料落地） | `cloudflare/public/index.html` 讀 raw `data/dashboard/latest.json` 與 `data/strategy_matrix.json`：今日候選 + History 矩陣 | 手機能開、矩陣每格顯示 n/EV/狀態 |
| 5 | Worker 接 LLM + decisions log | `data/decisions/` 每交易日一檔；T8 開始累積 |
| 6（**已實作 2026-09-08**） | P0-e：快照加 `features/warnings/events` 結構欄（`strategy_lab.split_tags`，🆕新倉暴量 → key `first_seen_in_feed`）、OI Δ7d 缺歷史→null＋`oi_delta_status`、指紋 cohort 改 feature 判定；P1 對照組：`data/universe_spots/<市場日>.json` 每日記全 universe spot，`strategy_lab.control_group_stats` 從後續日檔算 20 日漲>10% 比例（上榜 vs universe），矩陣 JSON `control` 節＋SHADOWLOG 一行 | T6 開始累積 |
| 7（**已實作 2026-09-08**，審計 bug） | tracer 回填 `err:*` 永久略過→改重試（終態只有有價/expiry_gone/strike_gone/missed_window）、回填記 `observed_at/late_days`、`today` 用市場基準日；`get_target_dates` 週五重複；快照月檔損壞→隔離不重建、原子寫入 | 回填失敗隔日自動補；週五到期日不再漏 |

---

## 7. 不做的事（重申）

- 不改計分公式、不改 -50% 停損規則、不把第一階梯改 3x——**等 T1/T9 路徑資料**。
- 不在 dashboard 做即時推播、不接券商、不追個人部位（CONTEXT 紅線 1、2）。
- 不搬 Python 到 Cloudflare（見 PROJECT_ESCAPE_DOOR.md）；Worker 只做鬧鐘、LLM 呼叫、序列化。
- 不因單月矩陣反轉改綁定（1.1 逐月表就是為了讓反轉可見而不是可用）。
