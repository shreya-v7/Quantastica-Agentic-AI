"""Adversarial cross-tenant retrieval. RLS via SET LOCAL, FORCE, no session vars."""
from datetime import UTC, datetime

from app.infra.db.models import UserRow
from app.infra.factory import ProviderSlot
from app.providers.embeddings.hashing import HashingEmbeddings
from app.services.document_service import DocumentService
from sqlalchemy import text

USER = "usr_seed_arjun"
OTHER = "usr_other"


def _svc(container) -> DocumentService:
    container.providers["embeddings"] = ProviderSlot(HashingEmbeddings(), True, [], "hashing")
    return DocumentService(container)


async def test_hybrid_recall_holds_for_owner(container):
    svc = _svc(container)
    await svc.ingest(USER, "tax note", "New regime rebate for income below 12 lakh.")
    hits = await svc.retrieve(USER, "new regime rebate", k=3)
    assert hits
    other = await svc.retrieve(OTHER, "new regime rebate", k=3)
    assert other == []


async def test_rls_force_hides_other_tenant(container):
    """Table-owner superusers bypass RLS. Query as a NOBYPASSRLS role."""
    svc = _svc(container)
    await svc.ingest(USER, "secret", "Tenant A only holding note about RELIANCE lots.")
    async with container.session_factory() as session:
        session.add(UserRow(
            id=OTHER, email="other@example.com", password_hash="x", role="user",
            created_at=datetime.now(UTC),
        ))
        await session.commit()
    engine = container.repository.engine  # type: ignore[attr-defined]
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY"))
            await conn.execute(text("ALTER TABLE document_chunks FORCE ROW LEVEL SECURITY"))
            await conn.execute(text("DROP POLICY IF EXISTS tenant_chunks ON document_chunks"))
            await conn.execute(text(
                "CREATE POLICY tenant_chunks ON document_chunks "
                "USING (user_id = current_setting('app.current_user_id', true))"
            ))
            await conn.execute(text("""
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rls_reader') THEN
                        CREATE ROLE rls_reader NOLOGIN NOSUPERUSER NOBYPASSRLS;
                    END IF;
                END $$
            """))
            await conn.execute(text("GRANT USAGE ON SCHEMA public TO rls_reader"))
            await conn.execute(text("GRANT SELECT ON document_chunks TO rls_reader"))
            await conn.execute(
                text("SELECT set_config('app.current_user_id', :uid, true)"),
                {"uid": OTHER},
            )
            await conn.execute(text("SET LOCAL ROLE rls_reader"))
            leaked = (
                await conn.execute(text("SELECT user_id FROM document_chunks"))
            ).scalars().all()
        assert USER not in leaked
        assert all(uid == OTHER for uid in leaked)
    finally:
        async with engine.begin() as conn:
            await conn.execute(text("DROP POLICY IF EXISTS tenant_chunks ON document_chunks"))
            await conn.execute(text("ALTER TABLE document_chunks NO FORCE ROW LEVEL SECURITY"))
            await conn.execute(text("ALTER TABLE document_chunks DISABLE ROW LEVEL SECURITY"))
