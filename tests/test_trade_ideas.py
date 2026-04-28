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


def test_trade_ideas_structure_config_changes_legs():
    config = {
        "structures": {
            "skew_fade": {"short_put_delta": -0.30, "long_put_delta": -0.05},
            "fly": {"wing_delta": 0.30},
            "calendar": {
                "front_dte_min": 10,
                "front_dte_max": 20,
                "back_dte_min": 40,
                "back_dte_max": 70,
            },
        }
    }
    ctx = IdeaContext(
        spot=100,
        t_years=30 / 365,
        rate=0.0,
        div=0.0,
        iv_mid={},
        iv_bid={},
        iv_ask={},
        config=config,
    )

    rr = build_trade_ideas("RR_EXTREME", "30D", ctx)[0]
    fly = build_trade_ideas("FLY_EXTREME", "30D", ctx)[0]
    cal = build_trade_ideas("TERM_KINK", "30D", ctx)[0]

    assert '"delta": -0.3' in rr["legs"]
    assert '"delta": -0.05' in rr["legs"]
    assert '"delta": -0.3' in fly["legs"]
    assert '"dte_min": 10' in cal["legs"]
    assert '"dte_max": 70' in cal["legs"]
