from google.adk.agents import LlmAgent
from .prompt import MARKET_ANALYSIS_PROMPT
from google.adk.tools import google_search

market_analysis_agent = LlmAgent(
    name="market_analysis_agent",
    model="gemini-2.0-flash",
    description="Uses Google Search to analyze market trends for various sectors and suggests new investment opportunities.",
    instruction=MARKET_ANALYSIS_PROMPT,
    tools=[google_search],
    output_key="market_opportunities"
)
