"""
build_readme.py — 組合 space_radar + option sage 的最新輸出成 spcx_radar/README.md

定位：跟主 scanner 的 README.md 一樣，「資料夾首頁 = 最新報表」。
space_radar（A/B 池 + 階段機）與 spcx_options（Option Sage，C 池 gate）
每天依序跑完後呼叫本腳本重組 README。

設計原則：
- 純本地檔案組合，零網路、零計算
- 缺哪份輸出就標「尚無輸出」，不報錯（sage 可能 continue-on-error 掛掉，不該擋 README）
- 手冊：PLAYBOOK.md（執行手冊 v8.6.2）｜8 月後任務：PLAN_2026-08.md
"""
import os
from datetime import datetime, timezone

import spcx_common

SECTIONS = [
    (spcx_common.SPACE_RADAR_REPORT, "（space_radar 報告尚無輸出）"),
    (spcx_common.OPTIONS_REPORT, "（Option Sage 報告尚無輸出）"),
]


def read_or_none(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def main():
    md = "# 🚀 SPCX 雷達站（space_radar + Option Sage）\n\n"
    md += f"_README 由 build_readme.py 於 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} 重組；"
    md += "兩區塊各為該模組最近一次排程的輸出。_\n\n"
    md += "> 執行手冊：[PLAYBOOK.md](PLAYBOOK.md)｜8 月後任務計劃：[PLAN_2026-08.md](PLAN_2026-08.md)｜"
    md += "手動維護檔在 `config/`（dca_log / viewpoint / spcx_config）\n\n"
    md += "---\n\n"

    for path, placeholder in SECTIONS:
        content = read_or_none(path)
        if content:
            md += content + "\n\n---\n\n"
        else:
            md += f"_{placeholder}_\n\n---\n\n"

    with open(spcx_common.README_PATH, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"📝 已重組 {spcx_common.README_PATH}")


if __name__ == "__main__":
    main()
