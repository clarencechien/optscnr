# cloudflare/ — 第二鬧鐘 + LLM decisions + dashboard（Cloudflare Worker）

Python 與資料全部留在 GitHub Actions / git；這個資料夾只放 Worker。
部署**只靠 Cloudflare dashboard 的 Git 連動**，本機不需要 `wrangler login`。

雙軌：**軌 A ＝ GitHub README**（Python 直接渲染，CF 掛了也在，含 🎯 結構候選與前一市場日的 🤖 LLM 三題）；
**軌 B ＝ 這個 dashboard**（同一批 JSON，加上 History 矩陣、逐日 Decisions log、事實庫、排程健康）。

## 一次性設定（Cloudflare dashboard）

1. **Workers & Pages → Create → Workers → Import a repository**，選 `clarencechien/optscnr`
2. Build 設定：
   - Root directory：`cloudflare`
   - Build command：留空
   - Deploy command：`npx wrangler deploy`
   - 只部署 `main`（Settings → Builds → Branch control：production branch = main，關掉 non-production branch builds）
3. **Settings → Variables and Secrets** 加 Secret：
   - `GITHUB_TOKEN`：GitHub fine-grained PAT，Repository access 只勾 `optscnr`，權限 **Actions: Read and write**、**Contents: Read and write**
     （第 5 批要寫 `data/decisions/` 與 `docs/FACTS_ledger.md` 待審段；原本 Contents: Read 的 PAT 要重發或改權限）
   - `LLM_API_KEY`：OpenRouter API key（`sk-or-v1-…`）
4. **Settings → Domains & Routes**：`workers.dev` 與 Preview URLs 已在 `wrangler.toml` 關閉；
   要開 dashboard 網頁請加 Custom domain（並把 `wrangler.toml` 的 `[[routes]]` 解開改成同一個網域）。
   沒有網域時 cron 仍照跑，只是沒有網頁。
5. 之後每次 push `main` 自動重新部署；`wrangler.toml` 的 cron 也隨部署更新。

### 模型怎麼選（`wrangler.toml` 的 `LLM_MODEL`，改了 push 即生效）

| 模型（OpenRouter slug） | 價格 / 1M tok（in / out） | 每交易日約 | 適合 |
|---|---|---|---|
| `anthropic/claude-opus-5`（**預設**） | $5 / $25 | ≈ US$0.05–0.15 | 三題要附來源、要判「事實庫 vs 新查證」衝突；一天一次，貴不到哪去 |
| `anthropic/claude-sonnet-5` | $2 / $10 | ≈ US$0.02–0.06 | 想省；三題答對率若與 Opus 無差（T8 累積 60 個交易日後可比） |
| `anthropic/claude-fable-5.1` | $10 / $50 | ≈ US$0.10–0.30 | 沒必要——三題不是推理難題 |

- 每次呼叫 ≈ prompt 2.5K + 候選與事實 1–4K tok 進、1–2K tok 出；web 外掛另計（OpenRouter 每千次結果 $4，每日 5 筆 ≈ $0.02）。
- **候選 0 筆的日子不呼叫 LLM**（直接記「今日無結構候選」），所以多數日子花費是零。
- 模型名記在 decisions JSON 的 `model_served`，之後 T8 可以分模型比答對率。

### （建議）Cloudflare Access：只讓自己看

dashboard 有兩個會花錢／會動 repo 的按鈕（補發 scanner、立即產生 decisions），公開網址不該裸奔。
WAF Challenge 只擋機器人，擋不了人；用 **Zero Trust Access**（免費方案 50 位使用者內）：

1. Cloudflare dashboard → **Zero Trust → Access → Applications → Add an application → Self-hosted**
2. Application domain：`optscnr.ai-apps.work`（整站）；Session duration 隨意（例如 24h）
3. Policy：Action **Allow**、Include → **Emails** → 你的 email；Login method 只留 **One-time PIN**（不用接 IdP）
4. 存檔後在 application Overview 抄 **Application Audience (AUD) Tag**
5. Worker → Settings → Variables and Secrets 加兩個變數（plain text 即可，不進 git）：
   - `ACCESS_TEAM_DOMAIN`＝`<你的 team>.cloudflareaccess.com`（Zero Trust → Settings → Custom Pages 看得到 team name）
   - `ACCESS_AUD`＝上面抄的 AUD

設了這兩個變數 Worker 才會驗 JWT（`Cf-Access-Jwt-Assertion` 簽章、aud、exp）；沒設就維持原樣。
兩層的用意：Access 設錯（例如 policy 打開了）時 Worker 端還是 401，`/api/decide` 不會被路人按。
Cron 不走 HTTP，不受 Access 影響。原本的 WAF Challenge 可以拿掉（Access 登入頁本身就會擋機器人）。

### 電子報 `/brief`（公開分享用、唯讀）

`/brief` 是一頁「一眼看懂」的版本：TL;DR、今日候選＋LLM 三題、History 摘要、資料正確與否。
它只讀 `/api/brief`（Worker 從 GitHub 彙整，快取 5 分鐘），**不會觸發 LLM、不會補發、沒有任何按鈕**；
`?d=2026-09-04` 可看某一天。Worker 端對 `/brief`、`/brief.html`、`/api/brief` 不驗 Access JWT。

要讓沒登入的人也能開，Cloudflare Access 那層還要放行這三個路徑（Access 在 Worker 之前就擋了）：

1. Zero Trust → Access → Applications → **Add an application → Self-hosted**（第二個 app，跟主 app 並存）
2. Application domain 加兩條：`optscnr.ai-apps.work/brief` 與 `optscnr.ai-apps.work/api/brief`
   （Access 的 path 是前綴比對，`/brief` 會涵蓋 `/brief.html`；不會涵蓋 `/api/decide`）
3. Policy：Action **Bypass**、Include → **Everyone**
4. 存檔即可，不用改 Worker。之後把 `https://optscnr.ai-apps.work/brief` 這個連結給誰都行。

不做這步也沒關係：你自己登入後 `/brief` 一樣能開，只是別人開會被 Access 擋。

## 它做什麼

| 時間 (UTC) | 動作 |
|---|---|
| 23:05 平日 | ① 第二鬧鐘：22:00 之後 scanner.yml 有沒有任何 run；沒有 → `workflow_dispatch` ② decisions（見下） |
| 00:35 週二~六 | 同上（GitHub 延遲 3-8 小時的事故形狀，跨日再檢查一次） |
| 02:05 週二~六 | 同上（decisions 最後一次補：補發的 scanner 到這時也該跑完了） |
| 任何時間 | `/api/health` 排程健康；`/api/alarm/check` 手動補發；`POST /api/decide` 手動產生 decisions；`/api/decisions` 最近 N 天；`/api/facts` 解析後的事實庫；**`/brief` + `/api/brief` 公開唯讀電子報** |

**decisions 流程（冪等，同一市場日只寫一次）**：讀 main 的 `data/dashboard/latest.json` → `data/decisions/<市場日>.json` 已存在就跳過
→ 候選 0 筆：不呼叫 LLM、直接記檔 → 否則讀 `docs/PROMPT_daily_report_reading_v4.md` 的 ```` ```prompt ```` 區塊（**改 prompt 不用重新部署**）
＋ `docs/FACTS_ledger.md` 裡候選標的段與通用段 → OpenRouter → 答案寫檔（GitHub Contents API，append-only）
→ LLM 提的 `facts_proposed`（必附 URL）附加到事實庫「待審（LLM 提案）」段。
事後 `shadow_tracer.backfill_decisions` 只補每筆的 `outcome`，不改答案。

補發是安全的：主 scanner v3.13 用市場基準日與 signal_id 去重，跟稍後真的發出的排程 run 重疊不會重複記信號。

## 現況（2026-09-08）

- 已部署到自訂網域、Access 已開（`/api/health` 回 `access.enforced: true`）、PAT 與 `LLM_API_KEY` 已設。
- 首次實跑（09-07，市場日 9/4）：`data/decisions/2026-09-04.json` 由「立即產生」按鈕寫入，0 候選未呼叫 LLM。
- 靜態頁由 Cloudflare 先供檔、不經 Worker：Access 變數設錯時會「頁面開得了、/api 全 401」，401 的 JSON 帶 `reason/hint`，頁面頂端會顯示。
- 改 `src/index.js` 前先跑 `node --check`，並用離線 mock 測試（GitHub API、OpenRouter、Access 全 mock；見 docs/log.md 第 5 批專節）。

## 本機測試（選用）

```bash
cd cloudflare && npm i
cp .dev.vars.example .dev.vars   # 填 GITHUB_TOKEN / LLM_API_KEY
npx wrangler dev --test-scheduled
curl "http://localhost:8787/__scheduled?cron=5+23+*+*+1-5"
curl -X POST http://localhost:8787/api/decide
```
