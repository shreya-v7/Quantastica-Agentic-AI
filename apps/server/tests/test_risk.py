import pytest
from app.agents.risk import (
    compute_risk_metrics,
    herfindahl_index,
    top_n_share,
    volatility_proxy,
)
from app.schemas.common import Rating
from app.schemas.entities import AllocationSlice, PortfolioMetrics, PositionMetric, Transaction


def _metrics(weights, sector_max=0.0):
    positions = [
        PositionMetric(
            symbol=f"S{i}",
            name=f"S{i}",
            value=w * 1000,
            weight=w,
            cost_basis=0.0,
            unrealized_gain=0.0,
            unrealized_gain_pct=0.0,
        )
        for i, w in enumerate(weights)
    ]
    return PortfolioMetrics(
        portfolio_id="pf",
        total_value=1000.0,
        total_cost_basis=1000.0,
        unrealized_gain=0.0,
        unrealized_gain_pct=0.0,
        positions=positions,
        sector_allocation=[AllocationSlice(key="X", value=sector_max * 1000, weight=sector_max)],
        asset_class_allocation=[],
        top_positions=positions,
    )


def test_herfindahl_index():
    assert herfindahl_index([0.5, 0.5]) == pytest.approx(0.5)
    assert herfindahl_index([0.25, 0.25, 0.25, 0.25]) == pytest.approx(0.25)
    assert herfindahl_index([1.0]) == pytest.approx(1.0)


def test_top_n_share():
    assert top_n_share([0.5, 0.3, 0.1, 0.1], 2) == pytest.approx(0.8)
    assert top_n_share([0.2, 0.2], 5) == pytest.approx(0.4)


def test_volatility_proxy_known_returns():
    txs = [
        Transaction(id="t1", portfolio_id="pf", symbol="AAA", type="buy", quantity=1, price=100, timestamp="2024-01-01"),
        Transaction(id="t2", portfolio_id="pf", symbol="AAA", type="buy", quantity=1, price=110, timestamp="2024-02-01"),
        Transaction(id="t3", portfolio_id="pf", symbol="AAA", type="buy", quantity=1, price=99, timestamp="2024-03-01"),
    ]
    metrics = _metrics([1.0])
    metrics.positions[0].symbol = "AAA"
    # returns: +0.10 then -0.10, mean 0, population stdev 0.10
    assert volatility_proxy(metrics, txs) == pytest.approx(0.10, abs=1e-9)


def test_volatility_proxy_insufficient_history_is_zero():
    txs = [
        Transaction(id="t1", portfolio_id="pf", symbol="AAA", type="buy", quantity=1, price=100, timestamp="2024-01-01"),
    ]
    metrics = _metrics([1.0])
    metrics.positions[0].symbol = "AAA"
    assert volatility_proxy(metrics, txs) == 0.0


def test_compute_risk_metrics_ratings_concentrated():
    metrics = _metrics([0.6, 0.2, 0.1, 0.1], sector_max=0.7)
    result = {m.id: m for m in compute_risk_metrics(metrics, [])}

    assert result["hhi"].value == pytest.approx(0.42)
    assert result["hhi"].rating == Rating.high
    assert result["top5_weight"].value == pytest.approx(1.0)
    assert result["top5_weight"].rating == Rating.high
    assert result["sector_concentration"].rating == Rating.high
    assert result["diversification"].value == pytest.approx(0.58)
    assert result["diversification"].rating == Rating.high


def test_compute_risk_metrics_ratings_diversified():
    metrics = _metrics([0.1] * 10, sector_max=0.2)
    result = {m.id: m for m in compute_risk_metrics(metrics, [])}

    assert result["hhi"].value == pytest.approx(0.10)
    assert result["hhi"].rating == Rating.low
    assert result["diversification"].value == pytest.approx(0.90)
    assert result["diversification"].rating == Rating.low
    assert result["sector_concentration"].rating == Rating.low


def test_all_metric_ids_present():
    metrics = _metrics([0.5, 0.5], sector_max=0.5)
    ids = {m.id for m in compute_risk_metrics(metrics, [])}
    assert ids == {"hhi", "top5_weight", "sector_concentration", "diversification", "volatility"}
