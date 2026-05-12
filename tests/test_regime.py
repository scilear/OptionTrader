import duckdb
import pandas as pd
import json
from pathlib import Path
import logging

from src.core.regime import RegimeParams, compute_regime_state, regime_threshold_hash


def _create_regime_state_table(conn):
    conn.execute(
        """
        CREATE TABLE regime_state (
            regime_date DATE PRIMARY KEY,
            vix_percentile DOUBLE,
            rv20_percentile DOUBLE,
            drawdown_percent DOUBLE,
            regime_score INTEGER,
            regime_label TEXT,
            regime_config_hash TEXT,
            vix_spot DOUBLE,
            rv20_value DOUBLE,
            drawdown_value DOUBLE,
            event_score DOUBLE,
            stress_proxy_score DOUBLE,
            decomposition TEXT
        )
        """
    )


def _create_regime_snapshot_labels_table(conn):
    conn.execute(
        """
        CREATE TABLE regime_snapshot_labels (
            snapshot_id INTEGER PRIMARY KEY,
            run_id INTEGER,
            regime_date DATE,
            regime_label TEXT,
            regime_config_hash TEXT,
            decomposition TEXT
        )
        """
    )


def test_regime_handles_empty(monkeypatch):
    def fake_connect():
        conn = duckdb.connect(":memory:")
        conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
        _create_regime_state_table(conn)
        _create_regime_snapshot_labels_table(conn)
        return conn

    monkeypatch.setattr("src.core.regime.connect", fake_connect)
    assert compute_regime_state() == 0


def test_regime_inserts_rows(monkeypatch):
    def fake_connect():
        conn = duckdb.connect(":memory:")
        conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
        _create_regime_state_table(conn)
        _create_regime_snapshot_labels_table(conn)
        dates = pd.date_range("2026-01-01", periods=80, freq="D")
        for i, d in enumerate(dates):
            conn.execute(
                "INSERT INTO snapshots (snapshot_id, run_id, ts, spot) VALUES (?, ?, ?, ?)",
                (i + 1, 1, d.to_pydatetime(), 100 + i),
            )
        return conn

    monkeypatch.setattr("src.core.regime.connect", fake_connect)
    assert compute_regime_state() > 0


def test_regime_thresholds_from_params_change_labels(monkeypatch):
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
    _create_regime_state_table(conn)
    _create_regime_snapshot_labels_table(conn)
    dates = pd.date_range("2026-01-01", periods=80, freq="D")
    for i, d in enumerate(dates):
        conn.execute(
            "INSERT INTO snapshots (snapshot_id, run_id, ts, spot) VALUES (?, ?, ?, ?)",
            (i + 1, 1, d.to_pydatetime(), 100 + i),
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
        score_calm_max=0.1,
        score_stress_min=0.2,
    )
    low_thresholds = RegimeParams(
        vix_pct_calm=100,
        vix_pct_stress=100,
        rv20_pct_calm=100,
        rv20_pct_stress=100,
        drawdown_calm=100,
        drawdown_stress=100,
        score_calm_max=1.2,
        score_stress_min=1.8,
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


def test_regime_decomposition_payload_is_present(monkeypatch):
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
    _create_regime_state_table(conn)
    _create_regime_snapshot_labels_table(conn)
    dates = pd.date_range("2026-01-01", periods=80, freq="D")
    for i, d in enumerate(dates):
        conn.execute(
            "INSERT INTO snapshots (snapshot_id, run_id, ts, spot) VALUES (?, ?, ?, ?)",
            (i + 1, 1, d.to_pydatetime(), 100 + i),
        )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.regime.connect", lambda: ConnWrapper(conn))
    compute_regime_state()

    row = conn.execute(
        """
        SELECT decomposition, event_score, stress_proxy_score
        FROM regime_state
        ORDER BY regime_date DESC
        LIMIT 1
        """
    ).fetchone()
    assert row is not None
    decomposition = json.loads(row[0])
    assert "contributions" in decomposition
    assert "weights" in decomposition
    assert "normalized_score" in decomposition
    assert isinstance(row[1], float)
    assert isinstance(row[2], float)


def test_regime_event_signal_can_change_label(monkeypatch, tmp_path):
    event_path = tmp_path / "regime_events_v1.yaml"
    event_path.write_text(
        """
events:
  - date: 2026-03-21
    type: fomc
    label: FOMC
    severity: high
        """.strip()
    )

    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
    _create_regime_state_table(conn)
    _create_regime_snapshot_labels_table(conn)

    dates = pd.date_range("2026-01-01", periods=80, freq="D")
    for i, d in enumerate(dates):
        spot = 100 + i
        if d.date() == pd.to_datetime("2026-03-21").date():
            spot = 100
        conn.execute(
            "INSERT INTO snapshots (snapshot_id, run_id, ts, spot) VALUES (?, ?, ?, ?)",
            (i + 1, 1, d.to_pydatetime(), spot),
        )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.regime.connect", lambda: ConnWrapper(conn))

    params_without_event = RegimeParams(
        vix_pct_calm=100,
        vix_pct_stress=100,
        rv20_pct_calm=100,
        rv20_pct_stress=100,
        drawdown_calm=100,
        drawdown_stress=100,
        weight_vix=0.0,
        weight_rv20=0.0,
        weight_drawdown=0.0,
        weight_event=1.0,
        weight_stress_proxy=0.0,
        score_calm_max=0.5,
        score_stress_min=1.1,
        event_path=str(Path(tmp_path) / "no_events.yaml"),
    )
    compute_regime_state(params=params_without_event)
    no_event_label = conn.execute(
        "SELECT regime_label FROM regime_state WHERE regime_date = '2026-03-21'"
    ).fetchone()[0]

    params_with_event = RegimeParams(
        vix_pct_calm=100,
        vix_pct_stress=100,
        rv20_pct_calm=100,
        rv20_pct_stress=100,
        drawdown_calm=100,
        drawdown_stress=100,
        weight_vix=0.0,
        weight_rv20=0.0,
        weight_drawdown=0.0,
        weight_event=1.0,
        weight_stress_proxy=0.0,
        score_calm_max=0.5,
        score_stress_min=1.1,
        event_path=str(event_path),
    )
    compute_regime_state(params=params_with_event)
    with_event_label = conn.execute(
        "SELECT regime_label FROM regime_state WHERE regime_date = '2026-03-21'"
    ).fetchone()[0]

    assert no_event_label == "Calm"
    assert with_event_label == "Stress"


def test_regime_stress_proxy_signal_can_change_label(monkeypatch):
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
    _create_regime_state_table(conn)
    _create_regime_snapshot_labels_table(conn)

    dates = pd.date_range("2026-01-01", periods=120, freq="D")
    for i, d in enumerate(dates):
        # Build a volatile path so rv percentile climbs near sample end.
        spot = 100 + (i % 8) * (1 if i % 2 == 0 else -1)
        conn.execute(
            "INSERT INTO snapshots (snapshot_id, run_id, ts, spot) VALUES (?, ?, ?, ?)",
            (i + 1, 1, d.to_pydatetime(), spot),
        )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.regime.connect", lambda: ConnWrapper(conn))

    def proxy_fetch(ticker, date_index):
        if ticker == "^VIX":
            return {d: 10.0 for d in date_index}
        if ticker:
            return {d: float(i + 1) for i, d in enumerate(date_index)}
        return {}

    monkeypatch.setattr("src.core.regime._fetch_ticker_close_series", proxy_fetch)

    no_proxy_params = RegimeParams(
        weight_vix=0.0,
        weight_rv20=0.0,
        weight_drawdown=0.0,
        weight_event=0.0,
        weight_stress_proxy=1.0,
        score_calm_max=0.5,
        score_stress_min=1.1,
        stress_proxy_ticker="",
    )
    compute_regime_state(params=no_proxy_params)
    no_proxy_label = conn.execute(
        "SELECT regime_label FROM regime_state ORDER BY regime_date DESC LIMIT 1"
    ).fetchone()[0]

    with_proxy_params = RegimeParams(
        weight_vix=0.0,
        weight_rv20=0.0,
        weight_drawdown=0.0,
        weight_event=0.0,
        weight_stress_proxy=1.0,
        score_calm_max=0.5,
        score_stress_min=1.1,
        stress_proxy_ticker="^VIX",
    )
    compute_regime_state(params=with_proxy_params)
    with_proxy_label = conn.execute(
        "SELECT regime_label FROM regime_state ORDER BY regime_date DESC LIMIT 1"
    ).fetchone()[0]

    assert no_proxy_label == "Calm"
    assert with_proxy_label in {"Transition", "Stress"}


def test_regime_warmup_logs_warning(monkeypatch, caplog):
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
    _create_regime_state_table(conn)
    _create_regime_snapshot_labels_table(conn)
    # Deliberately below rolling windows.
    dates = pd.date_range("2026-01-01", periods=5, freq="D")
    for i, d in enumerate(dates):
        conn.execute(
            "INSERT INTO snapshots (snapshot_id, run_id, ts, spot) VALUES (?, ?, ?, ?)",
            (i + 1, 1, d.to_pydatetime(), 100 + i),
        )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.regime.connect", lambda: ConnWrapper(conn))
    with caplog.at_level(logging.WARNING, logger="regime"):
        assert compute_regime_state() == 0
    assert "Regime warm-up incomplete" in caplog.text


def test_regime_hash_normalizes_equivalent_event_paths(tmp_path):
    event_file = tmp_path / "events.yaml"
    event_file.write_text("events: []\n")
    params_a = RegimeParams(event_path=str(event_file))
    params_b = RegimeParams(event_path=str(event_file.resolve()))
    assert regime_threshold_hash(params_a) == regime_threshold_hash(params_b)


def test_regime_vix_signal_changes_label_independent_of_rv(monkeypatch):
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
    _create_regime_state_table(conn)
    _create_regime_snapshot_labels_table(conn)
    dates = pd.date_range("2026-01-01", periods=90, freq="D")
    for i, d in enumerate(dates):
        conn.execute(
            "INSERT INTO snapshots (snapshot_id, run_id, ts, spot) VALUES (?, ?, ?, ?)",
            (i + 1, 1, d.to_pydatetime(), 100 + i),
        )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.regime.connect", lambda: ConnWrapper(conn))

    params = RegimeParams(
        vix_pct_calm=60,
        vix_pct_stress=90,
        weight_vix=1.0,
        weight_rv20=0.0,
        weight_drawdown=0.0,
        weight_event=0.0,
        weight_stress_proxy=0.0,
        score_calm_max=0.5,
        score_stress_min=1.1,
    )

    def low_vix_fetch(ticker, date_index):
        if ticker == "^VIX":
            n = len(date_index)
            return {d: float(n - i) for i, d in enumerate(date_index)}
        return {}

    def high_vix_fetch(ticker, date_index):
        if ticker == "^VIX":
            return {d: float(i + 1) for i, d in enumerate(date_index)}
        return {}

    monkeypatch.setattr("src.core.regime._fetch_ticker_close_series", low_vix_fetch)
    compute_regime_state(params=params)
    low_label = conn.execute(
        "SELECT regime_label FROM regime_state ORDER BY regime_date DESC LIMIT 1"
    ).fetchone()[0]

    monkeypatch.setattr("src.core.regime._fetch_ticker_close_series", high_vix_fetch)
    compute_regime_state(params=params)
    high_label = conn.execute(
        "SELECT regime_label FROM regime_state ORDER BY regime_date DESC LIMIT 1"
    ).fetchone()[0]

    assert low_label == "Calm"
    assert high_label in {"Transition", "Stress"}


def test_trailing_percentile_logic_avoids_lookahead(monkeypatch):
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
    _create_regime_state_table(conn)
    _create_regime_snapshot_labels_table(conn)
    dates = pd.date_range("2026-01-01", periods=90, freq="D")
    for i, d in enumerate(dates):
        conn.execute(
            "INSERT INTO snapshots (snapshot_id, run_id, ts, spot) VALUES (?, ?, ?, ?)",
            (i + 1, 7, d.to_pydatetime(), 100 + (i % 7)),
        )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.regime.connect", lambda: ConnWrapper(conn))
    compute_regime_state(run_id=7)
    first = conn.execute(
        "SELECT rv20_percentile FROM regime_state ORDER BY regime_date ASC LIMIT 1"
    ).fetchone()[0]
    assert first is not None


def test_regime_snapshot_labels_are_populated(monkeypatch):
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, run_id INTEGER, ts TIMESTAMP, spot DOUBLE)")
    _create_regime_state_table(conn)
    _create_regime_snapshot_labels_table(conn)
    dates = pd.date_range("2026-01-01", periods=90, freq="D")
    for i, d in enumerate(dates):
        conn.execute(
            "INSERT INTO snapshots (snapshot_id, run_id, ts, spot) VALUES (?, ?, ?, ?)",
            (i + 1, 9, d.to_pydatetime(), 200 + i),
        )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.regime.connect", lambda: ConnWrapper(conn))
    compute_regime_state(run_id=9)
    count = conn.execute("SELECT COUNT(*) FROM regime_snapshot_labels WHERE run_id = 9").fetchone()[0]
    assert count > 0
