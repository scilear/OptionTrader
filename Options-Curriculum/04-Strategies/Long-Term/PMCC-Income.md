---
title: PMCC as a Long-Term Income Engine
tags:
  - strategy
  - long-term
  - income
  - PMCC
  - LEAPS
  - covered-call
aliases:
  - PMCC Income
  - Poor Man's Covered Call Income
status: draft
related:
  - "[[PMCC]]"
  - "[[LEAPS-Investing]]"
  - "[[Covered-Call]]"
---

# PMCC as a Long-Term Income Engine

The [[PMCC]] mechanics note covers how the position is constructed. This note focuses on a different question: can a series of short call sales eventually pay for the [[LEAPS-Investing|LEAPS]] entirely, and is that a realistic income strategy over a multi-year hold?

> [!note]
> A PMCC uses a deep in-the-money LEAPS (typically 0.70–0.85 delta, 18–24 months out) as a low-capital substitute for 100 shares. Short calls sold against it behave like [[Covered-Call|covered call]] income but require 60–80% less capital.

---

## 1. The Compounding Effect: A Numerical Example

**Setup — AAPL at $200:**

| Item | Value |
|------|-------|
| AAPL spot | $200 |
| LEAPS strike | $170 (deep ITM) |
| LEAPS expiry | 24 months out |
| LEAPS cost | ~$4,000 (0.78 delta, IV ~28%) |
| Target short call premium | $100–$150/month |

If you sell a 30-day call each month at the $210 strike (5% OTM) for $120 average, after 24 months you collect:

**24 × $120 = $2,880**

After 30 months at the same pace: **$3,600** — nearly covering the $4,000 LEAPS cost. After 34 months you are break-even on the LEAPS cost alone, before any intrinsic appreciation.

This is not guaranteed — it assumes: (a) the stock stays near or above current levels so the short calls keep having premium, (b) the LEAPS is not called away or assigned through sloppy strike selection.

> [!tip]
> Track cumulative short-call credit in a spreadsheet against your LEAPS cost basis. When net credit equals LEAPS cost, you are running the position "for free" on a cost basis — but the position still has [[Delta]] and [[Vega]] risk.

---

## 2. Target Annual Return on LEAPS Cost

**Rule of thumb (experienced traders):** Target collecting 15–25% of the LEAPS cost per year via short calls.

On a $4,000 LEAPS that is **$600–$1,000/year**, or roughly $50–$83/month. The $100–$150/month example above is at the upper end — achievable in names with elevated IV (AAPL, NVDA) but not in lower-vol stocks (XOM, JNJ).

The floor rate keeps you from over-selling (see §3). The ceiling is a sanity check: if you are collecting more than 25% annually, you are likely selling calls too close to the money.

---

## 3. Strike Discipline: Do Not Chase Yield

The most common PMCC mistake is selling the short call too close to the stock price to collect more premium. This caps upside aggressively and risks the short call trading through the LEAPS delta, collapsing the position.

**Minimum guideline:** Short call strike at least 5% OTM at entry. For AAPL at $200, that means $210 or higher.

**Why this matters:** If AAPL rallies to $215, a $205 short call may be exercised or need an expensive roll. A $210 short call gives you room to roll up-and-out for a credit or small debit.

> [!tip]
> Use the 30-delta line as a soft ceiling for short call strikes. Selling above 30 delta collapses the spread width and creates assignment risk.

---

## 4. LEAPS Replacement Strategy

LEAPS lose time value as expiry approaches. When your LEAPS drops below ~6 months to expiry, roll it forward:

1. Buy back the current LEAPS (you will pay less than original cost if stock is near your strike — intrinsic dominates).
2. Sell a new LEAPS 18–24 months out at the same or slightly higher strike.
3. Net debit on the roll is typically $400–$800 for a $4,000 LEAPS.

**The key test:** Is the net roll debit covered by accumulated short call credits?

If you have collected $1,800 in credits over 15 months and the roll costs $600, you are still net positive $1,200 on the hedge. Document this as your running cost basis.

> [!warning]
> If the stock has moved sharply against you (fallen 20%+), the LEAPS roll may cost more than expected because you are rolling from an underwater position. In this scenario, evaluate whether to close the entire spread rather than roll into a deeper hole.

---

## 5. Portfolio Allocation

How many PMCC positions make sense?

| Portfolio Size | Max PMCC Positions | Max % in LEAPS |
|---------------|-------------------|----------------|
| $100K | 3–5 | 12–18% |
| $250K | 5–10 | 10–15% |
| $500K | 8–15 | 8–12% |

Each PMCC LEAPS ties up $3,000–$6,000 in illiquid, long-dated options. Concentration in one name or sector amplifies [[Vega]] and [[Delta]] risk simultaneously.

Diversify across uncorrelated names — technology, financials, energy — rather than holding five PMCC positions on FAANG stocks.

---

## 6. Year 1–3 Income Projections

Assumes one PMCC per name, $4,000 LEAPS, $120/month average short call credit, 10 valid short call cycles per year (accounting for months where strikes are not attractive or positions are closed early).

| Year | Short Call Credits | Cumulative Credits | LEAPS Cost Remaining |
|------|-------------------|-------------------|----------------------|
| 1 | $1,200 | $1,200 | $2,800 |
| 2 | $1,200 | $2,400 | $1,600 |
| 3 | $1,200 | $3,600 | $400 |

By end of year 3 the LEAPS is nearly self-funded. Year 4 income is pure margin if the LEAPS has held value.

These are illustrative projections. Actual results depend on IV regime, strike selection, and whether the underlying trends away from the LEAPS strike.

---

## 7. Risks: This Is Not a Free Lunch

> [!warning]
> If the underlying stagnates or declines, the LEAPS loses time value faster than short call credits accumulate. A stock that moves sideways for 18 months can produce a LEAPS worth 40–50% less than purchase price, while short call credits cover only 30–40% of the original cost. Net result: a loss.

- **Vol crush:** If IV compresses after you buy the LEAPS, its value drops immediately even if price is unchanged.
- **Gap risk:** A sharp gap down eliminates LEAPS value before you can react.
- **Assignment risk:** Selling calls too close to the money before ex-dividend can trigger early assignment.

---

## 8. Capital Efficiency vs. Traditional Covered Call

| | Covered Call | PMCC |
|-|-------------|------|
| Capital required (AAPL $200) | ~$20,000 (100 shares) | ~$4,000 (LEAPS) |
| Monthly premium ($120 target) | $120 | $120 |
| Return on capital (monthly) | 0.6% | 3.0% |
| Upside participation | Full (above strike) | Limited to spread width |
| Dividend rights | Yes | No |

The PMCC wins on capital efficiency by roughly 5:1. The tradeoff is LEAPS time decay and the absence of dividend income.

---

## See Also

- [[PMCC]] — position construction and mechanics
- [[LEAPS-Investing]] — LEAPS selection, delta targeting, roll triggers
- [[Covered-Call]] — traditional covered call income comparison
