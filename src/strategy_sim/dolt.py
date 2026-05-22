from __future__ import annotations

from io import StringIO
from pathlib import Path
import subprocess

import pandas as pd


def run_dolt_query(repo_path: str | Path, query: str) -> pd.DataFrame:
    """Execute a Dolt SQL query and return a dataframe."""
    result = subprocess.run(
        ["dolt", "sql", "-r", "csv", "-q", query],
        cwd=str(Path(repo_path)),
        check=True,
        capture_output=True,
        text=True,
    )
    csv_payload = result.stdout.strip()
    if not csv_payload:
        return pd.DataFrame()
    return pd.read_csv(StringIO(csv_payload))


def execute_dolt_statement(repo_path: str | Path, statement: str) -> None:
    """Execute a Dolt SQL statement that does not return rows."""
    subprocess.run(
        ["dolt", "sql", "-q", statement],
        cwd=str(Path(repo_path)),
        check=True,
        capture_output=True,
        text=True,
    )
