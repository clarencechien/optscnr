"""
fallen_saas.py — 殞落 SaaS / 軟體股重生雷達

抓 FIG 級別的 setup：
- 從 52 週高跌 60%+ 的軟體/SaaS 股
- 但已經從低點反彈 5-30%（在「剛 double-bottom」階段）
- 近期成交量 > 平均 1.3 倍（資金開始流入）
- 有期權市場

輸出：data/fallen_saas.json
頻率：每週日跑一次

設計理念：
- 不抓「動能」（那是 small_cap_momentum 的事）
- 不抓「催化劑」（那是 catalyst_fetch 的事）
- 專門抓「**還在地板但開始呼吸**」的標的
"""
import yfinance as yf
import pandas as pd
import json
import os
import time
import random
import logging
from datetime import datetime

OUTPUT_PATH = "data/fallen_saas.json"
MAX_TICKERS = 15

# 壓掉 yfinance 噪音
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

CRITERIA = {
    'MIN_DRAWDOWN_FROM_52W_HIGH': 0.55,   # 從 52w 高跌 55%+（重傷）
    'MIN_REBOUND_FROM_52W_LOW': 1.03,     # 已從 52w 低反彈 3%+（不是還在跌）
    'MAX_REBOUND_FROM_52W_LOW': 1.35,     # 但反彈 < 35%（還在早期，避免追高）
    'MIN_MARKET_CAP': 1e9,                # 至少 $1B（避地雷）
    'MAX_MARKET_CAP': 50e9,               # 上限 $500B（不要 Netflix 級）
    'MIN_VOL_RATIO': 1.2,                 # 近 10 日量能 > 整體平均 1.2x
    'MIN_AVG_VOLUME': 500_000,            # 日均量 > 50 萬（流動性）
}

# 候選池：軟體 / SaaS / 設計工具 / 開發者工具 / AI 應用
# 涵蓋曾經高位後來大跌的軟體股
FALLEN_SAAS_UNIVERSE = [
    # === 設計 / 創作工具 ===
    'FIG',    # Figma（IPO 後跌 86%）
    'ADBE',   # Adobe（大盤但被 AI 焦慮殺到）
    'PINS',   # Pinterest
    'SNAP',   # Snap

    # === 開發者工具 / DevOps ===
    'GTLB',   # GitLab
    'JFROG',  # JFrog
    'ESTC',   # Elastic
    'BAND',   # Bandwidth
    'TWLO',   # Twilio
    'OKTA',   # Okta
    'CFLT',   # Confluent
    'MDB',    # MongoDB

    # === 行銷 / CDP / 數據 ===
    'BRZE',   # Braze
    'HUBS',   # HubSpot
    'TEAM',   # Atlassian
    'WDAY',   # Workday

    # === 雲端基礎建設 ===
    'NET',    # Cloudflare
    'DDOG',   # Datadog
    'SNOW',   # Snowflake
    'ZS',     # Zscaler
    'S',      # SentinelOne
    'PANW',   # Palo Alto Networks
    'CRWD',   # CrowdStrike

    # === 視訊會議 / 通訊 ===
    'ZM',     # Zoom（從 $500 跌到 $60）
    'RNG',    # RingCentral
    'EGHT',   # 8x8

    # === 電商 / 訂閱 ===
    'WIX',    # Wix
    'PLNT',   # Planet Labs (不算 SaaS 但類似結構)
    'AFRM',   # Affirm
    'COUR',   # Coursera
    'CHWY',   # Chewy
    'CVNA',   # Carvana (重生案例經典)

    # === CRM / SaaS 老牌 ===
    'CRM',    # Salesforce
    'NOW',    # ServiceNow
    'INTU',   # Intuit
    'WDAY',   # Workday

    # === AI / ML 平台 ===
    'AI',     # C3.ai
    'PATH',   # UiPath
    'SOUN',   # SoundHound
    'BBAI',   # BigBear

    # === 教育 / 健康 SaaS ===
    'TDOC',   # Teladoc
    'VEEV',   # Veeva
    'CHGG',   # Chegg
    'DUOL',   # Duolingo

    # === Fintech SaaS ===
    'SQ',     # Block
    'PYPL',   # PayPal
    'UPST',   # Upstart
    'LMND',   # Lemonade

    # === 媒體 / 內容 SaaS ===
    'ROKU',   # Roku
    'PARA',   # Paramount
    'WBD',    # Warner Bros Discovery
    'DIS',    # Disney

    # === 其他 SaaS 跌深名單 ===
    'U',      # Unity
    'RBLX',   # Roblox
    'COIN',   # Coinbase
    'OPEN',   # Opendoor
    'RDFN',   # Redfin
    'Z',      # Zillow
    'AFRM',   # Affirm
]


def screen_ticker(symbol):
    """單一標的篩選"""
    try:
        tk = yf.Ticker(symbol)
        info = tk.info

        mc = info.get('marketCap', 0)
        if mc < CRITERIA['MIN_MARKET_CAP'] or mc > CRITERIA['MAX_MARKET_CAP']:
            return None

        high_52w = info.get('fiftyTwoWeekHigh', 0)
        low_52w = info.get('fiftyTwoWeekLow', 0)
        if high_52w <= 0 or low_52w <= 0:
            return None

        hist = tk.history(period='3mo')
        if len(hist) < 20:
            return None

        current_price = hist['Close'].iloc[-1]

        # 條件 1：跌幅夠深
        drawdown = 1 - (current_price / high_52w)
        if drawdown < CRITERIA['MIN_DRAWDOWN_FROM_52W_HIGH']:
            return None

        # 條件 2：已開始反彈（從低點上來 3-35%）
        rebound = current_price / low_52w
        if rebound < CRITERIA['MIN_REBOUND_FROM_52W_LOW']:
            return None  # 還在跌
        if rebound > CRITERIA['MAX_REBOUND_FROM_52W_LOW']:
            return None  # 已經彈太多

        # 條件 3：資金開始流入
        avg_vol_all = hist['Volume'].mean()
        avg_vol_10d = hist['Volume'].tail(10).mean()
        if avg_vol_all < CRITERIA['MIN_AVG_VOLUME']:
            return None

        vol_ratio = avg_vol_10d / avg_vol_all
        if vol_ratio < CRITERIA['MIN_VOL_RATIO']:
            return None

        # 條件 4：有期權市場
        if not tk.options:
            return None

        # 評分：
        # - 跌得深（rebirth 空間大）
        # - 反彈幅度小（早期紅利）
        # - 量能放大（市場注意到）
        score = (
            drawdown * 30                          # 跌 60% = 18 分，跌 80% = 24 分
            + (1.4 - rebound) * 20                 # 反彈 5% = 7 分，反彈 30% = 2 分
            + (vol_ratio - 1) * 10                 # 量能 1.5x = 5 分
        )

        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'drawdown_pct': round(drawdown * 100, 1),
            'rebound_pct': round((rebound - 1) * 100, 1),
            'vol_ratio': round(vol_ratio, 2),
            'market_cap_b': round(mc / 1e9, 1),
            'score': round(score, 2),
        }

    except Exception:
        return None


def main():
    print(f"💀 啟動 Fallen SaaS Scanner: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📋 候選池：{len(FALLEN_SAAS_UNIVERSE)} 檔 SaaS/軟體股")
    print(f"🎯 條件：跌 {CRITERIA['MIN_DRAWDOWN_FROM_52W_HIGH']*100:.0f}%+ / 反彈 "
          f"{(CRITERIA['MIN_REBOUND_FROM_52W_LOW']-1)*100:.0f}-"
          f"{(CRITERIA['MAX_REBOUND_FROM_52W_LOW']-1)*100:.0f}% / "
          f"量能 +{(CRITERIA['MIN_VOL_RATIO']-1)*100:.0f}%+")

    if not os.path.exists('data'):
        os.makedirs('data')

    # 去重（清單裡有些重複）
    universe = list(dict.fromkeys(FALLEN_SAAS_UNIVERSE))
    print(f"📋 去重後：{len(universe)} 檔\n")

    candidates = []

    for i, symbol in enumerate(universe):
        if i % 15 == 0:
            print(f"  進度: {i}/{len(universe)}")

        result = screen_ticker(symbol)
        if result:
            candidates.append(result)

        time.sleep(random.uniform(0.15, 0.35))

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

    print(f"\n✅ 找到 {len(top)} 檔 fallen SaaS 重生候選：")
    for c in top[:10]:
        print(f"  {c['symbol']}: ${c['price']} "
              f"(從高跌 {c['drawdown_pct']:.0f}% / "
              f"從低反彈 +{c['rebound_pct']:.0f}% / "
              f"量能 {c['vol_ratio']:.1f}x)")

    print(f"\n💾 已寫入 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
