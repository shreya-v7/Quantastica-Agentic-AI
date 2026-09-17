from app.mcp.server import build_server
from app.mcp.tools import compare_tax_regimes, required_sip
from evals.runner import run_golden_india


def test_golden_india_all_pass():
    results = run_golden_india()
    failed = [row for row in results if not row["ok"]]
    assert failed == [], failed


def test_mcp_tax_tool_zero_new_regime():
    result = compare_tax_regimes(basic_salary=775_000)
    assert result["newRegime"]["totalTax"] == 0
    assert "Not investment advice" in result["disclaimer"]


def test_mcp_sip_tool_zero_return():
    result = required_sip(120_000, 10, 0)
    assert result["monthlySip"] == 1000.0


def test_mcp_server_registers_tools():
    server = build_server()
    names = {tool.name for tool in server._tool_manager.list_tools()}
    assert "compare_tax_regimes" in names
    assert "required_sip" in names
    assert "affordability_check" in names
