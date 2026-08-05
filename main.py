"""
Scanner 3.12 — PATCH #2（2026-08-05）：標籤靜默缺漏 / TLT 根因 / 時間標示
【v3.12 改動】
- P0-3 📅 標籤靜默缺漏（缺漏比誤標危險——缺漏你看不到）：
  ETF → 📅無財報(ETF)、個股抓不到 → 📅財報日未知（兩者視覺可分）；
  報表頭加標籤覆蓋率（X 筆中 Y 筆有財報日）；缺漏 log 原始回傳到
  data/earnings_fetch_misses.log（8/4 事故：PFE 盤前雙 beat 開牌卻無標籤）
- P0-4 TLT 鏈抓取根因（方案 A）：獨立排程跑在 04:58 UTC 時段鏈常回空，
  主掃描 23:0X UTC 抓上百檔鏈全成功 → TLT 併入主掃描 session 執行
  （本週已成功即跳過；regime 維持週更），tlt_radar.yml 只留手動觸發；
  方案 C：鏈抓取失敗記診斷 log（expiry 數/exception 型別）到 tlt_fetch_errors.log
- P1-4 時間標示：「今日 TLT 收盤」→「最近收盤 + 實際交易日」（盤前執行時
  history 給的是前一交易日收盤）；比對基準同為 history Close 單一資料源

Scanner 3.11 — handoff #2（2026-08-01）殘項修正
【v3.11 改動】
- P0-1 渲染側 nan 防線：TLT 報告檔含 nan 一律不轉貼，改貼警示區塊
  （7/27-31 事故：舊程式寫出的 nan 報告被每天照貼，讀成「市場平靜」）
- P0-1 日更現況條：每天 1 次 API 抓 TLT 收盤，顯示「較快照日 ±%」，
  |Δ|>3% 警示「週更 regime 讀數可能已過期」（TLT 維持週更是設計決策，不改日更）
- P1-2 補強：低 IV 門檻 1%→5%，但只殺價外（價內 IV 合法偏低、spot 缺不誤殺）；
  末日區（DTE<5）IV 欄不顯示（到期日 IV 反推全面失真，7-45% 亂跳）
- P0-2 最後一哩：財報改用時間戳判斷——今日 16:00 後開牌→⚠️價格已失效、
  今晨已開→僅標📅財報已過（快照已反映）、明日 09:30 前→⚠️價格恐失效
- 環境指標：「吃不到財報」每日計數進報表頭與 data/earnings_window_history.csv
  （乾淨窗口數量可能比 TLT 溫度更貼近「今天有沒有獵物」）

Scanner 3.10 — 資料品質止血 + 財報日曆標籤 + 表格補欄
【v3.10 改動】（2026-07-31 handoff，依 17 份每日報表判讀反推的工具問題）
- P1-2 IV 硬過濾：IV <=1% 或 >300% 的合約直接剔除（IV 0% 數學上不可能，
    末日區 4-7% 是 IV 計算崩潰——垃圾資料不計分、不顯示）
- P1-3 點火倍數防爆：前日 Vol < 20 不算倍數（分母太小會出現 16944.7x 天文數字，
    讓無流動性垃圾票看起來最興奮），改標 🆕低基期不加分；倍數顯示封頂 >50x
- P0-2/P2-2 財報日曆標籤：接 yfinance earnings dates
    - 財報在今日盤後/明日盤前 → ⚠️價格已失效（16:00 收盤快照 vs 盤後開牌，報表價是死價格）
    - 每列標 📅覆蓋財報 / 📅吃不到財報 / 📅財報已過 三選一（只標記不排除——
      財報後的形狀本身有資訊，見 handoff「不建議現在改的」#4）
- P2-1 主表加「現價」「OTM%」欄（免每天手動反推 82% OTM 的 HOOD 200C 慘案）
- P2-3 流動性標籤：合約數 <10 或標的總 OI <10k → ⚠️流動性稀薄（紙上 3x ≠ 拿得到 3x）
- 信號快照加 P3-3 歸因欄（signal_day_underlying_move / why_it_popped，人工回填）
- 計分權重不動（維持 2026-07-06 改卷決策：分數只當及格線，樣本不足不重擬權重）

【v3.8 & 3.9 改動】「水快滾前提醒一下」——讓 scanner 在你被高分誘惑時標出陷阱
- 過濾一 ⚠️尾段價外：履約價距現價 >25%(按IV放寬) + DTE<45 → -3
    擋 F22C/META1100C 這類「極價外+短天期」的投機尾段
- 過濾二 ⚠️當沖刷量：Vol 大但 Δ7d≈0(OI沒沉澱) → -3
    擋 GOOGL575C 這類「量大但沒人真建倉」的假點火
- 過濾三 🏛️機構場：大市值 + IV<35% → -1
    標 AAPL320C/MSFT 這類「不會噴」的機構溫吞場
- main() 新增 Spot(現價)抓取；抓不到時過濾自動跳過，不誤殺
- 門檻集中在 RULE_CONFIG，要調鬆緊改那裡就好

【v3.7 改動】
- 讀 data/unknown_radar.json
- 在 README 加「🛸 字典外盲點」摘要區
- source_tag 加入 🛸盲點 標籤（只給有 ticker 的）
- 連續 2+ 天出現的盲點標的，自動加入主掃描清單

【v3.6 改動】
- 報表最下方自動插入 TLT 避險雷達 markdown

【v3.5 改動】
- 新增 fallen_saas 動態清單
"""
import pandas as pd
import yfinance as yf
import requests
import os
import io
import time
import random
import json
from datetime import datetime, timedelta, timezone

from enrichment import add_oi_delta, format_oi_delta, generate_deep_cards

# ==========================================
# 1. 設定與目標 (Configuration)
# ==========================================
DATA_DIR = "data"
GITHUB_USER = "clarencechien"
REPO_NAME = "optscnr"
BRANCH = "main"

TICKER_CATEGORIES = {
    'BIG_CAPS': ['TSLA', 'NVDA', 'AMD', 'MSFT', 'GOOG', 'MSTR', 'AAPL', 'IBIT', 'COIN', 'PLTR', 'SHOP', 'ANET', 'INTC'],
    'SMALL_CAPS': [
        'SMCI', 'OKLO', 'VST', 'RKLB', 'ASTS', 'IONQ', 'UPST', 'SOFI', 'DKNG',
        'IREN', 'NBIS', 'NEWT', 'COSM', 'ACRV', 'U', 'PATH', 'ROKU', 'HOOD',
        'TDOC', 'ZM', 'XYZ', 'OPEN', 'CRSP', 'NTLA', 'BEAM', 'PACB', 'TXG',
        'VCYT', 'HIMS', 'KTOS', 'ONDS', 'LUNR', 'JOBY', 'ACHR', 'SMR', 'NNE', 'VRT', 'CRWV'
    ]
}

RULE_CONFIG = {
    'VOL_SPIKE_RATIO': 2.5,
    'BIG_CAPS_THRESHOLD':  {'OI': 10000, 'VOL': 2500, 'PRICE': 30.0},
    'SMALL_CAPS_THRESHOLD': {'OI': 1500, 'VOL': 400, 'PRICE': 6.0},
    # === v3.8 三道「假高分」過濾門檻 ===
    'OTM_TAIL_PCT': 0.25,      # 履約價距現價 >25% = 極價外
    'OTM_TAIL_DTE': 45,        # 且 DTE<45 = 短天期 → 投機尾段，扣分
    'CHURN_VOL_MIN': 2000,     # Vol 夠大
    'CHURN_OI_DELTA_MAX': 200, # 但 Δ7d 幾乎沒增（OI 沒沉澱）→ 當沖刷量，扣分
    'INST_IV_MAX': 0.35,       # 大市值股 IV <35% = 機構溫吞場（不會噴）
    # === v3.9 第四道：暴動高 IV 過濾（RUN 暴露的漏洞）===
    'SURGE_IV_MIN': 80.0,      # IV >80% = 暴動已把 IV 炒高
    'SURGE_IV_DTE': 60,        # 且 DTE<60 短天期 → 進場會買在 IV 頂峰，等冷卻
    # === v3.10 資料品質 + 流動性（2026-07-31 handoff）===
    'IV_HARD_MIN': 1.0,          # IV <=1% = 資料異常（0% 數學上不可能），直接剔除
    'IV_HARD_MAX': 300.0,        # IV >300% = 資料異常/流動性崩潰，直接剔除
    # === v3.11 P1-2 補強（handoff #2）：7/31 末日區 7.6-8.8% 壞值穿過了 1% 門檻 ===
    # 低 IV 軟門檻提高到 5%，但只殺「價外」合約——深度價內合約 IV 可以合法偏低，
    # 抓不到現價（spot=0）時也不殺（不誤殺原則，同 v3.8 過濾一）
    'IV_SOFT_MIN': 5.0,          # IV <=5% 且價外 → 資料異常，剔除
    'IGNITION_MIN_PREV_VOL': 20, # 前日 Vol < 20 不算點火倍數（分母爆炸防呆）
    'IGNITION_DISPLAY_CAP': 50,  # 點火倍數顯示封頂：>50x 一律顯示 >50x
    'LIQUIDITY_MIN_CONTRACTS': 10,    # 今日掃到合約數 < 10 → 流動性稀薄
    'LIQUIDITY_MIN_TOTAL_OI': 10000,  # 標的總 OI < 10k → 流動性稀薄
}


# 動態小盤股集合：在 main() 初始化時填入
# catalyst / auto_watch / small_caps_momentum 進來且不在 BIG_CAPS 的標的會被加進來
_DYNAMIC_SMALL_CAPS = set()


def is_small_cap(symbol):
    """判定是否套用 SMALL_CAPS 閾值

    優先順序：
    1. 手動 SMALL_CAPS 名單（強制小盤）
    2. _DYNAMIC_SMALL_CAPS（動態加入的小盤）
    3. 否則用 BIG_CAPS 閾值
    """
    if symbol in TICKER_CATEGORIES['SMALL_CAPS']:
        return True
    if symbol in _DYNAMIC_SMALL_CAPS:
        return True
    return False


# ==========================================
# 2. 動態清單載入
# ==========================================
def load_auto_watch():
    path = os.path.join(DATA_DIR, "auto_watch.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get('tickers', [])
    except Exception as e:
        print(f"⚠️ auto_watch 載入失敗：{e}")
        return []


def load_catalyst_today():
    path = os.path.join(DATA_DIR, "catalyst_today.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get('tickers', [])
    except Exception as e:
        print(f"⚠️ catalyst 載入失敗：{e}")
        return []


def load_small_caps_momentum():
    """從 data/small_caps_momentum.json 載入每週更新的小盤動能股"""
    path = os.path.join(DATA_DIR, "small_caps_momentum.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get('tickers', [])
    except Exception as e:
        print(f"⚠️ small_caps_momentum 載入失敗：{e}")
        return []


def load_fallen_saas():
    """從 data/fallen_saas.json 載入每週更新的殞落 SaaS 重生候選"""
    path = os.path.join(DATA_DIR, "fallen_saas.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get('tickers', [])
    except Exception as e:
        print(f"⚠️ fallen_saas 載入失敗：{e}")
        return []


def load_unknown_radar():
    """從 data/unknown_radar.json 載入盲點雷達

    回傳：
    - tickers: 連續 2+ 天出現且有對應 ticker 的標的（加入主掃描）
    - all_blind_spots: 全部盲點清單（給 README 顯示）
    """
    path = os.path.join(DATA_DIR, "unknown_radar.json")
    if not os.path.exists(path):
        return [], []
    try:
        with open(path) as f:
            data = json.load(f)
        blind_spots = data.get('blind_spots', [])
        # 只把「連續 2+ 天 + 有 ticker」的加入主掃描
        strong_tickers = [
            b['ticker'] for b in blind_spots
            if b.get('is_strong') and b.get('ticker')
        ]
        return strong_tickers, blind_spots
    except Exception as e:
        print(f"⚠️ unknown_radar 載入失敗：{e}")
        return [], []


# ==========================================
# 2.5 財報日曆（v3.10 P0-2 + P2-2）
# ==========================================
def _today_et():
    """美東今日日期（掃描跑在 UTC 22-23 = 美東 17-19，取 -5 保守換算，同 us_market_traded_today）"""
    return (datetime.now(timezone.utc) - timedelta(hours=5)).date()


_EARNINGS_CACHE = {}


def _now_et_naive():
    """naive 的美東現在時間（UTC-5 保守近似，同 _today_et）"""
    return (datetime.now(timezone.utc) - timedelta(hours=5)).replace(tzinfo=None)


def _to_naive_et(ts):
    """把 yfinance 的 earnings timestamp 轉 naive ET。tz-aware → 轉美東去 tz；naive 視為 ET。"""
    try:
        if getattr(ts, 'tzinfo', None) is not None:
            return ts.tz_convert('America/New_York').tz_localize(None)
    except Exception:
        pass
    return ts


# 已知無財報的 ETF/基金（quoteType 抓不到時的靜態後盾）
KNOWN_ETF_TICKERS = {'IBIT'}


def _log_earnings_miss(symbol, raw_desc):
    """v3.12 P0-3：個股財報日抓不到時記下原始回傳，缺漏才有辦法定位（不再只能猜）"""
    line = f"{datetime.now().isoformat()} {symbol} {raw_desc}\n"
    print(f"  🩺 財報日缺漏：{symbol}（{raw_desc}）")
    try:
        with open(os.path.join(DATA_DIR, "earnings_fetch_misses.log"), 'a', encoding='utf-8') as f:
            f.write(line)
    except Exception:
        pass


def get_earnings_window(symbol):
    """抓標的的 (下次財報 ts, 上次財報 ts, kind)，naive ET。
    kind：'ok'=有財報日 / 'etf'=ETF基金本來就沒財報 / 'unknown'=個股但抓不到（缺漏，須可見）

    P0-2 背景：掃描時間 23:0X UTC = 19:0X ET，yf 選擇權是 16:00 ET 收盤快照，
    財報多在 16:05-16:30 ET 開牌 → 當天盤後財報股的報表權利金是財報前的死價格。

    v3.12（PATCH #2 P0-3）：缺漏比誤標危險——無標籤會被判讀者讀成「這格沒資訊」，
    實際是「有資訊但沒抓到」。ETF 與個股資料缺失必須視覺可分，缺漏要 log 原始回傳。
    """
    if symbol in _EARNINGS_CACHE:
        return _EARNINGS_CACHE[symbol]
    nxt, prev, kind = None, None, 'unknown'
    raw_desc = ""
    try:
        tk = yf.Ticker(symbol)
        edf = tk.get_earnings_dates(limit=12)
        if edf is not None and len(edf) > 0:
            now_et = _now_et_naive()
            stamps = sorted({_to_naive_et(ts) for ts in edf.index})
            future = [t for t in stamps if t > now_et]
            past = [t for t in stamps if t <= now_et]
            nxt = future[0] if future else None
            prev = past[-1] if past else None
            kind = 'ok'
        else:
            raw_desc = f"empty_return:{type(edf).__name__}:len={0 if edf is None else len(edf)}"
    except Exception as e:
        raw_desc = f"exception:{type(e).__name__}:{e}"

    if kind != 'ok':
        # ETF/基金判定：本來就沒財報，不算缺漏
        if symbol in KNOWN_ETF_TICKERS:
            kind = 'etf'
        else:
            qt = ''
            try:
                qt = str(tk.fast_info.get('quoteType', '') or '')
            except Exception:
                pass
            if not qt:
                try:
                    qt = str((tk.info or {}).get('quoteType', '') or '')
                except Exception:
                    pass
            if qt.upper() in ('ETF', 'MUTUALFUND', 'INDEX', 'CRYPTOCURRENCY'):
                kind = 'etf'
        if kind == 'unknown':
            _log_earnings_miss(symbol, raw_desc or "no_data")

    _EARNINGS_CACHE[symbol] = (nxt, prev, kind)
    return nxt, prev, kind


def add_earnings_tags(df):
    """為每列附加財報標籤（只標記、不改分——handoff「不建議現在改的」#4）：

    1. ⚠️價格已失效：財報在今日盤後（報表價已死）/ 明日盤前（隔夜就死）
    2. 三選一分流標籤（自動化第⑩格物種閘門，7/28 F、7/29 T、7/30 PYPL 全死在這格）：
       📅覆蓋財報 = 到期日 >= 下次財報 → 二元事件票
       📅財報已過 = 14 天內剛開完牌且窗口吃不到下次 → 災後/慶功反彈賭局
       📅吃不到財報 = 窗口內無事件 → 純動能
    """
    today = _today_et()
    tomorrow = today + timedelta(days=1)

    symbols = list(df['Stock'].unique())
    print(f"  📅 抓取 {len(symbols)} 檔財報日曆...")
    for s in symbols:
        get_earnings_window(s)
        time.sleep(random.uniform(0.1, 0.3))

    def row_tag(r):
        nxt_ts, prev_ts, kind = _EARNINGS_CACHE.get(r['Stock'], (None, None, 'unknown'))
        # v3.12 P0-3：兩種「沒有財報日」必須視覺可分——
        # ETF 本來就沒財報（正常）vs 個股抓不到（缺漏，判讀時要人工查證）
        if kind == 'etf':
            return "📅無財報(ETF)"
        nxt = nxt_ts.date() if nxt_ts is not None else None
        prev = prev_ts.date() if prev_ts is not None else None
        parts = []

        # === v3.11 P0-2 最後一哩：用時間戳判斷價格是否已死 ===
        # 已失效：財報「今日 16:00 之後」已開牌（16:00 快照是財報前的死價格）。
        #   今日早上開的牌快照已反映 → 不標（由下方 📅財報已過 呈現）。
        #   時間戳只有日期（00:00，來源沒給時間）→ 保守標已失效。
        if prev == today:
            t = prev_ts.time()
            if t.hour == 0 and t.minute == 0:
                parts.append(f"⚠️價格已失效(財報{prev_ts.strftime('%m-%d')})")
            elif (t.hour, t.minute) >= (15, 55):
                parts.append(f"⚠️價格已失效(財報{prev_ts.strftime('%m-%d')}盤後)")
        # 恐失效：財報在「明日開盤(09:30 ET)前」→ 今晚到明早之間價格會死
        if nxt == tomorrow:
            t = nxt_ts.time()
            if (t.hour == 0 and t.minute == 0) or (t.hour, t.minute) <= (9, 30):
                parts.append(f"⚠️價格恐失效(財報{nxt_ts.strftime('%m-%d')}盤前)")
        # 邊界：財報「今晚稍後」才開（掃描 19:0X ET 之後，罕見）→ 視同今日盤後即將失效
        if nxt == today:
            parts.append(f"⚠️價格恐失效(財報{nxt_ts.strftime('%m-%d')}盤後)")

        try:
            expiry_d = pd.to_datetime(r['Expiry']).date()
        except Exception:
            expiry_d = None
        if expiry_d is not None:
            if nxt and expiry_d >= nxt:
                parts.append(f"📅覆蓋財報({nxt.strftime('%m-%d')})")
            elif prev and (today - prev).days <= 14:
                parts.append(f"📅財報已過({prev.strftime('%m-%d')})")
            elif nxt:
                parts.append(f"📅吃不到財報(下次{nxt.strftime('%m-%d')})")
            else:
                # v3.12 P0-3：個股但財報日抓不到（或下次未排定）→ 缺漏必須可見。
                # 8/4 事故：PFE 盤前雙 beat 開牌卻無任何標籤，判讀者讀成「沒資訊」
                # ——而它正好是當日唯一三格全過的票
                parts.append("📅財報日未知")
        return " ".join(parts)

    extra = df.apply(row_tag, axis=1)
    df['Tags'] = (df['Tags'].fillna('') + ' ' + extra).str.strip()
    n_dead = int(extra.str.contains('價格').sum())
    n_cover = int(extra.str.contains('覆蓋').sum())
    print(f"  📅 財報標籤完成：{n_dead} 筆價格失效警示、{n_cover} 筆覆蓋財報")
    return df


# ==========================================
# 3. 資料抓取
# ==========================================
def get_target_dates():
    """生成理想的目標日期"""
    dates = set()
    today = datetime.now()

    for i in range(2):
        target = today + timedelta(days=(4 - today.weekday() + 7 * i) % 7)
        dates.add(target.strftime('%Y-%m-%d'))

    for i in range(6):
        first_day = (today.replace(day=1) + timedelta(days=32 * i)).replace(day=1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)
        third_friday = first_friday + timedelta(days=14)
        if third_friday >= today:
            dates.add(third_friday.strftime('%Y-%m-%d'))

    for year in [today.year + 1, today.year + 2]:
        for month in [1, 6]:
            first_day = datetime(year, month, 1)
            first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)
            dates.add((first_friday + timedelta(days=14)).strftime('%Y-%m-%d'))

    return sorted(list(dates))


def fetch_yesterday_data_from_github():
    """
    優先讀本地歷史 CSV（最穩，因為 actions/checkout 已經把整個 repo 拉下來）
    Fallback 到 GitHub raw

    這是修「🚀點火」標籤消失的關鍵：
    GitHub raw 對剛 commit 的檔案有 CDN cache 延遲，
    讀本地檔可以完全繞過這個問題。
    """
    # 嘗試本地 1-5 天前的 CSV
    for days_back in range(1, 6):
        target_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        local_path = os.path.join(DATA_DIR, f"{target_date}.csv")
        if os.path.exists(local_path):
            try:
                df = pd.read_csv(local_path)
                print(f"📅 從本地載入 {target_date} 的數據（{len(df)} 筆），啟動動能比對。")
                return df
            except Exception as e:
                print(f"⚠️ 本地 {target_date}.csv 讀取失敗：{e}")
                continue

    # 本地 latest.csv 試試
    local_latest = os.path.join(DATA_DIR, "latest.csv")
    if os.path.exists(local_latest):
        try:
            df = pd.read_csv(local_latest)
            print(f"📅 從本地載入 latest.csv（{len(df)} 筆），啟動動能比對。")
            return df
        except Exception:
            pass

    # 最後才走 GitHub raw（保留作為遠端 fallback）
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{DATA_DIR}/latest.csv"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            print("📅 從 GitHub raw 載入歷史數據，啟動動能比對。")
            return pd.read_csv(io.StringIO(res.text))
    except Exception:
        pass

    print("⚠️ 無法載入歷史數據，降級為盲測模式（合約會缺「🚀點火」標籤）。")
    return None


# ==========================================
# 4. 規則引擎
# ==========================================
def apply_rules(row, prev_data=None):
    tags = []
    action = "HOLD"
    score = 0

    symbol, price, oi, vol = row['Stock'], row['Ask'], row['OpenInterest'], row['Volume']
    expiry, strike = row['Expiry'], row['Strike']
    iv = row.get('IV', 0.0)
    dte = row.get('DTE', 0)
    spot = row.get('Spot', 0.0)  # 現價，可能為 0（抓不到時）

    cfg = RULE_CONFIG['SMALL_CAPS_THRESHOLD'] if is_small_cap(symbol) else RULE_CONFIG['BIG_CAPS_THRESHOLD']
    p_limit = cfg['PRICE'] * (2.0 if dte > 180 else 1.0)

    if price > p_limit or oi < (cfg['OI'] * 0.5):
        return "", "HOLD", 0

    # === 計算價外程度（otm_pct）===
    # otm_pct = (履約價 - 現價) / 現價；正值=價外，越大越價外
    # 抓不到現價(spot<=0)時設為 None，用到它的判斷一律跳過（不誤殺）
    otm_pct = None
    if spot and spot > 0:
        otm_pct = (strike - spot) / spot

    is_gamble = (dte < 5)
    if is_gamble:
        tags.append("🎲末日結算")
        score -= 2

    vol_oi_ratio = vol / oi if oi > 0 else 0
    if vol_oi_ratio > 1.2 and vol > cfg['VOL']:
        tags.append("🚨異常掃貨")
        score += 5
        action = "STRONG_BUY"

    ignition = False
    if prev_data is not None and not prev_data.empty:
        prev_row = prev_data[(prev_data['Stock'] == symbol) & (prev_data['Expiry'] == expiry) & (prev_data['Strike'] == strike)]
        if not prev_row.empty:
            prev_vol = prev_row.iloc[0]['Volume']
            if prev_vol > 0 and (vol / prev_vol) >= RULE_CONFIG['VOL_SPIKE_RATIO']:
                # v3.10 P1-3：前日只成交幾口時，倍數會出現 16944.7x 這種天文數字，
                # 讓無流動性垃圾票視覺上最興奮。分母 < 門檻 → 只標低基期，不算倍數、不加分。
                if prev_vol < RULE_CONFIG['IGNITION_MIN_PREV_VOL']:
                    tags.append(f"🆕低基期(前日Vol{int(prev_vol)})")
                else:
                    ratio = vol / prev_vol
                    cap = RULE_CONFIG['IGNITION_DISPLAY_CAP']
                    ratio_str = f">{cap}x" if ratio > cap else f"{ratio:.1f}x"
                    tags.append(f"🚀點火({ratio_str})")
                    score += 3
                    ignition = True
        else:
            if vol > cfg['VOL'] and vol > (oi * 0.2):
                tags.append("🆕新倉暴量")
                score += 3
                ignition = True
    else:
        if vol > cfg['VOL'] and vol > (oi * 0.2):
            tags.append("🚀突發暴量")
            score += 2
            ignition = True

    if iv > 150:
        tags.append("⚠️IV頂峰")
        score -= 3

    is_leaps = False
    is_smoke = False
    if dte > 300:
        tags.append("🔭LEAPS"); score += 1; is_leaps = True
    elif price < 1.0:
        tags.append("🚬菸屁股"); score += 1; is_smoke = True

    if oi > 30000:
        tags.append("🔥萬人塚"); score += 2

    # ============================================================
    # === v3.8 過濾一：極價外尾段（OTM% 過大 + 短天期）===
    # 主升段點火（如 F 16C，距現價近）vs 尾段狂歡（如 F 22C / META 1100C，極價外）
    # scanner 給一樣的點火分，但意義相反。極價外+短天期=投機尾段，扣分+警示。
    # IV 調整：高 IV 股本來就容易大幅波動，門檻按 IV 放寬，避免誤殺 HOOD 這類高波動股。
    #   有效門檻 = 基準25% × (1 + (IV-50%)/100)，IV70%→門檻30%，IV100%→門檻37.5%
    # 只在抓得到現價(otm_pct 非 None)時才判斷，否則跳過不誤殺。
    if otm_pct is not None and ignition:
        iv_frac = iv / 100.0 if iv > 0 else 0.5
        otm_threshold = RULE_CONFIG['OTM_TAIL_PCT'] * (1 + max(0, iv_frac - 0.5))
        if otm_pct > otm_threshold and dte < RULE_CONFIG['OTM_TAIL_DTE']:
            tags.append(f"⚠️尾段價外({otm_pct*100:.0f}%)")
            score -= 3

    # === v3.8 過濾三：機構溫吞場（大市值 + 低 IV）===
    # 大市值權值股 + IV<35% = 機構避險/收租場，不會噴，free ride 啟動不了
    # （AAPL 320C IV26%、MSFT 這種）。標警示但不重扣（有時你只是想看看）。
    if (not is_small_cap(symbol)) and iv > 0 and (iv / 100.0) < RULE_CONFIG['INST_IV_MAX']:
        tags.append("🏛️機構場")
        score -= 1

    # === v3.9 過濾四：暴動高 IV（RUN 暴露的漏洞）===
    # 點火 + IV 已被炒到很高 + 短天期 = 進場買在 IV 頂峰，會被 crush。
    # RUN 暴動當天 IV 飆到 90%+ 卻給高分 → 應提醒「等冷卻」。
    # 盯的是 IV 這個真變數，不是「第幾天」這個表象。標警示降分，不是排除。
    if ignition and iv >= RULE_CONFIG['SURGE_IV_MIN'] and dte < RULE_CONFIG['SURGE_IV_DTE']:
        tags.append(f"⚠️暴動高IV({iv:.0f}%)")
        score -= 2

    if action != "STRONG_BUY" and ignition and (is_leaps or is_smoke):
        action = "BUY_WATCH"
        score += 2

    if is_gamble and action in ["STRONG_BUY", "BUY_WATCH"]:
        action = "GAMBLE"

    return " ".join(tags), action, score


# ==========================================
# 5. 報表生成
# ==========================================
def generate_report(df):
    print("\n🔬 開始計算 enrichment...")
    df, hist_date = add_oi_delta(df)
    print(f"  ✅ OI Δ7d 已計算 (vs {hist_date})")

    # ============================================================
    # === v3.8 過濾二：當沖刷量（Vol 大但 Δ7d≈0）===
    # 點火倍數會被當沖量灌水。真建倉=Vol大+Δ7d大；當沖刷量=Vol大+Δ7d≈0(OI沒沉澱)。
    # 如 GOOGL 575C：Vol 2509 但 Δ7d +1 → 假點火。這裡 enrichment 後才有 OI_d7，故在此後處理。
    if 'OI_d7' in df.columns:
        churn_mask = (
            (df['Volume'] >= RULE_CONFIG['CHURN_VOL_MIN']) &
            (df['OI_d7'].abs() <= RULE_CONFIG['CHURN_OI_DELTA_MAX'])
        )
        n_churn = int(churn_mask.sum())
        if n_churn > 0:
            df.loc[churn_mask, 'Score'] = df.loc[churn_mask, 'Score'] - 3
            df.loc[churn_mask, 'Tags'] = df.loc[churn_mask, 'Tags'] + " ⚠️當沖刷量"
            print(f"  🔍 當沖刷量過濾：{n_churn} 筆 Vol大但OI沒增，已降級")
        # 重新依調整後分數排序
        df = df.sort_values(by=['Score', 'Volume'], ascending=[False, False])

    # === v3.10 財報日曆標籤（P0-2 價格已失效 + P2-2 覆蓋/吃不到/已過）===
    try:
        df = add_earnings_tags(df)
    except Exception as e:
        print(f"  ⚠️ 財報標籤失敗（降級跳過）：{e}")

    # === v3.11 環境指標：「吃不到財報」每日計數（handoff #2 附註）===
    # 7/31 全表僅 4 筆吃不到財報——連四天三格全過的票全死在物種閘門，
    # 不是判讀太嚴，是市場上根本沒有乾淨無事件的窗口。這個數字可能比
    # TLT 溫度更貼近「今天有沒有你要的獵物」，記錄下來當環境序列。
    # 分母定義（PATCH 2026-08-04 §7.2）：report_rows = 進入報表的信號列數
    # （通過門檻、score>0 或 action!=HOLD 的合約），不是掃描到的全部合約。
    # 序列可比性依賴這個定義不變；欄名 report_rows 即為此意。
    clean_window_count = int(df['Tags'].str.contains('吃不到財報', na=False).sum())
    try:
        cw_path = os.path.join(DATA_DIR, "earnings_window_history.csv")
        today_str = datetime.now().strftime('%Y-%m-%d')
        if os.path.exists(cw_path):
            cw = pd.read_csv(cw_path)
            if 'total_rows' in cw.columns:  # 舊欄名遷移（2026-08-01/02 兩列）
                cw = cw.rename(columns={'total_rows': 'report_rows'})
            cw = cw[cw['date'] != today_str]  # 同日重跑取代不重複
        else:
            cw = pd.DataFrame(columns=['date', 'clean_window_count', 'report_rows'])
        cw = pd.concat([cw, pd.DataFrame([{
            'date': today_str, 'clean_window_count': clean_window_count, 'report_rows': len(df)}])],
            ignore_index=True)
        cw.to_csv(cw_path, index=False)
    except Exception as e:
        print(f"  ⚠️ 乾淨窗口計數寫入失敗：{e}")

    # === v3.10 P2-3 流動性標籤：合約數 < 10 或標的總 OI < 10k → ⚠️流動性稀薄 ===
    # 深度卡本來就有這兩個數字，只是沒進主表（CNP 45C 拿 9 分但全標的只 2 條合約/OI 3,632）。
    # 出場紀律需要流動性才能執行——紙上 3x 和拿得到 3x 是兩回事。
    try:
        depth = df.groupby('Stock').agg(
            n_contracts=('Strike', 'count'), total_oi=('OpenInterest', 'sum'))
        thin_info = {
            sym: (int(row['n_contracts']), int(row['total_oi']))
            for sym, row in depth.iterrows()
            if row['n_contracts'] < RULE_CONFIG['LIQUIDITY_MIN_CONTRACTS']
            or row['total_oi'] < RULE_CONFIG['LIQUIDITY_MIN_TOTAL_OI']
        }
        if thin_info:
            thin_mask = df['Stock'].isin(thin_info)
            df.loc[thin_mask, 'Tags'] = df.loc[thin_mask].apply(
                lambda r: f"{r['Tags']} ⚠️流動性稀薄({thin_info[r['Stock']][0]}條/OI{thin_info[r['Stock']][1]:,})".strip(),
                axis=1
            )
            print(f"  💧 流動性稀薄標籤：{len(thin_info)} 檔標的")
    except Exception as e:
        print(f"  ⚠️ 流動性標籤失敗（降級跳過）：{e}")

    auto_watch = set(load_auto_watch())
    catalyst = set(load_catalyst_today())
    small_caps_mom = set(load_small_caps_momentum())
    fallen_saas = set(load_fallen_saas())
    unknown_tickers, all_blind_spots = load_unknown_radar()
    unknown_set = set(unknown_tickers)

    def source_tag(symbol):
        if symbol in catalyst: return "📰催化劑"
        elif symbol in fallen_saas: return "💀重生"
        elif symbol in unknown_set: return "🛸盲點"
        elif symbol in small_caps_mom: return "🎰動能"
        elif symbol in auto_watch: return "🔭候選"
        return ""

    md = "# 🚬 每日妖股獵殺報表 (Scanner 3.12 / yf Engine)\n\n"
    md += f"**掃描時間**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
    md += (f"**📅 乾淨窗口計數**: 今日 {clean_window_count} 筆「吃不到財報」（窗口內無事件的純動能局）"
           f"／報表信號 {len(df)} 筆（分母＝進入報表的信號列，非掃描到的全部合約）。"
           f"數字越小＝市場越被財報事件佔據，今天越沒有你要的獵物"
           f"（環境序列：`data/earnings_window_history.csv`）\n\n")
    md += _earnings_coverage_line(df)

    if catalyst:
        md += f"**📰 今日催化劑股**: {', '.join(sorted(catalyst))}\n\n"
    if fallen_saas:
        md += f"**💀 本週重生候選**: {', '.join(sorted(fallen_saas))}\n\n"
    if unknown_set:
        md += f"**🛸 字典外盲點（連 2+ 天上新聞但不在我清單）**: {', '.join(sorted(unknown_set))}\n\n"
    if small_caps_mom:
        md += f"**🎰 本週動能小盤股**: {', '.join(sorted(small_caps_mom))}\n\n"
    if auto_watch:
        md += f"**🔭 本週候選池**: {', '.join(sorted(auto_watch))}\n\n"

    # 盲點雷達詳細摘要
    if all_blind_spots:
        strong = [b for b in all_blind_spots if b.get('is_strong')]
        new = [b for b in all_blind_spots if not b.get('is_strong')]
        md += "### 🛸 盲點雷達詳情\n\n"
        if strong:
            md += "**連續多天出現（強訊號）**：\n"
            for b in strong[:5]:
                tk_str = f"`{b['ticker']}`" if b.get('ticker') else "_私募/未找到 ticker_"
                md += f"- **{b['name']}** {tk_str} — 連 {b['consecutive_days']} 天 / 累積 {b.get('total_mentions', b['mentions_today'])} 次\n"
        if new:
            md += "\n**今日新出現**：\n"
            for b in new[:5]:
                tk_str = f"`{b['ticker']}`" if b.get('ticker') else "_私募/未找到 ticker_"
                md += f"- {b['name']} {tk_str} — {b['mentions_today']} 次\n"
        md += "\n"

    df['Expiry'] = pd.to_datetime(df['Expiry'])

    # v3.10 P2-1：每列加「現價」「OTM%」——體檢卡第①②欄，之前只能靠尾段價外標籤反推
    # （7/13 HOOD 200C 拿全表最高 9 分，實際 82% OTM，深度卡沒涵蓋就完全看不到）
    if 'Spot' not in df.columns:
        df['Spot'] = 0.0

    def format_view(sub_df):
        view = sub_df[['Stock', 'Expiry', 'Strike', 'Spot', 'Ask', 'OpenInterest', 'OI_d7', 'Volume', 'IV', 'Tags', 'Score']].copy()
        view['_DTE'] = sub_df['DTE'].values
        view['Expiry'] = view['Expiry'].dt.strftime('%Y-%m-%d')
        view['OTM%'] = view.apply(
            lambda r: f"{(r['Strike'] - r['Spot']) / r['Spot'] * 100:+.0f}%" if r['Spot'] and r['Spot'] > 0 else "—",
            axis=1
        )
        view['Spot'] = view['Spot'].apply(lambda x: f"{x:.2f}" if x and x > 0 else "—")
        # v3.11 P1-2：末日區（DTE<5）IV 計算失真（剩餘時間→0 反推崩潰，7-45% 亂跳），
        # 整欄不顯示，避免拿它做任何判斷
        view['IV'] = view.apply(
            lambda r: "—" if r['_DTE'] < 5 else f"{r['IV']:.1f}%", axis=1)
        view = view.drop(columns=['_DTE'])
        view['OI_d7'] = view['OI_d7'].apply(format_oi_delta)
        view['Tags'] = view.apply(
            lambda r: f"{source_tag(r['Stock'])} {r['Tags']}".strip(),
            axis=1
        )
        view = view[['Stock', 'Expiry', 'Strike', 'Spot', 'OTM%', 'Ask', 'OpenInterest', 'OI_d7', 'Volume', 'IV', 'Tags', 'Score']]
        view.columns = ['代號', '到期日', '履約價', '現價', 'OTM%', '價格', '持倉(OI)', 'Δ7d', '成交(Vol)', 'IV', '標籤', '分數']
        return view

    md += "## 🏆 TL;DR 總結 (精選狙擊名單)\n"
    md += "> 策略：過濾掉結算日雜訊，直擊 Score >= 8 的核心異動。**Δ7d** 顯示「過去 7 天 OI 累積變化」——大正數代表機構在持續建倉。\n\n"
    tldr_df = df[(df['Score'] >= 8) & (df['Action'] != 'GAMBLE')].sort_values(by=['Score', 'Volume'], ascending=[False, False]).head(10)
    if not tldr_df.empty:
        md += format_view(tldr_df).to_markdown(index=False) + "\n\n"
    else:
        md += "*今日無高分狙擊標的。*\n\n"

    action_order = ['STRONG_BUY', 'BUY_WATCH', 'GAMBLE', 'HOLD']
    for action in action_order:
        sub_df = df[df['Action'] == action]
        if sub_df.empty: continue

        if action == 'STRONG_BUY' or action == 'BUY_WATCH':
            icon = "🚨" if action == 'STRONG_BUY' else "👀"
            title_action = "核彈級異動 (STRONG_BUY)" if action == 'STRONG_BUY' else "重點觀察 (BUY_WATCH)"
            md += f"## {icon} {title_action}\n\n"

            leaps_mask = sub_df['DTE'] > 120
            leaps_df = sub_df[leaps_mask].copy()
            short_df = sub_df[~leaps_mask].copy()

            if not leaps_df.empty:
                md += "### 🔭 遠期埋伏 (LEAPS > 120天)\n"
                md += "> 策略：時間換空間，跟隨聰明錢長期囤貨 (按分數與持倉排序，每股至多 3 條)。\n\n"
                leaps_df = leaps_df.sort_values(by=['Score', 'OpenInterest'], ascending=[False, False])
                leaps_df = leaps_df.groupby('Stock').head(3)
                md += format_view(leaps_df).to_markdown(index=False) + "\n\n"

            if not short_df.empty:
                md += "### 🚀 短期波段 (Short Term < 120天)\n"
                md += "> 策略：波段點火，關注資金流向 (排除 DTE<5，按分數與成交排序，每股至多 3 條)。\n\n"
                short_df = short_df.sort_values(by=['Score', 'Volume'], ascending=[False, False])
                short_df = short_df.groupby('Stock').head(3)
                md += format_view(short_df).to_markdown(index=False) + "\n\n"

        elif action == 'GAMBLE':
            md += f"## 🎲 末日賭博專區 (DTE < 5)\n"
            md += "> 警告：極端短線結算，高機率為造市商平倉雜訊，若要玩請當樂透買。\n"
            md += "> 本區 IV 欄不顯示——到期日剩餘時間趨近 0，IV 反推全面失真，不可用於判斷。\n\n"
            sub_df = sub_df.sort_values(by=['Volume'], ascending=[False]).head(15)
            md += format_view(sub_df).to_markdown(index=False) + "\n\n"

        else:
            md += f"## 🚬 常規雷達 (HOLD)\n"
            sub_df = sub_df.sort_values(by=['Score', 'Volume'], ascending=[False, False]).head(20)
            md += format_view(sub_df).to_markdown(index=False) + "\n\n"

    # === Top 5 深度卡片 ===
    print("\n🔬 開始生成深度卡片...")
    try:
        deep_section = generate_deep_cards(df, top_n=5)
        md += deep_section
    except Exception as e:
        print(f"  ⚠️ 深度卡片生成失敗：{e}")
        md += f"\n## 🔬 深度分析\n*（生成失敗：{e}）*\n"

    # === TLT 避險雷達（如果有產出，附在最後）===
    # v3.11（handoff #2 P0-1）：
    # 1. 渲染側 nan 防線——就算舊程式/壞資料寫出含 nan 的報告檔，主報表也不轉貼，
    #    改貼警示區塊（7/27-7/31 事故：nan 報告被每天照貼五天，讀成「市場平靜」）
    # 2. 廉價日更「現況條」——TLT 為週更 regime gauge（維持週更是設計決策），
    #    每天只多抓 1 次 TLT 收盤價，顯示「較快照日變動 %」告訴你週快照有沒有過期
    tlt_report_path = os.path.join(DATA_DIR, "tlt_radar_report.md")
    if os.path.exists(tlt_report_path):
        try:
            with open(tlt_report_path, encoding='utf-8') as f:
                tlt_md = f.read()
            if 'nan' in tlt_md.lower():
                md += ("\n## 📉 TLT 避險雷達\n\n"
                       "⚠️ **快照檔含無效資料（nan），本區不轉貼**——"
                       "「抓取失敗」不等於「市場平靜」，請勿把本區當環境訊號。\n"
                       "等 tlt_radar 下次成功抓取後自動恢復。\n\n")
                print("  ⚠️ TLT 報告含 nan，已替換為警示區塊")
            else:
                md += tlt_md
                md += _tlt_daily_status_line()
                print("  ✅ TLT 避險雷達已附加（含日更現況條）")
        except Exception as e:
            print(f"  ⚠️ TLT 報告載入失敗：{e}")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("📝 README.md 報表已生成。")

    # === v3.9 信號快照（給 shadow_tracer 事後回填 T+N 用）===
    # 只記「市場事實」（信號當下的價格/IV），不記「你持有什麼、賺賠多少」
    # 這份是 append-only 永久保存，跟 7 天輪替的掃描 CSV 是不同生命週期
    try:
        save_signal_snapshot(df)
    except Exception as e:
        print(f"  ⚠️ 信號快照儲存失敗：{e}")


def _earnings_coverage_line(df):
    """v3.12 P0-3（T12）：📅 標籤覆蓋率——缺漏率變成可監控的數字，不靠人工發現"""
    total = len(df)
    known = int(df['Tags'].str.contains('覆蓋財報|財報已過|吃不到財報', na=False, regex=True).sum())
    unknown = int(df['Tags'].str.contains('財報日未知', na=False).sum())
    etf = int(df['Tags'].str.contains(r'無財報\(ETF\)', na=False).sum())
    line = (f"**📅 標籤覆蓋率**: 報表 {total} 筆中 {known} 筆有財報日"
            f"（{unknown} 筆未知、{etf} 筆 ETF）")
    if unknown > 0:
        line += "——缺漏原始回傳見 `data/earnings_fetch_misses.log`"
    return line + "\n\n"


def _tlt_daily_status_line():
    """v3.11 P0-1：TLT 週更快照的日更「現況條」。

    只抓 1 次 TLT 收盤價（成本可忽略），與週快照價比較：
    |Δ| > 3% → 加警示「週更 regime 讀數可能已過期」。
    補的是 7/22-23 的缺口：45 分讀數是 7/20 抓的，完全沒含入油價破百與
    殖利率創高的衝擊，而報表沒有任何跡象顯示這件事。
    任何失敗都靜默跳過（現況條是輔助資訊，不值得為它擋報表）。
    """
    try:
        with open(os.path.join(DATA_DIR, "tlt_radar.json"), encoding='utf-8') as f:
            snap = json.load(f)
        snap_price = float(snap.get('tlt_price') or 0)
        snap_date = str(snap.get('updated_at', ''))[:10]
        if snap_price <= 0 or not snap_date:
            return ""

        closes = yf.Ticker('TLT').history(period='5d')['Close'].dropna()
        if closes.empty:
            return ""
        last_close = float(closes.iloc[-1])
        if last_close <= 0 or pd.isna(last_close):
            return ""
        # v3.12 P1-4：這個收盤價實際屬於哪個交易日（盤前執行時是前一交易日，
        # 標「今日收盤」會誤導）——標籤改「最近收盤」+ 實際日期
        last_close_date = str(closes.index[-1].date())

        # PATCH 2026-08-04 §7.1：最近收盤與週快照同一交易日 → 不做比較
        # （同日兩次抓取的 0.1% 差是來源/時點雜訊，第 0 天的比對沒有資訊）
        if last_close_date == snap_date:
            return ""

        delta_pct = (last_close / snap_price - 1) * 100
        line = (f"**最近收盤**: ${last_close:.2f}（{last_close_date}）"
                f"｜較週快照 {snap_date} {delta_pct:+.1f}%｜日更現況條，僅檢查週快照是否過期\n")
        if abs(delta_pct) > 3.0:
            line += (f"\n⚠️ **標的自快照日已變動 {delta_pct:+.1f}%，"
                     f"上方週更 regime 讀數可能已過期**——請改看即時外部資料（10Y/油價/VIX）。\n")
        return "\n" + line + "\n"
    except Exception:
        return ""


def save_signal_snapshot(df):
    """把今天 TL;DR 高分信號存成 append-only 月檔，供 shadow_tracer 事後回填。

    設計原則（從雨縫 SHADOWLOG_SPEC 搬來）：
    - append-only：寫了就不改，事後不能竄改當初的預測（避免自欺）
    - 每月一檔：data/iv_log/signals_YYYY-MM.json
    - 和錢隔離：只記信號的市場快照，不記持有/損益
    """
    iv_log_dir = os.path.join(DATA_DIR, "iv_log")
    os.makedirs(iv_log_dir, exist_ok=True)

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    month_str = today.strftime("%Y-%m")
    snapshot_path = os.path.join(iv_log_dir, f"signals_{month_str}.json")

    # 只記 TL;DR 等級的高分信號（Score >= 8 且非末日賭博）
    # 這些才是「scanner 在喊買」的信號，值得事後驗證準不準
    hi = df[(df['Score'] >= 8) & (df['Action'] != 'GAMBLE')].copy()

    # news_at_signal 貼標用：掃描當天這檔是否已在公開新聞催化名單上
    # （catalyst_fetch 每天 20:30 UTC 先跑，scanner 22:00 跑，名單必然是當天的）
    catalyst_set = set(load_catalyst_today())

    new_records = []
    for _, r in hi.iterrows():
        # signal_id：日期+標的+到期+履約，唯一識別一個信號，T+N 回填時用
        expiry_str = r['Expiry'].strftime('%Y-%m-%d') if hasattr(r['Expiry'], 'strftime') else str(r['Expiry'])
        sig_id = f"{today_str}_{r['Stock']}_{expiry_str}_{r['Strike']}"
        new_records.append({
            "signal_id": sig_id,
            "snapshot_date": today_str,
            "ticker": r['Stock'],
            "expiry": expiry_str,
            "strike": float(r['Strike']),
            "score": int(r['Score']),
            "tags": r.get('Tags', ''),
            "entry_price": float(r['Ask']),       # 信號當下的 option 價格
            "entry_iv": float(r.get('IV', 0)),    # 信號當下的 IV
            "entry_spot": float(r.get('Spot', 0)),# 信號當下的現價
            "oi": int(r['OpenInterest']),
            "oi_d7": int(r['OI_d7']) if 'OI_d7' in r and pd.notna(r['OI_d7']) else 0,
            # volume：信號當日成交量（供未來「量大倉退」刷量 cohort 分析，Vol/OI 比）
            "volume": int(r['Volume']),
            # premium_tier：權利金分級貼標（只記錄，不影響掃描邏輯）
            # lottery(<$1.5)=散戶樂透/知情者低成本埋伏；heavy(>$3)=機構級真金白銀方向單
            # 用途：shadow log 事後驗證兩類命中率是否有顯著差異，數據說話後才考慮動報表
            "premium_tier": ("lottery" if float(r['Ask']) < 1.5
                             else ("mid" if float(r['Ask']) < 3.0 else "heavy")),
            # news_at_signal：掃描當天標的是否在公開新聞催化名單（只記錄，不影響掃描邏輯）
            # True=新聞點火型（新聞已公開、flow 確認有人押注）；False=純flow型（沉默佈局）
            # 用途：驗證「新聞×flow 交集 vs 無新聞 flow」兩類命中率差異（2026-06-26 批的觀察）
            "news_at_signal": r['Stock'] in catalyst_set,
            # v3.10 P3-3 歸因欄（人工回填，shadow_tracer 只顯示不計算）：
            # signal_day_underlying_move = 信號日標的漲跌 %（驗「逆勢佈局 flow 優於追漲 flow」
            #   假說用——WMT/CMG 兩贏家信號都在下跌日，3 個樣本，30+ 前不得據此改規則）
            # why_it_popped = 跳空脈衝 / 慢磨 / 災後反彈續命 / 不明
            "signal_day_underlying_move": None,
            "why_it_popped": None,
            # T+N 結果欄位，先留空，由 shadow_tracer 事後回填
            "t5": None, "t10": None, "t20": None,
            "verdict": None,  # 事後判定：噴了/沒噴/歸零
        })

    # 讀現有月檔（append-only：不覆蓋，只新增今天的）
    existing = []
    if os.path.exists(snapshot_path):
        try:
            with open(snapshot_path, encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []

    # 防重複：同一個 signal_id 今天已寫過就不重複（手動重跑時的保護）
    existing_ids = {e['signal_id'] for e in existing}
    appended = [r for r in new_records if r['signal_id'] not in existing_ids]
    existing.extend(appended)

    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"  📸 信號快照：今日 {len(appended)} 筆新信號 → {snapshot_path}")


# ==========================================
# 6. 主執行程序
# ==========================================
def us_market_traded_today():
    """檢查美股今天（美東日期）是否有交易。

    方法：SPY 最後一根日 K 的日期 vs 今天美東日期比對。
    - 掃描跑在 UTC 22:00 = 美東 17-18:00，UTC-4/-5 換算到同一天，取 -5 保守即可
    - 抓不到資料時 fail-open（回 True），避免 yfinance 偶發故障誤殺每日掃描
    - 此防護與 cron 修正是雙保險：cron 擋週日、這裡擋假日（如 7/3 落平日）
    """
    try:
        from datetime import timezone
        spy = yf.Ticker("SPY").history(period="5d")
        if spy.empty:
            return True  # fail-open
        last_trade = spy.index[-1].date()
        today_et = (datetime.now(timezone.utc) - timedelta(hours=5)).date()
        return last_trade == today_et
    except Exception:
        return True  # fail-open


def main():
    print(f"🔥 啟動 Scanner 3.12 (yfinance Engine): {datetime.now().strftime('%Y-%m-%d')}")
    if not us_market_traded_today():
        print("🛑 美股今日休市（週末/假日），市場資料為舊收盤殘留。")
        print("   跳過本次掃描與信號快照，避免污染 shadow log。")
        return
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

    # === v3.12 P0-4 方案 A：TLT 雷達併入主掃描時段 ===
    # 根因：獨立排程跑在 04:58 UTC（美股收盤後 9 小時），yfinance 該時段選擇權鏈
    # 常回空——同一天主掃描在 23:0X UTC 抓上百檔鏈全部成功。與其修時段不如併時段。
    # tlt_radar 內建「本週已有有效讀數即跳過」，這裡呼叫成本一週只實跑一次；
    # regime 維持週更（設計決策），只是換到可靠的執行時段。失敗不擋主掃描。
    try:
        import tlt_radar
        tlt_radar.main()
    except Exception as e:
        print(f"⚠️ TLT 雷達執行失敗（不影響主掃描）：{e}")

    auto_watch = load_auto_watch()
    catalyst = load_catalyst_today()
    small_caps_mom = load_small_caps_momentum()
    fallen_saas = load_fallen_saas()
    unknown_tickers, _ = load_unknown_radar()

    # 動態小盤判定：把 catalyst / auto_watch / small_caps_momentum / fallen_saas / unknown
    # 進來的標的中所有「不在 BIG_CAPS」的都當小盤處理
    global _DYNAMIC_SMALL_CAPS
    big_caps_set = set(TICKER_CATEGORIES['BIG_CAPS'])
    _DYNAMIC_SMALL_CAPS = set(small_caps_mom)
    _DYNAMIC_SMALL_CAPS |= {t for t in fallen_saas if t not in big_caps_set}
    _DYNAMIC_SMALL_CAPS |= {t for t in catalyst if t not in big_caps_set}
    _DYNAMIC_SMALL_CAPS |= {t for t in auto_watch if t not in big_caps_set}
    _DYNAMIC_SMALL_CAPS |= {t for t in unknown_tickers if t not in big_caps_set}

    seen = set()
    target_tickers = []
    for t in (TICKER_CATEGORIES['BIG_CAPS']
              + TICKER_CATEGORIES['SMALL_CAPS']
              + auto_watch
              + catalyst
              + small_caps_mom
              + fallen_saas
              + unknown_tickers):
        if t not in seen:
            seen.add(t)
            target_tickers.append(t)

    print(f"🎯 核心池: {len(TICKER_CATEGORIES['BIG_CAPS']) + len(TICKER_CATEGORIES['SMALL_CAPS'])} 檔")
    print(f"🔭 自動候選: {len(auto_watch)} 檔")
    print(f"📰 催化劑: {len(catalyst)} 檔")
    print(f"🎰 小盤動能: {len(small_caps_mom)} 檔")
    print(f"💀 殞落重生: {len(fallen_saas)} 檔")
    print(f"🛸 字典外盲點: {len(unknown_tickers)} 檔")
    print(f"📐 動態判定為小盤: {len(_DYNAMIC_SMALL_CAPS)} 檔")
    print(f"🎯 掃描總數（去重後）: {len(target_tickers)} 檔")

    prev_df = fetch_yesterday_data_from_github()
    results = []
    target_dates = get_target_dates()

    for symbol in target_tickers:
        print(f"🔍 {symbol}...", end=" ", flush=True)

        try:
            tk = yf.Ticker(symbol)
            available_dates = tk.options
        except Exception:
            print("❌ (無法取得期權鏈)")
            continue

        if not available_dates:
            print("💨 (無期權)")
            continue

        # 抓現價（spot）給「極價外尾段」過濾用。抓不到設 0，過濾自動跳過不誤殺。
        spot_price = 0.0
        try:
            fast = tk.fast_info
            spot_price = float(fast.get('lastPrice', 0) or fast.get('last_price', 0) or 0)
        except Exception:
            spot_price = 0.0
        if not spot_price:
            try:
                hist = tk.history(period="1d")
                if not hist.empty:
                    spot_price = float(hist['Close'].iloc[-1])
            except Exception:
                spot_price = 0.0

        valid_target_dates = [d for d in target_dates if d in available_dates]
        found_any = False

        for d_str in valid_target_dates:
            try:
                chain = tk.option_chain(d_str)
                df = chain.calls

                rename_map = {
                    'strike': 'Strike',
                    'lastPrice': 'Ask',
                    'openInterest': 'OpenInterest',
                    'volume': 'Volume',
                    'impliedVolatility': 'IV'
                }

                df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

                for col in ['Ask', 'OpenInterest', 'Volume', 'Strike']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                if 'IV' in df.columns:
                    df['IV'] = pd.to_numeric(df['IV'], errors='coerce').fillna(0.0) * 100
                else:
                    df['IV'] = 0.0

                for _, row in df[df['OpenInterest'] > 500].iterrows():
                    # v3.10 P1-2：IV 硬過濾——0%/異常低值曾連續多日進 TL;DR（F 4.82C 拿 8 分），
                    # 末日區 4-7% 是到期日 IV 計算崩潰。垃圾資料不計分、不顯示。
                    if row['IV'] <= RULE_CONFIG['IV_HARD_MIN'] or row['IV'] > RULE_CONFIG['IV_HARD_MAX']:
                        continue
                    # v3.11 P1-2 補強：1-5% 的低 IV 只有「價外」才可能是壞值
                    # （7/31 NVDA 202.5C 8.6%/AAPL 310C 8.4% 等到期日壞值穿過 1% 門檻；
                    #   價內合約 IV 合法偏低、spot 抓不到時不誤殺）
                    if (row['IV'] <= RULE_CONFIG['IV_SOFT_MIN']
                            and spot_price > 0 and row['Strike'] > spot_price):
                        continue
                    dte = (datetime.strptime(d_str, "%Y-%m-%d") - datetime.now()).days
                    d_row = {
                        'Stock': symbol, 'Expiry': d_str, 'Strike': row['Strike'], 'Ask': row['Ask'],
                        'OpenInterest': int(row['OpenInterest']), 'Volume': int(row['Volume']),
                        'IV': row['IV'], 'DTE': dte, 'Spot': spot_price
                    }
                    tags, action, score = apply_rules(d_row, prev_df)
                    if score > 0 or action != "HOLD":
                        d_row.update({'Tags': tags, 'Action': action, 'Score': score})
                        results.append(d_row)
                        found_any = True

                time.sleep(random.uniform(0.3, 0.8))

            except Exception:
                pass

        print("✅" if found_any else "💨")

    if results:
        final_df = pd.DataFrame(results).sort_values(by=['Score', 'Volume'], ascending=[False, False])
        today_str = datetime.now().strftime("%Y-%m-%d")

        final_df.to_csv(f"{DATA_DIR}/{today_str}.csv", index=False)
        final_df.to_csv(f"{DATA_DIR}/latest.csv", index=False)
        print(f"\n💾 數據已存檔 (共 {len(final_df)} 筆訊號)。")

        generate_report(final_df)
    else:
        print("\n💀 今日全軍覆沒，沒戲。")


if __name__ == "__main__":
    main()
