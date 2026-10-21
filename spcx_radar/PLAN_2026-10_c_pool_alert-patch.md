# PLAN_2026-10_c_pool_alert — patch 1：gate 換量 LEAPS 保費（config 驅動，預設不變）

> 接在 `PLAN_2026-10_c_pool_alert.md` 之後做；不改該 handoff 已定的管道工作（橫幅／分頁／推播／decisions），只加一塊。
> 做完原 handoff 的步驟 1（`level`/`transition` 進 history）之後再做這份；本 patch 的歷史回填依賴那一步。

---

## 〇、為什麼要補這一塊（原 handoff 寫完才算出來的事實）

原 handoff 第一節第 4 條寫「不改 gate 的任何閾值」，理由是 55% 絕對線可達。可達是真的，但接著算六週窗口的損益時發現一件更根本的事：

從 Sage 每天 commit 的 `spcx_options.json` 抽 2028-12-15 $100C 的 bid/ask（窗口內資料最完整的深價內 LEAPS）：

| 日期 | 股價 | 近月 ATM IV | LEAPS IV（`leaps_atm_iv`） | $100C mid | 外在價值 |
|---|---|---|---|---|---|
| 09/24 | $154.72 | 50% | 60.6% | 74.80 | 20.08 |
| 09/29 | $145.47 | 47% | 60.5% | 71.58 | 26.10 |
| 10/01 | $149.24 | 44% | 60.3% | 76.28 | 27.03 |
| 10/14 | $163.42 | 48% | 61.0% | 80.60 | 17.18 |
| 10/20 | $147.96 | 66% | 59.5% | 72.62 | 24.66 |

近月 ATM IV 從 43% 跑到 66%，**LEAPS 自己的 IV 整段 59–61%，沒動**；外在價值的變化只是 theta。
意思是：Sage 六週亮 L2，是因為「近月 IV 冷了」，但 C 池要買的那張東西根本沒變便宜。gate 量的是 B，你買的是 A。
損益也對得上：窗口內任一天進場、以 10/20 bid 計，都在 0 到 -7% 之間，跟直接持股無差。

這不是閾值問題，是量錯尺。但 LEAPS IV 的序列只有 60 多天，現在就換主門是在資料不足時賭新門檻——所以做成 config 切換、三條線並算，12/9 復盤時用累積的歷史選。

---

## 一、設計決策

1. **三種 gate 模式同時算、同時記進 history，判定只看 config 指的那一個。** 預設 `near`（＝現狀），行為零改變；12/9 改一行 config 切換。
2. 模式：
   - `near`：現狀。近月 ATM IV 的相對分位 ≤ `opt_iv_pctile_calm` 且連續 `opt_iv_stable_days` 天、絕對值 ≤ `opt_iv_abs_acceptable`。
   - `leaps`：同一套邏輯，輸入換成 `leaps_atm_iv`（Sage 已在記，取最長天期 ATM）；分位對 history 的 `leaps_atm_iv` 序列算。閾值獨立：`opt_leaps_iv_pctile_calm`、`opt_leaps_iv_abs_acceptable`。
   - `carry`：對 `liquidity.detail` 裡 `moneyness ≤ opt_deep_itm_moneyness` 的 strike，算 `carry_pct_annual = (mid − intrinsic) / price / (DTE/365) × 100`，取最小值；gate ＝ 最小值 ≤ `opt_max_carry_pct` 且連續 `opt_iv_stable_days` 天。這條直接量「用 LEAPS 借錢持股的隱含年利率」，拿來跟 SGOV 殖利率或融資利率比。
3. **流動性、觀點兩條件不變**，三種模式只替換「IV 相對冷卻且穩定」＋「IV 絕對可接受」那兩條。
4. 報告並列三條線的當日判定（各自 ✅/❌），讓人一眼看到「近月說綠、LEAPS 說紅」這種分歧；分歧本身就是 12/9 要看的證據。

---

## 二、config（`spcx_radar/config/spcx_config.json`）新增

```json
"opt_gate_mode": "near",
"opt_leaps_iv_pctile_calm": 40,
"opt_leaps_iv_abs_acceptable": 0.55,
"opt_max_carry_pct": 5.0,
"_gate_mode_note": "near=近月ATM IV(現狀) / leaps=LEAPS IV / carry=深價內LEAPS外在價值年化%。三條線都算都記，只有這個決定 L2。12/9 復盤用 history 選。"
```

`opt_leaps_iv_abs_acceptable` 先沿用 0.55（嚴起點；資料顯示 LEAPS IV 常態 60%，這條線在切換前就會被 12/9 的資料校準）。`opt_max_carry_pct` 5.0 是嚴起點（10/20 實測 7.7%）。

---

## 三、`spcx_options.py` 改動

### 3.1 `get_iv_signal()` 泛化

拆成 `_iv_gate(series_col, current_iv, pctile_calm, abs_ok, stable_days)`：輸入「history 的哪一欄、當前值、兩個閾值」，回傳同形狀的 dict（`pctile / rel_calm / abs_acceptable / stable / n_samples`）。
- `near`：`series_col='atm_iv'`，來源仍是 space_radar 的 `spcx_iv_history.csv`（唯讀，不變）。
- `leaps`：`series_col='leaps_atm_iv'`，來源是 Sage 自己的 `spcx_options_history.csv`。

### 3.2 新增 `get_carry_signal(liq_sig, price, market_date)`

- 對 `liq_sig['detail']` 每筆算 `dte`（exp − market_date）、`intrinsic = max(price − strike, 0)`、`mid`、`extrinsic`、`carry_pct_annual`。
- 回傳 `{'min_carry_pct': …, 'best_strike': {...}, 'ok': min ≤ opt_max_carry_pct, 'stable': 最近 N 天 ok}`。穩定性用 history 新欄 `min_carry_pct`。
- 注意 `detail` 現在只存價差最窄前 5 名（`[:5]`）；carry 要看全部深價內可用 strike，所以 `get_liquidity_signal` 另存一份完整的 `usable_all`（不進報告，只給 carry 用）。

### 3.3 `evaluate_action_level()` 吃 `gate_mode`

```python
gates = {
  'near':  (iv_near['rel_calm'] and iv_near['stable'], iv_near['abs_acceptable']),
  'leaps': (iv_leaps['rel_calm'] and iv_leaps['stable'], iv_leaps['abs_acceptable']),
  'carry': (carry['stable'], carry['ok']),
}
c1, c2 = gates[GATE_MODE]
```
其餘（c3 流動性、c4 觀點、L0/L1/L2 分支）不動。`conditions` dict 的前兩個 key 名改成帶模式的，例如 `'IV 相對冷卻且穩定（near）'`，報告才看得出用的是哪條。

### 3.4 history 新欄

`record_options_history()` 加：`leaps_pctile`、`leaps_rel_calm`、`leaps_abs_ok`、`leaps_stable`、`min_carry_pct`、`carry_ok`、`carry_stable`、`gate_mode`、`level_near`、`level_leaps`、`level_carry`（三種模式各自會給的 level，不管 config 指哪個）。
最後三欄是 12/9 的關鍵：直接 `groupby` 就能看三條線各亮了幾天、分歧在哪。

### 3.5 回填

原 handoff 的 `backfill_level.py` 延伸：對 history 每一列同時回填 `level_near / level_leaps`（`leaps_atm_iv` 從 Sage 上線起就有）；`level_carry` 用 git 歷史裡每日 `spcx_options.json` 的 `liquidity.detail` 回填（`git log -- spcx_radar/output/spcx_options.json` 逐 commit `git show`），detail 只有前 5 名、仍可算最小 carry 的近似值，標 `carry_backfill_approx=true`。
驗收：回填後 `level_leaps=='L2'` 的天數應接近 0（LEAPS IV 整段 ~60% > 0.55），`level_near=='L2'` 約 21 天——兩條線的分歧就是這份 patch 存在的理由，回填出來應該肉眼可見。

### 3.6 報告（`generate_report`）

「三結構訊號」段的 IV 一行改成三行並列：
```
- IV 水位（near｜現行 gate）：66%｜分位 51｜相對冷卻 ❌ 絕對 ❌ 穩定 ❌
- LEAPS IV（leaps）：59.5%｜分位 38｜相對冷卻 ✅ 絕對 ❌ 穩定 ❌
- 隱含融資成本（carry）：7.7%/年（2028-12 $100C）｜門檻 5.0%｜❌
```
本回合判定標題加 `（gate: near）`。

---

## 四、brief / dashboard 連動（對原 handoff 的小改）

- `spcx_brief.json` 的 `c_pool` 加 `gate_mode` 與 `gates: { near: {...}, leaps: {...}, carry: {...} }`（各含 ok/level）。
- `/brief?m=spcx` 第 2 段「IV 雙軌」改名「三條 gate 線」，三行並列；哪一條是現行 gate 加粗。
- 橫幅與推播**只看 `level`（＝現行 gate 的結果）**，不因為其他兩條線變化而觸發——避免切換前就開始吵。

---

## 五、不做的事

- 不改預設：`opt_gate_mode` 出廠是 `near`，這份 patch 合進去那天 Sage 的 L0/L1/L2 不會變。
- 不在 12/9 前切換模式，即使 `leaps` 或 `carry` 看起來更合理——等 history 累積到能比。
- 不改流動性、觀點兩條件。
- 不把 carry 算進橫幅／推播的觸發條件。

## 六、驗收

1. `opt_gate_mode=near` 跑一次：`level` 與 patch 前完全相同；history 多出的欄位有值。
2. 手動把 config 改 `leaps` 跑一次：`level` 應為 L1（LEAPS IV 59.5% > 0.55）；改回 `near`。
3. 改 `carry` 跑一次：報告顯示最小 carry 與對應 strike；10/20 資料應為 7.7% 附近、❌。
4. 回填後 `python -c "import pandas as pd; h=pd.read_csv('spcx_radar/output/spcx_options_history.csv'); print(h[['level_near','level_leaps','level_carry']].apply(lambda s:(s=='L2').sum()))"` → near ≈ 21、leaps ≈ 0、carry 視門檻。
5. `/brief?m=spcx` 三條線並列、現行那條加粗；橫幅行為不變。

## 七、估時

| 步 | 內容 | 估時 |
|---|---|---|
| 1 | config + `_iv_gate` 泛化 + `get_carry_signal` | 1 h |
| 2 | `evaluate_action_level` 吃 mode + history 新欄 + 報告三行 | 45 min |
| 3 | 回填延伸（含 git 抽 detail） | 45 min |
| 4 | brief 連動 | 30 min |
| 5 | 驗收 1–5 | 30 min |

---

_12/9 復盤時要回答的問題，資料到時候都在 history：三條線各亮了幾天？分歧的日子，事後哪一條跟「你真正付的保費」對得上？選一條，改一行 config。_
