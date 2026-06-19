"""Assembles the FinancialProfile read model and computes net worth.

Net worth blends the profile balances (cash, deposits, retirement) with the live equity
value of the user's portfolios, less outstanding debt. The aggregate is also the source
the tax engine and the chat researcher read profile slices from.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.india.format import format_inr_compact
from app.infra.factory import Container
from app.infra.repo.profile_repo import ProfileRepository
from app.schemas.profile import (
    CashAccount,
    Debt,
    Deposit,
    Expense,
    FinancialProfile,
    Goal,
    IncomeProfile,
    InsurancePolicy,
    MfFolio,
    NetWorth,
    RetirementAccount,
)

if TYPE_CHECKING:
    from app.calculators.tax import TaxInput


class ProfileService:
    def __init__(self, container: Container):
        self._c = container
        self._repo = ProfileRepository(container.session_factory)

    async def income(self, user_id: str) -> IncomeProfile:
        row = await self._repo.get_income(user_id)
        if row is None:
            return IncomeProfile()
        return IncomeProfile(
            basic_salary=row.basic_salary,
            hra_received=row.hra_received,
            special_allowance=row.special_allowance,
            other_income=row.other_income,
            rent_paid=row.rent_paid,
            metro=row.metro,
        )

    async def set_income(self, user_id: str, income: IncomeProfile) -> IncomeProfile:
        await self._repo.upsert_income(user_id, income.model_dump())
        return income

    async def get_profile(self, user_id: str) -> FinancialProfile:
        income = await self.income(user_id)
        cash = [
            CashAccount(id=r.id, name=r.name, institution=r.institution, balance_inr=r.balance_inr)
            for r in await self._repo.list_all(user_id, "cash_accounts")
        ]
        deposits = [
            Deposit(
                id=r.id, kind=r.kind, institution=r.institution, principal_inr=r.principal_inr,
                rate=r.rate, maturity_date=r.maturity_date,
            )
            for r in await self._repo.list_all(user_id, "deposits")
        ]
        retirement = [
            RetirementAccount(
                id=r.id, kind=r.kind, balance_inr=r.balance_inr,
                annual_contribution_inr=r.annual_contribution_inr,
            )
            for r in await self._repo.list_all(user_id, "retirement_accounts")
        ]
        folios = [
            MfFolio(
                id=r.id, scheme_code=r.scheme_code, scheme_name=r.scheme_name,
                units=float(r.units), sip_amount_inr=r.sip_amount_inr, sip_day=r.sip_day,
            )
            for r in await self._repo.list_all(user_id, "mf_folios")
        ]
        debts = [
            Debt(
                id=r.id, loan_type=r.loan_type, lender=r.lender,
                principal_outstanding_inr=r.principal_outstanding_inr, rate=r.rate,
                emi_inr=r.emi_inr, tenure_months=r.tenure_months,
                annual_interest_inr=r.annual_interest_inr,
            )
            for r in await self._repo.list_all(user_id, "debts")
        ]
        insurance = [
            InsurancePolicy(
                id=r.id, policy_type=r.policy_type, provider=r.provider, cover_inr=r.cover_inr,
                annual_premium_inr=r.annual_premium_inr, term_years=r.term_years,
            )
            for r in await self._repo.list_all(user_id, "insurance_policies")
        ]
        expenses = [
            Expense(id=r.id, category=r.category, monthly_inr=r.monthly_inr)
            for r in await self._repo.list_all(user_id, "expenses")
        ]
        goals = [
            Goal(
                id=r.id, name=r.name, target_inr=r.target_inr, target_date=r.target_date,
                priority=r.priority, saved_inr=r.saved_inr,
                progress=min(1.0, r.saved_inr / r.target_inr) if r.target_inr else 0.0,
            )
            for r in await self._repo.list_all(user_id, "goals")
        ]

        equity_value = await self._equity_value(user_id)
        assets = (
            sum(c.balance_inr for c in cash)
            + sum(d.principal_inr for d in deposits)
            + sum(a.balance_inr for a in retirement)
            + equity_value
        )
        liabilities = sum(d.principal_outstanding_inr for d in debts)
        net = assets - liabilities
        net_worth = NetWorth(
            assets_inr=round(assets, 2),
            liabilities_inr=round(liabilities, 2),
            net_worth_inr=round(net, 2),
            net_worth_display=format_inr_compact(net),
        )

        return FinancialProfile(
            user_id=user_id,
            income=income,
            cash_accounts=cash,
            deposits=deposits,
            retirement_accounts=retirement,
            mf_folios=folios,
            debts=debts,
            insurance_policies=insurance,
            expenses=expenses,
            goals=goals,
            net_worth=net_worth,
        )

    async def build_tax_input(self, user_id: str) -> TaxInput:
        """Derive the tax engine input from stored profile slices: 80C from EPF/PPF
        contributions plus life/endowment premiums, 80CCD(1B) from NPS, 80D from health
        premiums, and 24(b) home loan interest from debts."""
        from app.calculators.tax import TaxInput

        profile = await self.get_profile(user_id)
        retirement = profile.retirement_accounts
        epf_ppf = sum(a.annual_contribution_inr for a in retirement if a.kind in ("epf", "ppf"))
        nps = sum(a.annual_contribution_inr for a in retirement if a.kind == "nps")
        life_premiums = sum(
            p.annual_premium_inr
            for p in profile.insurance_policies
            if p.policy_type in ("term", "endowment", "ulip")
        )
        health_premiums = sum(
            p.annual_premium_inr for p in profile.insurance_policies if p.policy_type == "health"
        )
        home_interest = sum(
            d.annual_interest_inr for d in profile.debts if d.loan_type == "home"
        )
        return TaxInput(
            basic_salary=profile.income.basic_salary,
            hra_received=profile.income.hra_received,
            other_income=profile.income.special_allowance + profile.income.other_income,
            rent_paid=profile.income.rent_paid,
            metro_city=profile.income.metro,
            deduction_80c=epf_ppf + life_premiums,
            health_premium_self=health_premiums,
            nps_80ccd_1b=nps,
            home_loan_interest=home_interest,
        )

    async def affordability_context(self, user_id: str) -> dict:
        """Profile-derived defaults for the affordability calculator."""
        profile = await self.get_profile(user_id)
        monthly_income = (
            profile.income.basic_salary
            + profile.income.hra_received
            + profile.income.special_allowance
            + profile.income.other_income
        ) / 12
        return {
            "monthlyIncome": round(monthly_income, 2),
            "existingEmi": round(sum(d.emi_inr for d in profile.debts), 2),
            "liquidSavings": round(
                sum(c.balance_inr for c in profile.cash_accounts)
                + sum(d.principal_inr for d in profile.deposits),
                2,
            ),
            "monthlyExpenses": round(sum(e.monthly_inr for e in profile.expenses), 2),
        }

    async def _equity_value(self, user_id: str) -> float:
        repo = self._c.repository
        total = 0.0
        for portfolio in await repo.list_portfolios(user_id):
            for holding in await repo.holdings_for(user_id, portfolio.id):
                total += float(holding.quantity) * float(holding.current_price)
        return total
