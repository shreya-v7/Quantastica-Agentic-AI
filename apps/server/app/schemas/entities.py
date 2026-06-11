from app.schemas.base import Contract
from app.schemas.common import AssetClass, TransactionType


class Holding(Contract):
    id: str
    portfolio_id: str
    symbol: str
    name: str
    asset_class: AssetClass
    sector: str
    quantity: float
    cost_basis: float
    current_price: float
    seed: bool = False


class Transaction(Contract):
    id: str
    portfolio_id: str
    symbol: str
    type: TransactionType
    quantity: float
    price: float
    timestamp: str
    seed: bool = False


class Portfolio(Contract):
    id: str
    name: str
    base_currency: str
    created_at: str
    seed: bool = False


class AllocationSlice(Contract):
    key: str
    value: float
    weight: float


class PositionMetric(Contract):
    symbol: str
    name: str
    value: float
    weight: float
    cost_basis: float
    unrealized_gain: float
    unrealized_gain_pct: float


class PortfolioMetrics(Contract):
    portfolio_id: str
    total_value: float
    total_cost_basis: float
    unrealized_gain: float
    unrealized_gain_pct: float
    positions: list[PositionMetric]
    sector_allocation: list[AllocationSlice]
    asset_class_allocation: list[AllocationSlice]
    top_positions: list[PositionMetric]


class PortfolioDetail(Contract):
    portfolio: Portfolio
    holdings: list[Holding]
    metrics: PortfolioMetrics
