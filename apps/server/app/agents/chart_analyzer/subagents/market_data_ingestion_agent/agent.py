from google.adk.agents import Agent
from ...tools.market_data_fetcher import fetch_stock_data
from .prompt import market_data_ingestion_prompt

market_data_ingestion_agent = Agent(
    name="market_data_ingestion",
    model="gemini-2.0-flash",
    description="Fetches historical and real-time market data for a given financial entity.",
    instruction=market_data_ingestion_prompt,
    tools=[fetch_stock_data],
    output_key="market_data",
)
