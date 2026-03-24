"""
Quick smoke-test script for the Quantastica ADK agents.

Usage:
    1. Start the server:   uvicorn app.main:app --reload --port 8000
    2. Run this script:    python test_agent.py

Each test sends a POST to /prompt/ask and prints the response.
Agents that only require GCP credentials are tested by default.
Set RUN_ALL=1 to include agents that need Alpaca keys.
"""

import os
import sys
import json
import urllib.request
import urllib.error

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# ── Test cases ────────────────────────────────────────────────────────────
# Each tuple: (app_name, description, user_message)
CORE_TESTS = [
    (
        "wealth_manager",
        "Net worth tracker (test data)",
        "What is my net worth? My phone is 1010101010",
    ),
    (
        "indicator_analysis",
        "Stock indicator analysis (stock_data.json)",
        "Analyze the RSI and MACD for the stock data.",
    ),
    (
        "loan_insurance",
        "Loan advisor (test data)",
        "I want a home loan of 50 lakhs. My phone is 1010101010. What are my options?",
    ),
    (
        "tax_advisor",
        "Tax advisor (hardcoded knowledge)",
        "I earn 15 lakhs per year. How can I save tax under the new regime?",
    ),
    (
        "investment",
        "Investment advisor (test data + search)",
        "I have 5 lakhs to invest. Suggest a diversified portfolio for moderate risk.",
    ),
    (
        "news_analyzer",
        "Financial news analysis (Google Search)",
        "What is the latest news about Reliance Industries and how does it affect the stock?",
    ),
    (
        "chart_analyzer",
        "Chart analyzer (NSE live data)",
        "Analyze the trend for RELIANCE over the last 30 days.",
    ),
]

EXTRA_TESTS = [
    (
        "trade_execution",
        "Trade execution (requires Alpaca keys)",
        "Show me all my current orders.",
    ),
]


def call_agent(app_name: str, message: str, user_id: str = "test_user") -> dict:
    """Send a prompt to the API and return the JSON response."""
    payload = json.dumps({
        "app_name": app_name,
        "user_id": user_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": message}],
        },
    }).encode()

    req = urllib.request.Request(
        f"{BASE_URL}/prompt/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode() if exc.fp else ""
        return {"error": f"HTTP {exc.code}", "detail": body}
    except urllib.error.URLError as exc:
        return {"error": str(exc.reason)}


def run_tests(tests: list[tuple[str, str, str]]) -> None:
    """Run a list of test cases and print results."""
    passed = 0
    failed = 0

    for app_name, description, message in tests:
        print(f"\n{'=' * 70}")
        print(f"  Agent:   {app_name}")
        print(f"  Test:    {description}")
        print(f"  Prompt:  {message[:80]}{'...' if len(message) > 80 else ''}")
        print(f"{'=' * 70}")

        result = call_agent(app_name, message)

        if "error" in result:
            print(f"  FAILED: {result['error']}")
            detail = result.get("detail", "")
            if detail:
                print(f"  Detail: {detail[:200]}")
            failed += 1
        else:
            # Print a truncated version of the response
            text = json.dumps(result, indent=2)
            if len(text) > 500:
                text = text[:500] + "\n  ... (truncated)"
            print(f"  OK\n{text}")
            passed += 1

    print(f"\n{'=' * 70}")
    print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")
    print(f"{'=' * 70}\n")


def main():
    # Quick health check
    print(f"Checking server at {BASE_URL} ...")
    try:
        with urllib.request.urlopen(f"{BASE_URL}/health", timeout=5) as resp:
            health = json.loads(resp.read().decode())
            print(f"Server is up: {health}\n")
    except Exception as exc:
        print(f"Cannot reach server at {BASE_URL}: {exc}")
        print("Start it with:  uvicorn app.main:app --reload --port 8000")
        sys.exit(1)

    tests = list(CORE_TESTS)
    if os.getenv("RUN_ALL", "").strip() == "1":
        tests.extend(EXTRA_TESTS)
    else:
        print("Tip: set RUN_ALL=1 to also test trade_execution (needs Alpaca keys).\n")

    run_tests(tests)


if __name__ == "__main__":
    main()
