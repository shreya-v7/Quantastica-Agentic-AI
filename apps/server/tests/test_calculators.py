"""Exhaustive checks for the deterministic calculators: hand-computed Indian tax cases,
capital gains, SIP math, EMI/FOIR affordability, and seeded Monte Carlo."""

from __future__ import annotations

import pytest
from app.calculators.capital_gains import SellLot, compute_equity_gains
from app.calculators.planning import (
    AffordabilityInput,
    affordability,
    emi,
    monte_carlo_sip,
    required_monthly_sip,
    step_up_sip_first_month,
)
from app.calculators.tax import TaxInput, compare_regimes, hra_exemption, slab_tax
from app.calculators.tax_rules.ay_2025_26 import NEW_REGIME, OLD_REGIME


class TestSlabTax:
    def test_old_regime_10l(self):
        # 2.5L at 0, 2.5L at 5% = 12500, 5L at 20% = 100000
        assert slab_tax(1_000_000, OLD_REGIME["slabs"]) == pytest.approx(112_500)

    def test_new_regime_16l(self):
        # 3L at 0, 4L at 5% = 20000, 3L at 10% = 30000, 2L at 15% = 30000,
        # 3L at 20% = 60000, 1L at 30% = 30000
        assert slab_tax(1_600_000, NEW_REGIME["slabs"]) == pytest.approx(170_000)

    def test_zero(self):
        assert slab_tax(0, OLD_REGIME["slabs"]) == 0


class TestRebate87A:
    def test_new_regime_7l_income_pays_zero(self):
        result = compare_regimes(TaxInput(basic_salary=775_000))
        # 775000 - 75000 std deduction = 700000 taxable, fully rebated.
        assert result.new_regime.total_tax == 0

    def test_old_regime_5l_taxable_pays_zero(self):
        result = compare_regimes(TaxInput(basic_salary=550_000))
        # 550000 - 50000 std = 500000 taxable, 12500 tax fully rebated.
        assert result.old_regime.total_tax == 0


class TestRegimeComparison:
    def test_heavy_deductions_favor_old(self):
        result = compare_regimes(
            TaxInput(
                basic_salary=1_200_000,
                hra_received=400_000,
                rent_paid=360_000,
                deduction_80c=150_000,
                health_premium_self=25_000,
                nps_80ccd_1b=50_000,
                home_loan_interest=200_000,
            )
        )
        assert result.recommended == "old"
        assert result.old_regime.total_tax < result.new_regime.total_tax

    def test_no_deductions_favor_new(self):
        result = compare_regimes(TaxInput(basic_salary=1_500_000))
        assert result.recommended == "new"

    def test_cess_is_4_percent(self):
        result = compare_regimes(TaxInput(basic_salary=2_000_000))
        new = result.new_regime
        assert new.cess == pytest.approx((new.slab_tax - new.rebate_87a + new.surcharge) * 0.04)

    def test_deduction_caps_applied(self):
        result = compare_regimes(TaxInput(basic_salary=2_000_000, deduction_80c=500_000))
        line = next(ln for ln in result.old_regime.lines if "80C" in ln.label)
        assert line.amount == 150_000

    def test_surcharge_above_50l(self):
        result = compare_regimes(TaxInput(basic_salary=7_500_000))
        assert result.new_regime.surcharge > 0

    def test_unknown_ay_rejected(self):
        from app.core.errors import ValidationError

        with pytest.raises(ValidationError):
            compare_regimes(TaxInput(assessment_year="1999-00", basic_salary=1_000_000))


class TestHra:
    def test_metro_minimum_of_three(self):
        # min(HRA 300000, rent - 10% basic = 240000 - 100000 = 140000, 50% basic = 500000)
        assert hra_exemption(1_000_000, 300_000, 240_000, metro=True) == 140_000

    def test_no_rent_no_exemption(self):
        assert hra_exemption(1_000_000, 300_000, 0, metro=True) == 0


class TestCapitalGains:
    def test_stcg_and_ltcg_split(self):
        result = compute_equity_gains(
            [
                SellLot(
                    quantity=100, buy_price=100, sell_price=150,
                    buy_date="2025-01-01", sell_date="2025-06-01",
                ),
                SellLot(
                    quantity=100, buy_price=100, sell_price=200,
                    buy_date="2023-01-01", sell_date="2025-06-01",
                ),
            ]
        )
        assert result.stcg == 5_000
        assert result.ltcg == 10_000
        # LTCG below the 1.25L exemption.
        assert result.ltcg_tax == 0
        assert result.stcg_tax == pytest.approx(1_000)

    def test_ltcg_exemption_and_rate(self):
        result = compute_equity_gains(
            [
                SellLot(
                    quantity=1000, buy_price=100, sell_price=400,
                    buy_date="2022-01-01", sell_date="2025-06-01",
                )
            ]
        )
        assert result.ltcg == 300_000
        assert result.ltcg_taxable == 175_000
        assert result.ltcg_tax == pytest.approx(21_875)

    def test_grandfathering_uses_fmv(self):
        result = compute_equity_gains(
            [
                SellLot(
                    quantity=100, buy_price=50, sell_price=300,
                    buy_date="2016-01-01", sell_date="2025-06-01",
                    fmv_2018_01_31=200,
                )
            ]
        )
        # Cost steps up to FMV 200, gain is 100 per share.
        assert result.ltcg == 10_000


class TestSip:
    def test_formula(self):
        # FV of 10000/month at 12% for 10 years is about 23.0 lakh.
        sip = required_monthly_sip(2_300_000, 10, 0.12)
        assert sip == pytest.approx(10_000, rel=0.01)

    def test_zero_return(self):
        assert required_monthly_sip(120_000, 1, 0.0) == pytest.approx(10_000)

    def test_step_up_needs_less_up_front(self):
        flat = required_monthly_sip(5_000_000, 15, 0.12)
        stepped = step_up_sip_first_month(5_000_000, 15, 0.12, 0.10)
        assert stepped < flat


class TestAffordability:
    def test_emi_formula(self):
        # 50L at 9% for 20 years is about 44986/month.
        assert emi(5_000_000, 0.09, 20) == pytest.approx(44_986, rel=0.001)

    def test_foir_gate(self):
        result = affordability(
            AffordabilityInput(
                purchase_cost=8_000_000, down_payment=1_500_000, loan_rate=0.09,
                loan_years=20, monthly_income=100_000, existing_emi=10_000,
                liquid_savings=2_500_000, monthly_expenses=40_000,
            )
        )
        assert result.foir > 0.50
        assert not result.affordable

    def test_affordable_case(self):
        result = affordability(
            AffordabilityInput(
                purchase_cost=6_000_000, down_payment=2_000_000, loan_rate=0.085,
                loan_years=20, monthly_income=250_000, existing_emi=0,
                liquid_savings=3_500_000, monthly_expenses=80_000,
            )
        )
        assert result.foir_band_ok
        assert result.affordable


class TestMonteCarlo:
    def test_seeded_and_ordered(self):
        a = monte_carlo_sip(10_000, 10, 0.12, 0.18, paths=500, rng_seed=42)
        b = monte_carlo_sip(10_000, 10, 0.12, 0.18, paths=500, rng_seed=42)
        assert a == b
        assert a.p10 < a.p50 < a.p90
