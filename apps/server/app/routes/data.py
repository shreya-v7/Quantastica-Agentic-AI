"""
Test data routes -- loads user financial data from the test_data_dir.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.shared.data_loader import load_user_json

router = APIRouter()


class DataRequest(BaseModel):
    user_id: str
    json_filename: str


@router.post("/test_data/")
def get_test_data(request: DataRequest):
    """Load a test-data JSON file for a given user."""
    data = load_user_json(request.user_id, request.json_filename)
    if not data:
        raise HTTPException(status_code=404, detail="Test data file not found.")
    return data
