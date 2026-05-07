from __future__ import annotations

import subprocess
import sys


def test_validate_release_emits_payload_and_exit_code() -> None:
    cmd = [
        sys.executable,
        "scripts/validate_release.py",
        "--config-path",
        "config/config-test.yaml",
        "--start-ts",
        "2010-01-01T00:00:00Z",
        "--end-ts",
        "2010-02-28T23:59:59Z",
        "--underlying",
        "SPX",
        "--baseline-lineage",
        "3b024c9",
        "--candidate-lineage",
        "5128e8e",
        "--train-size",
        "10",
        "--test-size",
        "5",
        "--step-size",
        "5",
        "--skip-outcome-refresh",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode in {0, 2, 3}
    output = result.stdout
    assert '"contract"' in output
    assert '"gates"' in output
    assert '"recommendation"' in output


def test_adversarial_gate_runs_with_explicit_scenarios() -> None:
    cmd = [
        sys.executable,
        "scripts/validate_release.py",
        "--config-path",
        "config/config-test.yaml",
        "--start-ts",
        "2010-01-01T00:00:00Z",
        "--end-ts",
        "2010-02-28T23:59:59Z",
        "--underlying",
        "SPX",
        "--baseline-lineage",
        "3b024c9",
        "--candidate-lineage",
        "5128e8e",
        "--train-size",
        "10",
        "--test-size",
        "5",
        "--step-size",
        "5",
        "--skip-outcome-refresh",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout
    assert '"adversarial"' in output
    assert '"sparse_wings"' in output
    assert '"stale_books"' in output
    assert '"missing_tenors"' in output
    assert '"discontinuous_chain_snapshots"' in output
