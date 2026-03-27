# Module 3 - Alert-to-Trade Process (Rationale-First)

## Learning Objectives

- Convert signal observations into explicit decisions.
- Make reasoning auditable and repeatable.
- Reduce emotional and narrative-driven trade errors.

## The Five-Gate Decision Process

Before using the gates, define the unit of analysis:

- one alert,
- one bucket,
- one snapshot window (current + recent confirmations).

Each gate should be supported by explicit evidence, not intuition labels.

Current default parameters (from `config/config-v1.yaml`):

- `alerts.z_threshold = 2.0`
- `alerts.persistence_snapshots = 2`
- `quality.spread_gate_pct = 0.15`
- `metrics.expiry_buckets_days = [21, 30, 45]`

This means the default signal gate is not discretionary: by construction, the alert already passed a 2-sigma + persistence condition.

### Gate 1 - Signal Quality

Questions:

- Which metric family is driving the alert?
- Are both `zscore_mid` and `zscore_worst` supportive?
- Is persistence requirement met?

How to determine `pass`:

- alert is linked to one clear family (`RR_EXTREME`, `FLY_EXTREME`, `TERM_KINK`),
- `zscore_mid` exceeds configured threshold,
- `zscore_worst` also exceeds threshold in same directional sense,
- persistence count meets configured requirement.

Code-level logic reference:

- alert construction: `src/core/alerts.py`
- insertion and additional filtering: `src/core/compute_snapshot.py`

Practical note:

- If an alert is present in `alerts` table, Signal gate is usually pre-passed.
- Your task is to verify whether the signal remains trustworthy after data/regime/execution/risk gates.

What `fail` means:

- disagreement between mid and worst,
- or threshold/persistence not satisfied.

If no -> do not proceed.

### Gate 2 - Data Integrity

Questions:

- Is coverage complete for expected buckets?
- Is cadence stable enough to infer pattern shape?
- Did source switch around the signal window?

How to determine `pass`:

- expected bucket metrics are present (no missing key bucket for evaluation),
- cadence is interpretable (`Points`, `median gap`, `max gap` not dominated by large discontinuities),
- no suspicious ingest artifacts around the signal,
- source transitions are either absent or clearly explained.

Concrete evidence fields to inspect:

- from logs: `iv_points=...`, `metrics_rows=...`
- from chart caption: `Points`, `median gap`, `max gap`
- from chart coloring: `source`

What `fail` means:

- sparse/intermittent points that can create false shapes,
- coverage drop (e.g., weak `iv_points` / missing metric rows),
- unresolved ingest anomalies.

If uncertain -> downgrade to `Watch` or `Research`.

### Gate 3 - Regime and Event Context

Questions:

- Is this likely mean-reversion context or continuation context?
- Are there near-term catalysts that can justify persistent distortion?
- Does current regime suppress this alert family?

How to determine `pass`:

- current regime does not conflict with alert family policy,
- event calendar does not provide a stronger competing explanation,
- chosen thesis (reversion or continuation) matches observed context.

Concrete evidence fields:

- `regime_label` in alert detail,
- event calendar notes in your journal,
- alert family policy checks (for example, `RR_EXTREME` may be suppressed in stress context in current compute logic).

What `neutral` means:

- regime does not strongly confirm or reject thesis,
- but no explicit contradiction exists.

What `fail` means:

- regime/event context directly contradicts thesis,
- or policy suppresses that alert family in current regime.

If context conflicts with thesis -> reject or delay.

### Gate 4 - Execution Realism

Questions:

- Is tradability score acceptable?
- Are spread conditions consistent with your structure?
- Is slippage likely to dominate expected edge?

How to determine `pass`:

- tradability score is inside your allowed range,
- quoted spreads are acceptable for intended combo,
- estimated friction leaves positive expected edge.

How tradability is currently computed in code (`src/core/tradability.py`):

- compute median relative spread across valid quotes,
- `tradability_score = 1 - min(1, median_spread / spread_gate_pct)`.

Interpretation:

- score near `1.0`: spreads are tight relative to your gate,
- score near `0.0`: spreads are wide; execution risk high.

What `fail` means:

- spreads/slippage likely consume most of theoretical edge,
- or intended structure is not realistically fillable.

If execution is weak -> keep as research candidate only.

### Gate 5 - Risk Definition

Questions:

- Is max loss known before entry?
- Is invalidation condition explicit?
- Is position size compatible with portfolio exposure?

How to determine `pass`:

- maximum loss is explicitly defined,
- invalidation condition is specific and testable,
- position sizing respects portfolio and correlation limits,
- planned action on invalidation is pre-committed.

Minimum required risk fields in your decision log:

- max loss,
- invalidation trigger,
- size rule,
- action on invalidation.

What `fail` means:

- undefined downside,
- vague invalidation,
- or size inconsistent with risk limits.

If risk is not explicit -> no trade.

## Decision Labels (Required)

Every candidate must end with one label:

- `Trade now`
- `Watch for confirmation`
- `Research only`
- `Reject`

Reasoning must be written in one paragraph minimum.

## Gate Evidence Card (Required)

Use this compact structure in logs:

- `Signal gate`: pass/fail + evidence (`zscore_mid`, `zscore_worst`, persistence)
- `Data gate`: pass/fail + evidence (coverage, cadence, source)
- `Regime gate`: pass/neutral/fail + evidence (regime label, event context)
- `Execution gate`: pass/fail + evidence (tradability, spread/slippage)
- `Risk gate`: pass/fail + evidence (max loss, invalidation, size)

Do not write gate status without evidence.

## From Gate Results to Decision (Deterministic Mapping)

Use this mapping to avoid fuzzy conclusions:

- **Trade now**:
  - Signal pass, Data pass, Execution pass, Risk pass,
  - Regime is pass or neutral with explicit rationale.
- **Watch for confirmation**:
  - Signal pass,
  - one non-critical gate uncertain (usually Regime neutral or minor Data uncertainty),
  - no hard fail in Execution/Risk.
- **Research only**:
  - Signal pass but Execution fails or Data uncertainty is material.
- **Reject**:
  - Signal fail, or Risk fail, or strong Regime contradiction.

Hard-stop rule:

- Any **Risk fail** -> `Reject` regardless of other gates.

## Why This Process Works

- It forces separation between observation and action.
- It prevents single-metric overreaction.
- It creates evidence for post-trade review and process improvement.

## Drill

Take 10 alerts and produce a one-page decision log containing:

- gate outcomes,
- final label,
- invalidation condition,
- one sentence on what could make the decision change.
