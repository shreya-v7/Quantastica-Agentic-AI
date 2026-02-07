from google.adk.agents import Agent
from .prompt import trend_analysis_prompt
from ...tools.market_data_fetcher import calculate_indicators_and_risk
trend_analysis_agent = Agent(
    name="trend_analysis",
    model="gemini-2.0-flash",
    description="Applies technical analysis to market data to find trends and patterns.",
    instruction=trend_analysis_prompt,
    tools=[calculate_indicators_and_risk],
    output_key="trend_analysis_results"
)
