"""
Shared data-loading utilities for Quantastica agents.

Consolidates the duplicated `load_json`, `load_stock_data`, and user-data
helpers that were previously copied across 7+ agent files.
"""

import json
import os
from typing import Optional

from app.config import settings


# ---------------------------------------------------------------------------
# Generic JSON loader
# ---------------------------------------------------------------------------

def load_json(file_path: str) -> dict:
    """
    Load and return a JSON file.  Returns {} on missing file or decode error.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found at {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {file_path}")
        return {}


# ---------------------------------------------------------------------------
# User financial-data helpers (test_data_dir)
# ---------------------------------------------------------------------------

def get_user_data_dir(user_ph: str) -> str:
    """Return the path to a user's test-data directory."""
    return os.path.join(settings.resolved_test_data_dir, user_ph)


def load_user_json(user_ph: str, filename: str) -> dict:
    """
    Load a specific JSON file from a user's test-data directory.

    Example:
        load_user_json("1010101010", "fetch_credit_report.json")
    """
    path = os.path.join(get_user_data_dir(user_ph), filename)
    return load_json(path)


def fetch_all_financial_data(user_ph: str) -> dict:
    """
    Fetch all standard financial data files for a user.

    Returns a dict keyed by data type. Used by the InvestmentAgent's
    personal_finance_agent.
    """
    user_dir = get_user_data_dir(user_ph)
    if not os.path.isdir(user_dir):
        return {"error": f"User data directory not found at: {user_dir}"}

    data_files = {
        "bank_transactions_json": "fetch_bank_transactions.json",
        "credit_report_json": "fetch_credit_report.json",
        "net_worth_json": "fetch_net_worth.json",
        "mf_transactions_json": "fetch_mf_transactions.json",
        "stock_transactions_json": "fetch_stock_transactions.json",
        "epf_details_json": "fetch_epf_details.json",
    }

    fetched = {}
    for key, fname in data_files.items():
        fpath = os.path.join(user_dir, fname)
        try:
            with open(fpath, "r") as f:
                fetched[key] = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Data file not found: {fpath}")
            fetched[key] = {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from file: {fpath}")
            fetched[key] = {"error": "Invalid JSON format"}
    return fetched


# ---------------------------------------------------------------------------
# Stock-data loader
# ---------------------------------------------------------------------------

def load_stock_data(symbol: str, json_file_path: Optional[str] = None) -> Optional[dict]:
    """
    Load data for a single stock symbol from a JSON file.

    If *json_file_path* is not supplied, the function looks for
    ``stock_data.json`` next to the calling agent (kept for backward compat).
    In practice, agents should pass an explicit path.

    Args:
        symbol: Stock ticker (case-sensitive).
        json_file_path: Absolute path to the JSON file containing stock data.

    Returns:
        The dict for the requested symbol, or None if not found.
    """
    if json_file_path is None:
        # Fallback: look relative to cwd (backward compat)
        json_file_path = "stock_data.json"

    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Warning: Stock data file not found: {json_file_path}")
        return None

    for stock in data:
        if stock.get("symbol") == symbol:
            return stock
    return None
