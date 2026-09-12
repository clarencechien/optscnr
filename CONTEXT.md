# CONTEXT.md — optscnr 系統脈絡（給 Claude Code 與未來 session）

> 目的：讓任何接手的 AI session 或未來的自己，不必重讀整段對話史就能理解
> 「這個系統是什麼、為什麼長這樣、哪些線不能踩」。改動系統前先讀完本文件。

---

## 一、這個 repo 是什麼

美股選擇權「湯姆熊」玩法的每日掃描系統：便宜價外 Call（$0.2-1.5 樂透）+
等敘事重定價噴出 + free ride（+100% 賣半、剩餘零成本續抱）。
GitHub Actions 每日掃描 → README.md 妖股報表 + shadow log 信號校準。

**擁有者資金三層結構（改動時要知道這個系統只服務第 3 層）：**
1. 核心資本（長期複利）
2. SPCX 主題投資（$200k 三池，另有 spcx_options.py 雷達）
3. 湯姆熊閒錢（本 repo 主掃描的服務對象；本金已撤，桌上只剩免費籌碼）

## 二、系統地圖（誰做什麼）

| 檔案 | 職責 |
|---|---|
| main.py | 主掃描（Scanner 3.13：市場基準日、四道假高分過濾、財報標籤、🎯 結構候選、🤖 LLM 三題節），產 README + 信號快照 + 候選 JSON + universe spot |
| strategy_lab.py | 純計算：分類邊界、三策略 A/B/C 與四種出場政策、規則 B `structural_pass`、賣點、策略矩陣、對照組、tags→features 拆解（預先登記 2026-09-08） |
| shadow_tracer.py | 回填信號 T+5/T+10/T+20 結果、每日路徑 `path[]`、策略矩陣 `data/strategy_matrix.json`、decisions 的 `outcome` 回填，產 SHADOWLOG_YYYY-MM.md |
| enrichment.py | OI Δ7d 計算（缺 7 日歷史 → null + `OI_d7_status`）+ Top5 深度卡 |
| tlt_radar.py | TLT 避險溫度計（週更、併入主掃描 session，附加在 README 尾） |
| catalyst_fetch / fallen_saas / small_cap_momentum / unknown_radar / universe_update | 動態清單餵給主掃描 |
| cloudflare/ | Cloudflare Worker（獨立資料夾、dashboard Git 連動部署）：第二鬧鐘（GitHub 排程沒發就 `workflow_dispatch`）、每交易日盤後 LLM 三題 → `data/decisions/`、dashboard 靜態頁。**Python 一行都不在這裡**，見 `cloudflare/README.md` |
| spcx_radar/ | SPCX 主題雷達（space_radar + spcx_options/Option Sage；共用碼在 spcx_common.py；config/=手動維護、output/=產出、README.md=每日報表、PLAYBOOK.md=執行手冊、PLAN_2026-08.md=8月後任務） |
| tw_scanner/ | 台股子專案：tw_scanner 天氣台 + delta_radar 2308 雷達 + **dca_ledger.py（DCA 規則影子帳本，2026-09-12）** + **tw_brief.py（週報組裝 → tw_brief.json / tw_weekly.md）**；README.md 由 build_readme.py 重組（週報在最上面）、MANUAL_*.md=維護文件、REVIEW_2026-07.md=改進判準。tw_scanner.py 每次簡報另導出 `tw_scanner_history.json`（2019 起全序列 regime/alerts，帳本回測用）；delta_radar 有背離旗標與退役判準表（REVIEW 改進項 1、2） |
| data/*.csv | 每日掃描結果（保留一年，靠檔名日期 prune；也是 OI Δ7d 的歷史來源） |
| data/iv_log/signals_*.json | 信號快照（**永久保存、append-only**；schema v2 含 bid/ask、features、path[]） |
| data/dashboard/ | `candidates_<市場日>.json` + `latest.json`（結構候選＋綁定策略＋賣點，dashboard 與 Worker 讀）、`decisions_log.json`（tracer 彙整） |
| data/decisions/ | `<市場日>.json`：Worker 寫的 LLM 三題答案（**append-only**；tracer 只補 `outcome`） |
| data/universe_spots/ | 每日全 universe 收盤（對照組 T6、LLM 第 (b) 題） |
| data/strategy_matrix.json | 分類 × 出場政策矩陣（每天重算） |
| docs/ | CONTEXT 之外的文件：`PLAN_2026-09_strategy_dashboard.md`（預先登記書＋建置）、`PROJECT_ESCAPE_DOOR.md`（GitHub 依賴評估）、`FACTS_ledger.md`（事實庫，人維護、Worker 只寫待審段）、`PROMPT_daily_report_reading.md`（人用 v3）／`_v4.md`（機器用）、`CASEBOOK_2026-07.md`、`exit_playbook.md`、`log.md` |

**雙軌呈現**：軌 A ＝ GitHub README（Python 渲染，CF 掛了也在）；軌 B ＝ CF dashboard（同一批 JSON，多 History／Decisions／事實庫／排程健康）；
軌 B 另有 `/brief` 電子報（公開唯讀、一頁 TL;DR、不觸發任何動作，可分享連結）與 `/tw` 台股週報（同樣唯讀，讀 `tw_scanner/output/tw_brief.json`）。資料主權永遠在 git。

**架構原則：平鋪但有序（每雷達一檔+對應 yml）。不做大目錄重構**——
10 個 workflows 正在跑，重構美觀收益遠低於弄斷每日掃描的風險。
（2026-07-31 例外：擁有者主動要求將 delta_radar 併入 tw_scanner/、SPCX 檔案集中到
spcx_radar/——workflows 同 commit 同步改路徑並以 selftest 驗證，紅線的本意
「不弄斷排程」有被遵守。）

## 三、Scanner v3.9 的四道過濾（為什麼存在）

每道過濾都是真實虧損教訓的產物，門檻集中在 RULE_CONFIG：

1. **⚠️尾段價外**（距現價>25%按IV放寬 + DTE<45 → -3）：擋 F 22C / META 1100C
   這類「極價外+短天期」投機尾段——主升段點火與尾段狂歡的點火分數一樣，意義相反。
2. **⚠️當沖刷量**（Vol大但Δ7d≈0 → -3）：擋 GOOGL 575C 這類量大但 OI 沒沉澱的假點火。
3. **🏛️機構場**（大市值+IV<35% → -1）：標 AAPL/MSFT 這類機構溫吞場。
4. **⚠️暴動高IV**（點火+IV≥80%+DTE<60 → -2）：RUN 事件的產物——暴動當天 IV 飆到
   90%+ 卻給高分，追進去被 IV crush。盯的是 IV 這個真變數，不是「第幾天」表象。

**SURGE_IV_MIN=80 是假設值**，等 SHADOWLOG 區塊一驗證（被標記的後來大多歸零→有效；
大多噴了→誤殺，調高門檻）。**驗證樣本 <50 筆前不要動任何門檻。**

**已知過濾盲點（記錄中，等數據決定是否補過濾）：**
- 盲點一「長天期極價外」：過濾一要求 DTE<45 才觸發，DTE>45 的極價外漏網。
  活案例：TSLA 990C（2026-07-06，DTE 74、OTM 135%、8分）。
- 盲點二「倉退刷量」：過濾二門檻 |Δ7d|≤200，量大但 OI 減少者若略超門檻即漏網。
  活案例：VST 180C（2026-07-06，Vol 7,688、Δ7d -234、9分）。
- 盲點三「長假 OI 延遲」：OI 有 T+1 更新延遲——長假前最後交易日的尾盤突襲建倉，
  成交沉澱成 OI 時已休市；假日重播掃描被 cron+guard 正確關閉後（見第六節），
  下一個交易日掃描看到的是「新 OI + 當日新成交量」，vol/OI 條件多半不再觸發
  → 這類信號結構性漏接。活案例：PEP 155C（7/2 尾盤 41,087 口掃貨、OI 8,525
  全為新倉，7/2 當日掃描因 OI 未更新被前置過濾擋掉，只出現在已清除的 7/5
  假日重播批）。可能解法方向：用 enrichment 已計算的 OI Δ 跳變做「隔日確認」
  信號——等指紋 cohort 數據成熟後再議，現階段只記錄。
- 前兩者由 SHADOWLOG「🕳️ 過濾盲點觀察」cohort 持續追蹤，
  初步數據（6月，樣本小）：長天期極價外與倉退命中率均低於整體。

## 四、Shadow log 設計鐵律（違反=系統失去意義）

1. **append-only**：信號寫入後不得竄改（防事後自欺）。唯一例外見第六節污染清理。
2. **和錢隔離**：只記「信號的市場後續」，絕不記「持有什麼、賺賠多少」。
   **tracing ≠ portfolio**——追蹤 scanner 準不準是校準鏡；追蹤損益是毒藥
   （會把凸性遊戲拉回損益焦慮：浮虧想攤平、浮盈捨不得跑）。
3. **shadow 先行**：任何規則調整先用數據驗證，不憑感覺。
4. **NO_DATA 優雅降級**：抓不到就標 null，不猜、不中斷。

**Scanner 是篩子不是神諭**：它把幾千個合約篩到每天 ~10 個「值得看」；
「能不能買」需要人查證催化（財報日期、併購、內部人動向）——這層不自動化，
是刻意設計不是缺陷。判斷器做不出來：能機械化的賺錢規則夠多人用就失效。

## 五、校準資料的三個已知偏差（解讀 SHADOWLOG 數字時必看）

1. **檢查點抽樣偏差**：tracer 只在 T+5/10/20 三點拍照，點間峰值看不到。
   實戰是 free ride（+100% 當下賣半），所以 **SHADOWLOG 命中率是實戰可得的下限估計**
   （RUN 型「暴動次日就 crush」的信號，T+5 拍到的已是崩完價）。不修——加密度
   讓系統複雜化不值得，知道偏差方向即可。
2. **日曆日 vs 交易日**：T+N 用日曆日，撞週末時回填抓到 stale 價。影響小。
3. **樣本規模**：分層（premium_tier）每層 <10 筆時命中率僅供參考。
   **動門檻的前提：T+20 全回填 + 已驗證 >50 筆 + 污染清理後的乾淨樣本。**

## 六、污染事件記錄（2026-07，本文件誕生的原因）

**症狀**：signals JSON 出現非交易日 snapshot_date（6/28 日、7/3 假日、7/5 日），
同一批陳舊異常用不同日期重複入庫，灌水樣本、扭曲命中率。

**根因鏈**：
- cron `'0 22 * * 0-5'` 含 UTC 週日 → 美股週末休市 → 該次掃描 = 週五資料重播
- 美股假日（7/3 國慶補假）落平日時 cron 照跑 → 同樣是舊資料重播
- save_signal_snapshot 無開盤日檢查 → 重播照記
- signal_id 含日期 → 跨日去重擋不住

**修復（雙保險）**：cron 改 `1-5`（擋週日）+ main.py `us_market_traded_today()`
guard（擋假日，SPY 最後交易日 vs 美東今日比對，fail-open）+
`clean_stale_signals.py` 一次性清除既有污染。

**為什麼清理不違反 append-only**：append-only 保護「預測不被事後竄改」；
污染信號是排程 bug 的機械性重播，從來不是新預測——移除是資料還原不是竄改。

**歷史教訓同族**：這是 repo 第三次栽在「靜默失敗」——
① `|| true` 吞掉 CSV 刪除失敗（半年沒清才發現）
② `ls -t` 靠 mtime 排序（checkout 重置 mtime 後排序失效）
③ 本次非交易日重複掃描。
**共同模式：pipeline 假設「每次執行環境都一樣」但沒驗證假設。**
新增任何排程任務時，先問：「休市日/資料缺失/重跑時，這段會做出什麼蠢事？」

## 七、第一次改卷結論（2026-07-06，已判定 66 筆，僅供觀察、不據此改規則）

Shadow log 累積到 66 筆已判定後做的第一次系統性分析。樣本仍小、
且只涵蓋一個月的上漲行情——以下是「目前最佳理解」，不是定論。

**1. 分數是及格線，不是排名（目前甚至反向）**
9 分已判定 0/10 全滅、8 分 3/56（三筆命中全在 8 分）。拆解後發現
8→9 的那 +1 幾乎全來自 🚬菸屁股（權利金 <$1），而三筆命中全是 ≥$1——
「便宜」目前是負向特徵卻拿正分。計分公式是手寫權重、從未用結果擬合過。
理論上限 11 分（掃貨5+點火3+萬人塚2+LEAPS1）從未在資料中出現。
**操作含義：過 8 分就值得看，但不要按分數排序或加碼；
重寫計分公式要等樣本 >50 筆/層——在那之前分數只當快照門檻用。**

**2. tag 指紋假說（目前最強的一條線索）**
三筆命中的唯一共同指紋：純「🚨異常掃貨 + 🆕新倉暴量」且無其他標籤
（= 合約七天內新生 + 量 >1.2x OI 的掃貨 + 不是菸屁股/萬人塚的散戶墳場）。
6/26 批 17 筆中此型態僅 4 筆，包辦全部 3 個命中 + 1 筆峰值 1.8x 的差點
（ASTS 190C）；同日其他 13 筆全滅。但此型態在 6/29-7/1 也出現 13 筆全沒中
→ **型態挑標的，日子給行情，兩者缺一不可**。
盲測進行中：7/2 批有 15 筆同型態待 T+5 驗證。

**3. 新聞×flow（見 news_at_signal 貼標）**
Scanner 沒有先於新聞（META/GOOGL 在 6/25 已上催化名單）。它的價值是
「新聞測謊器」：6/26 名單 12 檔中 flow 只放行 2 檔，兩檔全噴。
初步分層：新聞點火 2/18(11%) vs 純 flow 1/48(2%)，等樣本。

**4. 期望值模擬（等額買入 66 筆、以 T+N 檢查點價計）**
死抱 +15%、free ride +14%；沒噴組平均仍有 1.09x。**但尚不能宣稱 EV 為正**：
① 三個贏家扛了全部超額報酬，拿掉後 +9% ≈ 上漲月的 Call beta；
② 未計買賣價差（$1-5 價外合約來回 5-20%，可能吃光帳面優勢）；
③ 磨損還沒發生——只有 T+5/T+10 數據，theta 要到 T+20/到期才真正咬人，
   12 筆卡在 0.75-1.0x 的屆時會流血；
④ 單一月份、單一行情（上漲），盤整/下跌月未知。
free ride 與死抱在本樣本幾乎無差，因為只有 3 筆碰過 +100% 賣半線——
它的保護價值要等「先噴後崩」樣本（如 META 峰 9.1x→終 2.5x）夠多才顯現。

**5. 兩個判決性數據點（等排程送來，不用動手）**
① 7/2 批 15 筆純掃貨+新倉暴量型態的 T+5（測型態假說，~7/9 出爐）
② 6 月各批的 T+20 全回填（測磨損與真實 EV，6/26 批約 7/16 起）
兩者到位後應重跑一次 EV 模擬，屆時的數字才夠誠實。

## 八、進行中事項（PENDING）

- **premium_tier 貼標**：已部署（2026-07，PR #1/#2）。快照帶 lottery/mid/heavy
  分級、SHADOWLOG 有分層命中率表、歷史已回填。等樣本累積，每層 <50 筆前不下結論。
  背景：META 635C（$1.28 樂透）噴 9.1x 與 GOOGL 350C（$5.5 實彈）噴 3.1x
  是兩種不同性質信號，先貼標讓數據回答「哪類更準」，**不做分類池 UI、不做盤中 alert**。
- **news_at_signal 貼標**：已部署（2026-07）。快照記錄「信號日標的是否已在
  catalyst 新聞名單」，SHADOWLOG 有「新聞點火 vs 純flow」命中率表，歷史從
  catalyst_today.json 的 git 版本回填（用的是信號日當天的公開資訊，非事後資訊）。
  背景：2026-06-26 批新聞名單 12 檔中 flow 只放行 GOOGL/META 兩檔全噴、
  無新聞 15 筆只中 ASTS 一筆——「新聞×真金白銀交集」假說，等數據驗證。
- **tag 指紋盲測**：追蹤 7/2 批 15 筆「純掃貨+新倉暴量」的 T+5 結果，
  以及 T+20 全回填後重跑 EV 模擬（見第七節第 5 點）。純觀察，不改規則。
- **SURGE_IV_MIN 驗證**：等 SHADOWLOG 區塊一樣本累積。
- repo 整理 P1（requirements.txt 統一）P2（docs/ 歸攏）已完成（PR #1）；
  P3（抽 utils.py）等系統穩定；P4（大重構）不做。
- **策略矩陣預先登記（2026-09-08 起，docs/PLAN_2026-09_strategy_dashboard.md）**：三策略 A 死抱／B 2x 賣半／
  C 分類綁定＋規則 B 結構候選已凍結三個月；每天自動重算矩陣、記路徑、記對照組、記 LLM 三題。
  判準：100 筆出樣本 T+20 成熟後 C 在規則 B 上 EV ≥1.25x 且命中 ≥25% 才算成立。
  **累積期間不看單日、不看單月、不改綁定。** tracker T1–T9 的現況見該文件第 2、8 節。
- **LLM 三題（第 5 批，2026-09-08 起）**：Worker 每交易日盤後只問三題事實題（排定事件／近 5 日跳空／Δ7d 是否 confirmed），
  不做可玩判斷。答對率與候選命中率由 T8 累積 60 個交易日後看；人工抽查機制等 20 個交易日後再設計。

## 九、紅線（任何 session 都不得越過）

1. **不做盤中即時 alert / 推播 / 跟單功能**——擁有者的 edge 在「慢+查證+會說不」，
   即時化會製造 FOMO、跳過查證。快是別人的遊戲。
2. **不做 portfolio / 損益追蹤**——見第四節 tracing≠portfolio。（2026-09-12 界線說明：`tw_scanner/dca_ledger.py` 是**規則影子帳本**——等額假設、不記真實部位、不記個人損益，跟 strategy_lab 的 EV 模擬同一性質；它回答「tw_scanner 的訊號對定期定額值多少」，不是「你賺賠多少」。個人曝險與部位一律不進本 repo，本 repo 公開。）
3. **不在樣本不足時調門檻、不重寫計分公式**——見第五節與第七節。
4. **不竄改交易日信號的既有欄位**——append-only。
5. **不做大目錄重構**——10 個 workflows 會斷。
6. **所有面向擁有者的文字一律台灣正體中文**（勿簡體、勿中國用語）。
7. **預先登記期間（2026-09-08 起三個月／100 筆出樣本）不改策略綁定、規則 B 門檻、分類邊界**——改了 PLAN 文件作廢。
8. **decisions 與事實庫的 append-only**：`data/decisions/` 的 LLM 答案不回寫（tracer 只補 `outcome`）；
   `docs/FACTS_ledger.md` 程式只能寫「待審（LLM 提案）」段，入庫永遠是人。
9. **LLM 只答事實題，不做可玩/跳過判斷、不填機率**；改 prompt 要進位 `prompt_version`，讓 decisions 分得出版本。
10. **Secrets（GITHUB_TOKEN、LLM_API_KEY、ACCESS_*）只在 Cloudflare dashboard 設**，永不進 git；`cloudflare/` 只靠 Git 連動部署，`workers.dev` 關閉。

## 十、給接手 session 的最短路徑

1. 讀本文件（你正在做）
2. 看 SHADOWLOG_當月.md 了解校準現況；看 CF dashboard 的 History／Decisions（或 `data/strategy_matrix.json`、`data/dashboard/decisions_log.json`）
3. 看 docs/PLAN_2026-09_strategy_dashboard.md 第 0、2、3、8 節（預先登記與 tracker 現況）、docs/log.md、docs/exit_playbook.md
4. 動手前檢查：這個改動有沒有踩第九節紅線？有沒有重複第六節的靜默失敗模式？改 `cloudflare/` 要跑 `node --check` 與離線 mock 測試（docs/log.md 第 5 批專節）
