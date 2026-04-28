from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
import yaml

from src.db.connection import connect
from src.db.init_db import init_db

import scripts.run_pipeline as run_pipeline_module


def _write_test_config(tmp_path: Path) -> Path:
    config = yaml.safe_load(Path("config/config-test.yaml").read_text())
    config["storage"]["path"] = str(tmp_path / "optiontrader.duckdb")
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    return config_path


def test_run_pipeline_writes_success_manifest_and_snapshot_link(monkeypatch, tmp_path):
    config_path = _write_test_config(tmp_path)
    monkeypatch.setenv("OPTIONTRADER_CONFIG", str(config_path))
    monkeypatch.setenv("OPTIONTRADER_RESET_DB", "1")

    def fake_run_ingest(run_id: int | None = None) -> None:
        conn = connect()
        try:
            conn.execute(
                """
                INSERT INTO snapshots (
                    snapshot_id, run_id, ts, underlying, spot, source, session_tag, notes
                ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?)
                """,
                (run_id, datetime(2026, 2, 13, 12, 0, 0), "SPX", 100.0, "test", "mid", None),
            )
        finally:
            conn.close()

    monkeypatch.setattr(run_pipeline_module, "run_ingest", fake_run_ingest)
    monkeypatch.setattr(run_pipeline_module, "compute_regime_state", lambda: None)
    monkeypatch.setattr(run_pipeline_module, "compute_for_snapshot", lambda snapshot_id: None)
    monkeypatch.setattr(run_pipeline_module, "_resolve_code_version", lambda: "test-sha")

    run_pipeline_module.run_pipeline()

    conn = connect()
    try:
        runs = conn.execute(
            """
            SELECT run_id, status, error_message, config_hash, code_version
            FROM pipeline_runs
            """
        ).fetchall()
        assert len(runs) == 1
        run_id, status, error_message, config_hash, code_version = runs[0]
        assert status == "success"
        assert error_message is None
        assert config_hash
        assert code_version == "test-sha"

        snapshot = conn.execute(
            "SELECT run_id FROM snapshots ORDER BY snapshot_id DESC LIMIT 1"
        ).fetchone()
        assert snapshot is not None
        assert snapshot[0] == run_id
    finally:
        conn.close()


def test_run_pipeline_marks_failure(monkeypatch, tmp_path):
    config_path = _write_test_config(tmp_path)
    monkeypatch.setenv("OPTIONTRADER_CONFIG", str(config_path))
    monkeypatch.setenv("OPTIONTRADER_RESET_DB", "1")
    monkeypatch.setattr(
        run_pipeline_module,
        "run_ingest",
        lambda run_id=None: (_ for _ in ()).throw(RuntimeError("ingest boom")),
    )
    monkeypatch.setattr(run_pipeline_module, "_resolve_code_version", lambda: "test-sha")

    with pytest.raises(RuntimeError, match="ingest boom"):
        run_pipeline_module.run_pipeline()

    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT status, error_message
            FROM pipeline_runs
            ORDER BY run_id DESC
            LIMIT 1
            """
        ).fetchone()
        assert row is not None
        assert row[0] == "failed"
        assert row[1] == "ingest boom"
    finally:
        conn.close()


def test_latest_snapshot_id_is_scoped_to_run(monkeypatch, tmp_path):
    config_path = _write_test_config(tmp_path)
    monkeypatch.setenv("OPTIONTRADER_CONFIG", str(config_path))
    monkeypatch.setenv("OPTIONTRADER_RESET_DB", "1")
    init_db()

    conn = connect()
    try:
        conn.execute(
            """
            INSERT INTO pipeline_runs (
                run_id, started_at, finished_at, status, config_hash, code_version, error_message
            ) VALUES
                (DEFAULT, ?, NULL, 'started', 'hash-1', 'sha-1', NULL),
                (DEFAULT, ?, NULL, 'started', 'hash-2', 'sha-2', NULL)
            """,
            (datetime(2026, 2, 13, 9, 0, 0), datetime(2026, 2, 13, 10, 0, 0)),
        )
        conn.execute(
            """
            INSERT INTO snapshots (
                snapshot_id, run_id, ts, underlying, spot, source, session_tag, notes
            ) VALUES
                (DEFAULT, 1, ?, 'SPX', 100.0, 'test', 'mid', NULL),
                (DEFAULT, 2, ?, 'SPX', 101.0, 'test', 'mid', NULL),
                (DEFAULT, 2, ?, 'SPX', 102.0, 'test', 'mid', NULL)
            """,
            (
                datetime(2026, 2, 13, 9, 30, 0),
                datetime(2026, 2, 13, 10, 30, 0),
                datetime(2026, 2, 13, 10, 45, 0),
            ),
        )
    finally:
        conn.close()

    assert run_pipeline_module._latest_snapshot_id(1) == 1
    assert run_pipeline_module._latest_snapshot_id(2) == 3
