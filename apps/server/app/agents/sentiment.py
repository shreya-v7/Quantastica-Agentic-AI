"""Sentiment agent: one LLM call over real Indian-source headlines, strict JSON output
(validate, retry once with the error, then fail). Drivers must cite headline and URL."""

from __future__ import annotations

from pydantic import Field

from app.agents import prompts
from app.agents.llm_json import complete_json
from app.infra.llm.base import LLMClient
from app.providers.news.newsapi import NewsItem
from app.schemas.base import Contract


class SentimentDriver(Contract):
    headline: str
    url: str
    reason: str


class SentimentResult(Contract):
    symbol: str
    score: float = Field(ge=-1.0, le=1.0)
    label: str
    positive_drivers: list[SentimentDriver]
    negative_drivers: list[SentimentDriver]


async def run_sentiment(
    llm: LLMClient, symbol: str, items: list[NewsItem], retries: int
) -> SentimentResult:
    user = prompts.sentiment_user(symbol, items)
    result = await complete_json(llm, prompts.SENTIMENT_SYSTEM, user, SentimentResult, retries)
    valid_urls = {item.url for item in items}
    result.positive_drivers = [d for d in result.positive_drivers if d.url in valid_urls]
    result.negative_drivers = [d for d in result.negative_drivers if d.url in valid_urls]
    return result
