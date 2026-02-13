import duckdb
import pandas as pd

from src.core.regime import compute_regime_state


def test_regime_handles_empty(monkeypatch):
    def fake_connect():
        conn = duckdb.connect(":memory:")
        conn.execute("CREATE TABLE snapshots (ts TIMESTAMP, spot DOUBLE)")
        conn.execute(
            """
            CREATE TABLE regime_state (
                regime_date DATE PRIMARY KEY,
                vix_percentile DOUBLE,
                rv20_percentile DOUBLE,
                drawdown_percent DOUBLE,
                regime_score INTEGER,
                regime_label TEXT
            )
            """
        )
        return conn

    monkeypatch.setattr("src.core.regime.connect", fake_connect)
    assert compute_regime_state() == 0


def test_regime_inserts_rows(monkeypatch):
    def fake_connect():
        conn = duckdb.connect(":memory:")
        conn.execute("CREATE TABLE snapshots (ts TIMESTAMP, spot DOUBLE)")
        conn.execute(
            """
            CREATE TABLE regime_state (
                regime_date DATE PRIMARY KEY,
                vix_percentile DOUBLE,
                rv20_percentile DOUBLE,
                drawdown_percent DOUBLE,
                regime_score INTEGER,
                regime_label TEXT
            )
            """
        )
        dates = pd.date_range("2026-01-01", periods=80, freq="D")
        for i, d in enumerate(dates):
            conn.execute(
                "INSERT INTO snapshots (ts, spot) VALUES (?, ?)",
                (d.to_pydatetime(), 100 + i),
            )
        return conn

    monkeypatch.setattr("src.core.regime.connect", fake_connect)
    assert compute_regime_state() > 0
