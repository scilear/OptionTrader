# VIX Gate Fix Report

## What was fixed
- Corrected straddle VIX gate condition from `vix > 40` to `vix <= 40` in `src/strategy_sim/engine.py`.
- Put credit spread remains ungated by VIX (`gate_put_credit_spread: false`).

## Charts
- Corrected cumulative P&L chart: `artifacts/reports/pnl_corrected_spy_dia.png`
- Before vs after impact chart: `artifacts/reports/gate_fix_before_after.png`

## Core Numbers (Before vs After)

| Metric | Before Fix | After Fix | Delta |
|---|---:|---:|---:|
| Total trades | 188 | 346 | +158 |
| Short straddle trades | 10 | 168 | +158 |
| Put credit spread trades | 178 | 178 | +0 |
| Total realized P&L | 27539.76 | 28197.51 | +657.76 |
| Total daily P&L sum | 27052.11 | 27293.38 | +241.27 |

## Per-Symbol Realized P&L (SPY, DIA)

| Symbol | Before Fix | After Fix | Delta |
|---|---:|---:|---:|
| SPY | 13575.39 | 17965.98 | +4390.58 |
| DIA | 13964.36 | 10231.54 | -3732.83 |

## Trade Quality (After Fix)
- Overall win rate: 74.0%
- Short straddle win rate: 66.1%
- Put credit spread win rate: 81.5%

## Data Coverage Caveat
- IWM, QQQ, GLD still have no option-chain/vol-history rows in source data, so they produce no trades.
- That remains a data availability issue, not a strategy logic issue.
