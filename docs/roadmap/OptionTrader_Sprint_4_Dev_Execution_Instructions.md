# OptionTrader Sprint 4 Dev Execution Instructions

Date: 2026-05-02
Audience: Sprint 4 implementation owners
Status: Ready for execution

## 1) Source of Truth

Use these documents as the contract for implementation decisions:

- Master roadmap: `docs/roadmap/OptionTrader_Next_Level_Plan.md`
- Sprint 4 plan: `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`
- Sprint 4 ticket board: `docs/roadmap/OptionTrader_Sprint_4_Dev_Ticket_Sheet.md`
- Planning adversarial review: `docs/roadmap/OptionTrader_Sprint_4_Planning_Review.md`
- Prior-sprint closure artifacts:
  - `docs/roadmap/OptionTrader_Sprint_3_2_Execution_Plan.md`
  - `docs/roadmap/OptionTrader_Sprint_3_2_Replay_Artifact.md`

If any ambiguity appears, prefer Sprint 4 plan/ticket docs over ad-hoc assumptions.

## 2) Current Starting Point

Recent S4-00 groundwork is present:

- `regime_state` additive migration coverage added in `src/db/init_db.py`
- schema coverage test updated in `tests/test_schema.py`
- config matrix updated for new `regime.*` keys in
  `docs/roadmap/OptionTrader_Config_Contract_Matrix.md`

Treat this as partial S4-00 completion, not Sprint 4 completion.

## 3) Sprint Goal (Operational)

Deliver a multi-signal regime model that is:

1. config-driven,
2. decomposable/explainable,
3. resilient to config drift,
4. justified by explicit ablation gates.

## 4) Required Execution Order

Implement tickets in this exact order:

1. `S4-00` Regime feature contract + data plumbing
2. `S4-01` Multi-signal scoring engine
3. `S4-02` Event + cross-domain stress inputs
4. `S4-04` Drift/config safety guardrails
5. `S4-03` Ablation and incremental value gate

Reason: later tickets depend on schema/contract/scoring being stable first.

## 5) Detailed Ticket Instructions

### S4-00: Regime Feature Contract + Data Plumbing

Objective:
- Ensure every regime feature used in scoring is persisted or reproducibly derivable and testable.

Required files:
- `src/db/schema.sql`
- `src/db/init_db.py`
- `docs/roadmap/OptionTrader_Config_Contract_Matrix.md`
- `tests/test_schema.py`

Implementation checklist:
- Confirm `regime_state` includes all currently planned decomposition fields.
- Keep migration additive and idempotent (no destructive migrations).
- Ensure fresh schema path and migrate-existing path both yield same effective columns.
- Ensure config matrix entries for all active `regime.*` keys are present and consistent.

Done criteria:
- Schema test validates new columns on both fresh and migrated DBs.

### S4-01: Multi-Signal Regime Scoring Engine

Objective:
- Replace RV-dominant behavior with weighted multi-signal scoring and deterministic decomposition.

Required files:
- `src/core/regime.py`
- `src/core/config.py`
- `tests/test_regime.py`

Implementation checklist:
- Build a deterministic scorer using configured feature weights.
- Emit decomposition payload per regime decision (`component -> contribution`).
- Remove hardcoded thresholds from active logic.
- Preserve existing external API shape where possible; if changed, update all call sites/tests.

Done criteria:
- Regime label and decomposition are both test-covered.
- Config edits change output deterministically in fixtures.

### S4-02: Event + Cross-Domain Stress Inputs

Objective:
- Add independent signals beyond RV/drawdown.

Required files:
- `src/core/regime.py`
- `config/config-v1.yaml`
- `config/config-test.yaml`
- `config/regime_events_v1.yaml`
- `tests/test_regime.py`

Implementation checklist:
- Use `config/regime_events_v1.yaml` as v1 scheduled-event source.
- Add one cross-domain stress proxy path using
  `regime.stress_proxy_ticker` and related weights.
- Add fixtures covering event and stress-proxy signal paths.

Done criteria:
- Tests show event/stress signals can influence regime label.

### S4-04: Drift + Config Safety Guardrails

Objective:
- Prevent stale regime-state use after threshold/weight changes.

Required files:
- `src/core/compute_snapshot.py`
- `src/core/regime.py`
- `tests/test_regime_filter.py`

Implementation checklist:
- Keep regime-config hash checks explicit and visible in logs.
- Warning must be deterministic and actionable.
- Add tests for mismatch and non-mismatch paths.

Done criteria:
- Mismatch warning behavior is test-covered.

### S4-03: Ablation + Incremental Value Gate

Objective:
- Enforce falsification before accepting new complexity.

Required files:
- `src/core/replay.py` and/or helper scripts
- `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`

Locked gates (must be enforced exactly):
- Min sample: `>=50` alerts total and `>=10` per active regime bucket.
- Primary lift: `precision_candidate - precision_baseline >= +0.03`.
- Volume guardrail: candidate volume in `[-15%, +15%]` of baseline.
- Transition false-positive density deterioration: `<= +0.02`.

Implementation checklist:
- Produce reproducible ablation artifact.
- Include retain/remove decision per new feature.
- If gates fail, remove or disable failing feature(s).

Done criteria:
- Artifact exists and feature decisions are evidence-backed.

## 6) Cross-Cutting Rules

- Do not loosen fail-closed behavior from Sprint 3.
- Any new active config key must be updated in all three locations:
  - `ACTIVE_CONFIG_KEYS`
  - `HIGH_IMPACT_ACTIVE_KEYS` (when materially impactful)
  - `CONTRACT_TEST_COVERAGE`
- Keep schema changes additive.
- Keep tests deterministic (explicit column inserts, fixed fixtures).

## 7) Validation Commands

Run after each ticket and again before PR:

```bash
source .venv/bin/activate
pytest tests/test_schema.py tests/test_regime.py tests/test_regime_filter.py tests/test_config_contract.py
pytest -q
```

## 8) PR Strategy

Use one PR per ticket when feasible:

- PR 1: S4-00
- PR 2: S4-01
- PR 3: S4-02
- PR 4: S4-04
- PR 5: S4-03 (ablation gate + final retention decisions)

Each PR description must include:

- ticket ID,
- acceptance checklist,
- exact test commands run,
- explicit note on whether any config keys were added/changed.

## 9) Handoff Exit Criteria

Sprint 4 is implementation-complete only when:

1. S4-00..S4-04 are all closed with evidence,
2. all locked ablation thresholds are evaluated and documented,
3. full test suite passes,
4. docs remain consistent with shipped behavior.
