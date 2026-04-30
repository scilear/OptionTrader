# OptionTrader Sprint 3.2 Execution Plan

Date: 2026-04-30
Sprint window: Week 4 (closure slice)
Parent roadmap: `docs/roadmap/OptionTrader_Next_Level_Plan.md`
Prior sprint: `docs/roadmap/OptionTrader_Sprint_3_Execution_Plan.md`
Ticket sheet: `docs/roadmap/OptionTrader_Sprint_3_2_Dev_Ticket_Sheet.md`
Planning review: `docs/roadmap/OptionTrader_Sprint_4_Planning_Review.md`

## Sprint Objective

Close the remaining Sprint 3 follow-ups by publishing a reproducible replay artifact and adding
operational visibility for surface QC reason-code frequencies.

## Why This Sprint Exists

Sprint 3 and S3.1 delivered core safety and persistence hardening, but two closure artifacts are
still required for full roadmap hygiene:

- baseline-vs-S3 replay evidence in docs,
- production-facing QC reason-code monitoring.

## Locked Comparison Contract (S3.2-01)

Use one fixed comparison contract to avoid selection bias:

- Underlying: `SPX`.
- Official replay window:
  - `start_ts`: `2026-04-01T00:00:00Z`
  - `end_ts`: `2026-04-15T23:59:59Z`
- Baseline lineage: pre-Sprint-3 surface logic (`3b024c9` predecessor in replay runbook).
- Candidate lineage: Sprint 3 + S3.1 hardening (`5128e8e` stack).

Required artifact fields:

- `baseline_commit`, `candidate_commit`
- `start_ts`, `end_ts`, `underlying`
- `total_snapshots`, `regime_split_counts`
- `alert_count_baseline`, `alert_count_candidate`, `alert_delta_pct`
- per-family precision/volume summary

## Scope

In scope:

- Replay artifact generation for baseline vs current implementation on the same snapshot window.
- QC reason-code frequency rollup for operational monitoring.
- Documentation closure and handoff packaging into Sprint 4.

Out of scope:

- Regime model redesign (Sprint 4 scope).
- Signal state machine redesign (Sprint 5 scope).
- Execution-aware ranking redesign (Sprint 6 scope).

## Ticket Outcomes

### S3.2-01 Replay Artifact Publication

Goal:

- Publish a deterministic comparison report for baseline vs Sprint 3/S3.1 outputs.

Deliverables:

- Snapshot-window definition in docs.
- Comparison table for alert density and key signal-family deltas.
- Regime-split summary for the same window.
- Published artifact file:
  - `docs/roadmap/OptionTrader_Sprint_3_2_Replay_Artifact.md`

Acceptance:

- Artifact is reproducible from committed scripts/queries.
- Comparison uses identical data window and config lineage labels.
- Artifact schema includes all required fields in this plan.
- Artifact file path is stable and linked from Sprint 3 closure docs.

### S3.2-02 QC Reason-Code Monitoring

Goal:

- Expose how often QC blocks occur and why.

Deliverables:

- Query/script for reason-code frequency by day and by expiry bucket.
- Health-check script for proactive monitoring:
  - `scripts/qc_health_check.sh`
  - non-zero exit only when block rate exceeds threshold for sustained windows.
- Optional Streamlit panel or ops markdown table for quick inspection.

Acceptance:

- Operators can identify top QC block reasons without manual SQL assembly.
- Output includes at least: date, reason_code, count, total snapshots, block rate.
- Health-check fail condition is explicit and stable:
  - threshold: `block_rate > 0.20`
  - sustained: `3` consecutive 1-hour windows
  - minimum sample: `30` snapshots per window.

### S3.2-03 Closure and Sprint 4 Handoff

Goal:

- Lock closure notes and create clear handoff into Sprint 4 regime work.

Deliverables:

- Updated Sprint 3 docs with artifact references.
- Sprint 4 execution plan and ticket sheet finalized.

Acceptance:

- No open Sprint 3 follow-up remains undocumented.
- Sprint 4 starts from a concrete, assignable ticket board.

## Expected Files

- `docs/roadmap/OptionTrader_Sprint_3_Review_Report.md` (reference only)
- `docs/roadmap/OptionTrader_Sprint_3_Execution_Plan.md`
- `docs/roadmap/OptionTrader_Sprint_3_Dev_Ticket_Sheet.md`
- `docs/roadmap/OptionTrader_Sprint_3_2_Replay_Artifact.md` (new)
- `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`
- `docs/roadmap/OptionTrader_Sprint_4_Dev_Ticket_Sheet.md`
- Required implementation helpers for this sprint:
  - `scripts/generate_replay_artifact.py` (new)
  - `scripts/qc_health_check.sh` (new)
- Optional helpers:
  - `src/core/replay.py`
  - `scripts/validate_release.py`
  - `src/app/streamlit_app.py`

## Definition of Done

Sprint 3.2 is done only when all are true:

1. Replay artifact is published with reproducible steps.
2. QC reason-code monitoring output exists and is human-readable.
3. Sprint 4 planning docs are finalized and linked from Sprint 3 closure docs.

## Validation Commands

Pre-implementation baseline (must already run):

```bash
source .venv/bin/activate
pytest -q
```

Post-implementation ticket validation (commands below are deliverables of S3.2 and must exist before closure):

```bash
source .venv/bin/activate
python scripts/generate_replay_artifact.py --start-ts 2026-04-01T00:00:00Z --end-ts 2026-04-15T23:59:59Z
bash scripts/qc_health_check.sh --window-hours 1 --threshold 0.20 --consecutive 3 --min-snapshots 30
python scripts/run_pipeline.py
```
