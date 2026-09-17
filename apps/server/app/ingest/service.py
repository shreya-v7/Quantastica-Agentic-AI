"""Apply a validated extract to the household book, then recompute exceptions."""

from __future__ import annotations

from datetime import date

from app.core.errors import NotFoundError
from app.exceptions.snapshot import BookLot, TaxFacts
from app.infra.repo.book_repo import BookRepository
from app.infra.repo.ingest_repo import IngestRepository
from app.ingest.graph import IngestState, run_ingest
from app.services.desk_service import DeskService


class IngestService:
    def __init__(
        self,
        books: BookRepository,
        desk: DeskService,
        artifacts: IngestRepository | None = None,
    ):
        self._books = books
        self._desk = desk
        self._artifacts = artifacts
        self._paused: dict[str, IngestState] = {}

    def parse(self, state: IngestState) -> IngestState:
        return run_ingest(state)

    def pause(self, thread_id: str, state: IngestState) -> IngestState:
        self._paused[thread_id] = state
        return state

    async def persist_pause(self, thread_id: str, state: IngestState) -> IngestState:
        self.pause(thread_id, state)
        if self._artifacts is not None:
            await self._artifacts.save_checkpoint(thread_id, state)
        return state

    async def resume(self, thread_id: str, patch: dict) -> IngestState:
        state = self._paused.get(thread_id)
        if state is None and self._artifacts is not None:
            loaded = await self._artifacts.load_checkpoint(thread_id)
            state = loaded
        if state is None:
            raise KeyError(thread_id)
        extracted = {**(state.get("extracted") or {}), **patch}
        state = {
            **state,
            "extracted": extracted,
            "needs_review": False,
            "missing_fields": [],
            "confidence": max(float(state.get("confidence") or 0), 0.95),
        }
        self._paused[thread_id] = state
        if self._artifacts is not None:
            await self._artifacts.save_checkpoint(thread_id, state)
        return state

    async def apply(self, household_id: str, state: IngestState) -> dict:
        if state.get("needs_review"):
            thread_id = f"{household_id}:review"
            await self.persist_pause(thread_id, {**state, "household_id": household_id})
            if self._artifacts is not None:
                await self._artifacts.save_artifact(
                    household_id,
                    str(state.get("kind") or "unknown"),
                    "needs_review",
                    state.get("extracted"),
                    list(state.get("missing_fields") or []),
                    float(state.get("confidence") or 0),
                    thread_id,
                )
            return {
                "status": "needs_review",
                "threadId": thread_id,
                "missingFields": state.get("missing_fields") or [],
                "extracted": state.get("extracted"),
                "confidence": state.get("confidence"),
            }
        book = await self._books.load_snapshot(household_id)
        if book is None:
            raise NotFoundError(f"Household {household_id} not found")
        extracted = state.get("extracted") or {}
        kind = extracted.get("kind") or state.get("kind")
        if kind == "form16":
            salary_field = extracted.get("basic_salary") or extracted.get("basicSalary") or {}
            salary = float(salary_field.get("amount") or 0)
            tax = book.tax or TaxFacts(basic_salary=salary)
            book = book.model_copy(
                update={"tax": tax.model_copy(update={"basic_salary": salary})}
            )
            await self._books.seed_snapshot(book)
        elif kind == "text_event" and extracted.get("event_type") == "bonus":
            extra = float(extracted.get("amount_inr") or extracted.get("amountInr") or 0)
            tax = book.tax or TaxFacts(basic_salary=0)
            book = book.model_copy(
                update={"tax": tax.model_copy(update={"other_income": tax.other_income + extra})}
            )
            await self._books.seed_snapshot(book)
        elif kind == "cas":
            lots = list(book.lots)
            for row in extracted.get("lots") or []:
                lots.append(
                    BookLot(
                        id=f"lot_cas_{row['symbol']}_{len(lots)+1}",
                        symbol=row["symbol"],
                        name=row["name"],
                        asset_class="equity",
                        sector="Unknown",
                        quantity=float(row["quantity"]),
                        cost=float(row["cost"]),
                        price=float(row["cost"]),
                        acquired_on=date.fromisoformat(row["acquired_on"]),
                    )
                )
            await self._books.seed_snapshot(book.model_copy(update={"lots": lots}))
        if self._artifacts is not None:
            await self._artifacts.save_artifact(
                household_id,
                str(kind or "unknown"),
                "applied",
                extracted,
                [],
                float(state.get("confidence") or 1),
            )
        await self._desk.drain_outbox()
        return {"status": "applied", "queue": await self._desk.queue(household_id)}
