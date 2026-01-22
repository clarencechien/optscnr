import requests
import pandas as pd
import os
import glob
from datetime import datetime, timedelta
import time
import random
import io

# ==========================================
# 1. 設定與目標 (Configuration)
# ==========================================

# 資料儲存目錄
DATA_DIR = "data"

# GitHub Repo 設定
GITHUB_USER = "clarencechien" 
REPO_NAME = "optscnr"      
BRANCH = "main"

# --- 股票清單分類 (動態管理) ---
TICKER_CATEGORIES = {
    # 🦁 巨獸組: 高市值、流動性好、價格高
    'BIG_CAPS': [
        'TSLA', 'NVDA', 'AMD', 'MSTR', 'IBIT', 'COIN', 'PLTR', 'SHOP', 'ANET'
    ],
    
    # 🦄 妖股/成長股: 波動大、單價低、爆發力強
    'SMALL_CAPS': [
        # 妖股組
        'SMCI', 'OKLO', 'VST', 'RKLB', 'ASTS', 'IONQ', 
        'UPST', 'SOFI', 'DKNG', 'IREN', 'NBIS', 'NEWT', 'COSM', 'ACRV',
        # ARK 菸屁股
        'U', 'PATH', 'ROKU', 'HOOD', 'TDOC', 'ZM', 'XYZ', 'OPEN',
        # 生技彩票
        'CRSP', 'NTLA', 'BEAM', 'PACB', 'TXG', 'VCYT', 'HIMS',
        # 國防與太空
        'KTOS', 'ONDS', 'LUNR', 'JOBY', 'ACHR',
        # 核能與基建
        'SMR', 'NNE', 'VRT', 'CRWV'
    ]
}

# 展平所有代號供迴圈使用
TARGET_TICKERS = TICKER_CATEGORIES['BIG_CAPS'] + TICKER_CATEGORIES['SMALL_CAPS']

# --- 策略參數設定 (動態門檻) ---
RULE_CONFIG = {
    'VOL_SPIKE_RATIO': 2.0, # 量能爆發倍數 (今日量 / 昨日量)
    
    # 🦁 巨獸組參數
    'BIG_CAPS_THRESHOLD':  {
        'OI': 10000,      # 持倉量門檻
        'VOL': 2000,      # 點火成交量門檻
        'PRICE': 25.0     # 放寬價格上限 (LEAPS 通常比較貴)
    },
    
    # 🦄 妖股組參數
    'SMALL_CAPS_THRESHOLD': {
        'OI': 1500,       # 只要有 1500 張囤單就算多
        'VOL': 300,       # 小股票 300 張成交就算點火
        'PRICE': 5.0      # 放寬到 $5.0 (LEAPS 權利金較高)
    }
}

# ==========================================
# 2. 輔助函數 (Helpers)
# ==========================================

def get_target_dates():
    """
    生成目標日期 (V2.0 升級版)：
    1. [Gamma] 本週五、下週五
    2. [Swing] 未來 6 個月的月選 (每月第三個週五)
    3. [LEAPS] 未來 2 年的 1月 與 6月 (長期埋伏)
    """
    dates = set()
    today = datetime.now()
    
    # --- A. 近兩週週選 (Short Term Gamma) ---
    days_ahead = 4 - today.weekday() # 4 is Friday
    if days_ahead < 0: days_ahead += 7
    this_friday = today + timedelta(days=days_ahead)
    next_friday = this_friday + timedelta(days=7)
    
    dates.add(this_friday.strftime('%Y-%m-%d'))
    dates.add(next_friday.strftime('%Y-%m-%d'))

    # --- B. 未來 6 個月月選 (Swing Trade) ---
    for i in range(6):
        # 計算月份 (從下個月開始算比較保險，或是含本月)
        future_month_first = (today.replace(day=1) + timedelta(days=32*i)).replace(day=1)
        
        # 尋找該月第三個週五
        days_to_first_friday = (4 - future_month_first.weekday() + 7) % 7
        first_friday = future_month_first + timedelta(days=days_to_first_friday)
        third_friday = first_friday + timedelta(days=14)
        
        if third_friday >= today:
            dates.add(third_friday.strftime('%Y-%m-%d'))

    # --- C. LEAPS 獵人 (Long Term) ---
    # 鎖定未來兩年的 1 月 (通常流動性最好) 和 6 月
    current_year = today.year
    target_years = [current_year + 1, current_year + 2] # 明年與後年
    target_months = [1, 6] # Jan & Jun
    
    for year in target_years:
        for month in target_months:
            try:
                first_day = datetime(year, month, 1)
                days_to_first_friday = (4 - first_day.weekday() + 7) % 7
                first_friday = first_day + timedelta(days=days_to_first_friday)
                third_friday = first_friday + timedelta(days=14)
                dates.add(third_friday.strftime('%Y-%m-%d'))
            except ValueError:
                continue

    # 排序並轉回列表
    sorted_dates = sorted(list(dates))
    return sorted_dates

def fetch_yesterday_data_from_github():
    """
    從 GitHub 下載昨天的 CSV 以比較成交量變化
    """
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    for lookback in range(1, 4): # 若遇假日往前推
        check_date = (datetime.now() - timedelta(days=lookback)).strftime("%Y-%m-%d")
        url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{DATA_DIR}/{check_date}.csv"
        
        print(f"☁️ 嘗試載入歷史 ({check_date})...", end=" ")
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                df = pd.read_csv(io.StringIO(res.text))
                print(f"✅ 取得 {len(df)} 筆")
                return df
            else:
                print(f"❌ (HTTP {res.status_code})")
        except:
            print("💥 連線失敗")
            
    return None

def get_nasdaq_data(symbol, date_str):
    """
    爬取 Nasdaq Option Chain (支援 Stocks & ETF)
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    ]
    
    asset_classes = ['stocks', 'etf']
    
    for asset_class in asset_classes:
        url = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass={asset_class}&fromDate={date_str}&toDate={date_str}&money=all"
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nasdaq.com/'
        }
        
        try:
            time.sleep(random.uniform(0.3, 1.0)) # 稍微加快速度
            res = requests.get(url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                json_data = res.json()
                status = json_data.get('status', {})
                
                if status.get('rCode') == 200:
                    rows = json_data.get('data', {}).get('table', {}).get('rows', [])
                    if rows:
                        return pd.DataFrame(rows), date_str
                    else:
                        return None, date_str # 該日期無合約 (非交易日或未開倉)
                
                # 錯誤處理
                b_msg = str(status.get('bCodeMessage', ''))
                if "Symbol not exists" in b_msg or "Invalid Asset Class" in b_msg:
                    if asset_class == 'stocks': continue 
            
        except Exception:
            pass
            
    return None, date_str

# ==========================================
# 3. 規則引擎 (Core Logic)
# ==========================================

def apply_rules(row, prev_data=None):
    tags = []
    action = "HOLD"
    score = 0
    
    symbol = row['Stock']
    price = row['Ask']
    oi = row['OpenInterest']
    vol = row['Volume']
    expiry = row['Expiry']
    strike = row['Strike']
    
    # 計算距離到期日天數 (DTE) 用於判斷是末日還是 LEAPS
    try:
        exp_date = datetime.strptime(expiry, "%Y-%m-%d")
        dte = (exp_date - datetime.now()).days
    except:
        dte = 0

    # --- 1. 門檻設定 ---
    if symbol in TICKER_CATEGORIES['SMALL_CAPS']:
        cfg = RULE_CONFIG['SMALL_CAPS_THRESHOLD']
        # LEAPS 容許價格較高
        price_threshold = cfg['PRICE'] * 2.0 if dte > 180 else cfg['PRICE']
        
        # 生技與太空股 OI 門檻打折
        if symbol in ['CRSP', 'NTLA', 'RKLB', 'ASTS']:
            cfg_oi = cfg['OI'] * 0.8
        else:
            cfg_oi = cfg['OI']
    else:
        cfg = RULE_CONFIG['BIG_CAPS_THRESHOLD']
        price_threshold = cfg['PRICE'] * 1.5 if dte > 180 else cfg['PRICE']
        cfg_oi = cfg['OI']

    # --- 規則 2: 菸屁股/LEAPS 埋伏 ---
    if price <= price_threshold and oi > cfg_oi:
        if dte > 300:
            tags.append("🔭LEAPS埋伏") # 遠期合約特有標籤
            score += 2 # LEAPS 加分
        else:
            tags.append("🚬菸屁股")
            score += 1

    # --- 規則 3: 點火偵測 ---
    ignition_detected = False
    vol_msg = ""
    
    # 比較昨日數據
    if prev_data is not None and not prev_data.empty:
        prev_row = prev_data[
            (prev_data['Stock'] == symbol) & 
            (prev_data['Expiry'] == expiry) & 
            (prev_data['Strike'] == strike)
        ]
        
        if not prev_row.empty:
            prev_vol = prev_row.iloc[0]['Volume']
            vol_ratio = vol / prev_vol if prev_vol > 0 else 0
            
            if vol > cfg['VOL']:
                if prev_vol == 0:
                    ignition_detected = True
                    vol_msg = "🚀死灰復燃"
                elif vol_ratio >= RULE_CONFIG['VOL_SPIKE_RATIO']:
                    ignition_detected = True
                    vol_msg = f"🚀點火({vol_ratio:.1f}x)"
        else:
            if vol > cfg['VOL']:
                ignition_detected = True
                vol_msg = "🆕新開倉點火"
    else:
        # 盲測模式
        if vol > cfg['VOL'] and vol > (oi * 0.2):
            ignition_detected = True
            vol_msg = "🚀突發暴量(盲)"

    if ignition_detected:
        tags.append(vol_msg)
        score += 3
        action = "BUY_WATCH"

    # --- 規則 4: 萬人塚 ---
    if oi > 50000:
        tags.append("👑超級萬人塚")
        score += 2
    elif oi > 20000:
        tags.append("🔥萬人塚")
        score += 1
        
    # --- 最終判定 ---
    # 如果是遠期 LEAPS 且有人在囤貨(菸屁股) + 點火 -> 強力買入
    if ("🚬菸屁股" in str(tags) or "🔭LEAPS埋伏" in str(tags)) and ignition_detected:
        action = "STRONG_BUY"
        score += 2 
        
    return " ".join(tags), action, score

# ==========================================
# 4. 主程序
# ==========================================

def main():
    print(f"🚀 啟動 ARK 妖股掃描器 (LEAPS Enhanced) - {datetime.now().strftime('%Y-%m-%d')}", flush=True)
    
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    prev_df = fetch_yesterday_data_from_github()
    
    today_results = []
    target_dates = get_target_dates()
    print(f"📅 掃描合約日期 (含遠期):")
    print(f"   {target_dates}")
    
    total_tickers = len(TARGET_TICKERS)
    
    for idx, symbol in enumerate(TARGET_TICKERS):
        print(f"[{idx+1}/{total_tickers}] 🔍 {symbol} ...", end=" ")
        
        has_data = False
        for date_str in target_dates:
            df, real_date = get_nasdaq_data(symbol, date_str)
            if df is None: continue
            
            has_data = True
            
            # 清洗與轉換
            cols_map = {'strike': 'Strike', 'c_Ask': 'Ask', 'c_Openinterest': 'OpenInterest', 'c_Volume': 'Volume'}
            if 'c_Openinterest' not in df.columns: continue
            
            calls = df[list(cols_map.keys())].rename(columns=cols_map)
            for c in ['Ask', 'OpenInterest', 'Volume']:
                calls[c] = pd.to_numeric(calls[c].astype(str).str.replace(',', '').str.replace('--', '0'), errors='coerce').fillna(0)
            calls['Strike'] = pd.to_numeric(calls['Strike'], errors='coerce')
            
            # 初步過濾
            candidates = calls[calls['OpenInterest'] > 500]
            
            for _, row in candidates.iterrows():
                data_row = {
                    'Stock': symbol,
                    'Expiry': real_date,
                    'Strike': row['Strike'],
                    'Ask': row['Ask'],
                    'OpenInterest': int(row['OpenInterest']),
                    'Volume': int(row['Volume'])
                }
                
                tags, action, score = apply_rules(data_row, prev_df)
                
                if score > 0 or action != "HOLD":
                    data_row['Tags'] = tags
                    data_row['Action'] = action
                    data_row['Score'] = score
                    today_results.append(data_row)
        
        if not has_data: print("❌ (無資料)")
        else: print("✅")

    if today_results:
        final_df = pd.DataFrame(today_results)
        final_df = final_df.sort_values(by=['Score', 'Volume'], ascending=[False, False])
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        file_path = f"{DATA_DIR}/{today_str}.csv"
        print(f"\n💾 儲存檔案: {file_path}")
        
        final_df.to_csv(file_path, index=False)
        generate_report(final_df)
    else:
        print("\n💨 今日無訊號。")

def generate_report(df):
    md = "# 🚬 每日妖股獵殺報表 (LEAPS版)\n\n"
    md += f"**更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
    
    # 增加按到期日排序的邏輯，讓報表更清楚
    df['Expiry'] = pd.to_datetime(df['Expiry'])
    
    # 計算 DTE (Days to Expiry)
    df['DTE'] = (df['Expiry'] - datetime.now()).dt.days
    
    action_order = ['STRONG_BUY', 'BUY_WATCH', 'HOLD']
    
    for action in action_order:
        sub_df = df[df['Action'] == action]
        if sub_df.empty: continue
            
        icon = "🚨" if action == 'STRONG_BUY' else ("👀" if "WATCH" in action else "🚬")
        
        if action == 'STRONG_BUY':
            md += f"## {icon} {action} (精選焦點)\n\n"
            
            # 分流：短期爆發 vs 長期埋伏 (界線: 120天)
            leaps_mask = sub_df['DTE'] > 120
            leaps_df = sub_df[leaps_mask].copy()
            short_df = sub_df[~leaps_mask].copy()
            
            # 1. LEAPS Section (重點：囤貨量 OI)
            if not leaps_df.empty:
                md += "### 🔭 遠期埋伏 (LEAPS > 120天)\n"
                md += "> 策略：時間換空間，跟隨聰明錢長期囤貨 (按持倉量排序)。\n\n"
                leaps_df = leaps_df.sort_values(by=['Score', 'OpenInterest'], ascending=[False, False])
                
                view = leaps_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'Volume', 'Tags', 'Score']].copy()
                view['Expiry'] = view['Expiry'].dt.strftime('%Y-%m-%d')
                view.columns = ['代號', '到期日', '履約價', '價格', '持倉(OI)', '成交(Vol)', '標籤', '分數']
                md += view.to_markdown(index=False) + "\n\n"

            # 2. Short Term Section (重點：成交動能 Volume)
            if not short_df.empty:
                md += "### 🚀 短期爆發 (Short Term < 120天)\n"
                md += "> 策略：末日輪盤或波段點火，關注資金流向 (按成交量排序)。\n\n"
                short_df = short_df.sort_values(by=['Score', 'Volume'], ascending=[False, False])
                
                view = short_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'Volume', 'Tags', 'Score']].copy()
                view['Expiry'] = view['Expiry'].dt.strftime('%Y-%m-%d')
                view.columns = ['代號', '到期日', '履約價', '價格', '持倉(OI)', '成交(Vol)', '標籤', '分數']
                md += view.to_markdown(index=False) + "\n\n"
        
        else:
            # 其他類別維持原樣
            md += f"## {icon} {action}\n"
            sub_df = sub_df.sort_values(by=['Score', 'Expiry'], ascending=[False, True])
            
            view = sub_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'Volume', 'Tags', 'Score']].copy()
            view['Expiry'] = view['Expiry'].dt.strftime('%Y-%m-%d')
            view.columns = ['代號', '到期日', '履約價', '價格', '持倉(OI)', '成交(Vol)', '標籤', '分數']
            md += view.to_markdown(index=False) + "\n\n"
            
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    main()
