from google.adk.agents import Agent
from .prompt import CONVERSATION_PROMPT
from .subagents.net_worth_tracker_agent.agent import net_worth_tracker_agent
from .subagents.affordability_analysis_agent.agent import affordability_analysis_agent
from .subagents.goal_progress_agent.agent import goal_progress_agent

conversation_agent = Agent(
    name="conversation_agent",
    model="gemini-2.0-flash",
    description="Handles natural language queries and delegates to other financial agents.",
    instruction=CONVERSATION_PROMPT,
    sub_agents=[net_worth_tracker_agent, affordability_analysis_agent, goal_progress_agent],
    output_key="conversational_response"
)
root_agent=conversation_agent