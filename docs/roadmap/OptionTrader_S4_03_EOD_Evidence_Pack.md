# OptionTrader S4-03 EOD Evidence Pack

Date: 2026-05-04
Window used: `2023-01-01T00:00:00Z` to `2023-01-10T23:59:59Z` (available local source-data range)
Runbook: `docs/roadmap/OptionTrader_S4_03_EOD_Runbook.md`

## Commands Executed

```bash
source .venv/bin/activate
export OPTIONTRADER_CONFIG=config/config-eod-truth.yaml

# Step 2
python scripts/validate_spx_eod_dataset.py \
  --db-path data/optiontrader_eod_truth.duckdb \
  --report docs/roadmap/OptionTrader_S4_03_EOD_Validation_Report.md

# Step 3
python scripts/materialize_s4_tracks_from_eod.py \
  --db-path data/optiontrader_eod_truth.duckdb \
  --baseline-lineage 3b024c9 \
  --candidate-lineage 5128e8e \
  --start-ts 2023-01-01T00:00:00Z \
  --end-ts 2023-01-10T23:59:59Z \
  --underlying SPX

python scripts/evaluate_alert_outcomes.py --horizon-days 5 --overwrite

python scripts/generate_regime_ablation_artifact.py \
  --start-ts 2023-01-01T00:00:00Z \
  --end-ts 2023-01-10T23:59:59Z \
  --baseline-lineage 3b024c9 \
  --candidate-lineage 5128e8e \
  --output docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md

# Step 4
pytest tests/test_eod_ingest.py tests/test_s4_ablation.py -q
pytest -q
```

## Data Validation Summary

- Validation report: `docs/roadmap/OptionTrader_S4_03_EOD_Validation_Report.md`
- Hard checks: all PASS
- Source truth counts:
  - snapshots: `8`
  - quotes: `111398`

## Lineage Row Counts

- Baseline lineage (`3b024c9`): snapshots `5`, alerts `0`, outcomes `0`
- Candidate lineage (`5128e8e`): snapshots `5`, alerts `0`, outcomes `0`

## Ablation Outcome

- Artifact: `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md`
- Gate result: overall `FAIL`
- Blocking reasons:
  - minimum sample gate unmet
  - no outcomes observed (`precision_blocked_reason=missing_outcome_labels`)
  - volume guardrail/transition FP gates non-computable under zero-alert sample

## Decision

S4-03 remains blocked on current objective evidence. Retain fail-closed defaults and keep
`event` / `stress_proxy` disabled until sample and precision gates are satisfiable on a valid EOD run.
