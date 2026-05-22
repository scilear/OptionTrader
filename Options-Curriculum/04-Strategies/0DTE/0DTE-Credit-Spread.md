---
title: 0DTE SPX Credit Spread
tags:
  - 0dte
  - credit-spread
  - spx
  - options-strategy
  - defined-risk
aliases:
  - 0DTE Bull Put Spread
  - 0DTE Bear Call Spread
  - Same-Day Credit Spread
status: draft
related:
  - "[[0DTE-Overview]]"
  - "[[0DTE-Entry-Timing]]"
  - "[[0DTE-Iron-Condor]]"
  - "[[Bull-Put-Spread]]"
---

# 0DTE SPX Credit Spread

The 0DTE credit spread is the **entry-level same-day strategy**: defined risk, one directional position, and a clear mechanical ruleset. It suits traders who are comfortable with [[0DTE-Overview|0DTE mechanics]] but want a lower-complexity alternative to a full [[0DTE-Iron-Condor]].

> [!note]
> A credit spread sells one option and buys a further out-of-the-money option for protection. The net credit received is your maximum profit; the difference in strikes minus the credit is your maximum loss. Both outcomes are known at entry.

---

## 1. Entry Window

Trade only during the **10:00–11:00 AM ET** window. See [[0DTE-Entry-Timing]] for the full rationale — the short version is that pre-10:00 AM volatility is elevated from the open auction, and after 11:00 AM the credit available shrinks faster than the risk does.

> [!tip]
> If SPX has not established a clear intraday range or direction by 10:15 AM, wait. A blank canvas is not a setup.

---

## 2. Strike Selection

Use the **expected move (EM)** as your anchor. The EM for a 0DTE session can be read directly from the at-the-money straddle price at market open (or estimated as approximately 0.68 × ATM IV × spot / 252^0.5).

**Rule:** Place the short strike **outside 0.75× EM** from current SPX price.

At SPX = 5000 with EM = $30:
- 0.75 × $30 = $22.50
- Put side: short strike ≤ 4977 → round to 4975 or lower
- Call side: short strike ≥ 5023 → round to 5025 or higher

Target delta on the short leg: **0.10–0.15**. These two filters (EM and delta) should agree. When they conflict, respect whichever puts the short strike farther from spot.

---

## 3. Spread Width and Credit Target

| Daily Range Feel | Spread Width | Target Credit |
|-----------------|--------------|---------------|
| Quiet (<$20 EM) | $25 wide | $5.00–$6.25 (20–25% of width) |
| Normal ($20–$40 EM) | $25–$50 wide | $5.00–$12.50 |
| Wide (>$40 EM) | $50 wide | $10.00–$12.50 |

If the market will not fill at ≥20% of width, the spread is not offering adequate compensation for the risk. Pass.

---

## 4. Directional Bias Filter (Rule of Thumb)

If SPX is **clearly trending intraday** — two or more consecutive 15-minute bars in one direction with above-average range — sell credit only on the **tested side**:

- Trending down → sell a bear call spread (sell calls above resistance)
- Trending up → sell a bull put spread (sell puts below support)

Do not fade a strong intraday trend with a credit spread on the other side. This rule is a practitioner heuristic, not backtested to a specific win-rate figure.

> [!danger]
> Selling credit spreads on both sides simultaneously creates an [[0DTE-Iron-Condor]], which carries meaningful pin risk and is a separate, more complex strategy. Do not attempt it by accident.

---

## 5. Worked Example

**SPX = 5000 | EM = $30 | Bull Put Spread**

- 0.75 × EM = $22.50 → short strike at or below 4977 → choose **4940 put** (delta ~0.10)
- Buy the **4915 put** for protection ($25 wide)
- Net credit: **$7.50** (30% of $25 width — above minimum, accept)
- Max loss: $25.00 − $7.50 = **$17.50 per share** ($1,750 per contract)

At 2 contracts, max loss = $3,500. This is 3.5% of a $100K portfolio — within the sizing rule stated below only if you manage the stop strictly.

---

## 6. Position Sizing

**Maximum allocation: 1% of portfolio per spread (max loss basis).**

At $100K:
- 1% = $1,000 max loss per trade
- $25-wide spread, $7.50 credit → max loss $17.50/share = $1,750/contract
- Rounded down: **1 contract** fits strictly within 1% rule
- 2 contracts = $3,500 max loss = 3.5% — only acceptable if stop is honored without exception

> [!warning]
> Sizing at 2 contracts assumes the 200% credit stop is executed mechanically. If you hold through the stop, the position becomes a 3.5% portfolio risk on a single 0DTE trade. Never rely on discretion to enforce a stop in the final hour of 0DTE expiration.

---

## 7. Management Rules

| Condition | Action |
|-----------|--------|
| Profit ≥ 50% of credit | Close — do not hold for the last dollar |
| Loss ≥ 200% of credit received | Close immediately — hard stop |
| Time: 3:30 PM ET | Close regardless of P&L |
| Short leg threatened (delta > 0.30) | Evaluate early close or roll to avoid assignment risk |

> [!warning]
> **Never hold a 0DTE loser past 3:45 PM.** Gamma accelerates losses exponentially in the final minutes before expiration. A spread that is $5 out-of-the-money at 3:30 PM can be fully in-the-money at 4:00 PM after a 10-point SPX move. Exit by 3:30 PM and remove the uncertainty entirely.

---

## Related Notes

- [[0DTE-Overview]] — mechanics, margin, and settlement rules for SPX 0DTE
- [[0DTE-Entry-Timing]] — detailed breakdown of the 10:00–11:00 AM window
- [[0DTE-Iron-Condor]] — combining bull put and bear call into a single position
- [[Bull-Put-Spread]] — the underlying structure used on the put side
