from google.adk.agents import Agent
from .prompt import GET_ORDERS_PROMPT
from .get_all_orders_tool import get_all_orders_for_symbol


get_all_orders_agent = Agent(
    name="get_all_orders_agent",
    model="gemini-2.0-flash",
    description="Retrieves and summarizes user trading orders.",
    instruction=GET_ORDERS_PROMPT,
    tools=[get_all_orders_for_symbol],
    output_key="view_orders_response"
)