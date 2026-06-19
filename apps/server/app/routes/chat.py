"""Conversational endpoint (Phase D). Classifies intent, runs the matching deterministic
calculator or the agent pipeline, and returns a grounded answer with the raw numbers."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import current_user_id, get_container, rate_limit
from app.core.envelope import success
from app.infra.factory import Container
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat")


@router.post("", dependencies=[Depends(rate_limit("chat"))])
async def chat(
    body: ChatRequest,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    response = await ChatService(container).answer(
        user_id, body.message, body.portfolio_id, body.params
    )
    return success(response)
