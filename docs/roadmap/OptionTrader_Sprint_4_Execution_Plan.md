# OptionTrader Sprint 4 Execution Plan

Date: 2026-04-30
Sprint window: Weeks 5-6
Parent roadmap: `docs/roadmap/OptionTrader_Next_Level_Plan.md`
Prior sprint: `docs/roadmap/OptionTrader_Sprint_3_2_Execution_Plan.md`
Ticket sheet: `docs/roadmap/OptionTrader_Sprint_4_Dev_Ticket_Sheet.md`
Planning review: `docs/roadmap/OptionTrader_Sprint_4_Planning_Review.md`

## Sprint Objective

Deliver regime-model independence by replacing RV-only behavior with a transparent, multi-signal,
config-driven regime state that has measurable incremental value over RV baseline.

## Baseline Constraints from Sprint 3.x

- Surface QC hard-blocking is now part of the safety baseline and must remain fail-closed.
- Replay artifact and QC monitoring from Sprint 3.2 become required reference inputs for Sprint 4
  evaluation.
- Regime changes must preserve existing run-manifest and explainability contracts.

## Scope

In scope:

- `src/core/regime.py` rework to use independent feature set and explicit config thresholds.
- Schema support for persisted regime feature components.
- Config contract updates and tests for all active regime thresholds.
- Replay/ablation evidence that new regime features add value over RV-only baseline.

Out of scope:

- Signal state machine redesign (Sprint 5).
- Trade candidate cost-aware ranking (Sprint 6).

## Planned Tickets

### S4-00 Regime Feature Contract and Data Plumbing

Goal:

- Define and persist all feature inputs used by regime scoring.

Deliverables:

- Regime feature schema additions (if needed) and migration support.
- Feature extraction contract documented in config matrix.

Acceptance:

- Every regime feature used in scoring is persisted or reproducibly derivable.

### S4-01 Multi-Signal Regime Scoring Engine

Goal:

- Replace RV-proxy dominance with weighted multi-signal scoring.

Deliverables:

- Refactored `src/core/regime.py` with config-driven thresholds/weights.
- Deterministic `why` decomposition for each regime label.

Acceptance:

- Regime labels are explainable by component contributions.
- No hardcoded threshold constants remain in active path.

### S4-02 Scheduled Event and Cross-Domain Stress Inputs

Goal:

- Add at least one scheduled-event feature and one cross-domain stress proxy.

Deliverables:

- Event-calendar integration path (FOMC/CPI style flags).
- Cross-domain stress feature integrated into regime score.
- Scheduled-events source explicitly defined:
  - v1 source: `config/regime_events_v1.yaml` (manual curated file),
  - optional later replacement: external API adapter with same schema.

Acceptance:

- New features alter labels on known stress dates in fixtures/replay.

### S4-03 Ablation and Incremental Value Gate

Goal:

- Enforce falsification discipline for new regime features.

Deliverables:

- Baseline (RV-only) vs new (multi-signal) comparison artifact.
- Feature ablation table showing incremental contribution.

Acceptance:

- At least one independent feature shows measurable lift over RV-only baseline.
- If no feature adds lift, component is removed or demoted.

Locked lift gate for retention decisions:

- Evaluation window: same as S3.2 locked contract unless superseded in sprint kickoff.
- Minimum sample: `>= 50` alerts total and `>= 10` per active regime bucket.
- Primary metric: alert precision delta at comparable volume.
  - pass threshold: `precision_candidate - precision_baseline >= +0.03`.
  - volume guardrail: candidate alert volume must be within `[-15%, +15%]` of baseline.
- Secondary metric: false-positive density in Transition regime must not worsen by more than `+0.02`.
- If thresholds are not met, feature fails ablation gate and is removed or disabled.

### S4-04 Regime Drift and Config Safety Guardrails

Goal:

- Prevent silent mismatch between stored regime states and current thresholds.

Deliverables:

- Regime config hash checks integrated into runtime warnings and tests.
- Explicit runbook guidance for recompute requirements.

Acceptance:

- Threshold changes produce deterministic warnings when historical regime rows are stale.

## Expected Files

- `src/core/regime.py`
- `src/core/config.py`
- `src/core/compute_snapshot.py`
- `src/db/schema.sql`
- `src/db/init_db.py`
- `config/config-v1.yaml`
- `config/config-test.yaml`
- `config/regime_events_v1.yaml`
- `docs/roadmap/OptionTrader_Config_Contract_Matrix.md`
- `tests/test_regime.py`
- `tests/test_regime_filter.py`
- `tests/test_config_contract.py`

## Definition of Done

Sprint 4 is done only when all are true:

1. Regime labels are no longer RV-only in practice.
2. Regime decomposition is transparent and test-covered.
3. Ablation evidence exists and justifies retained features.
4. Config and stale-state guardrails prevent silent drift.

## Validation Commands

```bash
source .venv/bin/activate
pytest tests/test_regime.py tests/test_regime_filter.py tests/test_config_contract.py
pytest -q
```
