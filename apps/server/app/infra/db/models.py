"""SQLAlchemy ORM models. PostgreSQL 16 is the single relational store on every platform.

Conventions: string primary keys with type prefixes (usr_, pf_, run_), timestamps stored
as timezone-aware UTC, money as NUMERIC, every user-owned row carries user_id for
query-level authorization scoping.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.providers.embeddings.voyage import EMBEDDING_DIMS


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
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    automation_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    trading_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class RefreshTokenRow(Base):
    """One row per issued refresh token. Rotation replaces a row and links the successor;
    presenting an already-rotated token triggers reuse detection and revokes the family."""

    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    family_id: Mapped[str] = mapped_column(String(64), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    replaced_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditLogRow(Base):
    """Append-only audit trail. Money-path and auth actions always land here."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    detail: Mapped[dict[str, Any]] = mapped_column(JSONB)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class OrderIntentRow(Base):
    """Trade intent state machine. Every order, paper or live, is an intent first."""

    __tablename__ = "order_intents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    portfolio_id: Mapped[str] = mapped_column(String(64), index=True)
    symbol: Mapped[str] = mapped_column(String(32))
    side: Mapped[str] = mapped_column(String(4))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    order_type: Mapped[str] = mapped_column(String(8))
    limit_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 4), nullable=True)
    mode: Mapped[str] = mapped_column(String(8))
    status: Mapped[str] = mapped_column(String(16), index=True)
    source: Mapped[str] = mapped_column(String(16), default="manual")
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    broker_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fill_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 4), nullable=True)
    notional_inr: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AutomationRuleRow(Base):
    __tablename__ = "automation_rules"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    portfolio_id: Mapped[str] = mapped_column(String(64))
    trigger: Mapped[dict[str, Any]] = mapped_column(JSONB)
    action: Mapped[dict[str, Any]] = mapped_column(JSONB)
    max_notional_inr: Mapped[float] = mapped_column(Float)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=3600)
    executions_today: Mapped[int] = mapped_column(Integer, default=0)
    day_notional_inr: Mapped[float] = mapped_column(Float, default=0.0)
    counter_date: Mapped[str] = mapped_column(String(10), default="")
    last_fired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AlertRow(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    kind: Mapped[str] = mapped_column(String(16), default="price")
    symbol: Mapped[str] = mapped_column(String(32))
    operator: Mapped[str] = mapped_column(String(8))
    threshold: Mapped[float] = mapped_column(Float)
    channel: Mapped[str] = mapped_column(String(16), default="whatsapp")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=3600)
    last_label: Mapped[str | None] = mapped_column(String(16), nullable=True)
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CatalogProductRow(Base):
    """Seedable Indian loan and insurance product catalog. Matching is deterministic."""

    __tablename__ = "catalog_products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(16), index=True)
    provider: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(255))
    attributes: Mapped[dict[str, Any]] = mapped_column(JSONB)
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class DocumentRow(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(64))
    location: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IncomeProfileRow(Base):
    """One income record per user: the salary structure that feeds the tax engine."""

    __tablename__ = "income_profiles"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    basic_salary: Mapped[float] = mapped_column(Float, default=0.0)
    hra_received: Mapped[float] = mapped_column(Float, default=0.0)
    special_allowance: Mapped[float] = mapped_column(Float, default=0.0)
    other_income: Mapped[float] = mapped_column(Float, default=0.0)
    rent_paid: Mapped[float] = mapped_column(Float, default=0.0)
    metro: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CashAccountRow(Base):
    __tablename__ = "cash_accounts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    institution: Mapped[str] = mapped_column(String(128))
    balance_inr: Mapped[float] = mapped_column(Float, default=0.0)
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class DepositRow(Base):
    """Fixed and recurring deposits."""

    __tablename__ = "deposits"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(8))
    institution: Mapped[str] = mapped_column(String(128))
    principal_inr: Mapped[float] = mapped_column(Float)
    rate: Mapped[float] = mapped_column(Float)
    maturity_date: Mapped[str] = mapped_column(String(10))
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class RetirementAccountRow(Base):
    """EPF, PPF, and NPS balances with annual contributions (80C / 80CCD inputs)."""

    __tablename__ = "retirement_accounts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(8))
    balance_inr: Mapped[float] = mapped_column(Float, default=0.0)
    annual_contribution_inr: Mapped[float] = mapped_column(Float, default=0.0)
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class MfFolioRow(Base):
    __tablename__ = "mf_folios"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    scheme_code: Mapped[str] = mapped_column(String(16))
    scheme_name: Mapped[str] = mapped_column(String(255))
    units: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    sip_amount_inr: Mapped[float] = mapped_column(Float, default=0.0)
    sip_day: Mapped[int] = mapped_column(Integer, default=0)
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class DebtRow(Base):
    __tablename__ = "debts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    loan_type: Mapped[str] = mapped_column(String(16))
    lender: Mapped[str] = mapped_column(String(128))
    principal_outstanding_inr: Mapped[float] = mapped_column(Float)
    rate: Mapped[float] = mapped_column(Float)
    emi_inr: Mapped[float] = mapped_column(Float)
    tenure_months: Mapped[int] = mapped_column(Integer)
    annual_interest_inr: Mapped[float] = mapped_column(Float, default=0.0)
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class InsurancePolicyRow(Base):
    __tablename__ = "insurance_policies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    policy_type: Mapped[str] = mapped_column(String(16))
    provider: Mapped[str] = mapped_column(String(128))
    cover_inr: Mapped[float] = mapped_column(Float)
    annual_premium_inr: Mapped[float] = mapped_column(Float)
    term_years: Mapped[int] = mapped_column(Integer, default=0)
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class ExpenseRow(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(64))
    monthly_inr: Mapped[float] = mapped_column(Float)
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class GoalRow(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    target_inr: Mapped[float] = mapped_column(Float)
    target_date: Mapped[str] = mapped_column(String(10))
    priority: Mapped[str] = mapped_column(String(8), default="medium")
    saved_inr: Mapped[float] = mapped_column(Float, default=0.0)
    seed: Mapped[bool] = mapped_column(Boolean, default=False)


class DocumentChunkRow(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMS))


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
Index("ix_intents_user_status", OrderIntentRow.user_id, OrderIntentRow.status)
Index("ix_chunks_user_doc", DocumentChunkRow.user_id, DocumentChunkRow.document_id)
