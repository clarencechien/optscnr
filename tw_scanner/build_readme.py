"""
build_readme.py — 組合 tw_scanner + delta_radar 的最新輸出成 tw_scanner/README.md

定位：跟主 scanner 的 README.md 一樣，「資料夾首頁 = 最新報表」。
兩支雷達各自跑各自的排程（天氣台每晚 21:45、delta 週一/四全掃 + 每日敘事），
誰跑完誰呼叫本腳本重組 README——README 永遠呈現「兩邊各自最新一份」。

設計原則：
- 純本地檔案組合，零網路、零計算——雷達的邏輯留在雷達裡
- 缺哪份輸出就標「尚無輸出」，不報錯（兩支雷達獨立跑，先跑的那支不該等後跑的）
- 原維護文件改名為 MANUAL_tw_scanner.md / MANUAL_delta_radar.md（2026-07-31 整併）
"""
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output")
README_PATH = os.path.join(HERE, "README.md")

SECTIONS = [
    ("tw_scanner_briefing.md", "（天氣台今日簡報尚無輸出）"),
    ("delta_radar_report.md", "（delta radar 報告尚無輸出）"),
    ("tw_scanner_backtest.md", None),  # 回測是月更，缺了不用佔位
]


def read_or_none(name):
    path = os.path.join(OUT_DIR, name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def mtime_str(name):
    path = os.path.join(OUT_DIR, name)
    try:
        ts = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
        return ts.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return "—"


def main():
    md = "# 🇹🇼 台股雷達站（tw_scanner + delta_radar）\n\n"
    md += f"_README 由 build_readme.py 於 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} 重組；"
    md += "兩區塊各為該雷達最近一次排程的輸出，時間戳以區塊內為準。_\n\n"
    md += "> 維護文件：[MANUAL_tw_scanner.md](MANUAL_tw_scanner.md)｜"
    md += "[MANUAL_delta_radar.md](MANUAL_delta_radar.md)｜"
    md += "改進判準與覆核紀錄：[REVIEW_2026-07.md](REVIEW_2026-07.md)\n\n"
    md += "---\n\n"

    for name, placeholder in SECTIONS:
        content = read_or_none(name)
        if content:
            md += content + "\n\n---\n\n"
        elif placeholder:
            md += f"_{placeholder}_\n\n---\n\n"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"📝 已重組 {README_PATH}")


if __name__ == "__main__":
    main()
