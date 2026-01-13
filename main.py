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

# GitHub Repo 設定 (用來抓昨天的資料進行比較)
# ⚠️ 請將這裡換成你的 GitHub 帳號與 Repo 名稱
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
        'UPST', 'SOFI', 'DKNG', 'IREN', 'NBIS',
        # ARK 菸屁股
        'U', 'PATH', 'ROKU', 'HOOD', 'TDOC', 'ZM', 'SQ', 
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
        'PRICE': 15.0     # 價格上限 (太貴的不算菸屁股)
    },
    
    # 🦄 妖股組參數 (門檻大幅降低以捕捉早期訊號)
    'SMALL_CAPS_THRESHOLD': {
        'OI': 1500,       # 只要有 1500 張囤單就算多
        'VOL': 300,       # 小股票 300 張成交就算點火
        'PRICE': 2.0      # 重點！只看 $2.0 (權利金$200) 以下的彩票
    }
}

# ==========================================
# 2. 輔助函數 (Helpers)
# ==========================================

def get_target_dates():
    """
    生成目標日期：
    1. 加入「本週五」與「下週五」 (捕捉 Gamma Squeeze)
    2. 加入未來 3 個月的「月選」(每個月第三個週五，捕捉波段佈局)
    """
    dates = set() # 使用 set 去重
    today = datetime.now()
    
    # --- A. 近兩週週選 (Short Term) ---
    days_ahead = 4 - today.weekday() # 4 is Friday
    if days_ahead < 0: days_ahead += 7
    this_friday = today + timedelta(days=days_ahead)
    next_friday = this_friday + timedelta(days=7)
    
    dates.add(this_friday.strftime('%Y-%m-%d'))
    dates.add(next_friday.strftime('%Y-%m-%d'))

    # --- B. 未來月選 (Long Term) ---
    # 掃描未來 4 個月
    for i in range(4):
        # 計算月份
        future_month_first = (today.replace(day=1) + timedelta(days=32*i)).replace(day=1)
        
        # 尋找該月第一個週五
        # weekday(): Mon=0, Fri=4
        # (4 - first_day.weekday() + 7) % 7 gives days to first friday
        days_to_first_friday = (4 - future_month_first.weekday() + 7) % 7
        first_friday = future_month_first + timedelta(days=days_to_first_friday)
        
        # 月選通常是第三個週五
        third_friday = first_friday + timedelta(days=14)
        
        # 只加入未來的日期
        if third_friday >= today:
            dates.add(third_friday.strftime('%Y-%m-%d'))

    # 排序並轉回列表
    sorted_dates = sorted(list(dates))
    return sorted_dates

def fetch_yesterday_data_from_github():
    """
    從 GitHub Raw Content 下載昨天的 CSV，解決 CI/CD 環境沒有歷史檔案的問題
    """
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    # 如果今天是週一，昨天可能是週日沒資料，往前多試幾天
    for lookback in range(1, 4):
        check_date = (datetime.now() - timedelta(days=lookback)).strftime("%Y-%m-%d")
        url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{DATA_DIR}/{check_date}.csv"
        
        print(f"☁️ 嘗試從 GitHub 下載歷史紀錄 ({check_date})...", end=" ")
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                df = pd.read_csv(io.StringIO(res.text))
                print(f"✅ 成功! 取得 {len(df)} 筆歷史資料")
                return df
            else:
                print(f"❌ 無資料 (HTTP {res.status_code})")
        except Exception as e:
            print(f"💥 連線錯誤: {e}")
            
    print("⚠️ 無法取得任何歷史資料，將使用盲測模式 (無法比較昨日成交量)")
    return None

def get_nasdaq_data(symbol, date_str):
    """
    爬取 Nasdaq Option Chain
    自動切換 'stocks' 與 'etf' 模式 (針對 IBIT, ARKK 等)
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    ]
    
    # IBIT, QQQ 等屬於 ETF，其他是 stocks。輪詢嘗試以免遺漏。
    asset_classes = ['stocks', 'etf']
    
    for asset_class in asset_classes:
        url = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass={asset_class}&fromDate={date_str}&toDate={date_str}&money=all"
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nasdaq.com/'
        }
        
        try:
            # 隨機延遲避免被封鎖
            time.sleep(random.uniform(0.5, 1.5))
            res = requests.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                json_data = res.json()
                status = json_data.get('status', {})
                
                # 成功取得數據
                if status.get('rCode') == 200:
                    rows = json_data.get('data', {}).get('table', {}).get('rows', [])
                    if rows:
                        return pd.DataFrame(rows), date_str
                    else:
                        # 該日期無資料 (可能休市)，不需要試 asset_class
                        return None, date_str
                
                # 錯誤處理：如果代號不存在，嘗試切換 asset_class
                b_msg = str(status.get('bCodeMessage', ''))
                if "Symbol not exists" in b_msg or "Invalid Asset Class" in b_msg:
                    if asset_class == 'stocks': continue # 試試看 ETF
            
        except Exception as e:
            print(f"💥 API 異常 {symbol}: {e}")
            
    return None, date_str

# ==========================================
# 3. 規則引擎 (Core Logic)
# ==========================================

def apply_rules(row, prev_data=None):
    """
    針對每一行選擇權數據進行評分
    """
    tags = []
    action = "HOLD"
    score = 0
    
    symbol = row['Stock']
    price = row['Ask']
    oi = row['OpenInterest']
    vol = row['Volume']
    expiry = row['Expiry']
    strike = row['Strike']

    # --- 1. 決定門檻 (巨獸 vs 妖股) ---
    if symbol in TICKER_CATEGORIES['SMALL_CAPS']:
        cfg = RULE_CONFIG['SMALL_CAPS_THRESHOLD']
        is_small_cap = True
        # 特殊微調：生技股與太空股 OI 通常更低，門檻再打 8 折
        if symbol in ['CRSP', 'NTLA', 'RKLB', 'ASTS']:
            cfg_oi = cfg['OI'] * 0.8
        else:
            cfg_oi = cfg['OI']
    else:
        cfg = RULE_CONFIG['BIG_CAPS_THRESHOLD']
        is_small_cap = False
        cfg_oi = cfg['OI']

    # --- 規則 2: 菸屁股篩選 (便宜 + 有人屯倉) ---
    # 這裡很嚴格，妖股必須 < $2.0，確保是樂透單
    if price <= cfg['PRICE'] and oi > cfg_oi:
        tags.append("🚬菸屁股")
        score += 1

    # --- 規則 3: 點火偵測 (Volume Spike) ---
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
            # 如果昨天沒量，今天突然有量 (且超過門檻)
            if prev_vol == 0:
                if vol > cfg['VOL']:
                    ignition_detected = True
                    vol_msg = "🚀死灰復燃"
            else:
                vol_ratio = vol / prev_vol
                if vol > cfg['VOL'] and vol_ratio >= RULE_CONFIG['VOL_SPIKE_RATIO']:
                    ignition_detected = True
                    vol_msg = f"🚀點火({vol_ratio:.1f}x)"
        else:
            # 昨天不存在這檔合約 (新開倉?)
            if vol > cfg['VOL']:
                ignition_detected = True
                vol_msg = "🆕新開倉點火"
    else:
        # 盲測模式 (無歷史資料)：如果成交量 > 持倉量的 20% 且超過門檻
        if vol > cfg['VOL'] and vol > (oi * 0.2):
            ignition_detected = True
            vol_msg = "🚀突發暴量(盲)"

    if ignition_detected:
        tags.append(vol_msg)
        score += 3
        action = "BUY_WATCH"

    # --- 規則 4: 萬人塚 (Whale Alert) ---
    # 這裡用絕對數值，代表極端共識
    if oi > 50000:
        tags.append("👑超級萬人塚")
        score += 2
    elif oi > 20000:
        tags.append("🔥萬人塚")
        score += 1
        
    # --- 最終判定 ---
    # 同時滿足「菸屁股」(低價高OI) 與 「點火」(成交量爆發) = 強力買入
    if "🚬菸屁股" in str(tags) and ignition_detected:
        action = "STRONG_BUY"
        score += 2 # 加分
        
    return " ".join(tags), action, score

# ==========================================
# 4. 主程序 (Main Execution)
# ==========================================

def main():
    print(f"🚀 啟動 ARK 妖股掃描器 - {datetime.now().strftime('%Y-%m-%d')}", flush=True)
    
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    # 1. 取得歷史資料
    prev_df = fetch_yesterday_data_from_github()
    
    today_results = []
    target_dates = get_target_dates()
    print(f"📅 鎖定合約日期: {target_dates}")
    
    total_tickers = len(TARGET_TICKERS)
    
    # 2. 開始掃描
    for idx, symbol in enumerate(TARGET_TICKERS):
        print(f"[{idx+1}/{total_tickers}] 🔍 掃描 {symbol} ...", end=" ")
        
        # 顯示該股屬於哪一類，方便除錯
        category = "🦁" if symbol in TICKER_CATEGORIES['BIG_CAPS'] else "🦄"
        print(f"({category})", end=" ")
        
        has_data = False
        for date_str in target_dates:
            df, real_date = get_nasdaq_data(symbol, date_str)
            if df is None: continue
            
            has_data = True
            
            # 資料清洗
            cols_map = {'strike': 'Strike', 'c_Ask': 'Ask', 'c_Openinterest': 'OpenInterest', 'c_Volume': 'Volume'}
            if 'c_Openinterest' not in df.columns: continue
            
            calls = df[list(cols_map.keys())].rename(columns=cols_map)
            
            # 數值轉換
            for c in ['Ask', 'OpenInterest', 'Volume']:
                calls[c] = pd.to_numeric(calls[c].astype(str).str.replace(',', '').str.replace('--', '0'), errors='coerce').fillna(0)
            calls['Strike'] = pd.to_numeric(calls['Strike'], errors='coerce')
            
            # --- 初步過濾 (Pre-filter) ---
            # 為了效能，只處理 OI > 500 的單子 (太小的單子沒意義)
            # 這裡用比較寬鬆的 500，詳細規則在 apply_rules 判定
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
                
                # 只保留有意義的結果
                if score > 0 or action != "HOLD":
                    data_row['Tags'] = tags
                    data_row['Action'] = action
                    data_row['Score'] = score
                    today_results.append(data_row)
        
        if not has_data:
            print("❌ (無資料)")
        else:
            print("✅")

    # 3. 輸出結果
    if today_results:
        final_df = pd.DataFrame(today_results)
        final_df = final_df.sort_values(by=['Score', 'Volume'], ascending=[False, False])
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        file_path = f"{DATA_DIR}/{today_str}.csv"
        print(f"\n💾 儲存檔案: {file_path} (共 {len(final_df)} 筆機會)")
        
        final_df.to_csv(file_path, index=False)
        generate_report(final_df)
    else:
        print("\n💨 今日市場平靜，無符合條件的標的。")

def generate_report(df):
    """
    生成 Markdown 報表
    """
    md = "# 🚬 每日妖股獵殺報表 (ARK Edition)\n\n"
    md += f"**更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
    md += f"**監控範圍**: {len(TARGET_TICKERS)} 檔標的 (含巨獸與妖股)\n\n"
    md += "---\n\n"
    
    # 定義顯示順序
    action_order = ['STRONG_BUY', 'BUY_WATCH', 'HOLD']
    
    for action in action_order:
        sub_df = df[df['Action'] == action]
        if not sub_df.empty:
            if action == 'STRONG_BUY':
                title = "🚨 強力買入訊號 (Strong Buy)"
                desc = "同時滿足「低價大量囤倉」與「今日爆量點火」，極具潛力。"
            elif action == 'BUY_WATCH':
                title = "👀 觀察清單 (Watch List)"
                desc = "出現異動（點火或暴量），但尚未完全符合菸屁股定義，建議放入觀察。"
            else:
                title = "🚬 菸屁股 / 萬人塚 (Hold)"
                desc = "大量持倉但今日無明顯動靜，適合埋伏或觀察支撐。"

            md += f"## {title}\n"
            md += f"_{desc}_\n\n"
            
            # 選取顯示欄位
            view = sub_df[['Stock', 'Expiry', 'Strike', 'Ask', 'OpenInterest', 'Volume', 'Tags', 'Score']].copy()
            
            # 格式美化
            view.columns = ['代號', '到期日', '履約價', '價格', '持倉(OI)', '成交(Vol)', '標籤', '分數']
            
            md += view.to_markdown(index=False) + "\n\n"
            
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("📝 README.md 報表已更新")

if __name__ == "__main__":
    main()
