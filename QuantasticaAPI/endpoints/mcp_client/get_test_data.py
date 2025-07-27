import os
import json

def load_test_data(user_id: str, json_filename: str, base_dir: str = 'D:\\hackathon\\QuantasticaAPI\\mcp-firebase\\test_data_dir'):
    file_path = os.path.join(base_dir, user_id, json_filename)
    print(file_path)
    if not os.path.exists(file_path):
        print(f"Test data file not found: {file_path}")
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    user_id = "1010101010"
    json_filename = "fetch_epf_details.json"
    data = load_test_data(user_id, json_filename)
    print("Test data loaded successfully:")
    print(json.dumps(data, indent=2))