"""
每週日跑一次：從 S&P 500 + 半導體 ETF 篩出「INTC-like」候選股
篩選邏輯：大市值 + 還在低位 + 有資金流入跡象 + 有期權市場
輸出：data/auto_watch.json

【v2 修正】
- Wikipedia 改用帶 User-Agent 的 requests，避免 403
- 多層 fallback：Wikipedia → datahub → 內建清單
"""
import yfinance as yf
import pandas as pd
import requests
import json
import os
import time
import random
import io
from datetime import datetime

OUTPUT_PATH = "data/auto_watch.json"
MAX_TICKERS = 25

CRITERIA = {
    'MIN_MARKET_CAP': 15e9,
    'MAX_PCT_FROM_52W_LOW': 1.8,
    'MIN_AVG_VOLUME': 5e6,
    'MIN_VOL_RATIO_20D': 1.2,
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}

# 內建 fallback 清單（半導體 + 大型科技 + 你可能感興趣的轉機股池）
FALLBACK_TICKERS = [
    # 半導體
    'AAPL', 'MSFT', 'NVDA', 'GOOG', 'META', 'TSLA', 'AMD', 'INTC',
    'AVGO', 'QCOM', 'MU', 'AMAT', 'LRCX', 'KLAC', 'TXN', 'ADI',
    'MRVL', 'NXPI', 'MCHP', 'ON', 'STX', 'WDC',
    # 大型科技 / 軟體
    'CSCO', 'IBM', 'ORCL', 'CRM', 'NOW', 'SNOW', 'PLTR', 'NET',
    'DDOG', 'CRWD', 'ZS', 'PANW', 'MDB', 'DBX',
    # 中型 / 轉機潛力
    'DELL', 'HPE', 'HPQ', 'WDAY', 'TEAM', 'OKTA', 'TWLO',
    # 金融 / 消費（可能有催化劑）
    'PYPL', 'SQ', 'COIN', 'HOOD', 'SOFI', 'AFRM',
    'F', 'GM', 'BA', 'GE', 'DIS', 'NKE', 'SBUX',
    # 製藥 / 生技
    'PFE', 'MRK', 'BMY', 'GILD', 'BIIB',
    # 能源 / 公用
    'VST', 'CEG', 'NEE', 'OKLO', 'SMR',
]


def fetch_sp500_from_wikipedia():
    """從 Wikipedia 抓 S&P 500（帶 User-Agent）"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        # 用 StringIO 包裝，避免 pandas 直接讀 URL（會丟失 UA）
        tables = pd.read_html(io.StringIO(res.text))
        df = tables[0]
        tickers = df['Symbol'].str.replace('.', '-').tolist()
        print(f"📋 Wikipedia S&P 500 載入 {len(tickers)} 檔")
        return tickers
    except Exception as e:
        print(f"⚠️ Wikipedia 失敗：{e}")
        return None


def fetch_sp500_from_datahub():
    """備援來源：datahub.io 提供的 CSV"""
    url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        df = pd.read_csv(io.StringIO(res.text))
        tickers = df['Symbol'].str.replace('.', '-').tolist()
        print(f"📋 datahub S&P 500 載入 {len(tickers)} 檔")
        return tickers
    except Exception as e:
        print(f"⚠️ datahub 失敗：{e}")
        return None


def get_sp500_tickers():
    """多層 fallback：Wikipedia → datahub → 內建清單"""
    for fetcher in (fetch_sp500_from_wikipedia, fetch_sp500_from_datahub):
        tickers = fetcher()
        if tickers and len(tickers) > 100:  # 至少 100 檔才算成功
            return tickers
    print(f"📋 全部來源失敗，使用內建 fallback ({len(FALLBACK_TICKERS)} 檔)")
    return FALLBACK_TICKERS


def screen_ticker(symbol):
    """單一標的篩選"""
    try:
        tk = yf.Ticker(symbol)
        info = tk.info
        
        mc = info.get('marketCap', 0)
        if mc < CRITERIA['MIN_MARKET_CAP']:
            return None
        
        low_52w = info.get('fiftyTwoWeekLow', 0)
        if low_52w <= 0:
            return None
        
        hist = tk.history(period='6mo')
        if len(hist) < 60:
            return None
        
        current_price = hist['Close'].iloc[-1]
        pct_from_low = current_price / low_52w
        
        if pct_from_low > CRITERIA['MAX_PCT_FROM_52W_LOW']:
            return None
        
        avg_vol_all = hist['Volume'].mean()
        avg_vol_20d = hist['Volume'].tail(20).mean()
        
        if avg_vol_all < CRITERIA['MIN_AVG_VOLUME']:
            return None
        
        vol_ratio = avg_vol_20d / avg_vol_all
        if vol_ratio < CRITERIA['MIN_VOL_RATIO_20D']:
            return None
        
        if not tk.options:
            return None
        
        score = (2.0 - pct_from_low) * 10 + vol_ratio * 5
        
        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'pct_from_52w_low': round(pct_from_low, 2),
            'vol_ratio_20d': round(vol_ratio, 2),
            'market_cap_b': round(mc / 1e9, 1),
            'score': round(score, 2),
        }
        
    except Exception:
        return None


def main():
    print(f"🔭 啟動 Universe Update: {datetime.now().strftime('%Y-%m-%d')}")
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    tickers = get_sp500_tickers()
    candidates = []
    
    for i, symbol in enumerate(tickers):
        if i % 50 == 0:
            print(f"  進度: {i}/{len(tickers)}")
        
        result = screen_ticker(symbol)
        if result:
            candidates.append(result)
        
        time.sleep(random.uniform(0.1, 0.3))
    
    candidates.sort(key=lambda x: x['score'], reverse=True)
    top = candidates[:MAX_TICKERS]
    
    output = {
        'updated_at': datetime.now().isoformat(),
        'criteria': CRITERIA,
        'count': len(top),
        'tickers': [c['symbol'] for c in top],
        'details': top,
    }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ 找到 {len(top)} 檔候選：{[c['symbol'] for c in top]}")
    print(f"💾 已寫入 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
