from __future__ import annotations

from pathlib import Path

import duckdb
import yaml

from scripts.ingest_spx_eod_option_data import ingest_spx_eod_option_data
from scripts.validate_spx_eod_dataset import validate_eod_dataset


def _make_test_config(base_path: Path, db_path: Path) -> Path:
    config = yaml.safe_load(base_path.read_text())
    config["storage"]["path"] = str(db_path)
    config_path = db_path.parent / "config-eod-test.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return config_path


def _write_sample_file(root: Path, name: str) -> Path:
    payload = "\n".join(
        [
            "[QUOTE_UNIXTIME], [QUOTE_READTIME], [QUOTE_DATE], [QUOTE_TIME_HOURS], [UNDERLYING_LAST], [EXPIRE_DATE], [EXPIRE_UNIX], [DTE], [C_DELTA], [C_GAMMA], [C_VEGA], [C_THETA], [C_RHO], [C_IV], [C_VOLUME], [C_LAST], [C_SIZE], [C_BID], [C_ASK], [STRIKE], [P_BID], [P_ASK], [P_SIZE], [P_LAST], [P_DELTA], [P_GAMMA], [P_VEGA], [P_THETA], [P_RHO], [P_IV], [P_VOLUME], [STRIKE_DISTANCE], [STRIKE_DISTANCE_PCT]",
            "1701464400, 2023-12-01 16:00, 2023-12-01, 16.0, 4593.68, 2024-01-19, 1705622400, 49, 0,0,0,0,0,0.2,10,100,12 x 14,1.20,1.30,4500,1.10,1.25,7 x 8,95,0,0,0,0,0,0.2,9,0,0",
            "1701464400, 2023-12-01 16:00, 2023-12-01, 16.0, 4593.68, 2024-01-19, 1705622400, 49, 0,0,0,0,0,0.2,10,100,12 x 14,1.30,1.20,4600,1.10,1.25,7 x 8,95,0,0,0,0,0,0.2,9,0,0",
            "1701550800, 2023-12-02 16:00, 2023-12-02, 16.0, 4601.15, 2024-01-19, 1705622400, 48, 0,0,0,0,0,0.2,10,100,12 x 14,1.10,1.20,4525,1.00,1.15,7 x 8,95,0,0,0,0,0,0.2,9,0,0",
        ]
    )
    path = root / name
    path.write_text(payload + "\n", encoding="utf-8")
    return path


def test_eod_ingest_idempotent_and_validation_passes(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    _write_sample_file(input_dir, "spx_eod_202312.txt")

    db_path = tmp_path / "eod.duckdb"
    config_path = _make_test_config(Path("config/config-test.yaml"), db_path)
    monkeypatch.setenv("OPTIONTRADER_CONFIG", str(config_path))

    first = ingest_spx_eod_option_data(
        input_dir=input_dir,
        glob_pattern="spx_eod_*.txt",
        underlying="SPX",
    )
    second = ingest_spx_eod_option_data(
        input_dir=input_dir,
        glob_pattern="spx_eod_*.txt",
        underlying="SPX",
    )

    assert first.snapshots_inserted == 2
    assert first.quotes_inserted == 5
    assert first.quotes_rejected == 1

    assert second.snapshots_inserted == 0
    assert second.snapshots_reused == 3
    assert second.quotes_inserted == 5
    assert second.quotes_rejected == 1

    conn = duckdb.connect(str(db_path))
    try:
        snapshot_count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
        quote_count = conn.execute("SELECT COUNT(*) FROM option_quotes").fetchone()[0]
    finally:
        conn.close()

    assert snapshot_count == 2
    assert quote_count == 5

    result = validate_eod_dataset(db_path)
    assert result["hard_pass"] is True
