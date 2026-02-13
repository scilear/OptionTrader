import math

from src.core.iv_solve import _bs_price, solve_iv


def test_solve_iv_recovers_vol():
    spot = 100.0
    strike = 100.0
    rate = 0.0
    div = 0.0
    t = 30 / 365
    vol = 0.2
    price = _bs_price(spot, strike, rate, div, t, vol, "C")
    result = solve_iv(price, spot, strike, rate, div, t, "C")
    assert result.iv is not None
    assert math.isclose(result.iv, vol, rel_tol=1e-2)


def test_solve_iv_out_of_bounds():
    result = solve_iv(0.0001, 100.0, 100.0, 0.0, 0.0, 30 / 365, "C")
    assert result.iv is None
