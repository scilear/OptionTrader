# OptionTrader Sprint 3.2 Dev Ticket Sheet

Date: 2026-04-30
Source plan: `docs/roadmap/OptionTrader_Sprint_3_2_Execution_Plan.md`
Sprint: Week 4 closure slice

## Ticket Board Snapshot

| Ticket | Objective | Priority | Status | Evidence |
|---|---|---|---|---|
| S3.2-01 | Publish baseline-vs-S3 replay artifact | P0 | Done | `docs/roadmap/OptionTrader_Sprint_3_2_Replay_Artifact.md`, `scripts/generate_replay_artifact.py` |
| S3.2-02 | Add QC reason-code monitoring output | P0 | Done | `scripts/qc_health_check.sh` + sustained-window fail policy |
| S3.2-03 | Final Sprint 3 closure + S4 handoff | P1 | Done | updated Sprint 3 closure docs + Sprint 4 assignment-ready package |

## Ticket Details

### S3.2-01 - Replay Artifact Publication

- Objective:
  - Generate and publish baseline-vs-current evidence using identical window + data lineage.
- Files:
  - `docs/roadmap/OptionTrader_Sprint_3_Execution_Plan.md`
  - `docs/roadmap/OptionTrader_Sprint_3_Dev_Ticket_Sheet.md`
  - `docs/roadmap/OptionTrader_Sprint_3_2_Replay_Artifact.md`
  - `scripts/generate_replay_artifact.py`
  - optional helper: `src/core/replay.py`
- Tasks:
  - Define fixed replay window and regime split.
  - Compute alert counts and key signal-family deltas baseline vs current.
  - Publish summary table and reproducibility commands.
- Acceptance:
  - [ ] Same input window for both runs is documented.
  - [ ] Artifact includes aggregate and regime-split summaries.
  - [ ] Artifact includes required fields from S3.2 execution plan locked contract.
  - [ ] Reproduction steps are executable from repo.

### S3.2-02 - QC Reason-Code Monitoring

- Objective:
  - Make QC block behavior observable in operations.
- Files:
  - `src/app/streamlit_app.py` (if UI panel)
  - `docs/roadmap/OptionTrader_Sprint_3_Execution_Plan.md`
  - `scripts/qc_health_check.sh`
  - optional helper scripts in `scripts/`
- Tasks:
  - Build reason-code rollup query from `surface_metrics.qc_reason_codes`.
  - Include counts + rates by date and reason code.
  - Implement sustained-window health-check thresholding:
    - `block_rate > 0.20`
    - `3` consecutive 1-hour windows
    - `>=30` snapshots per window.
  - Expose as table/panel and document usage.
- Acceptance:
  - [ ] Top reason codes visible without ad-hoc SQL editing.
  - [ ] Output includes count and block-rate context.
  - [ ] Health check exits non-zero only on sustained threshold breach with sample floor.
  - [ ] Documented runbook snippet exists in roadmap docs.

### S3.2-03 - Closure and Sprint 4 Handoff

- Objective:
  - Close Sprint 3 follow-ups and finalize Sprint 4 work package.
- Files:
  - `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`
  - `docs/roadmap/OptionTrader_Sprint_4_Dev_Ticket_Sheet.md`
  - `docs/roadmap/OptionTrader_Surface_Model_Card.md`
- Tasks:
  - Mark S3 follow-ups complete with links to artifacts.
  - Publish Sprint 4 tickets with explicit acceptance criteria.
  - Ensure dependency ordering from S3.2 -> S4 is explicit.
- Acceptance:
  - [ ] Sprint 3 docs have no unresolved Sprint-3-owned follow-up bullets.
  - [ ] Sprint 4 docs are assignment-ready.

## Delivery Order

1. S3.2-01
2. S3.2-02
3. S3.2-03

## Validation Commands

```bash
source .venv/bin/activate
pytest -q
python scripts/generate_replay_artifact.py --start-ts 2026-04-01T00:00:00Z --end-ts 2026-04-15T23:59:59Z
bash scripts/qc_health_check.sh --window-hours 1 --threshold 0.20 --consecutive 3 --min-snapshots 30
```
