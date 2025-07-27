from google.adk.agents import Agent
from .prompt import CANCEL_ORDER_PROMPT
from .cancel_order_tool import cancel_order_flow

cancel_order_agent = Agent(
    name="cancel_order_agent",
    model="gemini-2.0-flash",
    description="Cancels trading orders as instructed. An order id is passed and that trade will be cancelled",
    instruction=CANCEL_ORDER_PROMPT,
    tools=[cancel_order_flow],
    output_key="cancel_order_response"
)