# C 池 L2 警報：接進 dashboard／電子報／推播（2026-10-21 handoff）

> 問題：Option Sage 從 9/4 到 10/15 連續 21 個交易日判定 L2（「就是這個」），人沒看到。
> 原因不在 gate（55% 絕對線 88 天裡綠了 34 天），在管道：L2 跟 L0 走同一條路、同一個音量，
> 判定沒進 history，亮了之後沒有人工回應的 SOP。
> 目標：下一次 L2 亮時，人一定在。做法照既有雙軌：**Python 算、Worker 轉發、brief 渲染**（同 `/api/tw` 模式）。
> 依據：`git log -- spcx_radar/output/spcx_options_report.md` 抽出的逐日判定；`spcx_iv_history.csv`（88 天）；`spcx_options_history.csv`（69 天）。

---

## 〇、先把事實釘住（不用重算，給接手的人看）

從 git 歷史抽出的 Sage 逐日判定（只列有 commit 的日子）：

| 日期 | 判定 | 價格 | ATM IV |
|---|---|---|---|
| 09/04 – 09/12 | **L2**（09/09 一天 L1） | $140–153 | 48–54% |
| 09/22 – 10/15 | **L2 連續 16 個交易日** | $145–172 | 43–55% |
| 10/16 – 10/21 | L1 | $146–148 | 62–66% |

同期 `space_radar_report.md` 的 C 池區塊也顯示「✅ IV 已連續穩定冷卻 — C 池可開始評估」。兩個模組都亮，所以**不是邏輯 bug，是人機介面**。

三個缺口：
1. **L2 與 L0 同管道同音量**——每天覆寫同一份 md、commit；沒有推播、commit message 無差異。
2. **判定沒留紀錄**——`spcx_options_history.csv` 有 IV/INT/skew，沒有 `level`；要證明亮過得翻 git。
3. **沒有回應時限**——設計文件寫「模組是 gate 不是 hand」，但沒寫亮了之後人要在幾天內做什麼。跳過也沒留痕。

另：9/14–18、10/8–9 Sage 沒跑（`continue-on-error` 吞掉），也沒聲音。

---

## 一、設計決策（已定，不要再討論）

1. **Worker 不算任何判定。** 所有判定在 Python（Actions）做完、寫成 JSON；Worker 只轉發加快取。
2. **三個掛點 + 一條推播，一次做完：**
   - **(a) `/brief` 頂部跨市場橫幅**：不管 `?m=us` 或 `?m=tw`，只要 SPCX C 池處於 L2、或 L2 在最近 5 個交易日內關掉，頁面第一行之上出現一條橫幅。這是「不會忘了看」的關鍵——人每天看的是 US/TW 那頁，不是 SPCX 頁。
   - **(b) `/brief?m=spcx` 第三個市場分頁**：完整資料（四條件、IV 雙軌、Sage 列的可用 strike、觀點、L2 已亮天數、人工回應狀態、隱含融資成本）。
   - **(c) dashboard `index.html` 一顆燈**：與既有排程健康燈並列，顏色＝level。
   - **(d) 轉換事件推播**：`level` 與前一市場日不同（任何方向）→ 推播一則；Sage 跑失敗也推。
3. **人工回應留痕**：新增 `spcx_radar/config/spcx_c_decisions.json`（append-only，手動維護）。L2 亮燈後 **2 個交易日內**要有一筆（`act` 或 `skip` + 理由）；逾期 brief 橫幅標紅「未回應」。
4. **不改 gate 的任何閾值**（55%、分位 40、連續 3 天都不動）。資料證明它們可達；這次修的是管道不是尺。
5. **brief 不給 strike 建議**，只原樣轉 Sage 的 `liquidity.detail`（價差最窄前幾名），照「gate 不是 hand」。

---

## 二、資料層：新增 `spcx_radar/spcx_brief.py` → `spcx_radar/output/spcx_brief.json`

照 `tw_scanner/tw_brief.py` 的角色：排程最後一步，把當天幾份 JSON 組成 brief 專用的一份。
輸入：`output/space_radar.json`、`output/spcx_options.json`、`output/spcx_options_history.csv`、`config/spcx_dca_log.json`、`config/spcx_c_viewpoint.json`、`config/spcx_c_decisions.json`。

### 2.1 先改 `spcx_options.py`（兩處）

- `record_options_history()` 的 `record` 加兩欄：`level`（L0/L1/L2）、`transition`（`None` 或 `"L1->L2"` 這種字串，比對 history 最後一筆的 level）。
- `main()` 把 `level` 算完再呼叫 `record_options_history`（現在是先記錄再判定，順序要對調；`level` 已在 `output` dict 裡，直接帶進去）。
- **回填**：寫一支一次性 `spcx_radar/backfill_level.py`，用 `spcx_iv_history.csv` 逐日重算分位／穩定／絕對線，配 `spcx_options_history.csv` 的 `total_int` 與 viewpoint 生效日（2026-08-18 起 5/5）回填 `level`、`transition`。重算邏輯直接 import `spcx_options` 的 `get_iv_signal` 等函式，不要另寫一套。
  驗收：回填後 history 中 `level=='L2'` 的段應為兩段（9 月上旬、9/22–10/15）。

### 2.2 `spcx_brief.json` schema

```json
{
  "generated_at": "2026-10-21T00:41:16Z",
  "market_date": "2026-10-20",
  "days_since_ipo": 131,
  "price": 147.96,
  "market_cap_t": 1.95,
  "c_pool": {
    "level": "L1",
    "level_prev": "L1",
    "transition": null,
    "l2_streak_days": 0,
    "l2_last_date": "2026-10-15",
    "l2_days_since_close": 3,
    "conditions": {
      "iv_rel_calm_stable": false,
      "iv_abs_ok": false,
      "liquidity_ok": true,
      "viewpoint_ok": true
    },
    "iv": { "atm": 0.655, "pctile": 51.1, "stable": false, "leaps_atm": 0.595, "leaps_exp": "2029-01-19", "abs_gate": 0.55 },
    "liquidity": { "total_int": 1150288, "usable_strikes": 107, "best_spread_pct": 0.017 },
    "skew": "neutral",
    "viewpoint": { "confidence": 5, "catalyst": "…", "thesis": "…", "updated": "2026-08-18" },
    "strikes": [ { "exp": "2028-12-15", "strike": 100, "bid": 72.0, "ask": 73.25, "oi": 7703, "spread_pct": 0.017,
                   "intrinsic": 47.96, "extrinsic": 24.67, "carry_pct_annual": 7.7 } ],
    "response": { "required": false, "deadline": null, "status": "n/a", "last": null }
  },
  "positions": { "shares": 779, "avg_cost": 145.56, "unrealized_pct": 1.6, "pool_c_cash": 20000 },
  "sage_health": { "last_run": "2026-10-21T00:41Z", "missed_days": ["2026-10-08", "2026-10-09"] },
  "checks": [ { "level": "GREEN", "label": "Sage 今日有跑", "text": "…" } ],
  "do_line": "C 池：L1 觀察。IV 66% 在財報事件溢價裡，等它回到 45–50%（這檔的冷靜態）。",
  "items": [ "…白話三四句…" ]
}
```

欄位說明：
- `l2_streak_days`：連續 L2 的交易日數（從 history 的 `level` 序列算）。
- `l2_days_since_close`：最近一次 L2 結束到今天的交易日數；橫幅在 ≤5 時仍顯示（「剛關門」也要讓人知道）。
- `strikes[].carry_pct_annual`：`extrinsic / price / (DTE/365) × 100`。深價內 LEAPS 的真實成本是外在價值，不是 IV；這欄是輔助指標，不是 gate。（10/20 例：2028-12 $100C mid 72.6、內在 47.96 → 外在 24.7 ＝ 股價 16.7%，26 個月 → 約 7.7%/年。）
- `response`：讀 `spcx_c_decisions.json`，規則見第四節。
- `do_line` / `items`：給 brief 上半白話版用，Python 組好，Worker/前端不生成文字。

---

## 三、Worker 與前端

### 3.1 `cloudflare/src/index.js`

- 第 537 行 `PUBLIC_PATHS` 加 `"/api/spcx"`。
- 第 538 行旁加 `const SPCX_BRIEF_PATH = "spcx_radar/output/spcx_brief.json";`
- 第 634–645 行 `/api/tw` 那段**原樣複製**成 `/api/spcx`（cache key、`ghGetJson`、404 文案、`max-age=300` 全照抄）。404 文案：`"spcx_brief.json 尚未產生（space_radar 排程跑完才有）"`。
- 第 617 行同款：`/api/brief?m=spcx` → 302 到 `/api/spcx`。
- 不碰 Access / decisions / cron。

### 3.2 `cloudflare/public/brief.html`

- 第 97 行 `#switch` 加第三鍵：`<a href="/brief?m=spcx" data-m="spcx">SPCX C 池</a>`。
- 第 100 行 `#simple` **之上**插一個 `<div id="spcx-banner" hidden></div>`：這是跨市場橫幅，三種市場視圖都會渲染它。
- 第 124 行 `<section id="tw">` 之後加 `<section id="spcx" hidden>`，`<details class="sec">` 六段：
  1. 本回合判定（四條件燈 + L2 已亮天數 + 人工回應狀態）
  2. IV 雙軌（ATM / 分位 / 連續穩定 / LEAPS IV / 絕對線）
  3. 可用 strike（Sage 原樣，含 carry_pct_annual；表格包 `.scroll`）
  4. 觀點（catalyst / thesis / 信心 / 更新日；若 `updated` 超過 60 天標黃「觀點可能過期」）
  5. 持倉與 C 池現金
  6. 資料健康（Sage 有沒有跑、缺的日子）
- 第 292 行 `renderTW` 旁新增 `renderSPCX(b)`，第 281 行 `renderSimple` 直接用 `b.do_line` / `b.items` / `b.checks`。
- 第 361–388 行切換邏輯：`tw` 布林改成 `market` 三值（`us|tw|spcx`）；`document.title`、`#title`、三個 section 的 `hidden`、foot 都照三值切。
- **橫幅邏輯（新增，在主渲染之後再 fetch 一次）**：
  ```js
  // 跨市場：不論看哪一頁，L2 或剛關門都要看到
  try {
    const s = await (await fetch('/api/spcx', { cache: 'no-store' })).json();
    const c = s.c_pool || {};
    const show = c.level === 'L2' || (c.l2_days_since_close != null && c.l2_days_since_close <= 5);
    if (show) {
      const el = $('#spcx-banner');
      el.hidden = false;
      el.className = 'banner ' + (c.level === 'L2' ? (c.response.status === 'overdue' ? 'red' : 'green') : 'yellow');
      el.innerHTML = c.level === 'L2'
        ? `🟢🟢🟢 <b>SPCX C 池 L2「就是這個」已亮 ${c.l2_streak_days} 個交易日</b>｜回應狀態：${esc(c.response.status)}${c.response.deadline ? `（期限 ${c.response.deadline}）` : ''}｜<a href="/brief?m=spcx">看完整</a>`
        : `🟡 SPCX C 池 L2 在 ${c.l2_days_since_close} 個交易日前關門（最後 ${esc(c.l2_last_date)}）｜<a href="/brief?m=spcx">看完整</a>`;
    }
  } catch (_) { /* SPCX 資料讀不到不影響主頁 */ }
  ```
  CSS：`.banner` 固定在頁首下方、手機全寬、三色（green/yellow/red）用既有 `.light` 的色票。

### 3.3 `cloudflare/public/index.html`（dashboard）

- 排程健康燈那排加一顆「SPCX C 池」，顏色＝`c_pool.level`（L0 灰、L1 黃、L2 綠；`response.status==='overdue'` 時紅閃），點了開 `/brief?m=spcx`。
- 不加任何按鈕（C 池沒有可觸發的動作）。

### 3.4 Zero Trust Access

- Bypass 應用程式加兩條 path：`/api/spcx`（`/brief` 已涵蓋帶參數的情況）。README 的「電子報」一節補一行。

---

## 四、人工回應：`spcx_radar/config/spcx_c_decisions.json`

append-only，手動維護，格式：

```json
{
  "_說明": "C 池 L2 亮燈後的人工回應。每次 L2 段落（transition 到 L2 起算）2 個交易日內必須有一筆；跳過也要寫理由，不然下次還是靜默錯過。",
  "decisions": [
    { "date": "2026-10-23", "l2_start": "2026-10-22", "action": "skip", "reason": "viewpoint 的兩個催化劑都是公開資訊，不構成市場定價錯；等 12/8 全解鎖後再看", "by": "clarence" },
    { "date": "2026-11-03", "l2_start": "2026-11-02", "action": "act", "detail": "2028-12 $100C ×2，占 C 池 48%", "reason": "…", "by": "clarence" }
  ]
}
```

`spcx_brief.py` 計算 `response`：
- 今日 `level=='L2'` → `required=true`；`deadline` ＝ 本段 L2 起始日 + 2 個交易日。
- 本段 `l2_start` 以後有 decision → `status="answered"`（帶 `last`）；沒有且今天 ≤ deadline → `"pending"`；沒有且已過 → `"overdue"`（橫幅轉紅、dashboard 燈閃）。
- 非 L2 → `required=false, status="n/a"`。

PLAYBOOK.md 加一節「C 池 L2 回應 SOP」（三步，照設計文件的精神）：
1. 重讀 `spcx_c_viewpoint.json`：信心定義 4＝「有把握市場某處定價錯且我知道為什麼」。問自己：這個催化劑市場知道嗎？知道就不是觀點，是新聞。
2. 看 Sage 列的可用 strike 與 `carry_pct_annual`，跟 SGOV 殖利率比。
3. 2 個交易日內寫一筆 decision：`act`（≤ C 池一半，輸了不補）或 `skip`（寫理由）。

---

## 五、推播（轉換事件）

`.github/workflows/space_radar.yml`，在 `Run option sage` 之後、`Build folder README` 之前加一步：

```yaml
- name: Notify on C-pool transition
  if: always()
  run: python spcx_radar/notify_transition.py
  env:
    NOTIFY_URL: ${{ secrets.SPCX_NOTIFY_URL }}
    NOTIFY_TOKEN: ${{ secrets.SPCX_NOTIFY_TOKEN }}
```

`notify_transition.py`：讀 `output/spcx_brief.json`（或 Sage 的 json）；若 `c_pool.transition` 非空、或 `sage_health.last_run` 不是今天（＝Sage 沒跑）→ POST 一則。管道二選一，先不要兩個都做：
- **BentoDrop**（你自己的推送 PWA，bentodrop.ai-apps.work）：用它現有的推送 endpoint；
- 或 GitHub Actions 的 email action（`dawidd6/action-send-mail` 之類）。

內容固定格式：`SPCX C 池：L1->L2｜價 $148｜IV 47%｜回應期限 10/24｜/brief?m=spcx`。
**只在轉換時推，L2 持續中每天不推**（避免變成另一個被忽略的噪音）；但 `overdue` 第一天再推一次。

---

## 六、不做的事

- Worker 不算 gate、不讀 history、不碰 viewpoint。
- brief 不建議 strike、不算部位、不自動下單。
- 不改 Sage 任何閾值；不改 space_radar C 池區塊的舊邏輯（它和 Sage 已一致，留著當第二意見）。
- 不把 SPCX 併進 US 電子報的候選表；它是第三個市場分頁，橫幅是唯一跨頁的東西。
- 推播不每日發；只發轉換與失敗。

---

## 七、驗收

1. `backfill_level.py` 跑完：`spcx_options_history.csv` 多 `level`、`transition` 兩欄；`grep -c L2` 應為 21±3（有 commit 的日子）；`transition` 非空的列 ≈ 6。
2. 用 10/7 的歷史 JSON 當 `spcx_brief.json` 餵本機 Worker（docs/log.md 第 5 批的 mock 方式）：`/brief?m=us` 與 `/brief?m=tw` 都出現綠橫幅「已亮 N 個交易日」；`/brief?m=spcx` 六段都有資料；dashboard 燈為綠。
3. 用 10/21 的 JSON：橫幅為黃「3 個交易日前關門（最後 10/15）」。
4. `decisions` 空 + L2 第 3 天的 JSON：橫幅紅、`response.status=="overdue"`、dashboard 燈閃。
5. `node --check src/index.js` 過；手機寬度下 strike 表橫向捲、頁面不橫捲。
6. Actions 手動 `workflow_dispatch` 一次：`spcx_brief.json` 產出、`/api/spcx` 回 200、快取 5 分鐘生效。
7. 推播：手動把 history 最後一筆 level 改掉再跑一次 → 收到一則；改回來。

## 八、順序與估時

| 步 | 內容 | 估時 |
|---|---|---|
| 1 | `spcx_options.py` 加 level/transition + `backfill_level.py` | 1 h |
| 2 | `spcx_brief.py` + `spcx_c_decisions.json` 範本 + workflow 加步驟 | 1.5 h |
| 3 | Worker `/api/spcx` + Access Bypass path | 20 min |
| 4 | brief.html 第三分頁 + 跨市場橫幅 + renderSPCX | 2 h |
| 5 | index.html 燈 | 20 min |
| 6 | `notify_transition.py` + secrets | 40 min |
| 7 | 驗收 1–7 | 1 h |

先做 1–2（資料層對了，後面都是渲染）。做完 4 之後就算推播沒接，橫幅已經解決「忘了看」——因為你每天看的那一頁會先擋你。

---

_背景：這次 L2 窗口兩段合計 21 個交易日、價格 $140–172、IV 43–55%；10/15 最後一天是 $152 / 55%，財報前五天。管道修好之前，下一次窗口（12/8 全解鎖前後，IV 回到 45–50% 是這檔的常態）大概率會再開。_
