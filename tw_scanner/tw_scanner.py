import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import warnings
warnings.filterwarnings('ignore')

# 1. 核心時區與時間設定（強制鎖定台北時間 UTC+8，防止 GitHub 伺服器 UTC 時區錯位）
tw_tz = timezone(timedelta(hours=8))
now_tw = datetime.now(tw_tz)

TODAY_STR = now_tw.strftime("%Y%m%d")       # 證交所 API 格式: 20260611
TODAY_STR_DASH = now_tw.strftime("%Y-%m-%d") # FinMind API 格式: 2026-06-11
TODAY_ROC = now_tw.strftime("%Y/%m/%d")     # 期交所 API 格式: 2026/06/11

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"📡 tw_scanner 啟動：開始索取台北時間 {TODAY_STR_DASH} 的官方盤後籌碼...")

# --- [第一層：現貨數據] ---
def get_official_spot():
    url = f"https://www.twse.com.tw/fund/BFI82U?response=json&dayDate={TODAY_STR}&type=day"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        data = res.json()
        if 'data' not in data or not data['data']: return None
            
        f_spot, t_spot, d_spot = 0, 0, 0
        for row in data['data']:
            name = row[0]
            diff_val = float(row[3].replace(',', '')) / 100000000
            if '外資' in name: f_spot += diff_val
            elif '投信' in name: t_spot += diff_val
            elif '自營商' in name: d_spot += diff_val
        return {"foreign": f_spot, "trust": t_spot, "dealer": d_spot}
    except Exception as e:
        print(f"現貨數據下載異常: {e}")
        return None

# --- [第二層：期貨數據] ---
def get_official_futures():
    url = f"https://www.taifex.com.tw/cht/3/futContractsDateDown?queryStartDate={TODAY_ROC}&queryEndDate={TODAY_ROC}&commodityId="
    try:
        try:
            df = pd.read_csv(url, storage_options={'User-Agent': HEADERS['User-Agent']}, encoding='big5')
        except:
            df = pd.read_csv(url, storage_options={'User-Agent': HEADERS['User-Agent']}, encoding='utf-8')
            
        if df.empty or len(df) < 5: return None
            
        contract_col = [c for c in df.columns if '契約' in c or '商品' in c][0]
        investor_col = [c for c in df.columns if '身份' in c][0]
        net_oi_col = [c for c in df.columns if '未平倉' in c and '淨額' in c and '口數' in c][0]
        df[net_oi_col] = pd.to_numeric(df[net_oi_col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        
        # 外資大台
        tx_mask = (df[contract_col].str.contains('TX|臺股期貨', na=False)) & (df[investor_col].str.contains('外資', na=False))
        tx_net = df[tx_mask][net_oi_col].sum()
        
        # 散戶小台 (三大法人合計之反向)
        mtx_mask = df[contract_col].str.contains('MTX|小型臺指', na=False)
        mtx_inst_net = df[mtx_mask][net_oi_col].sum()
        retail_mtx = mtx_inst_net * -1
        
        return {"tx_net": tx_net, "retail_mtx": retail_mtx}
    except Exception as e:
        print(f"期貨數據下載異常: {e}")
        return None

# --- [第三層：融資數據] ---
def get_margin_balance():
    url = "https://api.finmindtrade.com/api/v4/data"
    try:
        res = requests.get(url, params={"dataset": "TaiwanStockTotalMarginPurchaseShortSale", "start_date": TODAY_STR_DASH, "end_date": TODAY_STR_DASH}, timeout=15)
        data = res.json().get("data", [])
        if not data: return None
        df = pd.DataFrame(data)
        if 'TodayBalance' in df.columns and 'YesBalance' in df.columns:
            if 'name' in df.columns:
                df = df[df['name'].str.contains('融資', na=False)]
            return (df['TodayBalance'] - df['YesBalance']).sum()
        return None
    except Exception as e:
        print(f"融資數據下載異常: {e}")
        return None

# --- 執行數據搜集 ---
spot_data = get_official_spot()
futures_data = get_official_futures()
margin_diff = get_margin_balance()

# 檢查今日是否為休市日（若現貨與期貨皆空，則不更新報告，避免洗掉舊有重要報告）
if spot_data is None and futures_data is None:
    print(f"📢 台北時間 {TODAY_STR_DASH} 交易所查無資料，判定可能為週末或國定休市日，腳本安全退出。")
    sys.exit(0)

# --- 4. 編譯產生極致精美的 Markdown 報告 ---
md_content = f"""# 📊 台股籌碼 X 光機 盤後診斷報告

> 📅 **診斷日期**：{TODAY_STR_DASH}
> 🕒 **生成時間**：{now_tw.strftime("%H:%M:%S")} (台北時間 UTC+8)
> 🤖 **驅動引擎**：`tw_scanner` 自動化量化特徵核心

---

## 🩸 第一層：現貨市場 (誰在砸盤？誰在護盤？)
"""

if spot_data:
    md_content += f"""- **外資買賣超**： `{spot_data['foreign']:+.2f} 億元` {"🔴 (⚠️ 外資瘋狂提款中)" if spot_data['foreign'] < -150 else ("🟢 (🚀 外資全面回補)" if spot_data['foreign'] > 150 else "")}
- **投信買賣超**： `{spot_data['trust']:+.2f} 億元` {"🛡️ (投信動用鋼鐵護盤)" if spot_data['trust'] > 50 else ""}
- **自營商合計**： `{spot_data['dealer']:+.2f} 億元`
"""
else:
    md_content += "- ⚠️ 今日現貨官方數據尚未更新或抓取失敗。\n"

md_content += """
## 🔮 第二層：期貨市場 (主力的底牌 vs 散戶的燃料)
"""

if futures_data:
    md_content += f"""- **外資大台 (TX) 淨未平倉**： `{futures_data['tx_net']:+.0f} 口` {"🚨 (外資高空單壓境，波段風險極高)" if futures_data['tx_net'] < -25000 else ""}
- **散戶小台 (MTX) 淨未平倉**： `{futures_data['retail_mtx']:+.0f} 口`

### 💡 期貨微觀結構診斷：
"""
    if futures_data['retail_mtx'] > 8000:
        md_content += f"👉 **[系統警告]** 散戶小台多單水位高達 `{futures_data['retail_mtx']}` 口。市場呈現典型**「外資佈空、散戶接刀」**的反指標格局，大盤短線易跌難漲，切勿盲目摸底。\n"
    elif futures_data['retail_mtx'] < -8000:
        md_content += f"👉 **[系統通知]** 散戶情緒陷入極度恐慌，小台指淨空單達 `{futures_data['retail_mtx']}` 口。盤面隨時可能觸發法人的**「強制軋空行情」**，不宜過度追空。\n"
    else:
        md_content += "👉 當前散戶期貨多空情緒相對中性，結構盤整中。\n"
else:
    md_content += "- ⚠️ 今日期貨官方數據尚未更新或抓取失敗。\n"

md_content += """
## 🔥 第三層：散戶現貨動向 (大盤融資增減)
"""

if margin_diff is not None:
    margin_billion = margin_diff / 100000000  # 換算為億元（適用於FinMind新制單位）
    if abs(margin_billion) < 0.01: # 防範單位落差，若數值過小則直接印出原始值
        if margin_diff > 0:
            md_content += f"- **融資餘額變化**： `增加 (原始差值: {margin_diff:+.0f})` 📉 散戶在現貨持續逆勢接刀，籌碼結構紊亂。\n"
        else:
            md_content += f"- **融資餘額變化**： `減少 (原始差值: {margin_diff:+.0f})` 📈 散戶大舉停損斷頭，現貨籌碼加速沉澱。\n"
    else:
        if margin_billion > 0:
            md_content += f"- **融資餘額變化**： `增加 {margin_billion:+.2f} 億元` 📉 散戶現貨逆勢套牢，上檔壓力加重。\n"
        else:
            md_content += f"- **融資餘額變化**： `減少 {margin_billion:+.2f} 億元` 📈 散戶停損或融資斷頭出場，短線浮額清洗乾淨。\n"
else:
    md_content += "- **融資餘額**： ⏳ 21:30 執行時若官方未公布，請稍後手動觸發 Action 刷新數據。\n"

md_content += """
---
*聲明：本報告由開源量化模組自動生成，數據源直連交易所後台接口。報告內容僅供量化回測與學術探討，不構成任何主觀投資買賣建議。*
"""

# --- 5. 確保寫入目錄存在，並儲存 output.md ---
output_dir = os.path.dirname(__file__)
output_path = os.path.join(output_dir, "output.md")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"🎉 報告編譯成功！已成功寫入：{output_path}")
