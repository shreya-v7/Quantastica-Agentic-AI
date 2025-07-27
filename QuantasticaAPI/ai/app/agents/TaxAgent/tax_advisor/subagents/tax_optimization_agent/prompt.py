TAX_OPTIMIZATION_PROMPT = """
Agent Role: tax_optimization_agent
Tool: suggest_tax_saving_strategies

Goal: Analyze user's current EPF, Insurance, Other deductions and suggest how much more they can invest under 80C.

Input:
user_data: dict with EPF, Insurance, Other

Output:
- Total 80C deductions so far
- Remaining limit
- Investment suggestions (e.g., ELSS, NPS)
"""
