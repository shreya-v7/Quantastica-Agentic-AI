"""Retrieve agent: hybrid RAG over the user's documents. Pure retrieval, no LLM.

Missing embeddings or an empty index is a completed skip, not a pipeline failure.
Passages are attached to context so Insight and Summarizer can cite them.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.agents.base import PipelineContext, RetrievedPassage
from app.core.errors import ProviderNotConfiguredError

Retriever = Callable[[str, str], Awaitable[list[RetrievedPassage]]]


class RetrieveAgent:
    name = "retrieve"

    def __init__(self, retriever: Retriever | None):
        self._retriever = retriever

    def input_summary(self, ctx: PipelineContext) -> str:
        return f"query='{ctx.query}'"

    async def run(self, ctx: PipelineContext) -> str:
        if self._retriever is None:
            ctx.retrieved = []
            return "retriever not wired; skipped"
        try:
            ctx.retrieved = await self._retriever(ctx.user_id, ctx.query)
        except ProviderNotConfiguredError:
            ctx.retrieved = []
            return "embeddings not configured; skipped"
        return f"{len(ctx.retrieved)} passages"
