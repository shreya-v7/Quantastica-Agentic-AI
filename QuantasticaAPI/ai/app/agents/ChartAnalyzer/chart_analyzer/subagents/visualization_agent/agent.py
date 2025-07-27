from google.adk.agents import Agent
from .prompt import visualization_prompt

visualization_agent = Agent(
    name="visualization",
    model="gemini-2.0-flash",
    description="Generates visualizations and charts for market data and analysis.",
    instruction=visualization_prompt,
)