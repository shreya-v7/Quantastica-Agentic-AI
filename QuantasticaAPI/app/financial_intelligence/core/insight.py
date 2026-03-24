from app.financial_intelligence.core.types import FinancialSnapshot


def generate_insights(data: FinancialSnapshot) -> dict:
    total_investments = sum(item.value for item in data.investments)
    total_liabilities = sum(item.amount for item in data.liabilities)
    net_worth = data.balance + total_investments - total_liabilities

    return {
        "net_worth": net_worth,
        "risk_exposure": len(data.investments),
        "debt_load": total_liabilities,
    }
