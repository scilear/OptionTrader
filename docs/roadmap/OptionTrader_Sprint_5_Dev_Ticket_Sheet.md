# OptionTrader Sprint 5 Dev Ticket Sheet

Date: 2026-05-04
Last updated: 2026-05-04 (implementation start)
Source plan: `docs/roadmap/OptionTrader_Sprint_5_Execution_Plan.md`
Sprint: Weeks 7-8

## Ticket Board Snapshot

| Ticket | Objective | Priority | Status | Evidence |
|---|---|---|---|---|
| S5-00 | Baseline freeze + evaluation contract | P0 | In progress | `docs/roadmap/OptionTrader_Sprint_5_Execution_Plan.md` |
| S5-01 | Robust scoring core | P0 | Done | `src/core/alerts.py`, `tests/test_alerts_logic.py` |
| S5-02 | Signal lifecycle state machine | P0 | Done | `src/core/compute_snapshot.py`, `tests/test_regime_filter.py` |
| S5-03 | Uncertainty-aware gating | P0 | Done | `src/core/compute_snapshot.py`, `tests/test_regime_filter.py` |
| S5-04 | Identifiability/correlation guardrails | P1 | Done | `src/core/alerts.py`, `tests/test_alerts_logic.py`, `tests/test_explainability.py` |
| S5-05 | Replay evidence + release gate | P0 | Ready | S5 replay artifact script + roadmap evidence doc |

## Ticket Details

### S5-00 - Baseline Freeze and Evaluation Contract

- Objective:
  - Lock one deterministic evaluation contract for Sprint 5 comparisons.
- Files:
  - `docs/roadmap/OptionTrader_Sprint_5_Execution_Plan.md`
  - `docs/roadmap/OptionTrader_Sprint_5_Dev_Ticket_Sheet.md`
- Tasks:
  - Define fixed window, lineages, and metric schema for S5 evidence.
  - Record volume/precision/false-positive guardrails used for pass/fail.
- Acceptance:
  - [x] S5 contract is explicit and reproducible.
  - [ ] Baseline run output is captured and versioned.

### S5-01 - Robust Scoring Core

- Objective:
  - Improve anomaly score robustness in sparse/noisy conditions.
- Files:
  - `src/core/alerts.py`
  - `tests/test_alerts_logic.py`
- Tasks:
  - Implement robust scoring behavior for low-sample and outlier-prone histories.
  - Preserve deterministic no-signal behavior when quality is insufficient.
- Acceptance:
  - [x] Sparse, flat, and outlier edge cases are test-covered.
  - [x] No silent fallback to unstable z-score behavior.

### S5-02 - Signal Lifecycle State Machine

- Objective:
  - Move from binary fired/not-fired to explicit promotion states.
- Files:
  - `src/core/compute_snapshot.py`
  - `src/core/alerts.py`
  - `tests/test_alerts_logic.py`
- Tasks:
  - Implement states: `Candidate`, `Validated`, `ExecutionReady`.
  - Define deterministic transition and demotion rules.
  - Add explain payload fields for transition reason codes.
- Acceptance:
  - [x] Every emitted signal has one valid state.
  - [x] Transition reasons are machine-readable and test-covered.

### S5-03 - Uncertainty-Aware Gating

- Objective:
  - Block promotion when uncertainty is high or quality checks fail.
- Files:
  - `src/core/compute_snapshot.py`
  - `tests/test_regime_filter.py`
  - `tests/test_alerts_logic.py`
- Tasks:
  - Integrate confidence and worst-case consistency checks into state promotion.
  - Ensure QC fail and stale-regime paths remain fail-closed.
- Acceptance:
  - [x] QC fail path blocks promotion deterministically.
  - [x] Worst-case/uncertainty block paths are covered in tests.

### S5-04 - Identifiability and Correlation Guardrails

- Objective:
  - Prevent correlated metrics from being counted as independent support.
- Files:
  - `src/core/alerts.py`
  - `tests/test_alerts_logic.py`
- Tasks:
  - Add overlap detection for RR/FLY/TERM evidence bundles.
  - Downweight or de-duplicate overlapping evidence contributions.
  - Expose overlap diagnostics in explain payload.
- Acceptance:
  - [x] Correlated perturbation tests show stable ranking and no evidence inflation.

### S5-05 - Replay Evidence and Release Gate

- Objective:
  - Produce reproducible pass/fail evidence for Sprint 5 signal redesign.
- Files:
  - replay/evidence script(s) under `scripts/`
  - sprint evidence artifact in `docs/roadmap/`
- Tasks:
  - Compare baseline vs redesigned engine using locked S5 contract.
  - Report per-regime false-positive density, precision proxy, and volume deltas.
  - Record clear promotion recommendation.
- Acceptance:
  - [ ] Artifact is reproducible from committed commands.
  - [ ] Transition-regime false-positive density improves vs baseline.
  - [ ] Volume inflation remains inside contract guardrail.

## Suggested Delivery Order

1. S5-00
2. S5-01
3. S5-02
4. S5-03
5. S5-04
6. S5-05

## End-of-Sprint Validation Commands

```bash
source .venv/bin/activate
pytest tests/test_alerts_logic.py tests/test_regime_filter.py -q
pytest -q
```
