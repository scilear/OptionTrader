# Module 2 — The Volatility Surface: Decomposition and Why It Matters

## Learning Objectives

- Understand why the vol surface has shape, not just a level.
- See why RR25, FLY25, and TERM are the right decomposition, not arbitrary choices.
- Build intuition for what each metric captures economically, not just mathematically.
- Understand the design decisions behind how OptionTrader measures and alerts on these metrics.

---

## 1) Why the Surface Has Shape

Implied volatility is not a single number — it varies by strike and by expiry. If markets believed future returns were normally distributed, every option on the same underlying and same expiry would have the same implied vol. They don't.

Two structural forces shape the surface permanently in equity index options:

**Asymmetric demand for insurance.** Large institutional investors hold equity portfolios and buy puts to hedge drawdowns. This demand for downside protection structurally exceeds demand for upside speculation. The result: put options are persistently more expensive (in vol terms) than equidistant calls. This is not a pricing anomaly waiting to be arbitraged — it reflects a structural premium that compensates option sellers for the asymmetric risk they take on. In SPX options specifically, this put-side premium has persisted for decades.

**Jump and volatility uncertainty.** Markets know that implied vol itself is uncertain, and that crashes can be sudden and large. Options priced under these conditions need to include compensation for fat tails even beyond what a normal distribution would imply. This makes *both* wings more expensive than ATM, not just the put side.

These two forces operate independently. The first makes the surface *asymmetric* (one side more expensive than the other). The second makes it *curved* (both wings elevated relative to ATM). A good decomposition separates them.

---

## 2) Why Three Metrics, and Why These Three

The full volatility surface has many degrees of freedom — every strike-expiry combination is its own data point. For practical analysis, you need a compact representation that:

- captures the economically meaningful dimensions,
- is stable enough to build a signal on,
- aligns with how professional desks actually communicate vol.

RR25, FLY25, and TERM meet all three criteria. They are approximately *orthogonal*: knowing one tells you relatively little about the others. A surface can be asymmetric without being unusually curved. It can be in steep backwardation without being unusually skewed. This orthogonality is what makes them useful as separate signal families.

They are also professional conventions inherited from FX vol markets. Vol traders quote and risk-manage in these coordinates. That means the metrics are liquid (desks actually trade these), interpretable (there's shared meaning), and comparable across time.

---

## 3) RR25 — Skew (Asymmetry)

### Formula

```
RR25(T) = IV(+0.25Δ call, T) − IV(−0.25Δ put, T)
```

In OptionTrader: `rr25_mid` (midpoint-based), `rr25_worst` (pessimistic bid/ask version).

### What it captures

RR25 measures the premium of one wing over the other. For SPX, it is almost always negative: put-side IV exceeds call-side IV. The more negative it is, the steeper the left skew.

Intuitively: how much more expensive is crash insurance than an equivalent bet on a rally?

### Why 25-delta specifically

25-delta is a market convention that balances two competing needs. Go too close to ATM (50-delta) and you're measuring vol level, not shape. Go too far OTM (10-delta or beyond) and liquidity thins out, quotes become unreliable, and the signal is dominated by noise. The 25-delta strike sits in the region where institutional hedging concentrates — it's deep enough to show tail pricing but liquid enough to trust.

The 10-delta points (also captured by OptionTrader) are more tail-focused and appropriate for measuring extreme fear regimes, but they are noisier and require stricter data quality checks.

### Why delta-based rather than strike-based

If SPX moves from 5000 to 4500, the "25-delta strike" moves with it. A fixed absolute strike (e.g., 4750) would change from 25-delta to something else. Delta-based reference points are sticky in *moneyness space* — they represent a roughly constant distance from the current probability mass, which makes the time series much more interpretable.

### Why SPX skew is persistently negative — and what that means for signals

The structural hedging demand described in Section 1 is the reason. SPX put demand consistently exceeds supply of naked put sellers willing to absorb it, so the market pays a skew premium. This is a real cost that option sellers collect over time in exchange for downside exposure.

This has two implications. First, the *absolute level* of RR25 is not a signal — a value of -4% can be completely normal. Second, the interesting question is always *how extreme is the current level relative to recent history*? This is why OptionTrader uses z-scores, not absolute thresholds.

### Same RR25, different stories

Two snapshots can show identical RR25 with entirely different mechanics:

- **Put-driven widening**: put IV rises, call IV is stable → fear-driven skew expansion (hedging demand surge or spot shock).
- **Call-driven compression**: call IV falls, put IV is stable → upside premium is leaving (rally complacency, call selling pressure).
- **Parallel shift**: both wings move but put moves more → mixed repricing, often in regime transitions.

These have different implications for structure selection. A put-driven widening might normalize as fear subsides; a call-driven compression might have a different reversal path. OptionTrader reports the RR25 spread; decomposing which wing moved requires inspecting the individual IV points or comparing against historical wing levels.

### The z-score: why absolute thresholds fail

RR25 = -0.08 means something different in a calm market than in a stress regime. In a calm regime, that level might be 3 standard deviations extreme. In a stress regime it might be unremarkable. A fixed threshold like "alert if RR25 < -0.06" will fire constantly in stress and never fire in calm.

OptionTrader solves this with a 60-day rolling z-score. The window is long enough to capture a meaningful local distribution (roughly one quarter), short enough that it doesn't average across very different regimes. An alert fires when the current value is extreme *relative to its own recent context*, not against any universal benchmark.

---

## 4) FLY25 — Smile Curvature (Convexity)

### Formula

```
FLY25(T) = 0.5 × (IV(+0.25Δ call, T) + IV(−0.25Δ put, T)) − IV(ATM, T)
```

In OptionTrader: `fly25_mid`, `fly25_worst`.

### What it captures

FLY25 measures how elevated the *average* wing is relative to the center of the smile. It is a proxy for smile curvature.

- High FLY25: both wings are expensive relative to ATM → the market prices large moves (in either direction) as more probable than the ATM IV alone would imply.
- Low (or negative) FLY25: wings are compressed relative to center → the distribution implied by option prices is narrower in the tails than usual.

Note the key difference from RR25: FLY25 is about *both* wings together. RR25 is about the *difference* between wings. A surface can have strong RR25 (asymmetric) with low FLY25 (flat overall smile), or high FLY25 (elevated wings) with RR25 near zero (symmetric). They are separate dimensions.

### Economic interpretation

Elevated FLY25 often reflects:
- event-driven tail-risk pricing (earnings, macro announcements, FOMC),
- general vol-of-vol stress (uncertainty about future uncertainty),
- supply/demand imbalances in wing options.

Suppressed FLY25 relative to history can indicate:
- complacency or post-event relaxation of tail pricing,
- opportunity if tails are genuinely underpriced vs recent norms.

### FLY25 decomposition matters

Before trading on a FLY signal, determine whether the move is wing-led or center-led:
- `W = 0.5 × (C25 + P25)` — the average wing
- `A = ATM`
- FLY25 = W − A

If FLY25 is high because wings rose, the interpretation is tail demand. If FLY25 is high because ATM fell while wings were stable, the interpretation is ATM compression (possibly a liquidity or data artifact). These have very different trade implications.

---

## 5) TERM Slope — Intertemporal Structure

### Formula

```
TERM(T_i, T_j) = IV_ATM(T_i) − IV_ATM(T_j)    where T_i < T_j
```

In OptionTrader, computed across expiry buckets (e.g., 21D, 30D, 45D): `term_slope_mid`, `term_slope_worst`.

### What it captures

TERM slope measures how steeply the surface rises or falls as you look at different maturities at the same delta (ATM).

- Positive (front > back): near-term uncertainty exceeds long-term. Typical in two cases: (1) known near-term event (earnings, FOMC, election) causes front vol to be bid, (2) spot stress has spiked near-term fear.
- Negative (back > front): long-term uncertainty exceeds near-term. Typical in calm markets where the near-term outlook is stable but long-run uncertainty is elevated.
- A **kink** — a non-monotone shape, where one maturity is above or below its neighbors in a way inconsistent with the surrounding structure — is what OptionTrader's `TERM_KINK` alert targets.

### Why kinks are more interesting than level slopes

A steady upward or downward slope is often rational and persistent. A kink — where one specific expiry is out of line with its neighbors — is more likely to reflect transient mispricing, event premium decay, or a supply/demand imbalance in one specific expiry. The kink premise is that the local distortion has a higher probability of resolving than a full slope does.

### Why term interpretation is the most context-sensitive

Term structure is highly sensitive to the event calendar. A large front-maturity premium one week before a Fed decision is rational and may persist until after the announcement. The same pattern one week after the decision may represent premium that should decay. OptionTrader cannot read the calendar — that judgment is yours. When you see a `TERM_KINK` alert, the first question is always: does the event calendar explain this kink, or is it truly an unexplained dislocation?

---

## 6) Mid vs Worst: The Execution Reality Gate

### Why mid alone is not enough

When OptionTrader computes `rr25_mid`, it uses implied vols derived from the midpoint of each option's bid/ask spread. This is a theoretical value — in live trading, you buy options at the ask and sell at the bid. The spread between bid and ask can be substantial, especially in wings and in lower-liquidity expiries.

The worst-case variants (`rr25_worst`, `fly25_worst`, `term_slope_worst`) compute the metric assuming every leg is filled at the unfavorable side. If you're buying the +0.25Δ call as part of a combo, the worst-case uses the ask IV. If you're selling the -0.25Δ put, the worst-case uses the bid IV.

### What agreement/disagreement tells you

- **Mid and worst agree** (both show extreme z-scores in the same direction): the signal is robust to realistic execution. The dislocation is large enough that even assuming adverse fills, the metric is extreme.
- **Mid extreme, worst weak or reversed**: the signal may be a *spread artifact* — the apparent dislocation lives in the bid-ask spread, not in the underlying option pricing. This is a common failure mode for options with wide, infrequently updated quotes.

This is why Gate 1 in the five-gate decision process requires *both* `zscore_mid` and `zscore_worst` to pass, and why divergence between them is a hard downgrade signal in OptionTrader.

---

## 7) Putting It Together: What the Tool Measures and Why

OptionTrader does not attempt to model the full volatility surface. It computes three targeted metrics per expiry bucket — RR25, FLY25, TERM slope — that each represent one economically meaningful dimension of vol surface behavior. It then measures whether the current value is extreme relative to its own recent history (z-score), whether that extremeness is durable (persistence gate), whether it survives realistic execution friction (worst-case gate), and whether the signal is coherent with current market regime.

This multi-gate architecture exists precisely because individual metrics can fire for bad reasons: sparse data, cadence artifacts, source transitions, wide spreads, event repricing. Each gate is a filter for one class of false signal.

The OptionTrader Metric Explorer gives you direct access to all of this. When you see a large move in `rr25_mid` on the chart:

1. Switch to `rr25_worst` — does it confirm? If not, it's probably a spread artifact.
2. Check the chart caption (`Points`, `median gap`, `max gap`) — is the shape built from dense or sparse data?
3. Switch between Timeline and Snapshot sequence modes — does the shape survive or disappear?
4. Go to Alert Detail for the corresponding alert — what did the pipeline's gate evidence show?

The chart is a starting point, not a conclusion.

---

## 8) Drill

For 5 historical alerts in OptionTrader:

1. For each, identify the primary metric driver (RR/FLY/TERM) and write one sentence on *what market behavior could have caused this level*.
2. Check whether the worst-case variant confirms. Write one sentence on what the agreement or divergence implies.
3. Sketch whether the move is more consistent with a fear-driven cause, an event-premium cause, or possibly a data artifact.
4. Choose one decision label (`Trade`, `Watch`, `Research`, `Reject`) and write the one fact that would most change your label.
