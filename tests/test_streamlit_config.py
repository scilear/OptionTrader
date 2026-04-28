from __future__ import annotations

from pathlib import Path

import yaml


def test_metric_bucket_options_are_config_driven() -> None:
    config = yaml.safe_load(Path("config/config-test.yaml").read_text())
    expected = [f"{int(b)}D" for b in config["metrics"]["expiry_buckets_days"]]

    source = Path("src/app/streamlit_app.py").read_text()

    assert 'config = load_config()' in source
    assert 'bucket_values = [f"{int(b)}D" for b in config["metrics"]["expiry_buckets_days"]]' in source
    assert 'bucket = st.selectbox("Expiry bucket", bucket_values)' in source
    assert expected
