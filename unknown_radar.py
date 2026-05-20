"""
unknown_radar.py — 「擦鞋童都聽過了但我沒聽過」雷達

設計理念：
- 不是要涵蓋全宇宙
- 是抓「**新聞已經反覆提到、但我的 scanner 字典裡沒有**」的標的
- 這些就是「擦鞋童效應」的早期訊號：新聞圈知道，但我還不認識

工作流程：
1. 讀同一輪 catalyst_fetch 抓的新聞（重抓一次）
2. 用 NER 抽取所有大寫公司名（不依賴字典）
3. 過濾掉：
   - 已在 TICKER_MAP 的（known）
   - 已在 WATCH_ONLY_NAMES 的（known unknown）
   - 太常見的字（Inc, Corp, US, AI 之類）
   - 私募公司（OpenAI/Stripe/Anthropic）
4. 對照上市公司名單（NASDAQ + NYSE 從 SEC 抓），找 ticker
5. 累積到本地 history（看連續幾天出現）
6. 連續 3 天出現 → 列為「強盲點訊號」

頻率：每天跑（跟 catalyst_fetch 同步）

輸出：
- data/unknown_radar.json
- data/unknown_radar_history.json（累積天數）
"""
import requests
import feedparser
import re
import json
import os
import csv
import io
from datetime import datetime, timedelta
from collections import Counter

# === 設定 ===
OUTPUT_PATH = "data/unknown_radar.json"
HISTORY_PATH = "data/unknown_radar_history.json"
LISTED_COMPANIES_CACHE = "data/listed_companies.json"

MIN_MENTIONS_TODAY = 2       # 今日至少被提到 2 次才算
MIN_CONSECUTIVE_DAYS = 2     # 連續 2 天出現才升級為「強訊號」
MAX_OUTPUT = 15              # 最多輸出 15 個盲點候選

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}

RSS_FEEDS = [
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://www.marketwatch.com/rss/topstories",
    "https://www.investing.com/rss/news_25.rss",
    "https://seekingalpha.com/market_currents.xml",
    "https://finance.yahoo.com/news/rssindex",
]

# 已知 ticker / 別名（手動同步 catalyst_fetch 的字典）
# 這裡列出常見的，避免被當「unknown」
KNOWN_TICKERS = {
    'AAPL', 'MSFT', 'GOOG', 'GOOGL', 'META', 'NVDA', 'AMZN', 'TSLA', 'NFLX',
    'INTC', 'AMD', 'TSM', 'AVGO', 'QCOM', 'MU', 'AMAT', 'LRCX', 'KLAC',
    'ASML', 'MRVL', 'ARM', 'SMCI', 'CRM', 'ORCL', 'IBM', 'NOW', 'SNOW',
    'PLTR', 'NET', 'DDOG', 'CRWD', 'ZS', 'PANW', 'MDB', 'COIN', 'HOOD',
    'SOFI', 'PYPL', 'MSTR', 'IBIT', 'AFRM', 'UPST', 'MARA', 'CLSK', 'RIOT',
    'HUT', 'BITF', 'IREN', 'RIVN', 'LCID', 'F', 'GM', 'CHPT', 'EVGO', 'BLNK',
    'WKHS', 'VST', 'CEG', 'NEE', 'NRG', 'OKLO', 'SMR', 'NNE', 'LEU', 'UEC',
    'UUUU', 'CCJ', 'FLNC', 'STEM', 'PLUG', 'BLDP', 'BE', 'SEDG', 'ENPH',
    'RUN', 'NOVA', 'FSLR', 'NXT', 'VELO', 'DDD', 'SSYS', 'NNDM', 'PRLB',
    'IONQ', 'RGTI', 'QBTS', 'RKLB', 'ASTS', 'LUNR', 'BKSY', 'IRDM', 'SPIR',
    'JOBY', 'ACHR', 'KTOS', 'BA', 'RTX', 'CRSP', 'NTLA', 'BEAM', 'EDIT',
    'HIMS', 'TDOC', 'PFE', 'MRK', 'GILD', 'MRNA', 'VKTX', 'BMEA', 'PACB',
    'NBIS', 'CRWV', 'SOUN', 'BBAI', 'DELL', 'HPE', 'HPQ', 'WDAY', 'OKTA',
    'TWLO', 'TEAM', 'SYM', 'PRCT', 'SHOP', 'ANET', 'DKNG', 'OPEN', 'ROKU',
    'U', 'VRT', 'PATH', 'DIS', 'NKE', 'SBUX', 'WMT', 'TGT', 'COST',
    'GS', 'MS', 'JPM', 'BAC', 'GOLD', 'FCX', 'ONDS', 'XYZ', 'NFLX',
    'AEHR', 'AMBA', 'WDC', 'STX', 'SNDK',
}

# 已知公司名（包含完整名稱、用來過濾）
KNOWN_COMPANY_NAMES = {
    'Apple', 'Microsoft', 'Google', 'Alphabet', 'Meta', 'Facebook', 'Nvidia',
    'Amazon', 'Tesla', 'Netflix', 'Intel', 'AMD', 'TSMC', 'Broadcom',
    'Qualcomm', 'Micron', 'Salesforce', 'Oracle', 'IBM', 'Snowflake',
    'Palantir', 'Cloudflare', 'Datadog', 'CrowdStrike', 'Zscaler',
    'MongoDB', 'Coinbase', 'Robinhood', 'SoFi', 'PayPal', 'MicroStrategy',
    'BlackRock', 'Affirm', 'Upstart', 'Marathon', 'CleanSpark', 'Riot',
    'Rivian', 'Lucid', 'Ford', 'General Motors', 'GM', 'ChargePoint',
    'EVgo', 'Vistra', 'Constellation', 'NextEra', 'Oklo', 'NuScale',
    'Fluence', 'Plug Power', 'Ballard', 'Bloom Energy', 'SolarEdge',
    'Enphase', 'Sunrun', 'First Solar', 'Nextracker', 'Velo3D', 'IonQ',
    'Rigetti', 'D-Wave', 'Rocket Lab', 'AST SpaceMobile', 'Iridium',
    'Joby', 'Archer', 'Kratos', 'Boeing', 'RTX', 'Raytheon', 'CRISPR',
    'Intellia', 'Hims', 'Teladoc', 'Pfizer', 'Merck', 'Gilead', 'Moderna',
    'Nebius', 'CoreWeave', 'SoundHound', 'BigBear', 'Dell', 'HP',
    'Workday', 'Okta', 'Twilio', 'Atlassian', 'Symbotic', 'Shopify',
    'Arista', 'DraftKings', 'Opendoor', 'Roku', 'Unity', 'Vertiv',
    'UiPath', 'Disney', 'Nike', 'Starbucks', 'Walmart', 'Target', 'Costco',
    'Goldman Sachs', 'Morgan Stanley', 'JPMorgan', 'JP Morgan', 'Bank of America',
    'Berkshire', 'Barrick', 'Freeport', 'Pinterest', 'Snap', 'Adobe',
    'GitLab', 'Elastic', 'HubSpot', 'Braze', 'Block', 'Square', 'Wix',
    'Carvana', 'Chewy', 'Coursera', 'Roblox', 'Redfin', 'Zillow',
    'C3', 'C3.ai', 'Veeva', 'Chegg', 'Duolingo', 'Lemonade',
    'Paramount', 'Warner Bros', 'Discovery', 'Affirm',
    'Aehr', 'Aehr Test', 'Ambarella', 'Lam Research', 'Applied Materials',
    'Western Digital', 'Seagate', 'SanDisk', 'Super Micro', 'Supermicro',
    # 私募 / 已知非美股
    'OpenAI', 'Anthropic', 'Stripe', 'DeepSeek', 'xAI', 'Cerebras',
    'Saudi Aramco', 'Nintendo', 'ByteDance', 'TikTok', 'SpaceX',
}

# 太常見的詞，過濾掉避免誤判公司名
COMMON_WORDS = {
    'The', 'A', 'An', 'And', 'Or', 'But', 'For', 'With', 'On', 'In', 'At',
    'To', 'From', 'By', 'Of', 'As', 'Is', 'Are', 'Was', 'Were', 'Be',
    'Been', 'Being', 'Have', 'Has', 'Had', 'Do', 'Does', 'Did', 'Will',
    'Would', 'Could', 'Should', 'May', 'Might', 'Must', 'Can',
    'Inc', 'Corp', 'Corporation', 'Company', 'Co', 'Ltd', 'LLC', 'LP',
    'US', 'USA', 'UK', 'EU', 'China', 'Japan', 'India', 'Russia',
    'America', 'American', 'European', 'Asian', 'Wall', 'Street',
    'AI', 'CEO', 'CFO', 'CTO', 'COO', 'IPO', 'ETF', 'GDP', 'CPI',
    'Fed', 'SEC', 'FDA', 'FTC', 'DOJ', 'Treasury', 'Pentagon',
    'Q1', 'Q2', 'Q3', 'Q4', 'FY', 'EPS', 'PE', 'YoY', 'QoQ',
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
    'New', 'York', 'San', 'Francisco', 'Los', 'Angeles', 'Chicago',
    'Trump', 'Biden', 'Harris', 'Musk', 'Bezos', 'Buffett',  # 不是公司
    'Bitcoin', 'Ethereum', 'Crypto', 'Dollar', 'Euro', 'Yen',
    'Reuters', 'Bloomberg', 'CNBC', 'WSJ', 'MarketWatch', 'Yahoo',
    'Seeking', 'Alpha', 'Forbes', 'Barron',  # 媒體名
    'Stock', 'Stocks', 'Market', 'Markets', 'Index', 'Indices',
    'Buy', 'Sell', 'Hold', 'Upgrade', 'Downgrade', 'Target', 'Rating',
    'NYSE', 'NASDAQ', 'Dow', 'Jones', 'Russell',
    'Group', 'Holdings', 'Partners', 'Capital', 'Securities', 'Energy',
    'Technologies', 'Systems', 'Solutions', 'Industries',
    'COVID', 'Pandemic', 'Recession',
    'Cowen', 'TD',  # 投行的人名
    'Lilly',  # 太常見的單一字
}


def fetch_listed_companies():
    """從 SEC 抓上市公司名單（NASDAQ + NYSE）
    
    SEC 要求 User-Agent 包含真實識別資訊（name + email），
    不接受瀏覽器假冒的 UA
    
    回傳: {company_name_normalized: ticker}
    """
    if os.path.exists(LISTED_COMPANIES_CACHE):
        cache_age = datetime.now().timestamp() - os.path.getmtime(LISTED_COMPANIES_CACHE)
        # 30 天內的 cache 直接用
        if cache_age < 30 * 86400:
            print("📋 使用本地上市公司清單 cache")
            with open(LISTED_COMPANIES_CACHE) as f:
                return json.load(f)
    
    # SEC 規定的 User-Agent 格式：公司或個人名稱 + email
    # 如果這個你要改成自己的識別資訊，把下面這行換掉
    SEC_HEADERS = {
        'User-Agent': 'optscnr-bot research@optscnr.dev',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov',
    }
    
    print("🌐 下載 SEC 上市公司清單...")
    url = "https://www.sec.gov/files/company_tickers.json"
    
    try:
        r = requests.get(url, headers=SEC_HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        # SEC 格式: {"0": {"cik_str": ..., "ticker": "AAPL", "title": "Apple Inc"}, ...}
        company_to_ticker = {}
        for _, info in data.items():
            ticker = info.get('ticker', '').upper()
            title = info.get('title', '')
            if ticker and title:
                name_clean = clean_company_name(title)
                if name_clean:
                    company_to_ticker[name_clean] = ticker
        
        # 寫 cache
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(LISTED_COMPANIES_CACHE, 'w') as f:
            json.dump(company_to_ticker, f)
        
        print(f"✅ 載入 {len(company_to_ticker)} 家上市公司（SEC）")
        return company_to_ticker
        
    except Exception as e:
        print(f"⚠️ SEC 公司清單下載失敗：{e}")
        print("   嘗試備用來源...")
        return fetch_listed_companies_fallback()


def fetch_listed_companies_fallback():
    """備用：從 NASDAQ 公開 trader 端口抓
    
    這個端口不需要特殊 User-Agent，但格式是 csv
    """
    try:
        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        
        company_to_ticker = {}
        # 格式: Symbol|Security Name|Market Category|...
        lines = r.text.split('\n')
        for line in lines[1:]:  # 跳過 header
            parts = line.split('|')
            if len(parts) < 2:
                continue
            ticker = parts[0].strip().upper()
            title = parts[1].strip()
            if ticker and title and not ticker.startswith('File'):
                name_clean = clean_company_name(title)
                if name_clean:
                    company_to_ticker[name_clean] = ticker
        
        # 也抓 NYSE 那邊的
        try:
            url2 = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
            r2 = requests.get(url2, headers=HEADERS, timeout=30)
            if r2.status_code == 200:
                for line in r2.text.split('\n')[1:]:
                    parts = line.split('|')
                    if len(parts) < 2:
                        continue
                    ticker = parts[0].strip().upper()
                    title = parts[1].strip()
                    if ticker and title and not ticker.startswith('File'):
                        name_clean = clean_company_name(title)
                        if name_clean:
                            company_to_ticker[name_clean] = ticker
        except Exception:
            pass
        
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(LISTED_COMPANIES_CACHE, 'w') as f:
            json.dump(company_to_ticker, f)
        
        print(f"✅ 載入 {len(company_to_ticker)} 家上市公司（NASDAQ Trader）")
        return company_to_ticker
        
    except Exception as e:
        print(f"⚠️ NASDAQ Trader 也失敗：{e}")
        return {}


def clean_company_name(name):
    """正規化公司名以便比對
    
    例如：'Apple Inc.' → 'apple'
    'Microsoft Corporation' → 'microsoft'
    """
    if not name:
        return ''
    
    name = name.lower()
    # 移除常見後綴
    suffixes = [' inc', ' corp', ' corporation', ' co.', ' co', ' ltd', 
                ' llc', ' lp', ' plc', ' sa', ' ag', ' nv', ' holdings',
                ' technologies', ' group', ' company', ' & co', '.com']
    for sfx in suffixes:
        if name.endswith(sfx):
            name = name[:-len(sfx)]
            break
    # 移除標點
    name = re.sub(r'[.,;:]', '', name)
    return name.strip()


def extract_proper_nouns(text):
    """從新聞文字抽取「可能的公司名」
    
    策略：抓所有大寫開頭的詞或多詞片語
    - 單詞：'Tempus'、'Symbotic'
    - 雙詞：'Astera Labs'、'Saudi Aramco'
    - 三詞：'AST SpaceMobile'
    
    過濾：
    - 句首大寫字（很多是普通字）
    - COMMON_WORDS
    """
    if not text:
        return []
    
    # 移除標題開頭，避免句首誤判
    # 直接抓「至少 2 個大寫字」的 pattern：
    # 1. 兩個或更多大寫詞連在一起 "AST SpaceMobile"
    # 2. 大寫詞 + (小寫詞)? + 大寫詞 "Bank of America"
    # 3. 單一大寫詞 + 後綴 Inc/Corp/Ltd
    
    # 簡化策略：先抓所有 capitalized words 連續組合（1-3 個詞）
    # Pattern: [A-Z][a-zA-Z0-9]+(?:\s+(?:of|and|&|de|la|the)\s+)?(?:\s+[A-Z][a-zA-Z0-9]+){0,2}
    pattern = r'\b([A-Z][a-zA-Z0-9]{2,}(?:\s+[A-Z][a-zA-Z0-9&]+){0,2})\b'
    matches = re.findall(pattern, text)
    
    result = []
    for m in matches:
        # 排除完全是常見字
        words = m.split()
        if all(w in COMMON_WORDS for w in words):
            continue
        # 排除單一短字
        if len(m) <= 3:
            continue
        # 排除明顯非公司（人名、地名）
        if any(w in COMMON_WORDS for w in words[:1]):
            # 例如 "May Q1" 的 "May" 排除
            continue
        result.append(m.strip())
    
    return result


def is_known(name, name_clean, known_tickers, known_names_lower):
    """檢查是否為已知標的（在 catalyst_fetch 字典裡）"""
    # 直接 ticker match
    if name.upper() in known_tickers:
        return True
    # 全名 match
    if name in KNOWN_COMPANY_NAMES:
        return True
    # 小寫 match
    if name_clean in known_names_lower:
        return True
    # 部分 match（"Apple Inc" 應該被 "Apple" 抓到）
    for known in KNOWN_COMPANY_NAMES:
        if known.lower() in name.lower() or name.lower() in known.lower():
            if len(known) > 3 and len(name) > 3:
                return True
    return False


def fetch_news():
    """抓所有 RSS feed 的新聞標題 + 摘要"""
    all_text = []
    for url in RSS_FEEDS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            feed = feedparser.parse(r.content)
            for entry in feed.entries[:50]:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                if title:
                    all_text.append({'title': title, 'summary': summary[:300]})
        except Exception as e:
            print(f"⚠️ {url} 失敗：{e}")
    return all_text


def load_history():
    """讀取連續出現天數的累積紀錄"""
    if not os.path.exists(HISTORY_PATH):
        return {}
    try:
        with open(HISTORY_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def save_history(history):
    """寫回歷史，淘汰 7 天沒出現的"""
    today = datetime.now().date().isoformat()
    cutoff = (datetime.now() - timedelta(days=7)).date().isoformat()
    
    # 淘汰 7 天前的紀錄
    cleaned = {}
    for name, info in history.items():
        last_seen = info.get('last_seen', '')
        if last_seen >= cutoff:
            cleaned[name] = info
    
    with open(HISTORY_PATH, 'w') as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)


def main():
    print(f"🛸 啟動 Unknown Radar: {datetime.now().strftime('%Y-%m-%d')}")
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # 1. 載入上市公司清單
    company_to_ticker = fetch_listed_companies()
    if not company_to_ticker:
        print("⚠️ 無法載入上市公司清單，盲點將無法對應 ticker（仍會記錄公司名）")
        company_to_ticker = {}
    
    # 已知公司名（小寫）用於快速 lookup
    known_names_lower = {clean_company_name(n) for n in KNOWN_COMPANY_NAMES}
    
    # 2. 抓新聞
    print("📰 抓 RSS 新聞...")
    news = fetch_news()
    print(f"   共 {len(news)} 則")
    
    # 3. 從每則新聞抽取公司名候選
    proper_nouns = Counter()
    name_evidence = {}  # 公司名 → [(新聞標題, ...), ...]
    
    for n in news:
        combined = n['title'] + ' ' + n['summary']
        candidates = extract_proper_nouns(combined)
        for c in candidates:
            proper_nouns[c] += 1
            if c not in name_evidence:
                name_evidence[c] = []
            if len(name_evidence[c]) < 3:
                name_evidence[c].append(n['title'][:100])
    
    print(f"   抽出 {len(proper_nouns)} 個專有名詞候選")
    
    # 4. 過濾「已知」標的
    unknowns = {}
    for name, count in proper_nouns.items():
        if count < MIN_MENTIONS_TODAY:
            continue
        
        name_clean = clean_company_name(name)
        if is_known(name, name_clean, KNOWN_TICKERS, known_names_lower):
            continue
        
        # 找對應 ticker
        ticker = None
        # 直接 lookup
        if name_clean in company_to_ticker:
            ticker = company_to_ticker[name_clean]
        else:
            # 模糊比對：去掉後綴
            for company_norm, t in company_to_ticker.items():
                if company_norm.startswith(name_clean) or name_clean.startswith(company_norm):
                    if len(company_norm) > 3:
                        ticker = t
                        break
        
        unknowns[name] = {
            'count': count,
            'ticker': ticker,
            'evidence': name_evidence.get(name, []),
        }
    
    # 5. 對照歷史，計算連續天數
    today = datetime.now().date().isoformat()
    history = load_history()
    
    for name, info in unknowns.items():
        if name in history:
            history[name]['consecutive_days'] = history[name].get('consecutive_days', 0) + 1
            history[name]['last_seen'] = today
            history[name]['total_mentions'] = history[name].get('total_mentions', 0) + info['count']
        else:
            history[name] = {
                'first_seen': today,
                'last_seen': today,
                'consecutive_days': 1,
                'total_mentions': info['count'],
                'ticker': info['ticker'],
            }
        
        # 從 history 補回 ticker（防止某天沒抓到）
        if not info.get('ticker') and history[name].get('ticker'):
            info['ticker'] = history[name]['ticker']
        info['consecutive_days'] = history[name]['consecutive_days']
        info['total_mentions'] = history[name]['total_mentions']
    
    # 6. 排序：連續天數 + 提及次數
    sorted_unknowns = sorted(
        unknowns.items(),
        key=lambda x: (
            x[1].get('consecutive_days', 0),
            x[1].get('total_mentions', 0),
        ),
        reverse=True,
    )
    
    # 7. 輸出
    top = sorted_unknowns[:MAX_OUTPUT]
    
    output = {
        'updated_at': datetime.now().isoformat(),
        'count': len(top),
        'blind_spots': [
            {
                'name': name,
                'ticker': info.get('ticker'),
                'mentions_today': info['count'],
                'total_mentions': info.get('total_mentions', info['count']),
                'consecutive_days': info.get('consecutive_days', 1),
                'is_strong': info.get('consecutive_days', 1) >= MIN_CONSECUTIVE_DAYS,
                'evidence': info.get('evidence', [])[:2],
            }
            for name, info in top
        ],
    }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    save_history(history)
    
    # 8. console 輸出
    if top:
        print(f"\n🛸 找到 {len(top)} 個盲點候選（新聞反覆出現但不在你字典裡）：")
        print()
        strong = [x for x in top if x[1].get('consecutive_days', 1) >= MIN_CONSECUTIVE_DAYS]
        new = [x for x in top if x[1].get('consecutive_days', 1) < MIN_CONSECUTIVE_DAYS]
        
        if strong:
            print(f"  🔴 連續 {MIN_CONSECUTIVE_DAYS}+ 天出現（強訊號）：")
            for name, info in strong[:5]:
                ticker_str = f"[{info['ticker']}]" if info.get('ticker') else "[私募/未上市?]"
                print(f"    {name} {ticker_str} — 連 {info['consecutive_days']} 天 / 累積 {info['total_mentions']} 次")
                if info.get('evidence'):
                    print(f"      e.g. {info['evidence'][0]}")
        
        if new:
            print(f"\n  🟡 今日新出現：")
            for name, info in new[:5]:
                ticker_str = f"[{info['ticker']}]" if info.get('ticker') else "[私募/未上市?]"
                print(f"    {name} {ticker_str} — {info['count']} 次")
    else:
        print("\n✅ 今日無盲點訊號")
    
    print(f"\n💾 已寫入 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
