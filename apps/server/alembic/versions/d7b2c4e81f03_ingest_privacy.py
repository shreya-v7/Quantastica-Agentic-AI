"""ingest artifacts, graph checkpoints, consents, firm members

Revision ID: d7b2c4e81f03
Revises: c4e8a1d90b21
Create Date: 2026-09-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "d7b2c4e81f03"
down_revision = "c4e8a1d90b21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingest_artifacts",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("household_id", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("sha256", sa.String(64), nullable=True),
        sa.Column("extracted", postgresql.JSONB(), nullable=True),
        sa.Column("missing_fields", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("thread_id", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ingest_artifacts_household_id", "ingest_artifacts", ["household_id"])
    op.create_index("ix_ingest_artifacts_status", "ingest_artifacts", ["status"])
    op.create_index("ix_ingest_artifacts_thread_id", "ingest_artifacts", ["thread_id"])
    op.create_table(
        "graph_checkpoints",
        sa.Column("thread_id", sa.String(128), primary_key=True),
        sa.Column("state", postgresql.JSONB(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "consents",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("household_id", sa.String(64), nullable=False),
        sa.Column("purpose", sa.String(64), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_consents_household_id", "consents", ["household_id"])
    op.create_table(
        "firm_members",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("firm_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, server_default="adviser"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_firm_members_firm_id", "firm_members", ["firm_id"])
    op.create_index("ix_firm_members_user_id", "firm_members", ["user_id"])


def downgrade() -> None:
    op.drop_table("firm_members")
    op.drop_table("consents")
    op.drop_table("graph_checkpoints")
    op.drop_table("ingest_artifacts")
