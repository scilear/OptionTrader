---
title: IV Crush Mechanics
tags: [earnings, implied-volatility, iv-crush, event-trading, calendar-spread]
aliases: [IV Crush, Volatility Crush, Earnings IV Collapse]
status: draft
related:
  - "[[Earnings-Overview]]"
  - "[[Earnings-IC-Playbook]]"
  - "[[Earnings-Straddle-Strangle]]"
  - "[[Implied-Volatility-Basics]]"
  - "[[Calendar-Spreads]]"
  - "[[Expected-Move]]"
---

# IV Crush Mechanics

[[Implied-Volatility-Basics|Implied volatility]] behaves predictably around earnings announcements: it inflates into the event and collapses immediately after. Understanding this cycle is the foundation of every earnings-based options strategy.

## 1. Why IV Spikes Before Earnings

Earnings reports are **binary events**. The market does not know the outcome, but it knows a large gap is likely. To price this uncertainty, [[Market-Makers|market makers]] widen spreads and lift implied volatility on contracts that span the announcement. The extra premium compensates them for the asymmetric gamma risk they cannot easily hedge overnight.

> [!note] Uncertainty premium
> The "earnings premium" embedded in IV is the market's collective insurance bill for an unknown jump. It is not a forecast of direction, only of magnitude.

The closer to the announcement, the steeper the IV ramp — short-dated options absorb almost all the event risk because they have no time left to "average it out."

## 2. Why IV Collapses After Earnings

The instant results are released, the uncertainty resolves — **regardless of whether the stock moves or not**. The binary risk that justified the premium no longer exists, so IV reverts toward its baseline. This is the [[IV-Crush|crush]].

> [!warning] You can be right on direction and still lose
> If you buy a [[Long-Straddle|straddle]] into earnings and the stock moves less than the implied move, the IV collapse will destroy both legs faster than delta can rescue them.

## 3. Typical Magnitude

Empirically, ATM IV on the front-week contract drops **30–60% overnight** after the report. Liquid mega-caps (AAPL, MSFT) tend toward the lower end; small-caps and biotech can exceed 70%. These ranges are rule-of-thumb based on multi-cycle observation; always measure on the specific name before sizing.

![[chart-iv-crush-pattern.png]]

## 4. Measuring the Expected Crush

Compare the ATM IV of the **earnings-week expiry** to the **next monthly expiry**:

```
earnings_premium ≈ IV_front - IV_back
```

A 20-vol gap between the weekly and the following month is the market's quoted earnings premium. After the report, the front IV should converge down toward the back IV.

> [!tip] Term-structure inversion is your signal
> When front-week IV trades higher than back-month IV (inverted term structure), an earnings event is being priced. The wider the inversion, the richer the crush trade.

## 5. Harvesting the Crush

The cleanest expression is a [[Calendar-Spreads|calendar spread]]: **sell** the earnings-week ATM option, **buy** the next-expiry ATM option. The front leg loses most of its value from IV collapse while the back leg retains most of its vega.

Alternatives include [[Iron-Condors|iron condors]] (see [[Earnings-IC-Playbook]]) and short strangles — both detailed in [[Earnings-Straddle-Strangle]].

> [!danger] Short premium into earnings is not a beginner trade
> Naked or under-hedged short straddles/strangles carry undefined or large defined risk on a binary event. Trade only with defined-risk structures (calendar, condor, butterfly) until you have lived through multiple earnings cycles.

## 6. When IV Crush Is Not Enough

If the stock **gaps beyond the expected move**, delta losses on the short leg overwhelm the IV gain. A calendar can lose its entire debit if the underlying jumps far enough that the short strike goes deep ITM and the back leg cannot keep pace. This is the dominant failure mode of crush trades.

> [!warning] Tail-risk dominates
> One outsized gap can erase the profit from many successful crush trades. Size each earnings position as if it could lose 100% of premium paid or maximum defined loss.

## 7. Straddle Price as Expected Move

A useful shortcut: the ATM straddle price ≈ the [[Expected-Move|expected one-standard-deviation move]] through expiry.

```
expected_move ≈ ATM_call + ATM_put
```

If a $100 stock has a $5 straddle, the market is pricing roughly a ±5% move. Compare this to historical post-earnings moves — if the implied move is meaningfully larger than realized history, premium-selling structures are favored; if smaller, premium-buying structures may be cheap.

See [[Earnings-Overview]] for the full event-trading framework.
