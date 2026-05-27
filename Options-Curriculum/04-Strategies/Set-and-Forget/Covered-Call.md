---
title: Covered Call
tags:
  - strategy
  - set-and-forget
  - income
  - defined-risk
  - equity
aliases:
  - CC
  - covered-call
status: draft
related:
  - "[[CSP-Cash-Secured-Put]]"
  - "[[Wheel-Strategy]]"
  - "[[PMCC]]"
---

# Covered Call

A covered call pairs 100 long shares of stock with one short OTM call at the same expiry. The short call is "covered" because the shares can satisfy delivery if the call is assigned — no additional margin is required. The strategy converts a passive stock position into an income-generating one at the cost of capping upside above the strike.

> [!note]
> "Covered" refers to the delivery obligation, not to downside risk. You still own the full stock position and bear all losses if the stock falls.

---

## When to Use It

The covered call works best under three conditions, all of which should be true simultaneously:

1. **Neutral to mildly bullish outlook** — you expect the stock to move sideways or drift slightly higher, but not rip. A strongly bullish view means you are selling away the upside you want.
2. **[[IV-Rank]] > 30** — elevated implied volatility inflates the premium you collect. Selling when IV rank is below 20–25 generates thin credits that do not compensate for the risk of a large move down. (Rule of thumb, not back-tested on all underlyings.)
3. **Long-term holder** — you own the stock for reasons independent of the option trade and are comfortable holding through a drawdown. If you are trying to exit the position, a [[CSP-Cash-Secured-Put]] or a direct sale is cleaner.

---

## Entry Rules

| Parameter | Target |
|-----------|--------|
| Delta | 0.25 – 0.35 |
| DTE | 21 – 45 days |
| Strike placement | At or near a technical resistance level |
| Credit | Aim for ≥ 1% of stock price per month (rule of thumb) |

Placing the strike at a resistance level gives the trade two sources of edge: the premium collected and the probability that resistance holds. Avoid selling at-the-money calls — the credit is larger but you cap nearly all upside and the position starts to hurt quickly on any rally.

![[pnl-covered-call.png]]

---

## Payoff Summary

- **Max profit**: Premium received + (strike price − stock purchase price) if assigned at expiry.
- **Breakeven**: Stock purchase price − premium received.
- **Max loss**: Stock falls to zero. Loss = stock purchase price − premium received. The premium provides only limited downside cushion.

> [!warning]
> The short call does not meaningfully hedge the stock. A 10% drawdown in a stock priced at $100 with a $2 premium collected is still an $8 net loss. Do not treat the covered call as a risk-reduction tool.

---

## Trade Management

**Profit target — close at 50% of max profit.** Data from tastytrade's research (published 2014–2018, SPY/IWM/QQQ universe) shows that closing at 50% captures most of the theoretical gain while freeing capital and reducing gamma risk in the final weeks. This is one of the better-supported rules of thumb in retail options literature.

**If the stock rallies through your strike before expiry**, you face a decision:
- **Roll up and out for a net credit**: buy back the short call, sell a higher strike in a later expiry. Only do this if you can collect a credit — never roll for a debit just to avoid assignment.
- **Let it get called away**: assignment at the strike is not a bad outcome. You collected the premium and sold the stock at the strike you chose. Reopen the position (or a new one) afterward if the thesis still holds.

**If the stock falls sharply**: the covered call is not the right lever. Manage the stock position directly (add a [[Zero-Risk-Collar]], trim shares, or hold according to your equity thesis). Do not roll the call down to collect more premium — that tightens the cap and locks in a lower exit price.

> [!tip]
> Do not sell covered calls on stocks you are unwilling to sell. If assignment would be emotionally painful, you will make poor rolling decisions under pressure.

---

## Tax Consideration

> [!warning]
> Covered calls on long-term stock holdings can affect your holding period and convert long-term capital gains to short-term under certain conditions (e.g., selling an in-the-money call, or a call with less than 30 DTE on a stock held less than a year). Consult your tax advisor before selling calls on appreciated, long-held positions. This is a real and frequently overlooked risk.

---

## Related Strategies

- [[CSP-Cash-Secured-Put]] — the synthetic equivalent on the downside; combined with the CC it forms the [[Wheel-Strategy]].
- [[PMCC]] (Poor Man's Covered Call) — replaces the 100 shares with a deep ITM long call (LEAPS) to reduce capital requirement.
- [[Wheel-Strategy]] — systematic cycle: sell CSPs until assigned, then sell CCs until called away, repeat.
