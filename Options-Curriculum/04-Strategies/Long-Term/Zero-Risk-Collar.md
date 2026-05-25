---
title: Zero Risk Collar
tags:
  - strategy
  - collar
  - hedging
  - long-term
  - tax-efficient
  - stock-protection
aliases:
  - Zero Cost Collar
  - Costless Collar
status: draft
related:
  - "[[Advanced-Collar]]"
  - "[[Covered-Call]]"
  - "[[CSP-Cash-Secured-Put]]"
  - "[[LEAPS-Investing]]"
  - "[[Greeks-Delta]]"
  - "[[Rolling-Options]]"
---

# Zero Risk Collar

A Zero Risk Collar (also called a costless collar) is a hedging strategy applied to an existing stock position. You buy an OTM put for downside protection and simultaneously sell an OTM call to finance the put premium. When both legs cost exactly the same, the net premium is zero — hence the name.

> [!warning]
> Collars cap your upside — you will underperform if the stock rallies strongly. Selling the call surrenders all gains above the call strike for the duration of the trade. If you are bullish on the stock, this is a significant tradeoff.

## Construction

Assume you own 100 shares of a stock trading at $100.

| Leg | Action | Strike | Premium |
|-----|--------|--------|---------|
| Long put | Buy | $90 | −$3.00 |
| Short call | Sell | $110 | +$3.00 |
| **Net cost** | | | **$0.00** |

Your effective range becomes **$90–$110**:
- Below $90: the put pays out, limiting your loss to 10% from the current price.
- Between $90–$110: you hold the stock, gaining or losing normally within that band.
- Above $110: your gain is capped at 10%; the call buyer profits on any further upside.

![[pnl-zero-risk-collar.png]]

> [!note]
> The put and call do not need to be the same delta. You pick strikes that make the net premium equal to zero — a 20-delta put financed by a 30-delta call is perfectly valid. The asymmetry just changes the width of your protected range vs. your capped upside.

## When to Use

The collar is most valuable when:

1. **Large unrealized gains** — You hold a stock that has appreciated significantly and you cannot sell without triggering a large tax event (long-term capital gains, incentive stock options, etc.).
2. **Company stock concentration** — Employees holding restricted stock units (RSUs) or founder shares who need downside protection while lock-up or vesting constraints prevent a sale.
3. **Near a known event** — Earnings, M&A vote, or macro uncertainty where you want to define risk without liquidating.
4. **Bear market insurance** — You believe the broader market is overextended but still want equity exposure.

> [!tip]
> Rule of thumb: use a collar when the cost of being wrong (i.e., a 20–30% drawdown) exceeds the cost of giving up upside. For concentrated positions that represent more than 20% of net worth, a collar is often the right starting point before exploring more complex hedges like [[Advanced-Collar]].

## DTE Selection

**3–6 months** is the practical sweet spot:

- Too short (< 30 DTE): premium is thin; the protection period barely covers a market correction cycle.
- Too long (> 9 months, approaching LEAPS): put premiums get expensive relative to the call premium you can collect; the zero-cost condition becomes harder to satisfy without accepting a very tight range.

A 90–180 DTE collar gives you meaningful protection while keeping the strikes reasonably wide.

## Delta Matching and Strike Selection

Because the goal is zero net cost, strike selection is iterative:

1. Start with the put you want — typically the 20–30 delta put, which protects against a 10–15% decline.
2. Find the call strike whose premium exactly offsets the put cost. Use your broker's options chain sorted by premium, or an options calculator.
3. If the call strike that achieves zero cost feels too close (limiting upside excessively), consider buying a cheaper put (lower delta, further OTM) to widen the call strike.

[[Greeks-Delta]] are your navigation tool here, but the actual match is premium-dollar-based, not delta-based.

## Tax Considerations

> [!note]
> This note contains general educational information, not tax advice. Consult a qualified tax professional before implementing collars on long-term holdings.

For U.S. investors, collars on appreciated stock generally do **not** trigger a taxable event at entry — unlike a sale. However, several rules apply:

- **Constructive sale risk**: A collar that is too tight (deep ITM put + near-ATM call) may be treated by the IRS as a constructive sale, triggering recognition of gains. The general guidance is to keep the put OTM.
- **Holding period reset**: Opening the collar may reset the long-term holding period clock in some circumstances. Verify with a tax advisor before trading.
- **Premium treatment**: The put premium paid and call premium received are typically not recognized until the options expire, are exercised, or are closed.

## Active Management: Annual Rolling

A collar is not set-and-forget. Best practice is to **roll both legs annually**:

1. **30–45 DTE before expiry**: buy back the short call and sell the long put, then re-establish a new collar 3–6 months out.
2. If the stock has moved significantly, re-center the strikes around the new price to maintain meaningful protection.
3. Evaluate whether the tax situation has changed (new holding period, different gain levels) each time you roll.

See [[Rolling-Options]] for the mechanics of rolling a two-leg position efficiently.

## Related Strategies

| Strategy | Relationship |
|----------|-------------|
| [[Covered-Call]] | The short call leg in isolation — income without protection |
| [[CSP-Cash-Secured-Put]] | Conceptually similar risk profile but on a cash position, not a stock position |
| [[Advanced-Collar]] | Collars with ratio legs, put spreads, or call spreads for refined payoff shaping |
