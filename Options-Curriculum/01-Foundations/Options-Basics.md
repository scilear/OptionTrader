---
title: Options Basics
tags:
  - foundations
  - core-concepts
aliases:
  - Options-Intro
  - Call-vs-Put
status: draft
related:
  - "[[Greeks-Overview]]"
  - "[[IV-Rank]]"
  - "[[Theta-Decay]]"
  - "[[Intrinsic-vs-Extrinsic-Value]]"
  - "[[Probability-of-Expiration]]"
---

# Options Basics

## Definition

An **option** is a contract granting the holder the right—but not the obligation—to buy or sell an underlying asset (stock, index, or ETF) at a fixed price (strike price) on or before a specific date (expiration).

More formally:

An option derives its value from an underlying asset and consists of two counterparties: the **buyer** (who pays a premium for the right to act) and the **seller** (who receives the premium and is obligated to deliver if the buyer exercises). There are two types:
- **Call**: Right to buy at the strike price
- **Put**: Right to sell at the strike price

**Key distinction:**
```
Buyer   → Pays premium, has rights, defined max loss
Seller  → Receives premium, has obligations, undefined/capped max loss
```

> [!warning]
> Selling options exposes you to potentially unlimited loss (naked calls) or significant loss (naked puts). Always understand your max loss before entering a sell trade. Use spreads to define risk if you're new to options.

## Why It Matters

### For Traders

1. **Leverage without margin debt**: Control 100 shares of SPX (notional $500K at 5000 spot) with a $2–5K premium outlay, not by borrowing cash.

2. **Defined risk on long positions**: A $200 long call on SPX gives you upside exposure with max loss capped at your $200 premium—no margin call surprises.

3. **Theta decay asymmetry**: Sellers benefit from time passing and market stagnation (theta decay works in their favor every single day). Buyers fight time decay. This structural edge is why professional traders skew toward selling.

4. **Volatility is tradable**: Implied volatility (IV) is an asset class. You can sell high IV (premium is expensive) and buy low IV (premium is cheap) independently of whether the market moves.

### Historical Context

Options trading formalized with the Black-Scholes model (1973), which proved that option prices depend on five factors: underlying price, strike, time to expiration, volatility, and interest rates. This framework underpins modern derivatives trading and made volatility-based strategies systematic and quant-driven.

---

## How to Apply

### The Four Basic Positions

| Position | Max Profit | Max Loss | When to Use |
|----------|-----------|----------|------------|
| **Long Call** | Unlimited | Premium paid | Bullish, limited capital, want leverage |
| **Short Call** | Premium received | Unlimited (or capped if spread) | Bearish/neutral, high IV, want theta decay |
| **Long Put** | Strike − Premium | Premium paid | Bearish, limited capital, defined risk |
| **Short Put** | Premium received | Strike − Premium (or capped if spread) | Neutral/bullish, want theta decay, high IV |

### Step 1: Understand Intrinsic vs Extrinsic Value

**Intrinsic value** is how much the option is worth *right now* if exercised:
- Call: max(underlying − strike, 0)
- Put: max(strike − underlying, 0)

**Extrinsic value** (time value) is everything else—decay as expiration nears. For SPX 5000:
- A 5025 call with SPX at 5000 is *out-of-the-money (OTM)* with zero intrinsic value; all premium is extrinsic.
- A 4975 call with SPX at 5000 is *in-the-money (ITM)* with $25 intrinsic value; rest is extrinsic.

### Step 2: Recognize Why Sellers Have the Edge

Theta decay is a seller's best friend:

1. **Time decay accelerates near expiration** (~30 days out, decay becomes material). An option losing $1/day of extrinsic value is that $1 going to the seller.

2. **Probability favors sellers**: A short 5050 call (50+ delta call is ~70% ITM, 30% OTM at spot 5000) will expire OTM 30% of the time. Free money to the seller.

3. **Volatility reversion**: Sold when IV is high (premium is inflated), reversion to mean reduces IV, crushing the sold option's value before expiration.

4. **Daily compounding**: Every day closer to expiration, theta accelerates. A short-dated option loses extrinsic value faster than a long-dated one.

### Step 3: Understand Defined vs Undefined Risk

**Defined Risk:**
- Long Call: max loss = premium paid (e.g., $200 call on SPX costs $2K, you lose max $2K)
- Long Put: max loss = premium paid
- Vertical Spread (call or put): max loss = width of strikes − premium collected

**Undefined Risk:**
- Short Call naked: max loss is unlimited (SPX can rally to 6000, 7000, ...)
- Short Put naked: max loss is capped at strike (SPX to zero), but that's 100% of position value

> [!danger]
> Do not sell naked calls or puts unless you have significant capital and have stress-tested your portfolio's margin availability in a crash scenario. Retail traders should start with spreads to define risk.

### Step 4: Build Your First Position

1. **Pick your direction and time horizon**: Bullish on SPX for 30 days? Neutral on AAPL for 14 days?
2. **Check [[IV-Rank]]**: High IV favors selling; low IV favors buying.
3. **Calculate [[Greeks-Overview]] (especially [[Theta-Decay]])**: How much is [[Theta-Decay]] working for or against me daily?
4. **Size small**: Trade 1–2 contracts. Learn the mechanics before scaling.

> [!tip]
> For your first trade, buy a call or put (defined risk). You pay premium, you own the right, you can't blow up your account. Once comfortable with profit/loss mechanics and [[Greeks-Overview]], move to spreads (defined risk selling). Only after 6+ months of consistent execution consider naked selling, and only if you have > $50K in capital.

---

## Example

**Setup**: SPX at 5000, 30 days to expiration (DTE), IV Rank at 60% (elevated, good for selling).

**Scenario 1: Long Call (Bullish, want leverage)**

- Buy 5050 call for $150 (premium)
- Max profit: unlimited (SPX rallies to 5200+ → call is deep ITM, intrinsic = $200, minus the $150 you paid = $50 profit; if SPX 5500, intrinsic $450 − $150 premium = $400 profit)
- Max loss: $150 (if SPX stays below 5050, call expires worthless)
- [[Theta-Decay]]: works against you. You lose ~$5/day in extrinsic value just from time passing.
- Use case: You're bullish short-term, capital-efficient

**Scenario 2: Short Call (Neutral/Bearish, want theta decay)**

- Sell 5050 call for $150 (premium collected)
- Max profit: $150 (if SPX stays below 5050, call expires worthless, you keep the $150)
- Max loss: unlimited (if SPX rallies to 5500, you're short 100 shares at 5050 strike, you owe $450 − $150 = $300 loss per contract; SPX to 6000 = $950 loss per contract)
- [[Theta-Decay]]: works for you. You gain $5/day just from time passing.
- Risk: Naked short call is dangerous. Better: sell a 5050/5075 call spread (capped max loss at $250 width − $50 premium collected = $200 max risk)

**Scenario 3: Long Put (Bearish, downside hedge)**

- Buy 4950 put for $130 (premium)
- Max profit: $4820 (if SPX crashes to zero, put is worth $4950 intrinsic, minus $130 premium = $4820)
- Max loss: $130
- [[Theta-Decay]]: works against you
- Use case: Portfolio hedge, or pure bearish bet

**Outcome**: 
- Long call: you profit if SPX > 5050, lose money if time passes and SPX doesn't rally.
- Short call: you profit if SPX < 5050 or time passes (theta decay), lose money if SPX rallies past 5050.
- This is the fundamental tension: buyers pay for upside optionality; sellers collect that premium and depend on stagnation or mean reversion.

### Counter-Example: Overestimating Your Extrinsic Value

**Scenario**: You sell a 5025 call (ATM) for $250 with 30 DTE on SPX at 5000.

**Wrong Approach**: "I'll keep the $250 no matter what. It's free money."

**Reality**: SPX rallies to 5100 in week 2. Your short call is now ITM and worth $200 (intrinsic) + $80 (extrinsic) = $280. You're underwater $30, and extrinsic value is collapsing because the option is now ITM and deep ITM (less extrinsic decay benefit).

**Correct Approach**: Understand that extrinsic value decays *faster* when OTM (you own this advantage when short). Once ITM, your short call becomes a short stock position via delta, and the risk structure inverts. Set a stop-loss (e.g., close if position is −50% of credit, or close at 2 weeks DTE before assignment).

**Lesson**: Theta decay doesn't protect you from large directional moves. It only helps if the underlying stays near your strike or moves against you slowly. Always pair theta selling with a directional thesis and a stop loss.

---

## Links

- **Foundational Concepts**: [[Greeks-Overview]], [[Intrinsic-vs-Extrinsic-Value]], [[Probability-of-Expiration]]
- **Volatility & Pricing**: [[IV-Rank]], [[Implied-vs-Realized-Volatility]], [[Volatility-Smile]]
- **Greeks in Depth**: [[Delta]], [[Gamma]], [[Theta-Decay]], [[Vega]], [[Rho]]
- **Strategy Intro**: [[Long-Call-Strategy]], [[Short-Call-Strategy]], [[Long-Put-Strategy]], [[Short-Put-Strategy]]
- **Risk Management**: [[Position-Sizing]], [[Stop-Loss-Strategies]], [[Max-Loss-Rules]]
- **Market Conditions**: [[IV-Rank]], [[Regime-Classification]], [[Greeks-Behavior-by-Regime]]
