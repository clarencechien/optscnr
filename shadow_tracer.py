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


def _mults_of(sig):
    """回傳該信號已回填檢查點的倍數列表（依 t5→t10→t20 順序）"""
    entry = sig.get("entry_price", 0)
    if not entry or entry <= 0:
        return []
    out = []
    for k in ("t5", "t10", "t20"):
        r = sig.get(k)
        if r and r.get("opt_price") is not None:
            out.append(r["opt_price"] / entry)
    return out


def _ladder_return(sig):
    """階梯出場模擬報酬（倍數，1.0 = 打平）。
    規則：峰值 >= 2x 時「+100% 賣半」→ 一半在 2x 落袋、剩一半以最後檢查點價出場；
    沒到 2x 就全部抱到最後檢查點。這是 P3-1 期望值欄的定義——
    命中率只數贏家（存活者偏差），期望值把歸零票也算進來。"""
    m = _mults_of(sig)
    if not m:
        return None
    peak, last = max(m), m[-1]
    if peak >= VERDICT_RULES["spike"]:
        return 0.5 * VERDICT_RULES["spike"] + 0.5 * last
    return last


def _is_zeroed(sig):
    """歸零定義：峰值 < 0.2x（連反彈逃命的機會都沒給）"""
    m = _mults_of(sig)
    return bool(m) and max(m) < 0.2


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
        md += f"- 待驗證（T+N 還沒到）：{len(signals) - len(judged)} 筆\n"

        # === P3-1：歸零率 + 期望值（修存活者偏差——命中率只數贏家，不數屍體）===
        zeroed = [s for s in judged if _is_zeroed(s)]
        evs = [v for v in (_ladder_return(s) for s in judged) if v is not None]
        md += f"- 歸零率（峰值 <0.2x）：{len(zeroed)} 筆 → **{len(zeroed)/len(judged)*100:.0f}%**\n"
        if evs:
            avg_ev = sum(evs) / len(evs)
            md += (f"- 期望值（階梯出場模擬：峰≥2x 賣半、餘以末檢查點出場）："
                   f"平均 **{avg_ev:.2f}x**（1.0x = 打平）\n")

        # === P3-2：標的-日去重命中率（主指標）===
        # 同一標的多履約是「同一次擲骰的不同角度」（T 20C/21C/30C 被 2x 線隨機切一刀），
        # 271 筆樣本實際只有 30-40 個獨立事件。以 (標的, 信號日) 去重後的命中率為主指標。
        groups = {}
        for s in judged:
            groups.setdefault((s["ticker"], s["snapshot_date"]), []).append(s)
        g_hit = [g for g in groups.values()
                 if any(x["verdict"].startswith("✅") for x in g)]
        md += (f"- **標的-日去重命中率（主指標）**：{len(g_hit)} / {len(groups)} 個獨立事件 → "
               f"**{len(g_hit)/len(groups)*100:.0f}%**（任一履約 ≥2x 即算命中）\n\n")

        # === 權利金分層命中率（lottery vs mid vs heavy）===
        # 驗證「$1.28 樂透票 vs $5.5 實彈單」兩類信號的期望值是否有顯著差異
        # 樣本夠多且差異顯著 → 才考慮在掃描報表分區顯示；否則此分類即雜訊
        md += "### 💰 權利金分層命中率\n\n"
        md += "| 分層 | 定義 | 已驗證 | 噴出 | 命中率 |\n|---|---|---|---|---|\n"
        for tier, label in [("lottery", "樂透 <$1.5"), ("mid", "中間 $1.5-3"), ("heavy", "實彈 >$3")]:
            tj = [s for s in judged if s.get("premium_tier") == tier]
            ts = [s for s in tj if s["verdict"].startswith("✅")]
            rate = f"{len(ts)/len(tj)*100:.0f}%" if tj else "—"
            md += f"| {label.split(' ')[0]} | {label.split(' ',1)[1] if ' ' in label else ''} | {len(tj)} | {len(ts)} | {rate} |\n"
        md += "\n_樣本 <10 筆時命中率僅供參考，勿據此改規則。_\n\n"

        # === 新聞點火 vs 純 flow 命中率 ===
        # 驗證 2026-06-26 批的觀察：當天新聞名單 12 檔中 flow 只放行 2 檔（GOOGL/META）全噴，
        # 無新聞的 15 筆只中 1（ASTS）。「新聞×真金白銀交集」是否真的比純 flow 準？
        # news_at_signal 缺欄的舊信號不列入（避免把未知當 False 灌進統計）
        md += "### 📰 新聞點火 vs 純 flow 命中率\n\n"
        md += "| 類型 | 定義 | 已驗證 | 噴出 | 命中率 |\n|---|---|---|---|---|\n"
        for flag, name, desc in [(True, "新聞點火", "信號日已在催化名單"),
                                 (False, "純flow", "無新聞的沉默佈局")]:
            nj = [s for s in judged if s.get("news_at_signal") is flag]
            ns = [s for s in nj if s["verdict"].startswith("✅")]
            nrate = f"{len(ns)/len(nj)*100:.0f}%" if nj else "—"
            md += f"| {name} | {desc} | {len(nj)} | {len(ns)} | {nrate} |\n"
        md += "\n_樣本 <10 筆時命中率僅供參考，勿據此改規則。_\n\n"

        # === DTE 分層命中率（theta 絞肉區驗證）===
        # 月選到期前 1-2 週流動性擠向近月，TL;DR 會塞滿 DTE<21 的合約（日曆效應）。
        # 驗證「近月高分信號是否系統性較差」。DTE 由 expiry-snapshot_date 推導，
        # 零 schema 改動、可回溯全部歷史信號。
        def _dte_of(s):
            try:
                exp = datetime.strptime(s["expiry"], "%Y-%m-%d")
                snap = datetime.strptime(s["snapshot_date"], "%Y-%m-%d")
                return (exp - snap).days
            except Exception:
                return None

        md += "### ⏳ DTE 分層命中率\n\n"
        md += "| 分層 | 已驗證 | 噴出 | 命中率 | 歸零率 | 期望值 |\n|---|---|---|---|---|---|\n"
        dte_buckets = [
            ("<21天（絞肉區）", lambda d: d is not None and d < 21),
            ("21-45天", lambda d: d is not None and 21 <= d <= 45),
            (">45天", lambda d: d is not None and d > 45),
        ]
        for label, cond in dte_buckets:
            bj = [s for s in judged if cond(_dte_of(s))]
            bs = [s for s in bj if s["verdict"].startswith("✅")]
            rate = f"{len(bs)/len(bj)*100:.0f}%" if bj else "—"
            bz = [s for s in bj if _is_zeroed(s)]
            zrate = f"{len(bz)/len(bj)*100:.0f}%" if bj else "—"
            bev = [v for v in (_ladder_return(s) for s in bj) if v is not None]
            ev = f"{sum(bev)/len(bev):.2f}x" if bev else "—"
            md += f"| {label} | {len(bj)} | {len(bs)} | {rate} | {zrate} | {ev} |\n"
        md += ("\n_命中率有存活者偏差（六月 21-45 天 60% vs 七月 0%，測的是「當月哪批標的動了」"
               "而非 DTE）——判讀以**期望值**為準；樣本 <10 筆僅供參考。_\n\n")

        # === 過濾盲點觀察（只記錄，不改分）===
        # 盲點一：長天期極價外——過濾一要求 DTE<45 才觸發，DTE>45 的極價外漏網
        #   （活案例：TSLA 990C 2026-07-06，DTE 74、OTM 135%，拿 8 分）
        # 盲點二：倉退信號——過濾二門檻 |Δ7d|≤200，量大但 OI 減少的刷量漏網
        #   （活案例：VST 180C 2026-07-06，Vol 7,688、Δ7d -234，拿 9 分）
        # 兩個 cohort 命中率若顯著低於整體 → 支持補過濾；先累積數據，不動門檻。
        def _otm_of(s):
            spot = s.get("entry_spot") or 0
            if spot <= 0:
                return None
            return (s["strike"] - spot) / spot

        blind1 = [s for s in judged if (_dte_of(s) or 0) > 45 and (_otm_of(s) or 0) > 0.25]
        b1_hit = [s for s in blind1 if s["verdict"].startswith("✅")]
        blind2 = [s for s in judged if s.get("oi_d7", 0) <= 0]
        b2_hit = [s for s in blind2 if s["verdict"].startswith("✅")]

        md += "### 🕳️ 過濾盲點觀察\n\n"
        md += "| 盲點 cohort | 定義 | 已驗證 | 噴出 | 命中率 |\n|---|---|---|---|---|\n"
        r1 = f"{len(b1_hit)/len(blind1)*100:.0f}%" if blind1 else "—"
        r2 = f"{len(b2_hit)/len(blind2)*100:.0f}%" if blind2 else "—"
        md += f"| 長天期極價外 | DTE>45 且 OTM>25%（躲過過濾一） | {len(blind1)} | {len(b1_hit)} | {r1} |\n"
        md += f"| 倉退信號 | Δ7d≤0（量大倉不增，過濾二邊界） | {len(blind2)} | {len(b2_hit)} | {r2} |\n"
        md += "\n_cohort 命中率顯著低於整體 → 支持補過濾；顯著高於 → 該「盲點」其實不是問題。_\n\n"

        # === 指紋 cohort：純「掃貨+新倉暴量」（第一次改卷的最強線索）===
        # 2026-06 三筆命中（GOOGL 350C / META 635C / ASTS 140C）的唯一共同指紋：
        # tags 恰為「🚨異常掃貨 🆕新倉暴量」且無其他標籤——合約七天內新生、
        # 量 >1.2x OI 的掃貨、且非菸屁股/萬人塚的散戶墳場。
        # 6/26 批內 4 筆此型態包辦全部 3 個命中；但 6/29-7/1 同型態 0/13
        # → 假說：型態挑標的、日子給行情。詳見 CONTEXT.md 第七節。只統計，不改分。
        FP = "🚨異常掃貨 🆕新倉暴量"
        fp_j = [s for s in judged if s.get("tags") == FP]
        fp_hit = [s for s in fp_j if s["verdict"].startswith("✅")]
        ot_j = [s for s in judged if s.get("tags") != FP]
        ot_hit = [s for s in ot_j if s["verdict"].startswith("✅")]
        md += "### 🧬 指紋 cohort：純「掃貨+新倉暴量」\n\n"
        md += "| 類型 | 已驗證 | 噴出 | 命中率 |\n|---|---|---|---|\n"
        fr_ = f"{len(fp_hit)/len(fp_j)*100:.0f}%" if fp_j else "—"
        or_ = f"{len(ot_hit)/len(ot_j)*100:.0f}%" if ot_j else "—"
        md += f"| 指紋（純掃貨+新倉暴量，無其他標籤） | {len(fp_j)} | {len(fp_hit)} | {fr_} |\n"
        md += f"| 其他 tag 組合 | {len(ot_j)} | {len(ot_hit)} | {or_} |\n"
        md += "\n_指紋假說出自事後分析（post-hoc），以本表的後續樣本為準；樣本 <10 筆僅供參考。_\n\n"

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
    md += "| 標的 | 日期 | 分 | 進場價 | T+5 | T+10 | T+20 | 判定 | 歸因 |\n"
    md += "|---|---|---|---|---|---|---|---|---|\n"
    for s in sorted(signals, key=lambda x: x["snapshot_date"], reverse=True):
        md += (f"| {s['ticker']} {s['strike']:.0f}C | {s['snapshot_date']} | {s['score']} "
               f"| ${s['entry_price']:.2f} | {_fmt_mult(s,'t5')} | {_fmt_mult(s,'t10')} "
               f"| {_fmt_mult(s,'t20')} | {s.get('verdict') or '待驗證'} | {_fmt_attribution(s)} |\n")
    md += "\n"
    md += ("_T+N 欄顯示「當時 option 價格是進場價的幾倍」。`—` = 還沒到檢查點；`💨` = 抓不到資料。_\n"
           "_歸因欄（P3-3，人工回填 JSON 的 `signal_day_underlying_move` / `why_it_popped`）：_\n"
           "_信號日標的漲跌% + 噴發型態（跳空脈衝/慢磨/災後反彈續命/不明），讓贏家分析不用每月從頭查新聞。_\n")

    return md


def _fmt_attribution(sig):
    """格式化 P3-3 歸因欄：信號日標的漲跌% + why_it_popped（皆為人工回填，缺就顯示 —）"""
    parts = []
    move = sig.get("signal_day_underlying_move")
    if move is not None:
        try:
            parts.append(f"{float(move):+.1f}%")
        except (TypeError, ValueError):
            pass
    why = sig.get("why_it_popped")
    if why:
        parts.append(str(why))
    return " ".join(parts) if parts else "—"


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
