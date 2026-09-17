"""MCP tool implementations. Pure functions so they can be unit tested without stdio."""

from app.calculators.planning import AffordabilityInput, affordability, required_monthly_sip
from app.calculators.tax import TaxInput, compare_regimes

DISCLAIMER = "Not investment advice, for informational purposes only."


def compare_tax_regimes(
    basic_salary: float,
    hra_received: float = 0,
    rent_paid: float = 0,
    deduction_80c: float = 0,
    metro_city: bool = True,
    assessment_year: str = "2025-26",
) -> dict:
    result = compare_regimes(
        TaxInput(
            assessment_year=assessment_year,
            basic_salary=basic_salary,
            hra_received=hra_received,
            rent_paid=rent_paid,
            deduction_80c=deduction_80c,
            metro_city=metro_city,
        )
    )
    payload = result.model_dump(by_alias=True)
    payload["disclaimer"] = DISCLAIMER
    return payload


def required_sip(target_inr: float, years: float, annual_return: float = 0.12) -> dict:
    sip = required_monthly_sip(target_inr, years, annual_return)
    return {
        "targetInr": target_inr,
        "years": years,
        "annualReturn": annual_return,
        "monthlySip": round(sip, 2),
        "disclaimer": DISCLAIMER,
    }


def affordability_check(
    purchase_cost: float,
    down_payment: float,
    loan_rate: float,
    loan_years: float,
    monthly_income: float,
    liquid_savings: float,
    existing_emi: float = 0,
    monthly_expenses: float = 0,
) -> dict:
    result = affordability(
        AffordabilityInput(
            purchase_cost=purchase_cost,
            down_payment=down_payment,
            loan_rate=loan_rate,
            loan_years=loan_years,
            monthly_income=monthly_income,
            existing_emi=existing_emi,
            liquid_savings=liquid_savings,
            monthly_expenses=monthly_expenses,
        )
    )
    payload = result.model_dump(by_alias=True)
    payload["disclaimer"] = DISCLAIMER
    return payload


def _mock_bank():
    from app.providers.bank.mock import MockNorthstarBank

    return MockNorthstarBank()


def bank_list_customers() -> dict:
    bank = _mock_bank()
    return {
        "bank": bank.status(),
        "customers": bank.list_customers(),
        "disclaimer": DISCLAIMER,
    }


def bank_customer_snapshot(customer_id: str) -> dict:
    return _mock_bank().snapshot(customer_id)


def bank_holdings(customer_id: str) -> dict:
    rows = _mock_bank().holdings(customer_id)
    return {
        "customerId": customer_id,
        "holdings": rows,
        "mock": True,
        "disclaimer": DISCLAIMER,
    }
