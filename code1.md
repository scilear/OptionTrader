Dev Instructions
- Start with these two docs (in order):
  1. docs/roadmap/OptionTrader_Sprint_1_Execution_Plan.md
  2. docs/roadmap/OptionTrader_Sprint_1_Dev_Ticket_Sheet.md
- Treat docs/roadmap/OptionTrader_Sprint_1_Dev_Ticket_Sheet.md as the source of truth for execution and acceptance.
- Work tickets strictly in this order:
  1. S1-01 Run manifest + snapshot linkage
  2. S1-02 Config digest + code version
  3. S1-03 Gate-by-gate alert trace
  4. S1-04 Rate/dividend plumbing
  5. S1-05 Determinism/provenance regression pack
- Scope guardrails (do not expand):
  - No surface model redesign
  - No regime redesign
  - No signal state-machine redesign
  - No execution-impact redesign
- Required implementation details (non-optional):
  - Add pipeline_runs + snapshots.run_id linkage.
  - Pass run_id through ingest path (dispatcher, ingest_ib, ingest_yfinance).
  - Use run-scoped snapshot lookup in pipeline.
  - Add config keys pricing.rate and pricing.dividend_yield.
  - Remove hardcoded rate=0.0 / div=0.0 from active compute path.
  - Persist normalized gate trace payload in alert explain.
- For each ticket:
  - Complete all implementation tasks in the ticket.
  - Check every acceptance checkbox before moving to next ticket.
  - Keep changes additive and backward-compatible where possible.
- Validation commands (must pass before handoff):
source .venv/bin/activate
pytest tests/test_schema.py tests/test_alerts_logic.py tests/test_iv_solve.py
pytest tests/test_run_manifest.py tests/test_config_digest.py tests/test_determinism.py tests/test_pricing_inputs.py
python scripts/run_pipeline.py
- Run post-implementation DB QA queries from:
  - docs/roadmap/OptionTrader_Sprint_1_Execution_Plan.md
  - docs/roadmap/OptionTrader_Sprint_1_Dev_Ticket_Sheet.md
- PR acceptance criteria:
  - All Sprint 1 ticket checkboxes completed.
  - Tests green.
  - SQL QA checks show traceability pipeline_runs -> snapshots -> alerts.
  - PR description maps code changes back to S1-01..S1-05.
