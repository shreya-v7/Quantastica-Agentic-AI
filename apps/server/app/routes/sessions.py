"""
Session management routes.

Creates or retrieves sessions for a given agent + user pair.
"""

from fastapi import APIRouter

from app.runner import get_or_create_session

router = APIRouter()

# In-memory cache so we don't re-create sessions on every request
_user_sessions: dict[tuple[str, str], str] = {}


@router.post("/{app_name}/{user_id}")
async def create_or_get_session(app_name: str, user_id: str):
    """Create a new session or return the existing one."""
    key = (app_name, user_id)
    if key in _user_sessions:
        return {"session_id": _user_sessions[key]}

    session_id = await get_or_create_session(app_name, user_id)
    _user_sessions[key] = session_id
    return {"session_id": session_id}
