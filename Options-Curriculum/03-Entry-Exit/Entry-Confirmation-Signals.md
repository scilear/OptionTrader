---
title: Entry Confirmation Signals
tags:
  - entry-exit
  - checklist
  - risk-management
  - iv-rank
  - volatility
aliases:
  - Pre-Trade Checklist
  - Before You Press the Button
status: draft
related:
  - "[[High-Probability-Setup-Checklist]]"
  - "[[When-Not-To-Trade]]"
  - "[[IV-Rank]]"
---

# Entry Confirmation Signals

Before placing any options trade, run through all five confirmation signals below. Skipping even one has a measurable cost: missed earnings dates, stale spread data, and VIX blindness account for a large share of avoidable losses in premium-selling strategies. Treat this as a preflight checklist, not a suggestion.

> [!warning]
> Entering a trade without confirming all five signals does not mean the trade will lose — it means you are accepting unquantified risk. Over a large sample, unquantified risk compounds against you.

---

## The Five Confirmation Signals

### 1. IV Rank Confirmed

- Open your screener and pull the current [[IV-Rank]] for the underlying.
- Compare today's IVR to yesterday's. A one-day spike (e.g., 28 → 52) requires a reason. If you cannot identify the cause, do not trade.
- Minimum threshold for premium selling: IVR ≥ 30. Preferred range: IVR 40–80. Above 80, reduce size — elevated IV often precedes a further move.
- Cross-check on two sources (e.g., Tastytrade platform + Market Chameleon) if the reading looks anomalous.

> [!note]
> IVR and IV Percentile are not the same metric. IVR compares current IV to the 52-week high/low; IV Percentile counts how many days in the past year current IV was lower. Both matter — see [[IV-Rank]] for the distinction.

### 2. Price at or Near a Key Technical Level

- Do not sell puts in the middle of a range. Wait for price to reach a defined support zone (prior swing low, major moving average, or high-volume node).
- Mark your level before the trade session opens, not while you are already watching the bid flash.
- Rule of thumb: if price is more than 3% above the nearest structural support, wait. The edge in a cash-secured put comes partly from the technical floor beneath the strike.

> [!tip]
> Draw the support level first, then check whether a strike with acceptable premium exists near it — not the other way around. Letting the premium dictate the strike is how you end up short puts in empty air.

### 3. No Catalysts Within 14 Days

Check all of the following before entry:
- **Earnings**: Earnings Whispers (earningswhispers.com) and Market Chameleon both show confirmed and estimated dates. Use the more conservative date if they differ.
- **FDA dates**: BioPharmCatalyst or Market Chameleon's FDA calendar for biotech underlyings.
- **Fed meetings and CPI**: Mark FOMC dates and scheduled macro releases for index-level trades (SPX, QQQ, IWM).
- Hard rule: if any binary event falls within 14 calendar days of your planned expiration, do not sell undefined-risk premium through that event. Use a defined-risk spread instead, or wait.

### 4. VIX Context

- Check spot VIX at the time of entry, not the prior close.
- If VIX > 30: use defined-risk structures only (vertical spreads, iron condors). Do not sell cash-secured puts on individual stocks — the correlation spike means your "uncorrelated" positions are not uncorrelated.
- If VIX is between 20 and 30: reduce notional size by 25–30% versus a calm-market baseline.
- If VIX < 15: premium is thin. Confirm IVR ≥ 40 before entering; flat VIX with low IVR is a low-edge environment.

> [!danger]
> Selling naked puts on individual stocks when VIX > 30 is unsuitable for most retail traders. Gap risk and margin calls can exceed the entire premium collected many times over.

### 5. Spread Confirmed — Live, Right Now

- Pull up the actual bid-ask spread at your target strike at the moment of entry. Do not rely on yesterday's mid or a morning screenshot.
- Maximum acceptable spread for a liquid underlying (SPX, QQQ, GLD): mid ± 0.10. For single stocks: mid ± 0.15 to 0.20.
- If the spread is wider than your limit, do not chase. Either wait for tightening or select an adjacent strike where liquidity is better.
- Calculate the spread as a percentage of the mid: `(ask - bid) / mid`. Above 15%, the fill quality will erode your edge.

---

## What to Do If You Are Not Sure

If you have checked all five signals and still feel uncertain about the trade — trust that feeling. The correct response is always one of two options:

1. **Paper trade it.** Log the trade in a journal or paper account. Watch how it behaves without capital at risk. Once you have seen three to five similar setups play out, your confidence will be calibrated to reality.
2. **Reduce size to 25%.** Enter one-quarter of your intended position. A quarter-size trade keeps you in the game, gives you real P&L feedback, and limits the damage if the setup fails. Scale up only after the trade confirms your thesis.

There is no third option. "Enter full size but watch it closely" is not a risk-management plan — it is rationalization. See [[When-Not-To-Trade]] for the conditions that warrant staying out entirely.

---

## Quick Reference Checklist

- [ ] IVR ≥ 30 confirmed on two sources; one-day change explained
- [ ] Price at or within 3% of a defined technical support level
- [ ] No earnings, FDA, FOMC, or major macro event within 14 days of expiration
- [ ] VIX checked: defined-risk only if VIX > 30; size reduced if VIX 20–30
- [ ] Live bid-ask spread at target strike: ≤ 15% of mid

All five checked? Cross-reference with [[High-Probability-Setup-Checklist]] and enter.
