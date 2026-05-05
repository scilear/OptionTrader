# OptionTrader Sprint 6 Execution Plan

Date: 2026-05-05
Last updated: 2026-05-05 (initial sprint 6 plan)
Sprint window: Weeks 9-10
Parent roadmap: `docs/roadmap/OptionTrader_Next_Level_Plan.md`
Prior sprint: `docs/roadmap/OptionTrader_Sprint_5_Execution_Plan.md`
Ticket sheet: `docs/roadmap/OptionTrader_Sprint_6_Dev_Ticket_Sheet.md`

## Sprint Objective

Deliver execution-aware trade idea generation and ranking so every candidate is evaluated on
friction-adjusted edge, size-aware impact, and risk-aware explainability before promotion.

## Carryover Context

- Sprint 5 is implementation complete but marked `not_promotable` under current evidence contract.
- Sprint 4 S4-03 remains a research and evidence-governance stream.
- Sprint 6 should proceed independently, while preserving conservative runtime defaults.

## Scope

In scope:

- Friction-adjusted edge model for trade ideas.
- Nonlinear size/impact model and size-sensitivity ranking.
- Basic hedge-path cost approximation for convex structures.
- Explainable ranking payload in runtime outputs and Streamlit review surface.
- Deterministic replay artifact proving no unsafe ranking regressions.

Out of scope:

- New signal families beyond current alert universe.
- Full portfolio optimizer or dynamic hedging engine.
- Production promotion without replay evidence gates.

## S6 Locked Evaluation Contract (v1)

Contract ID: `S6-CONTRACT-v1`

- Underlying: `SPX`
- Data source: EOD truth config unless explicitly superseded
- Baseline lineage: current mainline before S6 changes
- Candidate lineage: S6 branch output
- Required outputs:
  - edge-before-cost,
  - total friction cost,
  - edge-after-cost,
  - size-impact sensitivity,
  - risk flags used in gating

Gate principles:

1. `edge_after_cost <= 0` must block execution promotion.
2. Candidate ranking must remain stable under small perturbations.
3. Size increase must not produce implausible monotonicity violations in costs.

## Planned Tickets

### S6-00 Cost Model Contract and Baseline Capture

Goal:

- Lock assumptions for transaction costs, impact assumptions, and replay reporting schema.

Deliverables:

- Contract section in docs with explicit cost assumptions.
- Baseline capture artifact for pre-S6 ranking behavior.

Acceptance:

- Cost model assumptions are explicit and versioned.
- Baseline replay output is reproducible and committed.

### S6-01 Candidate Generation and Normalized Edge Inputs

Goal:

- Ensure trade idea candidates expose normalized edge components required by the cost model.

Deliverables:

- Candidate payload extension in `src/core/trade_ideas.py`.
- Deterministic component fields available to downstream ranking logic.

Acceptance:

- Every candidate has complete edge component payload or is explicitly rejected.

### S6-02 Friction-Adjusted Edge Engine

Goal:

- Compute edge-after-cost with transparent decomposition.

Deliverables:

- Cost decomposition module in trade-idea path.
- Explain payload fields for component costs and net edge.

Acceptance:

- No candidate reaches execution state with non-positive net edge.
- Decomposition is machine-readable and test-covered.

### S6-03 Nonlinear Size and Impact Model

Goal:

- Model impact as nonlinear with position size, not fixed linear haircut.

Deliverables:

- Size-sensitive impact function integrated into cost engine.
- Sensitivity tests over multiple size tiers.

Acceptance:

- Cost curves are monotonic non-decreasing with size.
- Ranking changes are coherent under size scaling tests.

### S6-04 Hedge-Path Cost Approximation

Goal:

- Add pragmatic hedge-path approximation for convex structures.

Deliverables:

- Hedge-path cost estimate integrated into `edge_after_cost`.
- Risk flags for hedge-path uncertainty in explain payload.

Acceptance:

- Hedge-path component is included for relevant structures and test-covered.

### S6-05 Explainability and UI Exposure

Goal:

- Make cost-aware ranking inspectable by ops/PM users.

Deliverables:

- Streamlit views exposing cost decomposition and promotion blockers.
- Ranking table with explicit `blocked_reason` when non-promotable.

Acceptance:

- UI and exported payload show the same ranking and blocker semantics.

### S6-06 Replay Evidence and Promotion Gate

Goal:

- Produce reproducible baseline-vs-candidate replay evidence for execution-aware ranking.

Deliverables:

- S6 replay artifact script and markdown report.
- Machine-readable gate payload and recommendation (`promotable` / `not_promotable`).

Acceptance:

- Replay artifact is reproducible from committed command block.
- No unsafe ranking regressions versus baseline contract.
- Promotion recommendation is explicit and evidence-backed.

## Expected Files

- `src/core/trade_ideas.py`
- `src/core/tradability.py`
- `src/core/compute_snapshot.py`
- `src/app/streamlit_app.py`
- `tests/test_trade_ideas.py`
- `tests/test_trade_pricing.py`
- `tests/test_alerts_logic.py` (if ranking/state handoff logic is touched)
- new S6 replay/evidence tests
- `docs/roadmap/OptionTrader_Sprint_6_Dev_Ticket_Sheet.md`

## Definition of Done

Sprint 6 is done only when all are true:

1. Trade candidates have explicit cost decomposition and net edge.
2. Net-edge gate blocks non-viable ideas deterministically.
3. Size/impact behavior is nonlinear and test-validated.
4. Replay artifact provides machine-readable pass/fail recommendation.
5. Ticket/issue/doc statuses are synchronized with evidence outcome.

## Validation Commands

```bash
source .venv/bin/activate
pytest tests/test_trade_ideas.py tests/test_trade_pricing.py -q
pytest -q
```
