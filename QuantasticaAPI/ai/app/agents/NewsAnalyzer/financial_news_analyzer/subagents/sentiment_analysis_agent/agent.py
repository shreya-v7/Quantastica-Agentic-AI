# financial_news_analyzer/subagents/sentiment_analyzer/agent.py

from google.adk.agents import LlmAgent
from .prompt import sentiment_analyzer_prompt

# Define the sentiment analyzer agent
sentiment_analysis_agent = LlmAgent(
    name="sentiment_analysis_agent",
    model="gemini-2.0-flash",
    description="Analyzes the sentiment of financial news articles.",
    instruction=sentiment_analyzer_prompt,
)
