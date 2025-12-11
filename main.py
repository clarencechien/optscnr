import requests
import pandas as pd
import os
import glob
from datetime import datetime, timedelta
import time
import random

# ==========================================
# 1. 設定與目標
# ==========================================
TARGET_TICKERS = ['TSLA', 'NVDA', 'MSTR', 'COIN', 'PLTR', 'GOOG']
DATA_DIR = "data"

RULE_CONFIG = {
    'CHEAP_PRICE': 10.0,
    'HIGH_OI': 10000,
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
        
        first_day = datetime(year, month, 1)
        days_to_first_friday = (4 - first_day.weekday() + 7) % 7
        first_friday = first_day + timedelta(days=days_to_first_friday)
        third_friday = first_friday + timedelta(days=14)
        dates.append(third_friday.strftime('%Y-%m-%d'))
    return dates

def get_nasdaq_data(symbol, date_str):
    # 增加隨機 User-Agent 以降低被擋機率
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    ]
    
    for attempt in range(2): 
        # ⚠️ 這裡改用 requests.Session 來模擬真實瀏覽器行為
        session = requests.Session()
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.nasdaq.com/market-activity/stocks/tsla/option-chain',
            'Origin': 'https://www.nasdaq.com',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        url = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass=stocks&fromDate={date_str}&toDate={date_str}&money=all"
        
        try:
            print(f"   ☁️ [嘗試 {attempt+1}] 連線至 {url} ...", end=" ")
            res = session.get(url, headers=headers, timeout=15)
            
            # 🔥 debug 重點：印出狀態碼
            if res.status_code == 200:
                json_data = res.json()
                # 檢查 NASDAQ 回傳的狀態
                if json_data.get('status', {}).get('rCode') == 200:
                    rows = json_data.get('data', {}).get('table', {}).get('rows', [])
                    if rows:
                        print(f"✅ 成功! 取得 {len(rows)} 筆資料")
                        return pd.DataFrame(rows), date_str
                    else:
                        print("⚠️ 成功連線但內容為空 (No Rows)")
                else:
                    print(f"❌ API 內部錯誤: {json_data.get('status')}")
            else:
                print(f"⛔ HTTP 錯誤: {res.status_code} (可能是 IP 被擋)")
                
        except Exception as e:
            print(f"💥 例外錯誤: {str(e)}")
        
        # 失敗後，嘗試減一天 (處理假日)
        dt = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)
        date_str = dt.strftime("%Y-%m-%d")
        time.sleep(2) # 休息一下再試
        
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
    
    if price < RULE_CONFIG['CHEAP_PRICE'] and oi > RULE_CONFIG['HIGH_OI']:
        tags.append("🚬菸屁股")
        score += 1

    if prev_data is not None and not prev_data.empty:
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

# --- 規則 3: 超級萬人塚 (Super Crowded) ---
    # 原本是 > 20000，現在改成 50000
    if oi > 50000:
        tags.append("👑超級萬人塚") # 給它一個皇冠
        score += 2 # 加分加重
    elif oi > 20000:
        tags.append("🔥萬人塚") # 2萬~5萬 是一般熱點
        score += 1
        
    if "🚀點火" in str(tags) and "🚬菸屁股" in str(tags):
        action = "STRONG_BUY"
        
    return " ".join(tags), action, score

# ==========================================
# 4. 主程序
# ==========================================
def main():
    print("🚀 啟動菸屁股掃描器 (Debug Mode)...", flush=True)
    
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    # 讀取歷史
    history_files = sorted(glob.glob(f"{DATA_DIR}/*.csv"))
    prev_df = None
    if history_files:
        try:
            if os.stat(history_files[-1]).st_size > 0:
                print(f"📚 讀取昨天的紀錄: {history_files[-1]}")
                prev_df = pd.read_csv(history_files[-1])
        except:
            pass

    today_results = []
    target_dates = get_target_dates()
    
    print(f"📅 目標日期: {target_dates}")
    
    for symbol in TARGET_TICKERS:
        print(f"\n🔍 正在掃描 {symbol} ...")
        for date_str in target_dates:
            df, real_date = get_nasdaq_data(symbol, date_str)
            if df is None: continue
            
            # 清洗與處理
            cols = {'strike': 'Strike', 'c_Ask': 'Ask', 'c_Openinterest': 'OpenInterest', 'c_Volume': 'Volume'}
            if 'c_Openinterest' not in df.columns: 
                print("   ⚠️ 欄位名稱不符，跳過")
                continue
            
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
    
    # 儲存結果
    if today_results:
        final_df = pd.DataFrame(today_results)
        final_df = final_df.sort_values(by='Score', ascending=False)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        print(f"\n💾 正在存檔: {DATA_DIR}/{today_str}.csv (共 {len(final_df)} 筆)")
        
        final_df.to_csv(f"{DATA_DIR}/{today_str}.csv", index=False)
        generate_report(final_df)
    else:
        print("\n💨 今日無符合條件的機會 (或 API 被擋)，無檔案產出。")

def generate_report(df):
    md = "# 🚬 每日菸屁股獵殺報表 \n\n"
    md += f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    for action in ['STRONG_BUY', 'BUY_WATCH', 'HOLD', 'SELL_ALERT']:
        sub_df = df[df['Action'] == action]
        if not sub_df.empty:
            icon = "🚀" if "BUY" in action else "👀"
            md += f"## {icon} {action} ({len(sub_df)})\n"
            view = sub_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'Volume', 'Tags']]
            md += view.to_markdown(index=False) + "\n\n"
            
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    main()
