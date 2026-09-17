"""MCP server exposing Quantastica grounded tools to Cursor, Claude Desktop, and other hosts.

Run: python -m app.mcp
"""

from __future__ import annotations

from app.mcp import tools


def build_server():
    from mcp.server.fastmcp import FastMCP

    server = FastMCP(
        "quantastica",
        instructions=(
            "Grounded Indian household and HNI tools. Numbers come from calculators or "
            "the mock bank book, never from a language model. Not investment advice. "
            "The mock bank is a demo core; a real deploy replaces it with the bank API."
        ),
    )

    server.tool()(tools.compare_tax_regimes)
    server.tool()(tools.required_sip)
    server.tool()(tools.affordability_check)
    server.tool()(tools.bank_list_customers)
    server.tool()(tools.bank_customer_snapshot)
    server.tool()(tools.bank_holdings)
    return server


def main() -> None:
    build_server().run()
