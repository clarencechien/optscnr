# PROJECT ESCAPE DOOR — 逃生門評估與路線圖

> 產出日期：2026-09-01
> 觸發事件：2026-08-26 ~ 08-31 GitHub Actions 排程全面延遲 3-8 小時、8/31 直接沒發
>（後果：8/27 整天沒掃、兩天資料標錯日期、擁有者被迫手動觸發——詳見 docs/log.md）
> 性質：**這是逃生門，不是搬家令。** 文末有明確的觸發條件——條件沒到就不動。

---

## 一、我們實際依賴 GitHub 的是什麼

| 依賴 | 用途 | 這次事故受傷了嗎 |
|---|---|---|
| **排程**（cron） | 每天固定時間跑 10 支雷達 | 🔴 **重傷**——延遲/丟棄是事故本體 |
| **運算**（Actions runner） | 跑 Python（pandas + yfinance，5,800+ 行） | 🟢 沒事——runner 本身從沒壞過 |
| **儲存**（git repo） | data/ 每日 CSV、append-only 信號快照 | 🟡 間接受傷（延遲導致標錯日期，非儲存本身的錯） |
| **觀看**（GitHub md 渲染） | README = 報表，手機開 GitHub 就能看 | 🟢 沒事 |
| **審計**（git history） | append-only 的不可竄改性靠 commit 歷史背書 | 🟢 沒事，而且是重要資產 |

**結論先講：五項依賴只有一項真的壞，而那一項（排程）恰好是最容易外掛補強、
最不需要搬家就能解的。** 全面遷移是拿四個沒壞的東西去賭一個修得好的東西。

---

## 二、三個問題的直答

### Q1：架構放 Cloudflare 會好一點嗎？data 放 R2 不放 git？

**排程會好，其他多半會更麻煩。**

- **排程**：Cloudflare Cron Triggers 的觸發準時性遠好於 GitHub schedule（GitHub 官方
  文件自己承認 schedule 是 best-effort，高負載會延遲/丟棄）。這是 CF 唯一明確的勝點。
- **R2 取代 git 存 data**：
  - ✅ 好處：repo 不再每天長大（data commits 已是 commit 史的主體）；R2 零 egress 費；
    大檔案不再撐爆 clone。
  - ❌ 代價一：**失去 git history = 失去 append-only 的審計背書**。CONTEXT.md 的鐵律
    「不竄改交易日信號」目前是靠 commit 歷史可驗證的；R2 物件可以被無痕覆寫，
    要自己搭 versioning/object lock 才等價——這是把「白拿的信任機制」換成「要自己維護的信任機制」。
  - ❌ 代價二：**「用 git 版本回填歷史」這招會失效**。news_at_signal 貼標當時就是靠
    checkout 舊 commit 拿到「信號日當天的公開資訊」——R2 沒有這個能力。
  - 折衷解（若真要做）：**分層**——`data/iv_log/` 信號快照與各 history csv（小、
    需要審計）留 git；每日掃描 CSV（大、365 天輪替、純 cache 性質）搬 R2。
    但目前 repo 大小根本還沒到需要這麼做的程度。

### Q2：觀看怎麼辦？原本直接看 md，要做網頁或 md→html 嗎？

**只要運算還在 GitHub Actions，觀看就完全不用動**（README 照舊）。真要搬才需要：

- 最省力：報表產出時多跑一步 `markdown → html`（Python `markdown` 套件，十行程式），
  靜態 html 丟 R2 + Cloudflare Pages/Workers Sites 掛出來。**不需要「做網頁」**，
  不需要框架，不需要前端——一份 html、一個 `<style>` 就是全部。
- 也可以更懶：html 裡用 client-side 渲染（marked.js 讀 R2 上的 .md），連轉檔都省。
- 手機閱讀體驗甚至會比 GitHub md 好（可以自訂字級、表格橫捲）。
- **結論：觀看層是整個遷移裡最便宜的一塊，任何時候要做半天就能做完，
  不構成搬或不搬的理由。**

### Q3：原本都是 Python，怎麼動？

這是**遷移的真正關卡**，三條路：

| 路 | 可行性 | 說明 |
|---|---|---|
| A. Cloudflare Python Workers | 🔴 **不可行**（對本專案） | Pyodide 環境：pandas 勉強、**yfinance 不支援**（依賴 requests/curl_cffi 的原生行為）；CPU 時間限制撐不住「掃 60 檔 × 節流 sleep ≈ 8-10 分鐘」的工作型態 |
| B. Cloudflare Containers + Cron | 🟡 可行但沒必要 | 能跑原生 Python，但等於把「免費的 GitHub runner」換成「要付費管理的容器」，只為了排程準時——用大砲打排程 |
| C. **不搬運算**（推薦） | 🟢 | Python 原封不動留在 Actions；CF 只當「第二個鬧鐘」（見下方 Phase 1）——排程可靠性拿到手，一行 Python 都不用改 |
| D. 重寫成 JS/TS | 🔴 **明確不做** | 5,800+ 行 pandas 邏輯 + shadow log 生態 + 兩年校準紀錄，重寫的風險與工時遠大於它要解的問題。這條寫在這裡是為了將來有人被說服時翻出來看 |

---

## 三、路線圖（分階段，每階段獨立可停）

### Phase 0 — 已完成（2026-09-01，本次 commit）
- ✅ cron 全面錯峰（避開 :00/:15/:30/:45——GitHub 在熱門分鐘最容易延遲）
- ✅ 市場基準日（v3.13）：排程延遲跨日不再標錯天、不再被休市防呆誤殺，
  **延遲的 run 從「毒藥」變「無害的補跑」**
- ✅ 報表頭監控行：市場基準日 + 執行時間 + 補跑標記，延遲一眼可見
- 效果：GitHub 排程再犯同樣的病，傷害從「資料污染 + 整天漏掃」降為「晚幾小時拿到報表」

### Phase 1 — 第二個鬧鐘（條件觸發，半天工）
用 Cloudflare Worker（免費額度綽綽有餘）做**外部喚醒器**，不搬任何東西：
```
CF Cron Trigger（23:30 UTC 平日）
  → GitHub API: 查 scanner.yml 今日是否已有 run
  → 沒有 → POST /actions/workflows/scanner.yml/dispatches（workflow_dispatch）
```
- 需要：一個 fine-grained PAT（僅 actions:write）放 CF secret，約 40 行 Worker JS
- 這一步拿到「CF 級的排程可靠性」而 Python/資料/觀看全部原地不動
- **觸發條件：Phase 0 上線後，任何一個月仍有 ≥2 個交易日排程沒發**

### Phase 2 — 觀看層上 CF（純加分項，隨時可做可不做）
- 報表 md→html 上 R2 + Pages；GitHub README 照舊並存
- 觸發條件：真的想要更好的手機閱讀體驗，或報表要給不看 GitHub 的人看

### Phase 3 — 大型 CSV 分層進 R2（遠期，門檻高）
- 觸發條件：repo 大小影響 clone/checkout 速度（Actions 每次 checkout 變慢 >1 分鐘），
  或 GitHub 對 repo 大小提出警告
- 信號快照與 history 永遠留 git（審計理由，見 Q1）

### 永不階段
- 運算搬 CF Workers（技術不可行）、重寫 JS/TS（風險不對稱）、
  regime 類指標改即時計算（違反 CONTEXT 紅線一「慢是特性」）

---

## 四、逃生門總開關（什麼情況下推翻本文件、真的全面搬）

同時滿足才動：
1. Phase 1 的第二個鬧鐘上線後，**連續兩個月**每月仍有 ≥3 個交易日掃描沒跑成
2. 且 GitHub 官方明確改變 Actions 免費政策（額度/排程），使現架構不可持續

屆時的目的地也不必然是 Cloudflare——按當時行情重新比價（Fly.io / 一台 $5 VPS + cron /
CF Containers）。**一台 VPS + crontab 其實是這個工作型態最古老也最對症的解**，
只是它要自己管機器；先記在這裡，防止到時候只比較「GitHub vs Cloudflare」二選一。
