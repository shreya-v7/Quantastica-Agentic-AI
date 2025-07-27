from google.adk.agents import Agent
from .prompt import ANALYZE_INDICATORS_PROMPT
from .stock_loader import load_stock_data

indicator_analysis_agent = Agent(
    name="indicator_analysis_agent",
    model="gemini-2.0-flash",
    description="Analyzes technical indicators and recommends BUY/SELL/NEUTRAL.",
    instruction=ANALYZE_INDICATORS_PROMPT,
    tools=[load_stock_data],
    output_key="analysis_response"
)
root_agent=indicator_analysis_agent