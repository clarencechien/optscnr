/**
 * optscnr Cloudflare Worker — 第二鬧鐘 + LLM decisions + dashboard 供檔
 *
 * 職責（刻意極小，Python 全部留在 GitHub Actions）：
 *   1. scheduled()：
 *      a. 第二鬧鐘：今天「該發的那一發」scanner run 發了沒；沒發 → workflow_dispatch
 *      b. 第 5 批：main 上的 data/dashboard/latest.json 若是新市場日且還沒有
 *         data/decisions/<市場日>.json → 讀 docs/PROMPT_daily_report_reading_v4.md 的 prompt
 *         → 呼叫 LLM（OpenRouter，OpenAI 相容格式）→ GitHub Contents API 建檔（append-only）
 *   2. fetch()：/api/health、/api/alarm/check、/api/decide、/api/decisions；其餘靜態 dashboard
 *   3. （選）Cloudflare Access：設了 ACCESS_TEAM_DOMAIN + ACCESS_AUD 就驗每個請求的 JWT，
 *      Access 設錯時 /api/decide 這種會花錢的端點也不會裸奔
 *
 * 背景：2026-08-26 起 GitHub schedule 反覆延遲 3-8 小時甚至丟棄（docs/log.md 3.13 專節、
 * docs/PROJECT_ESCAPE_DOOR.md Phase 1）。Cloudflare Cron Trigger 準時，所以用它當外部鬧鐘。
 */

const GH = "https://api.github.com";
const PROMPT_PATH = "docs/PROMPT_daily_report_reading_v4.md";
const LEDGER_PATH = "docs/FACTS_ledger.md";
const LATEST_PATH = "data/dashboard/latest.json";
const DECISIONS_DIR = "data/decisions";
const LEDGER_GENERAL = ["環境", "判決", "校準", "工具"];
const LEDGER_PENDING = "待審（LLM 提案）";

// ------------------------------------------------------------------ GitHub
function ghHeaders(env) {
  return {
    "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "optscnr-cloudflare-worker",
  };
}

function repoUrl(env, path) {
  return `${GH}/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/${path}`;
}

/** 讀 main 上的檔（Contents API，不走 raw CDN：raw 有 5 分鐘快取，剛 push 的檔會讀到舊的）。
 *  不存在回 null；其餘錯誤丟出。 */
async function ghGetFile(env, path) {
  const ref = env.DEFAULT_BRANCH || "main";
  const r = await fetch(repoUrl(env, `contents/${path}?ref=${ref}`), { headers: ghHeaders(env) });
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`get ${path}: ${r.status}`);
  const j = await r.json();
  const bytes = Uint8Array.from(atob(j.content.replace(/\n/g, "")), c => c.charCodeAt(0));
  return { sha: j.sha, text: new TextDecoder().decode(bytes) };
}

async function ghGetJson(env, path) {
  const f = await ghGetFile(env, path);
  return f ? JSON.parse(f.text) : null;
}

/** 建新檔（append-only：不傳 sha，檔已存在時 GitHub 回 422，我們就當「別人先寫了」放棄）。 */
async function ghCreateFile(env, path, text, message) {
  const bytes = new TextEncoder().encode(text);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  const r = await fetch(repoUrl(env, `contents/${path}`), {
    method: "PUT",
    headers: { ...ghHeaders(env), "Content-Type": "application/json" },
    body: JSON.stringify({ message, content: btoa(bin), branch: env.DEFAULT_BRANCH || "main" }),
  });
  if (r.status === 422) return { created: false, reason: "exists" };
  if (!r.ok) throw new Error(`create ${path}: ${r.status} ${await r.text()}`);
  return { created: true, commit: (await r.json()).commit?.sha };
}

/** 更新既有檔（需要讀到的 sha；別人先改了會 409，呼叫端自行重讀重試） */
async function ghUpdateFile(env, path, text, message, sha) {
  const bytes = new TextEncoder().encode(text);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  const r = await fetch(repoUrl(env, `contents/${path}`), {
    method: "PUT",
    headers: { ...ghHeaders(env), "Content-Type": "application/json" },
    body: JSON.stringify({ message, content: btoa(bin), sha, branch: env.DEFAULT_BRANCH || "main" }),
  });
  if (r.status === 409 || r.status === 422) return { updated: false, status: r.status };
  if (!r.ok) throw new Error(`update ${path}: ${r.status} ${await r.text()}`);
  return { updated: true, commit: (await r.json()).commit?.sha };
}

async function ghListDir(env, path) {
  const r = await fetch(repoUrl(env, `contents/${path}?ref=${env.DEFAULT_BRANCH || "main"}`), { headers: ghHeaders(env) });
  if (r.status === 404) return [];
  if (!r.ok) throw new Error(`list ${path}: ${r.status}`);
  return (await r.json()).filter(x => x.type === "file" && x.name.endsWith(".json")).map(x => x.name);
}

// ------------------------------------------------------------------ 第二鬧鐘
/** 今天（UTC）該發的那一發的「排定時刻」：以 SCANNER_CRON_UTC_HOUR 為準。
 *  00:35 那發檢查的是「前一個 UTC 日」的排定 run（跨日補檢查）。 */
function expectedFireTime(now, env) {
  const hour = parseInt(env.SCANNER_CRON_UTC_HOUR || "22", 10);
  const t = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), hour, 0, 0));
  if (now < t) t.setUTCDate(t.getUTCDate() - 1); // 現在還沒到今天的排定時刻 → 看昨天那一發
  return t;
}

async function listRunsSince(env, workflowFile, sinceIso) {
  const url = repoUrl(env, `actions/workflows/${workflowFile}/runs`)
    + `?created=%3E%3D${encodeURIComponent(sinceIso)}&per_page=10`;
  const r = await fetch(url, { headers: ghHeaders(env) });
  if (!r.ok) throw new Error(`list runs ${workflowFile}: ${r.status}`);
  return (await r.json()).workflow_runs || [];
}

async function dispatch(env, workflowFile) {
  const r = await fetch(repoUrl(env, `actions/workflows/${workflowFile}/dispatches`), {
    method: "POST",
    headers: { ...ghHeaders(env), "Content-Type": "application/json" },
    body: JSON.stringify({ ref: env.DEFAULT_BRANCH || "main" }),
  });
  if (r.status !== 204) throw new Error(`dispatch ${workflowFile}: ${r.status} ${await r.text()}`);
}

/** 第二鬧鐘核心：排定時刻之後有沒有任何 run（schedule 或 dispatch 都算）；沒有就補發。
 *  週末（UTC 週六/日）不補：美股休市，補發只會重播週五收盤。 */
async function secondAlarm(env, now) {
  const dow = now.getUTCDay();
  if (dow === 0 || dow === 6) return { checked_at: now.toISOString(), action: "weekend_skip" };
  const expected = expectedFireTime(now, env);
  // 排定時刻前 10 分鐘起算，涵蓋 GitHub 偶爾提早幾分鐘發的情況
  const since = new Date(expected.getTime() - 10 * 60 * 1000).toISOString();
  const runs = await listRunsSince(env, env.SCANNER_WORKFLOW, since);
  const result = { checked_at: now.toISOString(), expected_fire: expected.toISOString(), runs: runs.length, action: "none" };
  if (runs.length === 0) {
    await dispatch(env, env.SCANNER_WORKFLOW);
    result.action = "dispatched";
  }
  console.log(JSON.stringify({ event: "second_alarm", ...result }));
  return result;
}

/** /api/health：各 workflow 最近一次觸發時間，dashboard「排程」區用 */
async function health(env) {
  const now = new Date();
  // 84 小時：週一下午看得到週五的 run（36 小時會把週末正常沒跑的 workflow 標成紅的）
  const since = new Date(now.getTime() - 84 * 3600 * 1000).toISOString();
  const workflows = ["scanner.yml", "catalyst_fetch.yml", "unknown_radar.yml", "space_radar.yml", "tw_scanner.yml", "delta_radar.yml"];
  const out = {};
  for (const wf of workflows) {
    try {
      const runs = await listRunsSince(env, wf, since);
      out[wf] = runs.slice(0, 3).map(r => ({
        event: r.event, status: r.status, conclusion: r.conclusion,
        created_at: r.created_at, updated_at: r.updated_at, url: r.html_url,
      }));
    } catch (e) {
      out[wf] = { error: String(e) };
    }
  }
  return {
    generated_at: now.toISOString(),
    window_hours: 84,
    expected_scanner_fire: expectedFireTime(now, env).toISOString(),
    llm: { configured: Boolean(env.LLM_API_KEY), model: env.LLM_MODEL || null, web_search: env.LLM_WEB_SEARCH === "1" },
    access: { enforced: Boolean(env.ACCESS_TEAM_DOMAIN && env.ACCESS_AUD) },
    workflows: out,
  };
}

// ------------------------------------------------------------------ 第 5 批：LLM decisions
/** 從 docs/PROMPT_daily_report_reading_v4.md 抽 ```prompt 區塊；第一行 prompt_version: 是版本。 */
async function loadPrompt(env) {
  const f = await ghGetFile(env, PROMPT_PATH);
  if (!f) throw new Error(`${PROMPT_PATH} 不存在`);
  const m = f.text.match(/```prompt\s*\n([\s\S]*?)\n```/);
  if (!m) throw new Error("prompt 檔沒有 ```prompt 區塊");
  const body = m[1];
  const v = body.match(/^prompt_version:\s*(\S+)/m);
  return { version: v ? v[1] : "unknown", text: body.replace(/^prompt_version:.*\n?/m, "").trim() };
}

// ---- 事實庫（docs/FACTS_ledger.md）：格式規則寫在該檔檔頭 ----
/** 解析成 {sections: [{key, title, items:[...]}]}；key＝段名第一個大寫英數 token（T（AT&T）→ T）或通用段名。 */
export function parseLedger(md) {
  const sections = [];
  let cur = null;
  for (const line of md.split("\n")) {
    const h = line.match(/^##\s+(.+?)\s*$/);
    if (h) {
      const title = h[1];
      const tk = title.match(/^([A-Z][A-Z0-9.\-]*)/);
      const key = LEDGER_GENERAL.includes(title) ? title : (title.startsWith(LEDGER_PENDING) ? "__pending__" : (tk ? tk[1] : title));
      cur = { key, title, items: [] };
      sections.push(cur);
      continue;
    }
    if (!cur) continue;
    const t = line.trim();
    if (t.startsWith("- ")) cur.items.push(t.slice(2));
    else if (t && !t.startsWith("<!--") && cur.items.length && line.startsWith("  ")) cur.items[cur.items.length - 1] += " " + t;
  }
  return { sections };
}

/** 給 LLM 的事實：候選標的各段全部（每條截 600 字、最多 12 條）＋ 通用段最新 5 條 */
function factsFor(ledger, tickers) {
  const clip = s => (s.length > 600 ? s.slice(0, 600) + "…" : s);
  const by_ticker = {};
  for (const t of tickers) {
    const items = ledger.sections.filter(s => s.key === t).flatMap(s => s.items);
    if (items.length) by_ticker[t] = items.slice(-12).map(clip);
  }
  const general = {};
  for (const g of LEDGER_GENERAL) {
    const items = ledger.sections.filter(s => s.key === g).flatMap(s => s.items);
    if (items.length) general[g] = items.slice(-5).map(clip);
  }
  return { by_ticker, general, source: LEDGER_PATH };
}

/** 把 LLM 的 facts_proposed 附加到「待審（LLM 提案）」段（沒有 URL 的不收；段不存在就補在檔尾） */
async function appendProposals(env, proposals, mkt) {
  const rows = (proposals || []).filter(p => p && p.ticker && p.fact && /^https?:\/\//.test(String(p.source || "")))
    .map(p => `- ${String(p.ticker).toUpperCase().slice(0, 12)} ｜ ${String(p.fact).replace(/\s*\n\s*/g, " ").slice(0, 400)} ｜ ${p.date || "日期未知"} ｜ ${p.source} ｜ ${mkt} LLM 提案`);
  if (!rows.length) return { appended: 0 };
  for (let attempt = 0; attempt < 3; attempt++) {
    const f = await ghGetFile(env, LEDGER_PATH);
    if (!f) return { appended: 0, reason: "ledger_missing" };
    const marker = `## ${LEDGER_PENDING}`;
    let text = f.text.replace(/\s+$/, "") + "\n";
    if (!text.includes(marker)) text += `\n---\n\n${marker}\n<!-- Worker 自動附加；審過請搬到該標的段落 -->\n`;
    // 去重：同 ticker 同 source 已在檔內就不再附
    const fresh = rows.filter(r => { const src = r.split(" ｜ ")[3]; return !text.includes(src); });
    if (!fresh.length) return { appended: 0, reason: "duplicate" };
    text += fresh.join("\n") + "\n";
    const res = await ghUpdateFile(env, LEDGER_PATH, text, `📚 FACTS 待審：${mkt} LLM 提案 ${fresh.length} 條 [skip ci]`, f.sha);
    if (res.updated) return { appended: fresh.length };
  }
  return { appended: 0, reason: "conflict" };
}

/** 送給 LLM 的候選欄位（去掉 dashboard 用的顯示欄，保留三題需要的） */
function trimCandidate(c) {
  const keep = ["signal_id", "ticker", "expiry", "strike", "dte", "spot", "otm_pct", "last", "iv", "oi", "oi_d7",
    "oi_delta_status", "volume", "score", "features", "warnings", "events", "recent_spots", "strategy_label"];
  const o = {};
  for (const k of keep) if (c[k] !== undefined) o[k] = c[k];
  return o;
}

/** 從 LLM 回覆抽 JSON（模型偶爾還是會包 ``` 圍欄或前後加一句話） */
function extractJson(text) {
  const t = String(text || "").trim();
  try { return JSON.parse(t); } catch {}
  const fenced = t.match(/```(?:json)?\s*\n?([\s\S]*?)```/);
  if (fenced) { try { return JSON.parse(fenced[1].trim()); } catch {} }
  const a = t.indexOf("{"), b = t.lastIndexOf("}");
  if (a >= 0 && b > a) { try { return JSON.parse(t.slice(a, b + 1)); } catch {} }
  return null;
}

async function callLLM(env, systemPrompt, userPayload) {
  const base = (env.LLM_BASE_URL || "https://openrouter.ai/api/v1").replace(/\/$/, "");
  const body = {
    model: env.LLM_MODEL || "anthropic/claude-opus-5",
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: JSON.stringify(userPayload) },
    ],
    temperature: 0,
    max_tokens: parseInt(env.LLM_MAX_TOKENS || "6000", 10),
  };
  // OpenRouter web 外掛：第 (a) 題「排定事件＋來源 URL」要靠它；不要就把 LLM_WEB_SEARCH 設成 0
  if (env.LLM_WEB_SEARCH === "1") body.plugins = [{ id: "web", max_results: parseInt(env.LLM_WEB_MAX_RESULTS || "5", 10) }];
  const r = await fetch(`${base}/chat/completions`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.LLM_API_KEY}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://github.com/clarencechien/optscnr",
      "X-Title": "optscnr decisions",
    },
    body: JSON.stringify(body),
  });
  const text = await r.text();
  if (!r.ok) throw new Error(`LLM ${r.status}: ${text.slice(0, 500)}`);
  const j = JSON.parse(text);
  const content = j.choices?.[0]?.message?.content ?? "";
  return { content: typeof content === "string" ? content : JSON.stringify(content), model_served: j.model || body.model, usage: j.usage || null };
}

/**
 * 決策流程（冪等：同一市場日只寫一次）：
 *   latest.json 的 market_date → 已有 decisions/<日>.json？有 → 跳過
 *   候選 0 筆 → 不呼叫 LLM，直接記「今日無結構候選」
 *   否則 → prompt v4 + 候選 → LLM → 組檔 → Contents API 建檔
 */
async function runDecision(env, { source = "cron" } = {}) {
  const startedAt = new Date().toISOString();
  const latest = await ghGetJson(env, LATEST_PATH);
  if (!latest) return { action: "no_latest_json" };
  const mkt = latest.market_date;
  const path = `${DECISIONS_DIR}/${mkt}.json`;
  if (await ghGetFile(env, path)) return { action: "exists", market_date: mkt };
  if (!env.LLM_API_KEY) return { action: "llm_not_configured", market_date: mkt };

  const prompt = await loadPrompt(env);
  const cands = latest.candidates || [];
  // 事實庫：讀不到也照跑（facts 空），但記在 record 裡
  let facts = { by_ticker: {}, general: {}, source: LEDGER_PATH, error: null };
  if (cands.length) {
    try { facts = { ...factsFor(parseLedger((await ghGetFile(env, LEDGER_PATH))?.text || ""), [...new Set(cands.map(c => c.ticker))]), error: null }; }
    catch (e) { facts.error = String(e); }
  }
  const base = c => ({
    signal_id: c.signal_id, ticker: c.ticker, expiry: c.expiry, strike: c.strike, entry_price: c.last,
    strategy: c.strategy, strategy_label: c.strategy_label, sell_points: c.sell_points,
    facts_used: (facts.by_ticker[c.ticker] || []).length,
  });
  const record = {
    market_date: mkt, decided_at: startedAt, source, prompt_version: prompt.version,
    model: env.LLM_MODEL || "anthropic/claude-opus-5", model_served: null,
    llm_called: false, web_search: env.LLM_WEB_SEARCH === "1",
    candidates_generated_at: latest.generated_at, n_candidates: cands.length,
    facts_general_n: Object.values(facts.general).reduce((a, b) => a + b.length, 0), facts_error: facts.error,
    candidates: [], facts_proposed: [], facts_appended: 0, raw_answer: null, usage: null, error: null,
  };

  if (cands.length === 0) {
    record.note = "今日無結構候選（空手是正確執行，不補名額；未呼叫 LLM）";
  } else {
    try {
      const { error: _e, ...factsPayload } = facts;
      const res = await callLLM(env, prompt.text, { market_date: mkt, candidates: cands.map(trimCandidate), facts: factsPayload });
      record.llm_called = true;
      record.model_served = res.model_served;
      record.usage = res.usage;
      record.raw_answer = res.content;
      const parsed = extractJson(res.content);
      const byId = new Map(((parsed && parsed.candidates) || []).map(x => [x.signal_id, x]));
      record.candidates = cands.map(c => {
        const a = byId.get(c.signal_id);
        return a
          ? { ...base(c), q_event: a.q_event ?? null, q_gap: a.q_gap ?? null, q_delta: a.q_delta ?? null, note: a.note ?? null, status: "answered" }
          : { ...base(c), q_event: null, q_gap: null, q_delta: null, note: null, status: "unanswered" };
      });
      if (!parsed) record.error = "LLM 回覆不是可解析的 JSON（raw_answer 保留）";
      record.facts_proposed = Array.isArray(parsed?.facts_proposed) ? parsed.facts_proposed.slice(0, 20) : [];
      if (record.facts_proposed.length) {
        try { record.facts_appended = (await appendProposals(env, record.facts_proposed, mkt)).appended; }
        catch (e) { record.facts_error = `append: ${String(e).slice(0, 300)}`; }
      }
    } catch (e) {
      // LLM 失敗也要留檔：T8 的分母是「有候選的交易日」，缺檔會讓後面的統計偏樂觀
      record.error = String(e).slice(0, 1000);
      record.candidates = cands.map(c => ({ ...base(c), q_event: null, q_gap: null, q_delta: null, note: null, status: "error" }));
    }
  }

  const put = await ghCreateFile(env, path, JSON.stringify(record, null, 2) + "\n",
    `🤖 decisions ${mkt}（${record.llm_called ? record.model_served : "no-llm"}）[skip ci]`);
  const out = { action: put.created ? "written" : "exists", market_date: mkt, n_candidates: cands.length,
    llm_called: record.llm_called, error: record.error, usage: record.usage,
    facts_proposed: record.facts_proposed.length, facts_appended: record.facts_appended };
  console.log(JSON.stringify({ event: "decision", ...out }));
  return out;
}

/** /api/decisions：最近 N 天的 decisions 檔（dashboard「Decisions」頁；tracer 補的 outcome 也在裡面） */
async function listDecisions(env, limit) {
  const names = (await ghListDir(env, DECISIONS_DIR)).sort().reverse().slice(0, limit);
  const days = [];
  for (const n of names) {
    try { days.push(await ghGetJson(env, `${DECISIONS_DIR}/${n}`)); } catch (e) { days.push({ market_date: n.replace(".json", ""), error: String(e) }); }
  }
  return { generated_at: new Date().toISOString(), days };
}

// ------------------------------------------------------------------ Cloudflare Access（選用）
let _certCache = { at: 0, keys: [] };

async function accessKeys(env) {
  if (Date.now() - _certCache.at < 3600 * 1000 && _certCache.keys.length) return _certCache.keys;
  const r = await fetch(`https://${env.ACCESS_TEAM_DOMAIN}/cdn-cgi/access/certs`);
  if (!r.ok) throw new Error(`access certs ${r.status}`);
  _certCache = { at: Date.now(), keys: (await r.json()).keys || [] };
  return _certCache.keys;
}

function b64urlToBytes(s) {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - s.length % 4) % 4);
  return Uint8Array.from(atob(b64), c => c.charCodeAt(0));
}

/** 驗 Cf-Access-Jwt-Assertion（或 CF_Authorization cookie）：簽章、aud、exp。
 *  沒設 ACCESS_TEAM_DOMAIN/ACCESS_AUD → 不驗，行為與以前一樣。
 *  回 {ok, reason}：reason 會放進 401 的 JSON，dashboard 直接顯示，設錯時不用猜。
 *  注意：靜態頁（public/）由 Cloudflare 先供檔、不經過這裡，所以「頁面開得了但 /api 全 401」
 *  就是這個檢查沒過——不是頁面壞了。 */
async function verifyAccess(request, env) {
  if (!env.ACCESS_TEAM_DOMAIN || !env.ACCESS_AUD) return { ok: true };
  const team = String(env.ACCESS_TEAM_DOMAIN).replace(/^https?:\/\//, "").replace(/\/.*$/, "");
  let token = request.headers.get("Cf-Access-Jwt-Assertion");
  if (!token) {
    const m = (request.headers.get("Cookie") || "").match(/(?:^|;\s*)CF_Authorization=([^;]+)/);
    token = m ? m[1] : null;
  }
  if (!token) return { ok: false, reason: "no_token", hint: "請求沒帶 Access JWT：這個網域還沒被 Zero Trust Access 應用程式保護，或你是用舊分頁。先在 Zero Trust 建好 Self-hosted 應用程式再設 ACCESS_* 變數；不想用 Access 就把兩個變數刪掉。" };
  try {
    const [h, p, s] = token.split(".");
    const header = JSON.parse(new TextDecoder().decode(b64urlToBytes(h)));
    const payload = JSON.parse(new TextDecoder().decode(b64urlToBytes(p)));
    const auds = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
    if (!auds.includes(env.ACCESS_AUD)) return { ok: false, reason: "aud_mismatch", hint: `token 的 aud 是 ${auds.map(a => String(a).slice(0, 8) + "…").join(",")}，Worker 設的 ACCESS_AUD 開頭是 ${String(env.ACCESS_AUD).slice(0, 8)}…；請從 Access 應用程式 Overview 重抄 Application Audience Tag。` };
    if (!payload.exp || payload.exp * 1000 < Date.now()) return { ok: false, reason: "expired", hint: "Access session 過期，重新整理頁面重新登入。" };
    let keys;
    try { keys = await accessKeys({ ACCESS_TEAM_DOMAIN: team }); }
    catch (e) { return { ok: false, reason: "certs_fetch_failed", hint: `抓不到 https://${team}/cdn-cgi/access/certs：ACCESS_TEAM_DOMAIN 應是 <team>.cloudflareaccess.com（不含 https://）。${String(e).slice(0, 120)}` }; }
    const jwk = keys.find(k => k.kid === header.kid);
    if (!jwk) return { ok: false, reason: "kid_not_found", hint: "token 的簽章 key 不在這個 team 的 certs 裡：ACCESS_TEAM_DOMAIN 填到別的 team 了。" };
    const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
    const good = await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, b64urlToBytes(s), new TextEncoder().encode(`${h}.${p}`));
    return good ? { ok: true } : { ok: false, reason: "bad_signature", hint: "簽章不符。" };
  } catch (e) {
    console.log(JSON.stringify({ event: "access_verify_error", error: String(e) }));
    return { ok: false, reason: "verify_error", hint: String(e).slice(0, 200) };
  }
}

// ------------------------------------------------------------------ entry points
const noStore = { "Cache-Control": "no-store" };

// ------------------------------------------------------------------ 電子報（公開、唯讀、不觸發任何動作）
/** 這些路徑跳過 Worker 端的 Access 驗證。Cloudflare Access 本身仍會擋——要公開分享，
 *  在 Zero Trust 另建一個 path 為 /brief* 與 /api/brief 的應用程式、policy 用 Bypass（見 cloudflare/README.md）。 */
const PUBLIC_PATHS = new Set(["/brief", "/brief.html", "/api/brief"]);

/** /api/brief?d=YYYY-MM-DD：把候選、decisions、矩陣摘要、排程狀態、資料檢查彙整成一份；只讀 GitHub。 */
async function brief(env, dateParam) {
  const now = new Date();
  const latest = await ghGetJson(env, LATEST_PATH);
  const d = dateParam || latest?.market_date || null;
  const cands = (d && latest && d !== latest.market_date) ? await ghGetJson(env, `data/dashboard/candidates_${d}.json`) : latest;
  const decision = d ? await ghGetJson(env, `${DECISIONS_DIR}/${d}.json`) : null;
  const matrix = await ghGetJson(env, "data/strategy_matrix.json");
  let spotsExists = false;
  try { spotsExists = Boolean(d && await ghGetFile(env, `data/universe_spots/${d}.json`)); } catch {}
  let dates = [];
  try { dates = (await ghListDir(env, DECISIONS_DIR)).map(n => n.replace(".json", "")).sort(); } catch {}

  // 排程：22:00 UTC 之後 scanner 有沒有 run、結果如何
  const expected = expectedFireTime(now, env);
  let runs = [];
  try { runs = await listRunsSince(env, env.SCANNER_WORKFLOW, new Date(expected.getTime() - 10 * 60 * 1000).toISOString()); } catch {}
  const run = runs[0] || null;
  const weekend = now.getUTCDay() === 0 || now.getUTCDay() === 6;
  const latestFresh = latest && new Date(latest.generated_at) >= new Date(expected.getTime() - 10 * 60 * 1000);
  const matrixFresh = matrix && /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}/.test(matrix.generated_at || "")
    && new Date(matrix.generated_at.replace(" UTC", "Z").replace(" ", "T")) >= new Date(expected.getTime() - 10 * 60 * 1000);

  const checks = [];
  const push = (level, text, label) => checks.push({ level, text, label: label || text.split(/[（：。]/)[0].slice(0, 12) });
  if (weekend) push("info", "週末休市：本週最後一個交易日的資料。", "週末休市");
  if (!run) push(Date.now() - expected.getTime() > 65 * 60000 && !weekend ? "bad" : "warn",
    weekend ? "週末沒有 scanner 排程，正常。" : "排定時刻之後 scanner 還沒跑（Worker 07:05 台北會補發）。", weekend ? "scanner 週末不跑" : "scanner 未跑");
  else if (run.conclusion === "success") push("ok", `scanner 已跑（${run.event === "workflow_dispatch" ? "Worker 補發或手動" : "GitHub 排程"}）。`, "scanner 已跑");
  else if (run.status === "completed") push("bad", `scanner 跑失敗（${run.conclusion}），看 Actions log。`, "scanner 失敗");
  else push("warn", "scanner 正在跑。", "scanner 跑中");
  if (latest) push(latestFresh ? "ok" : (run && run.conclusion === "success" ? "info" : "warn"),
    latestFresh ? `候選 JSON 是本次產出（市場日 ${latest.market_date}）。`
      : `候選 JSON 停在市場日 ${latest.market_date}${run && run.conclusion === "success" ? "——scanner 判休市（無新收盤），沿用上一個交易日。" : "。"}`,
    latestFresh ? "候選是今日的" : "候選沿用上一交易日");
  else push("bad", "找不到候選 JSON（data/dashboard/latest.json）。", "候選 JSON 缺");
  if (matrix) push(matrixFresh ? "ok" : "info", `策略矩陣更新於 ${matrix.generated_at}（成熟 ${matrix.n_mature}/${matrix.n_signals}）。`, matrixFresh ? "矩陣已更新" : "矩陣未重算");
  else push("bad", "找不到策略矩陣。", "矩陣缺");
  if (d) push(decision ? "ok" : (latestFresh ? "warn" : "info"),
    decision ? `LLM 三題已記錄（${decision.llm_called ? decision.model_served || decision.model : "零候選未呼叫"}）。`
      : `市場日 ${d} 的 decisions 還沒產生（Worker 07:05／08:35／10:05 台北會寫）。`, decision ? "LLM 三題已記" : "LLM 三題未產生");
  if (d) push(spotsExists ? "ok" : "info", spotsExists ? "對照組 universe 收盤已記。" : "對照組當日檔尚未出現。", spotsExists ? "對照組已記" : "對照組未記");

  const cohort = k => (matrix && matrix[k] && matrix[k].n ? matrix[k] : null);
  return {
    generated_at: now.toISOString(), market_date: d, requested_date: dateParam || null,
    available_dates: dates, prev_date: dates.filter(x => x < d).pop() || null, next_date: dates.find(x => x > d) || null,
    candidates: cands ? { market_date: cands.market_date, generated_at: cands.generated_at, n_candidates: cands.n_candidates,
      n_report_rows: cands.n_report_rows, candidates: cands.candidates || [] } : null,
    decision: decision ? { ...decision, raw_answer: undefined } : null,
    matrix: matrix ? { generated_at: matrix.generated_at, n_mature: matrix.n_mature, n_signals: matrix.n_signals, prereg_date: matrix.prereg_date,
      policy_label: matrix.policy_label, overall: cohort("overall"), rule_b: cohort("rule_b"), oos_all: cohort("oos_all"), oos_rule_b: cohort("oos_rule_b"),
      monthly: matrix.monthly, control: matrix.control } : null,
    schedule: { expected_fire: expected.toISOString(), weekend, run: run ? { event: run.event, status: run.status, conclusion: run.conclusion, created_at: run.created_at, url: run.html_url } : null },
    checks,
  };
}

export default {
  async scheduled(event, env, ctx) {
    const now = new Date();
    ctx.waitUntil((async () => {
      try { await secondAlarm(env, now); } catch (e) { console.log(JSON.stringify({ event: "second_alarm_error", error: String(e) })); }
      // 第二鬧鐘先查，再看 decisions：scanner 若剛被補發，latest.json 還是舊市場日 → exists → 下一發 cron 再來
      try { await runDecision(env, { source: `cron ${event.cron}` }); } catch (e) { console.log(JSON.stringify({ event: "decision_error", error: String(e) })); }
    })());
  },

  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (!PUBLIC_PATHS.has(url.pathname)) {
      const access = await verifyAccess(request, env);
      if (!access.ok) {
        return Response.json({ error: "unauthorized", reason: access.reason, hint: access.hint }, { status: 401, headers: noStore });
      }
    }
    try {
      if (url.pathname === "/api/brief") {
        // 公開唯讀；GitHub API 有配額，快取 5 分鐘
        const key = new Request(url.toString(), { method: "GET" });
        const cache = caches.default;
        const hit = await cache.match(key);
        if (hit) return hit;
        const res = Response.json(await brief(env, url.searchParams.get("d")), { headers: { "Cache-Control": "public, max-age=300" } });
        if (ctx) ctx.waitUntil(cache.put(key, res.clone()));
        return res;
      }
      if (url.pathname === "/brief") return env.ASSETS.fetch(new Request(new URL("/brief.html", url).toString(), request));
      if (url.pathname === "/api/health") return Response.json(await health(env), { headers: noStore });
      if (url.pathname === "/api/alarm/check") return Response.json(await secondAlarm(env, new Date()), { headers: noStore }); // 手動補發
      if (url.pathname === "/api/decide") {
        if (request.method !== "POST") return new Response("POST only", { status: 405 });
        return Response.json(await runDecision(env, { source: "manual" }), { headers: noStore });
      }
      if (url.pathname === "/api/decisions") {
        const limit = Math.min(60, Math.max(1, parseInt(url.searchParams.get("limit") || "20", 10)));
        return Response.json(await listDecisions(env, limit), { headers: noStore });
      }
      if (url.pathname === "/api/facts") {
        // dashboard「事實庫」頁：解析後的 ledger（讀 main 最新版，含 Worker 剛附加的待審條目）
        const f = await ghGetFile(env, LEDGER_PATH);
        return Response.json({ generated_at: new Date().toISOString(), sha: f?.sha || null, ...parseLedger(f?.text || "") }, { headers: noStore });
      }
    } catch (e) {
      return Response.json({ error: String(e) }, { status: 500, headers: noStore });
    }
    // 其餘：靜態 dashboard（cloudflare/public/）
    return env.ASSETS.fetch(request);
  },
};
