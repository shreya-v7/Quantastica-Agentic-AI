"""Application-boundary checks that the isolated kernel CI job cannot import."""
from app.calculators.tax import compare_regimes as old
from app.offline_demo import TIERS, household, proof
from quantastica_kernel.api import replay
from quantastica_kernel.calculators.tax import compare_regimes as new


def test_compatibility_exports():
    assert old is new


def test_demo_seed_and_all_tiers():
    for count in TIERS.values():
        assert proof(count - 1, 42) == proof(count - 1, 42)
    assert household(2, 42) != household(2, 43)
    for index in (0, 1):
        receipt = proof(index, 42)["receipt"]
        assert receipt["outputs"]
        assert replay(receipt) == receipt
