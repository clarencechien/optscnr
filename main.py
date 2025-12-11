import requests
import pandas as pd
import os
import glob
from datetime import datetime, timedelta

# ==========================================
# 1. 設定與目標
# ==========================================
TARGET_TICKERS = ['TSLA', 'NVDA', 'MSTR', 'COIN', 'PLTR', 'GOOG']
DATA_DIR = "data"

RULE_CONFIG = {
    'CHEAP_PRICE': 10.0,
    'HIGH_OI': 5000,
    'IGNITION_VOL': 1000,
    'VOL_SPIKE_RATIO': 2.0,
    'DANGER_DAYS': 45
}

# ==========================================
# 2. 輔助函數
# ==========================================
def get_target_dates(months=[3, 4, 5, 6]):
    dates = []
    today = datetime.now()
    for i in months:
        future_idx = today.month - 1 + i
        year = today.year + future_idx // 12
        month = future_idx % 12 + 1
        
        # 計算第三個星期五
        first_day = datetime(year, month, 1)
        days_to_first_friday = (4 - first_day.weekday() + 7) % 7
        first_friday = first_day + timedelta(days=days_to_first_friday)
        third_friday = first_friday + timedelta(days=14)
        dates.append(third_friday.strftime('%Y-%m-%d'))
    return dates

def get_nasdaq_data(symbol, date_str):
    for _ in range(2): 
        url = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass=stocks&fromDate={date_str}&toDate={date_str}&money=all"
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.nasdaq.com'}
        try:
            res = requests.get(url, headers=headers, timeout=10).json()
            rows = res.get('data', {}).get('table', {}).get('rows', [])
            if rows: return pd.DataFrame(rows), date_str
        except:
            pass
        dt = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)
        date_str = dt.strftime("%Y-%m-%d")
    return None, date_str

# ==========================================
# 3. 規則引擎
# ==========================================
def apply_rules(row, prev_data=None):
    tags = []
    action = "HOLD"
    score = 0
    
    price = row['Ask']
    oi = row['OpenInterest']
    vol = row['Volume']
    strike = row['Strike']
    
    # 規則 1: 菸屁股基礎
    if price < RULE_CONFIG['CHEAP_PRICE'] and oi > RULE_CONFIG['HIGH_OI']:
        tags.append("🚬菸屁股")
        score += 1

    # 規則 2: 主力點火
    if prev_data is not None and not prev_data.empty:
        # 找昨天同一張合約
        prev_row = prev_data[
            (prev_data['Stock'] == row['Stock']) & 
            (prev_data['Expiry'] == row['Expiry']) & 
            (prev_data['Strike'] == strike)
        ]
        
        if not prev_row.empty:
            prev_vol = prev_row.iloc[0]['Volume']
            if prev_vol > 0:
                vol_change_pct = (vol - prev_vol) / prev_vol
            else:
                vol_change_pct = 9.99 if vol > 500 else 0 
                
            if vol > RULE_CONFIG['IGNITION_VOL'] and vol_change_pct > RULE_CONFIG['VOL_SPIKE_RATIO']:
                tags.append(f"🚀點火(+{int(vol_change_pct*100)}%)")
                action = "BUY_WATCH"
                score += 3

    # 規則 3: 萬人塚
    if oi > 20000:
        tags.append("🔥萬人塚")
        score += 1
        
    # 規則 4: 時間警示
    try:
        days_left = (datetime.strptime(row['Expiry'], "%Y-%m-%d") - datetime.now()).days
        if days_left < RULE_CONFIG['DANGER_DAYS']:
            tags.append("⚠️末日近了")
            action = "SELL_ALERT"
    except:
        pass # 日期格式錯誤忽略
    
    if "🚀點火" in str(tags) and "🚬菸屁股" in str(tags):
        action = "STRONG_BUY"
        
    return " ".join(tags), action, score

# ==========================================
# 4. 主程序 (含除錯修正)
# ==========================================
def main():
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    # --- 修正點：更安全的讀取歷史檔案邏輯 ---
    history_files = sorted(glob.glob(f"{DATA_DIR}/*.csv"))
    prev_df = None
    
    if history_files:
        try:
            latest_file = history_files[-1]
            # 檢查檔案大小是否大於 0
            if os.stat(latest_file).st_size > 0:
                print(f"正在讀取歷史資料: {latest_file}")
                prev_df = pd.read_csv(latest_file)
            else:
                print(f"⚠️ 警告: 發現空檔案 {latest_file}，跳過歷史比對。")
        except Exception as e:
            print(f"⚠️ 讀取歷史檔案失敗: {e}，將視為第一次執行。")
            prev_df = None
    # --------------------------------------
    
    today_results = []
    target_dates = get_target_dates()
    
    print("開始掃描...")
    for symbol in TARGET_TICKERS:
        for date_str in target_dates:
            df, real_date = get_nasdaq_data(symbol, date_str)
            if df is None: continue
            
            cols = {'strike': 'Strike', 'c_Ask': 'Ask', 'c_Openinterest': 'OpenInterest', 'c_Volume': 'Volume'}
            if 'c_Openinterest' not in df.columns: continue
            
            calls = df[list(cols.keys())].rename(columns=cols)
            for c in calls.columns:
                if c != 'Strike':
                    calls[c] = pd.to_numeric(calls[c].astype(str).str.replace(',', '').str.replace('--', '0'), errors='coerce').fillna(0)
            calls['Strike'] = pd.to_numeric(calls['Strike'], errors='coerce')
            
            candidates = calls[calls['OpenInterest'] > 1000] 
            
            for _, row in candidates.iterrows():
                data_row = {
                    'Stock': symbol,
                    'Expiry': real_date,
                    'Strike': row['Strike'],
                    'Ask': row['Ask'],
                    'OpenInterest': row['OpenInterest'],
                    'Volume': row['Volume']
                }
                
                tags, action, score = apply_rules(data_row, prev_df)
                
                if score > 0 or action != "HOLD":
                    data_row['Tags'] = tags
                    data_row['Action'] = action
                    data_row['Score'] = score
                    today_results.append(data_row)
    
    if today_results:
        final_df = pd.DataFrame(today_results)
        final_df = final_df.sort_values(by='Score', ascending=False)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        #
