#!/usr/bin/env node
// 安全標頭與公開路徑白名單的回歸檢查。
//
//   node cloudflare/scripts/headers-check.mjs
//   node cloudflare/scripts/headers-check.mjs ../path/to/old-index.js   # 紅綠對照用
//
// 為什麼要有這支:
//   1. PUBLIC_PATHS 是「不需要 Access 的路徑」,它必須與 Zero Trust 的
//      optscnr-brief 應用 bypass 清單一致。多一條就是多開一個公開端點,
//      而那在 code review 時很容易看漏。
//   2. Worker 自產的回應(14 個 Response.json)先前一條安全標頭都沒有。
//      harden() 在出口統一補,這支確認它真的蓋到每一條路徑。
//
// 驗證範圍:路由與標頭。用假的 env,不打 GitHub、不打 Access 的 JWKS。
// **不驗 Cloudflare Access 本身** —— 那在邊緣,Worker 看不到;也不驗 CSP 的內容
// 對不對,那要真瀏覽器開頁面數 console 的攔截次數,curl 與 Node 都不會執行 CSP。

import { pathToFileURL } from 'node:url';
import path from 'node:path';

const rel = process.argv[2] || new URL('../src/index.js', import.meta.url).pathname;
const worker = (await import(pathToFileURL(path.resolve(rel)).href)).default;

globalThis.caches = { default: { match: async () => undefined, put: async () => {} } };

const baseEnv = {
  ASSETS: { fetch: async () => new Response('<html>dash</html>', { headers: { 'content-type': 'text/html' } }) },
  GITHUB_OWNER: 'x', GITHUB_REPO: 'y', DEFAULT_BRANCH: 'main',
  // 不設 GITHUB_TOKEN:上游呼叫會失敗,但那不影響要驗的東西(路由與標頭)
};
// ⚠️ ACCESS_* 一定要設。verifyAccess 的第一行是
//      if (!env.ACCESS_TEAM_DOMAIN || !env.ACCESS_AUD) return { ok: true };
// 也就是**兩個變數沒設時這一層整個不驗**。正式環境兩個都設了(2026-10-22 以
// Cloudflare API 確認),但測試若不設,下面每一條「要 Access」的斷言都會假通過。
const env = { ...baseEnv, ACCESS_TEAM_DOMAIN: 'swtech.cloudflareaccess.com', ACCESS_AUD: 'a'.repeat(64) };
const ctx = { waitUntil() {} };

const WANT = [
  'x-content-type-options',
  'x-frame-options',
  'referrer-policy',
  'strict-transport-security',
  'content-security-policy',
];

// [顯示名稱, 路徑, 是否為公開路徑]
const CASES = [
  ['/brief            公開',      '/brief',         true],
  ['/api/brief        公開',      '/api/brief',     true],
  ['/tw               公開',      '/tw',            true],
  ['/api/tw           公開',      '/api/tw',        true],
  ['/api/spcx         公開',      '/api/spcx',      true],
  ['/brief.html       不該公開',  '/brief.html',    false],
  ['/api/health       要 Access', '/api/health',    false],
  ['/api/facts        要 Access', '/api/facts',     false],
  ['/api/decisions    要 Access', '/api/decisions', false],
  ['/api/decide       要 Access', '/api/decide',    false],
  ['/                 要 Access', '/',              false],
];

let bad = 0;
for (const [name, p, isPublic] of CASES) {
  let res;
  try {
    res = await worker.fetch(new Request('https://optscnr.ai-apps.work' + p), env, ctx);
  } catch (e) {
    bad++;
    console.log(`✗ ${name.padEnd(26)} 拋出 ${e.constructor.name}: ${String(e.message).slice(0, 60)}`);
    continue;
  }
  const missing = WANT.filter((h) => !res.headers.get(h));
  // 非公開路徑在沒有 Access JWT 時必須是 401
  const gateOk = isPublic ? res.status !== 401 : res.status === 401;
  const ok = gateOk && missing.length === 0;
  if (!ok) bad++;
  console.log(
    `${ok ? '✓' : '✗'} ${name.padEnd(26)} ${String(res.status).padEnd(5)} ` +
    `${missing.length ? '缺標頭:' + missing.join(', ') : '五個標頭都在'}${gateOk ? '' : '  ← 閘門不對'}`,
  );
}

// 把 verifyAccess 的 fail-open 行為寫成一條明確的斷言,免得它靜靜地變成「沒有第二層」。
{
  const res = await worker.fetch(new Request('https://optscnr.ai-apps.work/api/facts'), baseEnv, ctx);
  const open = res.status !== 401;
  console.log(
    `${open ? '!' : '✓'} ${'ACCESS_* 沒設時'.padEnd(26)} ${String(res.status).padEnd(5)} ` +
    (open
      ? 'verifyAccess 直接放行 —— 這一層只在兩個 secret 都在時才存在(目前正式環境有設)'
      : '仍然擋下來'),
  );
}

console.log(bad ? `\n${bad} 個案例失敗` : `\n全部 ${CASES.length} 個案例通過`);
process.exit(bad ? 1 : 0);
