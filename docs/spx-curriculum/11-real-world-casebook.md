# Module 11 - Real-World Casebook (From This Dataset)

This module uses actual snapshots from `data/optiontrader.duckdb`.

Important context:

- At the time of writing, `alerts` table is empty for the current dataset window.
- Cases below are built from observed metric extremes and ingestion quality markers.
- Goal is to train decision/reflexion process, not to imply guaranteed outcomes.

## Case 1 - RR 30D shock then normalization (reversion candidate)

Observed data:

- metric: `rr25_mid`, bucket `30D`
- snapshot `11` (`2026-03-26 10:55:19`, source `yfinance`)
- value `-0.1190`, historical z approx `-2.27`
- following snapshots:
  - `13`: `-0.0341` (source `ib`)
  - `14`: `-0.0342` (source `ib`)

Interpretation:

- extreme downside skew reading followed by normalization.

Decision branch:

- **Reversion branch** is plausible.

Strategy mapping:

- candidate family: RR skew-fade (`SkewFade_PutSpread`) with strict risk fields.

Validation rationale:

- confirm worst-case RR and persistence,
- confirm execution quality before entry,
- document invalidation in case skew re-expands.

## Case 2 - TERM 30D one-snapshot spike at source switch (artifact risk)

Observed data:

- metric: `term_slope_mid`, bucket `30D`
- snapshot `16` (`2026-03-27 07:39:03`, source `yfinance`)
- value `0.0710`, historical z approx `+2.81`
- adjacent snapshots:
  - `15` (IB): `0.0029`
  - `17` (IB): `-0.0011`

Interpretation:

- large isolated spike occurred between IB snapshots, during temporary source change.

Decision branch:

- **No-trade branch** preferred (data/context uncertainty too high).

Strategy mapping:

- do **not** directly map to calendar trade from this point alone.

Validation rationale:

- data integrity gate weak (isolated jump + source transition),
- insufficient evidence for persistent term dislocation.

## Case 3 - RR 21D sign flip after source transition (continuation/repricing risk)

Observed data:

- metric: `rr25_mid`, bucket `21D`
- `15` (IB): `-0.0436`
- `16` (yfinance): `-0.0386`
- `17` (IB): `+0.0244` (historical z approx `+2.46`)

Interpretation:

- rapid sign flip from negative to positive RR can indicate call-side repricing,
- but context includes source transition and close spacing.

Decision branch:

- **Watch/continuation branch** is more coherent than automatic reversion.

Strategy mapping:

- avoid immediate skew-fade assumption,
- wait for additional confirmations on stable source/cadence.

Validation rationale:

- branch uncertainty is high; forcing mean reversion is not justified.

## Case 4 - Ingestion quality break (hard no-trade)

Observed data:

- snapshot `12` (`ib`)
- `iv_points=10`
- `metrics_rows=2` (missing one configured bucket)

Interpretation:

- coverage degraded materially relative to healthy snapshots (`metrics_rows=3`).

Decision branch:

- **No-trade branch** (hard block).

Strategy mapping:

- no mapping until ingestion quality is restored.

Validation rationale:

- data gate fails directly; any strategy decision is unreliable.

## Cross-Case Lessons

1. Not all extremes are reversion opportunities.
2. Isolated spikes near source/cadence disruptions are often non-tradable.
3. Branch selection (`reversion` / `continuation` / `no-trade`) must happen before template selection.
4. Data-quality failures should hard-block trade preparation.

## Practical Workflow (Use in App)

1. Use `Metric Explorer` to identify candidate distortion and inspect cadence/source.
2. Use `Alert Detail` decision summary gates for signal/data/regime/execution/risk evidence.
3. Fill `Decision Worksheet` (thesis + rationale + invalidation + max loss + size).
4. Export trade idea only when worksheet gate passes.
