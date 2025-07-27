import json
import os

def load_stock_data(symbol:str):
    """
    Loads data for a single stock symbol from the given JSON file.

    Args:
        json_file_path (str): Path to the JSON file containing stock data (list of dicts).
        symbol (str): The stock symbol to retrieve (case sensitive).

    Returns:
        dict: The data dictionary for the requested stock symbol, or None if not found.
    """
    file_path = os.path.join('trade_execution_agent','subagents','indicator_analysis_agent', 'stock_data.json')
    print(file_path)
    with open(file_path, 'r') as f:
        data = json.load(f)
    for stock in data:
        if stock.get("symbol") == symbol:
            return stock
    return None

#Example usage:
if __name__ == "__main__":
   # stock_file = "stock_data.json"
    stock_symbol = "META"
    stock_info = load_stock_data(stock_symbol)
    if stock_info:
        print(json.dumps(stock_info, indent=2))
    else:
        print(f"Stock symbol {stock_symbol} not found in .")