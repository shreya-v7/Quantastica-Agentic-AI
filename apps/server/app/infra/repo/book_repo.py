"""Household book of record. Lots, events, outbox, exceptions."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from quantastica_kernel.temporal import instant, reconstruct, snapshot_patch
from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.ids import new_id
from app.exceptions.fixtures import demo_books
from app.exceptions.hits import ExceptionHit, PolicyTable
from app.exceptions.snapshot import BookLot, BookSnapshot, TaxFacts
from app.infra.db.models import (
    BookEventRow,
    CalculatorRunRow,
    ExceptionDiffRow,
    ExceptionRow,
    FirmRow,
    HouseholdRow,
    LotRow,
    OutboxRow,
    ProcessedEventRow,
)

FIRM_ID = "firm_northstar"
CONSUMER = "recompute"


class BookRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession],
                 clock: Callable[[], datetime] | None = None):
        self._sessions = session_factory
        self._clock = clock or (lambda: datetime.now(UTC))

    async def _lock(self, session, household_id: str) -> None:
        await session.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
                              {"key": "book:" + household_id})

    async def _history(self, session, household_id: str) -> list[dict]:
        rows = (await session.scalars(select(BookEventRow).where(
            BookEventRow.household_id == household_id,
            BookEventRow.event_type.in_(["book.snapshot", "book.patch"]),
        ).order_by(BookEventRow.seq))).all()
        return [self._event_dict(row) for row in rows]

    def _event_dict(self, row: BookEventRow) -> dict:
        return {
            "id": row.id,
            "event_type": row.event_type,
            "payload": row.payload,
            "seq": row.seq,
            "valid_time": row.valid_time,
            "recorded_time": row.recorded_time,
        }

    async def history(self, household_id: str) -> list[dict]:
        async with self._sessions() as session:
            return await self._history(session, household_id)

    async def get_event(self, event_id: str) -> dict | None:
        async with self._sessions() as session:
            row = await session.get(BookEventRow, event_id)
        if row is None:
            return None
        return self._event_dict(row)

    async def as_of(self, household_id: str, valid_time: datetime,
                    recorded_time: datetime) -> BookSnapshot | None:
        return reconstruct(await self.history(household_id), valid_time, recorded_time)

    async def _append(self, session, household_id: str, event_type: str,
                      payload: dict, valid_time: datetime, idempotency_key: str | None = None):
        valid_time = instant(valid_time)
        prior = (await session.scalars(select(BookEventRow).where(
            BookEventRow.household_id == household_id
        ).order_by(BookEventRow.seq.desc()).limit(1))).first()
        now = instant(self._clock())
        if prior:
            now = max(now, prior.recorded_time + timedelta(microseconds=1))
        event_id = new_id("bev")
        row = BookEventRow(
            id=event_id, household_id=household_id, event_type=event_type, payload=payload,
            seq=prior.seq + 1 if prior else 1, idempotency_key=idempotency_key or event_id,
            valid_time=valid_time, recorded_time=now, created_at=now,
        )
        session.add(row)
        session.add(OutboxRow(
            id=new_id("obx"), aggregate_type="household", aggregate_id=household_id,
            event_type="household.recompute",
            payload={"householdId": household_id, "eventId": event_id},
            status="pending", created_at=now,
        ))
        await session.flush()
        return row

    async def seed_snapshot(self, book: BookSnapshot) -> None:
        book = book.model_copy(update={"lots": sorted(book.lots, key=lambda lot: lot.id)})
        async with self._sessions() as session:
            # A single firm lock also protects simultaneous first-time demo seeding.
            await self._lock(session, FIRM_ID)
            await self._lock(session, book.household_id)
            existing = await session.get(FirmRow, FIRM_ID)
            if existing is None:
                session.add(FirmRow(id=FIRM_ID, name="Northstar Private",
                                    created_at=self._clock()))
                await session.flush()
            history = await self._history(session, book.household_id)
            before = reconstruct(history, datetime.max.replace(tzinfo=UTC),
                                 datetime.max.replace(tzinfo=UTC))
            valid = datetime.combine(book.as_of, datetime.min.time(), tzinfo=UTC)
            payload = snapshot_patch(before, book) if before else book.model_dump(mode="json")
            if before and before == book:
                return
            event = await self._append(session, book.household_id,
                                       "book.patch" if before else "book.snapshot", payload, valid)
            await self._upsert_book(session, book, event.valid_time, event.recorded_time)
            await session.commit()

    async def seed_demo(self) -> dict[str, int]:
        for book in demo_books():
            await self.seed_snapshot(book)
        return {"households": 2}

    async def _upsert_book(self, session: AsyncSession, book: BookSnapshot,
                           valid_time: datetime, recorded_time: datetime) -> None:
        row = await session.get(HouseholdRow, book.household_id)
        tax = book.tax.model_dump(mode="json") if book.tax else None
        if row is None:
            session.add(
                HouseholdRow(
                    id=book.household_id,
                    firm_id=FIRM_ID,
                    valid_time=valid_time, recorded_time=recorded_time,
                    name=book.household_name,
                    bank_customer_id=(
                        "cust_hni_mehta" if book.household_id == "hh_mehta" else "cust_affluent_rao"
                    ),
                    as_of=book.as_of.isoformat(),
                    tax=tax,
                    seed=True,
                    created_at=datetime.now(UTC),
                )
            )
        else:
            row.valid_time = valid_time
            row.recorded_time = recorded_time
            row.tax = tax
            row.as_of = book.as_of.isoformat()
            row.name = book.household_name
        await session.execute(delete(LotRow).where(LotRow.household_id == book.household_id))
        for lot in book.lots:
            session.add(
                LotRow(
                    id=lot.id,
                    firm_id=FIRM_ID,
                    household_id=book.household_id,
                    valid_time=valid_time, recorded_time=recorded_time,
                    symbol=lot.symbol,
                    name=lot.name,
                    asset_class=lot.asset_class,
                    sector=lot.sector,
                    quantity=Decimal(str(lot.quantity)),
                    cost=Decimal(str(lot.cost)),
                    price=Decimal(str(lot.price)),
                    acquired_on=lot.acquired_on.isoformat(),
                    fmv_2018=Decimal(str(lot.fmv_2018)) if lot.fmv_2018 is not None else None,
                    seed=True,
                )
            )

    async def list_households(self) -> list[dict]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(select(HouseholdRow).order_by(HouseholdRow.name))
            ).all()
        return [{"id": r.id, "name": r.name, "asOf": r.as_of} for r in rows]

    async def load_snapshot(self, household_id: str) -> BookSnapshot | None:
        async with self._sessions() as session:
            hh = await session.get(HouseholdRow, household_id)
            if hh is None:
                return None
            lots = (
                await session.scalars(
                    select(LotRow)
                    .where(LotRow.household_id == household_id)
                    .order_by(LotRow.symbol)
                )
            ).all()
            tax = TaxFacts.model_validate(hh.tax) if hh.tax else None
            return BookSnapshot(
                household_id=hh.id,
                household_name=hh.name,
                as_of=date.fromisoformat(hh.as_of),
                lots=[
                    BookLot(
                        id=lot.id,
                        symbol=lot.symbol,
                        name=lot.name,
                        asset_class=lot.asset_class,
                        sector=lot.sector,
                        quantity=float(lot.quantity),
                        cost=float(lot.cost),
                        price=float(lot.price),
                        acquired_on=date.fromisoformat(lot.acquired_on),
                        fmv_2018=float(lot.fmv_2018) if lot.fmv_2018 is not None else None,
                    )
                    for lot in lots
                ],
                tax=tax,
            )

    async def policy(self) -> PolicyTable:
        async with self._sessions() as session:
            firm = await session.get(FirmRow, FIRM_ID)
        if firm is None:
            return PolicyTable()
        return PolicyTable(name_cap=firm.name_cap, sector_cap=firm.sector_cap)

    async def mutate_lot_quantity(self, household_id: str, lot_id: str, quantity: float,
                                  valid_time: datetime | None = None,
                                  idempotency_key: str | None = None) -> None:
        from math import isfinite
        if not isfinite(quantity) or quantity < 0:
            raise ValueError("quantity must be finite and non-negative")
        async with self._sessions() as session:
            await self._lock(session, household_id)
            history = await self._history(session, household_id)
            if not history:
                raise KeyError(household_id)
            book = reconstruct(history, datetime.max.replace(tzinfo=UTC),
                               datetime.max.replace(tzinfo=UTC))
            if book is None or lot_id not in {lot.id for lot in book.lots}:
                raise KeyError(lot_id)
            valid = instant(valid_time) if valid_time else datetime.combine(
                book.as_of, datetime.min.time(), tzinfo=UTC)
            if valid < min(row["valid_time"] for row in history):
                raise ValueError("Correction cannot precede the first known household state")
            payload = {"lot_quantities": [{"id": lot_id, "quantity": quantity}]}
            if idempotency_key:
                key = household_id + ":" + idempotency_key
                prior = await session.scalar(select(BookEventRow).where(
                    BookEventRow.idempotency_key == key))
                if prior:
                    if prior.payload != payload or prior.valid_time != valid:
                        raise ValueError("Idempotency key reused with a different command")
                    return
            else:
                key = None
            event = await self._append(session, household_id, "book.patch", payload, valid, key)
            current = reconstruct(await self._history(session, household_id),
                                  datetime.max.replace(tzinfo=UTC),
                                  datetime.max.replace(tzinfo=UTC))
            await self._upsert_book(session, current, event.valid_time, event.recorded_time)
            await session.commit()

    async def pending_outbox(self) -> list[dict]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(OutboxRow)
                    .where(OutboxRow.status == "pending")
                    .order_by(OutboxRow.created_at)
                    .limit(50)
                )
            ).all()
            return [
                {
                    "id": row.id,
                    "aggregateId": row.aggregate_id,
                    "payload": dict(row.payload),
                }
                for row in rows
            ]

    async def mark_outbox(self, outbox_id: str, status: str) -> None:
        async with self._sessions() as session:
            await session.execute(
                update(OutboxRow).where(OutboxRow.id == outbox_id).values(status=status)
            )
            await session.commit()

    async def already_processed(self, event_id: str) -> bool:
        async with self._sessions() as session:
            row = await session.get(ProcessedEventRow, (CONSUMER, event_id))
            return row is not None

    async def mark_processed(self, event_id: str) -> None:
        async with self._sessions() as session:
            session.add(
                ProcessedEventRow(
                    consumer=CONSUMER, event_id=event_id, processed_at=datetime.now(UTC)
                )
            )
            await session.commit()

    async def replace_exceptions(
        self,
        household_id: str,
        hits: list[ExceptionHit],
        diff: dict[str, list[str]],
        run_id: str,
    ) -> None:
        now = datetime.now(UTC)
        async with self._sessions() as session:
            await session.execute(
                delete(ExceptionRow).where(ExceptionRow.household_id == household_id)
            )
            await session.execute(
                delete(CalculatorRunRow).where(CalculatorRunRow.household_id == household_id)
            )
            for hit in hits:
                ex_id = new_id("exc")
                session.add(
                    ExceptionRow(
                        id=ex_id,
                        household_id=household_id,
                        rule_id=hit.rule_id,
                        title=hit.title,
                        rupee_delta=hit.rupee_delta,
                        due_date=hit.due_date.isoformat() if hit.due_date else None,
                        severity=hit.severity,
                        metric_ids=hit.metric_ids,
                        fingerprint=hit.fingerprint,
                        trace_id=ex_id,
                        status="open",
                        calculator=hit.calculator,
                        calculator_version=hit.calculator_version,
                        inputs=hit.inputs,
                        outputs=hit.outputs,
                        computed_at=now,
                    )
                )
                session.add(
                    CalculatorRunRow(
                        id=new_id("crun"),
                        household_id=household_id,
                        exception_id=ex_id,
                        calculator=hit.calculator,
                        version=hit.calculator_version,
                        inputs=hit.inputs,
                        outputs=hit.outputs,
                        created_at=now,
                    )
                )
            session.add(
                ExceptionDiffRow(
                    id=new_id("ediff"),
                    household_id=household_id,
                    run_id=run_id,
                    added=diff["added"],
                    removed=diff["removed"],
                    changed=diff["changed"],
                    created_at=now,
                )
            )
            await session.commit()

    async def list_exceptions(self, household_id: str) -> list[dict]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(ExceptionRow)
                    .where(
                        ExceptionRow.household_id == household_id,
                        ExceptionRow.status == "open",
                    )
                    .order_by(ExceptionRow.rupee_delta.desc())
                )
            ).all()
        return [
            {
                "id": r.id,
                "householdId": r.household_id,
                "ruleId": r.rule_id,
                "title": r.title,
                "rupeeDelta": r.rupee_delta,
                "dueDate": r.due_date,
                "severity": r.severity,
                "metricIds": r.metric_ids,
                "fingerprint": r.fingerprint,
                "traceId": r.trace_id,
                "calculator": r.calculator,
                "calculatorVersion": r.calculator_version,
                "inputs": r.inputs,
                "outputs": r.outputs,
                "computedAt": r.computed_at.isoformat(),
            }
            for r in rows
        ]

    async def get_exception(self, exception_id: str) -> dict | None:
        async with self._sessions() as session:
            row = await session.get(ExceptionRow, exception_id)
        if row is None:
            return None
        rows = await self.list_exceptions(row.household_id)
        return next((item for item in rows if item["id"] == exception_id), None)

    async def list_lots(self, household_id: str) -> list[dict]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(LotRow)
                    .where(LotRow.household_id == household_id)
                    .order_by(LotRow.symbol)
                )
            ).all()
        return [
            {
                "id": r.id,
                "symbol": r.symbol,
                "name": r.name,
                "quantity": float(r.quantity),
                "price": float(r.price),
                "marketValue": float(r.quantity) * float(r.price),
                "sector": r.sector,
                "acquiredOn": r.acquired_on,
            }
            for r in rows
        ]
