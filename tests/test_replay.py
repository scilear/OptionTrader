import duckdb

from src.core.replay import replay_snapshots
from src.db.connection import connect


def test_replay_handles_empty_snapshots(monkeypatch):
    def fake_connect():
        conn = duckdb.connect(":memory:")
        conn.execute("CREATE TABLE snapshots (snapshot_id INTEGER, ts TIMESTAMP)")
        return conn

    monkeypatch.setattr("src.core.replay.connect", fake_connect)
    assert replay_snapshots(limit=5) == 0
