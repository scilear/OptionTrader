# OptionTrader Sprint 7 Release Validation Report

Generated at: 2026-05-22T02:48:37.798165Z
Source script: `scripts/validate_release.py`

## Contract

- Contract ID: `S7-CONTRACT-v1`
- Config path: `config/config-eod-truth.yaml`
- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- Effective start (post warm-up): `2010-04-05T00:00:00Z`
- End: `2012-12-31T23:59:59Z`
- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e-v2a`

## Gate Evaluation

- Walk-forward deterministic gate: PASS
- Adversarial resilience gate: PASS
- Regime falsification gate: FAIL
- Ablation ledger gate: FAIL
- Overall release gate: FAIL

## Warm-up Exclusion

- Warm-up exclusion applied: `True`
- Warm-up excluded days: `94`
- Requested start: `2010-01-01T00:00:00Z`
- Effective start: `2010-04-05T00:00:00Z`

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
          "1 passed in 0.56s"
        ]
      },
      "missing_tenors": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_missing_tenors_term_slope_remains_null",
        "stderr": [],
        "stdout": [
          "1 passed in 0.60s"
        ]
      },
      "sparse_wings": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_sparse_wings_emit_degraded_status",
        "stderr": [],
        "stdout": [
          "1 passed in 0.57s"
        ]
      },
      "stale_books": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_stale_books_emit_no_alert",
        "stderr": [],
        "stdout": [
          "1 passed in 0.58s"
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
    "candidate_lineage": "5128e8e-v2a",
    "config_path": "config/config-eod-truth.yaml",
    "effective_start_ts": "2010-04-05T00:00:00Z",
    "end_ts": "2012-12-31T23:59:59Z",
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
  "generated_at": "2026-05-22T02:48:37.798165Z",
  "independence_diagnostics": {
    "baseline": {
      "contribution_shares": {
        "drawdown": 0.0,
        "event": 0.0,
        "rv20": 0.5160599571734475,
        "stress_proxy": 0.0,
        "vix": 0.48394004282655245
      },
      "correlation_stress_vs_rv20": 0.7788632939693122,
      "correlation_stress_vs_vix": 1.0,
      "near_redundant_feature_warning": true,
      "samples": 683
    },
    "candidate": {
      "contribution_shares": {
        "drawdown": 0.0,
        "event": 0.0,
        "rv20": 0.0,
        "stress_proxy": 0.0,
        "vix": 0.0
      },
      "correlation_stress_vs_rv20": null,
      "correlation_stress_vs_vix": null,
      "near_redundant_feature_warning": false,
      "samples": 0
    }
  },
  "lineage_metadata": {
    "baseline": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "a6440afa83ff9f447c210ff9943e54243434132725f466e6bff0f9b1890c8c07",
      "profile_id": "baseline_rv_only",
      "run_id": 51
    },
    "candidate": {
      "code_version": "5128e8e-v2a+profile:candidate_multi_signal_v2a",
      "config_hash": "20776af3d4924050091369612d07a73770d51f41965c43a6de8b8dd71e9d70ec",
      "profile_id": "candidate_multi_signal_v2a",
      "run_id": 50
    }
  },
  "recommendation": "not_promotable",
  "regime_falsification": {
    "baseline": {
      "fp": 141,
      "outcomes_observed": 165,
      "precision": 0.14545454545454545,
      "tp": 24,
      "transition_alerts": 57,
      "transition_fp": 22,
      "transition_fp_density": 0.38596491228070173
    },
    "baseline_by_regime": {
      "Calm": {
        "alerts": 40,
        "fp": 11,
        "precision": 0.15384615384615385,
        "tp": 2
      },
      "Stress": {
        "alerts": 176,
        "fp": 108,
        "precision": 0.10743801652892562,
        "tp": 13
      },
      "Transition": {
        "alerts": 57,
        "fp": 22,
        "precision": 0.2903225806451613,
        "tp": 9
      }
    },
    "blocked_reasons": [
      "missing_required_regimes",
      "precision_regression_or_missing",
      "missing_transition_alerts",
      "insufficient_per_regime_outcomes",
      "missing_transition_fp_density",
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
    "transition_metric_available": false,
    "unknown_regime_count": 0,
    "unknown_regime_pass": true,
    "unknown_regime_share": null
  },
  "taxonomy_verdict": "invalid_evidence",
  "threshold_freeze": {
    "baseline_config_hash": "a6440afa83ff9f447c210ff9943e54243434132725f466e6bff0f9b1890c8c07",
    "blocked_reasons": [],
    "candidate_config_hash": "20776af3d4924050091369612d07a73770d51f41965c43a6de8b8dd71e9d70ec",
    "current_config_hash": "ec039d97d121f629cd73d47701c3461b281498f2ab93fac5af85cafdb5609e2e",
    "threshold_freeze_pass": true
  },
  "walk_forward": {
    "deterministic_schedule": true,
    "pass": true,
    "split_count": 6,
    "step_size": 63,
    "test_size": 63,
    "test_window_lengths": [
      63,
      63,
      63,
      63,
      63,
      63
    ],
    "train_size": 252
  },
  "window": {
    "effective_start_ts": "2010-04-05T00:00:00Z",
    "end_ts": "2012-12-31T23:59:59Z",
    "regime_ready_dates": {
      "baseline": "2010-04-05",
      "candidate": "2010-04-05"
    },
    "requested_start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX",
    "warmup_excluded_days": 94,
    "warmup_exclusion_applied": true
  }
}
```

## Reproducibility

```bash
source .venv/bin/activate
python scripts/validate_release.py --config-path config/config-eod-truth.yaml --start-ts 2010-01-01T00:00:00Z --end-ts 2012-12-31T23:59:59Z --underlying SPX --baseline-lineage 3b024c9 --candidate-lineage 5128e8e-v2a --train-size 252 --test-size 63 --step-size 63 --horizon-days 5
```

