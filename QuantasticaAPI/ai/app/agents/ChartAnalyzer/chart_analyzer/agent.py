from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from .subagents.market_data_ingestion_agent.agent import market_data_ingestion_agent
from .subagents.trend_analysis_agent.agent import trend_analysis_agent
from .subagents.scenario_simulation_agent.agent import scenario_simulation_agent
from .subagents.visualization_agent.agent import visualization_agent
from .prompt import chart_analyzer_instruction
from google.adk.runners import Runner
# Load environment variables from .env file.
# The ADK will automatically pick up the necessary credentials and settings.
load_dotenv()

# Instantiate the built-in in-memory service to be shared across agents
shared_memory_service = InMemoryMemoryService()
shared_session_service=InMemorySessionService()
# Define the root agent for the Chart Analyzer team using the new syntax
root_agent = Agent(
    name="chart_analyzer_agent",
    model="gemini-2.0-flash",
    description="Analyzes market data, identifies trends, simulates scenarios, and visualizes outcomes for a financial entity.",
    instruction=chart_analyzer_instruction,
    # Sub-agents are passed as a list of AgentTools
    tools=[
        AgentTool(agent=market_data_ingestion_agent),
        AgentTool(agent=trend_analysis_agent),
        AgentTool(agent=scenario_simulation_agent),
        AgentTool(agent=visualization_agent),
    ],
)
runner = Runner(
    # Start with the info capture agent
    agent=root_agent,
    app_name="chart_analyzer",
    session_service=shared_memory_service,
    memory_service=shared_memory_service # Provide the memory service to the Runner
)
