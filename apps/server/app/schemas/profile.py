"""FinancialProfile schemas: the unified per-user picture of an Indian household's
finances. Sub-collections are created and deleted individually; the aggregate read model
is assembled by the service and feeds the tax engine and the chat researcher."""

from typing import Literal

from pydantic import Field

from app.schemas.base import Contract


class IncomeProfile(Contract):
    basic_salary: float = Field(default=0.0, ge=0)
    hra_received: float = Field(default=0.0, ge=0)
    special_allowance: float = Field(default=0.0, ge=0)
    other_income: float = Field(default=0.0, ge=0)
    rent_paid: float = Field(default=0.0, ge=0)
    metro: bool = False


class CashAccount(Contract):
    id: str
    name: str
    institution: str
    balance_inr: float


class CreateCashAccount(Contract):
    name: str = Field(min_length=1, max_length=128)
    institution: str = Field(min_length=1, max_length=128)
    balance_inr: float = Field(ge=0)


class Deposit(Contract):
    id: str
    kind: Literal["fd", "rd"]
    institution: str
    principal_inr: float
    rate: float
    maturity_date: str


class CreateDeposit(Contract):
    kind: Literal["fd", "rd"]
    institution: str = Field(min_length=1, max_length=128)
    principal_inr: float = Field(gt=0)
    rate: float = Field(ge=0, le=1)
    maturity_date: str


class RetirementAccount(Contract):
    id: str
    kind: Literal["epf", "ppf", "nps"]
    balance_inr: float
    annual_contribution_inr: float


class CreateRetirementAccount(Contract):
    kind: Literal["epf", "ppf", "nps"]
    balance_inr: float = Field(ge=0)
    annual_contribution_inr: float = Field(ge=0)


class MfFolio(Contract):
    id: str
    scheme_code: str
    scheme_name: str
    units: float
    sip_amount_inr: float
    sip_day: int


class CreateMfFolio(Contract):
    scheme_code: str = Field(min_length=1, max_length=16)
    scheme_name: str = Field(min_length=1, max_length=255)
    units: float = Field(ge=0)
    sip_amount_inr: float = Field(default=0.0, ge=0)
    sip_day: int = Field(default=0, ge=0, le=28)


class Debt(Contract):
    id: str
    loan_type: str
    lender: str
    principal_outstanding_inr: float
    rate: float
    emi_inr: float
    tenure_months: int
    annual_interest_inr: float


class CreateDebt(Contract):
    loan_type: Literal["home", "personal", "car", "education"]
    lender: str = Field(min_length=1, max_length=128)
    principal_outstanding_inr: float = Field(gt=0)
    rate: float = Field(ge=0, le=1)
    emi_inr: float = Field(gt=0)
    tenure_months: int = Field(gt=0)
    annual_interest_inr: float = Field(default=0.0, ge=0)


class InsurancePolicy(Contract):
    id: str
    policy_type: str
    provider: str
    cover_inr: float
    annual_premium_inr: float
    term_years: int


class CreateInsurancePolicy(Contract):
    policy_type: Literal["term", "health", "endowment", "ulip"]
    provider: str = Field(min_length=1, max_length=128)
    cover_inr: float = Field(gt=0)
    annual_premium_inr: float = Field(ge=0)
    term_years: int = Field(default=0, ge=0)


class Expense(Contract):
    id: str
    category: str
    monthly_inr: float


class CreateExpense(Contract):
    category: str = Field(min_length=1, max_length=64)
    monthly_inr: float = Field(ge=0)


class Goal(Contract):
    id: str
    name: str
    target_inr: float
    target_date: str
    priority: str
    saved_inr: float
    progress: float


class CreateGoal(Contract):
    name: str = Field(min_length=1, max_length=128)
    target_inr: float = Field(gt=0)
    target_date: str
    priority: Literal["high", "medium", "low"] = "medium"
    saved_inr: float = Field(default=0.0, ge=0)


class NetWorth(Contract):
    assets_inr: float
    liabilities_inr: float
    net_worth_inr: float
    net_worth_display: str


class FinancialProfile(Contract):
    user_id: str
    income: IncomeProfile
    cash_accounts: list[CashAccount]
    deposits: list[Deposit]
    retirement_accounts: list[RetirementAccount]
    mf_folios: list[MfFolio]
    debts: list[Debt]
    insurance_policies: list[InsurancePolicy]
    expenses: list[Expense]
    goals: list[Goal]
    net_worth: NetWorth
