"""Deterministic LLM test double. The only permitted fake. It never ships in app/."""

from __future__ import annotations

from typing import Any

from app.infra.llm.base import LLMClient


class FakeLLM(LLMClient):
    """Returns deterministic, schema-aware responses for the pipeline."""

    def __init__(self, *, invalid_plan: bool = False):
        self.invalid_plan = invalid_plan
        self.calls: list[dict[str, Any]] = []

    async def complete(
        self, system: str, user: str, json_schema: dict[str, Any] | None = None
    ) -> str | dict[str, Any]:
        self.calls.append({"system": system, "user": user, "schema": json_schema})

        if json_schema is None:
            return (
                "Your portfolio is highly concentrated. The finding 'Concentration risk' "
                "shows the largest positions dominate total value."
            )

        properties = json_schema.get("properties", {})
        if "intent" in properties:
            return self._classify(user)
        if "steps" in properties:
            if self.invalid_plan:
                return {"unexpected": "no steps here"}
            return {
                "steps": [
                    {"analysis": "research", "reason": "compute holdings and weights"},
                    {"analysis": "risk", "reason": "compute concentration metrics"},
                    {"analysis": "insight", "reason": "summarize risks"},
                ]
            }
        if "findings" in properties:
            return {
                "findings": [
                    {
                        "title": "Concentration risk",
                        "body": "The largest positions dominate total portfolio value.",
                        "severity": "high",
                        "confidence": 0.9,
                        "metricIds": ["hhi", "top5_weight", "bogus_id"],
                    }
                ]
            }
        raise AssertionError("Unexpected schema in FakeLLM")

    @staticmethod
    def _classify(user: str) -> dict[str, Any]:
        import re

        text = user.lower()
        symbol_match = re.search(r"[A-Z][A-Z0-9&-]*\.(?:NS|BO)", user)
        symbol = symbol_match.group(0) if symbol_match else None
        if "tax" in text or "regime" in text:
            intent = "tax"
        elif "sip" in text or "goal" in text or "corpus" in text:
            intent = "sip"
        elif "afford" in text or "emi" in text or "loan" in text:
            intent = "affordability"
        elif "sentiment" in text or "news" in text:
            intent = "sentiment"
        elif "price" in text or "quote" in text:
            intent = "market"
        elif "document" in text or "statement" in text:
            intent = "document"
        elif "portfolio" in text or "concentrat" in text or "risk" in text:
            intent = "portfolio"
        else:
            intent = "general"
        return {"intent": intent, "symbol": symbol}
