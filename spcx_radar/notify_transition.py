#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notify_transition.py — C 池判定轉換推播（PLAN_2026-10_c_pool_alert §五）

只在三種情況發一則，L2 持續中每天不發（避免變成另一個被忽略的噪音）：
  1. c_pool.transition 非空（任何方向，例如 L1->L2、L2->L1）
  2. Sage 今天沒跑（sage_health.ran_for_latest_market_day == False）
  3. 回應逾期的第一天（response.status == overdue 且 overdue_days == 1）

管道（NOTIFY_FORMAT，預設 bentodrop）：
  bentodrop：BentoDrop §12.4 明文模式。POST {NOTIFY_URL}/api/push，Bearer bd_… token，body {"text": "..."}。
             token 在 BentoDrop 設定 → API Tokens 建立，**要勾「明文模式」**（沒勾會回 403 plaintext_disabled）。
             明文 ≤2000 bytes、24 小時後自動刪、收件匣標「未加密」——這則只有 level/價/IV/連結，沒有需要加密的東西。
             要走加密模式（§12.3，token 只拿公鑰）得用 BentoDrop repo 的 cli/bentodrop-push.mjs，Python 這裡不重做 ECDH。
  webhook  ：任何收 JSON POST 的 URL（Slack/Discord/ntfy…），body {"title","body","message","url","source"}，有 token 才帶 Bearer。

沒設 NOTIFY_URL → 印出訊息、exit 0（管道還沒接也不會讓 workflow 變紅）。
發送失敗 → exit 1（要看得見；本步驟排在 commit 之後，失敗不影響資料入庫）。

用法：python spcx_radar/notify_transition.py          # 讀 brief，該發才發
      python spcx_radar/notify_transition.py --test   # 不看 brief，直接送一則測試訊息（驗管道用）

內容固定格式：SPCX C 池：L1->L2｜價 $148｜IV 47%｜回應期限 10/24｜https://optscnr.ai-apps.work/brief?m=spcx
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEF_PATH = os.path.join(HERE, "output", "spcx_brief.json")
BRIEF_URL = os.environ.get("BRIEF_URL", "https://optscnr.ai-apps.work/brief?m=spcx")
FORMATS = ("bentodrop", "webhook")


def build_message(b: dict) -> tuple[str, str] | None:
    """回 (title, body)；不該發回 None。"""
    c = b.get("c_pool") or {}
    h = b.get("sage_health") or {}
    r = c.get("response") or {}
    price = b.get("price")
    iv = ((c.get("iv") or {}).get("atm"))
    tail = f"價 ${price:.0f}" if price else "價 —"
    tail += f"｜IV {iv*100:.0f}%" if iv else "｜IV —"
    if r.get("deadline"):
        tail += f"｜回應期限 {r['deadline'][5:].replace('-', '/')}"
    tail += f"｜{BRIEF_URL}"
    if c.get("transition"):
        return ("SPCX C 池", f"SPCX C 池：{c['transition']}｜{tail}")
    if h and h.get("ran_for_latest_market_day") is False:
        return ("SPCX C 池：Sage 沒跑", f"SPCX C 池：Option Sage 在 {h.get('latest_market_day')} 沒跑（最後 {h.get('market_date')}）｜{BRIEF_URL}")
    if r.get("status") == "overdue" and r.get("overdue_days") == 1:
        return ("SPCX C 池：回應逾期", f"SPCX C 池：L2 自 {c.get('l2_start')} 亮起，回應已逾期｜{tail}")
    return None


def endpoint(url: str, fmt: str) -> str:
    """bentodrop：NOTIFY_URL 可以是站台根（https://bentodrop.ai-apps.work）或完整 /api/push，都接受。"""
    url = url.rstrip("/")
    if fmt == "bentodrop" and not url.endswith("/api/push"):
        url += "/api/push"
    return url


def send(url: str, token: str | None, title: str, body: str, fmt: str = "bentodrop") -> None:
    if fmt == "bentodrop":
        if not token:
            raise RuntimeError("BentoDrop 需要 API token（NOTIFY_TOKEN，bd_ 開頭，設定 → API Tokens，勾明文模式）")
        payload = {"text": body}
    else:
        payload = {"title": title, "body": body, "message": body, "url": BRIEF_URL, "source": "optscnr/spcx_radar"}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(endpoint(url, fmt), data=data, method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "optscnr-notify"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        extra = ""
        if fmt == "bentodrop":
            try:
                j = json.loads(raw)
                ok = sum(1 for x in j.get("receipts") or [] if x.get("ok"))
                extra = f"，msg {j.get('msgId')}，送達 {ok} 台裝置"
            except Exception:
                pass
        print(f"📨 推播已送出：HTTP {resp.status}{extra}")


def main() -> int:
    fmt = os.environ.get("NOTIFY_FORMAT", "bentodrop").strip().lower() or "bentodrop"
    if fmt not in FORMATS:
        print(f"::error::NOTIFY_FORMAT 只能是 {FORMATS}，得到 {fmt!r}")
        return 1
    if "--test" in sys.argv[1:]:
        now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime("%m/%d %H:%M")
        msg = ("SPCX C 池：測試", f"SPCX C 池：測試訊息 {now} 台北｜管道正常就會看到這則｜{BRIEF_URL}")
    else:
        if not os.path.exists(BRIEF_PATH):
            print("spcx_brief.json 不存在，略過推播")
            return 0
        b = json.load(open(BRIEF_PATH, encoding="utf-8"))
        msg = build_message(b)
        if not msg:
            print(f"無轉換事件（level {((b.get('c_pool') or {}).get('level'))}），不推播")
            return 0
    title, body = msg
    print(f"🔔 {body}")
    url = os.environ.get("NOTIFY_URL", "").strip()
    if not url:
        print(f"NOTIFY_URL 未設定（repo secret SPCX_NOTIFY_URL），只印不發（格式 {fmt}）")
        return 0
    try:
        send(url, os.environ.get("NOTIFY_TOKEN", "").strip() or None, title, body, fmt)
    except urllib.error.HTTPError as e:
        detail = e.read()[:300].decode("utf-8", "replace")
        hint = ""
        if fmt == "bentodrop" and e.code == 403 and "plaintext" in detail:
            hint = "（這個 token 沒勾「明文模式」：到 BentoDrop 設定 → API Tokens 重建一個勾明文的）"
        elif fmt == "bentodrop" and e.code == 401:
            hint = "（token 不對或已撤銷；要 bd_ 開頭）"
        print(f"::error::推播失敗 HTTP {e.code}: {detail}{hint}")
        return 1
    except Exception as e:
        print(f"::error::推播失敗：{e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
