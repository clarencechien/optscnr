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
            # schema v2：T+N 也記 bid/ask（可成交價；舊紀錄沒有這兩欄）
            "bid": _num(row.get('bid')), "ask": _num(row.get('ask')),
            "note": "ok",
        }
    except Exception as e:
        return {"opt_price": None, "spot": None, "iv": None, "note": f"err:{e}"}


def _num(x):
    try:
        v = float(x)
        return None if v != v else v
    except (TypeError, ValueError):
        return None


def market_date_str():
    """市場基準日（SPY 最後交易日；抓不到 fallback 今日）——路徑紀錄的日期標籤用，
    與 main.py v3.13 同一套錨，排程延遲跨日不會標錯天。"""
    try:
        spy = yf.Ticker("SPY").history(period="5d")
        if not spy.empty:
            return spy.index[-1].date().isoformat()
    except Exception:
        pass
    return datetime.now().date().isoformat()


def record_paths(all_month_signals, mkt_date, max_chains=250):
    """PLAN 4.1 P0-b：每日路徑紀錄。對「未到期且信號 ≤60 天」的高分信號，
    每天 append 一筆 {date,last,bid,ask,spot,iv} 到 sig['path']（append-only，同日不重複）。
    同 (ticker, expiry) 只抓一次鏈；回答 tracker T1（剩餘半倉抱到 DTE 21 的下場）與 T9。
    回傳 (更新筆數, 抓鏈次數)。"""
    today = datetime.strptime(mkt_date, "%Y-%m-%d").date()
    open_sigs = {}
    for sig in all_month_signals:
        try:
            exp = datetime.strptime(sig["expiry"], "%Y-%m-%d").date()
            snap = datetime.strptime(sig["snapshot_date"], "%Y-%m-%d").date()
        except Exception:
            continue
        # exp == today 也跳過：到期日當天收盤後鏈已下架，yfinance 對已到期 expiry 一律 ValueError
        # （2026-09-07 log：27 條鏈全是 9/4 到期的八月信號，白抓）；到期日價值由 T+N 回填負責
        if exp <= today or (today - snap).days > 60:
            continue
        if any(p.get("date") == mkt_date for p in (sig.get("path") or [])):
            continue  # 今天記過了（手動重跑保護）
        open_sigs.setdefault((sig["ticker"], sig["expiry"]), []).append(sig)
    if not open_sigs:
        print("  🛤️  路徑紀錄：沒有未到期信號。")
        return 0, 0
    keys = list(open_sigs)[:max_chains]
    print(f"  🛤️  路徑紀錄：{sum(len(v) for v in open_sigs.values())} 筆未到期信號、{len(keys)} 條鏈...")
    updated = 0
    for ticker, expiry in keys:
        try:
            tk = yf.Ticker(ticker)
            spot = None
            try:
                h = tk.history(period="1d")
                spot = float(h['Close'].iloc[-1]) if not h.empty else None
            except Exception:
                pass
            calls = tk.option_chain(expiry).calls
        except Exception as e:
            print(f"    💨 {ticker} {expiry}: {type(e).__name__} {str(e)[:80]}")
            continue
        for sig in open_sigs[(ticker, expiry)]:
            m = calls[calls['strike'] == sig["strike"]]
            entry = {"date": mkt_date, "spot": spot}
            if m.empty:
                entry.update({"last": None, "bid": None, "ask": None, "iv": None, "note": "strike_gone"})
            else:
                row = m.iloc[0]
                entry.update({"last": _num(row.get('lastPrice')), "bid": _num(row.get('bid')),
                              "ask": _num(row.get('ask')),
                              "iv": (_num(row.get('impliedVolatility')) or 0) * 100 or None})
            sig.setdefault("path", []).append(entry)
            updated += 1
        time.sleep(random.uniform(0.2, 0.5))
    print(f"  🛤️  路徑紀錄完成：{updated} 筆")
    return updated, len(keys)


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


TERMINAL_NOTES = ("expiry_gone", "strike_gone", "missed_window")
RETRY_GRACE_DAYS = 10  # 檢查點過後 10 天內抓失敗都會重試；再久就標 missed_window 停止


def _is_terminal(res):
    """已填且不需重抓：有價、或到期/履約消失/逾時（永遠拿不到）。
    err:* 這種抓取失敗**不是**終態——之前 `if sig.get(key) is not None: continue`
    把它們當已填永久略過，「失敗明天再補」的註解與實作不符（GPT 審計 P1）。"""
    if res is None:
        return False
    if res.get("opt_price") is not None:
        return True
    return str(res.get("note", "")) in TERMINAL_NOTES


def backfill(signals, mkt_date=None):
    """回填到檢查點的信號。只填空欄位／重試失敗欄位（append-only：有價的不動）。
    回傳：是否有更新。
    - today 用市場基準日（排程延遲跨日不會把檢查點算歪）
    - 每筆回填記 observed_at 與 late_days（逾期幾天才抓到；分析時可過濾）"""
    today = datetime.strptime(mkt_date, "%Y-%m-%d").date() if mkt_date else datetime.now().date()
    updated = False
    to_fetch = []  # (signal_index, checkpoint_key, checkpoint_date)

    for i, sig in enumerate(signals):
        snap_date = datetime.strptime(sig["snapshot_date"], "%Y-%m-%d").date()
        for key, days in CHECKPOINTS.items():
            if _is_terminal(sig.get(key)):
                continue  # 有價或終態，不動（append-only）
            checkpoint_date = snap_date + timedelta(days=days)
            # 今天 >= 檢查點日 才回填（到期了才看）
            if today >= checkpoint_date:
                to_fetch.append((i, key, checkpoint_date))

    if not to_fetch:
        print("  📭 今天沒有到檢查點的信號需要回填。")
        return False

    print(f"  🔍 需回填 {len(to_fetch)} 筆（T+N 到期的信號，含失敗重試）...")
    for idx, key, checkpoint_date in to_fetch:
        sig = signals[idx]
        res = fetch_option_price(sig["ticker"], sig["expiry"], sig["strike"])
        late = (today - checkpoint_date).days
        res["observed_at"] = today.isoformat()
        res["late_days"] = late
        if res.get("opt_price") is None and str(res.get("note", "")).startswith("err") and late > RETRY_GRACE_DAYS:
            res["note"] = "missed_window"  # 逾時且抓不到 → 終態，不再重試（path[] 仍可補）
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


def generate_shadowlog_md(signals, month_str, matrix_md=""):
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
        blind2 = [s for s in judged if s.get("oi_d7") is not None and s["oi_d7"] <= 0]  # P0-e：缺歷史(None)不算倉退
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
        # P0-e/P0-D：cohort 改以結構 feature keys 判定（顯示文字加財報/價格/流動性註記不再破壞 membership）
        import strategy_lab as _SL
        FP_KEYS = {"sweep", "first_seen_in_feed"}
        _fp = lambda s: set(_SL.features_of(s)) == FP_KEYS
        fp_j = [s for s in judged if _fp(s)]
        fp_hit = [s for s in fp_j if s["verdict"].startswith("✅")]
        ot_j = [s for s in judged if not _fp(s)]
        ot_hit = [s for s in ot_j if s["verdict"].startswith("✅")]
        md += "### 🧬 指紋 cohort：純「掃貨+新倉暴量」\n\n"
        md += "| 類型 | 已驗證 | 噴出 | 命中率 |\n|---|---|---|---|\n"
        fr_ = f"{len(fp_hit)/len(fp_j)*100:.0f}%" if fp_j else "—"
        or_ = f"{len(ot_hit)/len(ot_j)*100:.0f}%" if ot_j else "—"
        md += f"| 指紋（純掃貨+新倉暴量，無其他標籤） | {len(fp_j)} | {len(fp_hit)} | {fr_} |\n"
        md += f"| 其他 tag 組合 | {len(ot_j)} | {len(ot_hit)} | {or_} |\n"
        md += "\n_指紋假說出自事後分析（post-hoc），以本表的後續樣本為準；樣本 <10 筆僅供參考。_\n\n"

    # === 🎯 結構候選 cohort（PLAN 4.1 P0-c；舊信號即時推導 structural_pass）===
    try:
        import strategy_lab as SL
        judged_all = [s for s in signals if s.get("verdict")]
        sp = [s for s in judged_all if SL.sig_structural_pass(s)]
        nsp = [s for s in judged_all if not SL.sig_structural_pass(s)]
        md += "## 🎯 結構候選 vs 其他（規則 B：DTE 21–120、IV<50、OTM<25%、Δ7d>0）\n\n"
        md += "| cohort | 已驗證 | 噴出 | 命中率 | 歸零率 | 期望值(階梯) |\n|---|---|---|---|---|---|\n"
        for name, grp in (("🎯 結構候選", sp), ("其他", nsp)):
            hit = [s for s in grp if s["verdict"].startswith("✅")]
            zr = [s for s in grp if _is_zeroed(s)]
            evs = [v for v in (_ladder_return(s) for s in grp) if v is not None]
            md += (f"| {name} | {len(grp)} | {len(hit)} | {len(hit)/len(grp)*100:.0f}% | {len(zr)/len(grp)*100:.0f}% "
                   f"| {sum(evs)/len(evs):.2f}x |\n") if grp else f"| {name} | 0 | — | — | — | — |\n"
        md += "\n_預先登記 2026-09-08；100 筆出樣本 T+20 前不改門檻。_\n\n"
    except Exception as e:
        md += f"_（結構候選 cohort 計算失敗：{e}）_\n\n"

    if matrix_md:
        md += matrix_md

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


# ---------------------------------------------------------------- 第 5 批：LLM decisions 事後結果回填
DECISIONS_DIR = os.path.join(DATA_DIR, "decisions")


def _outcome_of(sig):
    """一筆信號的事後結果（只用已回填的 T+N）；三點都沒價回 None。"""
    entry = sig.get("entry_price") or 0
    if entry <= 0:
        return None
    mult = {}
    for k in ("t5", "t10", "t20"):
        r = sig.get(k)
        if r and r.get("opt_price") is not None:
            mult[k] = round(r["opt_price"] / entry, 2)
    if not mult:
        return None
    return {
        **{k: mult.get(k) for k in ("t5", "t10", "t20")},
        "peak": max(mult.values()),
        "mature": len(mult) == 3,
        "verdict": sig.get("verdict"),
    }


def backfill_decisions(all_signals):
    """把 Worker 寫的 data/decisions/<市場日>.json 逐筆補上 outcome（append-only：
    只補空的或未成熟的 outcome，當時的 LLM 答案一字不改），
    並彙整成 data/dashboard/decisions_log.json 給 dashboard「Decisions」頁與 T8 統計。"""
    if not os.path.isdir(DECISIONS_DIR):
        return
    by_id = {s["signal_id"]: s for s in all_signals if s.get("signal_id")}
    filled_at = market_date_str()
    days = []
    for path in sorted(glob(os.path.join(DECISIONS_DIR, "*.json"))):
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
        except Exception as e:
            print(f"  ⚠️ decisions 檔損壞，略過：{path}（{e}）")
            continue
        changed = False
        for c in d.get("candidates", []):
            prev = c.get("outcome")
            if prev and prev.get("mature"):
                continue
            sig = by_id.get(c.get("signal_id"))
            if not sig:
                continue
            new = _outcome_of(sig)
            if new and new != prev:
                new["filled_at"] = filled_at
                c["outcome"] = new
                changed = True
        if changed:
            tmp = path + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)
        days.append({
            "market_date": d.get("market_date"), "decided_at": d.get("decided_at"),
            "model": d.get("model_served") or d.get("model"), "prompt_version": d.get("prompt_version"),
            "llm_called": d.get("llm_called"), "error": d.get("error"),
            "n_candidates": len(d.get("candidates", [])),
            "candidates": [{k: c.get(k) for k in ("signal_id", "ticker", "expiry", "strike", "entry_price",
                                                   "strategy", "sell_points", "q_event", "q_gap", "q_delta",
                                                   "note", "status", "outcome")}
                           for c in d.get("candidates", [])],
        })

    # T8 摘要：LLM 說「到期前有排定事件」的 vs 沒有的，成熟後命中率各多少（樣本夠了才有意義）
    def _bucket(c):
        a = (c.get("q_event") or {}).get("answer") if isinstance(c.get("q_event"), dict) else None
        return a if a in ("有", "無", "未確認") else "未答"
    stats = {}
    for day in days:
        for c in day["candidates"]:
            o = c.get("outcome")
            if not o or not o.get("mature"):
                continue
            b = stats.setdefault(_bucket(c), {"n": 0, "hit_2x": 0, "peaks": []})
            b["n"] += 1
            b["hit_2x"] += int(o["peak"] >= VERDICT_RULES["spike"])
            b["peaks"].append(o["peak"])
    summary = {k: {"n": v["n"], "hit_rate": round(v["hit_2x"] / v["n"], 3),
                   "avg_peak": round(sum(v["peaks"]) / v["n"], 2)} for k, v in stats.items()}
    out = {"generated_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'), "n_days": len(days),
           "t8_by_event_answer": summary, "days": list(reversed(days))}
    os.makedirs(os.path.join(DATA_DIR, "dashboard"), exist_ok=True)
    out_path = os.path.join(DATA_DIR, "dashboard", "decisions_log.json")
    tmp = out_path + ".tmp"
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)
    print(f"  🤖 decisions：{len(days)} 天 → data/dashboard/decisions_log.json")


def main():
    print(f"🌑 啟動 Shadow Tracer：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    os.makedirs(IV_LOG_DIR, exist_ok=True)

    # 處理「本月 + 上月」兩個檔（因為月初時，上月的信號可能還在 T+20 回填期）
    now = datetime.now()
    months = [now.strftime("%Y-%m")]
    prev_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    months.append(prev_month)

    mkt_date = market_date_str()
    loaded = {}
    for month_str in months:
        signals, path = load_month_signals(month_str)
        if signals is None:
            print(f"  ⏭️  {month_str} 無信號檔，跳過。")
            continue

        print(f"\n📂 處理 {month_str}（{len(signals)} 筆信號）")
        updated = backfill(signals, mkt_date)
        # PLAN 4.1 P0-b：每日路徑紀錄（未到期信號）
        try:
            record_paths(signals, mkt_date)
        except Exception as e:
            print(f"  ⚠️ 路徑紀錄失敗（不影響回填）：{e}")

        # 寫回 JSON（原子寫入：先寫 tmp 再 replace，中途掛掉不會留下半個檔）
        tmp = path + ".tmp"
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(signals, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        loaded[month_str] = signals

    # PLAN 4.1 P0-d：策略矩陣——用全部月份（含已封存的）重算，寫 JSON + 附進各月 SHADOWLOG
    matrix_md = ""
    try:
        import strategy_lab as SL
        all_sigs = []
        for f in sorted(glob(os.path.join(IV_LOG_DIR, "signals_*.json"))):
            with open(f, encoding='utf-8') as fh:
                all_sigs.extend(json.load(fh))
        mx = SL.compute_matrix(all_sigs, universe_dir=os.path.join(DATA_DIR, "universe_spots"))
        with open(os.path.join(DATA_DIR, "strategy_matrix.json"), 'w', encoding='utf-8') as f:
            json.dump(mx, f, ensure_ascii=False, indent=2)
        matrix_md = SL.render_matrix_md(mx)
        print(f"  🧭 策略矩陣：成熟 {mx['n_mature']} / {mx['n_signals']} 筆 → data/strategy_matrix.json")
    except Exception as e:
        print(f"  ⚠️ 策略矩陣失敗：{e}")

    # 第 5 批：LLM decisions 的事後結果回填（讀 all_sigs；失敗不擋 SHADOWLOG）
    try:
        backfill_decisions(all_sigs)
    except Exception as e:
        print(f"  ⚠️ decisions 回填失敗：{e}")

    for month_str, signals in loaded.items():
        md = generate_shadowlog_md(signals, month_str, matrix_md=matrix_md)
        md_path = f"SHADOWLOG_{month_str}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"  📝 {md_path} 已生成")

    print("\n✅ Shadow Tracer 完成。")


if __name__ == "__main__":
    main()
