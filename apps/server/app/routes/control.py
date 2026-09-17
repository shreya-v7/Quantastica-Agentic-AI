"""DSR, eval catalog, dashboards, and trust-center JSON. Informational only."""
from __future__ import annotations

from datetime import UTC, datetime

from evals.catalog import run_catalog
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import delete, text, update

from app.core.dependencies import get_container, require_role
from app.core.envelope import success
from app.core.ids import new_id
from app.fde import health, layout_for
from app.infra.db.models import (
    ConsentRow,
    DsrRequestRow,
    ExceptionRow,
    HouseholdRow,
    IngestArtifactRow,
    LotRow,
)
from app.infra.factory import Container
from app.infra.repo.book_repo import BookRepository
from app.olap import aggregate
from app.slo import alert

router = APIRouter(prefix="/control")


class EraseBody(BaseModel):
    household_id: str


@router.post("/dsr/access")
async def dsr_access(
    body: EraseBody,
    container: Container = Depends(get_container),
    _: str = Depends(require_role("admin", "adviser")),
) -> dict:
    from app.infra.repo.ingest_repo import IngestRepository
    from app.privacy import mask_pii
    from app.services.desk_service import DeskService

    desk = DeskService(BookRepository(container.session_factory))
    queue = await desk.queue(body.household_id)
    consents = await IngestRepository(container.session_factory).list_consents(body.household_id)
    return success({
        "household": queue["household"],
        "lots": queue["lots"],
        "exceptions": queue["exceptions"],
        "consents": consents,
        "maskedSample": mask_pii("PAN ABCDE1234F account 123456789012"),
        "kind": "access",
    })


@router.post("/dsr/erasure")
async def dsr_erasure(
    body: EraseBody,
    container: Container = Depends(get_container),
    _: str = Depends(require_role("admin")),
) -> dict:
    async with container.session_factory() as session:
        await session.execute(delete(LotRow).where(LotRow.household_id == body.household_id))
        await session.execute(
            delete(ExceptionRow).where(ExceptionRow.household_id == body.household_id)
        )
        await session.execute(
            delete(IngestArtifactRow).where(IngestArtifactRow.household_id == body.household_id)
        )
        await session.execute(
            delete(ConsentRow).where(ConsentRow.household_id == body.household_id)
        )
        await session.execute(
            update(HouseholdRow)
            .where(HouseholdRow.id == body.household_id)
            .values(name="erased", tax=None, bank_customer_id=None)
        )
        session.add(
            DsrRequestRow(
                id=new_id("dsr"),
                household_id=body.household_id,
                kind="erasure",
                status="closed",
                created_at=datetime.now(UTC),
            )
        )
        await session.commit()
    return success({"status": "erased", "householdId": body.household_id, "auditRetained": True})


@router.get("/evals")
def evals() -> dict:
    return success(run_catalog())


@router.get("/dashboards")
def dashboards() -> dict:
    catalog = run_catalog()
    page = alert(0.02, 0.02)
    ticket = alert(0.0, 0.0, 0.007)
    return success({
        "exec": {"arr": 0, "logos": 0, "nrr": None, "rupeesSurfaced": catalog["pitch"]["rupees"]},
        "product": {
            "documents": catalog["pitch"]["documents"],
            "exceptions": catalog["pitch"]["exceptions"],
        },
        "aiQuality": catalog["metrics"],
        "sre": {
            "pageAlert": page.__dict__ if page else None,
            "ticketAlert": ticket.__dict__ if ticket else None,
            "dlqDepth": 0,
            "replayDeterminism": 1.0,
        },
        "finops": {"costPerHousehold": 0.0, "cacheHit": None},
        "security": {"crossTenantLeakage": 0, "guardFailClosed": True},
        "fde": health(0.4, 4, catalog["pitch"]["rupees"], 12, 0.0, 1.0),
        "olap": aggregate([]),
    })


@router.get("/slo/synthetic-incident")
def synthetic_incident() -> dict:
    fired = alert(0.02, 0.03)
    return success({"alert": fired.__dict__ if fired else None, "expected": "page"})


@router.get("/trust")
def trust() -> dict:
    return success({
        "residency": "asia-south1 planned; local Postgres today",
        "cmek": False,
        "rls": "document_chunks SET LOCAL app.current_user_id",
        "dsr": ["access", "erasure"],
        "breachWindowHours": 72,
        "advice": "informational only",
        "trading": "paper, flagged, TRADING_CHAT_ENABLED",
    })


@router.get("/fde/layout")
def layout(employer: str = "Northstar Labs Pvt Ltd") -> dict:
    return success(layout_for(employer))


@router.post("/retrieval/enable-rls")
async def enable_rls(
    container: Container = Depends(get_container),
    _: str = Depends(require_role("admin")),
) -> dict:
    async with container.session_factory() as session:
        await session.execute(text("ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY"))
        await session.execute(text("ALTER TABLE document_chunks FORCE ROW LEVEL SECURITY"))
        await session.execute(text(
            "DROP POLICY IF EXISTS tenant_chunks ON document_chunks"
        ))
        await session.execute(text(
            "CREATE POLICY tenant_chunks ON document_chunks "
            "USING (user_id = current_setting('app.current_user_id', true))"
        ))
        await session.commit()
    return success({"rls": True})
