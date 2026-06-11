from app.agents.researcher import compute_metrics
from app.schemas.common import AssetClass
from app.schemas.entities import Holding


def _holding(symbol, qty, price, cost, sector="Technology", asset=AssetClass.equity):
    return Holding(
        id=f"h_{symbol}",
        portfolio_id="pf",
        symbol=symbol,
        name=symbol,
        asset_class=asset,
        sector=sector,
        quantity=qty,
        cost_basis=cost,
        current_price=price,
        seed=False,
    )


def test_compute_metrics_known_values():
    holdings = [
        _holding("AAA", 10, 100, 80),
        _holding("BBB", 5, 200, 210, sector="Energy"),
    ]
    metrics = compute_metrics("pf", holdings)

    assert metrics.total_value == 2000.0
    assert metrics.total_cost_basis == 1850.0
    assert metrics.unrealized_gain == 150.0
    assert {p.symbol: p.weight for p in metrics.positions} == {"AAA": 0.5, "BBB": 0.5}

    aaa = next(p for p in metrics.positions if p.symbol == "AAA")
    assert aaa.unrealized_gain == 200.0
    assert aaa.unrealized_gain_pct == 0.25

    sectors = {s.key: s.weight for s in metrics.sector_allocation}
    assert sectors == {"Technology": 0.5, "Energy": 0.5}


def test_top_positions_capped_at_five():
    holdings = [_holding(f"S{i}", 1, 10 * (i + 1), 5) for i in range(8)]
    metrics = compute_metrics("pf", holdings)
    assert len(metrics.top_positions) == 5
    values = [p.value for p in metrics.top_positions]
    assert values == sorted(values, reverse=True)


def test_empty_total_value_yields_zero_weights():
    metrics = compute_metrics("pf", [_holding("ZZZ", 0, 0, 0)])
    assert metrics.total_value == 0.0
    assert metrics.positions[0].weight == 0.0
