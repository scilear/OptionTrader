from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import statistics
import sys
from typing import Any

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from scripts.evaluate_alert_outcomes import evaluate_alert_outcomes
from scripts.generate_regime_ablation_artifact import _fetch_precision_metrics
from src.core.config import load_config
from src.core.replay import replay_walk_forward
from src.db.connection import connect
from src.db.init_db import init_db


DEFAULT_CONTRACT_ID = "S7-CONTRACT-v1"
DEFAULT_START_TS = "2010-01-01T00:00:00Z"
DEFAULT_END_TS = "2023-12-31T23:59:59Z"
DEFAULT_UNDERLYING = "SPX"
DEFAULT_BASELINE_LINEAGE = "3b024c9"
DEFAULT_CANDIDATE_LINEAGE = "5128e8e"
DEFAULT_CONFIG_PATH = "config/config-eod-truth.yaml"
DEFAULT_OUTPUT_PATH = "docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Report.md"
DEFAULT_JSON_OUTPUT_PATH = "docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Payload.json"
DEFAULT_BASELINE_CAPTURE_PATH = "docs/roadmap/OptionTrader_Sprint_7_Baseline_Capture_v1.json"


def _lineage_meta(underlying: str, start_ts: str, end_ts: str, lineage_prefix: str) -> dict[str, Any]:
    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT pr.run_id, pr.code_version, pr.config_hash
            FROM pipeline_runs pr
            JOIN snapshots s ON s.run_id = pr.run_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            GROUP BY pr.run_id, pr.code_version, pr.config_hash
            ORDER BY pr.run_id DESC
            LIMIT 1
            """,
            (underlying, start_ts, end_ts, f"{lineage_prefix}%"),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return {
            "run_id": None,
            "code_version": None,
            "config_hash": None,
            "profile_id": None,
        }
    run_id, code_version, config_hash = row
    profile_id = None
    marker = "+profile:"
    code_version_value = str(code_version) if code_version is not None else None
    if code_version_value and marker in code_version_value:
        profile_id = code_version_value.split(marker, 1)[1]
    return {
        "run_id": int(run_id),
        "code_version": code_version_value,
        "config_hash": str(config_hash) if config_hash is not None else None,
        "profile_id": profile_id,
    }


def _walk_forward_gate(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    candidate_lineage: str,
    train_size: int,
    test_size: int,
    step_size: int,
) -> dict[str, Any]:
    splits = replay_walk_forward(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
        lineage_prefix=candidate_lineage,
        purge_existing=False,
        execute_test_replay=False,
    )
    test_lengths = [len(split.test_snapshot_ids) for split in splits]
    deterministic = len(set(test_lengths)) <= 1 if test_lengths else False
    return {
        "split_count": len(splits),
        "train_size": train_size,
        "test_size": test_size,
        "step_size": step_size,
        "test_window_lengths": test_lengths,
        "deterministic_schedule": deterministic,
        "pass": len(splits) > 0 and deterministic,
    }


def _adversarial_gate() -> dict[str, Any]:
    scenario_selectors = {
        "sparse_wings": "tests/test_surface_adversarial.py::test_sparse_wings_emit_degraded_status",
        "stale_books": "tests/test_surface_adversarial.py::test_stale_books_emit_no_alert",
        "missing_tenors": "tests/test_surface_adversarial.py::test_missing_tenors_term_slope_remains_null",
        "discontinuous_chain_snapshots": (
            "tests/test_surface_adversarial.py::test_discontinuous_chain_snapshots_emit_no_false_alert"
        ),
    }

    scenarios: dict[str, bool] = {}
    details: dict[str, dict[str, Any]] = {}
    for scenario, selector in scenario_selectors.items():
        cmd = [sys.executable, "-m", "pytest", selector, "-q"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        passed = result.returncode == 0
        scenarios[scenario] = passed
        details[scenario] = {
            "selector": selector,
            "returncode": int(result.returncode),
            "stdout": result.stdout.strip().splitlines()[-1:] if result.stdout else [],
            "stderr": result.stderr.strip().splitlines()[-1:] if result.stderr else [],
        }
    return {
        "scenarios": scenarios,
        "details": details,
        "pass": all(scenarios.values()),
    }


def _regime_stratified_summary(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    lineage_prefix: str,
    horizon_days: int,
) -> dict[str, dict[str, float | int | None]]:
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT
              COALESCE(a.regime_label, 'Unknown') AS regime_label,
              COUNT(*) AS alerts,
              SUM(CASE WHEN ao.outcome_label = 'tp' THEN 1 ELSE 0 END) AS tp,
              SUM(CASE WHEN ao.outcome_label = 'fp' THEN 1 ELSE 0 END) AS fp
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            LEFT JOIN alert_outcomes ao
              ON ao.alert_id = a.alert_id AND ao.horizon_days = ?
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            GROUP BY 1
            ORDER BY 1
            """,
            (horizon_days, underlying, start_ts, end_ts, f"{lineage_prefix}%"),
        ).fetchall()
    finally:
        conn.close()

    out: dict[str, dict[str, float | int | None]] = {}
    for regime_label, alerts, tp, fp in rows:
        tp_count = int(tp or 0)
        fp_count = int(fp or 0)
        precision = (tp_count / (tp_count + fp_count)) if (tp_count + fp_count) > 0 else None
        out[str(regime_label)] = {
            "alerts": int(alerts),
            "tp": tp_count,
            "fp": fp_count,
            "precision": precision,
        }
    return out


def _regime_gate(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    baseline_lineage: str,
    candidate_lineage: str,
    horizon_days: int,
) -> dict[str, Any]:
    baseline = _fetch_precision_metrics(
        underlying,
        start_ts,
        end_ts,
        baseline_lineage,
        horizon_days,
    )
    candidate = _fetch_precision_metrics(
        underlying,
        start_ts,
        end_ts,
        candidate_lineage,
        horizon_days,
    )
    baseline_precision = baseline.get("precision")
    candidate_precision = candidate.get("precision")
    precision_non_regression = (
        baseline_precision is not None
        and candidate_precision is not None
        and float(candidate_precision) >= float(baseline_precision)
    )
    transition_blocked_reason = None
    transition_ok = False
    if (
        baseline.get("transition_fp_density") is not None
        and candidate.get("transition_fp_density") is not None
    ):
        transition_ok = float(candidate["transition_fp_density"]) <= float(baseline["transition_fp_density"])
    else:
        transition_blocked_reason = "missing_transition_alerts"

    baseline_by_regime = _regime_stratified_summary(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        lineage_prefix=baseline_lineage,
        horizon_days=horizon_days,
    )
    candidate_by_regime = _regime_stratified_summary(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        lineage_prefix=candidate_lineage,
        horizon_days=horizon_days,
    )
    required_regimes = ["Calm", "Transition", "Stress"]
    observed_regimes = sorted(candidate_by_regime.keys())
    missing_regimes = [name for name in required_regimes if name not in candidate_by_regime]
    regime_coverage_pass = len(missing_regimes) == 0

    return {
        "horizon_days": horizon_days,
        "baseline": baseline,
        "candidate": candidate,
        "baseline_by_regime": baseline_by_regime,
        "candidate_by_regime": candidate_by_regime,
        "required_regimes": required_regimes,
        "observed_regimes": observed_regimes,
        "missing_regimes": missing_regimes,
        "regime_coverage_pass": regime_coverage_pass,
        "precision_non_regression": precision_non_regression,
        "transition_fp_density_non_worsening": transition_ok,
        "transition_fp_density_blocked_reason": transition_blocked_reason,
        "pass": regime_coverage_pass and precision_non_regression and transition_ok,
    }


def _ablation_gate(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    candidate_lineage: str,
    config_path: str,
) -> dict[str, Any]:
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT ti.scenarios
            FROM trade_ideas ti
            JOIN alerts a ON a.alert_id = ti.alert_id
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            """,
            (underlying, start_ts, end_ts, f"{candidate_lineage}%"),
        ).fetchall()
    finally:
        conn.close()

    edge_values: list[float] = []
    cost_values: list[float] = []
    for (scenarios_json,) in rows:
        if not scenarios_json:
            continue
        try:
            payload = json.loads(scenarios_json)
        except Exception:
            continue
        ranking = payload.get("ranking") if isinstance(payload, dict) else None
        if not isinstance(ranking, dict):
            continue
        edge = ranking.get("edge_after_cost")
        cost = ranking.get("total_friction_cost")
        if isinstance(edge, (int, float)):
            edge_values.append(float(edge))
        if isinstance(cost, (int, float)):
            cost_values.append(float(cost))

    mean_edge = statistics.mean(edge_values) if edge_values else None
    mean_cost = statistics.mean(cost_values) if cost_values else None

    cfg = load_config(path=Path(config_path))
    regime_weights = cfg.get("regime", {}).get("weights", {}) if isinstance(cfg, dict) else {}
    components = []
    for component_name in ["vix", "rv20", "drawdown", "event", "stress_proxy"]:
        weight = float(regime_weights.get(component_name, 0.0))
        components.append(
            {
                "component": component_name,
                "weight": weight,
                "status": "retained" if weight > 0.0 else "ablated",
            }
        )

    return {
        "ideas_with_ranking": len(edge_values),
        "mean_edge_after_cost": mean_edge,
        "mean_total_friction_cost": mean_cost,
        "component_ledger": components,
        "pass": len(edge_values) > 0,
    }


def _build_payload(
    *,
    contract_id: str,
    config_path: str,
    underlying: str,
    start_ts: str,
    end_ts: str,
    baseline_lineage: str,
    candidate_lineage: str,
    train_size: int,
    test_size: int,
    step_size: int,
    horizon_days: int,
) -> dict[str, Any]:
    lineage_metadata = {
        "baseline": _lineage_meta(underlying, start_ts, end_ts, baseline_lineage),
        "candidate": _lineage_meta(underlying, start_ts, end_ts, candidate_lineage),
    }

    walk_forward = _walk_forward_gate(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        candidate_lineage=candidate_lineage,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
    )
    adversarial = _adversarial_gate()
    regime = _regime_gate(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        baseline_lineage=baseline_lineage,
        candidate_lineage=candidate_lineage,
        horizon_days=horizon_days,
    )
    ablation = _ablation_gate(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        candidate_lineage=candidate_lineage,
        config_path=config_path,
    )

    gates = {
        "walk_forward_pass": walk_forward["pass"],
        "adversarial_resilience_pass": adversarial["pass"],
        "regime_falsification_pass": regime["pass"],
        "ablation_ledger_pass": ablation["pass"],
    }
    overall_pass = all(gates.values())
    gates["overall_pass"] = overall_pass

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "contract": {
            "id": contract_id,
            "config_path": config_path,
            "underlying": underlying,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "baseline_lineage": baseline_lineage,
            "candidate_lineage": candidate_lineage,
            "walk_forward": {
                "train_size": train_size,
                "test_size": test_size,
                "step_size": step_size,
            },
            "horizon_days": horizon_days,
        },
        "lineage_metadata": lineage_metadata,
        "walk_forward": walk_forward,
        "adversarial": adversarial,
        "regime_falsification": regime,
        "ablation_ledger": ablation,
        "gates": gates,
        "recommendation": "promotable" if overall_pass else "not_promotable",
    }


def _is_missing_lineage(payload: dict[str, Any]) -> bool:
    baseline_run = payload["lineage_metadata"]["baseline"].get("run_id")
    candidate_run = payload["lineage_metadata"]["candidate"].get("run_id")
    return baseline_run is None or candidate_run is None


def _render_markdown(payload: dict[str, Any], command: str) -> str:
    gates = payload["gates"]
    lines = [
        "# OptionTrader Sprint 7 Release Validation Report",
        "",
        f"Generated at: {payload['generated_at']}",
        "Source script: `scripts/validate_release.py`",
        "",
        "## Contract",
        "",
        f"- Contract ID: `{payload['contract']['id']}`",
        f"- Config path: `{payload['contract']['config_path']}`",
        f"- Underlying: `{payload['contract']['underlying']}`",
        f"- Start: `{payload['contract']['start_ts']}`",
        f"- End: `{payload['contract']['end_ts']}`",
        f"- Baseline lineage: `{payload['contract']['baseline_lineage']}`",
        f"- Candidate lineage: `{payload['contract']['candidate_lineage']}`",
        "",
        "## Gate Evaluation",
        "",
        f"- Walk-forward deterministic gate: {'PASS' if gates['walk_forward_pass'] else 'FAIL'}",
        (
            "- Adversarial resilience gate: "
            f"{'PASS' if gates['adversarial_resilience_pass'] else 'FAIL'}"
        ),
        (
            "- Regime falsification gate: "
            f"{'PASS' if gates['regime_falsification_pass'] else 'FAIL'}"
        ),
        f"- Ablation ledger gate: {'PASS' if gates['ablation_ledger_pass'] else 'FAIL'}",
        f"- Overall release gate: {'PASS' if gates['overall_pass'] else 'FAIL'}",
        "",
        "## Recommendation",
        "",
        f"- Final recommendation: `{payload['recommendation']}`",
        "",
        "## Summary Payload",
        "",
        "```json",
        json.dumps(payload, indent=2, sort_keys=True),
        "```",
        "",
        "## Reproducibility",
        "",
        "```bash",
        "source .venv/bin/activate",
        command,
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Sprint 7 release gates")
    parser.add_argument("--contract-id", default=DEFAULT_CONTRACT_ID)
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--start-ts", default=DEFAULT_START_TS)
    parser.add_argument("--end-ts", default=DEFAULT_END_TS)
    parser.add_argument("--underlying", default=DEFAULT_UNDERLYING)
    parser.add_argument("--baseline-lineage", default=DEFAULT_BASELINE_LINEAGE)
    parser.add_argument("--candidate-lineage", default=DEFAULT_CANDIDATE_LINEAGE)
    parser.add_argument("--train-size", type=int, default=252)
    parser.add_argument("--test-size", type=int, default=63)
    parser.add_argument("--step-size", type=int, default=63)
    parser.add_argument("--horizon-days", type=int, default=5)
    parser.add_argument("--report-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--payload-path", default=DEFAULT_JSON_OUTPUT_PATH)
    parser.add_argument("--baseline-capture-path", default=DEFAULT_BASELINE_CAPTURE_PATH)
    parser.add_argument("--skip-outcome-refresh", action="store_true")
    args = parser.parse_args()

    os.environ["OPTIONTRADER_CONFIG"] = args.config_path
    init_db()
    if not args.skip_outcome_refresh:
        evaluate_alert_outcomes(horizon_days=args.horizon_days, overwrite=False)

    payload = _build_payload(
        contract_id=args.contract_id,
        config_path=args.config_path,
        underlying=args.underlying,
        start_ts=args.start_ts,
        end_ts=args.end_ts,
        baseline_lineage=args.baseline_lineage,
        candidate_lineage=args.candidate_lineage,
        train_size=args.train_size,
        test_size=args.test_size,
        step_size=args.step_size,
        horizon_days=args.horizon_days,
    )
    command = (
        f"python scripts/validate_release.py --config-path {args.config_path} "
        f"--start-ts {args.start_ts} --end-ts {args.end_ts} "
        f"--underlying {args.underlying} --baseline-lineage {args.baseline_lineage} "
        f"--candidate-lineage {args.candidate_lineage} --train-size {args.train_size} "
        f"--test-size {args.test_size} --step-size {args.step_size} "
        f"--horizon-days {args.horizon_days}"
    )
    report_text = _render_markdown(payload, command)

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text + "\n", encoding="utf-8")

    payload_path = Path(args.payload_path)
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    baseline_capture = {
        "captured_at": payload["generated_at"],
        "contract": payload["contract"],
        "lineage_metadata": {
            "baseline": payload["lineage_metadata"]["baseline"],
        },
        "walk_forward": payload["walk_forward"],
        "regime_falsification": {
            "baseline": payload["regime_falsification"]["baseline"],
            "baseline_by_regime": payload["regime_falsification"].get("baseline_by_regime", {}),
        },
    }
    baseline_capture_path = Path(args.baseline_capture_path)
    baseline_capture_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_capture_path.write_text(
        json.dumps(baseline_capture, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(payload, indent=2, sort_keys=True))
    print(f"report_written={report_path}")
    print(f"payload_written={payload_path}")
    print(f"baseline_capture_written={baseline_capture_path}")
    if _is_missing_lineage(payload):
        raise SystemExit(3)
    if payload["gates"]["overall_pass"]:
        raise SystemExit(0)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
