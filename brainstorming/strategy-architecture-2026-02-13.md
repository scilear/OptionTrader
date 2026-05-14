---
session: party-mode
date: 2026-02-13
participants: [Victor (Innovation Strategist), Dr. Quinn (Problem Solver), Carson (Brainstorming Coach)]
topic: Options Strategy Selection for High Sharpe & High Calmar
phase: Strategy Architecture
status: complete
---

# Options Strategy Architecture: Phase 1 & Phase 2

**Date:** 2026-02-13
**Led by:** Victor (Innovation Strategist) ⚡
**Supporting:** Dr. Quinn (Problem Solver) 🔬, Carson (Brainstorming Coach) 🧠
**Objective:** Select and detail options strategies optimized for high Sharpe ratio and high Calmar ratio

---

## Guiding Principles

- **High Sharpe** = consistent positive returns relative to volatility
- **High Calmar** = returns don't come at the cost of catastrophic drawdowns
- Combined implication: **cannot be a net seller of tail risk without strict regime gating**
- Every strategy evaluated through this dual lens

---

## Phase 1: Foundation Strategies

### Strategy 1: Regime-Conditioned Skew Fade (Bounded)

**Thesis:** RR25 z-score extremes mean-revert in calm/neutral regimes. Sell rich put skew with defined risk.

**Structure:** Put spread (sell 25-delta put, buy 10-delta put), optionally financed by a small call spread.

**Why it scores well on Sharpe/Calmar:**
- Defined max loss (spread width minus credit) caps drawdowns → Calmar
- In calm regimes, skew mean-reverts ~60-70% of the time within 10 days → Sharpe
- Persistence filter (2+ snapshots) and momentum guard (3-day z-change >= -0.5) eliminate false signals

**Entry Rules:**
- Calm regime (score 0-2): Z_RR25 <= -2.0
- Transition regime (score 3-4): Z_RR25 <= -2.5
- Stress regime (score 5-6): **NO ENTRY** (Calmar protector)

**Confirmations:**
- Skew momentum not accelerating: ΔZ_RR25_3d >= -0.5
- No extreme term inversion: Z_TS(front,next) < +2.0 (optional)

**Tradability Gate:**
- Per-leg spread filter: (ask-bid)/mid < threshold (8-12% for SPX wings)
- Strategy pessimistic fill (buy at ask, sell at bid) must preserve positive edge

**Exit Rules:**
- Take profit: Z_RR25 crosses above -1.0
- Stop loss: Z_RR25 goes below -3.0
- Time stop: 10 trading days
- Spot stop: SPX drops > 4% from entry or short put reaches 40-delta

**Assessment:** *Bread and butter. Unsexy. Consistent. Hard to blow up.*

---

### Strategy 2: Curvature Mean-Reversion Fly

**Thesis:** When Fly25 z-score spikes (wings too rich vs ATM), sell curvature via butterfly or broken-wing fly. Slower to mean-revert than skew, but more bounded in risk.

**Structure:** 1x2x1 put fly (centered near ATM-forward) or broken-wing fly for cheaper entry.

**Why it scores well:**
- Butterflies have inherently capped risk on both sides → excellent for Calmar
- Curvature overshoots often driven by hedging flow, not structural regime change → cleaner mean-reversion
- Low correlation with skew trades → portfolio diversification lifts Sharpe

**Entry Rules:**
- Z_Fly25 >= +2.0
- |Z_RR25| <= 2.0 (avoids confusing curvature with skew)
- Persistence: 2+ snapshots
- Regime: Calm or Transition only

**Tradability Gate:**
- Wing strikes must pass spread filter (leg-level)
- Strategy pessimistic fill must be reasonable

**Exit Rules:**
- Take profit: Z_Fly25 reverts to +1.0
- Stop loss: Z_Fly25 worsens to +3.0
- Time stop: 10 trading days
- Delta stop: |Δ| exceeds 0.25

**Assessment:** *The diversifier. Doesn't fire often, but risk/reward is clean. Excellent Calmar contribution.*

---

### Strategy 3: Event Premium Calendar (Sell Rich Front Vol)

**Thesis:** When front-month ATM IV is elevated vs. back month (Z_TS >= +2.0) — typically pre-FOMC/CPI — sell the rich front via ATM calendar spread.

**Structure:** Sell front ATM (14-30 DTE), buy back ATM (30-60 DTE).

**Why it scores well:**
- Event premium crushes are fast and predictable (post-event normalization) → high hit rate → Sharpe
- Calendar max loss is the debit paid → naturally bounded → Calmar
- Caveat: holding through event with spot gap exposes short gamma in front leg

**Entry Rules:**
- Z_TS(front, back) >= +2.0
- Regime NOT Stress (term inversion can persist in stress)
- Skew not accelerating (Z_RR25 not worsening rapidly)

**Critical Guard:** Auto-flag FOMC/CPI weeks. Decompose variance premium before trading — the signal may be rational event premium, not a dislocation.

**Exit Rules:**
- Take profit: Z_TS normalizes to +1.0
- Stop loss: Z_TS worsens to +3.0
- Time stop: 7-12 trading days (calendars stagnate)
- Delta stop: |Δ| exceeds 0.20

**Assessment:** *Event calendars are seductive because mean-reversion is visible. Tail risk is 'spot gaps through your strike.' Size accordingly.*

---

## Phase 1: Portfolio Construction (The Sharpe/Calmar Multiplier)

**Key Insight (Dr. Quinn):** The three strategies have **low correlation to each other**:
- Skew fade = skew bet (put wing vs call wing)
- Fly = curvature bet (wings vs belly)
- Calendar = term structure bet (front vs back)

Running all three simultaneously, regime-gated, with independent sizing and risk limits, creates natural diversification that's hard to achieve with a single strategy. Combined Sharpe will be materially higher than any individual leg.

**Position Sizing Rule for Calmar:**
- Max loss per trade: 1-2% of portfolio
- Max aggregate exposure: 5% of portfolio
- This caps drawdown mechanically

---

## Phase 2: Original / Innovative Ideas (Deferred)

### Idea 2A: Cross-Signal Confluence Trading

When multiple signals fire simultaneously (e.g., RR extreme AND Fly extreme AND term kink), the edge may be larger and faster to realize. Build a confluence scoring engine that detects multi-signal clusters and suggests hybrid structures (e.g., calendar fly, diagonal risk reversal).

**Why deferred:** Requires validated single-signal backtests first. Confluence without calibration = overfitting.

### Idea 2B: Regime Transition Alpha

Trade the *transition* rather than within a regime. Detect Calm → Transition shift (VIX percentile crossing 40th, RV accelerating) and position for skew steepening rather than fading it. Flips Strategy 1 — buy skew when regime is shifting.

**Why deferred:** Requires regime model validation + enough historical transitions to be statistically credible. Powerful because it front-runs the crowd.

### Idea 2C: Signal Half-Life Adaptive Sizing

Use backtest event-study data (reversion time, MAE, MFE by regime) to dynamically size positions. Faster historical reversion = larger size. A volatility-of-signal adjustment that directly targets Sharpe improvement.

**Why deferred:** Needs 6+ months of live signal tracking to calibrate without overfitting.

### Idea 2D: Dealer Gamma Overlay (GEX Proxy)

Add crude estimate of dealer positioning (spot vs large OI strikes, gamma exposure sign). Long gamma → vol dampens → skew reverts faster → more aggressive entry. Short gamma → amplification risk → tighten stops or sit out.

**Why deferred:** Higher data requirements (detailed OI analysis), and v1 regime model may capture 80% of this signal already.

### Idea 2E: Volatility Risk Premium (VRP) Harvest Layer

Systematically sell ATM straddles/strangles when realized vol is persistently below implied (VRP positive), regime-conditioned. Classic "short vol" carry trade, gated by regime model.

**Why deferred:** Well-known and crowded. Works, but edge is thin and tail risk is real. Only add after Phase 1 proves regime model.

---

## Strategy Summary Table

| Strategy | Phase | Signal | Structure | Sharpe Driver | Calmar Driver |
|---|---|---|---|---|---|
| Skew Fade (bounded) | 1 | RR25 z <= -2.0 | Put spread +/- call spread | High hit rate, regime-gated | Defined max loss, stress lockout |
| Curvature Fly | 1 | Fly25 z >= +2.0 | Butterfly / BWF | Low correlation diversifier | Capped risk both sides |
| Event Calendar | 1 | TS z >= +2.0 | ATM calendar | Fast post-event normalization | Max loss = debit paid |
| Cross-Signal Confluence | 2 | Multi-signal cluster | Hybrid structures | Higher edge per trade | Requires calibration |
| Regime Transition Alpha | 2 | Regime shift detection | Buy skew/vol | Front-runs crowd | Novel, needs data |
| Adaptive Sizing | 2 | Half-life metrics | Size modulation | Direct Sharpe targeting | Needs live tracking |
| Dealer Gamma Overlay | 2 | GEX proxy | Filter/modifier | Timing improvement | Regime model overlap |
| VRP Harvest | 2 | RV < IV persistently | Short straddle/strangle | Carry income | Crowded, thin edge |

---

## Key Takeaway (Carson — Brainstorming Coach)

The *learning loop* IS the edge. Phase 1 generates live signals. You track which you took, which you skipped, and why. Phase 2's real moat isn't a fancier model — it's that the replay/post-mortem system makes you smarter every week. No commercial tool does that well. That's the unfair advantage.

---

## Next Steps

- Validate Phase 1 strategies via backtest event-study (feature-level first, then structure P&L)
- Build implementation plan for the technical platform
- Proceed to technical architecture and development workflow
