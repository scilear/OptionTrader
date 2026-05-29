# OptionTrader S4-03 Regime Logic Redefinition and Adversarial Review

Date: 2026-05-12
Author: PM/logic redesign pass
Status: Paper design complete, ready for implementation plan

## 1) Plain-language goal

OptionTrader emits an alert when options-surface metrics (risk reversal, fly, term slope) become
abnormal enough and persist long enough. A regime label is meant to answer:

- is this a calm market,
- a transition market,
- or a stress market,

so that we can gate alerts and evaluate performance by market state.

The S4-03 claim to prove is:

- regime logic adds measurable predictive value over baseline,
- without inflating low-quality alerts.

## 2) What is currently broken (confirmed)

Confirmed in local EOD truth DB and current code paths:

1. Regime persistence is not run in S4 track materialization.
   - `scripts/materialize_s4_tracks_from_eod.py` computes snapshots but does not call
     `compute_regime_state()`.
2. Alert fallback masks missing regime rows.
   - `src/core/compute_snapshot.py` uses `"Neutral"` when no matching regime row exists.
3. Result: validation artifacts can report only `Neutral` even when true regime table would have
   `Calm`/`Transition`/`Stress` rows.
4. Regime table itself can be populated and does produce all three labels.
   - After recompute in `/mnt/Data/EVA/optiontrader_eod_truth.duckdb`: `Calm=2463`, `Stress=689`,
     `Transition=285`.
5. Additional design weakness: percentile features are computed over the full sample, which can
   leak future distribution information into past labels.

Conclusion:

- The "all Neutral" outcome is primarily an implementation/integration defect.
- The regime design still needs hardening for causality and independence.

## 3) Redefined regime logic (V1)

### 3.1 Regime definition

For each day `t`, compute independent stress components from information available at or before `t`:

- `vix_pct_t`: trailing percentile of VIX level.
- `rv20_pct_t`: trailing percentile of 20-day realized volatility.
- `drawdown_t`: rolling drawdown from trailing high.
- `event_score_t`: scheduled macro-event severity on day `t`.
- `xasset_stress_pct_t`: trailing percentile of an external stress proxy not equal to VIX.

Map each component to levels `{0,1,2}` using calibrated thresholds. Compute weighted score:

- `score_t = sum(level_i * weight_i) / sum(weight_i)`

Label:

- `Calm` if `score_t <= calm_max`
- `Stress` if `score_t >= stress_min`
- otherwise `Transition`

### 3.2 Governance rules

1. No fallback to `Neutral` for missing regime rows.
   - Missing regime must be explicit: `Unknown`.
2. `Unknown` cannot pass release falsification gates.
3. Regime rows must be generated before snapshot compute in every materialization path.
4. Regime assignment must be run-scoped or snapshot-scoped (no cross-run contamination).

### 3.3 Success criteria

The regime subsystem is valid only if all are true:

1. Coverage: alert population includes all required labels or explicitly fails gate with reason.
2. Causality: no feature uses forward data.
3. Independence: at least one non-RV, non-VIX component has non-trivial contribution.
4. Utility: regime-stratified precision is not driven by one accidental bucket.

## 4) Adversarial review - Round 1

### Attack A: Hidden missing-data bug

Claim:

- If regime rows are missing, fallback label can silently produce fake coverage.

Finding:

- Valid attack. Current fallback to `Neutral` hides data-generation failures.

Action:

- Replace fallback label with `Unknown` and hard-fail regime coverage gate if `Unknown > 0` in
  evaluation set.

### Attack B: Future leakage via full-sample percentiles

Claim:

- Ranking percentiles on the whole time series gives past dates information about future
  distribution.

Finding:

- Valid attack. Current percentile logic is vulnerable to lookahead.

Action:

- Use trailing/expanding percentile computed only on history available at each date.

### Attack C: Cross-run contamination

Claim:

- Shared `regime_state` table can mix baseline/candidate contexts and mutate labels outside run
  lineage control.

Finding:

- Valid attack in principle.

Action:

- Persist regime labels per snapshot (preferred) or add run/profile scoping to regime rows used for
  alert labeling.

### Attack D: Fake independence

Claim:

- If stress proxy equals VIX (or near-perfectly tracks it), multi-signal is cosmetic.

Finding:

- Valid attack. In current config, stress proxy ticker is `^VIX`; independence is weak.

Action:

- Use a distinct cross-asset proxy and report rolling correlation vs VIX and RV.

## 5) Revised logic after Round 1 (V2)

1. Mandatory precompute step:
   - `compute_regime_state` (or successor) must run before `compute_for_snapshot` in all replay and
     materialization scripts.
2. Missing regime handling:
   - `Unknown` label, never silently remapped to `Neutral`.
3. Causality-safe features:
   - trailing percentiles only.
4. Scope-safe labeling:
   - label assignment from snapshot-date mapping produced in same run context.
5. Independence monitor:
   - publish component contribution and correlation diagnostics in artifact.

## 6) Adversarial review - Round 2

### Attack E: Class imbalance makes gate meaningless

Claim:

- If 90% of alerts are Calm, aggregate precision can improve while regime logic is still useless.

Finding:

- Valid attack.

Action:

- Add minimum per-regime outcome counts for gate validity (not just alert counts).

### Attack F: Threshold overfitting

Claim:

- Thresholds tuned on full span may overfit and fail in later periods.

Finding:

- Valid attack.

Action:

- Calibrate thresholds only on training subwindow; freeze for test windows.

### Attack G: Event feature contamination

Claim:

- Event calendar may embed hindsight edits.

Finding:

- Plausible attack.

Action:

- Version event file with immutable snapshot hash and effective dates.

## 7) Final logic (V3) to implement

### 7.1 What a regime is

Regime is a causal daily market-state label derived from independent stress features, produced before
alert scoring, with explicit unknown-state handling and auditable decomposition.

### 7.2 Required release-gate validity checks

A regime falsification run is invalid unless:

1. `Unknown` alert share is zero.
2. All required regimes have minimum outcome count.
3. Thresholds are frozen before test period.
4. Feature correlations and contribution shares are reported.

### 7.3 Decision policy

1. If validity checks fail -> verdict `invalid_evidence`, not `pass`/`fail`.
2. If valid and no incremental lift -> `no_incremental_edge_observed`.
3. If valid and lift present -> `incremental_edge_confirmed`.

## 8) Implementation sequence (next)

1. Fix labeling integrity:
   - remove `Neutral` fallback behavior,
   - add `Unknown` handling and explicit gate checks.
2. Fix materialization path:
   - ensure regime generation runs in S4 track pipeline.
3. Fix causality:
   - replace full-sample percentiles with trailing-only percentiles.
4. Add validity diagnostics:
   - per-regime outcome counts, unknown-share, contribution/correlation tables.
5. Re-run locked windows and full span under identical contract.

## 9) Why this addresses the user concern

This redesign separates two failure modes that were previously conflated:

- implementation failure (missing regime rows -> fake `Neutral`), and
- model-value failure (regime logic may still not add predictive edge).

That allows a correct conclusion:

- first fix evidence validity,
- then judge whether regime logic is valuable.
