# OptionTrader Next Level Plan

Date: 2026-04-27
Scope: Evolve OptionTrader from a volatility feature pipeline into an execution-aware, auditable signal system for SPX options.

## Outcome Definition

The target is not "more alerts". The target is:

- execution-adjusted expectancy that is positive out-of-sample,
- stable behavior across regimes,
- strict auditability from raw quotes to final decision label.

## Program Principles

1. Edge before templates: no trade idea without quantified edge-after-friction.
2. Uncertainty first-class: every key metric carries confidence and failure state.
3. Fail closed: if data quality is insufficient, emit no tradeable signal.
4. Regime independence: regime model must include independent forward-looking signals.
5. Reproducibility and governance: every run is attributable to code+config+data state.
6. Falsification over elaboration: any new component must beat baseline in ablation.
7. Uncertainty is a control variable: it can block decisions, never justify them.

## 12-Week Delivery Plan

### Sprint 1 (Week 1): Baseline freeze and observability

Goal:
- Create a reproducible baseline and decision-trace foundation.

Primary changes:
- `src/core/compute_snapshot.py`: add gate-by-gate decision trace payload.
- `src/db/schema.sql`: add run metadata table and trace-friendly columns.
- `scripts/run_pipeline.py`: persist run metadata (`run_id`, config hash, code version).
- `src/core/config.py`: stable config digest utility.
- `src/core/iv_solve.py`, `src/core/metrics.py`: integrate non-zero rates and dividend yield as baseline pricing inputs.

Deliverables:
- Repeatable run manifest.
- Alert-level reason codes for pass/fail per gate.
- Pricing-input baseline (rates/dividends) wired and testable.

Acceptance criteria:
- Two identical runs on identical data produce identical metrics/alerts.
- Every alert row includes machine-readable decision evidence.
- ATM/term metrics change predictably when rates/dividend assumptions are perturbed in tests.

### Sprint 2 (Week 2): Config truth and drift removal

Goal:
- Eliminate non-operative configuration and hidden hardcoding.

Primary changes:
- `config/config-v1.yaml`: annotate active/deprecated fields.
- `src/core/*`: wire currently unused high-impact fields or remove them.
- `tests/`: add explicit tests that fail if config fields are ignored.

Deliverables:
- Config contract matrix: field -> code path -> test.

Acceptance criteria:
- No high-impact config field remains silently unused.
- Config changes demonstrably alter runtime behavior under test.

### Sprint 3 (Weeks 3-4): Surface integrity and no-arbitrage checks

Goal:
- Replace nearest-neighbor artifacts with a statistically stabilized surface representation.

Primary changes:
- `src/core/metrics.py`: introduce fitted/interpolated smile extraction with explicit model-selection protocol (e.g., constrained spline vs SVI-class fit).
- `src/core/iv_solve.py`: expose fit diagnostics and solver status propagation.
- new `src/core/surface_qc.py`: no-arbitrage sanity checks (vertical/calendar).
- `src/db/schema.sql`: store fit error and surface quality metrics.

Deliverables:
- Surface quality score and no-arbitrage flags per bucket.
- Model card for surface representation: chosen class, rejected alternatives, and acceptance thresholds.

Acceptance criteria:
- Spurious metric jumps from strike boundary crossing are reduced versus baseline.
- Alerts are hard-blocked when surface consistency/no-arbitrage checks fail.

### Sprint 4 (Weeks 5-6): Regime model independence

Goal:
- Replace endogenous RV proxy regime logic with independent multi-signal regime states.

Primary changes:
- `src/core/regime.py`: rework scoring inputs and wire config thresholds.
- `config/config-v1.yaml`: explicit regime feature thresholds.
- `src/db/schema.sql`: add regime feature component storage.
- Add macro-event calendar inputs (FOMC, CPI, major scheduled risk) as explicit regime features.
- Add at least one cross-domain stress proxy beyond local surface geometry.

Deliverables:
- Transparent regime decomposition (`why Calm/Transition/Stress`).

Acceptance criteria:
- Regime labels no longer collapse to RV-only behavior.
- Regime transitions align with known stress episodes in replay tests.
- Regime features show measurable incremental value in ablation over RV-only baseline.

### Sprint 5 (Weeks 7-8): Signal engine redesign

Goal:
- Move from static z-score gating to robust, regime-aware anomaly detection.

Primary changes:
- `src/core/alerts.py`: robust scoring and state transitions (`Candidate`, `Validated`, `ExecutionReady`).
- `src/core/compute_snapshot.py`: uncertainty-aware gating.
- `tests/test_alerts_logic.py`: regime-conditional and uncertainty-path tests.
- Add identifiability checks so correlated metrics (RR/FLY/TERM) are not double-counted as independent evidence.

Deliverables:
- State machine for signal lifecycle.

Acceptance criteria:
- False-positive alert density in transition regimes is lower than baseline.
- Worst-case and uncertainty gates are explicitly test-covered.
- Signal ranking remains stable under metric-perturbation tests (identifiability guardrail).

### Sprint 6 (Weeks 9-10): Execution-aware idea generation

Goal:
- Replace template-only mapping with cost-aware candidate ranking.

Primary changes:
- `src/core/trade_ideas.py`: candidate generation, friction-adjusted edge score.
- `src/core/tradability.py`: depth/spread-aware execution quality factors.
- `src/app/streamlit_app.py`: show edge decomposition and blocking reasons.
- Add nonlinear impact model by size and basic hedge-path cost approximation for convex structures.

Deliverables:
- Trade idea ranking by expected edge-after-cost and risk budget impact.

Acceptance criteria:
- No trade export if edge-after-friction <= 0.
- UI shows full decomposition (signal edge, costs, risk flags).
- Candidate ranking changes consistently with size/impact assumptions (nonlinear sanity).

### Sprint 7 (Weeks 11-12): Validation and release gating

Goal:
- Enforce out-of-sample and execution-quality gates before promotion.

Primary changes:
- `src/core/replay.py`: walk-forward evaluation hooks.
- new `scripts/validate_release.py`: release checklist automation.
- `tests/`: adversarial suite for sparse/stale/discontinuous chains.
- Add mandatory regime-stratified falsification report and ablation ledger.

Deliverables:
- Validation report with OOS metrics and stability diagnostics.
- Falsification report: what failed, what was removed, what survived.

Acceptance criteria:
- Promotion blocked if OOS execution-adjusted expectancy or drawdown limits fail.
- Adversarial tests must pass in CI.
- Promotion blocked if gains disappear in regime-stratified or component-ablation tests.

## Falsification and Reduction Discipline

Every major enhancement ships with:

1. Baseline comparison (before/after) on identical replay windows.
2. Regime-stratified metrics (Calm/Transition/Stress).
3. Component ablation (remove one new component at a time).
4. Removal decision: if component adds explanation but no predictive lift, remove it.

## File-Level Workstreams

### Data + schema
- `src/db/schema.sql`
- `src/db/init_db.py`

### Signal compute core
- `src/core/compute_snapshot.py`
- `src/core/metrics.py`
- `src/core/alerts.py`
- `src/core/regime.py`
- `src/core/tradability.py`
- `src/core/trade_ideas.py`
- `src/core/iv_solve.py`

### Ops + runtime
- `scripts/run_pipeline.py`
- `scripts/run_pipeline_and_notify.sh`
- `src/core/replay.py`

### UI + review
- `src/app/streamlit_app.py`

### Test hardening
- `tests/test_alerts_logic.py`
- `tests/test_regime_filter.py`
- `tests/test_tier_logic.py`
- `tests/test_trade_pricing.py`
- plus new adversarial tests for sparse/stale surface edge cases

## Quantitative Go/No-Go Gates

1. OOS execution-adjusted expectancy > 0 by signal family and in aggregate.
2. Max drawdown and tail-loss constraints within predefined budget.
3. Regime robustness: no single regime responsible for the majority of profits.
4. Alert precision improves versus baseline while alert volume does not inflate.
5. Runtime integrity: no unknown decision states, no silent config drift.
6. Surface model gate: selected fit class outperforms nearest-neighbor baseline in both stability and predictive utility.
7. Ablation gate: each retained component shows incremental OOS value.

## Risks and Controls

- Risk: overfitting during model upgrades.
  - Control: locked OOS window and strict walk-forward splits.
- Risk: quality gates reduce signal count too aggressively.
  - Control: monitor precision-recall tradeoff and calibrate state thresholds.
- Risk: additional complexity reduces interpretability.
  - Control: preserve machine-readable decision trace for every gate.

## Immediate Next 10 Days (Execution Sequence)

1. Implement run manifest and decision trace persistence.
2. Integrate rates/dividend inputs and add pricing-sensitivity tests.
3. Build config contract matrix and remove dead knobs.
4. Add hard-block surface quality/no-arbitrage path.
5. Add first adversarial + ablation test pack (sparse wings, stale books, missing tenors).
6. Ship baseline-vs-new comparison report with regime split.
