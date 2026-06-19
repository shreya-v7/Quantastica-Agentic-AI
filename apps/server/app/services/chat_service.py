"""Conversational Q&A (Phase D).

The LLM classifies intent only. All numbers come from the deterministic calculators or
the agent pipeline; the LLM then narrates those exact numbers (grounding). Computational
intents that lack inputs return a clarifying prompt naming the missing fields rather than
guessing.
"""

from __future__ import annotations

from pydantic import ValidationError as PydanticValidationError

from app.agents import prompts
from app.agents.llm_json import complete_json
from app.calculators.planning import AffordabilityInput, affordability, required_monthly_sip
from app.calculators.tax import TaxInput, compare_regimes
from app.infra.factory import Container
from app.providers.marketdata.base import validate_symbol
from app.schemas.chat import ChatClassification, ChatResponse
from app.services.agent_service import AgentService

DISCLAIMER = "Not investment advice, for informational purposes only."


class ChatService:
    def __init__(self, container: Container):
        self._c = container
        self._retries = container.settings.llm_retries

    async def answer(
        self, user_id: str, message: str, portfolio_id: str | None, params: dict
    ) -> ChatResponse:
        classification = await complete_json(
            self._c.llm,
            prompts.CHAT_CLASSIFIER_SYSTEM,
            prompts.chat_classify_user(message),
            ChatClassification,
            self._retries,
        )
        intent = classification.intent
        handler = {
            "tax": self._tax,
            "sip": self._sip,
            "affordability": self._affordability,
            "portfolio": self._portfolio,
            "market": self._market,
            "sentiment": self._sentiment,
            "document": self._document,
            "general": self._general,
        }[intent]
        return await handler(user_id, message, portfolio_id, params, classification)

    async def _ground(self, message: str, computed: dict) -> str:
        result = await self._c.llm.complete(
            prompts.CHAT_GROUND_SYSTEM, prompts.chat_ground_user(message, computed)
        )
        return result if isinstance(result, str) else DISCLAIMER

    async def _tax(self, user_id, message, portfolio_id, params, c) -> ChatResponse:
        from app.services.profile_service import ProfileService

        # Explicit params win; otherwise the researcher derives the input from the
        # user's stored FinancialProfile so "compare my tax" works with no arguments.
        try:
            tax_input = TaxInput.model_validate(params) if params else None
        except PydanticValidationError:
            tax_input = None
        source = "params"
        if tax_input is None:
            tax_input = await ProfileService(self._c).build_tax_input(user_id)
            source = "profile"
        if tax_input.basic_salary <= 0:
            return ChatResponse(
                intent="tax",
                answer="I need your salary details, or set up your income profile first.",
                needs_input=["basicSalary", "hraReceived", "rentPaid", "deduction80C"],
            )
        computed = compare_regimes(tax_input).model_dump(by_alias=True)
        computed["source"] = source
        return ChatResponse(
            intent="tax", answer=await self._ground(message, computed), data=computed
        )

    async def _sip(self, user_id, message, portfolio_id, params, c) -> ChatResponse:
        target = params.get("targetInr") or params.get("target_inr")
        years = params.get("years")
        if not target or not years:
            return ChatResponse(
                intent="sip",
                answer="Tell me your target corpus and how many years you have.",
                needs_input=["targetInr", "years", "annualReturn (optional)"],
            )
        annual = float(params.get("annualReturn", 0.12))
        sip = required_monthly_sip(float(target), float(years), annual)
        computed = {
            "targetInr": float(target),
            "years": float(years),
            "annualReturn": annual,
            "monthlySip": round(sip, 2),
        }
        return ChatResponse(
            intent="sip", answer=await self._ground(message, computed), data=computed
        )

    async def _affordability(self, user_id, message, portfolio_id, params, c) -> ChatResponse:
        from app.services.profile_service import ProfileService

        # Fill household figures from the profile, letting explicit params override.
        context = await ProfileService(self._c).affordability_context(user_id)
        merged = {**context, **params}
        try:
            result = affordability(AffordabilityInput.model_validate(merged))
        except PydanticValidationError:
            return ChatResponse(
                intent="affordability",
                answer="I can check affordability with a few inputs.",
                needs_input=[
                    "purchaseCost", "downPayment", "loanRate", "loanYears",
                    "monthlyIncome", "liquidSavings",
                ],
            )
        computed = result.model_dump(by_alias=True)
        return ChatResponse(
            intent="affordability", answer=await self._ground(message, computed), data=computed
        )

    async def _portfolio(self, user_id, message, portfolio_id, params, c) -> ChatResponse:
        if not portfolio_id:
            return ChatResponse(
                intent="portfolio",
                answer="Which portfolio should I analyse?",
                needs_input=["portfolioId"],
            )
        run = await AgentService(self._c).run(user_id, message, portfolio_id)
        return ChatResponse(
            intent="portfolio",
            answer=run.answer or "Analysis complete.",
            data={"runId": run.id, "status": run.status.value},
            citations=[f.title for f in run.findings],
        )

    async def _market(self, user_id, message, portfolio_id, params, c) -> ChatResponse:
        if not c.symbol:
            return ChatResponse(
                intent="market",
                answer="Which stock? Use its exchange symbol like RELIANCE.NS.",
                needs_input=["symbol"],
            )
        quote = await self._c.provider("marketdata").quote(validate_symbol(c.symbol))
        computed = quote.model_dump()
        return ChatResponse(
            intent="market", answer=await self._ground(message, computed), data=computed
        )

    async def _sentiment(self, user_id, message, portfolio_id, params, c) -> ChatResponse:
        if not c.symbol:
            return ChatResponse(
                intent="sentiment",
                answer="Which stock's news sentiment do you want?",
                needs_input=["symbol"],
            )
        from app.agents.sentiment import run_sentiment

        symbol = validate_symbol(c.symbol)
        items = await self._c.provider("news").search(symbol.split(".")[0], limit=10)
        result = await run_sentiment(self._c.llm, symbol, items, self._retries)
        computed = result.model_dump(by_alias=True)
        return ChatResponse(
            intent="sentiment",
            answer=f"Sentiment for {symbol}: {result.label} ({result.score:+.2f}). {DISCLAIMER}",
            data=computed,
        )

    async def _document(self, user_id, message, portfolio_id, params, c) -> ChatResponse:
        from app.services.document_service import DocumentService

        chunks = await DocumentService(self._c).retrieve(user_id, message, k=5)
        if not chunks:
            return ChatResponse(
                intent="document",
                answer="I could not find anything in your uploaded documents.",
            )
        excerpts = [ch["content"] for ch in chunks]
        result = await self._c.llm.complete(
            prompts.CHAT_DOC_SYSTEM, prompts.chat_doc_user(message, excerpts)
        )
        answer = result if isinstance(result, str) else DISCLAIMER
        return ChatResponse(
            intent="document",
            answer=answer,
            citations=[ch["documentId"] for ch in chunks],
        )

    async def _general(self, user_id, message, portfolio_id, params, c) -> ChatResponse:
        result = await self._c.llm.complete(
            prompts.CHAT_GROUND_SYSTEM,
            f"Question: {message}\nNo calculator was run; answer briefly and add the disclaimer.",
        )
        answer = result if isinstance(result, str) else DISCLAIMER
        return ChatResponse(intent="general", answer=answer)
