---
title: Earnings Iron Condor Playbook
tags:
  - earnings
  - iron-condor
  - iv-crush
  - income
  - options-strategy
aliases:
  - Earnings IC
  - Earnings Iron Condor
status: draft
related:
  - "[[IV-Crush-Mechanics]]"
  - "[[Iron-Condor]]"
  - "[[Earnings-Ticker-Selection]]"
  - "[[Earnings-Execution-Playbook]]"
---

# Earnings Iron Condor Playbook

The earnings [[Iron-Condor]] is the primary earnings trade for income-focused traders. You sell an IC immediately before the announcement to harvest the [[IV-Crush-Mechanics|IV crush]] that follows — implied volatility typically collapses 30–50% within hours of the report, regardless of whether the stock moves. The edge is not directional; it is volatility-premium decay.

> [!danger]
> This trade carries binary gap risk. A stock can open 15–20% beyond the expected move on a surprise. Maximum loss is defined but can be 3–5× the credit collected in a single session. Do not attempt this trade without first understanding [[Earnings-Risk-Rules]] and sizing correctly.

---

## 1. Entry Timing

Enter **1 to 3 trading days before** the earnings announcement. Entering earlier dilutes the vol-crush edge; entering later sacrifices premium as market makers reprice wings intraday on the day of the event.

Always use the **shortest-dated expiry that includes the earnings date**. Weekly options expiring the Friday after the event capture concentrated IV crush. Monthly expirations that happen to include the event date are acceptable when weeklies are illiquid.

> [!tip]
> Check the earnings date against the option expiry calendar using the [[Earnings-Tools]] screener before placing the trade. A misread expiry that excludes the event earns no crush.

---

## 2. Strike Selection

Anchor short strikes at **1× to 1.5× the implied expected move (EM)** from the at-the-money straddle price. The goal is for short strikes to sit just outside the market-implied range.

**Example — AAPL at $200, EM = $8:**

- Short put: $192 (1× EM below spot) → use $190 for a cleaner strike
- Short call: $208 (1× EM above spot) → use $210 for a cleaner strike
- Long put wing: $187.50 (2.5-point wide put spread)
- Long call wing: $212.50 (2.5-point wide call spread)

Result: sell the $190/$187.50 put spread + $210/$212.50 call spread.

See [[Expected-Move-Formula]] for the calculation. Using 1× EM gives the best win rate; widening to 1.5× reduces premium but improves probability of profit if you want more cushion.

![[chart-earnings-ic-example.png]]

---

## 3. Credit Target

Collect at least **25–30% of the wing width** in net credit.

On a $2.50-wide wing, the minimum acceptable credit is $0.625–$0.75 per spread, or $1.25–$1.50 for both sides combined. Trades below this threshold do not justify the binary risk.

> [!note]
> Credit as a percentage of width is the key ratio — not the absolute dollar credit. A $1.50 credit on $2.50 wings is 60% of width, which is excellent. The same $1.50 credit on $5.00 wings (30%) is borderline acceptable.

If the market is not offering 25% of width at 1× EM, the stock's IV is not elevated enough. See [[Earnings-Ticker-Selection]] for pre-screening criteria.

---

## 4. Exit Rule

**Close at the next market open after earnings.** Do not hold into the second day.

The IV crush is front-loaded — 80–90% of the collapse happens in the first hour of the post-earnings session. Holding longer does not generate meaningful additional theta and re-exposes you to directional drift if the stock continues to trend.

Set a **closing order at 50% of max profit** as a limit order before the open. If the stock is inside your strikes, fill the order immediately at the open rather than waiting.

> [!tip]
> Many traders set the closing GTC order the night before earnings results drop, so execution is automatic at the open.

---

## 5. Risk Scenario

If the stock moves beyond the expected move and breaches a short strike, max loss = **spread width − credit received**.

AAPL example: $2.50 width − $1.50 credit = **$1.00 max loss per spread** ($100 per contract side). Both spreads breached simultaneously: $2.00 total max loss per IC.

> [!warning]
> This trade can lose 3–5× the credit received in a single gap if the stock moves 1.5–2× the expected move and both wings are threatened. Always use defined risk (never a naked short strangle on earnings). Pre-calculate your max loss before entering and confirm it fits within your [[Earnings-Risk-Rules|position-level loss limit]].

---

## 6. Position Sizing

Allocate **1–2% of portfolio risk per earnings trade**, measured as max loss per IC.

Binary events are uncorrelated trade-by-trade but cluster during reporting season. Running more than 3–4 earnings ICs simultaneously concentrates binary risk in a single week.

---

## 7. Historical Edge

This trade wins when the **actual move is smaller than the implied move**. Historically, for high-IV stocks (IVR > 50 at the time of earnings), the actual move undershoots the EM approximately **55–65% of the time** — a modest but consistent edge over a large sample. (Source: academic studies on earnings vol premium, e.g., Goyal & Saretto 2009; consistent with internal backtest findings on SPX-adjacent large-caps.)

> [!note]
> Win rate alone does not determine profitability. A 60% win rate is only an edge if average wins are proportionate to average losses. At 25–30% credit / width, the math supports a positive EV with a 55%+ win rate. Verify this on your own ticker universe using [[Earnings-Tools]].

---

## Quick Reference

| Parameter | Target |
|---|---|
| Entry window | 1–3 days before earnings |
| Expiry | Shortest weekly including earnings date |
| Short strikes | 1×–1.5× implied expected move |
| Wing width | $2.50–$5.00 (liquid strikes) |
| Minimum credit | ≥25–30% of wing width |
| Exit | Next market open after earnings |
| Position size | Max 1–2% portfolio (by max loss) |
| Historical win rate | ~55–65% (high-IVR stocks) |
