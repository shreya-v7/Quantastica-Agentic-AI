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
from .prompt import LOAN_ADVISOR_PROMPT
import json
import os
import random

def get_eligible_options(user_ph: str, product_type: str) -> str:
    """
    Generates 50 mock product options, fetches the user's credit score from a file,
    prints the score, and returns a list of options for which the user is eligible.

    Args:
        user_ph: The user's identifier (phone number).
        product_type: The type of product, either "loan" or "insurance".

    Returns:
        A JSON string of eligible product options.
    """
    # --- 1. Generate Mock Data ---
    mock_data = []
    if "loan" in product_type.lower():
        providers = ["National Bank", "City Finance", "Home Lenders Inc.", "Secure Credit", "People's Bank"]
        for i in range(50):
            mock_data.append({
                "provider": f"{random.choice(providers)} #{i+1}",
                "product_name": f"{random.choice(['Personal', 'Home', 'Car'])} Loan",
                "interest_rate": f"{random.uniform(8.5, 18.0):.2f}%",
                "max_term_months": random.choice([60, 84, 120, 240, 360]),
                "min_eligibility_score": random.randint(680, 780),
            })
    elif "insurance" in product_type.lower():
        providers = ["SecureLife Insurance", "General Health Co.", "SafeGuard Plus", "Family First Assurance"]
        for i in range(50):
            mock_data.append({
                "provider": f"{random.choice(providers)} #{i+1}",
                "plan_name": f"{random.choice(['Gold', 'Silver', 'Bronze'])} Health Shield",
                "sum_insured": f"{random.choice([5, 10, 15, 20, 50])} Lakhs",
                "annual_premium": f"₹{random.randint(12000, 35000):,}",
                "min_eligibility_score": random.randint(680, 780)
            })

    # --- 2. Fetch Credit Score ---
    # Construct the path relative to the current agent.py file
    current_dir = os.path.dirname(__file__)
    test_data_dir = os.path.abspath(os.path.join(current_dir,'test_data_dir'))
    credit_report_path = os.path.join(test_data_dir, user_ph, 'fetch_credit_report.json')

    user_credit_score = 0
    try:
        with open(credit_report_path, 'r', encoding='utf-8') as f:
            credit_data = json.load(f)
        user_credit_score = int(credit_data["creditReports"][0]["creditReportData"]["score"]["bureauScore"])
    except (FileNotFoundError, json.JSONDecodeError, KeyError, IndexError, ValueError, TypeError) as e:
        print(f"Error fetching credit score: {e}")
        user_credit_score = 0 # Default to 0 if any error occurs

    # --- 3. Print Credit Score ---
    print(f"User's Credit Score: {user_credit_score}")

    # --- 4. Filter for Eligibility ---
    eligible_products = []
    if "loan" in product_type.lower():
        for product in mock_data:
            min_score_required = product.get("min_eligibility_score", 0)
            if user_credit_score >= min_score_required:
                eligible_products.append(product)
    else:
        # For insurance, all mock options are considered eligible
        eligible_products = mock_data

    return json.dumps(eligible_products, indent=2)

def get_credit_score(user_ph: str) -> str:
    """
    Fetches the user's credit score from a file and returns it.

    Args:
        user_ph: The user's identifier (phone number).

    Returns:
        A JSON string containing the user's credit score.
    """
    # Construct the path relative to the current agent.py file
    current_dir = os.path.dirname(__file__)
    test_data_dir = os.path.abspath(os.path.join(current_dir,'test_data_dir'))
    credit_report_path = os.path.join(test_data_dir, user_ph, 'fetch_credit_report.json')

    try:
        with open(credit_report_path, 'r', encoding='utf-8') as f:
            credit_data = json.load(f)
        user_credit_score = int(credit_data["creditReports"][0]["creditReportData"]["score"]["bureauScore"])
        return json.dumps({"credit_score": user_credit_score})
    except (FileNotFoundError, json.JSONDecodeError, KeyError, IndexError, ValueError, TypeError) as e:
        return json.dumps({"error": f"Failed to fetch credit score: {e}"})

# The main agent for this simplified team
root_agent = Agent(
    name="loan_advisor_agent",
    model="gemini-2.0-flash",
    description="Provides a list of eligible loan or insurance options based on a user's credit score.",
    instruction=LOAN_ADVISOR_PROMPT,
    tools=[get_eligible_options,get_credit_score],
    output_key="eligible_options"
)