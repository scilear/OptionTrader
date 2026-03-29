# Module 5b — Greeks, Exposure, and Position Management

## Learning Objectives

- Understand what each Greek measures for a combo, not just a single option.
- Build the Greek profile of each OptionTrader template and know its dominant risks.
- Aggregate exposure across multiple positions and identify concentration.
- Run what-if scenarios before entry and use them as management triggers mid-trade.

---

## 1) Why Greeks Are Different for Vol Surface Trades

For a directional trader, delta dominates: how much does P&L move with the underlying? For a vol surface trader, the frame is different. You are expressing a view about the *shape* of the implied vol surface — skew, curvature, term structure. The primary exposures are:

- **Vega**: sensitivity to changes in implied vol level. A vol surface trade that is net short vega loses if IV rises uniformly — regardless of what skew does.
- **Skew vega / relative vega**: sensitivity to changes in the *difference* between two points on the surface. This is the actual edge the trade is targeting. A SkewFade is not an outright vega trade — it is a bet on relative vega (one wing's IV relative to another).
- **Gamma**: sensitivity to large realized moves. Short-gamma positions profit from stability and suffer from large moves. Long-gamma positions profit from large moves regardless of direction.
- **Delta**: residual directional exposure. Vol combos are often approximately delta-neutral at entry, but this can change quickly with spot moves.
- **Theta**: daily P&L from time decay. Most defined-risk vol structures are net short options (short vega, short gamma), which means they collect positive theta — time works in your favor in calm conditions but accelerates against you if the position is underwater.

These five exposures interact. A position that looks manageable in isolation may behave very differently in motion. Understanding how each template's Greeks evolve is the key to in-trade management.

---

## 2) Greeks from OptionTrader

OptionTrader computes per-leg Greeks using Black-Scholes via `src/core/iv_solve.py::bs_greeks`. Each trade idea exported from the tool includes:

- `delta`: sensitivity of leg price to a 1-point move in the underlying.
- `gamma`: sensitivity of delta to a 1-point move (i.e., second-order spot risk, per point²).
- `vega`: sensitivity of leg price to a 1% (100bp) move in implied vol.

Theta is not currently output by the tool but can be approximated: for a short-premium structure, daily theta ≈ `0.5 × gamma × spot² × vol²` (the Black-Scholes theta-gamma relationship). This means you can estimate your daily time decay from the gamma output.

When reviewing a trade idea, always look at the aggregate Greeks of the full combo (sum across all legs with their respective quantities and signs), not individual legs in isolation.

---

## 3) Greek Profile: SkewFade_PutSpread

**Legs**: sell -0.25Δ put (short), buy -0.10Δ put (long)

| Greek | Sold -0.25P leg | Bought -0.10P leg | Net combo |
|-------|----------------|-------------------|-----------|
| Delta | +0.25 (short put → long delta) | −0.10 (long put → short delta) | **≈ +0.15** |
| Vega | negative (short option) | positive (long option) | **net short vega** (−0.25P has more vega than −0.10P) |
| Gamma | negative (short option) | positive (long option) | **net short gamma** |
| Theta | positive | negative | **net positive theta** |

**What this means in practice:**

The position has modest long-delta exposure: a 1% down move costs you roughly 0.15 × notional × 1%. This is small but meaningful if the move is large.

The net short vega means a uniform IV spike works against you — even if your skew thesis is eventually right. This is the key trap: in a sudden vol expansion, you can lose on vega before you gain on skew normalization. This is why regime context matters: entering this structure when stress is *accelerating* is fighting both delta and vega at the same time.

The short gamma means large moves in either direction hurt. The long -0.10P tail hedge limits how bad the downside can get, but doesn't eliminate the loss.

The positive theta is the compensation: if the underlying stays stable and skew gradually normalizes, you collect theta while the trade converges.

**Primary risk**: spot sells off sharply with skew steepening → adverse delta + vega + gamma simultaneously. This is the archetypical "wrong-regime entry" failure mode.

**What-if table (approximate, per 100-unit notional at entry):**

| Scenario | Delta P&L | Vega P&L | Net |
|----------|-----------|----------|-----|
| Spot flat, skew −1σ normalizes | ~0 | positive (skew-vega gain) | **positive** |
| Spot −1%, IV +2pp | small loss | loss | **negative** |
| Spot +1%, IV flat | small gain | neutral | **small positive** |
| Spot −3%, IV +5pp (stress) | moderate loss | significant loss | **significantly negative** |
| 5 days pass, vol flat | neutral | neutral | **small positive (theta)** |

---

## 4) Greek Profile: Fly_1x2x1

**Legs**: buy -0.25Δ put × 1, sell -0.50Δ put × 2, buy -0.10Δ put × 1

| Greek | Long -0.25P | Short 2× -0.50P | Long -0.10P | Net combo |
|-------|-------------|-----------------|-------------|-----------|
| Delta | −0.25 | +1.00 (2 × +0.50) | −0.10 | **≈ +0.65** |
| Vega | positive | negative × 2 | positive | **near zero to slightly negative** (ATM vega largest) |
| Gamma | positive | negative × 2 | positive | **net negative gamma** (short two ATM, highest gamma) |
| Theta | negative | positive × 2 | negative | **net positive theta** |

**What this means in practice:**

The fly has significant long-delta bias (+0.65) from selling two ATM puts. This is not a delta-neutral position at entry — a large down move has two adverse effects: the delta loss *and* the fact that spot is moving away from the sweet spot (the 0.50Δ body strike where the maximum profit lives).

The near-zero net vega means the fly is relatively insensitive to a uniform IV shift. This is intentional: the thesis is about *shape* (wings vs center), not level. However, if wings and ATM reprice asymmetrically (wings rise while ATM stays, or vice versa), the vega decomposition matters.

The short net gamma is the most significant ongoing risk: the position needs the underlying to stay near the body strike. A large realized move in either direction costs you. This is why flies are particularly sensitive to path and should not be held through high-gamma-risk periods (e.g., immediately before major economic releases).

**Primary risk**: large realized move (high gamma), especially to the downside where delta and gamma losses compound.

**What-if table:**

| Scenario | Delta P&L | Gamma P&L | Net |
|----------|-----------|-----------|-----|
| Spot flat at expiry near body | ~0 | positive convergence | **positive (max payoff zone)** |
| Spot −3% (large down move) | significant loss | gamma loss | **significantly negative** |
| Spot +2% (moderate up move) | gain | small gamma loss | **small net** |
| Wings normalize, ATM stable | 0 | 0 | **positive (vega/skew gain)** |
| ATM IV spikes, wings flat | 0 | 0 | **negative (FLY widens)** |

---

## 5) Greek Profile: ATM_Calendar

**Legs**: sell front ATM call/put (short), buy back ATM call/put (long), sized to approximate vega neutrality

| Greek | Short front ATM | Long back ATM | Net combo |
|-------|----------------|---------------|-----------|
| Delta | ≈ +0.50 (short ATM put) | ≈ −0.50 (long ATM put) | **≈ 0 (near delta-neutral)** |
| Vega | negative (front) | positive (back) | **depends on sizing: targeted near-neutral or slightly long** |
| Gamma | negative (short front — highest gamma) | positive (long back — lower gamma) | **net short gamma** |
| Theta | positive (front decays faster) | negative (back decays slower) | **net positive theta** |

**What this means in practice:**

The calendar is the most theta-sensitive structure of the three. You are short the fast-decaying front option and long the slower-decaying back option. Time works in your favor day-to-day, as long as the underlying stays near the body strike.

Vega decomposition is the key nuance. The calendar is long *back vega* and short *front vega*. If the term KINK resolves because front vol falls (normalization), both theta and relative vega work for you. If front vol stays elevated (event remains priced), you collect theta slowly but the vega thesis doesn't converge. This is why pre-event entries are risky: you may collect theta while the vol thesis goes against you.

The short net gamma means large moves hurt, just as with the fly. The calendar needs stability in the underlying to work.

**Primary risk**: a large underlying move at any point during the hold period, or a persistent event premium that prevents front-back convergence.

**What-if table:**

| Scenario | Theta P&L | Vega P&L | Net |
|----------|-----------|----------|-----|
| 5 days pass, spot flat | positive | neutral | **positive** |
| Front vol −2pp (normalization) | neutral | positive | **positive** |
| Spot ±3% (large move) | neutral | neutral | **negative (gamma loss)** |
| Front vol stays elevated (event) | positive (slow) | negative (no convergence) | **uncertain / small** |
| Post-event vol collapse across curve | neutral | mixed | **depends on relative vol change** |

---

## 6) Aggregating Exposure Across Positions

If you hold multiple positions simultaneously, you need to track the *portfolio* Greeks, not just each trade in isolation.

**Net delta** is the most immediate risk. Sum all leg deltas weighted by notional. If your portfolio has +0.80 net delta, a 1% sell-off costs roughly 0.8% of your options notional before any vol effects.

**Net vega** tells you your overall sensitivity to a vol regime shift. A portfolio that is net short vega across multiple trades can suffer disproportionately in a sudden vol expansion even if each individual trade was sized modestly.

**Concentration check**: ask two questions:
1. Are most of your active trades in the same expiry bucket? Concentrated maturity risk.
2. Are they all in the same alert family (all RR, all FLY)? Correlated vol-surface risk — they will likely move together.

A simple aggregation table to maintain:

| Position | Alert family | Bucket | Net delta | Net vega | Net gamma | Entry date |
|----------|-------------|--------|-----------|----------|-----------|------------|
| Trade A | RR_EXTREME | 30D | +0.15 | −0.20 | −0.05 | — |
| Trade B | FLY_EXTREME | 21D | +0.60 | −0.05 | −0.12 | — |
| Trade C | TERM_KINK | 30D/45D | 0.00 | +0.10 | −0.08 | — |
| **Total** | | | **+0.75** | **−0.15** | **−0.25** | |

This portfolio is net long delta, net short vega, net short gamma. A large down move with a vol spike would be adverse across all three dimensions simultaneously.

---

## 7) What-If Scenarios: Using Greeks to Stress-Test Before Entry

Before entering any position, run these four scenarios mentally (or on paper). Each corresponds to a realistic market shock:

**Scenario 1 — Spot moves ±X% (delta + gamma)**

Estimated P&L ≈ `net_delta × spot_move + 0.5 × net_gamma × spot_move²`

For a +0.15 delta, −0.05 gamma position with a −3% spot move:
`= 0.15 × (−0.03) + 0.5 × (−0.05) × (0.03)² ≈ −4.5% − 0.002% ≈ −4.5%` of notional

If this exceeds your max-loss, the position is sized too large for the scenario.

**Scenario 2 — IV rises uniformly +2pp (vega)**

Estimated P&L ≈ `net_vega × 0.02`

A net vega of −0.20 with a 2pp IV rise → estimated loss of 0.4% of notional per unit. Understand this *before* entry, not after.

**Scenario 3 — Time passes with no move (theta)**

Estimated daily P&L ≈ `net_theta` or approximately `−0.5 × net_gamma × spot² × vol²` (annualized, divide by 365).

If you are net short gamma and net short vega, theta is your return source. Know how many days of theta you need to recover a 1% adverse move scenario.

**Scenario 4 — Your thesis reverses (signal degrades)**

What happens if the vol signal that justified entry begins to fade? For example, RR25 stops being extreme or persistence drops. This is not a Greek scenario — it is a *thesis degradation* scenario. Pre-commit: at what threshold do you exit even if mark-to-market is break-even?

---

## 8) Adjustment Triggers

The purpose of pre-trade scenarios is to create *pre-committed adjustment rules*, not react emotionally mid-trade.

**Delta trigger**: if net portfolio delta exceeds a predefined limit (e.g., ±0.5 normalized to your options notional), consider a delta hedge or size reduction — regardless of your vol thesis conviction.

**Vega trigger**: if the portfolio is net short vega and a vol regime shift is underway (IV rising, regime moving toward Stress), reduce net vega exposure before the loss compounds.

**Gamma trigger**: if a large realized move puts your short-gamma positions materially underwater, do not double down. The short-gamma loss is geometric — it accelerates with move size.

**Signal degradation trigger** (most important): if the alert that prompted entry no longer meets the persistence threshold, or `zscore_worst` has fallen below the configured threshold, the statistical basis for the trade has weakened. This is your primary exit signal, independent of P&L.

**P&L stop**: define a max-loss per position at entry (required by Gate 5 of the decision process). Honor it. Vega and gamma losses can compound faster than linear.

**Rule**: if two or more triggers fire simultaneously, exit the position. Do not reason your way around coincident adverse signals.

---

## 9) Drill

For each of the three OptionTrader templates:

1. Write the net delta, vega, and gamma profile in one sentence (no table needed).
2. Identify the single market scenario that is most adverse for that profile.
3. Define one numeric trigger (e.g., "if net delta of portfolio > X") that would cause you to reduce or exit.
4. For a hypothetical portfolio of two concurrent trades (e.g., SkewFade + Calendar in the same bucket), aggregate the Greeks and run Scenario 1 and 2 from Section 7. Is the combined exposure acceptable?
