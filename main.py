import requests
import pandas as pd
import os
import io
import time
import random
from datetime import datetime, timedelta

# ==========================================
# 1. 設定與目標 (Configuration)
# ==========================================
DATA_DIR = "data"
GITHUB_USER = "clarencechien" 
REPO_NAME = "optscnr"      
BRANCH = "main"

TICKER_CATEGORIES = {
    'BIG_CAPS': ['TSLA', 'NVDA', 'AMD', 'MSTR', 'IBIT', 'COIN', 'PLTR', 'SHOP', 'ANET'],
    'SMALL_CAPS': [
        'SMCI', 'OKLO', 'VST', 'RKLB', 'ASTS', 'IONQ', 'UPST', 'SOFI', 'DKNG', 
        'IREN', 'NBIS', 'NEWT', 'COSM', 'ACRV', 'U', 'PATH', 'ROKU', 'HOOD', 
        'TDOC', 'ZM', 'XYZ', 'OPEN', 'CRSP', 'NTLA', 'BEAM', 'PACB', 'TXG', 
        'VCYT', 'HIMS', 'KTOS', 'ONDS', 'LUNR', 'JOBY', 'ACHR', 'SMR', 'NNE', 'VRT', 'CRWV'
    ]
}

TARGET_TICKERS = TICKER_CATEGORIES['BIG_CAPS'] + TICKER_CATEGORIES['SMALL_CAPS']

RULE_CONFIG = {
    'VOL_SPIKE_RATIO': 2.5,  # 點火倍數門檻
    'BIG_CAPS_THRESHOLD':  {'OI': 10000, 'VOL': 2500, 'PRICE': 30.0},
    'SMALL_CAPS_THRESHOLD': {'OI': 1500, 'VOL': 400, 'PRICE': 6.0}
}

# ==========================================
# 2. 資料抓取 (Data Fetching)
# ==========================================
def get_target_dates():
    dates = set()
    today = datetime.now()
    
    # 近兩週週選
    for i in range(2):
        target = today + timedelta(days=(4 - today.weekday() + 7*i) % 7)
        dates.add(target.strftime('%Y-%m-%d'))

    # 未來 6 個月月選
    for i in range(6):
        first_day = (today.replace(day=1) + timedelta(days=32*i)).replace(day=1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)
        third_friday = first_friday + timedelta(days=14)
        if third_friday >= today:
            dates.add(third_friday.strftime('%Y-%m-%d'))

    # LEAPS 獵人 (明後年 1, 6月)
    for year in [today.year + 1, today.year + 2]:
        for month in [1, 6]:
            first_day = datetime(year, month, 1)
            first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)
            dates.add((first_friday + timedelta(days=14)).strftime('%Y-%m-%d'))

    return sorted(list(dates))

def fetch_nasdaq_api(symbol, date_str):
    asset_class = 'etf' if symbol in ['IBIT', 'TLT', 'BITO'] else 'stocks'
    url = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass={asset_class}&fromDate={date_str}&toDate={date_str}&money=all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Origin': 'https://www.nasdaq.com',
        'Referer': 'https://www.nasdaq.com/'
    }
    
    try:
        time.sleep(random.uniform(1.0, 2.5)) 
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json().get('data', {})
            if data and data.get('table'):
                return pd.DataFrame(data['table']['rows']), date_str
    except Exception as e:
        pass
    return None, date_str

def fetch_yesterday_data_from_github():
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{DATA_DIR}/latest.csv"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            print("📅 歷史最新數據載入成功，啟動動能比對。")
            return pd.read_csv(io.StringIO(res.text))
    except:
        pass
    print("⚠️ 無法載入歷史數據，降級為盲測模式。")
    return None

# ==========================================
# 3. 規則引擎 (Rule Engine)
# ==========================================
def apply_rules(row, prev_data=None):
    tags = []
    action = "HOLD"
    score = 0
    
    symbol, price, oi, vol = row['Stock'], row['Ask'], row['OpenInterest'], row['Volume']
    expiry, strike = row['Expiry'], row['Strike']
    iv = row.get('IV', 0.0)
    dte = row.get('DTE', 0)
    
    cfg = RULE_CONFIG['SMALL_CAPS_THRESHOLD'] if symbol in TICKER_CATEGORIES['SMALL_CAPS'] else RULE_CONFIG['BIG_CAPS_THRESHOLD']
    p_limit = cfg['PRICE'] * (2.0 if dte > 180 else 1.0)
    
    # 基本防護：太貴或沒人玩的直接濾掉
    if price > p_limit or oi < (cfg['OI'] * 0.5):
        return "", "HOLD", 0

    # 針對末日的隔離機制 (DTE < 5)
    is_gamble = (dte < 5)
    if is_gamble:
        tags.append("🎲末日結算")
        score -= 2 # 降低末日權重

    # A: 莊家掃貨 (Vol/OI Ratio)
    vol_oi_ratio = vol / oi if oi > 0 else 0
    if vol_oi_ratio > 1.2 and vol > cfg['VOL']:
        tags.append("🚨異常掃貨")
        score += 5
        action = "STRONG_BUY"

    # B: 動能點火
    ignition = False
    if prev_data is not None and not prev_data.empty:
        prev_row = prev_data[(prev_data['Stock'] == symbol) & (prev_data['Expiry'] == expiry) & (prev_data['Strike'] == strike)]
        if not prev_row.empty:
            prev_vol = prev_row.iloc[0]['Volume']
            if prev_vol > 0 and (vol / prev_vol) >= RULE_CONFIG['VOL_SPIKE_RATIO']:
                tags.append(f"🚀點火({vol/prev_vol:.1f}x)")
                score += 3
                ignition = True
    elif vol > cfg['VOL'] and vol > (oi * 0.2):
        tags.append("🚀突發暴量")
        score += 2
        ignition = True

    # C: IV 避險
    if iv > 150:
        tags.append("⚠️IV頂峰")
        score -= 3

    # D: 屬性標籤
    is_leaps = False
    is_smoke = False
    if dte > 300: 
        tags.append("🔭LEAPS"); score += 1; is_leaps = True
    elif price < 1.0: 
        tags.append("🚬菸屁股"); score += 1; is_smoke = True
        
    if oi > 30000: 
        tags.append("🔥萬人塚"); score += 2

    # 綜合判定與分流
    if action != "STRONG_BUY" and ignition and (is_leaps or is_smoke):
        action = "BUY_WATCH"
        score += 2

    # 強制隔離末日合約到 GAMBLE 區
    if is_gamble and action in ["STRONG_BUY", "BUY_WATCH"]:
        action = "GAMBLE"

    return " ".join(tags), action, score

# ==========================================
# 4. 報表生成 (Report Generation)
# ==========================================
def generate_report(df):
    md = "# 🚬 每日妖股獵殺報表 (Scanner 2.2)\n\n"
    md += f"**掃描時間**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
    
    df['Expiry'] = pd.to_datetime(df['Expiry'])
    
    # 建立一個統一的顯示欄位格式函數
    def format_view(sub_df):
        view = sub_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'Volume', 'IV', 'Tags', 'Score']].copy()
        view['Expiry'] = view['Expiry'].dt.strftime('%Y-%m-%d')
        view['IV'] = view['IV'].apply(lambda x: f"{x:.1f}%")
        view.columns = ['代號', '到期日', '履約價', '價格', '持倉(OI)', '成交(Vol)', 'IV', '標籤', '分數']
        return view

    # -----------------------------------
    # 0. TL;DR 總結 (高分狙擊名單)
    # -----------------------------------
    md += "## 🏆 TL;DR 總結 (精選狙擊名單)\n"
    md += "> 策略：過濾掉結算日雜訊，直擊 Score >= 8 的核心異動。\n\n"
    tldr_df = df[(df['Score'] >= 8) & (df['Action'] != 'GAMBLE')].sort_values(by=['Score', 'Volume'], ascending=[False, False]).head(10)
    if not tldr_df.empty:
        md += format_view(tldr_df).to_markdown(index=False) + "\n\n"
    else:
        md += "*今日無高分狙擊標的。*\n\n"

    # -----------------------------------
    # 1. 核心異動區
    # -----------------------------------
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
            
            # LEAPS 區塊 (先顯示)
            if not leaps_df.empty:
                md += "### 🔭 遠期埋伏 (LEAPS > 120天)\n"
                md += "> 策略：時間換空間，跟隨聰明錢長期囤貨 (按分數與持倉排序)。\n\n"
                leaps_df = leaps_df.sort_values(by=['Score', 'OpenInterest'], ascending=[False, False])
                md += format_view(leaps_df).to_markdown(index=False) + "\n\n"

            # 短期波段區塊
            if not short_df.empty:
                md += "### 🚀 短期波段 (Short Term < 120天)\n"
                md += "> 策略：波段點火，關注資金流向 (排除 DTE<5，按分數與成交排序)。\n\n"
                short_df = short_df.sort_values(by=['Score', 'Volume'], ascending=[False, False])
                md += format_view(short_df).to_markdown(index=False) + "\n\n"
                
        elif action == 'GAMBLE':
            md += f"## 🎲 末日賭博專區 (DTE < 5)\n"
            md += "> 警告：極端短線結算，高機率為造市商平倉雜訊，若要玩請當樂透買。\n\n"
            sub_df = sub_df.sort_values(by=['Volume'], ascending=[False]).head(15) # 賭博專區只列前15大成交量
            md += format_view(sub_df).to_markdown(index=False) + "\n\n"
            
        else:
            md += f"## 🚬 常規雷達 (HOLD)\n"
            sub_df = sub_df.sort_values(by=['Score', 'Volume'], ascending=[False, False]).head(20) # 只列前20筆防洗版
            md += format_view(sub_df).to_markdown(index=False) + "\n\n"
            
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("📝 README.md 報表已生成。")

# ==========================================
# 5. 主執行程序 (Main)
# ==========================================
def main():
    print(f"🔥 啟動 Scanner 2.2 (IV Fixed & Gamble Zone): {datetime.now().strftime('%Y-%m-%d')}")
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    prev_df = fetch_yesterday_data_from_github()
    results = []
    target_dates = get_target_dates()
    
    print(f"🎯 掃描標的總數: {len(TARGET_TICKERS)}")
    
    for symbol in TARGET_TICKERS:
        print(f"🔍 {symbol}...", end=" ", flush=True)
        found_any = False
        
        for d_str in target_dates:
            df, _ = fetch_nasdaq_api(symbol, d_str)
            if df is None or 'c_Openinterest' not in df.columns: continue
            
            # 清洗資料
            rename_map = {'strike': 'Strike', 'c_Ask': 'Ask', 'c_Openinterest': 'OpenInterest', 'c_Volume': 'Volume', 'c_IV': 'IV'}
            df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
            
            for col in ['Ask', 'OpenInterest', 'Volume', 'Strike']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace('[$,]', '', regex=True).replace('--', '0'), errors='coerce').fillna(0)
            
            # 正確解析 IV (移除 % 與 , 並轉 float)
            if 'IV' in df.columns:
                df['IV'] = pd.to_numeric(df['IV'].astype(str).str.replace('%', '', regex=False).str.replace(',', '', regex=False).replace('--', '0'), errors='coerce').fillna(0)
            else:
                df['IV'] = 0.0
            
            # 過濾並應用規則
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
