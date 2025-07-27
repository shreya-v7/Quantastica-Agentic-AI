from google.adk.agents import Agent
from .prompt import PERSONAL_FINANCE_PROMPT
from ...data_fetcher import fetch_all_financial_data

personal_finance_agent = Agent(
    name="personal_finance_agent",
    model="gemini-2.0-flash",
    description="A comprehensive agent that analyzes a user's entire financial situation, from debt and transactions to investments and long-term goals.",
    instruction=PERSONAL_FINANCE_PROMPT,
    # This agent needs the tool to fetch the user's data
    tools=[fetch_all_financial_data],
    output_key="personal_finance_analysis"
)
