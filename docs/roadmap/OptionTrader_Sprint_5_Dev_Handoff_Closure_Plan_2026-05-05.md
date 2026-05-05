# OptionTrader Sprint 5 Dev Handoff Closure Plan (2026-05-05)

Date: 2026-05-05
Scope: Close remaining Sprint 5 tasks and produce final S5 promotion evidence.
References:
- `docs/roadmap/OptionTrader_Sprint_5_Execution_Plan.md`
- `docs/roadmap/OptionTrader_Sprint_5_Dev_Ticket_Sheet.md`

## Current S5 State (Observed)

Implemented and test-covered:

- S5-01 robust scoring core (`src/core/alerts.py`)
- S5-02 lifecycle state machine (`src/core/compute_snapshot.py`)
- S5-03 uncertainty-aware gating (`src/core/compute_snapshot.py`)
- S5-04 overlap/identifiability guardrails (`src/core/alerts.py`)

Validation status observed on current branch:

- `pytest tests/test_alerts_logic.py tests/test_regime_filter.py -q` -> pass
- `pytest -q` -> pass (91 tests)

Still open for closure:

- S5-00 baseline output capture/versioning
- S5-05 replay evidence artifact + promotion decision

## Closure Objectives

1. Freeze S5 baseline/candidate evaluation contract in docs and issue references.
2. Produce reproducible S5 replay artifact with pass/fail decision payload.
3. Update ticket statuses and issue states to reflect final closure outcome.

## Required Dev Tasks

### T1 - Lock S5 Evaluation Contract (S5-00 completion)

Deliverables:

- fixed window(s), lineages, and metrics schema for S5 evidence,
- explicit guardrails for:
  - transition-regime false-positive density,
  - alert-volume inflation,
  - state-distribution sanity (Candidate/Validated/ExecutionReady).

Doc updates:

- `docs/roadmap/OptionTrader_Sprint_5_Execution_Plan.md`
- `docs/roadmap/OptionTrader_Sprint_5_Dev_Ticket_Sheet.md`

Acceptance:

- baseline output path and command are documented and reproducible.

### T2 - Implement S5 Replay Evidence Script (S5-05)

Add script:

- `scripts/generate_s5_replay_artifact.py`

Minimum payload fields:

- window metadata,
- baseline/candidate lineage metadata,
- alert counts by state,
- transition-regime FP density baseline vs candidate,
- volume delta %,
- pass/fail booleans by gate,
- final recommendation label (`promotable` or `not_promotable`).

### T3 - Produce S5 Artifact Document

Add artifact doc:

- `docs/roadmap/OptionTrader_Sprint_5_Replay_Artifact.md`

Must include:

- exact command block,
- JSON payload,
- concise interpretation,
- promotion recommendation.

### T4 - Regression + Evidence Gate

Run and record:

```bash
source .venv/bin/activate
pytest tests/test_alerts_logic.py tests/test_regime_filter.py -q
pytest -q
python scripts/generate_s5_replay_artifact.py <locked-contract-args>
```

Acceptance:

- all tests green,
- replay artifact generated with deterministic output structure.

### T5 - Ticket and Issue Closure Hygiene

- Mark S5-00 done once baseline capture is versioned.
- Mark S5-05 done only with artifact + recommendation checked in.
- Close GH issues `#5` and `#10` only after evidence is merged.

## Definition of Sprint 5 Closure

Sprint 5 closes when:

1. S5-00 and S5-05 are completed with reproducible evidence,
2. S5 replay artifact exists and is up to date,
3. promotion decision is explicit and justified by gate payload,
4. ticket sheet statuses and GH issues are synchronized.

## Suggested Command Sequence for Dev

```bash
source .venv/bin/activate

# 1) verify core S5 behavior
pytest tests/test_alerts_logic.py tests/test_regime_filter.py -q

# 2) full safety check
pytest -q

# 3) generate S5 replay artifact (script to be added)
python scripts/generate_s5_replay_artifact.py --start-ts <...> --end-ts <...>
```
