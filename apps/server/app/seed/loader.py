"""Seed loader. The only place in the codebase that introduces fabricated records.

Every record is flagged "seed": true. Loading is always an explicit action, never
automatic in prod. Market prices and news are never seeded.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.infra.repo.base import Repository, SeedBundle
from app.schemas.entities import Holding, Portfolio, Transaction

_FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> list[dict]:
    return json.loads((_FIXTURES / name).read_text())


def load_users() -> list[dict]:
    return _load("users.json")


def load_portfolio_records() -> list[dict]:
    return _load("portfolios.json")


def load_portfolios() -> list[Portfolio]:
    records = []
    for record in load_portfolio_records():
        data = {k: v for k, v in record.items() if k != "ownerId"}
        records.append(Portfolio.model_validate(data))
    return records


def load_holdings() -> list[Holding]:
    return [Holding.model_validate(r) for r in _load("holdings.json")]


def load_transactions() -> list[Transaction]:
    return [Transaction.model_validate(r) for r in _load("transactions.json")]


def load_catalog() -> list[dict]:
    return _load("catalog.json")


def load_profile() -> dict:
    return _load("profile.json")


def build_bundle() -> SeedBundle:
    owner_by_portfolio = {r["id"]: r["ownerId"] for r in load_portfolio_records()}
    return SeedBundle(
        users=load_users(),
        portfolios=load_portfolios(),
        holdings=load_holdings(),
        transactions=load_transactions(),
        owner_by_portfolio=owner_by_portfolio,
        catalog=load_catalog(),
        profile=load_profile(),
    )


async def load_into(repository: Repository) -> dict[str, int]:
    return await repository.load_seed(build_bundle())


async def reset(repository: Repository) -> dict[str, int]:
    return await repository.reset_seed()
