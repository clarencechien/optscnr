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
import json
import os
from datetime import datetime, timezone

import spcx_common

SECTIONS = [
    (spcx_common.SPACE_RADAR_REPORT, "（space_radar 報告尚無輸出）"),
    (spcx_common.OPTIONS_REPORT, "（Option Sage 報告尚無輸出）"),
]
BRIEF_PATH = os.path.join(spcx_common.OUTPUT_DIR, "spcx_brief.json")
BRIEF_URL = "https://optscnr.ai-apps.work/brief?m=spcx"
LV_WORD = {"L2": "🟢 綠燈", "L1": "🟡 黃燈", "L0": "⚪ 灰燈"}


def read_or_none(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def c_pool_block():
    """C 池燈號一眼版（PLAN_2026-10_c_pool_alert）：讀 spcx_brief.py 組好的 JSON，零計算；缺檔就一行帶過。
    文案跟 /brief?m=spcx 同一套白話：綠燈／黃燈／灰燈、做／不做／再看。"""
    try:
        b = json.load(open(BRIEF_PATH, encoding="utf-8"))
    except Exception:
        return "## 🚦 C 池燈號\n\n_（spcx_brief.json 尚無輸出；排程跑完才有）_\n\n"
    c = b.get("c_pool") or {}
    r = c.get("response") or {}
    lv = c.get("level")
    md = "## 🚦 C 池燈號\n\n"
    head = f"**{LV_WORD.get(lv, '⚪ 沒資料')}（{lv or '—'}）**"
    if lv == "L2":
        head += f"，已經亮了 {c.get('l2_streak_days')} 天（{c.get('l2_start')} 起）"
    elif c.get("l2_days_since_close") is not None and c.get("l2_last_date"):
        head += f"，上次綠燈到 {c['l2_last_date']}（{c['l2_days_since_close']} 天前熄）"
    md += head + f"｜市場日 {b.get('market_date', '—')}｜用「{ {'near': '近月 IV', 'leaps': '長天期 IV', 'carry': '借錢成本'}.get(c.get('gate_mode'), c.get('gate_mode') or '—') }」這把尺\n\n"
    if b.get("do_line"):
        md += f"{b['do_line']}\n\n"
    if r.get("status") == "overdue":
        md += f"🔴 **你還沒回答**：{r.get('deadline')} 前該答，已經晚 {r.get('overdue_days')} 天。做、不做、再看，在 `config/spcx_c_decisions.json` 加一筆就好。\n\n"
    elif r.get("status") == "pending":
        md += f"⏳ **{r.get('deadline')} 前要回答**：做、不做、還是再看，寫進 `config/spcx_c_decisions.json`。\n\n"
    elif r.get("status") == "answered":
        last = r.get("last") or {}
        md += f"✅ 這段綠燈已回答：{last.get('date')} {last.get('action')}。\n\n"
    gates = c.get("gates") or {}
    tri = "／".join(f"{n} {LV_WORD.get((gates.get(k) or {}).get('level'), '—').split(' ')[-1]}" for k, n in (("near", "近月 IV"), ("leaps", "長天期 IV"), ("carry", "借錢成本")))
    md += f"三把尺各自的結果：{tri}（只有現在用的那把決定燈色）。\n\n"
    bad = [x for x in (b.get("checks") or []) if x.get("level") == "bad"]
    if bad:
        md += "⚠️ 資料有問題：" + "；".join(x.get("text", "") for x in bad) + "\n\n"
    md += (f"> 完整版（四個條件、三把尺、好買賣的合約、你的看法、資料健康）：[{BRIEF_URL}]({BRIEF_URL})｜"
           "燈亮後怎麼做：[PLAYBOOK.md「C 池 L2 回應 SOP」](PLAYBOOK.md)｜"
           "判定每天寫進 `output/spcx_options_history.csv`（level／transition／三把尺）｜轉換那天會推播一則（BentoDrop）\n\n")
    return md


def main():
    md = "# 🚀 SPCX 雷達站（space_radar + Option Sage）\n\n"
    md += f"_README 由 build_readme.py 於 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} 重組；"
    md += "C 池燈號來自 spcx_brief.json，兩個報告區塊各為該模組最近一次排程的輸出。_\n\n"
    md += "> 執行手冊：[PLAYBOOK.md](PLAYBOOK.md)｜8 月後任務計劃：[PLAN_2026-08.md](PLAN_2026-08.md)｜"
    md += "C 池管道（燈號／橫幅／推播／回應）：[PLAN_2026-10_c_pool_alert.md](PLAN_2026-10_c_pool_alert.md)｜"
    md += "手動維護檔在 `config/`（dca_log / viewpoint / spcx_config / **spcx_c_decisions**＝你的回答，只加不改）\n\n"
    md += "---\n\n"
    md += c_pool_block()
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
