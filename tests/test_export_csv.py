import pandas as pd

from src.core.export import export_df_to_csv


def test_export_df_to_csv():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    csv = export_df_to_csv(df)
    assert "a,b" in csv
