# OptionTrader S4-03 EOD Evidence Runbook

Date: 2026-05-04
Owner: Dev team
Scope: End-to-end execution sequence for S4-03 using SPX EOD source-of-truth data.
Related issues: `#12`, `#14`, `#13`, `#15`, `#4`

## Purpose

Provide one deterministic execution path from raw EOD files to S4-03 ablation artifact output,
with explicit validation and evidence checkpoints.

## Required Inputs

- Raw data directory available: `/mnt/Data/OPTION_DATA`
- File pattern present: `spx_eod_YYYYMM.txt`
- Python venv ready in repo root (`.venv`)
- Data availability note: local dataset currently spans through 2023; use an available
  window for validation runs.

## Output Targets

- EOD truth DB: `data/optiontrader_eod_truth.duckdb`
- Validation report: `docs/roadmap/OptionTrader_S4_03_EOD_Validation_Report.md`
- S4-03 artifact: `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md`

## Single-Path Execution Order

Use this order exactly; do not skip steps.

1. `#12` ingest raw SPX EOD files into EOD truth DB.
2. `#14` run hard/soft validation checks and persist report.
3. `#13` materialize baseline/candidate tracks and run ablation pipeline.
4. `#15` run tests and verify reproducibility.

## Standard Environment

```bash
source .venv/bin/activate
export OPTIONTRADER_CONFIG=config/config-test.yaml
```

Create a dedicated config variant for EOD runs (example: `config/config-eod-truth.yaml`) with:

- `storage.path: data/optiontrader_eod_truth.duckdb`
- `data.underlying: SPX`
- fail-closed quality defaults unchanged

Then use:

```bash
export OPTIONTRADER_CONFIG=config/config-eod-truth.yaml
```

## Step 1 - Ingest SPX EOD Files (`#12`)

Expected script:

- `scripts/ingest_spx_eod_option_data.py`

Reference command:

```bash
python scripts/ingest_spx_eod_option_data.py \
  --input-dir /mnt/Data/OPTION_DATA \
  --glob "spx_eod_*.txt" \
  --underlying SPX
```

Checkpoint:

- snapshots and option_quotes inserted into `data/optiontrader_eod_truth.duckdb`
- rerun is idempotent (no duplicate natural keys)

## Step 2 - Validate Ingested EOD Data (`#14`)

Expected script:

- `scripts/validate_spx_eod_dataset.py`

Reference command:

```bash
python scripts/validate_spx_eod_dataset.py \
  --db-path data/optiontrader_eod_truth.duckdb \
  --report docs/roadmap/OptionTrader_S4_03_EOD_Validation_Report.md
```

Checkpoint:

- hard checks all pass (schema/timestamp/quote/order/key constraints)
- soft-check summary produced per date

## Step 3 - Materialize Tracks and Compute Evidence (`#13`)

Expected script:

- `scripts/materialize_s4_tracks_from_eod.py`

Reference command:

```bash
python scripts/materialize_s4_tracks_from_eod.py \
  --db-path data/optiontrader_eod_truth.duckdb \
  --baseline-lineage 3b024c9 \
  --candidate-lineage 5128e8e \
  --start-ts 2023-01-01T00:00:00Z \
  --end-ts 2023-12-31T23:59:59Z \
  --underlying SPX
```

Then run outcomes and ablation on the same DB/config:

```bash
python scripts/evaluate_alert_outcomes.py --horizon-days 5 --overwrite

python scripts/generate_regime_ablation_artifact.py \
  --start-ts 2023-01-01T00:00:00Z \
  --end-ts 2023-12-31T23:59:59Z \
  --baseline-lineage 3b024c9 \
  --candidate-lineage 5128e8e \
  --output docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md
```

Checkpoint:

- baseline and candidate both have non-zero snapshots on same calendar
- artifact generated with machine-readable gate summary

## Step 4 - Test and Reproducibility Gate (`#15`)

```bash
pytest tests/test_eod_ingest.py tests/test_s4_ablation.py -q
pytest -q
```

Checkpoint:

- parser, idempotency, validation behavior, and gate status logic pass
- rerunning steps 1-3 yields stable counts and artifact semantics

## Minimum Evidence Pack for PR

Include these artifacts in PR description:

1. row-count summary by lineage (snapshots, alerts, outcomes)
2. validation report path and key hard-check results
3. final ablation artifact path and top gate outcomes
4. exact commands used

## Decision Rule

- If sample/gate thresholds are met: move S4-03 toward closure recommendation.
- If thresholds remain unmet with valid EOD data: keep S4-03 blocked and document objective evidence
  in issue `#4`.

## Notes

- Keep synthetic methodology evidence separate (`#11` protocol).
- Do not change production thresholds inside this runbook workflow.
- If 2026 source files become available later, rerun with the locked 2026 window for parity with
  prior sprint artifacts.
