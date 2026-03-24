from google.adk.agents import Agent
from .prompt import UPDATE_ORDER_PROMPT
from .update_order_tool import update_order

update_order_agent = Agent(
    name="update_order_agent",
    model="gemini-2.0-flash",
    description="Updates trading orders as instructed like updating quantity, price, etc.",
    instruction=UPDATE_ORDER_PROMPT,
    tools=[update_order],
    output_key="update_order_response"
)