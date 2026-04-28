from __future__ import annotations

import inspect

from src.ingest.dispatcher import run_ingest


def test_data_source_yfinance_bypasses_ib(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.ingest.dispatcher.load_config",
        lambda: {
            "data": {"source": "yfinance"},
        },
    )

    calls: dict[str, int] = {"ib": 0, "yf": 0}

    def fake_try_ingest_ib(config, run_id=None):
        calls["ib"] += 1
        return True

    def fake_yf_ingest(run_id=None):
        calls["yf"] += 1

    monkeypatch.setattr("src.ingest.ingest_ib.try_ingest_ib", fake_try_ingest_ib)
    monkeypatch.setattr("src.ingest.ingest_yfinance.run_ingest", fake_yf_ingest)

    run_ingest(run_id=42)

    assert calls["ib"] == 0
    assert calls["yf"] == 1


def test_data_source_ib_keeps_fallback_behavior(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.ingest.dispatcher.load_config",
        lambda: {
            "data": {"source": "ib"},
        },
    )

    calls: dict[str, int] = {"ib": 0, "yf": 0}

    def fake_try_ingest_ib(config, run_id=None):
        calls["ib"] += 1
        return False

    def fake_yf_ingest(run_id=None):
        calls["yf"] += 1

    monkeypatch.setattr("src.ingest.ingest_ib.try_ingest_ib", fake_try_ingest_ib)
    monkeypatch.setattr("src.ingest.ingest_yfinance.run_ingest", fake_yf_ingest)

    run_ingest(run_id=7)

    assert calls["ib"] == 1
    assert calls["yf"] == 1


def test_real_ingest_signatures_accept_run_id() -> None:
    from src.ingest.ingest_ib import try_ingest_ib
    from src.ingest.ingest_yfinance import run_ingest as yf_run_ingest

    ib_sig = inspect.signature(try_ingest_ib)
    yf_sig = inspect.signature(yf_run_ingest)

    assert "run_id" in ib_sig.parameters
    assert "run_id" in yf_sig.parameters
