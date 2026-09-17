import pytest
from app.core.errors import NotFoundError
from app.mcp.server import build_server
from app.mcp.tools import bank_customer_snapshot, bank_holdings, bank_list_customers
from app.providers.bank.mock import MockNorthstarBank


def test_hni_book_is_sized_like_a_private_bank_sleeve():
    snap = MockNorthstarBank().snapshot("cust_hni_mehta")
    assert snap["mock"] is True
    assert snap["customer"]["segment"] == "hni"
    assert snap["totals"]["holdingsMarketValueInr"] == 41_485_000
    reliance = next(h for h in snap["holdings"] if h["symbol"] == "RELIANCE.NS")
    assert reliance["marketValueInr"] == 14_750_000


def test_affluent_book_is_smaller_and_still_labelled_mock():
    snap = MockNorthstarBank().snapshot("cust_affluent_rao")
    assert snap["customer"]["segment"] == "mass_affluent"
    assert snap["totals"]["holdingsMarketValueInr"] == 756_000
    assert snap["totals"]["cashAndEpfInr"] == 1_650_000


def test_unknown_customer_is_not_found():
    with pytest.raises(NotFoundError):
        MockNorthstarBank().customer("cust_nope")


def test_mcp_bank_tools_share_the_mock_book():
    listed = bank_list_customers()
    ids = {row["id"] for row in listed["customers"]}
    assert ids == {"cust_hni_mehta", "cust_affluent_rao"}
    snap = bank_customer_snapshot("cust_hni_mehta")
    held = bank_holdings("cust_hni_mehta")
    assert snap["totals"]["holdingsMarketValueInr"] == 41_485_000
    assert len(held["holdings"]) == 6


def test_mcp_server_registers_bank_tools():
    server = build_server()
    names = {tool.name for tool in server._tool_manager.list_tools()}
    assert "bank_customer_snapshot" in names
    assert "bank_list_customers" in names
    assert "compare_tax_regimes" in names
