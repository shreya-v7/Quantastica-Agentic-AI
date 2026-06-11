"""SQLAlchemy ORM models. PostgreSQL 16 is the single relational store on every platform.

Conventions: string primary keys with type prefixes (usr_, pf_, run_), timestamps stored
as timezone-aware UTC, money as NUMERIC, every user-owned row carries user_id for
query-level authorization scoping.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSONB,
        list[str]: JSONB,
    }


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String(16), default="user")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    totp_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    automation_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    trading_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class PortfolioRow(Base):
    __tablename__ = "portfolios"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    base_currency: Mapped[str] = mapped_column(String(8), default="INR")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class HoldingRow(Base):
    __tablename__ = "holdings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), index=True
    )
    symbol: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(255))
    asset_class: Mapped[str] = mapped_column(String(16))
    sector: Mapped[str] = mapped_column(String(64))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    cost_basis: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    current_price: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class TransactionRow(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), index=True
    )
    symbol: Mapped[str] = mapped_column(String(32))
    type: Mapped[str] = mapped_column(String(8))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    timestamp: Mapped[str] = mapped_column(String(40))
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class FindingRow(Base):
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    portfolio_id: Mapped[str] = mapped_column(String(64), index=True)
    run_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(8), index=True)
    confidence: Mapped[float] = mapped_column()
    metric_ids: Mapped[list[str]] = mapped_column(JSONB)
    created_at: Mapped[str] = mapped_column(String(40))
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class AgentRunRow(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    portfolio_id: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[str] = mapped_column(String(40))
    data: Mapped[dict[str, Any]] = mapped_column(JSONB)


Index("ix_findings_user_portfolio", FindingRow.user_id, FindingRow.portfolio_id)
Index("ix_runs_user_portfolio", AgentRunRow.user_id, AgentRunRow.portfolio_id)
