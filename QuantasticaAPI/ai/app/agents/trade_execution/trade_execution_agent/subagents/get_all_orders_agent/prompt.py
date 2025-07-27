GET_ORDERS_PROMPT = """
Agent Role: view_orders_agent
Task: Show a user's orders.
Inputs: symbol (optional str), status (optional: 'all', 'open', etc.)
Process: Retrieve relevant orders and summarize them for the user.
Output: A string summary of the user's orders.
"""