"""Order-intent persistence plus the holding/transaction effects of a fill.

A fill is applied in one transaction: the intent flips to filled, a transaction row is
written, and the holding position is upserted (weighted-average cost on buys, quantity
reduction on sells). User scoping is enforced on every query.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.ids import new_id, now_iso
from app.infra.db.models import HoldingRow, OrderIntentRow, TransactionRow
from app.schemas.common import OrderSide, OrderStatus, OrderType, TradingMode
from app.schemas.trade import CreateOrderIntent, OrderIntent

_ACTIVE = (OrderStatus.pending_approval.value, OrderStatus.approved.value,
           OrderStatus.submitted.value)


class TradeRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sessions = session_factory

    async def create(
        self, user_id: str, req: CreateOrderIntent, mode: str, notional: float, source: str
    ) -> OrderIntent:
        now = datetime.now(UTC)
        row = OrderIntentRow(
            id=new_id("oi"),
            user_id=user_id,
            portfolio_id=req.portfolio_id,
            symbol=req.symbol,
            side=req.side.value,
            quantity=Decimal(str(req.quantity)),
            order_type=req.order_type.value,
            limit_price=Decimal(str(req.limit_price)) if req.limit_price else None,
            mode=mode,
            status=OrderStatus.pending_approval.value,
            source=source,
            notional_inr=notional,
            created_at=now,
            updated_at=now,
        )
        async with self._sessions() as session:
            session.add(row)
            await session.commit()
            await session.refresh(row)
        return self._intent(row)

    async def get(self, user_id: str, intent_id: str) -> OrderIntentRow | None:
        async with self._sessions() as session:
            return await session.scalar(
                select(OrderIntentRow).where(
                    OrderIntentRow.user_id == user_id, OrderIntentRow.id == intent_id
                )
            )

    async def list(self, user_id: str) -> list[OrderIntent]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(OrderIntentRow)
                    .where(OrderIntentRow.user_id == user_id)
                    .order_by(OrderIntentRow.created_at.desc())
                )
            ).all()
        return [self._intent(r) for r in rows]

    async def count_open(self, user_id: str) -> int:
        async with self._sessions() as session:
            return int(
                await session.scalar(
                    select(func.count(OrderIntentRow.id)).where(
                        OrderIntentRow.user_id == user_id,
                        OrderIntentRow.status.in_(_ACTIVE),
                    )
                )
                or 0
            )

    async def filled_notional_today(self, user_id: str) -> float:
        start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        async with self._sessions() as session:
            return float(
                await session.scalar(
                    select(func.coalesce(func.sum(OrderIntentRow.notional_inr), 0.0)).where(
                        OrderIntentRow.user_id == user_id,
                        OrderIntentRow.status == OrderStatus.filled.value,
                        OrderIntentRow.updated_at >= start,
                    )
                )
                or 0.0
            )

    async def set_status(
        self,
        user_id: str,
        intent_id: str,
        status: OrderStatus,
        reason: str | None = None,
        broker_order_id: str | None = None,
    ) -> None:
        async with self._sessions() as session:
            row = await session.get(OrderIntentRow, intent_id)
            if row is None or row.user_id != user_id:
                return
            row.status = status.value
            row.reason = reason
            if broker_order_id:
                row.broker_order_id = broker_order_id
            row.updated_at = datetime.now(UTC)
            await session.commit()

    async def apply_fill(
        self, user_id: str, intent_id: str, fill_price: float, broker_order_id: str
    ) -> OrderIntent:
        """Flip to filled and apply the position change atomically."""
        async with self._sessions() as session:
            row = await session.get(OrderIntentRow, intent_id)
            if row is None or row.user_id != user_id:
                raise ValueError("intent not found")
            row.status = OrderStatus.filled.value
            row.fill_price = Decimal(str(fill_price))
            row.broker_order_id = broker_order_id
            row.notional_inr = float(row.quantity) * fill_price
            row.updated_at = datetime.now(UTC)

            session.add(
                TransactionRow(
                    id=new_id("tx"),
                    user_id=user_id,
                    portfolio_id=row.portfolio_id,
                    symbol=row.symbol,
                    type=row.side,
                    quantity=row.quantity,
                    price=Decimal(str(fill_price)),
                    timestamp=now_iso(),
                    seed=False,
                )
            )
            await self._apply_position(session, user_id, row, fill_price)
            await session.commit()
            await session.refresh(row)
        return self._intent(row)

    async def _apply_position(
        self, session: AsyncSession, user_id: str, intent: OrderIntentRow, price: float
    ) -> None:
        holding = await session.scalar(
            select(HoldingRow).where(
                HoldingRow.user_id == user_id,
                HoldingRow.portfolio_id == intent.portfolio_id,
                HoldingRow.symbol == intent.symbol,
            )
        )
        qty = float(intent.quantity)
        if intent.side == OrderSide.buy.value:
            if holding is None:
                session.add(
                    HoldingRow(
                        id=new_id("h"),
                        user_id=user_id,
                        portfolio_id=intent.portfolio_id,
                        symbol=intent.symbol,
                        name=intent.symbol.split(".")[0],
                        asset_class="equity",
                        sector="Unknown",
                        quantity=Decimal(str(qty)),
                        cost_basis=Decimal(str(price)),
                        current_price=Decimal(str(price)),
                        seed=False,
                    )
                )
            else:
                old_qty = float(holding.quantity)
                old_cost = float(holding.cost_basis)
                new_qty = old_qty + qty
                holding.cost_basis = Decimal(
                    str((old_qty * old_cost + qty * price) / new_qty)
                )
                holding.quantity = Decimal(str(new_qty))
                holding.current_price = Decimal(str(price))
        else:
            if holding is not None:
                holding.quantity = Decimal(str(max(0.0, float(holding.quantity) - qty)))
                holding.current_price = Decimal(str(price))

    @staticmethod
    def _intent(row: OrderIntentRow) -> OrderIntent:
        return OrderIntent(
            id=row.id,
            portfolio_id=row.portfolio_id,
            symbol=row.symbol,
            side=OrderSide(row.side),
            quantity=float(row.quantity),
            order_type=OrderType(row.order_type),
            limit_price=float(row.limit_price) if row.limit_price is not None else None,
            mode=TradingMode(row.mode),
            status=OrderStatus(row.status),
            source=row.source,
            reason=row.reason,
            broker_order_id=row.broker_order_id,
            fill_price=float(row.fill_price) if row.fill_price is not None else None,
            notional_inr=float(row.notional_inr),
            created_at=row.created_at.isoformat(),
            updated_at=row.updated_at.isoformat(),
        )
