# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from .prompt import GOAL_PROGRESS_PROMPT
import json
import os
from datetime import datetime

# Assume a directory structure where user data is stored in subfolders
# e.g., test_data_dir/user_phone_number/fetch_net_worth.json
test_data_dir = os.path.join(os.path.dirname(__file__), '..','..','test_data_dir')

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

def project_financial_goal(user_ph: str, target_age: int, goal_name: str = "Retirement") -> str:
    """
    Projects a user's future financial worth based on current data.

    Args:
        user_ph: The user's identifier to locate their data directory.
        target_age: The age at which to project the user's worth.
        goal_name: The name of the financial goal.

    Returns:
        A JSON string summarizing the financial projection.
    """
    # --- Construct file paths ---
    net_worth_path = os.path.join(test_data_dir, user_ph, 'fetch_net_worth.json')
    credit_report_path = os.path.join(test_data_dir, user_ph, 'fetch_credit_report.json')
    bank_transactions_path = os.path.join(test_data_dir, user_ph, 'fetch_bank_transactions.json')

    # --- Load Data ---
    net_worth_data = load_json(net_worth_path)
    credit_data = load_json(credit_report_path)
    bank_data = load_json(bank_transactions_path)

    # --- Analysis & Calculation ---

    # 1. Get current assets (Present Value - PV)
    total_assets = 0
    if net_worth_data:
        asset_values = net_worth_data.get("netWorthResponse", {}).get("assetValues", [])
        total_assets = sum(int(a.get("value", {}).get("units", 0)) for a in asset_values)

    # 2. Determine current age
    current_age = 0
    if credit_data:
        try:
            dob_str = credit_data["creditReports"][0]["creditReportData"]["currentApplication"]["currentApplicationDetails"]["currentApplicantDetails"]["dateOfBirthApplicant"]
            dob = datetime.strptime(dob_str, "%Y%m%d")
            today = datetime.today()
            current_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except (KeyError, IndexError, ValueError):
            current_age = 30 # Default if not found

    years_to_grow = target_age - current_age
    if years_to_grow < 0:
        return json.dumps({"error": "Target age must be in the future."})

    # 3. Estimate annual savings (Payment - PMT)
    monthly_income = 0
    monthly_expenses = 0
    if bank_data:
        credits = []
        debits = []
        for bank in bank_data.get("bankTransactions", []):
            for txn in bank.get("txns", []):
                # txn schema: [amount, narration, date, type(1:CREDIT, 2:DEBIT), ...]
                txn_type = txn[3]
                amount = float(txn[0])
                if txn_type == 1: # Credit
                    credits.append(amount)
                elif txn_type == 2: # Debit
                    debits.append(amount)
        # Simple average over the period covered by the data
        monthly_income = sum(credits) / 2 if len(credits) > 0 else 0
        monthly_expenses = sum(debits) / 2 if len(debits) > 0 else 0

    annual_savings = (monthly_income - monthly_expenses) * 12
    if annual_savings < 0:
        annual_savings = 0 # Assume no savings if expenses exceed income

    # 4. Project Future Value (FV)
    # FV = PV * (1+r)^n + PMT * [((1+r)^n - 1) / r]
    annual_growth_rate = 0.08  # Assume 8% annual return
    r = annual_growth_rate
    n = years_to_grow
    pv = total_assets
    pmt = annual_savings

    future_value_of_pv = pv * ((1 + r) ** n)
    future_value_of_pmt = pmt * ((((1 + r) ** n) - 1) / r) if r > 0 else pmt * n
    projected_net_worth = future_value_of_pv + future_value_of_pmt

    # --- Build Report ---
    report = {
        f"Financial Goal Projection: {goal_name}": {
            "Projection Summary": {
                "Target Age": target_age,
                "Projected Net Worth": f"₹{projected_net_worth:,.2f}",
                "Projection Date": datetime.now().strftime('%Y-%m-%d')
            },
            "Key Assumptions": {
                "Current Age": current_age,
                "Years to Grow": years_to_grow,
                "Current Assets (PV)": f"₹{pv:,.2f}",
                "Estimated Annual Savings (PMT)": f"₹{pmt:,.2f}",
                "Assumed Annual Growth Rate (r)": f"{r:.1%}"
            },
            "Suggestions & Next Steps": [
                "This projection is an estimate. Market conditions and changes in your savings habits will affect the outcome.",
                "To potentially increase this amount, consider exploring investment options with higher average returns, while being mindful of risk.",
                "Reviewing your monthly expenses to identify areas for increased savings can significantly boost your future net worth."
            ]
        }
    }
    return json.dumps(report, indent=2)




# Create the Agent instance
goal_progress_agent = Agent(
    name="goal_progress_agent",
    model="gemini-2.0-flash",
    description="Monitors and reports on progress towards financial goals by projecting future outcomes.",
    instruction=GOAL_PROGRESS_PROMPT,
    tools=[project_financial_goal],
    output_key="goal_projection_results"
)