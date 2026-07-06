"""
backfill_news_at_signal.py — 一次性腳本：對歷史信號回填 news_at_signal 貼標

【做什麼】
掃 data/iv_log/signals_*.json，對缺 news_at_signal 欄位的信號，
從 git 歷史撈出「該 snapshot_date 當天的 data/catalyst_today.json 版本」，
比對標的是否在當天的公開新聞催化名單上：
  True  = 新聞點火型（新聞已公開、flow 確認有人押注）
  False = 純 flow 型（無新聞的沉默佈局，如 2026-06-26 的 ASTS）

【為什麼可以回填】
catalyst_fetch 每天 20:30 UTC commit 名單、scanner 22:00 才掃，
所以「信號日最後一版 catalyst_today.json」就是掃描當下看得到的名單，
git 歷史完整保存了每一天的版本——回填用的是當天就存在的公開資訊，
不是事後資訊，不違反 append-only 精神。

【設計原則】
- 只補空缺欄位，不動任何既有資料
- 冪等：已有 news_at_signal 的跳過
- 某天撈不到 catalyst 版本時跳過該筆（留空缺，不猜 False）
- 需在 git repo 內執行（依賴 git log / git show）

用法：python backfill_news_at_signal.py
"""
import json
import os
import subprocess
from glob import glob

IV_LOG_DIR = os.path.join("data", "iv_log")
CATALYST_PATH = "data/catalyst_today.json"


def catalyst_as_of(date_str, cache={}):
    """撈出 date_str 當天最後一版 catalyst_today.json 的標的集合；撈不到回 None。"""
    if date_str in cache:
        return cache[date_str]
    result = None
    try:
        commit = subprocess.run(
            ["git", "log", "-1", "--format=%H",
             f"--before={date_str}T23:59:59+00:00", "--", CATALYST_PATH],
            capture_output=True, text=True, check=True).stdout.strip()
        if commit:
            # 只採用「當天」的版本：太舊的名單不能代表信號日的新聞面
            commit_date = subprocess.run(
                ["git", "show", "-s", "--format=%cs", commit],
                capture_output=True, text=True, check=True).stdout.strip()
            if commit_date == date_str:
                raw = subprocess.run(
                    ["git", "show", f"{commit}:{CATALYST_PATH}"],
                    capture_output=True, text=True, check=True).stdout
                data = json.loads(raw)
                tickers = data if isinstance(data, list) else data.get("tickers", [])
                result = set(t if isinstance(t, str) else t.get("ticker", "") for t in tickers)
    except Exception as e:
        print(f"  ⚠️ {date_str} catalyst 版本撈取失敗：{e}")
    cache[date_str] = result
    return result


def main():
    files = sorted(glob(os.path.join(IV_LOG_DIR, "signals_*.json")))
    if not files:
        print("找不到 signals_*.json，結束。")
        return

    for path in files:
        with open(path, encoding="utf-8") as f:
            signals = json.load(f)

        patched, skipped = 0, 0
        for s in signals:
            if "news_at_signal" in s:
                continue
            cat = catalyst_as_of(s["snapshot_date"])
            if cat is None:
                skipped += 1  # 當天沒有 catalyst 版本 → 留空缺，不猜
                continue
            s["news_at_signal"] = s["ticker"] in cat
            patched += 1

        if patched:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(signals, f, ensure_ascii=False, indent=2)

        print(f"{os.path.basename(path)}: 共 {len(signals)} 筆，"
              f"補貼標 {patched} 筆" + (f"，無當日名單跳過 {skipped} 筆" if skipped else ""))

    print("✅ 回填完成。此腳本為一次性工具，可留檔供 schema 變更參考。")


if __name__ == "__main__":
    main()
