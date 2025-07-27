from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json

app = FastAPI()

# Set your base directory for test data
BASE_DIR = 'D:\\hackathon\\QuantasticaAPI\\mcp-firebase\\test_data_dir'

# Request schema
class TestDataRequest(BaseModel):
    user_id: str
    json_filename: str

# Function to load data
def load_test_data(user_id: str, json_filename: str, base_dir: str = BASE_DIR):
    file_path = os.path.join(base_dir, user_id, json_filename)
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# REST endpoint
@app.post("/test-data/")
def get_test_data(request: TestDataRequest):
    data = load_test_data(request.user_id, request.json_filename)
    if data is None:
        raise HTTPException(status_code=404, detail="Test data file not found.")
    return data
