# cloudflare/ — 第二鬧鐘 + dashboard（Cloudflare Worker）

Python 與資料全部留在 GitHub Actions / git；這個資料夾只放 Worker。
部署**只靠 Cloudflare dashboard 的 Git 連動**，本機不需要 `wrangler login`。

## 一次性設定（Cloudflare dashboard）

1. **Workers & Pages → Create → Workers → Import a repository**，選 `clarencechien/optscnr`
2. Build 設定：
   - Root directory：`cloudflare`
   - Build command：留空
   - Deploy command：`npx wrangler deploy`
   - 只部署 `main`（Settings → Builds → Branch control：production branch = main，關掉 non-production branch builds）
3. **Settings → Variables and Secrets** 加 Secret：
   - `GITHUB_TOKEN`：GitHub fine-grained PAT，Repository access 只勾 `optscnr`，權限 **Actions: Read and write**、**Contents: Read**
   - （第 5 批接 LLM 時再加 `LLM_API_KEY`）
4. **Settings → Domains & Routes**：`workers.dev` 與 Preview URLs 已在 `wrangler.toml` 關閉；
   要開 dashboard 網頁請加 Custom domain（並把 `wrangler.toml` 的 `[[routes]]` 解開改成同一個網域）。
   沒有網域時 cron 仍照跑，只是沒有網頁。
5. 之後每次 push `main` 自動重新部署；`wrangler.toml` 的 cron 也隨部署更新。

## 它做什麼

| 時間 (UTC) | 動作 |
|---|---|
| 23:05 平日 | 檢查 22:00 之後 scanner.yml 有沒有任何 run；沒有 → `workflow_dispatch` |
| 00:35 週二~六 | 同上（GitHub 延遲 3-8 小時的事故形狀，跨日再檢查一次） |
| 任何時間 | `/api/health`：各 workflow 近 36 小時觸發時間；`/api/alarm/check`：手動補發 |

補發是安全的：主 scanner v3.13 用市場基準日與 signal_id 去重，跟稍後真的發出的排程 run 重疊不會重複記信號。

## 本機測試（選用）

```bash
cd cloudflare && npm i
cp .dev.vars.example .dev.vars   # 填 GITHUB_TOKEN
npx wrangler dev --test-scheduled
curl "http://localhost:8787/__scheduled?cron=5+23+*+*+1-5"
```

## 後續批次會加的東西（見 docs/PLAN_2026-09_strategy_dashboard.md 第 4.2、6 節）

- 第 4 批：dashboard 讀 `data/dashboard/candidates_*.json`、`data/strategy_matrix.json`（History 矩陣）
- 第 5 批：cron 內接 LLM（v4 三題 prompt），回答寫回 `data/decisions/<市場日>.json`（GitHub API commit）
