import requests
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import glob

# ==========================================
# 1. 設定與目標
# ==========================================
TARGET_TICKERS = ['TSLA', 'NVDA', 'MSTR', 'COIN', 'PLTR', 'GOOG']
DATA_DIR = "data" # 存放歷史資料的資料夾

# 規則參數
RULE_CONFIG = {
    'CHEAP_PRICE': 10.0,      # 便宜定義
    'HIGH_OI': 5000,          # 高人氣定義
    'IGNITION_VOL': 1000,     # 點火成交量低標
    'VOL_SPIKE_RATIO': 2.0,   # 成交量暴增倍數 (今天 vs 昨天)
    'DANGER_DAYS': 45         # 剩餘天數警示
}

# ==========================================
# 2. 輔助函數 (日期與 API)
# ==========================================
def get_third_friday(year, month):
    first_day = datetime(year, month, 1)
    days_to_first_friday = (4 - first_day.weekday() + 7) % 7
    first_friday = first_day + timedelta(days=days_to_first_friday)
    return (first_friday + timedelta(days=14)).strftime('%Y-%m-%d')

def get_target_dates(months=[3, 4, 5, 6]):
    dates = []
    today = datetime.now()
    for i in months:
        future_idx = today.month - 1 + i
        year = today.year + future_idx // 12
        month = future_idx % 12 + 1
        dates.append(get_third_friday(year, month))
    return dates

def get_nasdaq_data(symbol, date_str):
    # 包含假日重試邏輯
    for _ in range(2): # 試兩次 (今天 & 昨天)
        url = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass=stocks&fromDate={date_str}&toDate={date_str}&money=all"
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.nasdaq.com'}
        try:
            res = requests.get(url, headers=headers, timeout=10).json()
            rows = res.get('data', {}).get('table', {}).get('rows', [])
            if rows: return pd.DataFrame(rows), date_str
        except:
            pass
        # 如果失敗，日期減一天重試 (處理假日)
        dt = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)
        date_str = dt.strftime("%Y-%m-%d")
    return None, date_str

# ==========================================
# 3. 規則引擎 (Rule Engine) - 這是大腦
# ==========================================
def apply_rules(row, prev_data=None):
    tags = []
    action = "HOLD" # 預設觀望
    score = 0
    
    # 基礎數據
    price = row['Ask']
    oi = row['OpenInterest']
    vol = row['Volume']
    strike = row['Strike']
    
    # --- 規則 1: 菸屁股基礎 (The Foundation) ---
    if price < RULE_CONFIG['CHEAP_PRICE'] and oi > RULE_CONFIG['HIGH_OI']:
        tags.append("🚬菸屁股")
        score += 1

    # --- 規則 2: 主力點火 (Volume Spike) ---
    # 這是你要的「變化量」分析
    vol_change_pct = 0
    if prev_data is not None:
        # 找昨天同一張合約
        prev_row = prev_data[
            (prev_data['Stock'] == row['Stock']) & 
            (prev_data['Expiry'] == row['Expiry']) & 
            (prev_data['Strike'] == strike)
        ]
        
        if not prev_row.empty:
            prev_vol = prev_row.iloc[0]['Volume']
            # 防止除以零
            if prev_vol > 0:
                vol_change_pct = (vol - prev_vol) / prev_vol
            else:
                vol_change_pct = 9.99 if vol > 500 else 0 # 從 0 變有量
                
            if vol > RULE_CONFIG['IGNITION_VOL'] and vol_change_pct > RULE_CONFIG['VOL_SPIKE_RATIO']:
                tags.append(f"🚀點火(+{int(vol_change_pct*100)}%)")
                action = "BUY_WATCH" # 列入觀察
                score += 3

    # --- 規則 3: 萬人擁戴 (Crowded Trade) ---
    if oi > 20000:
        tags.append("🔥萬人塚")
        score += 1
        
    # --- 規則 4: 時間警示 (Time Decay) ---
    # 這裡假設 Expiry 格式為 YYYY-MM-DD
    days_left = (datetime.strptime(row['Expiry'], "%Y-%m-%d") - datetime.now()).days
    if days_left < RULE_CONFIG['DANGER_DAYS']:
        tags.append("⚠️末日近了")
        action = "SELL_ALERT" # 建議出場
    
    # 綜合判斷
    if "🚀點火" in str(tags) and "🚬菸屁股" in str(tags):
        action = "STRONG_BUY"
        
    return " ".join(tags), action, score

# ==========================================
# 4. 主程序
# ==========================================
def main():
    # 建立資料夾
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    # 讀取昨天的資料 (用於比對)
    history_files = sorted(glob.glob(f"{DATA_DIR}/*.csv"))
    prev_df = pd.read_csv(history_files[-1]) if history_files else None
    
    today_results = []
    target_dates = get_target_dates()
    
    print("開始掃描...")
    for symbol in TARGET_TICKERS:
        for date_str in target_dates:
            df, real_date = get_nasdaq_data(symbol, date_str)
            if df is None: continue
            
            # 清洗
            cols = {'strike': 'Strike', 'c_Ask': 'Ask', 'c_Openinterest': 'OpenInterest', 'c_Volume': 'Volume'}
            if 'c_Openinterest' not in df.columns: continue
            
            calls = df[list(cols.keys())].rename(columns=cols)
            for c in calls.columns:
                if c != 'Strike':
                    calls[c] = pd.to_numeric(calls[c].astype(str).str.replace(',', '').str.replace('--', '0'), errors='coerce').fillna(0)
            calls['Strike'] = pd.to_numeric(calls['Strike'], errors='coerce')
            
            # 初步篩選 (只留有人氣的)
            candidates = calls[calls['OpenInterest'] > 1000] 
            
            for _, row in candidates.iterrows():
                # 組裝資料列
                data_row = {
                    'Stock': symbol,
                    'Expiry': real_date,
                    'Strike': row['Strike'],
                    'Ask': row['Ask'],
                    'OpenInterest': row['OpenInterest'],
                    'Volume': row['Volume']
                }
                
                # === 呼叫規則引擎 ===
                tags, action, score = apply_rules(data_row, prev_df)
                
                # 只有當有特殊標記或分數高時才紀錄
                if score > 0 or action != "HOLD":
                    data_row['Tags'] = tags
                    data_row['Action'] = action
                    data_row['Score'] = score
                    today_results.append(data_row)
    
    # 儲存今天的結果
    if today_results:
        final_df = pd.DataFrame(today_results)
        final_df = final_df.sort_values(by='Score', ascending=False)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        final_df.to_csv(f"{DATA_DIR}/{today_str}.csv", index=False)
        
        # 產生 Markdown 報表
        generate_report(final_df)
        print(f"掃描完成，發現 {len(final_df)} 個機會。")
    else:
        print("今日無發現。")

def generate_report(df):
    md = "# 🚬 每日菸屁股獵殺報表 \n\n"
    md += f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # 分類顯示
    for action in ['STRONG_BUY', 'BUY_WATCH', 'HOLD', 'SELL_ALERT']:
        sub_df = df[df['Action'] == action]
        if not sub_df.empty:
            icon = "🚀" if "BUY" in action else "👀"
            md += f"## {icon} {action} ({len(sub_df)})\n"
            # 選取重要欄位並轉成 Markdown 表格
            view = sub_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'Volume', 'Tags']]
            md += view.to_markdown(index=False) + "\n\n"
            
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    main()
