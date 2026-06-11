import json
from pathlib import Path

from app import __version__
from app.seed import loader

_CONTRACTS = Path(__file__).resolve().parents[3] / "packages" / "types" / "contracts.json"


def test_seed_fixtures_validate_against_schemas_and_are_flagged():
    portfolios = loader.load_portfolios()
    holdings = loader.load_holdings()
    transactions = loader.load_transactions()

    assert portfolios and holdings and transactions
    assert all(p.seed for p in portfolios)
    assert all(h.seed for h in holdings)
    assert all(t.seed for t in transactions)

    portfolio_ids = {p.id for p in portfolios}
    assert all(h.portfolio_id in portfolio_ids for h in holdings)
    assert all(t.portfolio_id in portfolio_ids for t in transactions)


def test_contract_version_matches_package():
    contract_version = json.loads(_CONTRACTS.read_text())["version"]
    assert contract_version == __version__
