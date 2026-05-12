# OptionTrader Sprint 7 Release Validation Report

Generated at: 2026-05-12T21:08:43.651658Z
Source script: `scripts/validate_release.py`

## Contract

- Contract ID: `S7-CONTRACT-v1`
- Config path: `config/config-eod-truth.yaml`
- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- End: `2023-12-31T23:59:59Z`
- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e`

## Gate Evaluation

- Walk-forward deterministic gate: PASS
- Adversarial resilience gate: PASS
- Regime falsification gate: FAIL
- Ablation ledger gate: FAIL
- Overall release gate: FAIL

## Recommendation

- Final recommendation: `not_promotable`
- Taxonomy verdict: `invalid_evidence`

## Summary Payload

```json
{
  "ablation_ledger": {
    "component_ledger": [
      {
        "component": "vix",
        "status": "retained",
        "weight": 0.25
      },
      {
        "component": "rv20",
        "status": "retained",
        "weight": 0.25
      },
      {
        "component": "drawdown",
        "status": "retained",
        "weight": 0.25
      },
      {
        "component": "event",
        "status": "ablated",
        "weight": 0.0
      },
      {
        "component": "stress_proxy",
        "status": "ablated",
        "weight": 0.0
      }
    ],
    "ideas_with_ranking": 0,
    "mean_edge_after_cost": null,
    "mean_total_friction_cost": null,
    "pass": false
  },
  "adversarial": {
    "details": {
      "discontinuous_chain_snapshots": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_discontinuous_chain_snapshots_emit_no_false_alert",
        "stderr": [],
        "stdout": [
          "1 passed in 0.57s"
        ]
      },
      "missing_tenors": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_missing_tenors_term_slope_remains_null",
        "stderr": [],
        "stdout": [
          "1 passed in 0.61s"
        ]
      },
      "sparse_wings": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_sparse_wings_emit_degraded_status",
        "stderr": [],
        "stdout": [
          "1 passed in 0.59s"
        ]
      },
      "stale_books": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_stale_books_emit_no_alert",
        "stderr": [],
        "stdout": [
          "1 passed in 0.56s"
        ]
      }
    },
    "pass": true,
    "scenarios": {
      "discontinuous_chain_snapshots": true,
      "missing_tenors": true,
      "sparse_wings": true,
      "stale_books": true
    }
  },
  "contract": {
    "baseline_lineage": "3b024c9",
    "candidate_lineage": "5128e8e",
    "config_path": "config/config-eod-truth.yaml",
    "end_ts": "2023-12-31T23:59:59Z",
    "horizon_days": 5,
    "id": "S7-CONTRACT-v1",
    "start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX",
    "walk_forward": {
      "step_size": 63,
      "test_size": 63,
      "train_size": 252
    }
  },
  "event_governance": {
    "blocked_reasons": [],
    "effective_date_immutability_pass": true,
    "event_calendar_exists": true,
    "event_path": "config/regime_events_v1.yaml"
  },
  "gates": {
    "ablation_ledger_pass": false,
    "adversarial_resilience_pass": true,
    "event_governance_pass": true,
    "overall_pass": false,
    "regime_falsification_pass": false,
    "threshold_freeze_pass": true,
    "walk_forward_pass": true
  },
  "generated_at": "2026-05-12T21:08:43.651658Z",
  "independence_diagnostics": {
    "baseline": {
      "contribution_shares": {
        "drawdown": 0.13665254237288219,
        "event": 0.0,
        "rv20": 0.3520921610169513,
        "stress_proxy": 0.18697033898304588,
        "vix": 0.3242849576271206
      },
      "correlation_stress_vs_rv20": 0.7847293985911984,
      "correlation_stress_vs_vix": 1.0,
      "near_redundant_feature_warning": true,
      "samples": 3437
    },
    "candidate": {
      "contribution_shares": {
        "drawdown": 0.13665254237288219,
        "event": 0.0,
        "rv20": 0.3520921610169513,
        "stress_proxy": 0.18697033898304588,
        "vix": 0.3242849576271206
      },
      "correlation_stress_vs_rv20": 0.7847293985911984,
      "correlation_stress_vs_vix": 1.0,
      "near_redundant_feature_warning": true,
      "samples": 3437
    }
  },
  "lineage_metadata": {
    "baseline": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
      "profile_id": "baseline_rv_only",
      "run_id": 29
    },
    "candidate": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 30
    }
  },
  "recommendation": "not_promotable",
  "regime_falsification": {
    "baseline": {
      "fp": 0,
      "outcomes_observed": 0,
      "precision": null,
      "tp": 0,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "baseline_by_regime": {},
    "blocked_reasons": [
      "missing_required_regimes",
      "precision_regression_or_missing",
      "missing_transition_alerts",
      "insufficient_per_regime_outcomes",
      "no_candidate_alerts"
    ],
    "candidate": {
      "fp": 0,
      "outcomes_observed": 0,
      "precision": null,
      "tp": 0,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "candidate_alert_count": 0,
    "candidate_by_regime": {},
    "evidence_valid": false,
    "horizon_days": 5,
    "min_required_outcomes_per_regime": 5,
    "missing_regimes": [
      "Calm",
      "Transition",
      "Stress"
    ],
    "observed_regimes": [],
    "outcome_validity_pass": false,
    "pass": false,
    "per_regime_outcome_counts": {
      "Calm": 0,
      "Stress": 0,
      "Transition": 0
    },
    "per_regime_outcome_validity": {
      "Calm": false,
      "Stress": false,
      "Transition": false
    },
    "precision_non_regression": false,
    "regime_coverage_pass": false,
    "required_regimes": [
      "Calm",
      "Transition",
      "Stress"
    ],
    "taxonomy_verdict": "invalid_evidence",
    "transition_fp_density_blocked_reason": "missing_transition_alerts",
    "transition_fp_density_non_worsening": false,
    "unknown_regime_count": 0,
    "unknown_regime_pass": true,
    "unknown_regime_share": null
  },
  "taxonomy_verdict": "invalid_evidence",
  "threshold_freeze": {
    "baseline_config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
    "blocked_reasons": [],
    "candidate_config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
    "current_config_hash": "ec039d97d121f629cd73d47701c3461b281498f2ab93fac5af85cafdb5609e2e",
    "threshold_freeze_pass": true
  },
  "walk_forward": {
    "deterministic_schedule": true,
    "pass": true,
    "split_count": 51,
    "step_size": 63,
    "test_size": 63,
    "test_window_lengths": [
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63
    ],
    "train_size": 252
  }
}
```

## Reproducibility

```bash
source .venv/bin/activate
python scripts/validate_release.py --config-path config/config-eod-truth.yaml --start-ts 2010-01-01T00:00:00Z --end-ts 2023-12-31T23:59:59Z --underlying SPX --baseline-lineage 3b024c9 --candidate-lineage 5128e8e --train-size 252 --test-size 63 --step-size 63 --horizon-days 5
```

