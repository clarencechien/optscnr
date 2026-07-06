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

### 4. tlt_radar.py (v2.1)
- TLT 避險「溫度計」0–100 分（Put 巨鯨 + IV Skew + OI 週累積三訊號合成）
- **v2 修 bug**：原本 `tk.options[:6]` 全抓到週選近月 → IV term structure 失真（ATM Call IV 出現 1.2% 等垃圾值）。改智慧 DTE 選擇 `[30,60,90,180,240,365,500]`
- 加 IV 5%–200% 過濾 + OI≥50 要求（濾 stale quote）
- 每週六 UTC 02:00 跑

### 5. unknown_radar.py (v1.3) — 「擦鞋童雷達」
- 目標：抓「新聞反覆出現但不在我字典裡」的標的（認知盲點）
- 流程：RSS 抽大寫公司名 → 過濾 KNOWN_TICKERS(251 檔) + COMMON_WORDS(390 詞，含國家/姓氏/術語) → 對照 SEC 上市清單找 ticker → 累積連續天數
- **SEC 403 修法**：User-Agent 須含真實識別資訊（不能用瀏覽器 UA 假冒）；加 NASDAQ Trader 備援來源
- 連續 2+ 天出現 = 強訊號，ticker 自動進主掃描
- 雜訊清理是迭代式的：第一版抓到 Here/Iran/Singapore/Chinese 等誤判，逐步加進 COMMON_WORDS

### 6. space_radar.py (v8.1) — SPCX (SpaceX IPO，預計 6/12)
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

## GitHub Actions 排程（UTC，台灣 = UTC+8）

| 雷達 | cron | 台灣時間 |
|---|---|---|
| catalyst_fetch | `0 21 * * 0-5` | 平日 05:00 |
| unknown_radar | `30 21 * * 0-5` | 平日 05:30 |
| main scanner | `0 22 * * 0-5` | 平日 06:00 |
| space_radar | `15 22 * * 0-5` | 平日 06:15 |
| small_cap_momentum | `0 0 * * 6` | 週六 08:00 |
| fallen_saas | `0 1 * * 6` | 週六 09:00 |
| tlt_radar | `0 2 * * 6` | 週六 10:00 |

週末雷達刻意錯開，避免同時搶 RSS / API。

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
optscnr/
├── main.py                          (v3.7)
├── catalyst_fetch.py                (v6)
├── small_cap_momentum.py
├── fallen_saas.py
├── tlt_radar.py                     (v2.1)
├── unknown_radar.py                 (v1.3)
├── space_radar.py                   (v8.1)
├── enrichment.py
├── universe_update.py
├── .github/workflows/
│   ├── scanner.yml
│   ├── catalyst_fetch.yml
│   ├── small_cap_momentum.yml
│   ├── fallen_saas.yml
│   ├── tlt_radar.yml
│   ├── unknown_radar.yml
│   └── space_radar.yml
└── data/
    ├── catalyst_today.json
    ├── small_caps_momentum.json
    ├── fallen_saas.json
    ├── tlt_radar.json / _report.md / _history.csv
    ├── unknown_radar.json / _history.json
    ├── listed_companies.json        (SEC 上市清單 cache)
    ├── space_radar.json / _report.md
    ├── spcx_config.json             (SPCX 可變參數，改這裡不用動 code)
    ├── spcx_dca_log.json            (手動維護 DCA 買進紀錄)
    └── spcx_iv_history.csv          (選擇權上市後才生成)
```
