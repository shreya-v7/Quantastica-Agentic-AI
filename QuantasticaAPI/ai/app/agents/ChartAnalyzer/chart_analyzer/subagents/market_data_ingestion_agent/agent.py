from google.adk.agents import Agent
from pywin.framework.toolmenu import tools
from ...tools.market_data_fetcher import fetch_stock_data
from .prompt import market_data_ingestion_prompt

market_data_ingestion_agent = Agent(
    name="market_data_ingestion",
    model="gemini-2.0-flash",
    description="Fetches historical and real-time market data for a given financial entity.",
    instruction=market_data_ingestion_prompt,
    # The output of this agent will be stored in the in-memory service
    # under the key 'market_data'.
    tools=[fetch_stock_data],
    output_key="market_data",
)
