"""Stock data loader -- reads from the shared stock_data.json."""

import json
import os

_SHARED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "shared")
_STOCK_DATA_FILE = os.path.join(_SHARED_DIR, "stock_data.json")


def load_stock_data(symbol: str):
    """
    Loads data for a single stock symbol from the shared stock_data.json.

    Args:
        symbol: The stock symbol to retrieve (case sensitive).

    Returns:
        The data dict for the symbol, or None if not found.
    """
    with open(_STOCK_DATA_FILE, "r") as f:
        data = json.load(f)
    for stock in data:
        if stock.get("symbol") == symbol:
            return stock
    return None
