import json

from src.core.trade_ideas import build_trade_ideas, IdeaContext
from src.core.tradability import build_size_sensitivity, compute_friction_costs


def _context(config=None):
    return IdeaContext(
        spot=100,
        t_years=30 / 365,
        rate=0.0,
        div=0.0,
        iv_mid={
            0.5: 0.21,
            -0.5: 0.21,
            0.25: 0.2,
            -0.25: 0.22,
            0.10: 0.24,
            -0.10: 0.25,
            -0.125: 0.235,
        },
        iv_bid={
            0.5: 0.20,
            -0.5: 0.20,
            0.25: 0.19,
            -0.25: 0.21,
            0.10: 0.23,
            -0.10: 0.24,
            -0.125: 0.225,
        },
        iv_ask={
            0.5: 0.22,
            -0.5: 0.22,
            0.25: 0.21,
            -0.25: 0.23,
            0.10: 0.25,
            -0.10: 0.26,
            -0.125: 0.245,
        },
        alert_severity=2.5,
        alert_zscore_mid=2.6,
        tradability_score=0.8,
        config=config,
    )


def test_trade_idea_pricing_populates():
    ctx = _context()
    ideas = build_trade_ideas("RR_EXTREME", "30D", ctx)
    assert ideas[0]["price_mid"] is not None
    assert ideas[0]["price_worst"] is not None


def test_friction_cost_curve_monotonic_with_size():
    points = build_size_sensitivity(
        edge_before_cost=120.0,
        gross_premium_notional=200.0,
        net_gamma=0.02,
        spot=100.0,
        transaction_cost_bps=5.0,
        impact_cost_bps=3.0,
        impact_exponent=1.35,
        hedge_turnover_bps=2.0,
        include_hedge_path=True,
        size_tiers=[1.0, 2.0, 4.0],
    )
    costs = [point["total_friction_cost"] for point in points]
    edges = [point["edge_after_cost"] for point in points]
    assert costs[0] <= costs[1] <= costs[2]
    assert edges[0] >= edges[1] >= edges[2]


def test_trade_idea_emits_cost_decomposition_payload():
    ctx = _context()
    idea = build_trade_ideas("RR_EXTREME", "30D", ctx)[0]
    scenarios = json.loads(idea["scenarios"])
    ranking = scenarios["ranking"]
    assert ranking["edge_before_cost"] >= 0.0
    assert ranking["total_friction_cost"] >= 0.0
    assert isinstance(ranking["size_sensitivity"], list)
    assert ranking["size_sensitivity"]
    assert ranking["blocked_reason"] is None
    assert ranking["promote_eligible"] is True


def test_trade_idea_blocks_when_edge_after_cost_non_positive():
    expensive_config = {
        "structures": {
            "execution_costs": {
                "transaction_cost_bps": 5000.0,
                "impact_cost_bps": 5000.0,
                "impact_exponent": 2.0,
                "hedge_turnover_bps": 2000.0,
                "size_tiers": [1.0, 2.0, 4.0],
            }
        }
    }
    ctx = _context(config=expensive_config)
    idea = build_trade_ideas("TERM_KINK", "30D", ctx)[0]
    scenarios = json.loads(idea["scenarios"])
    ranking = scenarios["ranking"]
    assert ranking["promote_eligible"] is False
    assert ranking["blocked_reason"] == "non_positive_edge_after_cost"
    assert "non_positive_edge_after_cost" in ranking["blocked_reasons"]
    flags = json.loads(idea["risk_flags"])
    assert "hedge_path_estimated" in flags


def test_compute_friction_costs_uses_nonnegative_inputs():
    cost = compute_friction_costs(
        edge_before_cost=-1.0,
        gross_premium_notional=-5.0,
        net_gamma=-0.2,
        spot=-100.0,
        size=-2.0,
        transaction_cost_bps=5.0,
        impact_cost_bps=3.0,
        impact_exponent=1.35,
        hedge_turnover_bps=2.0,
        include_hedge_path=True,
    )
    assert cost.edge_before_cost == 0.0
    assert cost.total_friction_cost == 0.0
