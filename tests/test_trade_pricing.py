from src.core.trade_ideas import build_trade_ideas, IdeaContext


def test_trade_idea_pricing_populates():
    ctx = IdeaContext(
        spot=100,
        t_years=30 / 365,
        rate=0.0,
        div=0.0,
        iv_mid={0.25: 0.2, -0.25: 0.22, 0.10: 0.24, -0.10: 0.25},
        iv_bid={0.25: 0.19, -0.25: 0.21, 0.10: 0.23, -0.10: 0.24},
        iv_ask={0.25: 0.21, -0.25: 0.23, 0.10: 0.25, -0.10: 0.26},
    )
    ideas = build_trade_ideas("RR_EXTREME", "30D", ctx)
    assert ideas[0]["price_mid"] is not None
    assert ideas[0]["price_worst"] is not None
