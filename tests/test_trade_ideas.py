from src.core.trade_ideas import build_trade_ideas, IdeaContext


def test_trade_ideas_rr_extreme():
    ctx = IdeaContext(spot=100, t_years=30/365, rate=0.0, div=0.0, iv_mid={}, iv_bid={}, iv_ask={})
    ideas = build_trade_ideas("RR_EXTREME", "30D", ctx)
    assert ideas
    assert ideas[0]["template"] == "SkewFade_PutSpread"


def test_trade_ideas_fly_extreme():
    ctx = IdeaContext(spot=100, t_years=30/365, rate=0.0, div=0.0, iv_mid={}, iv_bid={}, iv_ask={})
    ideas = build_trade_ideas("FLY_EXTREME", "30D", ctx)
    assert ideas
    assert ideas[0]["template"] == "Fly_1x2x1"


def test_trade_ideas_term_kink():
    ctx = IdeaContext(spot=100, t_years=30/365, rate=0.0, div=0.0, iv_mid={}, iv_bid={}, iv_ask={})
    ideas = build_trade_ideas("TERM_KINK", "30D", ctx)
    assert ideas
    assert ideas[0]["template"] == "ATM_Calendar"
