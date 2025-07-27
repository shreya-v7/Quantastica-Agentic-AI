# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from uuid import uuid4
# import requests
#
# BASE_URL = "http://localhost:8000"
# USER_ID = "u_123"
# router = APIRouter()
# user_sessions = {}  # In-memory store: user_id -> session_id
#
# class SessionRequest(BaseModel):
#     user_id: str
#
# class SessionResponse(BaseModel):
#     session_id: str
#
# @router.post("/financial_analyzer/create_session/{user_id}", response_model=SessionResponse)
# def create_session(user_id: str):
#     session_id = ""
#     if user_id in user_sessions:
#         session_id = user_sessions[user_id]
#     else:
#         session_id = f"s_{uuid4().hex[:8]}"
#         user_sessions[user_id] = session_id
#     url = f"{BASE_URL}/apps/financial_news_analyzer/users/{USER_ID}/sessions/{session_id}"
#     response = requests.post(url)
#     if response.status_code == 200:
#         print(response)
#     else:
#         print("Error:", response.status_code, response.text)
#     return SessionResponse(session_id=session_id)
