from src.core.health import compute_health_summary, latest_snapshot_summary


def test_health_summary(monkeypatch):
    class FakeConn:
        def __init__(self):
            self.counts = iter([1, 2, 3, 4, 5])

        def execute(self, _):
            return self

        def fetchone(self):
            return (next(self.counts),)

        def close(self):
            pass

    monkeypatch.setattr("src.core.health.connect", lambda: FakeConn())
    summary = compute_health_summary()
    assert summary.snapshots == 1
    assert summary.alerts == 5


def test_latest_snapshot_summary(monkeypatch):
    class FakeConn:
        def __init__(self):
            self.calls = 0

        def execute(self, _sql, _params=None):
            self.calls += 1
            return self

        def fetchone(self):
            if self.calls == 1:
                return (7, "2026-02-13T00:00:00")
            return (3,)

        def close(self):
            pass

    monkeypatch.setattr("src.core.health.connect", lambda: FakeConn())
    latest = latest_snapshot_summary()
    assert latest.snapshot_id == 7
    assert latest.alert_count == 3
