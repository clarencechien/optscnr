/**
 * optscnr Cloudflare Worker — 第二鬧鐘 + dashboard 供檔
 *
 * 職責（刻意極小，Python 全部留在 GitHub Actions）：
 *   1. scheduled()：檢查今天「該發的那一發」scanner run 發了沒；沒發 → workflow_dispatch
 *   2. fetch()：/api/health 回傳各 workflow 今日觸發時間 vs 排定時間；其餘路徑由靜態資產供檔
 *
 * 背景：2026-08-26 起 GitHub schedule 反覆延遲 3-8 小時甚至丟棄（docs/log.md 3.13 專節、
 * docs/PROJECT_ESCAPE_DOOR.md Phase 1）。Cloudflare Cron Trigger 準時，所以用它當外部鬧鐘。
 */

const GH = "https://api.github.com";

function ghHeaders(env) {
  return {
    "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "optscnr-cloudflare-worker",
  };
}

/** 今天（UTC）該發的那一發的「排定時刻」：以 SCANNER_CRON_UTC_HOUR 為準。
 *  00:35 那發檢查的是「前一個 UTC 日」的排定 run（跨日補檢查）。 */
function expectedFireTime(now, env) {
  const hour = parseInt(env.SCANNER_CRON_UTC_HOUR || "22", 10);
  const t = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), hour, 0, 0));
  if (now < t) t.setUTCDate(t.getUTCDate() - 1); // 現在還沒到今天的排定時刻 → 看昨天那一發
  return t;
}

async function listRunsSince(env, workflowFile, sinceIso) {
  const url = `${GH}/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/actions/workflows/${workflowFile}/runs`
    + `?created=%3E%3D${encodeURIComponent(sinceIso)}&per_page=10`;
  const r = await fetch(url, { headers: ghHeaders(env) });
  if (!r.ok) throw new Error(`list runs ${workflowFile}: ${r.status}`);
  return (await r.json()).workflow_runs || [];
}

async function dispatch(env, workflowFile) {
  const url = `${GH}/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/actions/workflows/${workflowFile}/dispatches`;
  const r = await fetch(url, {
    method: "POST",
    headers: { ...ghHeaders(env), "Content-Type": "application/json" },
    body: JSON.stringify({ ref: env.DEFAULT_BRANCH || "main" }),
  });
  if (r.status !== 204) throw new Error(`dispatch ${workflowFile}: ${r.status} ${await r.text()}`);
}

/** 第二鬧鐘核心：排定時刻之後有沒有任何 run（schedule 或 dispatch 都算）；沒有就補發。 */
async function secondAlarm(env, now) {
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

/** /api/health：各 workflow 最近一次觸發時間，dashboard「排程健康」區用 */
async function health(env) {
  const now = new Date();
  const since = new Date(now.getTime() - 36 * 3600 * 1000).toISOString();
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
  return { generated_at: now.toISOString(), expected_scanner_fire: expectedFireTime(now, env).toISOString(), workflows: out };
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(secondAlarm(env, new Date()));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/health") {
      return Response.json(await health(env), { headers: { "Cache-Control": "no-store" } });
    }
    if (url.pathname === "/api/alarm/check") {
      // 手動觸發第二鬧鐘檢查（dashboard 上的「立即補發」按鈕）
      return Response.json(await secondAlarm(env, new Date()));
    }
    // 其餘：靜態 dashboard（cloudflare/public/）
    return env.ASSETS.fetch(request);
  },
};
