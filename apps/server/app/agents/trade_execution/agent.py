from google.adk.agents import Agent
from .prompt import CONVERSATION_PROMPT
from .subagents.cancel_order_agent.agent import cancel_order_agent
from .subagents.place_order_agent.agent import place_order_agent
from .subagents.update_order_agent.agent import update_order_agent
from .subagents.get_all_orders_agent.agent import get_all_orders_agent
from .subagents.indicator_analysis_agent.agent import indicator_analysis_agent

conversation_agent = Agent(
    name="trade_execution_agent",
    model="gemini-2.0-flash",
    description="Handles natural language trading queries and delegates to order management subagents.",
    instruction=CONVERSATION_PROMPT,
    sub_agents=[cancel_order_agent, place_order_agent, update_order_agent,get_all_orders_agent,indicator_analysis_agent],
    output_key="conversational_response"
)
root_agent=conversation_agent