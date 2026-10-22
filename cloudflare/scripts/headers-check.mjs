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

// ASSETS 的替身要學 Workers Assets 預設的 html_handling = auto-trailing-slash:
// 直接要 *.html 會被 307 轉到去掉副檔名的路徑。少了這一條,Worker 把 /brief 改寫成
// /brief.html 再丟給 ASSETS 的無限轉址(2026-10-22 正式站)在這裡就測不出來。
const fakeAssets = {
  fetch: async (req) => {
    const u = new URL(req.url);
    if (u.pathname.endsWith('.html')) {
      const to = u.pathname === '/index.html' ? '/' : u.pathname.slice(0, -'.html'.length);
      return new Response(null, { status: 307, headers: { location: to } });
    }
    return new Response('<html>dash</html>', { headers: { 'content-type': 'text/html' } });
  },
};
const baseEnv = {
  ASSETS: fakeAssets,
  GITHUB_OWNER: 'x', GITHUB_REPO: 'y', DEFAULT_BRANCH: 'main',
  // 不設 GITHUB_TOKEN:上游呼叫會失敗,但那不影響要驗的東西(路由與標頭)
};
// ⚠️ ACCESS_* 一定要設。verifyAccess 的第一行是
//      if (!env.ACCESS_TEAM_DOMAIN || !env.ACCESS_AUD) return { ok: true };
// 也就是**兩個變數沒設時這一層整個不驗**。正式環境兩個都設了(2026-10-22 以
// Cloudflare API 確認),但測試若不設,下面每一條「要 Access」的斷言都會假通過。
const env = { ...baseEnv, ACCESS_TEAM_DOMAIN: 'swtech.cloudflareaccess.com', ACCESS_AUD: 'a'.repeat(64) };

// CSP 要分兩種:HTML 頁面要能載行內 script 與 Google Fonts,JSON 則是
// 「這是資料不是頁面」。harden() 若把頁面的 CSP 蓋成 default-src 'none',
// dashboard 與 /brief 會連自己的行內 script 都載不了 —— 那是 run_worker_first
// 打開之後才會發生的事,所以這裡要驗。
const isPageCsp = (c) => /script-src 'self' 'unsafe-inline'/.test(c || '');
const isDataCsp = (c) => /^default-src 'none'/.test(c || '');
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

// run_worker_first = true 之後,靜態檔也會經過 Worker。
// 公開的那一頁必須拿到**頁面版** CSP,不能被 harden() 蓋成 default-src 'none' ——
// 蓋掉的話 /brief 連自己的行內 <script> 都載不了,頁面是空的。
async function checkBriefIsUsable() {
  const res = await worker.fetch(new Request('https://optscnr.ai-apps.work/brief'), env, ctx);
  const csp = res.headers.get('content-security-policy') || '';
  const ok = res.status === 200 && isPageCsp(csp) && /fonts\.googleapis\.com/.test(csp);
  const why = res.status >= 300 && res.status < 400
    ? `被轉址到 ${res.headers.get('location')}(run_worker_first 之後這就是無限迴圈)`
    : 'CSP: ' + csp.slice(0, 70);
  console.log(`${ok ? '✓' : '✗'} ${'/brief 拿到 200 + 頁面版 CSP'.padEnd(26)} ${String(res.status).padEnd(5)} ${ok ? '行內 script 與字型都放行' : why}`);
  return ok;
}

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
  // CSP 的種類要跟 content-type 對得上
  const csp = res.headers.get('content-security-policy');
  const html = /text\/html/i.test(res.headers.get('content-type') || '');
  const cspOk = missing.length ? true : (html ? isPageCsp(csp) : isDataCsp(csp));
  const all = ok && cspOk;
  if (ok && !cspOk) bad++;
  console.log(
    `${all ? '✓' : '✗'} ${name.padEnd(26)} ${String(res.status).padEnd(5)} ` +
    `${missing.length ? '缺標頭:' + missing.join(', ') : '五個標頭都在'}` +
    `${gateOk ? '' : '  ← 閘門不對'}` +
    `${cspOk ? '' : `  ← CSP 種類不對(${html ? '頁面' : 'JSON'} 拿到 ${isPageCsp(csp) ? '頁面版' : isDataCsp(csp) ? '資料版' : '未知'})`}`,
  );
}

if (!(await checkBriefIsUsable())) bad++;

// 正式環境的那條路:public/_headers 已經替靜態檔設好頁面版 CSP,harden() **不可以**
// 蓋掉它。這是 run_worker_first 打開之後最容易弄壞 dashboard 的一步。
{
  const PRESET = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com";
  const envWithHeaders = {
    ...env,
    ASSETS: { fetch: async () => new Response('<html>dash</html>', {
      headers: { 'content-type': 'text/html', 'content-security-policy': PRESET },
    }) },
  };
  const res = await worker.fetch(new Request('https://optscnr.ai-apps.work/brief'), envWithHeaders, ctx);
  const kept = res.headers.get('content-security-policy') === PRESET;
  if (!kept) bad++;
  console.log(`${kept ? '✓' : '✗'} ${'_headers 的 CSP 不被蓋掉'.padEnd(26)} ${String(res.status).padEnd(5)} ${kept ? '原樣保留' : '被 harden() 覆寫成:' + (res.headers.get('content-security-policy') || '').slice(0, 60)}`);
}

// fail-open 現在會在 Workers Logs 留一行。驗它有沒有真的叫 console.warn。
{
  const warned = [];
  const orig = console.warn;
  console.warn = (...a) => warned.push(a.join(' '));
  const res = await worker.fetch(new Request('https://optscnr.ai-apps.work/api/facts'), baseEnv, ctx);
  console.warn = orig;
  const open = res.status !== 401;
  const noisy = warned.some((w) => w.includes('access_check_disabled'));
  if (!noisy) bad++;
  console.log(
    `${noisy ? '✓' : '✗'} ${'ACCESS_* 沒設時'.padEnd(26)} ${String(res.status).padEnd(5)} ` +
    (open ? 'fail-open(刻意:邊緣 Access 蓋整個 host)' : '擋下來') +
    (noisy ? ',而且有寫進 log' : ' —— ✗ 沒有留下任何 log,會靜靜地少一層'),
  );
}

console.log(bad ? `\n${bad} 個案例失敗` : `\n全部 ${CASES.length} 個案例通過`);
process.exit(bad ? 1 : 0);
