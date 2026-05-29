# OptionTrader S4-03 EOD Source-of-Truth Spec

Date: 2026-05-04
Scope: Use SPX end-of-day option-chain files under `/mnt/Data/OPTION_DATA` to produce
production-grade S4-03 ablation evidence.
Related issues: `#2`, `#3`, `#4`, `#11`

## Objective

Provide a reproducible, validated EOD data path that can produce non-zero baseline/candidate alert
samples for S4-03 gate evaluation without weakening production thresholds.

## Data Source

- Directory: `/mnt/Data/OPTION_DATA`
- File pattern: `spx_eod_YYYYMM.txt`
- Format: CSV-like text with header, column names wrapped in brackets.
- One raw row contains both call and put quotes for the same `(QUOTE_DATE, EXPIRE_DATE, STRIKE)`.

## Design Decision

Maintain a separate EOD truth database from intraday runtime DB.

- Runtime DB: existing `data/optiontrader.duckdb`.
- EOD truth DB (new): recommended `/mnt/Data/EVA/optiontrader_eod_truth.duckdb`.

This prevents intraday process side effects from contaminating S4-03 production evidence runs.

## Ingestion Contract (v1)

### Snapshot granularity

- One snapshot per unique `(QUOTE_UNIXTIME, QUOTE_DATE, QUOTE_TIME_HOURS)` for SPX.
- `snapshots.ts`: use `QUOTE_UNIXTIME` as authoritative UTC timestamp.
- `snapshots.underlying`: `SPX`.
- `snapshots.spot`: `UNDERLYING_LAST`.
- `snapshots.source`: `option_data_eod`.
- `snapshots.session_tag`: `eod`.
- `snapshots.notes`: include source filename and raw readtime.

### Option quote mapping

Each raw row becomes two `option_quotes` rows:

1. Call leg (`option_right='C'`)
2. Put leg (`option_right='P'`)

Field mapping:

- `expiry` <- `EXPIRE_DATE`
- `strike` <- `STRIKE`
- `bid/ask/last` <- side-specific (`C_*` or `P_*`)
- `volume` <- `C_VOLUME` or `P_VOLUME`
- `bid_size/ask_size` <- parsed from `C_SIZE` / `P_SIZE` formatted like `12 x 14`
- `oi` <- `NULL` (not provided by this file format unless confirmed in future variants)
- `flags` <- JSON with parse diagnostics (missing iv/greeks, crossed market, zero bid, etc.)

### Natural key and idempotency

Use deterministic natural key to avoid duplicate loads:

- snapshot key: `(ts, underlying, source, session_tag)`
- quote key: `(snapshot_id, expiry, strike, option_right)`

Re-running ingestion for same files must be idempotent (upsert/replace behavior).

## Required Validation Layer

Run validation after each ingestion batch and fail the batch if hard checks fail.

### Hard checks (must pass)

1. Required columns present in header.
2. `QUOTE_UNIXTIME` parseable and consistent with `QUOTE_DATE` (timezone-tolerant sanity).
3. `UNDERLYING_LAST > 0`.
4. `EXPIRE_DATE >= QUOTE_DATE` for non-negative DTE cases.
5. `ask >= bid` when both exist and non-zero.
6. No duplicate natural keys after load.

### Soft checks (warn + report)

1. Missing side-IV ratio by date.
2. Missing greeks ratio by date/tenor.
3. Extreme spread ratio tails.
4. DTE distribution anomalies.
5. Coverage counts (`expiries`, strikes, rows per date) versus trailing baseline.

Validation output should be persisted as a report artifact in `docs/roadmap/`.

## Derived Compute Pipeline on EOD DB

After ingestion, run existing compute pipeline components against EOD DB:

1. `compute_regime_state()`
2. `compute_for_snapshot(snapshot_id, purge_existing=True)` for EOD snapshots
3. `evaluate_alert_outcomes.py`
4. `generate_regime_ablation_artifact.py`

No threshold relaxation is allowed for production evidence mode.

## Baseline vs Candidate Track Materialization

For S4-03 evidence, create explicit lineages in `pipeline_runs.code_version`:

- baseline: `3b024c9`
- candidate: `5128e8e`

Tracks must use the same EOD snapshot calendar and only differ by model path/config profile.
Lineage relabeling alone is insufficient.

## Outcomes and Gate Semantics

- Keep current gate contract:
  - minimum sample gate,
  - precision lift gate,
  - volume guardrail,
  - transition FP density worsening.
- For EOD sources, document whether horizon is calendar-day or trading-day.
  - v1 default may remain calendar-day if unchanged,
  - any trading-day horizon switch must be explicit and tested.

## Deliverables for Dev

1. Ingestion script for `/mnt/Data/OPTION_DATA` into EOD truth DB.
2. Validation script/report for hard + soft checks.
3. Deterministic lineage materialization workflow (baseline/candidate) on EOD DB.
4. Reproducible ablation artifact generated from EOD truth DB.
5. Test coverage for parser, key constraints, and validation checks.

## Recommended New/Updated Files

- `scripts/ingest_spx_eod_option_data.py`
- `scripts/validate_spx_eod_dataset.py`
- `scripts/materialize_s4_tracks_from_eod.py`
- `tests/test_eod_ingest.py`
- `tests/test_s4_ablation.py` (extend)
- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md` (regenerated)

## Non-Goals

- Replacing intraday DB with EOD DB.
- Using synthetic-only evidence for final production sign-off.
- Mixing SPY proxy dataset into SPX contract without explicit approved mapping.
