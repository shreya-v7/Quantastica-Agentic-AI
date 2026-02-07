from google.adk.agents import Agent
from .prompt import PLACE_ORDER_PROMPT
from .place_order_tool import place_order

place_order_agent = Agent(
    name="place_order_agent",
    model="gemini-2.0-flash",
    description="Places trading orders as instructed like BUY, SELL etc",
    instruction=PLACE_ORDER_PROMPT,
    tools=[place_order],
    output_key="place_order_response"
)