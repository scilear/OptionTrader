# OptionTrader S4-03 Spec-to-Code Trace Matrix

Date: 2026-05-12
Mode: Read-only analysis (no code changes)
Spec reference: `docs/roadmap/OptionTrader_S4_03_Regime_Logic_Redefinition_and_Adversarial_Review.md`

## Sources reviewed

- `src/core/compute_snapshot.py`
- `src/core/regime.py`
- `scripts/materialize_s4_tracks_from_eod.py`
- `scripts/validate_release.py`
- `scripts/generate_regime_ablation_artifact.py`

## Trace Matrix

### 1) Missing regime handling must be explicit `Unknown` (no silent `Neutral` fallback)

- Spec clauses: 3.2.1, 5.2
- Code evidence:
  - `src/core/compute_snapshot.py:407` (default label is `Unknown` when no row)
  - `src/core/compute_snapshot.py:170` (`regime_missing` blocker)
  - `src/core/compute_snapshot.py:261` (regime gate fails on `Unknown`)
- Status: Implemented

### 2) `Unknown` cannot pass release falsification gates

- Spec clauses: 3.2.2, 7.2(1)
- Code evidence:
  - `scripts/validate_release.py:257` (`unknown_regime_count`)
  - `scripts/validate_release.py:259` (`unknown_regime_pass`)
  - `scripts/validate_release.py:261` (included in final pass expression)
  - `scripts/validate_release.py:271` (`unknown_regime_labels_present` blocker)
- Status: Implemented

### 3) Regime rows must be generated before snapshot compute in materialization

- Spec clauses: 3.2.3, 5.1
- Code evidence:
  - `scripts/materialize_s4_tracks_from_eod.py:328` (`compute_regime_state()` before baseline compute)
  - `scripts/materialize_s4_tracks_from_eod.py:334` (`compute_regime_state()` before candidate compute)
- Status: Implemented

### 4) Run/snapshot scope-safe labeling (no cross-run contamination)

- Spec clauses: 3.2.4, 5.4, Attack C
- Code evidence:
  - `src/core/regime.py:328` writes into shared date-keyed `regime_state`
  - `src/core/compute_snapshot.py:399` reads by date
  - `scripts/validate_release.py:170` joins by `regime_date = CAST(s.ts AS DATE)`
- Status: Partial (risk remains)
- Note: shared date table is still global; lineage/run-scoped isolation is not explicit.

### 5) Coverage validity checks (required regimes present or explicit fail)

- Spec clauses: 3.3(1), 7.2(2)
- Code evidence:
  - `scripts/validate_release.py:253` required regimes list
  - `scripts/validate_release.py:255` missing regimes derivation
  - `scripts/validate_release.py:256` coverage pass
  - `scripts/validate_release.py:265` blocker reason
- Status: Implemented (presence check)

### 6) Causality-safe features (trailing/expanding percentiles only)

- Spec clauses: 3.3(2), 5.3, Attack B
- Code evidence:
  - `src/core/regime.py:235` and `src/core/regime.py:236` use full-sample `.rank(pct=True)`
  - `src/core/regime.py:180` helper also uses full-sample ranking
- Status: Missing
- Note: lookahead leakage risk remains.

### 7) Minimum per-regime outcome counts for gate validity

- Spec clauses: Attack E, 7.2(2)
- Code evidence:
  - No minimum per-regime outcome-count enforcement in regime gate block
    (`scripts/validate_release.py:253-291`)
- Status: Missing

### 8) Threshold freeze before test period

- Spec clauses: Attack F, 7.2(3)
- Code evidence:
  - Contract metadata captured, but no explicit freeze-audit enforcement in validator
- Status: Missing

### 9) Independence diagnostics (contribution + correlation reporting)

- Spec clauses: 5.5, 7.2(4), Attack D
- Code evidence:
  - Component weight ledger is emitted: `scripts/validate_release.py:343-353`
  - No correlation diagnostics vs VIX/RV in release payload
- Status: Partial

### 10) Event feature governance / immutability safeguards

- Spec clauses: Attack G
- Code evidence:
  - Event file digest included in threshold hash path: `src/core/regime.py:111`, `src/core/regime.py:125`
  - No explicit validator check for effective-date immutability policy
- Status: Partial

### 11) Decision taxonomy alignment with V3

- Spec clauses: 7.3
- Code evidence:
  - Validator currently outputs `promotable`/`not_promotable`: `scripts/validate_release.py:442`
- Status: Missing
- Note: new taxonomy (`invalid_evidence`, `no_incremental_edge_observed`,
  `incremental_edge_confirmed`) not yet implemented.

## Additional issue identified

- `unknown_regime_share` denominator uses `outcomes_observed` rather than total candidate alerts:
  - `scripts/validate_release.py:258`
- Impact: can distort Unknown prevalence when outcome coverage is sparse.

## Overall assessment

- Original integration bug (regime generation + neutral masking): largely fixed.
- V3 evidence-validity redesign: partially implemented.
- Promotion-quality conclusions should be treated as incomplete under V3 until causality,
  per-regime sample validity, threshold freeze audit, and decision taxonomy are fully aligned.
