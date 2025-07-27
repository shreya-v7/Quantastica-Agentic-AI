from google.adk.agents import Agent
from .prompt import TAX_OPTIMIZATION_PROMPT
import json

def suggest_tax_saving_strategies(user_data):
    income = user_data.get("GrossIncome", 0)
    epf = user_data.get("EPF", 0)
    insurance = user_data.get("Insurance", 0)
    other = user_data.get("Other", 0)
    total_80C = min(epf + insurance + other, 150000)

    def old_regime_tax(income, deductions):
        taxable = income - deductions
        if taxable <= 250000: return 0
        elif taxable <= 500000: return 0.05 * (taxable - 250000)
        elif taxable <= 1000000: return 12500 + 0.2 * (taxable - 500000)
        else: return 112500 + 0.3 * (taxable - 1000000)

    def new_regime_tax(income):
        slabs = [(300000, 0), (600000, 0.05), (900000, 0.1), (1200000, 0.15), (1500000, 0.2)]
        tax = 0
        last = 0
        for limit, rate in slabs:
            if income > limit:
                tax += (limit - last) * rate
                last = limit
            else:
                tax += (income - last) * rate
                return tax
        if income > 1500000:
            tax += (income - 1500000) * 0.3
        return tax

    old_tax = old_regime_tax(income, total_80C)
    new_tax = new_regime_tax(income)
    better = "Old Regime" if old_tax < new_tax else "New Regime"

    return json.dumps({
        "Gross Income": income,
        "80C Deduction": total_80C,
        "Old Regime Tax": old_tax,
        "New Regime Tax": new_tax,
        "Recommended Regime": better
    }, indent=2)

tax_optimization_agent = Agent(
    name="tax_optimization_agent",
    model="gemini-2.0-pro",
    description="Compares new vs old regime and gives tax-saving advice.",
    instruction=TAX_OPTIMIZATION_PROMPT,
    tools=[suggest_tax_saving_strategies],
    output_key="tax_optimization_summary"
)