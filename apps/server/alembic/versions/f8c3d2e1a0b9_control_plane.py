"""Control plane tables, DSR log, and document RLS."""
from alembic import op

revision = "f8c3d2e1a0b9"
down_revision = "e81c0b90a124"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE dsr_requests (
            id VARCHAR(64) PRIMARY KEY,
            household_id VARCHAR(64) NOT NULL,
            kind VARCHAR(16) NOT NULL,
            status VARCHAR(16) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE bus_dlq (
            id VARCHAR(64) PRIMARY KEY,
            household_id VARCHAR(64) NOT NULL,
            event_id VARCHAR(64) NOT NULL,
            payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE layout_packs (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            employer VARCHAR(255) NOT NULL,
            fields JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE document_chunks FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_chunks ON document_chunks
        USING (user_id = current_setting('app.current_user_id', true))
    """)


def downgrade():
    op.execute("DROP POLICY IF EXISTS tenant_chunks ON document_chunks")
    op.execute("ALTER TABLE document_chunks DISABLE ROW LEVEL SECURITY")
    op.execute("DROP TABLE layout_packs")
    op.execute("DROP TABLE bus_dlq")
    op.execute("DROP TABLE dsr_requests")
