# dca_ledger — DCA 規則影子帳本 + tw_brief 週報

> 回答一個問題：**tw_scanner 的訊號，對「定期定額買 0050 的人」值多少？**
> 單位是你的錢（平均成本、XIRR），不是 TAIEX 20 日中位數。等額假設、不記真實部位、不記個人損益
>（CONTEXT.md 紅線 2 的界線說明）。非投資建議。

## 為什麼存在（2026-09-12）

tw_scanner 唯一可行動的輸出是投降警報，一年響幾次；其他 250 天是天氣描述。對 DCA 的人，這是用
日報的形式送年報的內容，所以每天打開都是「無」。帳本把它換成三個能行動的東西：

1. **本週機械指示**（週檢查・月預算）：每週五收盤後看一次，本週有警報且本月預算未動 → 下一交易日投入 ×2，
   當月不再行動；到當月最後決策週仍未動 → 例行投入。使用者 2026-09-12 拍板「每月太長、改每週 update、
   當週行動當月不再行動」。
2. **五條規則的成績單**（2019 起）：純 DCA／週檢查／投降窗加碼／鋒面調節／一次投入對照。
3. **每筆加碼的 edge**：跟「同一筆錢等到下一個例行買日再買」比，正 = 警報日買比較便宜；另看 T+60。

## 規則（config `dca_ledger_config.json`；改參數＝新實驗）

| 規則 | 定義 | 資金 |
|---|---|---|
| plain | 每月 `buy_day_of_month` 日（含）後首個交易日買 `amount_twd` | 月預算 |
| weekly_gate | 每週 `decision_weekday`（預設五）決策：本週有 capitulation 且本月未動 → 翌日 ×`multiplier`；當月最後決策週仍未動 → 翌日 ×1 | 月預算換時點；×2 的另一半是額外資金 |
| capitulation_boost | plain ＋ 警報簇首日翌日加買 (m−1)×amount（同簇 5 個交易日內只一次） | 額外資金 |
| regime_scaled | plain × 鋒面倍數（CAPITULATION 2、DE_RISK 1.5、OVERHEAT 0.5） | 假說，預期無效 |
| lump_sum | plain 總投入第一個買日一次投入 | 對照，不是策略 |

執行價一律用收盤：例行買日當日收盤（排程無資訊）、警報翌日收盤（警報是收盤後才知道）。
手續費只算買進（折扣後 0.0855%）；零股允許小數單位。

## 判準（先寫死，防捨不得）

- 投降窗規則（weekly_gate 與 capitulation_boost）：≥ 8 簇上 edge 均值 > 0 且勝率 ≥ 60% 才算「有東西」；
  否則它只是「早幾天買」的噪音。
- 鋒面調節：平均成本不優於純 DCA → 處決（同 tw_scanner overheat 前例，屍體留 config）。
- 每月 1 日的 backtest 排程重審一次。

## 資料與檔案

```
tw_scanner.py --briefing   → output/tw_scanner_history.json   2019 起每日 regime/score/alerts/分位（帳本回測用；每晚重寫）
tw_scanner.py --backtest   → output/tw_scanner_backtest.json   警報戰績（週報讀）
dca_ledger.py              → output/dca_prices.json            0050 收盤（FinMind 增量快取，進版控）
                           → output/dca_ledger.json / .md      帳本（每晚重算）
tw_brief.py                → output/tw_brief.json / tw_weekly.md   週報（Worker /api/tw 與 README 頂部）
```

排程：`tw_scanner.yml` 簡報後接著跑 ledger + brief；`delta_radar.yml` 跑完也重組 brief。
**首跑要在能連 FinMind 的環境**（Actions 即可）：沒有價格快取時帳本輸出 NO_DATA，不崩潰。

## 操作

```bash
python tw_scanner/dca_ledger.py --output-dir tw_scanner/output      # 抓價 + 重算
python tw_scanner/dca_ledger.py --no-fetch --output-dir tw_scanner/output   # 離線
python tw_scanner/dca_ledger.py --selftest
python tw_scanner/tw_brief.py --output-dir tw_scanner/output
python tw_scanner/tw_brief.py --selftest
```

## 已知限制

1. 0050 除息：用還原前收盤，DCA 報酬少算配息（約 3–4%/年）；規則之間比較不受影響（同一序列）。
2. weekly_gate 的「本週警報」用歷史序列的 `alerts` 判斷，跟 21:45 排程的簡報同源；日間手動跑是 3/4 特徵，
   警報可能晚一天出現。
3. `tw_scanner_history.json` 是推導物（cache CSV + config 重算），不是 append-only 狀態；config 改了序列會變，
   帳本跟著變——這是刻意的（改參數＝新實驗），舊結果在 git 歷史。

## 賭場 sector（casino_tracker.py，2026-09-12）

**定位：拉斯維加斯小部位。先收資料、不做規則、不宣稱期望值。** 名單（config `casino_config.json`
`universe`）是人挑的台股 AI 供應鏈，零股可買，`in_0050` 是人工標記。它做三件事，全部只記錄：

1. 每交易日每檔記特徵：收盤、20 日報酬、對 0050 超額、月營收 YoY／3 月均／斜率（台灣月營收強制公告
   是唯一結構性資訊優勢，同 delta_radar M6）。
2. 回填 T+5/10/20 個股報酬與對 0050 超額（`casino_state.json` append-only）。
3. 影子 DCA：每月固定金額等權買整籃，同一筆錢對照買 0050。

判準（config `verdict_rule`，先寫死）：籃子 DCA 對 0050 至少 12 個月；「月營收加速前三分之一 vs 後三分之一」
的 T+20 超額各 n≥30 才准下結論。之前報告一律「累積中」。**這不是 DCA 的一部分，是娛樂預算的記帳。**

```bash
python tw_scanner/casino_tracker.py --output-dir tw_scanner/output   # 抓價/營收 → 掃描 → 回填 → 報告
python tw_scanner/casino_tracker.py --selftest
```
輸出：`casino_report.md`、`casino_brief.json`（週報第 4 節讀）、`casino_state.json`、`casino_prices.json`、`casino_revenue.json`。
