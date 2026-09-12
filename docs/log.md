# Tom Bear Scanner — 開發紀錄 (log.md)

> 跨 session 交接文件
> Repo: `github.com/clarencechien/optscnr`
> 架構：每日 GitHub Actions 自動跑的美股選擇權多雷達 scanner，產出 README 報表

---

## 系統概覽

GitHub Actions 排程驅動的選擇權異動掃描系統。主 scanner 讀多個子雷達的 JSON 輸出，整合成每日 README 報表。所有資料持久化在 `data/` 目錄（已確認被 git 追蹤，commit 正常）。

---

## 主 Scanner 版本演進 (main.py)

| 版本 | 改動 |
|---|---|
| v3.2 | 本地檔案優先讀取（修 raw.githubusercontent CDN cache 問題）；整合 enrichment（OI Δ7d + Top 5 深度卡片）；每股最多 3 條 |
| v3.3 | 整合 small_caps_momentum 清單；加 🎰動能 標籤 |
| **v3.4** | **修小盤判定 bug**（見下方 Bug 紀錄）；新增 `is_small_cap()` + `_DYNAMIC_SMALL_CAPS` 全域集合 |
| v3.5 | 整合 fallen_saas；加 💀重生 標籤 |
| v3.6 | README 末端自動附 TLT 避險雷達報告 |
| **v3.7** | 整合 unknown_radar；加 🛸盲點 標籤；連續 2+ 天的盲點標的自動進主掃描 |
| v3.8/3.9 | 四道假高分過濾（尾段價外/當沖刷量/機構場/暴動高IV）；Spot 抓取；信號快照 |
| **v3.10** | **2026-07-31 handoff 修正批**（見下方專節）：IV 硬過濾、點火低基期防爆、財報日曆標籤、主表加現價/OTM%、流動性稀薄標籤、IV term structure 月選過濾、SHADOWLOG 歸零率/去重/歸因 |
| v3.11 / 3.12 | handoff #2 殘項；TLT 併入主掃描 session（方案 A）、盤後財報價格失效標籤（見各專節） |
| **v3.13** | **市場基準日**（排程延遲跨日不標錯天、休市補跑無害）＋ 報表頭監控行（2026-09-01） |
| 3.13＋（2026-09-08 批） | schema v2 快照、🎯 結構候選（規則 B）、候選 JSON、universe spot、features/warnings/events 結構欄、OI Δ7d null 語義、🤖 LLM 三題節、📚 文件導覽行（見「策略矩陣」「審計 bug」「第 5 批」三個專節） |

**source_tag 優先序**：📰催化劑 > 💀重生 > 🛸盲點 > 🎰動能 > 🔭候選

---

## 六個雷達模組

### 1. catalyst_fetch.py (v6)
- TICKER_MAP 擴到 **146 檔**（補 VELO/FLNC/RGTI/QBTS/BKSY/LEU/MARA/CHPT；加太陽能 SEDG/ENPH/RUN/NOVA/FSLR/NXT）
- RSS 新聞 → ticker 對應，計分後輸出當日催化劑股
- 注意：啟動 print 字串一度誤寫 "v5"（已修為 v6）

### 2. small_cap_momentum.py
- 篩選：市值 $200M–$5B、過去 30 天漲幅 > 30%、日均量 > 100 萬、有期權市場
- 移除已下市的 **AGRI**（造成 yfinance 404）
- 加 verbose debug 機制 + `DEBUG_TICKERS` 集合（揪出特定標的為何被濾掉）
- **發現**：SEDG 反彈僅 25.3% < 30% 門檻 → 沒掃到（非 bug，是已漲完）；ENPH($6.16B)/FSLR($23.82B)/NXT($19.12B) 市值超過 $5B 被正確擋下

### 3. fallen_saas.py
- 抓 FIG 級「殞落軟體股重生」：從 52 週高跌 55%+、從低點反彈 3–35%（早期）、量能 +20%+、市值 $1B–$500B、有期權
- ~55 檔候選池（設計/開發者工具/CRM/視訊/AI 應用/Fintech）

### 4. tlt_radar.py (v2.5)
- TLT 避險「溫度計」0–100 分（Put 巨鯨 + IV Skew + OI 週累積三訊號合成）
- **v2 修 bug**：原本 `tk.options[:6]` 全抓到週選近月 → IV term structure 失真（ATM Call IV 出現 1.2% 等垃圾值）。改智慧 DTE 選擇 `[30,60,90,180,240,365,500]`
- 加 IV 5%–200% 過濾 + OI≥50 要求（濾 stale quote）
- 週更（v2.5 起併入主掃描 session，每 ISO 週第一次成功抓取）

### 5. unknown_radar.py (v1.3) — 「擦鞋童雷達」
- 目標：抓「新聞反覆出現但不在我字典裡」的標的（認知盲點）
- 流程：RSS 抽大寫公司名 → 過濾 KNOWN_TICKERS(251 檔) + COMMON_WORDS(390 詞，含國家/姓氏/術語) → 對照 SEC 上市清單找 ticker → 累積連續天數
- **SEC 403 修法**：User-Agent 須含真實識別資訊（不能用瀏覽器 UA 假冒）；加 NASDAQ Trader 備援來源
- 連續 2+ 天出現 = 強訊號，ticker 自動進主掃描
- 雜訊清理是迭代式的：第一版抓到 Here/Iran/Singapore/Chinese 等誤判，逐步加進 COMMON_WORDS

### 6. space_radar.py (v8.8) — SPCX（已上市，檔案在 spcx_radar/）
最複雜的模組，多次迭代。核心設計：

**資金編制（60/30/10，硬上限 $200k）**
- A 核心 DCA 60% / $120k：依市值估值錨分批建倉（6/12→~7/3 分 5 筆 × $24k）
- B 地板預備 30% / $60k：GTC 掛 1.5T/1.3T/1.1T，承接鎖倉瀑布，掛到 12 月中
- C 機動/選擇權 10% / $20k：IV 崩後才動 LEAPS

**市值定錨（取代 VWAP）**
- B 池掛單用「絕對市值反推價格」，與開盤價無關
- 公式：價格 = 市值(兆) × 1000 / 總股數(十億)
- 以 13.0B 股計：1.5T=$115.38、1.3T=$100、1.1T=$84.62、IPO 1.75T≈$135、斷路器 2.2T≈$169

**階段機**
- 階段 0（未上市）→ 1（上市無選擇權）→ 2（IV 狂熱）→ 3（IV 冷卻可評估）

**四個修正**
1. 市值定錨（拔 VWAP）
2. 2.2T 斷路器（市值破頂禁止新資金）
3. Gamma Squeeze 預警（PC ratio < 0.2，含 Put 流動性防呆）
4. 論點破壞檢查清單（Starship/Starlink/指數納入/關聯交易）

**時間軸功能**
- 綠鞋撤除提醒（第 30 天，投行撐盤消失）
- 鎖倉瀑布事件（70/90/105/120/135/180 天，隨上市日平移）

**可變參數全抽到 `data/spcx_config.json`**
- 改 `ipo_date` 一行 → 所有天數自動平移
- 改 `total_shares_b` → 所有價格自動重算
- 讀不到 config 用內建預設（三層防呆）

---

## Bug 紀錄（重要，避免重蹈覆轍）

### Bug 1：小盤判定（main v3.4 修）
動態進來的標的（catalyst/auto_watch/small_caps_momentum）若不在 BIG_CAPS list，被當大盤套用 OI≥5000/VOL≥2500 高門檻，導致 VELO/AEHR 整個被濾掉。
修法：`is_small_cap()` 動態判定 + `_DYNAMIC_SMALL_CAPS` 集合。

### Bug 2：SPCX 股數單位（space_radar 修）
`TOTAL_SHARES_B` 一度寫 130（= 1300 億股，算出 $13.46），應為 **13.0**（= 130 億股，算出 $134.62）。
病因：中文「億」vs 英文「Billion」混淆。
**這是最危險的一類 bug——程式不報錯，默默全錯一個數量級**。靠「股價應是 134 上下」的市場直覺抓到。

### Bug 3：假 SPCX（space_radar 修）
IPO 前 SPCX 代號被一檔同名舊 ETF（SPAC and New Issue ETF，已改名 SPCK）佔用，yfinance 殘留報價 $22。
修法：日期防呆（< IPO 日強制階段 0）+ 公司名驗證（longName 須含 spacex/space exploration）。

### Bug 4：GitHub Actions「No changes」commit 失敗（重要）
病因：`git add` 一次列多個檔案，其中含階段性「不存在的檔案」（如 spcx_iv_history.csv 在階段 0 不存在），git 整條 fatal，被 `2>/dev/null || true` 吞掉 → 跳到 "No changes"。
修法：**逐檔 `[ -f "$f" ] && git add "$f"`**，存在才 add。
教訓：不要用 `|| true` 吞錯誤；debug 時加 echo 逐步驟印出真相。

### Bug 5：tlt_radar 週選擠壓（v2 修）
`tk.options[:6]` 對有週選的標的會全抓到 1–4 週近月，IV term structure 失真。
修法：智慧 DTE 選擇 + IV/OI 過濾。

---

## GitHub Actions 排程（UTC，台灣 = UTC+8；2026-09-01 更新）

| 雷達 | cron (UTC) | 台灣時間 | 備註 |
|---|---|---|---|
| catalyst_fetch | `37 20 * * 0-5` | 週一~六 04:37 | 餵 scanner |
| unknown_radar | `43 21 * * 0-5` | 週一~六 05:43 | 餵 scanner |
| main scanner | `17 22 * * 1-5` | **週二~六 06:17** | 掃前一晚美股收盤；台灣週一早上「不跑」是設計（美股無新資料） |
| space_radar + sage | `26 22 * * 1-5` | 週二~六 06:26 | v8.8 起排除 UTC 週日（週末殘留曾污染 IV 歷史） |
| tlt_radar | 無 cron | 跟主掃描 | v2.5 起併入主掃描 session，每 ISO 週第一次成功即跳過；yml 只留手動 |
| delta_radar | `41 2 * * *` / `47 3 * * 1,4` / `53 4 10-12 * *` | 每日 10:41 / 一四 11:47 / 10-12 日 12:53 | schedule 路由字串與 cron 同步 |
| tw_scanner | `52 13 * * 1-5` / `58 14 1 * *` | 週一~五 21:52 / 每月 1 日 22:58 | 融資 21:00 公布後 |
| small_cap_momentum | `13 0 * * 6` | 週六 08:13 | |
| fallen_saas | `19 1 * * 6` | 週六 09:19 | |
| universe_update | `9 23 * * 6` | 週日 07:09 | |
| **Cloudflare Worker**（`cloudflare/wrangler.toml`） | `5 23 * * 1-5` / `35 0 * * 2-6` / `5 2 * * 2-6` | 週二~六 07:05 / 08:35 / 10:05 | 每發都做：①第二鬧鐘（22:00 UTC 後 scanner 沒 run → `workflow_dispatch`）②decisions（`latest.json` 有新市場日且無 `data/decisions/<日>.json` → LLM 三題）。週末不補發 |

- **分鐘全部避開 :00/:15/:30/:45**——GitHub 排程在熱門分鐘最容易延遲/丟棄
  （2026-08-26~31 事故：全 repo 延遲 3-8 小時、8/31 直接沒發，見 3.13 專節）。
- 排程延遲的自我防護：主 scanner 用「市場基準日」補跑（v3.13）、
  spcx 用 market_freshness()（v8.8）——延遲跨日不再標錯天或誤殺。
- **2026-09 觀察**：GitHub 的 22:17 排程實際上每天在 00:09–00:20 UTC 才發（穩定晚 2 小時）；
  Worker 23:05 那發會先補發，之後遲到的排程 run 再跑一次是無害的重播（市場基準日＋signal_id 去重）。
  delta_radar 每日 02:41 那發也常晚 4–5 小時，未納入第二鬧鐘（只更新敘事，不急）。
- 週末雷達刻意錯開，避免同時搶 RSS / API。

---

## 設計原則（跨 session 要保留的判斷）

1. **雷達掃到 ≠ 進場訊號**。Scanner 是過濾雜訊的工具，不是選股權威。歷史最賺的部位（JOBY/SMCI/NVDA/HOOD/MSFT 皆翻倍）來自自己判斷 + free ride 紀律（+100% 賣一半、剩下免費遊戲），不是 scanner 選的。
2. **不是所有 docs 都該變 code**。Firstrade 無配額、7/6 指數買盤、TSLA 集中度 → 留人腦紀律。寫進 code 反而誘惑盯錯東西。
3. **用市場直覺檢查數字**。數字跟認知對不上時，通常是數字錯不是你錯。$13.5 vs $135 單位 bug 是直覺抓到的，不是程式報錯。
4. **DCA 池不給買賣訊號**，只做儀表板（成本線 + 均線）。力量來自機械化，不是判斷。
5. **市值定錨 > VWAP**。不賭隨機開盤價，定錨在「我認為值多少」。
6. **動腦只有 6/11 一天**（SPCX）。定價後改 config，6/12 之後是執行不是判斷——判斷在情緒最高時做一定錯。

---

## SPCX 待辦（6/11 定價日）

打開 `data/spcx_config.json` 改：
- `ipo_date`（若延期）
- `total_shares_b`（用 S-1 最終流通股數核對）

可重新考慮（thesis 層級，非必改）：
- `b_pool_anchors_t` 最高檔要不要從 1.5T 拉到 1.7T（避免 SPCX 暴漲時 40% B 池完全踏空）
- `hard_cap_t` 停手線

**S-1 已確認事實**：5 拆 1（5/4 完成）、Musk 366 天鎖倉（巨鯨不倒貨）、其餘 180 天解鎖瀑布、持 18,712 顆 BTC（EPS 受幣價放大波動）、Goldman 主辦、Firstrade 不在散戶通路名單（須開盤後二級市場買）、代號 SPCX、xAI 已併入 SpaceX。

**仍待 6/11 定案**：每股 IPO 價、發行張數/free float、綠鞋%、散戶保留%。

---

## Scanner 3.10 修正批（2026-07-31）

依據 7/7–7/30 共 17 份每日報表判讀累積的工具問題（SCANNER_HANDOFF_20260731.md），
四批一次做完。**計分權重不動**（維持 7/6 改卷決策），所有新資訊都以標籤/欄位形式加入。

### 第一批：止血
- **tlt_radar v2.2（P0-1 nan 綠燈事故）**：7/27 抓取失敗 → `current_price=nan` →
  三分項全 0 → 輸出「0/100 🟢平靜」，與實際市況（油價破 $100、10Y 創高）完全相反，
  瞎了一整週。修法：nan/失敗防呆（任一關鍵值異常一律當失敗）＋ retry 3 次指數退避 ＋
  仍失敗改寫「⚠️ 無資料」報告（附上次成功讀數與 TLT 現價/10Y fallback，不輸出溫度燈號）＋
  成功報告標「擷取於 X 日，下次更新 X+7」（週更讀數被誤讀為連續確認的問題）。
- **main P1-2 IV 硬過濾**：IV <=1% 或 >300% 直接剔除（F 4.82C IV 0.0% 曾連五日拿 8 分進 TL;DR）。
- **main P1-3 點火倍數防爆**：前日 Vol<20 不算倍數改標 `🆕低基期`不加分（OKLO 200C 曾顯示
  16944.7x）；倍數顯示封頂 `>50x`。

### 第二批：財報日曆（效益最大）
- **P0-2 價格已失效**：掃描 23:0X UTC 用的是 16:00 ET 收盤快照，盤後開牌財報股的權利金
  是死價格（7/28 F、7/29 SOFI/META、7/30 RIVN 三次應驗）。財報今日→`⚠️價格已失效`、
  明日→`⚠️價格恐失效`。**只標記不排除**（handoff「不建議現在改的」#4：財報後形狀有資訊）。
- **P2-2 物種閘門自動化**：每列標 `📅覆蓋財報`（二元票）/`📅財報已過`（14 天內，災後賭局）/
  `📅吃不到財報`（純動能）。資料源 yfinance `get_earnings_dates`，per-symbol cache，失敗降級不標。

### 第三批：表格欄位
- **P2-1**：主表加 `現價`+`OTM%` 欄（7/13 HOOD 200C 拿全表最高 9 分實為 82% OTM，之前只能反推）。
- **P2-3**：合約數<10 或標的總 OI<10k → `⚠️流動性稀薄(N條/OI X)`（CNP 45C 9 分事件；
  數字深度卡本來就有，只是沒進主表）。
- **P1-1 IV 峰值假陽性**：enrichment IV term structure 只用月選（第三個週五，遇假日週四）＋
  ATM 要求 OI>=50 ＋ IV 5-200% 過濾——與 Bug 5（tlt v2 週選擠壓）同型 bug，同一套修法。
  文案改「（未驗證，須人工查證財報/事件日曆）」（7/29 T、7/30 PYPL 同在 2026-08-28 週選出假峰值）。

### 第四批：SHADOWLOG 校準
- **P3-1 存活者偏差**：加`歸零率`（峰<0.2x）＋`期望值`（階梯出場模擬：峰≥2x 賣半、餘以末檢查點
  出場）；DTE 分層判讀改以期望值為準（命中率六月 60% vs 七月 0% 測的是市場環境不是 DTE）。
- **P3-2 樣本不獨立**：加「標的-日去重命中率」為主指標（271 筆實際約 30-40 個獨立事件；
  T 20C/21C/30C 是同一次擲骰）。
- **P3-3 歸因欄**：快照 schema 加 `signal_day_underlying_move`/`why_it_popped`（人工回填 JSON，
  區塊三顯示）。逆勢佈局假說樣本 3 筆，30+ 前不得據此改規則。

### 保留判斷（避免將來被說服，出自 handoff）
不放寬樂透 size 上限、不放寬絞肉區（DTE<21）閘門、不因單月命中率改規則、
盤後開牌標的只標記不自動排除。

## 第 5 批：Worker 接 LLM decisions + 事實庫活用 + dashboard 改版（2026-09-08，第三批）

- **cloudflare/src/index.js**：每發 cron 都跑「第二鬧鐘 → decisions」。decisions 冪等：讀 main 的
  `latest.json` → `data/decisions/<市場日>.json` 已存在就跳過；候選 0 筆不呼叫 LLM 直接記檔；否則
  prompt（`docs/PROMPT_daily_report_reading_v4.md` 的 ```prompt 區塊，**改 prompt 不用重部署**）＋候選＋
  事實庫 → OpenRouter（OpenAI 相容，預設 `anthropic/claude-opus-5`，web 外掛給第 (a) 題找來源）→ GitHub
  Contents API 建檔。LLM 失敗也留檔（T8 分母）。新端點 `POST /api/decide`、`/api/decisions`、`/api/facts`。
  cron 加 02:05 UTC 第三發（補發的 scanner 跑完後補 decisions）。週末第二鬧鐘不補發（休市重播）。
- **Cloudflare Access（選用）**：設 `ACCESS_TEAM_DOMAIN` + `ACCESS_AUD` 後 Worker 驗每個請求的 JWT
  （RS256、aud、exp；certs 快取 1 小時）。Access policy 設錯時 `/api/decide` 這種會花錢的端點仍 401。
- **事實庫活用（擁有者當日要求）**：`docs/FACTS_ledger.md` 重整（只搬不改字，字數核對 29,109 相同）：
  合併重複段、「其他」段逐條歸位、標的段依代號排序、檔頭寫機器可讀規則、尾端加「待審（LLM 提案）」段。
  Worker `parseLedger()` 把候選標的段＋通用段（環境/判決/校準/工具）最新 5 條帶進 payload.facts；
  prompt v4.1 加「事實庫優先／衝突標記」；LLM 回 `facts_proposed`（必附 URL）→ Worker 附加到待審段
  （同來源去重、sha 衝突重試 3 次）。人審過後搬到該標的段落。
- **PAT 權限變更**：`GITHUB_TOKEN` 要 Contents **read+write**（寫 decisions 與 ledger 待審段）。
- **shadow_tracer.backfill_decisions**：對每個 decisions 檔逐筆補 `outcome`（T+5/10/20 倍數、peak、mature、
  verdict；只補空的或未成熟的，不動答案）；彙整 `data/dashboard/decisions_log.json` 含 T8 摘要
  （事件答「有／無／未確認」各自的成熟命中率）。scanner.yml commit 加 `data/decisions/*.json`。
- **main.py**：候選 JSON 加 `oi_delta_status/features/warnings/events/recent_spots`（近 6 日 universe 收盤，
  第 (b) 題用，跳空＝日對日 >8% 近似）；README 加「🤖 LLM 三題」節（前一市場日的答案）——**雙軌**：
  軌 A README（Python 渲染，CF 掛了也在）、軌 B CF dashboard（加 History/Decisions/事實庫/排程）。
- **dashboard 改版**：dataviz 調色盤 tokens（淺/深各自選色）、四個 stat tile、五個分頁、EV 長條圖
  （最佳政策藍、其餘灰、1.0x 紅線）、候選表附 LLM 三題與事實庫條數、Decisions 逐日展開含 outcome、
  事實庫可搜尋、排程頁台北時間。用 Playwright 對 mock 資料截圖核對三種尺寸/深淺。
- **docs**：`PROMPT_daily_report_reading_v4.md`（機器用短版）、`CASEBOOK_2026-07.md`（判例從 v3 搬出）、
  v3 檔頭加分工說明。
- 模型費用估算：Opus 5 每交易日 ≈ US$0.05–0.15（候選 0 筆時零）；`model_served` 入檔，T8 可分模型比。
- 未做：LLM 三題答對率的人工抽查機制（先累積 20 個交易日再設計）；ledger 待審段的「一鍵入庫」（刻意不做，入庫要人審）。

### 同日下午：上線驗證與修補

- **首次實跑（擁有者手動 Run workflow，09-07 06:26 UTC，市場日 9/4 休市補跑）**：README 出現 🎯 區塊、
  `data/dashboard/latest.json`、`data/strategy_matrix.json`（成熟 579/1099）、`data/universe_spots/2026-09-04.json` 都落地；
  dashboard 按「立即產生」→ `data/decisions/2026-09-04.json`（0 候選、未呼叫 LLM、note 正確）；待審段空。
- **零候選核對**：Score≥8 非末日 24 張 → DTE 21–120 剩 10 → IV<50 剩 3（F 16C、TJX 140C、GOOGL 410C）→ Δ7d>0 全滅：
  F/TJX 在 8/31 歷史 CSV 裡沒有（🆕 first_seen_in_feed → Δ7d null，P0-e 語義下不算 confirmed）；
  GOOGL 33,204 vs 33,779 ＝ −575。**是真的零，不是 bug**；也證實規則 B 對「首次出現」合約是排除的，之後矩陣回答對不對。
- **dashboard 修補**：排程健康視窗 36→84 小時（週一下午不把週末正常沒跑的標紅）；對照組無資料時顯示「累積中」而非 `null pp`；
  候選 tile 的分母改「掃描 N 張」（`n_report_rows` 是進報表的合約數）。
- **Access 上線的坑**：靜態頁由 Cloudflare 先供檔不經 Worker，Access 變數設好前後會出現「頁面開得了、/api 全 401」。
  Worker 的 401 改回 JSON `reason/hint`（no_token／aud_mismatch／certs_fetch_failed／kid_not_found／expired），
  頁面頂端顯示紅色說明條；`ACCESS_TEAM_DOMAIN` 自動去掉 `https://`。
- **本 session 無法做的**：從沙盒打不到 dashboard（Cloudflare Challenge/Access）、也無 `workflow_dispatch` 權限，
  實跑與按鈕都由擁有者操作，我從 git 核對產物。
- **電子報 `/brief`（擁有者晚間要求「一眼看懂、可分享、不觸發 LLM」）**：`public/brief.html` 一頁式（TL;DR、規則 B 說明、
  候選卡片＋三題答案、History 摘要條、資料正確性檢查清單、前後日導覽）；`/api/brief?d=` 由 Worker 彙整候選／decisions／矩陣／
  排程狀態，`caches.default` 快取 5 分鐘，回傳去掉 `raw_answer`。Worker 對 `/brief`、`/brief.html`、`/api/brief` 不驗 JWT；
  Cloudflare Access 那層要另建 Bypass 應用程式放行這兩個 path（步驟在 cloudflare/README.md）。dashboard 分頁列加「電子報 ↗」。
  tracer 路徑紀錄改成到期日當天不抓鏈（yfinance 對已到期 expiry 必 ValueError）。

## 審計 bug 修復 + P0-e 語義 + P1 對照組（2026-09-08，第二批）

- **shadow_tracer 回填 bug**：`err:*` 失敗結果一存進去就被當「已填」永久略過（註解寫「明天再補」）。
  改：終態只有有價 / expiry_gone / strike_gone / missed_window；err 隔日重試，逾 10 天仍失敗才標
  missed_window。回填加 `observed_at`/`late_days`（逾期幾天才抓到，分析可過濾）；today 用市場基準日。
- **get_target_dates 週五重複**：`(4-wd+7i)%7` 對 i=0、1 同值 → 下週非月選到期日一直漏掃。改 `(4-wd)%7 + 7i`。
- **快照月檔損壞保護**：舊碼讀失敗 `existing=[]` 會從空歷史重建（append-only 失效）。改：隔離為
  `.corrupt-<ts>`、明確 raise、不寫；寫入改原子（tmp + replace），tracer 同。
- **P0-e**：快照加 `features/warnings/events`（`strategy_lab.split_tags`），🆕新倉暴量 的 key 是
  `first_seen_in_feed`（真實語義：昨天篩選表沒它，不是新開倉）；指紋 cohort 改用 feature 集合判定，
  顯示文字加財報/價格註記不再破壞 membership；enrichment OI Δ7d 缺歷史 → None + `OI_d7_status`
  （八月 376 筆有 206 筆 oi_d7==oi 是舊語義灌出來的）；structural_pass 因此對缺歷史合約為 False（誠實）。
- **P1 對照組（tracker T6）**：main 每日寫 `data/universe_spots/<市場日>.json`（掃描 universe 全部 spot），
  `control_group_stats` 從後續日檔算 20 日漲>10% 比例：上榜組 vs universe；進 `strategy_matrix.json`
  `control` 節與 SHADOWLOG。判準：差 <5 百分點（≥100 上榜標的-日）→ 選標的無 edge。
- **REVIEW_2026-07 補記**：tw_scanner 7/30 警報已入 9/1 月度回測（n=8、20 日中位 +8.72% vs 基線 +2.17%）；
  delta 背離旗標仍未做（10 月中前要）。

## 台股側第 6 批：週報／DCA 影子帳本／賭場 sector／tsmc_radar／電子報改版（2026-09-11～12）

> **給接手 session：動新功能前先 `git log --oneline -40`，再看本節與 CONTEXT §十。** 這批由 ai_radar 那邊的
> session 跨 repo 做的，PR #30–#34 合併；台股側從「兩支雷達的日報」變成「週報＋影子帳本＋論點監控×2＋賭場記帳」。

### 為什麼
tw_scanner 唯一可行動的輸出是投降警報，一年響幾次；對 DCA 0050 的人，日報 250 天都是「無」。delta_radar 作為訊號零價值
（103 筆回填超額為負），REVIEW_2026-07 的背離旗標拖了兩個月沒做。改成「週報＋規則影子帳本」，用使用者的錢當單位回答
「訊號值多少」；並補齊儀器。

### 改了什麼（依 commit）
| commit | 內容 |
|---|---|
| `6d12c1c` (#30) | **dca_ledger.py**（DCA 規則影子帳本：純 DCA／週檢查月預算／投降窗加碼／鋒面調節／一次投入對照；平均成本、XIRR、每筆加碼 edge）、**tw_brief.py**（週報 `tw_brief.json`＋`tw_weekly.md`）、tw_scanner.py 導出 `tw_scanner_history.json`（2019 起全序列）與 `tw_scanner_backtest.json`、delta_radar **背離旗標**＋**退役判準表**、workflows 接線、Worker `/api/tw` |
| `4be2780` (#31) | 電子報同一頁切換：`/brief?m=tw` 只呈現台股；`/tw` 轉址；dashboard 導覽 |
| `134ca0c` (#31) | **casino_tracker.py**（賭場 sector：16 檔台股 AI 個股影子追蹤，只收資料；T+N 對 0050 超額；影子等權 DCA 對 0050；判準寫死） |
| `f71b117` (#32) | 電子報 RWD：上半一分鐘白話版、下半 `<details>` 可收合、表格 `.scroll`、≤640px 調整 |
| `edd5fcf` (#32) | **splits.py 分割還原**：首跑實測 0050 2025-06-18 四拆一、6669 2026-09-02 三拆一未還原，帳本全錯（純 DCA 七年 +0.75% → 修後 +230%）；config override/ignore；state 衍生欄位修復 |
| `107f97e` (#33) | 2308 儀器修正：M8 樣本不足改 NO_DATA、退役判準加狀態翻轉數（`min_flips`）、M9 估值分位（觀察）；**tsmc_radar**（2330）：delta_radar.py instance 化（`name/display/modules_full/m3_mode`）、M3 ADR 溢價、M7 第二基準 SMH、config placeholder |
| 本 commit (#34) | M4 HS 碼改 6 位（4 位對 HS6 回空）、M6 標題 ticker 化、文件全層更新（本節、CONTEXT §十、MANUAL_tw_scanner 家族結構、README 📚 行） |
| 本 commit | **publish.sh**：三個 workflow 的 commit 步驟抽成共用腳本（tsmc-radar #1 attempt 2 實測 `pull --rebase --autostash` 對衍生檔衝突 exit 128） |

### 檔案地圖（tw_scanner/）
```
tw_scanner.py        天氣台（＋history.json／backtest.json 導出）        config/tw_scanner_config.json
delta_radar.py       論點監控引擎（2308 與 2330 共用）                   config/delta_radar_config.json、config/tsmc_radar_config.json
dca_ledger.py        DCA 規則影子帳本                                     config/dca_ledger_config.json
casino_tracker.py    賭場 sector 影子追蹤                                 config/casino_config.json
splits.py            分割還原（共用）
tw_brief.py          週報組裝（零網路）→ output/tw_brief.json、tw_weekly.md
build_readme.py      README = 週報＋簡報＋delta＋tsmc＋帳本＋賭場＋回測
publish.sh           三個 workflow 共用的 commit＋push（主輸出先 commit → pull --rebase → 重產生衍生檔 → push，重試 3 次）
MANUAL_tw_scanner.md / MANUAL_delta_radar.md / MANUAL_dca_ledger.md（含賭場）/ REVIEW_2026-07.md（覆核紀錄一路補記）
```
排程：`tw_scanner.yml`（平日 21:52 台北；簡報後接 ledger → casino → brief）、`delta_radar.yml`、`tsmc_radar.yml`（與台達錯開 30 分鐘；跑完重組 brief）。
Worker：`/brief?m=tw`、`/api/tw`（公開唯讀；Zero Trust Bypass 已加 `/tw`、`/api/tw`）。

### 首跑實測（2026-09-12）與待辦
- tw-scanner #76：帳本數字太平 → 追出分割未還原（見 edd5fcf）。**教訓入 CONTEXT §六第四例：新資料源首跑先看序列斷層。**
- tsmc-radar #1：總判定 YELLOW。M1 +53% GREEN、M2 GREEN（合約負債科目未匹配 → n/a）、M3 ADR 溢價 +13.7%（1 年第 19 分位）、
  M4 NO_DATA（HS 碼，本批修）、**M5 RED（placeholder 門檻：export_controls 16 則 > red 15）**、M6 GREEN、M8 NO_DATA、M9 PER 27.9（3 年第 72 分位）。
- **待校準（人做）**：tsmc config 各段 `_calibrate`——M1/M2/M4/M5 門檻對照真資料；M2 跑 `--dump-accounts --config config/tsmc_radar_config.json` 找台積合約負債科目名；
  M5 跑 5 次後 z-score 基準接手、RED 會自己退。校準前只看方向不看燈色。
- casino `in_0050` 是人工標記，季調要對。
- delta 下次全模組 run（週一）背離旗標會第一次亮（前提 YELLOW、價格 20 日 −14%）。
- **n≥30 之後才開的實驗**（REVIEW_2026-07.md 末節「樣本 n≥30 之後可加的方向」）：燈色×20 日價格交叉表（驗「綠燈沒漲＝先行指標」假說）、
  硬資料／敘事模組分開算退役、M3/M9 觀察模組轉正條件、賭場停增規則候選。下次覆核（delta 10/31、tsmc 12/31）看；之前不加功能、不調門檻。
- 判準（都寫死了，別捨不得）：DCA 投降窗規則 ≥8 簇 edge>0 且勝率 ≥60%；鋒面調節不優於純 DCA → 處決；賭場籃子 ≥12 個月、
  三分位每側 n≥30；delta 10/31 覆核、tsmc 12/31 覆核；退役判準狀態翻轉 <3 次一律無法判定。

### publish.sh：三個 workflow 共用的 commit 步驟（2026-09-12 第二次事故）
病因：tsmc-radar run #1 attempt 2 是 **re-run 舊 attempt**（checkout 的是 501806e，main 已前進到含 attempt 1 輸出的版本）。
舊步驟 `git pull --rebase --autostash` 把本地改動 stash 再套回 → README／tw_brief／tw_weekly／tsmc report+state 全衝突 → exit 128。
根本原因不是 re-run 本身，是三個 workflow 都重寫同一批「衍生檔」（README.md、tw_brief.json、tw_weekly.md），
只要 main 在跑的期間前進（tw-scanner 與 tsmc-radar 同一晚跑）就會撞。
修法（`tw_scanner/publish.sh`，三個 workflow 的 Commit results 都只剩一行呼叫）：
1. 只 `git add` 自己的**主輸出**（逐檔存在性檢查，缺就 `::error` 失敗，不吞）；衍生檔先還原成 main 的版本。
2. 重產生衍生檔（零網路、state 的純函數）併入同一 commit；`pull --rebase`；
   衍生檔衝突 → 當場重產生當作解法繼續 rebase；push 被搶先 → 重來，最多 3 次。
3. **主輸出**衝突 = main 已有本次輸出（re-run 舊 attempt）→ `::warning` 後放棄本次 commit、exit 0（資料已在 main，不是雷達的錯）。
本機 sandbox 模擬過五種情況（正常／並發衍生檔衝突／舊 attempt／無變化／主輸出缺檔）。
規矩：**要重跑請用 Run workflow 新發，不要 re-run 舊 attempt。**

### 紅線對照
- 紅線 2（不做 portfolio）：影子帳本＝等額假設規則帳，不記真實部位與個人損益；個人曝險一律不進本 repo（公開）。
- 紅線 3（不調門檻）：本批零閾值變動；新 config 的 placeholder 是「尚未校準」不是「調過」。
- 紅線 5（不重構）：一切平鋪在 tw_scanner/，10 個 workflows 未動路徑。

## 策略矩陣 shadow + 結構候選 + dashboard 資料層（2026-09-08，PLAN_2026-09_strategy_dashboard.md 第 1、2、4 批）

- **strategy_lab.py（新）**：預先登記的分類邊界（$1.5/$3、DTE 20/45/120、IV 50）、三策略
  A 死抱 / B 2x賣半 / C 分類綁定、規則 B `structural_pass`、賣點換算、`compute_matrix()`。純計算零網路。
- **main.py**：schema v2——`Ask` 欄仍是 lastPrice（歷史相容），另存 `Bid/AskReal/LastTradeAt` 進 CSV，
  快照加 `entry_bid/entry_ask/last_trade_at/quote_at/underlying_at`；`structural_pass/strategy/sell_points/path`；
  README 新增「🎯 結構候選」區塊（DTE 21-45 優先）；輸出 `data/dashboard/candidates_<市場日>.json` + `latest.json`
- **shadow_tracer.py**：`record_paths()` 每日對未到期高分信號 append `{date,last,bid,ask,spot,iv}`（同 (ticker,expiry)
  一鏈、同日不重複、市場基準日標籤）；T+N 回填加 bid/ask；每天重算全月份矩陣 → `data/strategy_matrix.json`；
  SHADOWLOG 新增「🎯 結構候選 vs 其他」cohort 表與「🧭 策略矩陣」節
- **scanner.yml** commit 清單加 `data/dashboard/*.json data/strategy_matrix.json`
- **cloudflare/public/index.html** 讀 raw JSON 渲染今日候選與 History 矩陣
- 數字對齊：規則 B 含 Δ7d>0 後 111 筆（非 118），A/B/C = 1.77/1.47/1.81（方向不變）
- 不動的：計分、停損規則、任何門檻——100 筆出樣本前不改（預先登記 2026-09-08）

## Scanner 3.13 — 市場基準日 + 排程延遲事故（2026-09-01）

### 事故（光看 GitHub Actions 就能定位）
8/26 起 GitHub schedule 全 repo 延遲 3-8 小時甚至丟棄（scanner 與 unknown_radar
同模式 → 平台端問題非程式問題）：
- 8/27 的 run 延到 ET 凌晨 01:10 → 休市防呆把平日當假日誤殺，**整天沒掃**
- 8/28 的盤延到 UTC 週六 03:43 才跑 → csv 標成 2026-08-29、**97 筆信號 snapshot_date=週六**
- 8/31 排程完全沒發 → 擁有者手動補跑（又標成 9/1）
教訓：防污染設計擋了「休市日跑」，沒防「延遲跑但日期標錯」——同一個洞的另一面。

### 修正
1. **cron 全面錯峰**：避開 :00/:15/:30/:45（GitHub 熱門分鐘最容易延遲/丟棄），
   餵食順序保持：catalyst 20:37 → unknown 21:43 → scanner 22:17 → space 22:26；
   delta/tw/週末雷達同步錯開（delta/tw 的 schedule 路由字串一併更新）
2. **市場基準日（v3.13 核心）**：= SPY 最後交易日。CSV 檔名、snapshot_date、
   財報時態、環境序列全部改用它，不用 runner 時鐘。resolve_market_date() 三態：
   normal / **catchup 補跑**（延遲跨日、ET 未開盤 → 照掃、標正確交易日，
   signal_id 天然去重）/ closed。延遲的 run 從「毒藥」變「無害補跑」
3. **監控行**：報表頭「市場基準日 + 掃描執行於 + ⏰補跑標記」，延遲一眼可見
4. **資料清理**：快照重標 8/27→8/26（7 筆，t5 已回填保留）、8/29→8/28（97 筆）、
   9/1→8/31（16 筆，移回 8 月檔、刪空的 9 月檔）；csv 改名同步；環境序列日期修正。
   定性：標籤錯誤修正，非竄改預測內容（append-only 紅線精神不變）

### 補充修正（同日第二批）
- **docs/log.md 排程表更新**：舊表還寫著 `0 22`/tlt 週六 cron 等已不存在的排程，
  已換成現行 cron 全表＋台灣時間對照＋「台灣週一早上不跑是設計」註記
- **space_radar v8.8 / sage v0.3 週末殘留**：原 cron 含 UTC 週日（台灣週一早上），
  每週把週五收盤殘留再寫一列進歷史（iv_history 66 列中 13 列、options_history
  50 列中 9 列是週末重複值，IV 分位樣本被灌 20%）。修：cron 改 1-5 ＋
  spcx_common.market_freshness() 防呆（假日也擋、延遲跨日以最後交易日補跑）＋
  記錄日期改用市場交易日；兩份歷史的週末列已清除（53/41 列）

### 補充修正（2026-09-02：push 競態）
排程延遲的第二種傷害：多個 workflow 被擠到同一時段跑，scanner 掃完 9 分鐘要 push 時
別的 workflow 已先 push → non-fast-forward 被拒 → **整次掃描結果隨 runner 銷毀**
（9/2 台灣早上事故；那次 log 同時證明 3.13 正確：延遲 run 仍標市場基準日 9/1）。
修：8 支沒有 `git pull --rebase` 的 workflow（scanner/catalyst/unknown/space/tlt/
small_cap/fallen/universe）push 前一律 `pull --rebase --autostash` ＋ 3 次重試，
三次皆失敗才大聲失敗（delta/tw 原本就有）。各 workflow 寫的檔案互不重疊，rebase 不衝突。

### 逃生門
docs/PROJECT_ESCAPE_DOOR.md：Cloudflare 遷移評估（R2/觀看層/Python 三問直答）。
結論：**現在不搬**——五項 GitHub 依賴只壞排程一項；Phase 1 備援=CF Worker 當
「第二個鬧鐘」（查當日 run 缺席就 workflow_dispatch），觸發條件寫死在文件裡。

## Scanner 3.12 + tlt_radar v2.5 — PATCH #2（2026-08-05）

三個問題：一個新缺陷、一個「偵測到但沒修好」的根因、一個時間標示錯誤。

### P0-3 📅 標籤靜默缺漏（新缺陷）
8/4 PFE 盤前雙 beat 開牌、KTOS 兩檔——完全沒有 📅 標籤。缺漏比誤標危險：
誤標看得到，缺漏被讀成「這格沒資訊」，而 PFE 26.5C 正好是當日唯一三格全過的票。
修法：
- get_earnings_window 回傳 kind（ok/etf/unknown）：ETF → `📅無財報(ETF)`、
  個股抓不到（含下次未排定）→ `📅財報日未知`——兩種「沒標籤」視覺可分
- 報表頭加「📅 標籤覆蓋率：X 筆中 Y 筆有財報日（Z 未知、W ETF）」——缺漏率變可監控
- 缺漏時 log 原始回傳（型別/長度/exception）到 data/earnings_fetch_misses.log

### P0-4 TLT 鏈抓取根因（方案 A + C）
v2.4 偵測層運作正常，但三次嘗試失敗兩次（8/3、8/4 鏈空）——失敗可見了，沒修好。
關鍵線索：主掃描 23:0X UTC 同日抓上百檔鏈全成功，TLT 獨立排程跑在 04:58 UTC
（美股收盤後 9 小時）→ 問題在時段不在標的。
- 方案 A：TLT 併入主掃描 session（main.py 呼叫 tlt_radar.main()，本週已成功
  即跳過），tlt_radar.yml 排程移除、只留手動觸發；**regime 維持週更**，
  只換執行時段；scanner.yml 一併 commit TLT 產出
- 方案 C：鏈抓取失敗記診斷 log（expiry list 長度、逐到期日 exception）到
  data/tlt_fetch_errors.log——沒有這個下次還是只能猜

### P1-4 時間標示
8/4 04:58 UTC 跑出「今日 TLT 收盤 $82.25」——美股尚未開盤，那是 8/3 的收盤。
修法：標籤改「最近收盤」+ 該價格實際所屬交易日（closes.index 的日期）；
週快照與現況條同用 history Close 單一資料源；收盤日==快照日 → 現況條靜默
（取代 v2.4 的「快照日當天靜默」，語義更準）。

測試 T9-T15 全過。8/4 驗收通過項（多層偵測、價格失效標籤兩種時態、
覆蓋率分母定義等）未重做。

## tlt_radar v2.4 — 部分失敗假綠燈（PATCH 2026-08-04）

2026-08-03「模式 B」：價格抓成功（$82.25）但選擇權鏈失敗 → Skew 表 0 列、
Skew 恰 0.00%、OI -100%/-99.9% → 三分項全 0 → 又輸出「0/100 🟢 平靜」。
v3.11 的 nan 防線攔不住（這次沒有 nan）。更糟：部分失敗被記進 history
（82.25/temp 0）→「本週已成功即跳過」成立 → 整週不再重試＝退回原本的病。

修正（tlt_radar v2.4）：
- **多層有效性檢查 tlt_data_is_valid()**：層1 價格/歷史 nan、層2 鏈存在性
  （Skew 表 0 列）、層3 OI 崩塌指紋（≤-99%，TLT OI 不可能歸零）、層4 Skew 恰為 0。
  偵測「資料不存在」而非「分數為 0」——真平靜三分項可同時為 0（T5 偽陽性防線）
- **無效渲染**：不輸出溫度/燈號/三分項；顯示上次有效讀數＋仍顯示有效的價格
  （$82.25 貼近 60 日低本身有資訊）
- **無效不寫 history** → 「本週已成功」不成立 → 每日排程持續重試（patch §4.3）
- 資料清理：移除 8/3 污染 history 列；報告檔以新邏輯重生（今晚主掃描不再貼假綠燈）
- §7.1 日更現況條快照日當天靜默（第 0 天比對是來源雜訊）
- §7.2 乾淨窗口分母欄名 total_rows→report_rows（定義＝進入報表的信號列，
  非掃描到的全部合約），報表文字同步明示
- 測試：T1-T8 全過（另加首次跑無 baseline 不誤觸層 3）

## Scanner 3.11 — handoff #2 殘項修正（2026-08-01）

驗收報告（handoff #2）判「P0-1/P1-2 未修」的真相：3.10 已合併部署，但
(a) TLT 是週更，修正版 7/31 前沒跑過——舊程式 7/25 產出的 nan 報告躺在
data/ 被主 scanner 每天照貼（8/1 週六排程用 v2.2 跑出正常讀數後自癒）；
(b) IV 過濾設 ≤1%，7/31 末日區 7.6-8.8% 壞值穿過。修正：

- **P0-1 三層補完**：
  1. tlt_radar v2.3：cron 改每日 + 腳本「本週已成功即跳過」＝「該週第一次成功
     抓取」語義（不硬編週幾，單點失敗不再瞎整週；regime 仍為週更——設計決策：
     日更會把週與週的 regime 變化埋進日間雜訊，且 5 倍 API 換慢速指標）
  2. main.py 渲染側 nan 防線：報告檔含 nan 一律不轉貼，改貼警示區塊
  3. main.py 日更「現況條」：每天 1 次 API 抓 TLT 收盤，顯示較快照日 ±%，
     |Δ|>3% 警示 regime 讀數可能過期（補 7/22-23 油價破百當週快照過期無跡象的缺口）
  4. 資料清理：history csv 移除 2026-07-25 失敗殘留列（空價格＋假 0 分）
- **P1-2 補強**：低 IV 門檻 1%→5%，只殺價外（價內 IV 合法偏低、spot 缺不誤殺）；
  末日區（DTE<5）IV 欄一律顯示「—」＋區塊註記（到期日 IV 反推全面失真）
- **P0-2 最後一哩**：財報標籤改時間戳判斷——今日 16:00 後開牌→⚠️已失效、
  今晨已開→只標📅財報已過（16:00 快照已反映，不誤標）、明日 09:30 前→⚠️恐失效、
  無時間資訊→保守標已失效
- **P1-1**：3.10 已修（月選 only + OI≥50 + 文案），本次加報表自證標示
  「（僅月選、ATM OI≥50）」——下次出現峰值提示時可直接從報表確認過濾已生效
- **環境指標（handoff 附註採納）**：「吃不到財報」每日計數進報表頭 +
  data/earnings_window_history.csv（7/31 全表僅 4 筆乾淨窗口——連四天票全死在
  物種閘門不是判讀太嚴，是市場沒有無事件窗口）
- 第四批 SHADOWLOG：**3.10 已全數上線**（現行 SHADOWLOG 已有歸零率 6%、
  標的-日去重命中率 9%、歸因欄），handoff #2 的第四批清單為過時資訊

## 資料夾整併＋子雷達覆核（2026-07-31，第二批）

同日第二批工作（第一批是 Scanner 3.10，見上節）。擁有者主動要求的目錄整理
（CONTEXT.md 紅線 5 的例外，workflows 同 commit 改路徑＋selftest 驗證）：

### tw_scanner/（delta_radar 併入）
- delta_radar.py、config、output（含 append-only state.json）全部 git mv 進 tw_scanner/
- 原 readme 改名：readme.md → MANUAL_tw_scanner.md、delta README → MANUAL_delta_radar.md
- 新增 build_readme.py：README.md 變成產出報表（天氣簡報＋delta 報告＋回測，像主 scanner）
- 兩份 workflow 各自 run 後重組 README；requirements 合併；刪除散落的 data/delta_radar_config.json（與正本完全相同的舊拷貝）
- tw_scanner selftest 補「寫臨時目錄」防呆（radar 家族紀律，原本會污染真實 output/）

### spcx_radar/（SPCX 集中）
- space_radar.py、spcx_options.py 搬入；data/spcx_* 九個檔案歸位 config/（手動維護）與 output/（產出）；spcx_playbook.md → PLAYBOOK.md
- 重複碼抽 spcx_common.py：load_config/現價(dropna+nan 防呆)/ATM IV/市值換算/IV 分位，兩模組同一套介面
- README.md = space_radar＋Option Sage 合併產出（build_readme.py）
- space_radar v8.7、sage v0.2

### 覆核結論（詳見 tw_scanner/REVIEW_2026-07.md）
- **tw_scanner 留任**：capitulation 回測與基線分離（60 日中位 +9.80% vs +4.94%、命中 83%），7/30 警報活體測試中
- **delta_radar 不退役但設死線**：hit-rate 63 筆顯示作為交易訊號零價值（全綠 cohort T+20 超額 -15%），但作為論點監控正產出「前提健在＋價格重挫」的背離資訊。待辦：加背離旗標；退役判準寫死（n≥30 後 GREEN 劣於自家 YELLOW/RED → 模組處決；2026-10 底整支生死判決）

### SPCX 8 月判斷（詳見 spcx_radar/PLAN_2026-08.md）
- A 池 74% 佈署、階梯全觸發 → 只剩補滿決策；B 池 1.5T 已觸發 → 剩 9/10 GT90 重掛與 12/9 終點 → **A/B 轉跟進手冊**（v8.7 報告新增日曆化區塊）
- C 池專用模組：**現在是「預備」時機非「出手」時機**——流動性 gate 已過（INT 296k）、IV 分位基準 41 樣本已可用，但 IV 123%/分位 93 歷史最高檔。sage_v0.2 開始記 LEAPS 專屬 IV（在崩之前建基準）＋viewpoint 範例偵測。gates 一條不放寬

## Shadow log 第一次改卷（2026-07-06）

污染清理（PR #2）+ 雙貼標（premium_tier / news_at_signal，PR #1/#3）完成後，
用乾淨的 66 筆已判定信號做第一次系統性分析。**完整結論寫在 CONTEXT.md 第七節**
（分數=及格線非排名、tag 指紋假說、新聞測謊器、EV 模擬與四個保留），這裡只記事件與決策：

- **決策：計分公式不動。** 9 分 0/10 vs 8 分 3/56，分數的排名功能目前失效
  （8→9 的 +1 來自「便宜」而便宜是負向特徵），但樣本太小不足以重新擬合權重。
  分數繼續只當「≥8 進快照」的及格線用，倉位不按分數加碼。
- **最強線索**：三筆命中（GOOGL 350C / META 635C / ASTS 140C）唯一共同指紋是
  純「🚨異常掃貨+🆕新倉暴量」無其他標籤。6/26 批內 4 筆此型態包辦 3 命中。
- **兩個判決性數據點在路上**：7/2 批 15 筆同型態的 T+5（~7/9）、
  6 月批 T+20 全回填（7/16 起）。到位後重跑 EV 模擬再談期望值。
- 方法論備忘：本次所有檢定都是事後挑選（post-hoc）+ 批內信號相關，
  p 值一律要打折；「顯著」二字在樣本 <50/層之前不要出口。

---

## 檔案清單

```
optscnr/                             (2026-09-08 更新)
├── CONTEXT.md                       (系統脈絡＋紅線，接手先讀)
├── README.md                        (每日報表，main.py 產出＝軌 A)
├── SHADOWLOG_YYYY-MM.md             (shadow_tracer 產出)
├── main.py                          (v3.13＋)
├── strategy_lab.py                  (純計算：策略矩陣／規則 B／賣點／對照組／tags 拆解)
├── shadow_tracer.py                 (T+N 回填、路徑、矩陣、decisions outcome)
├── catalyst_fetch.py                (v6)
├── small_cap_momentum.py
├── fallen_saas.py
├── tlt_radar.py                     (v2.5)
├── unknown_radar.py                 (v1.3)
├── enrichment.py                    (OI Δ7d null 語義)
├── universe_update.py
├── cloudflare/                      (Worker：第二鬧鐘＋LLM 三題＋dashboard＝軌 B；只靠 CF Git 連動部署)
│   ├── wrangler.toml                (workers_dev=false、crons、vars；secrets 只在 CF dashboard)
│   ├── src/index.js                 (scheduled/fetch、GitHub Contents API、OpenRouter、parseLedger、Access JWT)
│   ├── public/index.html            (dashboard：今日候選/History/Decisions/事實庫/排程)
│   └── README.md                    (一次性設定、模型選擇、Access 步驟)
├── docs/
│   ├── PLAN_2026-09_strategy_dashboard.md   (預先登記書＋建置批次＋tracker＋現況)
│   ├── PROJECT_ESCAPE_DOOR.md       (GitHub 依賴評估＋路線圖，Phase 1/2 已完成)
│   ├── FACTS_ledger.md              (事實庫：人維護；Worker 只寫「待審」段)
│   ├── PROMPT_daily_report_reading.md      (v3，人在對話裡用)
│   ├── PROMPT_daily_report_reading_v4.md   (v4.1，Worker 每天讀的 ```prompt 區塊)
│   ├── CASEBOOK_2026-07.md          (判例，從 v3 搬出)
│   ├── exit_playbook.md / docs.md / log.md
├── spcx_radar/                      (2026-07-31 集中)
│   ├── space_radar.py               (v8.7)
│   ├── spcx_options.py              (sage_v0.2)
│   ├── spcx_common.py / build_readme.py
│   ├── README.md                    (產出報表) / PLAYBOOK.md / PLAN_2026-08.md
│   ├── config/                      (spcx_config / dca_log / c_viewpoint，手動維護)
│   └── output/                      (json、iv_history、options_history、報告)
├── tw_scanner/                      (2026-07-31 併入 delta_radar)
│   ├── tw_scanner.py / delta_radar.py / build_readme.py
│   ├── README.md                    (產出報表) / MANUAL_*.md / REVIEW_2026-07.md
│   ├── config/  ├── output/  └── cache/
├── .github/workflows/
│   ├── scanner.yml
│   ├── catalyst_fetch.yml
│   ├── small_cap_momentum.yml
│   ├── fallen_saas.yml
│   ├── tlt_radar.yml
│   ├── unknown_radar.yml
│   ├── space_radar.yml              (路徑指向 spcx_radar/)
│   ├── delta_radar.yml / tw_scanner.yml (路徑指向 tw_scanner/)
│   └── ...
└── data/
    ├── YYYY-MM-DD.csv / latest.csv  (每日掃描；OI Δ7d 的歷史來源；留 365 天)
    ├── iv_log/signals_YYYY-MM.json  (信號快照，append-only，schema v2 含 path[])
    ├── dashboard/                   (candidates_<市場日>.json、latest.json、decisions_log.json)
    ├── decisions/<市場日>.json      (Worker 寫的 LLM 三題；tracer 只補 outcome)
    ├── universe_spots/<市場日>.json (全 universe 收盤；對照組 T6)
    ├── strategy_matrix.json         (每天重算)
    ├── catalyst_today.json
    ├── small_caps_momentum.json
    ├── fallen_saas.json
    ├── tlt_radar.json / _report.md / _history.csv
    ├── unknown_radar.json / _history.json
    └── listed_companies.json        (SEC 上市清單 cache)
```
