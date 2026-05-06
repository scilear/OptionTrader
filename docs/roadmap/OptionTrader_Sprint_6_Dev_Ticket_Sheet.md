# OptionTrader Sprint 6 Dev Ticket Sheet

Date: 2026-05-05
Last updated: 2026-05-06 (replay evidence complete)
Source plan: `docs/roadmap/OptionTrader_Sprint_6_Execution_Plan.md`
Sprint: Weeks 9-10

## Ticket Board Snapshot

| Ticket | Objective | Priority | Status | Evidence |
|---|---|---|---|---|
| S6-00 | Cost model contract + baseline capture | P0 | Done | `docs/roadmap/OptionTrader_Sprint_6_Execution_Plan.md`, `docs/roadmap/OptionTrader_Sprint_6_Baseline_Capture_v1.json` |
| S6-01 | Candidate edge component normalization | P0 | Done | `src/core/trade_ideas.py`, `tests/test_trade_ideas.py` |
| S6-02 | Friction-adjusted edge engine | P0 | Done | `src/core/trade_ideas.py`, `src/core/tradability.py`, `tests/test_trade_pricing.py` |
| S6-03 | Nonlinear size-impact model | P0 | Done | `src/core/tradability.py`, `tests/test_trade_pricing.py` |
| S6-04 | Hedge-path cost approximation | P1 | Done | `src/core/trade_ideas.py`, `tests/test_trade_pricing.py` |
| S6-05 | Explainability + Streamlit exposure | P1 | Done | `src/app/streamlit_app.py` |
| S6-06 | Replay evidence + promotion gate | P0 | Done | `scripts/generate_s6_replay_artifact.py`, `docs/roadmap/OptionTrader_Sprint_6_Replay_Artifact.md` |

## Ticket Details

### S6-00 - Cost Model Contract and Baseline Capture

- Objective:
  - Lock deterministic S6 evaluation contract and baseline capture.
- Files:
  - `docs/roadmap/OptionTrader_Sprint_6_Execution_Plan.md`
  - `docs/roadmap/OptionTrader_Sprint_6_Dev_Ticket_Sheet.md`
- Tasks:
  - Define explicit cost assumptions and replay contract.
  - Capture and version baseline ranking output before S6 changes.
- Acceptance:
  - [x] Contract is explicit, versioned, and reproducible.
  - [x] Baseline capture artifact is committed.

### S6-01 - Candidate Generation and Edge Component Normalization

- Objective:
  - Ensure every candidate has complete edge component inputs.
- Files:
  - `src/core/trade_ideas.py`
  - `tests/test_trade_ideas.py`
- Tasks:
  - Add normalized component fields required for cost engine.
  - Reject incomplete candidates with explicit blocker reasons.
- Acceptance:
  - [x] Candidate payload completeness is test-covered.

### S6-02 - Friction-Adjusted Edge Engine

- Objective:
  - Compute edge-after-cost and gate non-viable ideas.
- Files:
  - `src/core/trade_ideas.py`
  - `src/core/tradability.py`
  - `tests/test_trade_pricing.py`
- Tasks:
  - Implement cost decomposition and net-edge calculation.
  - Integrate deterministic block on non-positive net edge.
- Acceptance:
  - [x] `edge_after_cost <= 0` always blocks promotion.
  - [x] Cost decomposition fields are machine-readable and tested.

### S6-03 - Nonlinear Size and Impact Model

- Objective:
  - Replace linear cost assumptions with size-sensitive impact behavior.
- Files:
  - `src/core/tradability.py`
  - `tests/test_trade_pricing.py`
- Tasks:
  - Add nonlinear impact function by size tiers.
  - Validate monotonicity and ranking coherence under size scaling.
- Acceptance:
  - [x] Cost curves are monotonic non-decreasing with size.
  - [x] Ranking shifts are deterministic and explainable in tests.

### S6-04 - Hedge-Path Cost Approximation

- Objective:
  - Include hedge-path costs for convex structures in net-edge evaluation.
- Files:
  - `src/core/trade_ideas.py`
  - `tests/test_trade_pricing.py`
- Tasks:
  - Add hedge-path approximation component.
  - Emit uncertainty/risk flags for hedge-path estimates.
- Acceptance:
  - [x] Hedge-path component appears where applicable and is test-covered.

### S6-05 - Explainability and UI Exposure

- Objective:
  - Expose cost-aware ranking and blockers in user-facing review path.
- Files:
  - `src/app/streamlit_app.py`
  - explainability tests
- Tasks:
  - Display edge decomposition and blocker reasons per candidate.
  - Ensure UI view matches exported payload semantics.
- Acceptance:
  - [x] UI and payload rankings are consistent for same input.

### S6-06 - Replay Evidence and Promotion Gate

- Objective:
  - Publish reproducible S6 pass/fail recommendation.
- Files:
  - `scripts/generate_s6_replay_artifact.py`
  - `docs/roadmap/OptionTrader_Sprint_6_Replay_Artifact.md`
- Tasks:
  - Compare baseline vs candidate under S6 contract.
  - Emit machine-readable gate payload and recommendation.
- Acceptance:
  - [x] Artifact reproducible from committed command block.
  - [x] Promotion recommendation is explicit and evidence-backed.

## Progress Notes (2026-05-06)

- Completed implementation for S6-01 through S6-04.
- Added partial S6-05 UI exposure: cost-aware ranking table and blocked reason fields in alert
  detail page.
- Added S6 replay artifact generator:
  - `scripts/generate_s6_replay_artifact.py`

Validation run:

```bash
source .venv/bin/activate
pytest tests/test_trade_ideas.py tests/test_trade_pricing.py -q
```

Result: `12 passed`.

Replay outcome:

- Evidence run completed after lock release.
- Final recommendation from artifact: `promotable`.

## Suggested Delivery Order

1. S6-00
2. S6-01
3. S6-02
4. S6-03
5. S6-04
6. S6-05
7. S6-06

## End-of-Sprint Validation Commands

```bash
source .venv/bin/activate
pytest tests/test_trade_ideas.py tests/test_trade_pricing.py -q
pytest -q
```
