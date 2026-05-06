import json

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


def test_trade_idea_rejects_incomplete_edge_components():
    ctx = IdeaContext(
        spot=100,
        t_years=30 / 365,
        rate=0.0,
        div=0.0,
        iv_mid={0.25: 0.2, -0.25: 0.22, 0.10: 0.24, -0.10: 0.25},
        iv_bid={0.25: 0.19, -0.25: 0.21, 0.10: 0.23, -0.10: 0.24},
        iv_ask={0.25: 0.21, -0.25: 0.23, 0.10: 0.25, -0.10: 0.26},
    )
    idea = build_trade_ideas("RR_EXTREME", "30D", ctx)[0]
    ranking = json.loads(idea["scenarios"])["ranking"]
    assert ranking["promote_eligible"] is False
    assert "incomplete_edge_components" in ranking["blocked_reasons"]


def test_trade_idea_payload_complete_when_context_has_edge_components():
    ctx = IdeaContext(
        spot=100,
        t_years=30 / 365,
        rate=0.0,
        div=0.0,
        iv_mid={0.25: 0.2, -0.25: 0.22, 0.10: 0.24, -0.10: 0.25},
        iv_bid={0.25: 0.19, -0.25: 0.21, 0.10: 0.23, -0.10: 0.24},
        iv_ask={0.25: 0.21, -0.25: 0.23, 0.10: 0.25, -0.10: 0.26},
        alert_severity=2.3,
        alert_zscore_mid=2.4,
        tradability_score=0.8,
    )
    idea = build_trade_ideas("RR_EXTREME", "30D", ctx)[0]
    ranking = json.loads(idea["scenarios"])["ranking"]
    assert ranking["normalized_edge_components"]["severity"] is not None
    assert ranking["normalized_edge_components"]["zscore"] is not None
    assert ranking["normalized_edge_components"]["tradability"] is not None
    assert ranking["normalized_edge_components"]["pricing_spread"] is not None


def test_compute_snapshot_iv_lookup_parses_dynamic_delta_buckets() -> None:
    from datetime import date

    from src.core.compute_snapshot import _build_iv_lookup
    from src.core.metrics import IvPoint

    points = [
        IvPoint(date(2026, 3, 15), "ATM", 0.2, 0.19, 0.21, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "+0.30C", 0.24, 0.23, 0.25, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "-0.05P", 0.27, 0.26, 0.28, "ok", 1.0),
    ]

    iv_mid, iv_bid, iv_ask = _build_iv_lookup(points, target_expiry=date(2026, 3, 15))

    assert iv_mid[0.5] == 0.2
    assert iv_mid[-0.5] == 0.2
    assert iv_mid[0.3] == 0.24
    assert iv_mid[-0.05] == 0.27
    assert iv_bid[0.3] == 0.23
    assert iv_ask[-0.05] == 0.28
