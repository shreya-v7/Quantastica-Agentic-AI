from typing import Any, Literal

from pydantic import Field

from app.schemas.base import Contract

ChatIntent = Literal[
    "tax", "sip", "affordability", "portfolio", "market", "sentiment", "document", "general"
]


class ChatClassification(Contract):
    intent: ChatIntent
    symbol: str | None = None


class ChatRequest(Contract):
    message: str = Field(min_length=1, max_length=2000)
    portfolio_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(Contract):
    intent: ChatIntent
    answer: str
    data: dict[str, Any] | None = None
    needs_input: list[str] | None = None
    citations: list[str] | None = None
