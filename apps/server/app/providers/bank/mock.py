"""Mock Northstar Private. Deterministic demo core. Every payload is labelled mock.

Not a real bank. Not a scrape. The adapter a CBS integration is supposed to replace.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.core.errors import NotFoundError
from app.providers.bank.base import BankProvider

BANK = {
    "id": "northstar-private",
    "name": "Northstar Private",
    "mock": True,
    "note": "Demo core. Replace this adapter with the bank wealth API in a B2B deploy.",
}

_CUSTOMERS: dict[str, dict[str, Any]] = {
    "cust_hni_mehta": {
        "id": "cust_hni_mehta",
        "name": "Karan Mehta",
        "segment": "hni",
        "city": "Mumbai",
        "rm": "Priya Shah",
        "mock": True,
    },
    "cust_affluent_rao": {
        "id": "cust_affluent_rao",
        "name": "Ananya Rao",
        "segment": "mass_affluent",
        "city": "Bengaluru",
        "rm": "Dev Patel",
        "mock": True,
    },
}

_ACCOUNTS: dict[str, list[dict[str, Any]]] = {
    "cust_hni_mehta": [
        {"id": "acc_mehta_sav", "type": "savings", "currency": "INR", "balanceInr": 8_400_000},
        {"id": "acc_mehta_cur", "type": "current", "currency": "INR", "balanceInr": 2_150_000},
        {"id": "acc_mehta_demat", "type": "demat", "currency": "INR", "balanceInr": 0},
        {"id": "acc_mehta_hl", "type": "home_loan", "currency": "INR", "balanceInr": -18_500_000},
    ],
    "cust_affluent_rao": [
        {"id": "acc_rao_sav", "type": "savings", "currency": "INR", "balanceInr": 450_000},
        {"id": "acc_rao_demat", "type": "demat", "currency": "INR", "balanceInr": 0},
        {"id": "acc_rao_epf", "type": "epf", "currency": "INR", "balanceInr": 1_200_000},
    ],
}

def _h(
    symbol: str,
    name: str,
    asset_class: str,
    sector: str,
    quantity: float,
    cost: float,
    price: float,
) -> dict[str, Any]:
    market = round(quantity * price, 2)
    return {
        "symbol": symbol,
        "name": name,
        "assetClass": asset_class,
        "sector": sector,
        "quantity": quantity,
        "costBasis": cost,
        "priceInr": price,
        "marketValueInr": market,
        "mock": True,
    }


# Prices are fixtures, not live quotes. The mock core owns the book.
_HOLDINGS: dict[str, list[dict[str, Any]]] = {
    "cust_hni_mehta": [
        _h("RELIANCE.NS", "Reliance Industries", "equity", "Energy", 5000, 2400, 2950),
        _h(
            "TCS.NS",
            "Tata Consultancy Services",
            "equity",
            "Information Technology",
            2000,
            3300,
            4100,
        ),
        _h("INFY.NS", "Infosys", "equity", "Information Technology", 3000, 1350, 1820),
        _h("HDFCBANK.NS", "HDFC Bank", "equity", "Financials", 1500, 1480, 1650),
        _h("NIFTYBEES.NS", "Nippon India ETF Nifty BeES", "etf", "Index", 10000, 220, 260),
        _h("LIQUIDBEES.NS", "Nippon India ETF Liquid BeES", "etf", "Debt", 8000, 1000, 1000),
    ],
    "cust_affluent_rao": [
        _h("NIFTYBEES.NS", "Nippon India ETF Nifty BeES", "etf", "Index", 2000, 220, 260),
        _h("RELIANCE.NS", "Reliance Industries", "equity", "Energy", 80, 2400, 2950),
    ],
}

_TXNS: dict[str, list[dict[str, Any]]] = {
    "cust_hni_mehta": [
        {
            "id": "tx_m1",
            "date": "2026-09-01",
            "accountId": "acc_mehta_sav",
            "amountInr": 2_500_000,
            "narration": "Dividend CREDIT RELIANCE",
        },
        {
            "id": "tx_m2",
            "date": "2026-08-15",
            "accountId": "acc_mehta_hl",
            "amountInr": -185_000,
            "narration": "Home loan EMI",
        },
        {
            "id": "tx_m3",
            "date": "2026-08-05",
            "accountId": "acc_mehta_demat",
            "amountInr": -1_200_000,
            "narration": "Buy INFY.NS",
        },
    ],
    "cust_affluent_rao": [
        {
            "id": "tx_r1",
            "date": "2026-09-05",
            "accountId": "acc_rao_sav",
            "amountInr": 95_000,
            "narration": "Salary CREDIT",
        },
        {
            "id": "tx_r2",
            "date": "2026-09-07",
            "accountId": "acc_rao_demat",
            "amountInr": -10_000,
            "narration": "SIP NIFTYBEES",
        },
    ],
}


def _require(customer_id: str) -> dict[str, Any]:
    customer = _CUSTOMERS.get(customer_id)
    if customer is None:
        raise NotFoundError(f"Mock bank customer '{customer_id}' not found")
    return deepcopy(customer)


def market_value(holdings: list[dict[str, Any]]) -> float:
    return round(sum(float(row["marketValueInr"]) for row in holdings), 2)


class MockNorthstarBank(BankProvider):
    def status(self) -> dict[str, Any]:
        return {**BANK, "customers": len(_CUSTOMERS), "ready": True}

    def list_customers(self) -> list[dict[str, Any]]:
        return [deepcopy(row) for row in _CUSTOMERS.values()]

    def customer(self, customer_id: str) -> dict[str, Any]:
        return _require(customer_id)

    def accounts(self, customer_id: str) -> list[dict[str, Any]]:
        _require(customer_id)
        return deepcopy(_ACCOUNTS[customer_id])

    def holdings(self, customer_id: str) -> list[dict[str, Any]]:
        _require(customer_id)
        return deepcopy(_HOLDINGS[customer_id])

    def transactions(self, customer_id: str) -> list[dict[str, Any]]:
        _require(customer_id)
        return deepcopy(_TXNS[customer_id])

    def snapshot(self, customer_id: str) -> dict[str, Any]:
        holdings = self.holdings(customer_id)
        accounts = self.accounts(customer_id)
        cash_types = {"savings", "current", "epf"}
        cash = round(sum(float(a["balanceInr"]) for a in accounts if a["type"] in cash_types), 2)
        return {
            "bank": BANK,
            "customer": self.customer(customer_id),
            "accounts": accounts,
            "holdings": holdings,
            "transactions": self.transactions(customer_id),
            "totals": {
                "holdingsMarketValueInr": market_value(holdings),
                "cashAndEpfInr": cash,
            },
            "mock": True,
            "disclaimer": "Mock core. Not a live bank feed. Not investment advice.",
        }
