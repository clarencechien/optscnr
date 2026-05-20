"""
catalyst_fetch v6 — 大幅擴充 TICKER_MAP，涵蓋小盤股題材

【v6 改動】
- TICKER_MAP 從 ~90 檔擴充到 ~150 檔
- 補齊：3D 列印 / 量子 / 太空衛星 / 鈾礦核能 / EV 充電 / 加密礦企
- 重點新增：VELO, FLNC, RGTI, QBTS, BKSY, LEU, MARA, CHPT 等
- 改善 watch_only 涵蓋
"""
import requests
import xml.etree.ElementTree as ET
import json
import os
import re
from datetime import datetime
from collections import Counter

OUTPUT_PATH = "data/catalyst_today.json"
MAX_TICKERS = 20

# === Ticker ↔ 公司名/別名 映射（v6 大幅擴充）===
TICKER_MAP = {
    # === 大盤科技 ===
    'AAPL':  ('Apple', ['iPhone maker', 'Cupertino']),
    'MSFT':  ('Microsoft', []),
    'GOOG':  ('Alphabet', ['Google']),
    'GOOGL': ('Alphabet', ['Google']),
    'META':  ('Meta', ['Facebook', 'Instagram', 'WhatsApp']),
    'NVDA':  ('Nvidia', []),
    'AMZN':  ('Amazon', []),
    'TSLA':  ('Tesla', []),
    'NFLX':  ('Netflix', []),
    # === 半導體 ===
    'INTC':  ('Intel', []),
    'AMD':   ('AMD', ['Advanced Micro Devices']),
    'TSM':   ('TSMC', ['Taiwan Semiconductor']),
    'AVGO':  ('Broadcom', []),
    'QCOM':  ('Qualcomm', []),
    'MU':    ('Micron', []),
    'AMAT':  ('Applied Materials', []),
    'LRCX':  ('Lam Research', []),
    'KLAC':  ('KLA', []),
    'ASML':  ('ASML', []),
    'MRVL':  ('Marvell', []),
    'ARM':   ('Arm Holdings', []),
    'SMCI':  ('Super Micro', ['Supermicro']),
    'WDC':   ('Western Digital', []),
    'STX':   ('Seagate', []),
    'SNDK':  ('SanDisk', []),
    'AEHR':  ('Aehr Test Systems', []),
    'AMBA':  ('Ambarella', []),
    # === 軟體 / 雲端 ===
    'CRM':   ('Salesforce', []),
    'ORCL':  ('Oracle', []),
    'IBM':   ('IBM', ['International Business Machines']),
    'NOW':   ('ServiceNow', []),
    'SNOW':  ('Snowflake', []),
    'PLTR':  ('Palantir', []),
    'NET':   ('Cloudflare', []),
    'DDOG':  ('Datadog', []),
    'CRWD':  ('CrowdStrike', []),
    'ZS':    ('Zscaler', []),
    'PANW':  ('Palo Alto Networks', []),
    'MDB':   ('MongoDB', []),
    # === 金融科技 / 加密 ===
    'COIN':  ('Coinbase', []),
    'HOOD':  ('Robinhood', []),
    'SOFI':  ('SoFi', []),
    'PYPL':  ('PayPal', []),
    'XYZ':   ('Block', ['Square']),
    'MSTR':  ('MicroStrategy', ['Strategy Inc']),
    'IBIT':  ('iShares Bitcoin', ['BlackRock Bitcoin']),
    'AFRM':  ('Affirm', []),
    'UPST':  ('Upstart', []),
    # === 加密礦企 ===
    'MARA':  ('Marathon Digital', []),
    'CLSK':  ('CleanSpark', []),
    'RIOT':  ('Riot Platforms', ['Riot Blockchain']),
    'HUT':   ('Hut 8', []),
    'BITF':  ('Bitfarms', []),
    'IREN':  ('Iris Energy', []),
    # === 電動車 ===
    'RIVN':  ('Rivian', []),
    'LCID':  ('Lucid', []),
    'F':     ('Ford', []),
    'GM':    ('General Motors', []),
    # === EV 充電 ===
    'CHPT':  ('ChargePoint', []),
    'EVGO':  ('EVgo', []),
    'BLNK':  ('Blink Charging', []),
    'WKHS':  ('Workhorse', []),
    # === 能源 / 公用 ===
    'VST':   ('Vistra', []),
    'CEG':   ('Constellation Energy', []),
    'NEE':   ('NextEra Energy', []),
    'NRG':   ('NRG Energy', []),
    # === 核能 / 鈾礦 ===
    'OKLO':  ('Oklo', []),
    'SMR':   ('NuScale', []),
    'NNE':   ('Nano Nuclear', []),
    'LEU':   ('Centrus Energy', []),
    'UEC':   ('Uranium Energy', []),
    'UUUU':  ('Energy Fuels', []),
    'CCJ':   ('Cameco', []),
    # === 儲能 / 替代能源 ===
    'FLNC':  ('Fluence Energy', ['Fluence']),
    'STEM':  ('Stem Inc', []),
    'PLUG':  ('Plug Power', []),
    'BLDP':  ('Ballard Power', []),
    'BE':    ('Bloom Energy', []),
    # === 太陽能 / 電力電子（SEDG 在做 AI data center power）===
    'SEDG':  ('SolarEdge', ['SolarEdge Technologies']),
    'ENPH':  ('Enphase', ['Enphase Energy']),
    'RUN':   ('Sunrun', []),
    'NOVA':  ('Sunnova', []),
    'FSLR':  ('First Solar', []),
    'NXT':   ('Nextracker', []),
    # === 3D 列印 / 工業 ===
    'VELO':  ('Velo3D', ['Velo 3D']),
    'DDD':   ('3D Systems', []),
    'SSYS':  ('Stratasys', []),
    'NNDM':  ('Nano Dimension', []),
    'PRLB':  ('Protolabs', []),
    # === 量子計算 ===
    'IONQ':  ('IonQ', []),
    'RGTI':  ('Rigetti', []),
    'QBTS':  ('D-Wave', ['D Wave']),
    # === 航太 / 國防 / 太空 ===
    'RKLB':  ('Rocket Lab', []),
    'ASTS':  ('AST SpaceMobile', []),
    'LUNR':  ('Intuitive Machines', []),
    'BKSY':  ('BlackSky', []),
    'IRDM':  ('Iridium', []),
    'SPIR':  ('Spire Global', []),
    'JOBY':  ('Joby Aviation', []),
    'ACHR':  ('Archer Aviation', []),
    'KTOS':  ('Kratos', []),
    'BA':    ('Boeing', []),
    'RTX':   ('RTX', ['Raytheon']),
    # === 生技 ===
    'CRSP':  ('CRISPR Therapeutics', ['CRISPR']),
    'NTLA':  ('Intellia', []),
    'BEAM':  ('Beam Therapeutics', []),
    'EDIT':  ('Editas Medicine', []),
    'HIMS':  ('Hims', ['Hims & Hers']),
    'TDOC':  ('Teladoc', []),
    'PFE':   ('Pfizer', []),
    'MRK':   ('Merck', []),
    'GILD':  ('Gilead', []),
    'MRNA':  ('Moderna', []),
    'VKTX':  ('Viking Therapeutics', []),
    'BMEA':  ('Biomea Fusion', []),
    'PACB':  ('Pacific Biosciences', ['PacBio']),
    # === AI / 雲端基礎設施 ===
    'NBIS':  ('Nebius', []),
    'CRWV':  ('CoreWeave', []),
    'SOUN':  ('SoundHound', []),
    'BBAI':  ('BigBear', []),
    # === 中型 / 轉機股 ===
    'DELL':  ('Dell', []),
    'HPE':   ('Hewlett Packard Enterprise', ['HPE']),
    'HPQ':   ('HP Inc', []),
    'WDAY':  ('Workday', []),
    'OKTA':  ('Okta', []),
    'TWLO':  ('Twilio', []),
    'TEAM':  ('Atlassian', []),
    # === 機器人 / 自動化 ===
    'SYM':   ('Symbotic', []),
    'PRCT':  ('PROCEPT BioRobotics', ['Procept']),
    'MNTS':  ('Momentus', []),
    # === 其他常見 ===
    'SHOP':  ('Shopify', []),
    'ANET':  ('Arista Networks', ['Arista']),
    'DKNG':  ('DraftKings', []),
    'OPEN':  ('Opendoor', []),
    'ROKU':  ('Roku', []),
    'U':     ('Unity Software', ['Unity Technologies']),
    'VRT':   ('Vertiv', []),
    'PATH':  ('UiPath', []),
    'DIS':   ('Disney', []),
    'NKE':   ('Nike', []),
    'SBUX':  ('Starbucks', []),
    'WMT':   ('Walmart', []),
    'TGT':   ('Target', []),
    'COST':  ('Costco', []),
    'GS':    ('Goldman Sachs', []),
    'MS':    ('Morgan Stanley', []),
    'JPM':   ('JPMorgan', ['JP Morgan']),
    'BAC':   ('Bank of America', []),
    'BRK-B': ('Berkshire Hathaway', ['Berkshire']),
    # === 礦業 / 商品 ===
    'GOLD':  ('Barrick', ['Barrick Gold']),
    'FCX':   ('Freeport-McMoRan', ['Freeport']),
    # === 防詐騙 / IoT ===
    'ONDS':  ('Ondas', []),
}

# 同義詞：給 watch_only 用
WATCH_ONLY_NAMES = {
    'Nintendo': 'Nintendo',
    'Cerebras': 'Cerebras (pre-IPO)',
    'Saudi Aramco': 'Saudi Aramco',
    'DeepSeek': 'DeepSeek (private)',
    'Stripe': 'Stripe (private)',
    'OpenAI': 'OpenAI (private)',
    'Anthropic': 'Anthropic (private)',
    'xAI': 'xAI (private)',
}

# === 催化劑關鍵字（v4 大幅擴充）===
CATALYST_KEYWORDS = {
    # ↑ 漲幅相關（每個都很常見，特別補）
    'surge': 'price_up',
    'surges': 'price_up',
    'surged': 'price_up',
    'soar': 'price_up',
    'soars': 'price_up',
    'soared': 'price_up',
    'jump': 'price_up',
    'jumps': 'price_up',
    'jumped': 'price_up',
    'rally': 'price_up',
    'rallies': 'price_up',
    'rallied': 'price_up',
    'rises': 'price_up',
    'rising': 'price_up',
    'climbs': 'price_up',
    'climbed': 'price_up',
    'gain': 'price_up',
    'gains': 'price_up',
    'gained': 'price_up',
    'skyrocket': 'price_up',
    'pops': 'price_up',
    'breakout': 'price_up',
    'record high': 'price_up',
    'all-time high': 'price_up',
    # ↓ 跌幅相關
    'plunge': 'price_down',
    'plunges': 'price_down',
    'plummet': 'price_down',
    'falls': 'price_down',
    'drops': 'price_down',
    'sinks': 'price_down',
    'crash': 'price_down',
    'tumbles': 'price_down',
    'collapse': 'price_down',
    # 業務 / 訂單
    'foundry': 'business',
    'design win': 'business',
    'chip contract': 'business',
    'wins contract': 'business',
    'wins deal': 'business',
    'wins order': 'business',
    'partnership': 'business',
    'partners with': 'business',
    'collaboration': 'business',
    'acquisition': 'business',
    'acquires': 'business',
    'merger': 'business',
    'buyout': 'business',
    'takeover': 'business',
    # 分析師
    'upgrade': 'analyst',
    'upgraded': 'analyst',
    'price target raised': 'analyst',
    'price target hike': 'analyst',
    'overweight': 'analyst',
    'buy rating': 'analyst',
    'downgrade': 'analyst_neg',
    'downgraded': 'analyst_neg',
    # 財報
    'beats earnings': 'earnings',
    'beats estimates': 'earnings',
    'tops estimates': 'earnings',
    'earnings beat': 'earnings',
    'earnings beats': 'earnings',
    'guidance raised': 'earnings',
    'raises guidance': 'earnings',
    'raises outlook': 'earnings',
    'record revenue': 'earnings',
    'misses estimates': 'earnings_neg',
    'earnings miss': 'earnings_neg',
    # 選擇權異動
    'unusual options': 'options',
    'unusual activity': 'options',
    'options volume': 'options',
    'short squeeze': 'options',
    'gamma squeeze': 'options',
    # 產品 / 技術
    'ai deal': 'product',
    'ai contract': 'product',
    'breakthrough': 'product',
    'launches': 'product',
    'unveils': 'product',
    'fda approval': 'product',
    'fda approves': 'product',
}

RSS_FEEDS = [
    'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'https://www.marketwatch.com/rss/topstories',
    'https://www.investing.com/rss/news_25.rss',
    'https://seekingalpha.com/market_currents.xml',
    'https://finance.yahoo.com/news/rssindex',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
}


def build_lookup_table():
    """公司名（小寫）→ ticker"""
    lookup = {}
    for ticker, (name, aliases) in TICKER_MAP.items():
        names = [name] + aliases
        for n in names:
            lookup[n.lower()] = ticker
    return lookup


COMPANY_LOOKUP = build_lookup_table()


def find_companies(text):
    """從文字中找公司名，回傳 set of tickers"""
    found = set()
    text_lower = text.lower()
    
    # 直接 ticker 格式（極少數）
    for p in [r'\(([A-Z]{2,5})\)', r'\$([A-Z]{2,5})\b',
              r'NYSE:\s*([A-Z]{2,5})', r'NASDAQ:\s*([A-Z]{2,5})']:
        for m in re.finditer(p, text):
            t = m.group(1).upper()
            if t in TICKER_MAP:
                found.add(t)
    
    # 公司名反查
    for name_lower, ticker in COMPANY_LOOKUP.items():
        pattern = r'\b' + re.escape(name_lower) + r'\b'
        if re.search(pattern, text_lower):
            found.add(ticker)
    return found


def find_catalysts(text):
    """從文字找催化劑詞，回傳 list of (keyword, category)
    
    用 word boundary 比對，避免 'against' 命中 'gain' 這種子字串誤判。
    """
    text_lower = text.lower()
    hits = []
    for kw, cat in CATALYST_KEYWORDS.items():
        # word boundary 比對：適用單詞、多詞（如 'wins contract'）、含連字號（如 'all-time high'）
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower):
            hits.append((kw, cat))
    return hits


def find_watch_only(text):
    """找非 TICKER_MAP 內的熱門名字（用 word boundary 避免誤判）"""
    found = set()
    text_lower = text.lower()
    for name, display in WATCH_ONLY_NAMES.items():
        pattern = r'\b' + re.escape(name.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.add(display)
    return found


def parse_rss(xml_text):
    items = []
    try:
        xml_text = re.sub(r'\sxmlns="[^"]+"', '', xml_text, count=1)
        root = ET.fromstring(xml_text)
        for item in root.iter('item'):
            items.append({
                'title': item.findtext('title') or '',
                'summary': item.findtext('description') or '',
            })
        for entry in root.iter('entry'):
            items.append({
                'title': entry.findtext('title') or '',
                'summary': entry.findtext('summary') or entry.findtext('content') or '',
            })
    except ET.ParseError as e:
        print(f"  ⚠️ XML 解析失敗：{e}")
    return items


def fetch_feed(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        items = parse_rss(res.text)
        print(f"  ✅ {url[:55]}... → {len(items)} 則")
        return items
    except Exception as e:
        print(f"  ⚠️ {url[:55]}... → {e}")
        return []


def main():
    print(f"📰 啟動 Catalyst Fetch v6: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📚 字典：{len(TICKER_MAP)} 檔 ticker / {len(CATALYST_KEYWORDS)} 個關鍵字\n")
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    ticker_scores = Counter()        # ticker → 總分
    ticker_evidence = {}             # ticker → [evidence]
    watch_only_counter = Counter()   # 非 ticker 熱門名字
    
    total_items = 0
    items_with_company = 0
    items_with_catalyst = 0
    items_both = 0
    
    for feed_url in RSS_FEEDS:
        items = fetch_feed(feed_url)
        total_items += len(items)
        
        for entry in items:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            text = title + ' ' + summary
            
            companies = find_companies(text)
            catalysts = find_catalysts(text)
            watch_only = find_watch_only(text)
            
            for wo in watch_only:
                watch_only_counter[wo] += 1
            
            if companies:
                items_with_company += 1
            if catalysts:
                items_with_catalyst += 1
            if companies and catalysts:
                items_both += 1
            
            # 計分邏輯：
            # - 公司 + 催化劑：高分（每個催化劑 +2）
            # - 只有公司：低分（+0.5），代表「有提到但不確定方向」
            for ticker in companies:
                if catalysts:
                    score = len(catalysts) * 2
                else:
                    score = 0.5
                
                ticker_scores[ticker] += score
                ticker_evidence.setdefault(ticker, []).append({
                    'title': title[:140],
                    'catalysts': [c[0] for c in catalysts[:5]],
                    'has_catalyst': bool(catalysts),
                })
    
    print(f"\n📊 統計：")
    print(f"  總新聞:           {total_items}")
    print(f"  含公司名:         {items_with_company}")
    print(f"  含催化劑詞:       {items_with_catalyst}")
    print(f"  兩者都有 (狙擊):  {items_both}")
    
    top_tickers = ticker_scores.most_common(MAX_TICKERS)
    
    output = {
        'updated_at': datetime.now().isoformat(),
        'stats': {
            'total_items': total_items,
            'items_with_company': items_with_company,
            'items_with_catalyst': items_with_catalyst,
            'items_both': items_both,
        },
        'count': len(top_tickers),
        'tickers': [t for t, _ in top_tickers],
        'details': [
            {
                'symbol': t,
                'score': round(score, 1),
                'evidence': ticker_evidence[t][:3],
            }
            for t, score in top_tickers
        ],
        'watch_only': dict(watch_only_counter.most_common(10)),  # 非 ticker 但值得關注
    }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    if top_tickers:
        print(f"\n✅ 今日催化劑股 ({len(top_tickers)} 檔)：")
        for t, score in top_tickers[:10]:
            evi = ticker_evidence[t][0]
            tag = "🎯" if evi['has_catalyst'] else "👀"
            print(f"  {tag} {t} ({score:.1f}): {evi['title'][:90]}")
            if evi['catalysts']:
                print(f"      催化劑: {evi['catalysts']}")
    
    if watch_only_counter:
        print(f"\n📌 字典外熱門名字 (不在 TICKER_MAP)：")
        for name, count in watch_only_counter.most_common(5):
            print(f"  {name} ({count}x)")
    
    print(f"\n💾 已寫入 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
