---
title: Gamma Tsunami (Extreme GEX Event)
tags:
  - risk-management
  - gex
  - extreme-events
  - 0dte
aliases:
  - Gamma tsunami
  - Gamma squeeze
  - Negative gamma cascade
status: draft
related:
  - "[[Gamma-Regime-and-GEX]]"
  - "[[Term-Structure-of-Gamma]]"
  - "[[Index-vs-Single-Stock-GEX]]"
  - "[[Stop-Loss-Strategies]]"
---

# Gamma Tsunami: The Extreme GEX Event

A **Gamma Tsunami** is the most dangerous and least forgiving gamma setup in modern markets. It occurs when a stable, positive gamma regime **suddenly inverts to negative gamma**, triggering a self-reinforcing cascade of dealer selling that can accelerate price movements exponentially.

Unlike normal market moves, a gamma tsunami is **purely mechanical**. It can occur independently of fundamental news or technical triggers—the setup alone is sufficient to detonate catastrophic moves.

> [!danger]
> This is the most important risk concept in modern options trading. A gamma tsunami can turn a $50,000 account into a $10,000 account in minutes. Position sizing and stop-loss discipline are not optional.

---

## The Prerequisites: The Setup Phase

A gamma tsunami does not materialize randomly. Four specific conditions must align:

### 1. Positive Gamma Regime (Starting Point)
The market must initially be **above the [[Gamma-Regime-and-GEX|Gamma Flip]] level**, in a stable, long gamma environment where:
- Dealer hedging is **stabilizing** (buying dips, selling rallies)
- Volatility is contained; price action is mean-reverting
- Large concentrations of [[Gamma-Walls-Call-Put|gamma walls]] exist at key strikes
- The gamma flip is well **below** the spot price — a buffer

### 2. The Technical Condition
Spot price must be **trading directly above a significant Gamma Flip level**. This flip level often coincides with:
- A major technical support zone (VWAP, moving average, prior swing low)
- A key psychological level (round numbers, key options expiration strike)
- The flip is the "dam" holding back destabilizing flows

### 3. Extreme 0DTE Open Interest Concentration
The setup requires **concentrated OI in near-the-money 0DTE options**:
- 0DTE now drives close to **half of all SPX volume**
- 61%+ of SPX option volume is in expirations from 0 to 1 day
- A surge in OI of 30–100% at ATM or slightly OTM strikes
- **Gamma bombs**: 0DTE options waiting to explode in the final hours

### 4. Far-Dated Gamma Confirmation
The flip level should have **minimal backstop** from far-dated, deep ITM positive gamma. If quarterly puts have massive open interest just below the flip, they can act as a "floor" that prevents the tsunami.

---

## The Trigger: Breaking the Flip

The tsunami detonates when spot price **decisively breaks below the Gamma Flip level**.

**Why This is the Detonation Key:**

When price trades below the flip, net gamma instantly turns **negative (short gamma)**. Dealer hedging behavior reverses:
- **Before:** They sell rallies, buy dips (stabilizing)
- **After:** They buy rallies, sell dips (destabilizing)

The market transitions from "sticky terrain" (price gets pulled back) to "slippery terrain" (price travels freely downward).

---

## The Three Phases of Cascade

Once triggered, the tsunami unfolds in three explosive phases:

### Phase 1: From "Sticky" to "Slippery"
In positive gamma above the flip, price was "pinned" — gravity pulled it back to high-gamma strikes. At the moment of the flip breach, that gravity **disappears**. Price is now free to fall without mechanical resistance.

### Phase 2: The Self-Reinforcing Feedback Loop (The True Tsunami)
This is where the cascade becomes exponential:

1. **Price falls below flip** → Aggregate gamma turns negative
2. **Dealers' hedging flips** → They must sell to hedge (instead of buying)
3. **Their selling pushes price further down**
4. **ITM puts and OTM calls increase in value** → More forced hedging required
5. **The decline accelerates** → Hedging adjustments reinforce the move
6. **Market begins to "travel" rather than simply move** — reflexive acceleration

This is a **closed feedback loop**. Once started, it feeds itself. Dealer hedging is no longer market friction; it is market accelerant.

### Phase 3: The Gamma Blast (Intraday Extinction Event)
In the final stage, gamma in 0DTE options becomes **explosively exponential**. Delta becomes violently unstable:

- A ~1% market move can shift delta from **0.50 to 0.95 or 0.05** within hours
- Position Greeks become nonlinear and impossible to predict
- A position that seems "neutral" at 10:30am can be deep in the money by noon
- Manual hedging cannot keep pace — execution must happen in milliseconds

**The 0DTE Explosion:**
- Small directional twitch → 10–20x jump in option prices
- Flash-crash style moves
- Risk evolution that is **nonlinear and rapid**

---

## Case Study: August 5, 2024 Yen Carry Trade Unwind

The textbook example of a gamma tsunami in action:

| Phase | Event |
|---|---|
| **Setup** | SPX in stable positive gamma regime. Massive 0DTE OI. Gamma flip at 5800. |
| **Trigger** | Yen carry unwind begins. SPX slides through 5800 (the flip). |
| **Phase 1** | Transition from sticky to slippery. Price finds no resistance. |
| **Phase 2** | Dealers flip to negative gamma. Forced selling cascades the decline. |
| **Phase 3** | 0DTE gamma blast. VIX spikes from **17 to 38 within hours**. |
| **Result** | +120% intraday VIX explosion. Driven entirely by mechanical gamma amplification, not news. |

---

## How to Trade a Gamma Tsunami

Trading this setup is about **identifying the conditions, waiting for the trigger, and capitalizing on the amplification**.

### Step 1: Identify the Setup (Pre-Event)

**Monitor GEX daily:**
- Locate the gamma flip level for your underlying (SPX, NDX, QQQ, or mega-cap)
- **Condition A:** Spot must be trading comfortably **above** the flip (positive gamma regime)
- **Condition B:** Significant 0DTE OI surges at ATM and slightly OTM strikes (30–100% increase = red flag)
- **Condition C:** The flip must be technically meaningful (VWAP, key moving average, prior support/resistance)
- **Condition D:** Check far-dated gamma — is there a deep ITM put backstop below the flip? If yes, the tsunami could fail.

### Step 2: Wait for the Trigger (Event Entry)

**Do not pre-empt the break.** Timing is critical. Wait for:
- Price to break **and sustain** below the gamma flip
- Confirmation on a 5- or 15-minute candle close
- Rising volume on the break
- VIX starting to spike

**Entry signal:** The flip is violated on a decisive close with confirmation. This is the detonation.

### Step 3: Execute the Trade

**The Amplification Play (Tsunami Itself):**
- **Buy 0DTE puts** on SPY or QQQ (or long puts on SPX futures)
- **Target strikes:** One to two strikes below ATM (the strikes most likely to be ITM as the cascade progresses)
- **Time horizon:** Ride the acceleration for the next 2–4 hours (the peak gamma blast phase)
- **Exit:** Do not cut early — this is where 10–20x moves occur

**Alternative: The Pin Strategy (Post-Tsunami):**
- After the tsunami exhausts (usually by market close or next session open), price settles and pins to a high-gamma strike
- Use a **tight butterfly** (2-wide, 2-wide wings) centered on the high-gamma pin level
- Target 0DTE or weekly expiration for maximum gamma concentration
- Risk-reward can be asymmetric (3:1 or better) even with moderate win rates (50–60%)

### Step 4: Manage the Risk (CRITICAL)

This is the most dangerous setup in options trading. **Position sizing must be ruthless.**

- **Never hold position size > 0.5% of account per leg**
- **Stop loss is mechanical, not discretionary** — if your thesis is wrong, exit immediately
- **Do not sell options into a gamma tsunami** — you will be buying them back at 10x the credit
- **Watch the term structure** — if far-dated, deep ITM gamma intervenes, the tsunami can reverse suddenly
- **Time decay works against you** — if price stalls, 0DTE options decay rapidly; don't hold hoping for a move

> [!warning]
> A single misjudgment can wipe your account. This is not a strategy for learning or for small accounts. Execute with extreme discipline or don't execute at all.

---

## Where Gamma Tsunamis Fail

Even with perfect prerequisites, the setup can fail:

### 1. Intervention from Far-Dated Positive Gamma
If the sell-off pushes price into a zone where **quarterly or LEAPS put gamma becomes extremely positive**, longer-dated dealers step in and buy aggressively, creating a powerful floor that reverses the tsunami before it gains full momentum.

**How to prevent this loss:** Before entering, scan the **full term structure** of gamma, not just 0DTE. Is there a structural long-term put wall below the flip? If yes, reduce your conviction.

### 2. Reversal Catalyst
A positive fundamental catalyst (strong economic data, Fed pivot) can trigger a sudden squeeze that reverses the cascade before it completes. The market can snap back 2–3% in minutes.

### 3. Circuit Breaker Triggers
On extremely violent moves, circuit breakers can halt trading, disrupting the feedback loop. This can either save you or lock you in a bad position.

---

## Summary: Gamma Tsunami Cheat Sheet

| Element | Key Takeaway |
|---|---|
| **The Setup** | Spot above gamma flip + massive 0DTE OI concentration near the money + minimal far-dated ITM backstop |
| **The Trigger** | Decisive break **below** the gamma flip |
| **The Amplification** | Dealers flip from buying dips to selling declines; 0DTE gamma becomes explosively exponential |
| **The Trade** | Long 0DTE puts on the break; alternative: wait for exhaustion and pin-targeting butterfly |
| **Position Size** | Never exceed 0.5% of account per leg — this is a wipe-out scenario if wrong |
| **The Risk** | Extreme; losses can be rapid and severe; far-dated gamma intervention can reverse the setup |
| **The Failure Mode** | Long-term positive gamma creates a floor; fundamental catalyst reverses the cascade |

---

## Key Difference: Gamma Tsunami vs Normal Volatility Spike

| Aspect | Normal Vol Spike | Gamma Tsunami |
|---|---|---|
| **Cause** | News, economic data, earnings | Mechanical gamma flip; can happen without news |
| **Duration** | Hours to days | Minutes to hours |
| **Magnitude** | VIX +50 to +100% | VIX +100 to +300% (e.g., 17 → 38 or higher) |
| **Reversal** | Can reverse on counter-news | Often exhausts and stabilizes without reversal |
| **Hedging Effectiveness** | Traditional hedges work | Hedges become worthless as vol spikes; worse, they accelerate the move |

**This is why term structure and gamma landscape awareness is non-negotiable for risk management.** You must know where your gamma flip is, what the 0DTE concentration looks like, and whether long-dated gamma will act as a safety net or amplifier.