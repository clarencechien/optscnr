"""
clean_stale_signals.py — 一次性腳本：清除「非交易日掃描」產生的污染信號

【為什麼可以刪（不違反 append-only）】
append-only 保護的是「當初的預測不被事後竄改」。但非交易日（美股週末/假日）
掃描產生的信號，是舊收盤資料的機械性重播（同一批異常換個日期再記一次），
它們從來不是新預測，是排程 bug 的副產品。移除它們是資料還原，不是竄改歷史。

【污染機制】（詳見 CONTEXT.md）
cron '0 22 * * 0-5' 含 UTC 週日 → 美股週末休市 → 該次掃描抓到的是
週五收盤殘留 → save_signal_snapshot 用新日期把舊異常再記一次 → 樣本灌水。
美股假日（如 2026-07-03）同理。

【做什麼】
掃 data/iv_log/signals_*.json，移除 snapshot_date 落在
「週六/週日 或 美股假日」的信號。冪等，跑幾次結果相同。

用法：python clean_stale_signals.py
跑完後：下次 shadow_tracer 執行時 SHADOWLOG 會自動用乾淨資料重生。
"""
import json
import os
from datetime import datetime
from glob import glob

IV_LOG_DIR = os.path.join("data", "iv_log")

# 2026 美股休市日（NYSE）。若跨年使用，補下一年清單。
US_MARKET_HOLIDAYS = {
    "2026-01-01",  # New Year's Day
    "2026-01-19",  # MLK Day
    "2026-02-16",  # Presidents' Day
    "2026-04-03",  # Good Friday
    "2026-05-25",  # Memorial Day
    "2026-06-19",  # Juneteenth
    "2026-07-03",  # Independence Day (observed, 7/4 落週六)
    "2026-09-07",  # Labor Day
    "2026-11-26",  # Thanksgiving
    "2026-12-25",  # Christmas
}


def is_non_trading_day(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return d.weekday() >= 5 or date_str in US_MARKET_HOLIDAYS


def main():
    files = sorted(glob(os.path.join(IV_LOG_DIR, "signals_*.json")))
    if not files:
        print("找不到 signals_*.json，結束。")
        return

    total_removed = 0
    for path in files:
        with open(path, encoding="utf-8") as f:
            signals = json.load(f)

        keep = [s for s in signals if not is_non_trading_day(s["snapshot_date"])]
        removed = [s for s in signals if is_non_trading_day(s["snapshot_date"])]

        if removed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(keep, f, ensure_ascii=False, indent=2)
            total_removed += len(removed)
            bad_dates = sorted({s["snapshot_date"] for s in removed})
            print(f"🧹 {os.path.basename(path)}: 保留 {len(keep)}、移除 {len(removed)} 筆"
                  f"（污染日期: {', '.join(bad_dates)}）")
        else:
            print(f"✅ {os.path.basename(path)}: {len(signals)} 筆全部乾淨，無需清理")

    print(f"\n完成。共移除 {total_removed} 筆非交易日污染信號。")
    if total_removed:
        print("下次 shadow_tracer 跑完，SHADOWLOG 會自動以乾淨資料重生。")


if __name__ == "__main__":
    main()
