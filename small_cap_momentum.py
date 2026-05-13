"""
small_cap_momentum.py — 小盤動能 scanner

專門抓「VELO 級」的小妖股：
- 過去 30 天漲幅 > 30%（已經在動）
- 市值 $200M - $5B（小盤）
- 有期權市場
- 平均成交量 > 100 萬（有流動性）
- Short interest 高（軋空潛力）

輸出：data/small_caps_momentum.json
頻率：每週日跑（跟 universe_update 一起）
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

OUTPUT_PATH = "data/small_caps_momentum.json"
MAX_TICKERS = 20

CRITERIA = {
    'MIN_MARKET_CAP': 200e6,      # $200M
    'MAX_MARKET_CAP': 5e9,        # $5B（避開大盤）
    'MIN_30D_GAIN': 0.30,         # 過去 30 天漲幅 > 30%
    'MIN_AVG_VOLUME': 1e6,        # 日均量 > 100 萬
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}

# 候選池：常見的小盤股 + 高 beta 名單
# 這份清單你可以自己擴充
SMALL_CAP_UNIVERSE = [
    # 3D 列印 / 工業 4.0
    'VELO', 'DDD', 'SSYS', 'NNDM', 'XOMA', 'PRLB',
    # 儲能 / 電網
    'FLNC', 'STEM', 'NRG', 'AGRI', 'PLUG', 'BLDP', 'BE',
    # 量子 / AI 基礎設施
    'IONQ', 'RGTI', 'QBTS', 'NBIS', 'CRWV', 'SOUN', 'BBAI',
    # 太空 / 國防
    'RKLB', 'ASTS', 'LUNR', 'BKSY', 'PL', 'SPIR', 'IRDM',
    # 核能 / 替代能源
    'OKLO', 'SMR', 'NNE', 'VST', 'CEG', 'LEU', 'UEC', 'UUUU', 'CCJ',
    # 自動駕駛 / EV 概念
    'JOBY', 'ACHR', 'CHPT', 'EVGO', 'WKHS', 'SES', 'BLNK',
    # 生技 / GLP-1 / 基因編輯
    'HIMS', 'TDOC', 'CRSP', 'NTLA', 'BEAM', 'EDIT', 'VKTX', 'BMEA',
    # 金融科技 / 加密
    'SOFI', 'UPST', 'HOOD', 'AFRM', 'COIN', 'MARA', 'CLSK', 'RIOT', 'HUT', 'BITF',
    # 半導體小盤
    'AEHR', 'AMBA', 'POWI', 'ALGM', 'SITM', 'MTSI', 'ACMR',
    # 軟體 / SaaS 小盤
    'PATH', 'OPEN', 'ROKU', 'U', 'DKNG', 'TDUP', 'GRAB',
    # 機器人 / 自動化
    'SYM', 'BRZE', 'PRCT', 'MNTS', 'NVTS',
    # 熱門小妖股
    'ONDS', 'IREN', 'SMCI', 'OKLO', 'KTOS', 'PLTR', 'MSTR',
]


def screen_ticker(symbol):
    """單一標的篩選"""
    try:
        tk = yf.Ticker(symbol)
        info = tk.info
        
        mc = info.get('marketCap', 0)
        if mc < CRITERIA['MIN_MARKET_CAP'] or mc > CRITERIA['MAX_MARKET_CAP']:
            return None
        
        hist = tk.history(period='3mo')
        if len(hist) < 30:
            return None
        
        current_price = hist['Close'].iloc[-1]
        price_30d_ago = hist['Close'].iloc[-30] if len(hist) >= 30 else hist['Close'].iloc[0]
        gain_30d = (current_price / price_30d_ago) - 1
        
        if gain_30d < CRITERIA['MIN_30D_GAIN']:
            return None
        
        avg_vol = hist['Volume'].tail(20).mean()
        if avg_vol < CRITERIA['MIN_AVG_VOLUME']:
            return None
        
        if not tk.options:
            return None
        
        # Short interest 加分（高 short interest = 軋空潛力）
        short_pct = info.get('shortPercentOfFloat', 0) or 0
        
        # 計分：漲幅 × 量能 × short squeeze 潛力
        score = gain_30d * 10 + (short_pct * 100 if short_pct else 0)
        
        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'gain_30d_pct': round(gain_30d * 100, 1),
            'market_cap_m': round(mc / 1e6, 0),
            'avg_volume_m': round(avg_vol / 1e6, 2),
            'short_pct_float': round(short_pct * 100, 1) if short_pct else 0,
            'score': round(score, 2),
        }
        
    except Exception:
        return None


def main():
    print(f"🎰 啟動 Small Cap Momentum: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📋 候選池：{len(SMALL_CAP_UNIVERSE)} 檔小盤股")
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    candidates = []
    
    for i, symbol in enumerate(SMALL_CAP_UNIVERSE):
        if i % 20 == 0:
            print(f"  進度: {i}/{len(SMALL_CAP_UNIVERSE)}")
        
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
    
    print(f"\n✅ 找到 {len(top)} 檔小盤動能股：")
    for c in top[:10]:
        squeeze = f", short {c['short_pct_float']}%" if c['short_pct_float'] > 10 else ""
        print(f"  {c['symbol']}: ${c['price']} (+{c['gain_30d_pct']}% / 30d{squeeze})")
    
    print(f"\n💾 已寫入 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
