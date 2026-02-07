"""
Agent Registry -- central map from agent name to its root Agent instance.

Usage:
    from app.agents import AGENT_REGISTRY
    agent = AGENT_REGISTRY["chart_analyzer_agent"]
"""

from .chart_analyzer.agent import root_agent as chart_analyzer_agent
from .news_analyzer.agent import root_agent as news_analyzer_agent
from .wealth_manager.agent import root_agent as wealth_manager_agent
from .tax_advisor.agent import root_agent as tax_advisor_agent
from .trade_execution.agent import root_agent as trade_execution_agent
from .loan_insurance.agent import root_agent as loan_insurance_agent
from .investment.agent import root_agent as investment_agent
from .indicator_analysis.agent import root_agent as indicator_analysis_agent


# Maps the agent's `name` attribute (and friendly aliases) to its instance.
AGENT_REGISTRY = {
    # Keyed by their Agent.name
    "chart_analyzer_agent": chart_analyzer_agent,
    "financial_news_analyzer": news_analyzer_agent,
    "conversation_agent": wealth_manager_agent,       # ambiguous -- prefer alias
    "trade_execution_agent": trade_execution_agent,
    "loan_advisor_agent": loan_insurance_agent,
    "master_orchestrator": investment_agent,
    "indicator_analysis_agent": indicator_analysis_agent,

    # Friendly aliases (recommended -- use these in API calls)
    "chart_analyzer": chart_analyzer_agent,
    "news_analyzer": news_analyzer_agent,
    "wealth_manager": wealth_manager_agent,
    "tax_advisor": tax_advisor_agent,
    "trade_execution": trade_execution_agent,
    "loan_insurance": loan_insurance_agent,
    "investment": investment_agent,
    "indicator_analysis": indicator_analysis_agent,

    # Legacy names used by the old prompt.py port-mapping
    "wealth_manager_agent": wealth_manager_agent,
    "loan_insurance_agent": loan_insurance_agent,
    "net_worth_tracker_agent": wealth_manager_agent,         # was a sub-agent alias
    "affordability_analysis_agent": wealth_manager_agent,    # was a sub-agent alias
}
