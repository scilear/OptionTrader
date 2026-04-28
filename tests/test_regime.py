import duckdb
import pandas as pd

from src.core.regime import RegimeParams, compute_regime_state


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
                regime_label TEXT,
                regime_config_hash TEXT
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
                regime_label TEXT,
                regime_config_hash TEXT
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


def test_regime_thresholds_from_params_change_labels(monkeypatch):
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
            regime_label TEXT,
            regime_config_hash TEXT
        )
        """
    )
    dates = pd.date_range("2026-01-01", periods=80, freq="D")
    for i, d in enumerate(dates):
        conn.execute(
            "INSERT INTO snapshots (ts, spot) VALUES (?, ?)",
            (d.to_pydatetime(), 100 + i),
        )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.regime.connect", lambda: ConnWrapper(conn))

    high_thresholds = RegimeParams(
        vix_pct_calm=0,
        vix_pct_stress=0,
        rv20_pct_calm=0,
        rv20_pct_stress=0,
        drawdown_calm=0,
        drawdown_stress=0,
    )
    low_thresholds = RegimeParams(
        vix_pct_calm=100,
        vix_pct_stress=100,
        rv20_pct_calm=100,
        rv20_pct_stress=100,
        drawdown_calm=100,
        drawdown_stress=100,
    )

    compute_regime_state(params=high_thresholds)
    stress_label = conn.execute(
        "SELECT regime_label FROM regime_state ORDER BY regime_date DESC LIMIT 1"
    ).fetchone()[0]

    compute_regime_state(params=low_thresholds)
    calm_label = conn.execute(
        "SELECT regime_label FROM regime_state ORDER BY regime_date DESC LIMIT 1"
    ).fetchone()[0]

    assert stress_label == "Stress"
    assert calm_label == "Calm"
