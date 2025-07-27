from google.adk.agents import Agent
from .prompt import CONVERSATION_PROMPT
from .subagents.tax_rule_base_agent.agent import tax_rule_base_agent
from .subagents.income_expense_analyzer_agent.agent import income_expense_analyzer_agent
from .subagents.tax_optimization_agent.agent import tax_optimization_agent

conversation_agent = Agent(
    name="conversation_agent",
    model="gemini-2.0-flash",
    description="Handles tax-related queries and delegates to tax sub-agents.",
    instruction=CONVERSATION_PROMPT,
    sub_agents=[
        tax_rule_base_agent,
        income_expense_analyzer_agent,
        tax_optimization_agent
    ],
    output_key="tax_advisor_output"
)

root_agent = conversation_agent
