import json
import os

# Define the base directory for all test data
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__),'..','..','..', 'test_data_dir')
def load_json(filename):
    with open(os.path.join(TEST_DATA_DIR, filename), 'r', encoding='utf-8') as f:
        return json.load(f)



def fetch_all_financial_data(user_ph: str) -> dict:
    """
    Fetches all financial data for a given user phone number from local JSON files.

    This function reads data from a directory structure like:
    test_data_dir/
    └── {user_ph}/
        ├── bank_transactions.json
        ├── credit_report.json
        ├── net_worth.json
        ├── mf_transactions.json
        ├── stock_transactions.json
        └── epf_details.json

    Args:
        user_ph: The user's 10-digit phone number, which corresponds to a directory name.

    Returns:
        A dictionary where keys are data types (e.g., 'bank_transactions_json')
        and values are the corresponding JSON/dict data. Returns an error
        if the user directory is not found.
    """
    print(f"--- Fetching data for user: {user_ph} from {TEST_DATA_DIR} ---")
    user_data_dir = os.path.join(TEST_DATA_DIR, user_ph)

    if not os.path.isdir(user_data_dir):
        return {"error": f"User data directory not found at: {user_data_dir}"}

    # Mapping of the keys expected by the orchestrator to the filenames
    data_files = {
        "bank_transactions_json": "fetch_bank_transactions.json",
        "credit_report_json": "fetch_credit_report.json",
        "net_worth_json": "fetch_net_worth.json",
        "mf_transactions_json": "fetch_mf_transactions.json",
        "stock_transactions_json": "fetch_stock_transactions.json",
        "epf_details_json": "fetch_epf_details.json",
    }

    fetched_data = {}
    for data_key, file_name in data_files.items():
        file_path = os.path.join(user_data_dir, file_name)
        try:
            with open(file_path, 'r') as f:
                fetched_data[data_key] = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Data file not found: {file_path}")
            # Return an empty dictionary if a specific file is missing
            fetched_data[data_key] = {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from file: {file_path}")
            fetched_data[data_key] = {"error": "Invalid JSON format"}

    return fetched_data
