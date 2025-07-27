from google.adk.agents import Agent
# from google.adk.tools import Tool
from .prompt import NET_WORTH_TRACKER_PROMPT
import json,os
from datetime import datetime

test_data_dir = os.path.join(os.path.dirname(__file__),'..','..', 'test_data_dir')
def load_json(filename):
    with open(os.path.join(test_data_dir, filename), 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_net_worth_from_files(user_ph: str) -> str:
    """
    Calculates a user's net worth from various financial data files.

    Args:
        fetch_net_worth_json: JSON string of net worth summary.
        fetch_epf_details_json: JSON string of EPF details.
        fetch_credit_report_json: JSON string of the user's credit report.
        fetch_bank_transactions_json: JSON string of bank transactions.
        fetch_mf_transactions_json: JSON string of mutual fund transactions.
        fetch_stock_transactions_json: JSON string of stock transactions.

    Returns:
        A JSON string summarizing the net worth analysis.
    """
    net_worth_data = load_json(f'{user_ph}/fetch_net_worth.json')
    epf_data = load_json(f'{user_ph}/fetch_epf_details.json')
    credit_data = load_json(f'{user_ph}/fetch_credit_report.json')

    # Primary data from fetch_net_worth.json
    net_worth_response = net_worth_data.get("netWorthResponse", {})
    total_net_worth = net_worth_response.get("totalNetWorthValue", {}).get("units", "0")
    asset_values = net_worth_response.get("assetValues", [])
    liability_values = net_worth_response.get("liabilityValues", [])

    total_assets = sum(int(a.get("value", {}).get("units", 0)) for a in asset_values)
    total_liabilities = sum(int(l.get("value", {}).get("units", 0)) for l in liability_values)

    # Detailed breakdowns
    asset_breakdown = [
        {item.get("netWorthAttribute"): f'₹{int(item.get("value", {}).get("units", 0)):,}'}
        for item in asset_values
    ]
    liability_breakdown = [
        {item.get("netWorthAttribute"): f'₹{int(item.get("value", {}).get("units", 0)):,}'}
        for item in liability_values
    ]

    # EPF Details from fetch_epf_details.json
    overall_pf_balance = epf_data.get("uanAccounts", [{}])[0].get("rawDetails", {}).get("overall_pf_balance", {})
    epf_summary = {
        "Current PF Balance": f'₹{int(overall_pf_balance.get("current_pf_balance", 0)):,}',
        "Pension Balance": f'₹{int(overall_pf_balance.get("pension_balance", 0)):,}',
        "Total Employee Share": f'₹{int(overall_pf_balance.get("employee_share_total", {}).get("balance", 0)):,}'
    }

    # Credit report details from fetch_credit_report.json
    credit_summary = credit_data.get("creditReports", [{}])[0].get("creditReportData", {}).get("creditAccount", {}).get("creditAccountSummary", {})
    outstanding_balance = credit_summary.get("totalOutstandingBalance", {})
    credit_report_summary = {
        "Total Outstanding Balance": f'₹{int(outstanding_balance.get("outstandingBalanceAll", 0)):,}',
        "Secured Outstanding Balance": f'₹{int(outstanding_balance.get("outstandingBalanceSecured", 0)):,}',
        "Unsecured Outstanding Balance": f'₹{int(outstanding_balance.get("outstandingBalanceUnSecured", 0)):,}'
    }

    report = {
        f"Net Worth Report as of {datetime.now().strftime('%Y-%m-%d')}": {
            "Overall Summary": {
                "Total Assets": f"₹{total_assets:,}",
                "Total Liabilities": f"₹{total_liabilities:,}",
                "Total Net Worth": f"₹{int(total_net_worth):,}"
            },
            "Asset Breakdown": asset_breakdown,
            "Liability Breakdown": liability_breakdown,
            "EPF Details": epf_summary,
            "Credit Account Details": credit_report_summary
        }
    }
    return json.dumps(report, indent=2)




net_worth_tracker_agent = Agent(
    name="net_worth_tracker_agent",
    model="gemini-2.0-flash",
    description="Calculates and tracks user's net worth using detailed financial files.",
    instruction=NET_WORTH_TRACKER_PROMPT,
    tools=[calculate_net_worth_from_files],
    output_key="net_worth_analysis_results"
)