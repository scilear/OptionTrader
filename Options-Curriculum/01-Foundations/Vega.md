---
title: Vega
tags: [greeks, volatility, option-pricing, risk-management]
aliases: [vega-sensitivity, iv-duration, option-convexity]
status: draft
related:
  - "[[IV-Rank]]"
  - "[[IV-vs-HV]]"
  - "[[High-IV-Playbook]]"
  - "[[Low-IV-Playbook]]"
  - "[[Greeks-Overview]]"
  - "[[Greeks-Delta]]"
  - "[[Greeks-Gamma]]"
---

# Vega

**Vega** measures the sensitivity of an option's price to a 1 percentage-point change in **implied volatility (IV)**. It quantifies directional exposure to volatility moves independent of the underlying's price direction.

## Definition

For a single option:
- **Vega = ∂Price / ∂IV**
- Unit: Price change per 1 ppt IV move (e.g., vega of +0.05 means the option gains $0.05 if IV rises 1%)

For a position:
- **Position Vega = Sum of all leg vegas**, weighted by contract count and direction
- Long call or put: positive vega (benefits from IV expansion)
- Short call or put: negative vega (hurts from IV expansion)

Vega typically peaks **at-the-money (ATM)** and near **60 days to expiration (DTE)**, where options are most sensitive to volatility swings.

> [!note]
> Vega is sometimes called the "IV duration" of the option portfolio — analogous to how bond duration measures interest-rate sensitivity.

## Long Vega: Buying Volatility

When you **own options** (long call, long put, or spreads that net-long vega), you are **long vega**. Your position profits if IV expands:

- **Scenario**: Buy 1 SPX call. Call IV at 18%. IV rises to 20%.
  - Vega effect: +0.05 per contract = option gains $500 (at vega of 50), independent of SPX move
  - Net position P&L = Delta P&L (spot move) + Vega P&L (IV expansion) + Theta P&L (time decay)

**Long vega is profitable when:**
- Market expects volatility to rise (macroeconomic uncertainty, earnings, Fed announcements)
- IV is historically low relative to realized volatility (RV) → IV expansion likely
- IV rank is **very low** (< 20% — see [[IV-Rank]])

> [!tip]
> Long vega positions benefit from **straddles, strangles, and calendar spreads** in low-IV environments. Buy these structures when IV rank < 20% to capture mean reversion upward.

## Short Vega: Selling Volatility

When you **sell options** (short call, short put, or spreads that net-short vega), you are **short vega**. Your position loses if IV expands:

- **Scenario**: Sell 1 SPX call. Call IV at 20%. IV rises to 22%.
  - Vega effect: −0.05 per contract = option loses $500 (at vega of 50)
  - Your short position now underwater purely from IV expansion

**Short vega is profitable when:**
- IV is historically elevated relative to realized volatility (RV) → mean reversion favors IV contraction
- Market expects volatility to fall (post-crisis normalization, tail risk priced in)
- IV rank is **elevated** (> 30–40%)

> [!warning]
> Short vega positions are **negatively convex to volatility shocks**. A tail-risk event (flash crash, geopolitical shock) can spike IV 20+ ppts in minutes, causing catastrophic losses on short-vega portfolios. The 2020 VIX spike and March 2023 SVB crisis exemplify this tail risk.

> [!danger]
> Never short vega in **low-IV environments** (IV rank < 30%). You sacrifice all positive edge: theta decay is tiny, realized volatility will likely exceed sold IV, and tail risk is asymmetric. This is a beginner mistake that bankrupts many retail traders.

## IV Rank: The Edge Signal

[[IV-Rank]] is the percentile of current IV relative to 52-week history:
- **IV Rank > 50%**: Volatility is elevated historically → sell premium (short vega)
- **IV Rank 20–50%**: Neutral zone → delta-directional strategies preferred
- **IV Rank < 20%**: Volatility is depressed historically → buy premium (long vega)

**Tested rule of thumb** (from backtests on SPX, QQQ, IWM):
- **Sell premium when IV rank > 30–40%** → Positive theta decay + IV mean reversion outweigh vega risk
- **Buy premium when IV rank < 20%** → Potential IV expansion offsets theta drain

See [[IV-vs-HV]] for the mechanics of when IV reverts to realized volatility.

## Practical Vega Management

1. **Measure vega daily**: Track position-level vega in your broker or backtest tool. Know your net vega exposure.
2. **Cap vega per position**: High vega (> 100) concentrates volatility risk. Rebalance frequently.
3. **Pair vega with delta**: Vega P&L is real but often dwarfed by delta P&L on large spot moves. Size vega positions to your directional conviction.
4. **Use [[High-IV-Playbook]] and [[Low-IV-Playbook]]** for regime-based structure selection.

> [!note]
> Vega interacts with **gamma**: long gamma (long options) often comes bundled with long vega. See [[Greeks-Gamma]] for portfolio convexity.

---

**Related Greeks:** [[Greeks-Delta]], [[Greeks-Gamma]], [[Greeks-Theta]], [[Greeks-Rho]]
