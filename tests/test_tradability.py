import pandas as pd

from src.core.tradability import compute_tradability_score


def test_tradability_score_empty():
    score = compute_tradability_score(pd.DataFrame(), 0.15)
    assert score == 0.0


def test_tradability_score_reasonable():
    quotes = pd.DataFrame(
        {
            "bid": [1.0, 2.0, 1.5],
            "ask": [1.1, 2.2, 1.65],
        }
    )
    score = compute_tradability_score(quotes, 0.15)
    assert 0.0 <= score <= 1.0
