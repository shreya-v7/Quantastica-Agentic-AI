from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .subagents.market_data_ingestion_agent.agent import market_data_ingestion_agent
from .subagents.trend_analysis_agent.agent import trend_analysis_agent
from .subagents.scenario_simulation_agent.agent import scenario_simulation_agent
from .subagents.visualization_agent.agent import visualization_agent
from .prompt import chart_analyzer_instruction


root_agent = Agent(
    name="chart_analyzer_agent",
    model="gemini-2.0-flash",
    description="Analyzes market data, identifies trends, simulates scenarios, and visualizes outcomes for a financial entity.",
    instruction=chart_analyzer_instruction,
    tools=[
        AgentTool(agent=market_data_ingestion_agent),
        AgentTool(agent=trend_analysis_agent),
        AgentTool(agent=scenario_simulation_agent),
        AgentTool(agent=visualization_agent),
    ],
)
