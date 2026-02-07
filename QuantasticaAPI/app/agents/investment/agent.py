from google.adk.agents import Agent
from .prompt import MASTER_ORCHESTRATOR_PROMPT
# Import the two main agents
from .subagents.personal_finance_agent.agent import personal_finance_agent
from .subagents.market_analysis_agent.agent import market_analysis_agent

root_agent = Agent(
    name="master_orchestrator",
    model="gemini-2.0-flash",
    description="Coordinates a personal finance agent and a market analysis agent to create a holistic financial plan.",
    instruction=MASTER_ORCHESTRATOR_PROMPT,
    # This agent has no tools, only sub-agents
    sub_agents=[
        personal_finance_agent,
        market_analysis_agent
    ],
    output_key="final_investment_advice"
)
