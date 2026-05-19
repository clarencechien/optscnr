"""
Scanner 3.6 — 整合 TLT 避險雷達報告
【v3.6 改動】
- 報表最下方自動插入 TLT 避險雷達 markdown（如果存在）
- TLT 不進主掃描，但結果會出現在 README 末端

【v3.5 改動】
- 新增 fallen_saas 動態清單（抓 FIG 級殞落軟體股重生）
- 報表新增「💀 本週重生候選」摘要區
- source_tag 新增 💀重生 標籤

【v3.4 改動】
- 動態小盤判定：catalyst / auto_watch / small_caps_momentum 進來的標的，
  若不在 BIG_CAPS 裡，自動套用 SMALL_CAPS 閾值
"""
import pandas as pd
import yfinance as yf
import requests
import os
import io
import time
import random
import json
from datetime import datetime, timedelta

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
    'SMALL_CAPS_THRESHOLD': {'OI': 1500, 'VOL': 400, 'PRICE': 6.0}
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

    cfg = RULE_CONFIG['SMALL_CAPS_THRESHOLD'] if is_small_cap(symbol) else RULE_CONFIG['BIG_CAPS_THRESHOLD']
    p_limit = cfg['PRICE'] * (2.0 if dte > 180 else 1.0)

    if price > p_limit or oi < (cfg['OI'] * 0.5):
        return "", "HOLD", 0

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
                tags.append(f"🚀點火({vol/prev_vol:.1f}x)")
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

    auto_watch = set(load_auto_watch())
    catalyst = set(load_catalyst_today())
    small_caps_mom = set(load_small_caps_momentum())
    fallen_saas = set(load_fallen_saas())

    def source_tag(symbol):
        if symbol in catalyst: return "📰催化劑"
        elif symbol in fallen_saas: return "💀重生"
        elif symbol in small_caps_mom: return "🎰動能"
        elif symbol in auto_watch: return "🔭候選"
        return ""

    md = "# 🚬 每日妖股獵殺報表 (Scanner 3.6 / yf Engine)\n\n"
    md += f"**掃描時間**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"

    if catalyst:
        md += f"**📰 今日催化劑股**: {', '.join(sorted(catalyst))}\n\n"
    if fallen_saas:
        md += f"**💀 本週重生候選**: {', '.join(sorted(fallen_saas))}\n\n"
    if small_caps_mom:
        md += f"**🎰 本週動能小盤股**: {', '.join(sorted(small_caps_mom))}\n\n"
    if auto_watch:
        md += f"**🔭 本週候選池**: {', '.join(sorted(auto_watch))}\n\n"

    df['Expiry'] = pd.to_datetime(df['Expiry'])

    def format_view(sub_df):
        view = sub_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'OI_d7', 'Volume', 'IV', 'Tags', 'Score']].copy()
        view['Expiry'] = view['Expiry'].dt.strftime('%Y-%m-%d')
        view['IV'] = view['IV'].apply(lambda x: f"{x:.1f}%")
        view['OI_d7'] = view['OI_d7'].apply(format_oi_delta)
        view['Tags'] = view.apply(
            lambda r: f"{source_tag(r['Stock'])} {r['Tags']}".strip(),
            axis=1
        )
        view.columns = ['代號', '到期日', '履約價', '價格', '持倉(OI)', 'Δ7d', '成交(Vol)', 'IV', '標籤', '分數']
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
            md += "> 警告：極端短線結算，高機率為造市商平倉雜訊，若要玩請當樂透買。\n\n"
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
    tlt_report_path = os.path.join(DATA_DIR, "tlt_radar_report.md")
    if os.path.exists(tlt_report_path):
        try:
            with open(tlt_report_path, encoding='utf-8') as f:
                tlt_md = f.read()
            md += tlt_md
            print("  ✅ TLT 避險雷達已附加")
        except Exception as e:
            print(f"  ⚠️ TLT 報告載入失敗：{e}")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("📝 README.md 報表已生成。")


# ==========================================
# 6. 主執行程序
# ==========================================
def main():
    print(f"🔥 啟動 Scanner 3.6 (yfinance Engine): {datetime.now().strftime('%Y-%m-%d')}")
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

    auto_watch = load_auto_watch()
    catalyst = load_catalyst_today()
    small_caps_mom = load_small_caps_momentum()
    fallen_saas = load_fallen_saas()

    # 動態小盤判定：把 catalyst / auto_watch / small_caps_momentum / fallen_saas
    # 進來的標的中所有「不在 BIG_CAPS」的都當小盤處理
    global _DYNAMIC_SMALL_CAPS
    big_caps_set = set(TICKER_CATEGORIES['BIG_CAPS'])
    _DYNAMIC_SMALL_CAPS = set(small_caps_mom)  # 動能掃出來的全是小盤
    _DYNAMIC_SMALL_CAPS |= {t for t in fallen_saas if t not in big_caps_set}
    _DYNAMIC_SMALL_CAPS |= {t for t in catalyst if t not in big_caps_set}
    _DYNAMIC_SMALL_CAPS |= {t for t in auto_watch if t not in big_caps_set}

    seen = set()
    target_tickers = []
    for t in (TICKER_CATEGORIES['BIG_CAPS']
              + TICKER_CATEGORIES['SMALL_CAPS']
              + auto_watch
              + catalyst
              + small_caps_mom
              + fallen_saas):
        if t not in seen:
            seen.add(t)
            target_tickers.append(t)

    print(f"🎯 核心池: {len(TICKER_CATEGORIES['BIG_CAPS']) + len(TICKER_CATEGORIES['SMALL_CAPS'])} 檔")
    print(f"🔭 自動候選: {len(auto_watch)} 檔")
    print(f"📰 催化劑: {len(catalyst)} 檔")
    print(f"🎰 小盤動能: {len(small_caps_mom)} 檔")
    print(f"💀 殞落重生: {len(fallen_saas)} 檔")
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
                    dte = (datetime.strptime(d_str, "%Y-%m-%d") - datetime.now()).days
                    d_row = {
                        'Stock': symbol, 'Expiry': d_str, 'Strike': row['Strike'], 'Ask': row['Ask'],
                        'OpenInterest': int(row['OpenInterest']), 'Volume': int(row['Volume']),
                        'IV': row['IV'], 'DTE': dte
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
