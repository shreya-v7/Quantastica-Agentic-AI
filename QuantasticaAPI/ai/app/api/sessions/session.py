from fastapi import APIRouter
from uuid import uuid4
import requests
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv("BASE_URL")

router = APIRouter()
user_sessions = {}


@router.post("/{app_name}/{user_id}")
def create_or_get_session(app_name: str, user_id: str):
    PORT_NUMBER = 8001
    if app_name == "chart_analyzer_agent":
        PORT_NUMBER = 8002
    elif app_name == "wealth_manager_agent":
        PORT_NUMBER = 8003
    elif app_name == "loan_insurance_agent":
        PORT_NUMBER = 8004
    elif app_name == "net_worth_tracker_agent":
        PORT_NUMBER = 8005
    elif app_name == "affordability_analysis_agent":
        PORT_NUMBER = 8006
    if (app_name,user_id) in user_sessions:
        session_id = user_sessions[(app_name,user_id)]
        print(f"Using existing session for app {app_name}, user {user_id}: {session_id}")
    else:
        session_id = f"s_{uuid4().hex[:8]}"
        user_sessions[(app_name,user_id)] = session_id
        url = f"{BASE_URL}:{PORT_NUMBER}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
        response = requests.post(url)
        if response.status_code == 200:
            print(response.json())
        else:
            print("Error:", response.status_code, response.text)
    return {"session_id": session_id}
