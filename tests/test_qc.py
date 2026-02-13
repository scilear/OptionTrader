from src.core.qc import evaluate_quote


def test_crossed_quote_invalid():
    valid, flags = evaluate_quote(bid=2.0, ask=1.0, allow_zero_bid=False, spread_gate_pct=0.15)
    assert not valid
    assert flags.get("crossed") is True


def test_zero_bid_invalid_when_disallowed():
    valid, flags = evaluate_quote(bid=0.0, ask=1.0, allow_zero_bid=False, spread_gate_pct=0.15)
    assert not valid
    assert flags.get("zero_bid") is True


def test_wide_spread_flagged_but_valid():
    valid, flags = evaluate_quote(bid=1.0, ask=2.0, allow_zero_bid=False, spread_gate_pct=0.15)
    assert valid
    assert flags.get("wide_spread") is True
