from google.adk.agents import Agent
from .prompt import scenario_simulation_prompt

scenario_simulation_agent = Agent(
    name="scenario_simulation",
    model="gemini-2.0-flash",
    description="Simulates hypothetical investment scenarios based on historical data.",
    instruction=scenario_simulation_prompt,
    # The output of this agent will be stored in the in-memory service
    # under the key 'simulation_results'.
    output_key="simulation_results",
)
