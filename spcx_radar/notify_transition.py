#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notify_transition.py — C 池判定轉換推播（PLAN_2026-10_c_pool_alert §五）

只在三種情況發一則，L2 持續中每天不發（避免變成另一個被忽略的噪音）：
  1. c_pool.transition 非空（任何方向，例如 L1->L2、L2->L1）
  2. Sage 今天沒跑（sage_health.ran_for_latest_market_day == False）
  3. 回應逾期的第一天（response.status == overdue 且 overdue_days == 1）

管道：POST JSON 到 NOTIFY_URL（BentoDrop 推送 endpoint 或任何 webhook），Bearer NOTIFY_TOKEN。
沒設 NOTIFY_URL → 印出訊息、exit 0（管道還沒接也不會讓 workflow 變紅）。
發送失敗 → exit 1（要看得見；本步驟排在 commit 之後，失敗不影響資料入庫）。

內容固定格式：SPCX C 池：L1->L2｜價 $148｜IV 47%｜回應期限 10/24｜/brief?m=spcx
"""
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEF_PATH = os.path.join(HERE, "output", "spcx_brief.json")
BRIEF_URL = os.environ.get("BRIEF_URL", "https://optscnr.ai-apps.work/brief?m=spcx")


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


def send(url: str, token: str | None, title: str, body: str) -> None:
    payload = json.dumps({"title": title, "body": body, "message": body, "url": BRIEF_URL, "source": "optscnr/spcx_radar"}).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={"Content-Type": "application/json", "User-Agent": "optscnr-notify"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"📨 推播已送出：HTTP {resp.status}")


def main() -> int:
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
        print("NOTIFY_URL 未設定（repo secret SPCX_NOTIFY_URL），只印不發")
        return 0
    try:
        send(url, os.environ.get("NOTIFY_TOKEN", "").strip() or None, title, body)
    except urllib.error.HTTPError as e:
        print(f"::error::推播失敗 HTTP {e.code}: {e.read()[:200]!r}")
        return 1
    except Exception as e:
        print(f"::error::推播失敗：{e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
