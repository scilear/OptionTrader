from src.core.iv_solve import strike_from_delta


def test_strike_from_delta_returns_value():
    strike = strike_from_delta(
        spot=100,
        rate=0.0,
        div=0.0,
        t_years=30 / 365,
        vol=0.2,
        target_delta=0.25,
        right="C",
    )
    assert strike is not None
