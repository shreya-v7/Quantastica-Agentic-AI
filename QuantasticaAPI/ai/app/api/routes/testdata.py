from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import os
import json

router = APIRouter()

BASE_DIR = 'D:\\hackathon\\QuantasticaAPI\\mcp-firebase\\test_data_dir'

class DataRequest(BaseModel):
    user_id: str
    json_filename: str

def load_test_data(user_id: str, json_filename: str, base_dir: str = BASE_DIR):
    print(f"Loading test data for user_id: {user_id}, json_filename: {json_filename}")
    file_path = os.path.join(base_dir, user_id, json_filename)
    print(f"File path: {file_path}")
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@router.post("/test_data/")
def get_test_data(request: DataRequest):
    data = load_test_data(request.user_id, request.json_filename)
    if data is None:
        raise HTTPException(status_code=404, detail="Test data file not found.")
    return data
