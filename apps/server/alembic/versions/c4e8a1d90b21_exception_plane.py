"""exception control plane tables

Revision ID: c4e8a1d90b21
Revises: b2f8bf9660bd
Create Date: 2026-09-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "c4e8a1d90b21"
down_revision = "b2f8bf9660bd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "firms",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("name_cap", sa.Float(), nullable=False, server_default="0.15"),
        sa.Column("sector_cap", sa.Float(), nullable=False, server_default="0.4"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "households",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("firm_id", sa.String(64), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("bank_customer_id", sa.String(64), nullable=True),
        sa.Column("as_of", sa.String(10), nullable=False),
        sa.Column("tax", postgresql.JSONB(), nullable=True),
        sa.Column("seed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_households_firm_id", "households", ["firm_id"])
    op.create_table(
        "lots",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("firm_id", sa.String(64), nullable=False),
        sa.Column("household_id", sa.String(64), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("asset_class", sa.String(16), nullable=False),
        sa.Column("sector", sa.String(64), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 6), nullable=False),
        sa.Column("cost", sa.Numeric(20, 4), nullable=False),
        sa.Column("price", sa.Numeric(20, 4), nullable=False),
        sa.Column("acquired_on", sa.String(10), nullable=False),
        sa.Column("fmv_2018", sa.Numeric(20, 4), nullable=True),
        sa.Column("seed", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_index("ix_lots_hh_symbol", "lots", ["household_id", "symbol"])
    op.create_table(
        "book_events",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("household_id", sa.String(64), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "outbox",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("aggregate_type", sa.String(32), nullable=False),
        sa.Column("aggregate_id", sa.String(64), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "processed_events",
        sa.Column("consumer", sa.String(64), primary_key=True),
        sa.Column("event_id", sa.String(64), primary_key=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "exceptions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("household_id", sa.String(64), nullable=False),
        sa.Column("rule_id", sa.String(64), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("rupee_delta", sa.Float(), nullable=False),
        sa.Column("due_date", sa.String(10), nullable=True),
        sa.Column("severity", sa.String(8), nullable=False),
        sa.Column("metric_ids", postgresql.JSONB(), nullable=False),
        sa.Column("fingerprint", sa.String(32), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="open"),
        sa.Column("calculator", sa.String(64), nullable=False),
        sa.Column("calculator_version", sa.String(32), nullable=False),
        sa.Column("inputs", postgresql.JSONB(), nullable=False),
        sa.Column("outputs", postgresql.JSONB(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_exceptions_hh_status", "exceptions", ["household_id", "status"])
    op.create_table(
        "exception_diffs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("household_id", sa.String(64), nullable=False),
        sa.Column("run_id", sa.String(64), nullable=False),
        sa.Column("added", postgresql.JSONB(), nullable=False),
        sa.Column("removed", postgresql.JSONB(), nullable=False),
        sa.Column("changed", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "calculator_runs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("household_id", sa.String(64), nullable=False),
        sa.Column("exception_id", sa.String(64), nullable=False),
        sa.Column("calculator", sa.String(64), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("inputs", postgresql.JSONB(), nullable=False),
        sa.Column("outputs", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("calculator_runs")
    op.drop_table("exception_diffs")
    op.drop_table("exceptions")
    op.drop_table("processed_events")
    op.drop_table("outbox")
    op.drop_table("book_events")
    op.drop_table("lots")
    op.drop_table("households")
    op.drop_table("firms")
