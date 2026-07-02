"""
backfill_premium_tier.py — 一次性腳本：對歷史信號回填 premium_tier 貼標

【做什麼】
掃 data/iv_log/signals_*.json，對缺 premium_tier 欄位的信號，
按 entry_price 補上分級標籤（lottery <$1.5 / mid $1.5-3 / heavy >$3）。

【設計原則】
- 只補空缺欄位，不動任何既有資料（append-only 精神：不竄改歷史預測）
- 冪等：跑幾次結果都一樣，已有 tier 的跳過
- 跑完即可刪除本腳本（一次性工具）

用法：python backfill_premium_tier.py
"""
import json
import os
from glob import glob

IV_LOG_DIR = os.path.join("data", "iv_log")


def tier_of(price):
    if price < 1.5:
        return "lottery"
    elif price < 3.0:
        return "mid"
    return "heavy"


def main():
    files = sorted(glob(os.path.join(IV_LOG_DIR, "signals_*.json")))
    if not files:
        print("找不到任何 signals_*.json，結束。")
        return

    for path in files:
        with open(path, encoding="utf-8") as f:
            signals = json.load(f)

        patched = 0
        for s in signals:
            if "premium_tier" not in s:
                s["premium_tier"] = tier_of(float(s.get("entry_price", 0)))
                patched += 1

        if patched:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(signals, f, ensure_ascii=False, indent=2)

        print(f"{os.path.basename(path)}: 共 {len(signals)} 筆，補貼標 {patched} 筆")

    print("✅ 回填完成。此腳本為一次性工具，可刪除。")


if __name__ == "__main__":
    main()
