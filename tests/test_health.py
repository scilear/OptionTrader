from src.core.health import compute_health_summary


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
