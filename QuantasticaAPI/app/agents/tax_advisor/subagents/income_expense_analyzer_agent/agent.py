from google.adk.agents import Agent
from .prompt import INCOME_EXPENSE_PROMPT
import json

def analyze_transactions(transactions: list) -> str:
    summary = {
        "Salary": 0,
        "Rent": 0,
        "Investments": 0,
        "Other": 0
    }

    for txn in transactions:
        desc = txn.get("desc", "").lower()
        amt = txn.get("amount", 0)

        if "salary" in desc:
            summary["Salary"] += amt
        elif "rent" in desc:
            summary["Rent"] += amt
        elif "sip" in desc or "mutual" in desc:
            summary["Investments"] += amt
        else:
            summary["Other"] += amt

    return json.dumps(summary, indent=2)

income_expense_analyzer_agent = Agent(
    name="income_expense_analyzer_agent",
    model="gemini-2.0-flash",
    description="Analyzes transactions into tax-related buckets like salary, rent, SIP.",
    instruction=INCOME_EXPENSE_PROMPT,
    tools=[analyze_transactions],
    output_key="categorized_financial_data"
)
