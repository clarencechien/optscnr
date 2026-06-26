"""
shadow_tracer.py — 信號追蹤校準器（跟 main.py 解耦的獨立服務）

【做什麼】
讀 main.py 產出的信號快照（data/iv_log/signals_YYYY-MM.json），
回頭抓 T+5/T+10/T+20 的 option 價格回填，產出 SHADOWLOG_YYYY-MM.md。
回答唯一的問題：「scanner 標 9 分的，後來真的噴了嗎？」

【設計原則】（從雨縫 SHADOWLOG_SPEC 搬來）
- append-only：只回填空欄位，已填的不動（不竄改歷史）
- shadow 先行：純記錄驗證，不碰你的部位
- 和錢隔離：記「信號的市場後續」，不記「你買多少、賺賠多少」
- NO_DATA 優雅降級：抓不到價格標 null，不猜、不報錯中斷
- 跑慢 batch：T+N 回填不急，慢慢抓避免 yfinance 限流

【為什麼能跑慢】
這是「回頭看」不是「即時算」。每天只回填「剛好到檢查點」的那幾個信號，
量小、不急、失敗明天再補。所以 batch + sleep 完全 OK。
"""
import os
import json
import time
import random
from datetime import datetime, timedelta
from glob import glob

import yfinance as yf

DATA_DIR = "data"
IV_LOG_DIR = os.path.join(DATA_DIR, "iv_log")

# T+N 檢查點（交易日近似用日曆日，夠用）
CHECKPOINTS = {"t5": 5, "t10": 10, "t20": 20}

# 判定門檻：以「信號當下 entry_price」為基準，現價是它的幾倍
VERDICT_RULES = {
    "spike": 2.0,    # >= 2x → ✅ 噴了
    "alive": 0.5,    # 0.5x ~ 2x → 持平/緩漲
    # < 0.5x → ❌ 沒噴（腰斬以下）；接近 0 → 歸零
}


def load_month_signals(month_str):
    """讀某月的信號快照檔"""
    path = os.path.join(IV_LOG_DIR, f"signals_{month_str}.json")
    if not os.path.exists(path):
        return None, path
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f), path
    except Exception as e:
        print(f"⚠️ 讀取 {path} 失敗：{e}")
        return None, path


def fetch_option_price(ticker, expiry, strike):
    """抓某個 option 合約現在的價格 + 標的現價 + IV。
    抓不到回 None（NO_DATA 降級，不猜）。"""
    try:
        tk = yf.Ticker(ticker)
        # 標的現價
        spot = 0.0
        try:
            fast = tk.fast_info
            spot = float(fast.get('lastPrice', 0) or fast.get('last_price', 0) or 0)
        except Exception:
            pass
        if not spot:
            try:
                h = tk.history(period="1d")
                if not h.empty:
                    spot = float(h['Close'].iloc[-1])
            except Exception:
                pass

        # option 鏈
        if expiry not in (tk.options or []):
            # 到期日已不存在（可能已過期）→ 用標的現價推估是否價內
            return {"opt_price": None, "spot": spot, "iv": None, "note": "expiry_gone"}

        chain = tk.option_chain(expiry)
        calls = chain.calls
        match = calls[calls['strike'] == strike]
        if match.empty:
            return {"opt_price": None, "spot": spot, "iv": None, "note": "strike_gone"}

        row = match.iloc[0]
        return {
            "opt_price": float(row.get('lastPrice', 0)),
            "spot": spot,
            "iv": float(row.get('impliedVolatility', 0)) * 100,
            "note": "ok",
        }
    except Exception as e:
        return {"opt_price": None, "spot": None, "iv": None, "note": f"err:{e}"}


def make_verdict(entry_price, results):
    """根據已回填的 T+N 結果，給整體判定。
    取「曾達到的最高倍數」當主要依據（因為你的玩法是 free ride，碰到高點就該落袋）。"""
    if entry_price <= 0:
        return None
    multiples = []
    for key in ("t5", "t10", "t20"):
        r = results.get(key)
        if r and r.get("opt_price") is not None:
            multiples.append(r["opt_price"] / entry_price)
    if not multiples:
        return None
    peak = max(multiples)
    last = multiples[-1]
    if peak >= VERDICT_RULES["spike"]:
        return f"✅噴了(峰{peak:.1f}x)"
    elif last < 0.1:
        return f"💀歸零({last:.2f}x)"
    elif peak < VERDICT_RULES["alive"]:
        return f"❌沒噴(峰{peak:.1f}x)"
    else:
        return f"➖持平(峰{peak:.1f}x/今{last:.1f}x)"


def backfill(signals):
    """回填到檢查點的信號。只填空欄位（append-only），已填的不動。
    回傳：是否有更新。"""
    today = datetime.now().date()
    updated = False
    to_fetch = []  # (signal_index, checkpoint_key)

    for i, sig in enumerate(signals):
        snap_date = datetime.strptime(sig["snapshot_date"], "%Y-%m-%d").date()
        for key, days in CHECKPOINTS.items():
            if sig.get(key) is not None:
                continue  # 已填過，不動（append-only）
            checkpoint_date = snap_date + timedelta(days=days)
            # 今天 >= 檢查點日 才回填（到期了才看）
            if today >= checkpoint_date:
                to_fetch.append((i, key))

    if not to_fetch:
        print("  📭 今天沒有到檢查點的信號需要回填。")
        return False

    print(f"  🔍 需回填 {len(to_fetch)} 筆（T+N 到期的信號）...")
    for idx, key in to_fetch:
        sig = signals[idx]
        res = fetch_option_price(sig["ticker"], sig["expiry"], sig["strike"])
        sig[key] = res
        updated = True
        status = "✅" if res.get("opt_price") is not None else f"💨({res.get('note')})"
        print(f"    {sig['ticker']} {sig['strike']} {key} {status}")
        # 慢 batch：避免 yfinance 限流
        time.sleep(random.uniform(0.5, 1.2))

    # 更新 verdict（每次回填後重算）
    for sig in signals:
        results = {k: sig.get(k) for k in CHECKPOINTS}
        v = make_verdict(sig.get("entry_price", 0), results)
        if v:
            sig["verdict"] = v

    return updated


def generate_shadowlog_md(signals, month_str):
    """產出 SHADOWLOG_YYYY-MM.md，三區塊。
    只記市場事實，不記持有/損益。"""
    md = f"# 🌑 SHADOWLOG {month_str} — 信號校準報告\n\n"
    md += "> Shadow 追蹤：scanner 標高分的信號，後來真的噴了嗎？\n"
    md += "> **這是工具校準鏡，不是部位損益表**——記的是信號的市場後續，不是你買了多少。\n\n"
    md += f"_最後更新：{datetime.now().strftime('%Y-%m-%d %H:%M UTC')} ｜ 本月信號數：{len(signals)}_\n\n"

    # 統計命中率（只算已有 verdict 的）
    judged = [s for s in signals if s.get("verdict")]
    spiked = [s for s in judged if s["verdict"].startswith("✅")]
    if judged:
        hit_rate = len(spiked) / len(judged) * 100
        md += f"## 📊 整體命中率\n\n"
        md += f"- 已驗證信號：{len(judged)} / {len(signals)}\n"
        md += f"- 噴出（≥2x）：{len(spiked)} 筆 → **命中率 {hit_rate:.0f}%**\n"
        md += f"- 待驗證（T+N 還沒到）：{len(signals) - len(judged)} 筆\n\n"

    # === 區塊一：暴動高 IV 過濾驗證 ===
    md += "## 🔥 區塊一：暴動高 IV 過濾驗證\n\n"
    md += "> 被 v3.9「⚠️暴動高IV」標記的，後來真的該擋嗎？（驗證 IV>80% 門檻）\n\n"
    surge = [s for s in signals if "暴動高IV" in s.get("tags", "")]
    if surge:
        md += "| 標的 | 標記日 | 進場IV | 進場價 | T+5 | T+10 | 判定 |\n"
        md += "|---|---|---|---|---|---|---|\n"
        for s in surge:
            t5 = _fmt_mult(s, "t5")
            t10 = _fmt_mult(s, "t10")
            md += f"| {s['ticker']} {s['strike']:.0f}C | {s['snapshot_date']} | {s['entry_iv']:.0f}% | ${s['entry_price']:.2f} | {t5} | {t10} | {s.get('verdict','待驗證')} |\n"
        md += "\n_若被標記的多數後來歸零/沒噴 → 過濾有效；若多數反而噴了 → 門檻太嚴，調鬆 SURGE_IV_MIN。_\n\n"
    else:
        md += "_本月無暴動高 IV 標記。_\n\n"

    # === 區塊二：尾段價外 / 當沖刷量過濾驗證 ===
    md += "## ⚠️ 區塊二：尾段價外 / 當沖刷量過濾驗證\n\n"
    md += "> 被 v3.8 兩道過濾標記的，後續表現驗證\n\n"
    filtered = [s for s in signals if ("尾段價外" in s.get("tags", "") or "當沖刷量" in s.get("tags", ""))]
    if filtered:
        md += "| 標的 | 標記日 | 標籤 | 進場價 | T+5 | T+10 | 判定 |\n"
        md += "|---|---|---|---|---|---|---|\n"
        for s in filtered:
            short_tags = " ".join(t for t in s.get("tags", "").split() if "尾段" in t or "當沖" in t)
            md += f"| {s['ticker']} {s['strike']:.0f}C | {s['snapshot_date']} | {short_tags} | ${s['entry_price']:.2f} | {_fmt_mult(s,'t5')} | {_fmt_mult(s,'t10')} | {s.get('verdict','待驗證')} |\n"
        md += "\n"
    else:
        md += "_本月無尾段/當沖標記。_\n\n"

    # === 區塊三：全部高分信號 T+N 追蹤 ===
    md += "## 🎯 區塊三：高分信號 T+N 追蹤（全部）\n\n"
    md += "| 標的 | 日期 | 分 | 進場價 | T+5 | T+10 | T+20 | 判定 |\n"
    md += "|---|---|---|---|---|---|---|---|\n"
    for s in sorted(signals, key=lambda x: x["snapshot_date"], reverse=True):
        md += (f"| {s['ticker']} {s['strike']:.0f}C | {s['snapshot_date']} | {s['score']} "
               f"| ${s['entry_price']:.2f} | {_fmt_mult(s,'t5')} | {_fmt_mult(s,'t10')} "
               f"| {_fmt_mult(s,'t20')} | {s.get('verdict') or '待驗證'} |\n")
    md += "\n"
    md += "_T+N 欄顯示「當時 option 價格是進場價的幾倍」。`—` = 還沒到檢查點；`💨` = 抓不到資料。_\n"

    return md


def _fmt_mult(sig, key):
    """格式化 T+N 倍數顯示"""
    r = sig.get(key)
    if r is None:
        return "—"
    if r.get("opt_price") is None:
        return "💨"
    entry = sig.get("entry_price", 0)
    if entry <= 0:
        return "?"
    mult = r["opt_price"] / entry
    return f"{mult:.1f}x"


def main():
    print(f"🌑 啟動 Shadow Tracer：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    os.makedirs(IV_LOG_DIR, exist_ok=True)

    # 處理「本月 + 上月」兩個檔（因為月初時，上月的信號可能還在 T+20 回填期）
    now = datetime.now()
    months = [now.strftime("%Y-%m")]
    prev_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    months.append(prev_month)

    for month_str in months:
        signals, path = load_month_signals(month_str)
        if signals is None:
            print(f"  ⏭️  {month_str} 無信號檔，跳過。")
            continue

        print(f"\n📂 處理 {month_str}（{len(signals)} 筆信號）")
        updated = backfill(signals)

        # 寫回 JSON（即使沒回填也重算 verdict）
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(signals, f, ensure_ascii=False, indent=2)

        # 產出 md
        md = generate_shadowlog_md(signals, month_str)
        md_path = f"SHADOWLOG_{month_str}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"  📝 {md_path} 已生成（{'有回填' if updated else '無新回填，僅刷新'}）")

    print("\n✅ Shadow Tracer 完成。")


if __name__ == "__main__":
    main()
