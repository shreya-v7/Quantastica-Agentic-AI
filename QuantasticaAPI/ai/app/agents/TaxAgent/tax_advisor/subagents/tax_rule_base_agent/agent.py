from google.adk.agents import Agent
from .prompt import TAX_RULE_PROMPT
from tools.rag_utils import retrieve_tax_answer

tax_rule_base_agent = Agent(
    name="tax_rule_base_agent",
    model="gemini-1.5-flash",
    description="Provides interpretation of Indian tax rules and sections.",
    instruction=TAX_RULE_PROMPT,
    tools=[retrieve_tax_answer],
    output_key="tax_rule_output"
)
