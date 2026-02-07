from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from .prompt import news_fetcher_prompt

# Define the news fetcher agent
news_fetcher_agent = LlmAgent(
    name="news_fetcher_agent",
    model="gemini-2.0-flash",
    description="Fetches news articles for a specific financial entity.",
    instruction=news_fetcher_prompt,
    tools=[google_search],
)
