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
# 擴充了清單，加入未來可能想看的妖股
TARGET_TICKERS = [
    'GOOG',  # Google
    'TSLA',  # 載具與機器人 (Meme King)
    'NVDA',  # 算力軍火商
    'AMD',   # 算力老二
    'SMCI',  # 伺服器 (高風險妖股)
    'PLTR',  # AI 軟體與國防
    'MSTR',  # 比特幣槓桿 (Crypto Proxy)
    'COIN',  # 加密貨幣交易所
    'OKLO',  # 核能 (Sam Altman 概念)
    'VST',   # AI 電力龍頭 (新增) ⚡
    'RKLB',  # 太空運輸 (新增) 🚀
    'ASTS',  # 衛星通訊 (新增) 🛰️ (波動極大!)
    'IONQ'   # 量子電腦 (新增) ⚛️
]
DATA_DIR = "data"

# GitHub Repo 設定 (用來抓昨天的資料)
# ⚠️ 請將這裡換成你的 GitHub 帳號與 Repo 名稱
GITHUB_USER = "clarencechien" 
REPO_NAME = "optscnr"     
BRANCH = "main"

RULE_CONFIG = {
    'CHEAP_PRICE': 15.0,    # 稍微放寬價格，避免漏掉好貨
    'HIGH_OI': 10000,       # 基礎門檻
    'SUPER_OI': 50000,      # 超級萬人塚門檻
    'IGNITION_VOL': 1000,   # 點火成交量
    'VOL_SPIKE_RATIO': 2.0, # 量能爆發倍數 (今日/昨日)
    'DANGER_DAYS': 45       # 末日警示天數
}

# ==========================================
# 2. 輔助函數
# ==========================================
def get_target_dates(months=[2, 3, 4, 5, 6]):
    # 增加近月合約掃描 (2月, 3月...) 
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

def fetch_yesterday_data_from_github():
    """
    從 GitHub Raw Content 下載昨天的 CSV，解決 Actions 環境失憶問題
    """
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{DATA_DIR}/{yesterday}.csv"
    
    print(f"☁️ 嘗試從 GitHub 下載昨天 ({yesterday}) 的紀錄...", end=" ")
    try:
        res = requests.get(url)
        if res.status_code == 200:
            from io import StringIO
            df = pd.read_csv(StringIO(res.text))
            print(f"✅ 成功! 取得 {len(df)} 筆歷史資料")
            return df
        else:
            print(f"❌ 找不到 (HTTP {res.status_code}) - 可能是昨天沒跑或檔案不存在")
            return None
    except Exception as e:
        print(f"💥 下載失敗: {e}")
        return None

def get_nasdaq_data(symbol, date_str):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    ]
    
    for attempt in range(2): 
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
            print(f"    ☁️ [嘗試 {attempt+1}] 連線至 {symbol} {date_str} ...", end=" ")
            res = session.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                json_data = res.json()
                if json_data.get('status', {}).get('rCode') == 200:
                    rows = json_data.get('data', {}).get('table', {}).get('rows', [])
                    if rows:
                        print(f"✅ 成功! 取得 {len(rows)} 筆資料")
                        return pd.DataFrame(rows), date_str
                    else:
                        print("⚠️ 內容為空 (No Rows)")
                else:
                    print(f"❌ API 錯誤: {json_data.get('status')}")
            else:
                print(f"⛔ HTTP {res.status_code}")
                
        except Exception as e:
            print(f"💥 例外: {str(e)}")
        
        # 失敗處理：嘗試減一天
        dt = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)
        date_str = dt.strftime("%Y-%m-%d")
        time.sleep(random.uniform(1, 3)) 
        
    return None, date_str

# ==========================================
# 3. 規則引擎 (核心邏輯)
# ==========================================
def apply_rules(row, prev_data=None):
    tags = []
    action = "HOLD"
    score = 0
    
    price = row['Ask']
    oi = row['OpenInterest']
    vol = row['Volume']
    strike = row['Strike']
    symbol = row['Stock']
    expiry = row['Expiry']
    
    # --- 規則 1: 菸屁股 (便宜 + 有人氣) ---
    if price < RULE_CONFIG['CHEAP_PRICE'] and oi > RULE_CONFIG['HIGH_OI']:
        tags.append("🚬菸屁股")
        score += 1

    # --- 規則 2: 點火偵測 (成交量爆發) ---
    ignition_detected = False
    vol_msg = ""
    
    if prev_data is not None and not prev_data.empty:
        # 在昨天的資料裡找同一支合約
        prev_row = prev_data[
            (prev_data['Stock'] == symbol) & 
            (prev_data['Expiry'] == expiry) & 
            (prev_data['Strike'] == strike)
        ]
        
        if not prev_row.empty:
            prev_vol = prev_row.iloc[0]['Volume']
            # 計算爆發倍數
            if prev_vol > 0:
                vol_ratio = vol / prev_vol
            else:
                vol_ratio = 9.99 if vol > 500 else 0 
                
            if vol > RULE_CONFIG['IGNITION_VOL'] and vol_ratio >= RULE_CONFIG['VOL_SPIKE_RATIO']:
                ignition_detected = True
                vol_msg = f"🚀點火({vol_ratio:.1f}x)"
    else:
        # 如果真的完全沒有歷史資料，但量超大，也給過 (盲測)
        if vol > 5000 and vol > oi * 0.1: 
            ignition_detected = True
            vol_msg = "🚀點火(暴量)"

    if ignition_detected:
        tags.append(vol_msg)
        score += 3 # 點火權重最高
        action = "BUY_WATCH" # 至少要觀察

    # --- 規則 3: 萬人塚 (群眾共識) ---
    if oi > RULE_CONFIG['SUPER_OI']: # 50000
        tags.append("👑超級萬人塚") 
        score += 2
    elif oi > 20000: # 20000
        tags.append("🔥萬人塚")
        score += 1
        
    # --- 總結判定 ---
    # 如果同時是「菸屁股」且「點火」，直接升級 Strong Buy
    if "🚬菸屁股" in str(tags) and ignition_detected:
        action = "STRONG_BUY"
        score += 1 # 再加分
        
    return " ".join(tags), action, score

# ==========================================
# 4. 主程序
# ==========================================
def main():
    print("🚀 啟動菸屁股掃描器 (Auto-Fetch History Mode)...", flush=True)
    
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    # 1. 嘗試載入歷史資料 (優先從 GitHub 下載)
    prev_df = fetch_yesterday_data_from_github()
    
    # 如果下載失敗，才試著讀本地 (雖然在 Actions 裡通常沒用)
    if prev_df is None:
        history_files = sorted(glob.glob(f"{DATA_DIR}/*.csv"))
        if history_files:
            try:
                print(f"📚 讀取本地紀錄: {history_files[-1]}")
                prev_df = pd.read_csv(history_files[-1])
            except: pass

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
                continue
            
            calls = df[list(cols.keys())].rename(columns=cols)
            for c in calls.columns:
                if c != 'Strike':
                    calls[c] = pd.to_numeric(calls[c].astype(str).str.replace(',', '').str.replace('--', '0'), errors='coerce').fillna(0)
            calls['Strike'] = pd.to_numeric(calls['Strike'], errors='coerce')
            
            # 第一層過濾：至少要有 1000 張 OI (減少運算量)
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
                
                # 只有 "有分" 或 "非 HOLD" 的才存下來，保持版面乾淨
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
        file_path = f"{DATA_DIR}/{today_str}.csv"
        print(f"\n💾 正在存檔: {file_path} (共 {len(final_df)} 筆)")
        
        final_df.to_csv(file_path, index=False)
        generate_report(final_df)
    else:
        print("\n💨 今日無符合條件的機會，無檔案產出。")

def generate_report(df):
    md = "# 🚬 每日菸屁股獵殺報表 (AI Auto-Trade)\n\n"
    md += f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
    
    # 定義顯示順序
    action_order = ['STRONG_BUY', 'BUY_WATCH', 'HOLD', 'SELL_ALERT']
    
    for action in action_order:
        sub_df = df[df['Action'] == action]
        if not sub_df.empty:
            icon = "🚀" if "BUY" in action else ("👀" if "WATCH" in action else "🚬")
            md += f"## {icon} {action} ({len(sub_df)})\n"
            
            # 製作表格，隱藏小數點
            view = sub_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'Volume', 'Tags', 'Score']].copy()
            view['OpenInterest'] = view['OpenInterest'].astype(int)
            view['Volume'] = view['Volume'].astype(int)
            
            md += view.to_markdown(index=False) + "\n\n"
            
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    main()
