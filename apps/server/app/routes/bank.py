"""Mock bank core endpoints. Demo stand-in for a wealth / CBS API."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_container
from app.core.envelope import success
from app.infra.factory import Container
from app.providers.bank.base import BankProvider

router = APIRouter(prefix="/bank")


def _bank(container: Container) -> BankProvider:
    return container.provider("bank")  # type: ignore[return-value]


@router.get("/status")
def status(container: Container = Depends(get_container)) -> dict:
    return success(_bank(container).status())


@router.get("/customers")
def customers(container: Container = Depends(get_container)) -> dict:
    return success(_bank(container).list_customers())


@router.get("/customers/{customer_id}")
def customer(customer_id: str, container: Container = Depends(get_container)) -> dict:
    return success(_bank(container).customer(customer_id))


@router.get("/customers/{customer_id}/accounts")
def accounts(customer_id: str, container: Container = Depends(get_container)) -> dict:
    return success(_bank(container).accounts(customer_id))


@router.get("/customers/{customer_id}/holdings")
def holdings(customer_id: str, container: Container = Depends(get_container)) -> dict:
    return success(_bank(container).holdings(customer_id))


@router.get("/customers/{customer_id}/transactions")
def transactions(customer_id: str, container: Container = Depends(get_container)) -> dict:
    return success(_bank(container).transactions(customer_id))


@router.get("/customers/{customer_id}/snapshot")
def snapshot(customer_id: str, container: Container = Depends(get_container)) -> dict:
    return success(_bank(container).snapshot(customer_id))
