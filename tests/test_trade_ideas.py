from src.core.trade_ideas import build_trade_ideas


def test_trade_ideas_rr_extreme():
    ideas = build_trade_ideas("RR_EXTREME", "30D")
    assert ideas
    assert ideas[0]["template"] == "SkewFade_PutSpread"


def test_trade_ideas_fly_extreme():
    ideas = build_trade_ideas("FLY_EXTREME", "30D")
    assert ideas
    assert ideas[0]["template"] == "Fly_1x2x1"


def test_trade_ideas_term_kink():
    ideas = build_trade_ideas("TERM_KINK", "30D")
    assert ideas
    assert ideas[0]["template"] == "ATM_Calendar"
