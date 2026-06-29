# Delta Radar (2308.TW) — 2026-06-29 08:30 UTC

## 總判定：🟡 YELLOW

GS 4500 劇本三大未驗證前提的機械化監控：FCF 轉回 (M2)、合約負債續航 (M2)、
實體出貨上船 (M3/M4)，外加營收動能 (M1) 與敘事風險 (M5)。

| 模組 | 狀態 | 摘要 |
|---|---|---|
| M1 revenue_acceleration | 🟢 GREEN | 2026-05 YoY +43.7%, slope +4.22pp/月, 連續減速 1 個月 |
| M2 bullwhip_health | 🟡 YELLOW | 合約負債 QoQ +7.4% / 存貨 QoQ +17.4% / FCF/淨利 0.43 |
| M3 thai_shadow | 🟢 GREEN | DELTA.BK 2026-03-31 營收 YoY +47.0%, GM 31.7% |
| M4 customs_flow | 🟢 GREEN | US 進口 HS850440 (TH+TW) 近3月 $1244.3M, YoY +49.9% |
| M5 narrative_triggers | 🟡 YELLOW | capex_cut:4 / vr300_delay:3 / debt_financed_capex:17 |

### M1 revenue_acceleration — 🟢 GREEN
```json
{
  "latest_month": "2026-05",
  "latest_yoy_pct": 43.7,
  "yoy_slope_pp_per_month": 4.22,
  "consecutive_decel_months": 1
}
```

### M2 bullwhip_health — 🟡 YELLOW
```json
{
  "as_of": "2026-03-31",
  "contract_liab_qoq_pct": 7.4,
  "inventory_qoq_pct": 17.4,
  "fcf_to_net_income": 0.43,
  "accounts_used": {
    "contract": "CurrentContractLiabilities",
    "inventory": "Inventories",
    "ocf": "CashFlowsFromOperatingActivities",
    "capex": "PropertyAndPlantAndEquipment",
    "net_income": "EquityAttributableToOwnersOfParent"
  }
}
```

### M3 thai_shadow — 🟢 GREEN
```json
{
  "latest_q": "2026-03-31",
  "rev_yoy_pct": 47.0,
  "gross_margin_pct": 31.7
}
```

### M4 customs_flow — 🟢 GREEN
```json
{
  "window": "2026-02..2026-04",
  "rolling_value_usd_m": 1244.3,
  "rolling_yoy_pct": 49.9
}
```

### M5 narrative_triggers — 🟡 YELLOW
```json
{
  "hits": {
    "capex_cut": 4,
    "vr300_delay": 3,
    "debt_financed_capex": 17
  }
}
```
- [capex_cut] Can Sovereign AI Buffer Nvidia Against a Potential Hyperscaler Slowdown? - Trefis
- [capex_cut] Is the AI CapEx Trade Cracking? 5 Stocks Most Exposed If OpenAI’s Slowdown Is Real - 24/7 Wall St.
- [capex_cut] AI Infrastructure Stocks See a Strategic Pause - Let's Data Science
- [vr300_delay] Nvidia's CoWoS supplies still secured, but Rubin delay issues crop up: KeyBanc (NVDA:NASDAQ) - Seeking Alpha
- [vr300_delay] [News] NVIDIA Reportedly Denies Rubin Delay as AMD MI450 Spurs Redesign Speculation - TrendForce
- [vr300_delay] NVIDIA Reportedly Won’t Launch the RTX 50 SUPER Series This Year; GeForce RTX 60 “Rubin” Also Delayed as Memory Shortage
- [debt_financed_capex] Oracle Logs Worst Week Since 2001 Dot-Com Bust as AI Debt Pile Alarms Investors - MLQ.ai
- [debt_financed_capex] Oracle's AI spending blows past estimates, raising worries over growing debt - Reuters
- [debt_financed_capex] AI infrastructure is soaring, but data centers are burning through cash and the debt bubble is starting to burst - Bitge

---
*delta_radar — optscnr radar family. Shadow-mode instrument: this is a measurement device, not a trade signal.*