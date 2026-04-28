from __future__ import annotations

import os
from pathlib import Path
import pytest
import yaml
from datetime import datetime

from src.db.connection import connect
import scripts.run_pipeline as run_pipeline_module

def _write_test_config(tmp_path: Path) -> Path:
    config = yaml.safe_load(Path("config/config-test.yaml").read_text())
    config["storage"]["path"] = str(tmp_path / "reset_test.duckdb")
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    return config_path

def test_pipeline_reset_db_preserves_run_linkage(monkeypatch, tmp_path):
    """
    Ensures that OPTIONTRADER_RESET_DB=1 (which drops tables) 
    happens BEFORE the run row is created, not during ingest.
    """
    config_path = _write_test_config(tmp_path)
    monkeypatch.setenv("OPTIONTRADER_CONFIG", str(config_path))
    monkeypatch.setenv("OPTIONTRADER_RESET_DB", "1")

    # We want to use the real run_ingest -> yfinance path but mock the YF network call
    def fake_get_spot(ticker):
        return 5000.0

    # Mock ticker.options and ticker.option_chain to avoid network
    class FakeChain:
        calls = None
        puts = None

    class FakeTicker:
        def __init__(self, *args, **kwargs):
            self.options = [] # No expiries to process, just test the snapshot insert
        def history(self, *args, **kwargs):
            import pandas as pd
            return pd.DataFrame({"Close": [5000.0]})

    monkeypatch.setattr("src.ingest.ingest_yfinance.yf.Ticker", FakeTicker)
    monkeypatch.setattr("src.ingest.ingest_yfinance._get_spot", fake_get_spot)
    
    # Mock subsequent steps to isolate ingest
    monkeypatch.setattr(run_pipeline_module, "compute_regime_state", lambda: None)
    monkeypatch.setattr(run_pipeline_module, "compute_for_snapshot", lambda sid: None)

    # Execute pipeline
    run_pipeline_module.run_pipeline()

    # Verify run and snapshot exist and are linked
    conn = connect()
    try:
        run_row = conn.execute("SELECT run_id, status FROM pipeline_runs").fetchone()
        assert run_row is not None
        run_id = run_row[0]
        
        snap_row = conn.execute("SELECT snapshot_id, run_id FROM snapshots").fetchone()
        assert snap_row is not None
        assert snap_row[1] == run_id, "Snapshot run_id must match the active pipeline_run ID"
    finally:
        conn.close()
