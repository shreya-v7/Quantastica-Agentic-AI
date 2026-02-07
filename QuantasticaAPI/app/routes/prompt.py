"""
Prompt handling route.

Accepts a user prompt, routes it to the appropriate agent via the unified
runner, and returns the response (optionally as a stream).
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.runner import run_agent, run_agent_stream
from app.routes.sessions import create_or_get_session, _user_sessions

router = APIRouter()


# ---------------------------------------------------------------------------
# Request schema
# ---------------------------------------------------------------------------

class MessagePart(BaseModel):
    text: str


class NewMessage(BaseModel):
    role: str
    parts: list[MessagePart]


class PromptRequest(BaseModel):
    user_id: str
    app_name: str
    new_message: NewMessage
    streaming: bool = False


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/ask")
async def accept_prompt(req: PromptRequest):
    """
    Send a prompt to an agent and get the response.

    If ``streaming`` is True the response is an SSE text stream.
    """
    # Resolve or create session
    key = (req.app_name, req.user_id)
    session_id = _user_sessions.get(key)
    if not session_id:
        result = await create_or_get_session(req.app_name, req.user_id)
        session_id = result["session_id"] if isinstance(result, dict) else result

    message_text = req.new_message.parts[0].text if req.new_message.parts else ""

    if req.streaming:
        return StreamingResponse(
            run_agent_stream(req.app_name, req.user_id, session_id, message_text),
            media_type="text/event-stream",
        )

    result = await run_agent(req.app_name, req.user_id, session_id, message_text)
    return result
