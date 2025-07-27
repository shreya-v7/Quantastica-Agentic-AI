from google.adk.agents import Agent
from .prompt import AFFORDABILITY_ANALYSIS_PROMPT
import json
import os
from datetime import datetime

# Assume a directory structure where user data is stored in subfolders
# e.g., test_data_dir/user_phone_number/fetch_bank_transactions.json
test_data_dir = os.path.join(os.path.dirname(__file__),'..','..', 'test_data_dir')

def load_json(file_path: str) -> dict:
    """Loads a JSON file from the specified path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found at {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {file_path}")
        return {}

def calculate_affordability_from_files(user_ph: str, purchase_price: float, desired_loan_amount: float) -> str:
    """
    Determines affordability for a significant purchase by analyzing bank transactions and credit report.

    Args:
        user_ph: The user's identifier, used to locate their data directory.
        purchase_price: The total price of the purchase.
        desired_loan_amount: The desired loan amount.

    Returns:
        A JSON string summarizing the affordability analysis.
    """
    # Construct file paths
    bank_transactions_path = os.path.join(test_data_dir, user_ph, 'fetch_bank_transactions.json')
    credit_report_path = os.path.join(test_data_dir, user_ph, 'fetch_credit_report.json')

    # Load the financial data
    bank_data = load_json(bank_transactions_path)
    credit_data = load_json(credit_report_path)

    # --- Analysis Logic ---

    # 1. Estimate monthly income from bank transactions
    monthly_income = 0
    income_narrations = ["SALARY", "NEFT CR"]
    if bank_data and "bankTransactions" in bank_data:
        credits = []
        for bank in bank_data["bankTransactions"]:
            for txn in bank.get("txns", []):
                # txn schema: [amount, narration, date, type(1:CREDIT), mode, balance]
                narration = txn[1]
                txn_type = txn[3]
                if txn_type == 1 and any(keyword in narration for keyword in income_narrations):
                    credits.append(float(txn[0]))
        if credits:
            # Simple average, assuming the data covers a couple of months
            monthly_income = sum(credits) / len(credits) if len(credits) > 0 else 0


    # 2. Get total existing debt from credit report
    total_outstanding_debt = 0
    if credit_data:
        try:
            summary = credit_data["creditReports"][0]["creditReportData"]["creditAccount"]["creditAccountSummary"]
            total_outstanding_debt = float(summary["totalOutstandingBalance"]["outstandingBalanceAll"])
        except (KeyError, IndexError):
            total_outstanding_debt = 0 # Default if structure is not as expected

    # 3. Calculate estimated EMI for the new loan
    # Assumptions: 20-year (240 months) loan at 8.5% p.a. interest.
    interest_rate_monthly = 0.085 / 12
    tenure_months = 240
    if desired_loan_amount > 0 and interest_rate_monthly > 0:
        # Standard EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
        r_plus_1_pow_n = (1 + interest_rate_monthly) ** tenure_months
        estimated_emi = (desired_loan_amount * interest_rate_monthly * r_plus_1_pow_n) / (r_plus_1_pow_n - 1)
    else:
        estimated_emi = 0

    # 4. Determine affordability
    # Rule: New EMI should not exceed 40% of estimated monthly income.
    affordability = "Not Recommended"
    recommendation_text = "Could not determine affordability due to insufficient income data."
    if monthly_income > 0:
        max_permissible_emi = monthly_income * 0.40
        if estimated_emi <= max_permissible_emi:
            affordability = "Affordable"
            recommendation_text = (f"Based on an estimated monthly income of ₹{monthly_income:,.2f}, this loan appears affordable. "
                                   f"Your existing outstanding debt is ₹{total_outstanding_debt:,.2f}.")
        elif estimated_emi <= max_permissible_emi * 1.25: # Up to 50% of income
             affordability = "Manageable with a tight budget"
             recommendation_text = (f"This loan would consume a significant portion of your estimated monthly income of ₹{monthly_income:,.2f}, "
                                    f"making your budget tight. Your existing outstanding debt is ₹{total_outstanding_debt:,.2f}.")
        else:
            affordability = "Not Recommended"
            recommendation_text = (f"The estimated EMI of ₹{estimated_emi:,.2f} is high compared to your estimated monthly income of ₹{monthly_income:,.2f}. "
                                   "This loan is not recommended as it would likely strain your finances.")

    # --- Build Report ---
    report = {
        "Affordability Analysis Report": {
            "Purchase Details": {
                "Purchase Price": f"₹{purchase_price:,.2f}",
                "Desired Loan Amount": f"₹{desired_loan_amount:,.2f}"
            },
            "Affordability Assessment": {
                "Affordability": affordability,
                "Recommendation": recommendation_text
            },
            "Estimated Loan Terms": {
                "Estimated EMI": f"₹{estimated_emi:,.2f}",
                "Notes": "Assumes a 20-year loan tenure at an interest rate of 8.5% p.a. Income is estimated from salary credits in bank transactions."
            }
        }
    }
    return json.dumps(report, indent=2)



# Create the Agent instance
affordability_analysis_agent = Agent(
    name="affordability_analysis_agent",
    model="gemini-2.0-flash",
    description="Determines user's affordability for significant purchases like home loans by analyzing financial files.",
    instruction=AFFORDABILITY_ANALYSIS_PROMPT,
    tools=[calculate_affordability_from_files],
    output_key="affordability_analysis_results"
)