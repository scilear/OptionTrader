from __future__ import annotations

import logging

from src.core.config import load_config


def run_ingest(run_id: int | None = None) -> None:
    """
    Ingest option chain data using the configured source with automatic fallback.

    Resolution order:
      1. IB TWS/Gateway — try each host in ``config.ib.hosts`` in sequence.
      2. yfinance — used when all IB hosts are unreachable or fail.
    """
    logger = logging.getLogger("ingest")
    config = load_config()
    source = str(config["data"].get("source", "ib")).lower()

    if source == "yfinance":
        logger.info("data.source=yfinance; skipping IB and ingesting yfinance directly")
        from src.ingest.ingest_yfinance import run_ingest as _yf_ingest

        _yf_ingest(run_id=run_id)
        return

    from src.ingest.ingest_ib import try_ingest_ib

    if try_ingest_ib(config, run_id=run_id):
        return

    logger.info("IB unavailable — falling back to yfinance")
    from src.ingest.ingest_yfinance import run_ingest as _yf_ingest

    _yf_ingest(run_id=run_id)
