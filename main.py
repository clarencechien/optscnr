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
    'VOL_SPIKE_RATIO': 2.5,  # 提高點火門檻，過濾雜訊
    'BIG_CAPS_THRESHOLD':  {'OI': 10000, 'VOL': 2500, 'PRICE': 30.0},
    'SMALL_CAPS_THRESHOLD': {'OI': 1500, 'VOL': 400, 'PRICE': 6.0}
}

# ==========================================
# 2. 核心功能 (Core Functions)
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

    # LEAPS 獵人 (明後兩年的 1月與 6月)
    for year in [today.year + 1, today.year + 2]:
        for month in [1, 6]:
            first_day = datetime(year, month, 1)
            first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)
            dates.add((first_friday + timedelta(days=14)).strftime('%Y-%m-%d'))

    return sorted(list(dates))

def fetch_nasdaq_api(symbol, date_str):
    """修復版 API 抓取：自動判定資產類別並處理頻率限制"""
    asset_class = 'etf' if symbol in ['IBIT', 'TLT', 'BITO'] else 'stocks'
    url = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass={asset_class}&fromDate={date_str}&toDate={date_str}&money=all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://www.nasdaq.com',
        'Referer': 'https://www.nasdaq.com/'
    }
    
    try:
        # 強制隨機休息，防止 IP 被鎖
        time.sleep(random.uniform(1.0, 2.5)) 
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json().get('data', {})
            if data and data.get('table'):
                return pd.DataFrame(data['table']['rows']), date_str
    except Exception as e:
        print(f"ERR: {symbol} @ {date_str} -> {e}")
    return None, date_str

# ==========================================
# 3. 規則引擎 (Rule Engine 2.1)
# ==========================================

def apply_rules(row, prev_data=None):
    tags, score, action = [], 0, "HOLD"
    
    # 提取數值並防呆
    symbol, price, oi, vol = row['Stock'], row['Ask'], row['OpenInterest'], row['Volume']
    expiry, strike = row['Expiry'], row['Strike']
    iv = float(str(row.get('IV', 0)).replace('%', '').replace(',', ''))
    
    dte = (datetime.strptime(expiry, "%Y-%m-%d") - datetime.now()).days
    cfg = RULE_CONFIG['SMALL_CAPS_THRESHOLD'] if symbol in TICKER_CATEGORIES['SMALL_CAPS'] else RULE_CONFIG['BIG_CAPS_THRESHOLD']
    
    # 規則 A: 門檻檢查 (LEAPS 價格放寬)
    p_limit = cfg['PRICE'] * (2.0 if dte > 180 else 1.0)
    if price > p_limit or oi < (cfg['OI'] * 0.5):
        return "", "HOLD", 0

    # 規則 B: 偵測掃貨 (Vol/OI Ratio) - 莊家進場訊號
    vol_oi_ratio = vol / oi if oi > 0 else 0
    if vol_oi_ratio > 1.2 and vol > cfg['VOL']:
        tags.append("🚨異常掃貨")
        score += 5
        action = "STRONG_BUY"

    # 規則 C: 點火偵測 (VS 昨日)
    if prev_data is not None:
        prev_row = prev_data[(prev_data['Stock'] == symbol) & (prev_data['Expiry'] == expiry) & (prev_data['Strike'] == strike)]
        if not prev_row.empty:
            prev_vol = prev_row.iloc[0]['Volume']
            if prev_vol > 0 and (vol / prev_vol) >= RULE_CONFIG['VOL_SPIKE_RATIO']:
                tags.append(f"🚀點火({vol/prev_vol:.1f}x)")
                score += 3
    
    # 規則 D: IV 避險 (防止買在頂峰)
    if iv > 150:
        tags.append("⚠️IV過高(慎入)")
        score -= 2

    # 規則 E: 屬性標籤
    if dte > 300: tags.append("🔭LEAPS埋伏"); score += 1
    elif price < 1.0: tags.append("🚬菸屁股"); score += 1
    if oi > 30000: tags.append("🔥萬人塚"); score += 2

    return " ".join(tags), action, score

# ==========================================
# 4. 主執行程序
# ==========================================

def main():
    print(f"🔥 啟動 Scanner 2.1: {datetime.now().strftime('%Y-%m-%d')}")
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    # 抓取昨日資料 (用於比較點火)
    prev_df = None
    hist_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{DATA_DIR}/latest.csv"
    try:
        res = requests.get(hist_url, timeout=10)
        if res.status_code == 200:
            prev_df = pd.read_csv(io.StringIO(res.text))
            print("📅 歷史數據載入成功")
    except: print("⚠️ 無法載入歷史，將使用盲測模式")

    results = []
    target_dates = get_target_dates()
    
    for symbol in TARGET_TICKERS:
        print(f"🔍 {symbol}...", end=" ", flush=True)
        found_any = False
        for d_str in target_dates:
            df, _ = fetch_nasdaq_api(symbol, d_str)
            if df is None or 'c_Openinterest' not in df.columns: continue
            
            # 清洗資料
            df = df.rename(columns={'strike': 'Strike', 'c_Ask': 'Ask', 'c_Openinterest': 'OpenInterest', 'c_Volume': 'Volume', 'c_IV': 'IV'})
            for col in ['Ask', 'OpenInterest', 'Volume', 'Strike']:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('[$,]', '', regex=True).replace('--', '0'), errors='coerce').fillna(0)
            
            # 過濾並應用規則
            for _, row in df[df['OpenInterest'] > 500].iterrows():
                d_row = {'Stock': symbol, 'Expiry': d_str, 'Strike': row['Strike'], 'Ask': row['Ask'], 'OpenInterest': int(row['OpenInterest']), 'Volume': int(row['Volume']), 'IV': row.get('IV', '0%')}
                tags, action, score = apply_rules(d_row, prev_df)
                if score > 0:
                    d_row.update({'Tags': tags, 'Action': action, 'Score': score})
                    results.append(d_row)
                    found_any = True
        print("✅" if found_any else "💨")

    if results:
        final_df = pd.DataFrame(results).sort_values(by=['Score', 'Volume'], ascending=False)
        today_str = datetime.now().strftime("%Y-%m-%d")
        final_df.to_csv(f"{DATA_DIR}/{today_str}.csv", index=False)
        final_df.to_csv(f"{DATA_DIR}/latest.csv", index=False) # 供明天比對
        print(f"\n🎉 掃描完成，找到 {len(final_df)} 個潛在標的！")
    else:
        print("\n💀 今日全軍覆沒，沒戲。")

if __name__ == "__main__":
    main()
