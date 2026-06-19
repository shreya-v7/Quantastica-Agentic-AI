"""All agent prompts live here. Kept terse and grounded in the computed data."""

from __future__ import annotations

import json

from app.schemas.agents import RiskMetric
from app.schemas.entities import Portfolio, PortfolioMetrics

PLANNER_SYSTEM = (
    "You are the planner for a financial analysis pipeline. Given a user question and a "
    "portfolio summary, produce a short ordered plan of analyses to run. Valid analysis "
    "values are 'research', 'risk', and 'insight'. Always include them in that order."
)

INSIGHT_SYSTEM = (
    "You are a financial risk analyst. You are given computed portfolio metrics and risk "
    "metrics. Produce concise, specific findings. Every finding must reference the metric "
    "ids that support it. Do not invent numbers that are not in the inputs. Severity is one "
    "of info, low, medium, high. Confidence is a number between 0 and 1."
)

SENTIMENT_SYSTEM = (
    "You are a financial news sentiment analyst for Indian equities. You are given real "
    "headlines from Indian financial press. Produce a sentiment score between -1 and 1, a "
    "one-word label, and the top positive and negative drivers. Every driver must cite one "
    "of the provided headlines and its exact url. Do not invent headlines or urls."
)


def sentiment_user(symbol: str, items: list) -> str:
    payload = {
        "symbol": symbol,
        "headlines": [
            {"title": i.title, "url": i.url, "source": i.source, "publishedAt": i.published_at}
            for i in items
        ],
    }
    return json.dumps(payload)


CHAT_CLASSIFIER_SYSTEM = (
    "You route an Indian personal-finance question to exactly one intent. Valid intents: "
    "'tax' (income tax old vs new regime), 'sip' (SIP or goal corpus), 'affordability' "
    "(can I afford a purchase or loan, EMI, FOIR), 'portfolio' (analyse my holdings, risk, "
    "concentration), 'market' (a live price or quote), 'sentiment' (news sentiment for a "
    "stock), 'document' (a question about an uploaded statement or document), or 'general'. "
    "If a stock is named, return its exchange-qualified symbol (RELIANCE.NS, TCS.BO). "
    "Return only the JSON."
)

CHAT_GROUND_SYSTEM = (
    "You explain a financial result to an Indian user in plain language. You are given the "
    "user's question and the exact numbers a deterministic calculator produced. Use only "
    "those numbers, quote them, and use Indian formatting (1,50,000 and lakh/crore). End "
    "with: 'Not investment advice, for informational purposes only.' Do not use em dashes."
)

CHAT_DOC_SYSTEM = (
    "You answer the user's question using only the provided document excerpts. If the "
    "excerpts do not contain the answer, say so plainly. Do not invent figures. End with: "
    "'Not investment advice, for informational purposes only.' Do not use em dashes."
)


def chat_classify_user(message: str) -> str:
    return f"Question: {message}"


def chat_ground_user(message: str, computed: dict) -> str:
    import json as _json

    return f"Question: {message}\nCalculator result: {_json.dumps(computed)}"


def chat_doc_user(message: str, excerpts: list[str]) -> str:
    import json as _json

    return f"Question: {message}\nExcerpts: {_json.dumps(excerpts)}"


SUMMARIZER_SYSTEM = (
    "You are a financial analyst for an Indian user, writing a plain-language answer to "
    "their question. Base every claim on the provided findings and metrics, and cite "
    "findings by their title. All amounts are INR; use Indian formatting (1,50,000 and "
    "lakh/crore). End with: 'Not investment advice, for informational purposes only.' "
    "Be direct and concise. Do not use em dashes."
)


def planner_user(query: str, portfolio: Portfolio, metrics_preview: dict) -> str:
    return (
        f"User question: {query}\n"
        f"Portfolio: {portfolio.name} ({portfolio.base_currency})\n"
        f"Summary: {json.dumps(metrics_preview)}"
    )


def insight_user(
    query: str, metrics: PortfolioMetrics, risk_metrics: list[RiskMetric]
) -> str:
    payload = {
        "query": query,
        "metrics": metrics.model_dump(by_alias=True),
        "riskMetrics": [m.model_dump(by_alias=True) for m in risk_metrics],
    }
    return json.dumps(payload)


def summarizer_user(query: str, findings: list[dict], risk_metrics: list[RiskMetric]) -> str:
    payload = {
        "query": query,
        "findings": findings,
        "riskMetrics": [m.model_dump(by_alias=True) for m in risk_metrics],
    }
    return json.dumps(payload)
