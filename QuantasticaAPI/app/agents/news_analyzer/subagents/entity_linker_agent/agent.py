from google.adk.agents import LlmAgent
from .prompt import entity_linker_prompt


# Define the entity linker agent
entity_linker_agent = LlmAgent(
    name="entity_linker_agent",
    model="gemini-2.0-flash",
    description="Links sentiment from news articles to specific financial entities.",
    instruction=entity_linker_prompt,
)
