"""Desk: load book, recompute exceptions, drain local outbox."""

from __future__ import annotations

from datetime import date, datetime

from quantastica_kernel.recompute import dirty_rules, fields_from_event

from app.core.errors import NotFoundError, ValidationError
from app.core.ids import new_id
from app.exceptions.engine import compute_exceptions, diff_exceptions, merge_hits
from app.exceptions.hits import ExceptionHit
from app.infra.repo.book_repo import BookRepository


class DeskService:
    def __init__(self, books: BookRepository):
        self._books = books

    async def ensure_seeded(self) -> None:
        households = await self._books.list_households()
        if not households:
            await self._books.seed_demo()
            for row in await self._books.list_households():
                await self.recompute(row["id"])

    async def households(self) -> list[dict]:
        await self.ensure_seeded()
        return await self._books.list_households()

    async def queue(self, household_id: str) -> dict:
        await self.ensure_seeded()
        book = await self._books.load_snapshot(household_id)
        if book is None:
            raise NotFoundError(f"Household {household_id} not found")
        rows = await self._books.list_exceptions(household_id)
        if not rows:
            await self.recompute(household_id)
            rows = await self._books.list_exceptions(household_id)
        lots = await self._books.list_lots(household_id)
        return {
            "household": {
                "id": book.household_id,
                "name": book.household_name,
                "asOf": book.as_of.isoformat(),
                "totalMarket": book.total_market,
            },
            "exceptions": rows,
            "lots": lots,
        }

    async def exception(self, exception_id: str) -> dict:
        row = await self._books.get_exception(exception_id)
        if row is None:
            raise NotFoundError(f"Exception {exception_id} not found")
        return row

    async def set_lot_quantity(self, household_id: str, lot_id: str, quantity: float,
                               valid_time: datetime | None = None,
                               idempotency_key: str | None = None) -> dict:
        if quantity < 0:
            raise ValidationError("quantity must be >= 0")
        try:
            await self._books.mutate_lot_quantity(
                household_id, lot_id, quantity, valid_time, idempotency_key
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        except KeyError as exc:
            raise NotFoundError(f"Lot {lot_id} not found") from exc
        await self.drain_outbox()
        return await self.queue(household_id)

    def _hits_from_rows(self, rows: list[dict]) -> list[ExceptionHit]:
        return [
            ExceptionHit(
                rule_id=row["ruleId"],
                version="1",
                title=row["title"],
                rupee_delta=row["rupeeDelta"],
                due_date=date.fromisoformat(row["dueDate"]) if row["dueDate"] else None,
                severity=row["severity"],
                metric_ids=row["metricIds"],
                fingerprint=row["fingerprint"],
                calculator=row["calculator"],
                calculator_version=row["calculatorVersion"],
                inputs=row["inputs"],
                outputs=row["outputs"],
            )
            for row in rows
        ]

    async def recompute(
        self, household_id: str, event_id: str | None = None
    ) -> dict[str, list[str]]:
        if event_id and await self._books.already_processed(event_id):
            return {"added": [], "removed": [], "changed": []}
        book = await self._books.load_snapshot(household_id)
        if book is None:
            raise NotFoundError(f"Household {household_id} not found")
        policy = await self._books.policy()
        prior = self._hits_from_rows(await self._books.list_exceptions(household_id))
        event = await self._books.get_event(event_id) if event_id else None
        if event is None:
            hits = compute_exceptions(book, policy)
        else:
            dirty = dirty_rules(fields_from_event(event["event_type"], event["payload"]))
            if not dirty:
                if event_id:
                    await self._books.mark_processed(event_id)
                return {"added": [], "removed": [], "changed": []}
            hits = merge_hits(
                prior, compute_exceptions(book, policy, rule_ids=dirty), dirty
            )
        diff = diff_exceptions(prior, hits)
        await self._books.replace_exceptions(household_id, hits, diff, new_id("erun"))
        if event_id:
            await self._books.mark_processed(event_id)
        return diff

    async def drain_outbox(self) -> int:
        """Local relay. Prod swaps this for EventBridge/SQS."""
        pending = await self._books.pending_outbox()
        drained = 0
        for row in pending:
            household_id = str(row["payload"].get("householdId") or row["aggregateId"])
            event_id = row["payload"].get("eventId")
            try:
                await self.recompute(household_id, event_id)
                await self._books.mark_outbox(row["id"], "sent")
                drained += 1
            except Exception:
                await self._books.mark_outbox(row["id"], "failed")
                raise
        return drained
