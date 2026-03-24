"""
Unified ADK Agent Runner.

Supports two modes (controlled by settings.agent_mode):
  - "in_process"  : runs agents directly via google.adk.runners.Runner
                     (recommended for local development -- single process, no port juggling)
  - "microservice" : proxies requests to agents running on separate ports
                     (the legacy approach, suitable for production scaling)
"""

import requests
from uuid import uuid4
from typing import AsyncGenerator

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.config import settings
from app.agents import AGENT_REGISTRY


# ---------------------------------------------------------------------------
# Shared session service (in-process mode)
# ---------------------------------------------------------------------------
_session_service = InMemorySessionService()

# Cache of Runner instances keyed by app_name
_runners: dict[str, Runner] = {}


def _get_runner(app_name: str) -> Runner:
    """Return (or lazily create) a Runner for the given agent."""
    if app_name not in _runners:
        agent = AGENT_REGISTRY.get(app_name)
        if agent is None:
            raise ValueError(
                f"Unknown agent '{app_name}'. "
                f"Available: {sorted(AGENT_REGISTRY.keys())}"
            )
        _runners[app_name] = Runner(
            agent=agent,
            app_name=app_name,
            session_service=_session_service,
        )
    return _runners[app_name]


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

async def get_or_create_session(app_name: str, user_id: str) -> str:
    """Return an existing session id or create a new one."""
    if settings.agent_mode == "in_process":
        runner = _get_runner(app_name)
        session_id = f"s_{uuid4().hex[:8]}"
        await runner.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        return session_id
    else:
        # Microservice mode -- POST to the remote agent
        port = _resolve_port(app_name)
        url = f"{settings.base_url}:{port}/apps/{app_name}/users/{user_id}/sessions/s_{uuid4().hex[:8]}"
        resp = requests.post(url, timeout=10)
        resp.raise_for_status()
        return resp.json().get("session_id", "")


# ---------------------------------------------------------------------------
# Run agent
# ---------------------------------------------------------------------------

async def run_agent(
    app_name: str,
    user_id: str,
    session_id: str,
    message_text: str,
) -> dict:
    """
    Run an agent synchronously and return the final response.
    """
    if settings.agent_mode == "in_process":
        runner = _get_runner(app_name)

        user_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=message_text)],
        )

        final_response = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            if event.is_final_response():
                for part in event.content.parts:
                    if part.text:
                        final_response += part.text

        return {"response": final_response}

    else:
        # Microservice mode -- proxy the request
        port = _resolve_port(app_name)
        url = f"{settings.base_url}:{port}/run"
        payload = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {"role": "user", "parts": [{"text": message_text}]},
            "streaming": False,
        }
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()


async def run_agent_stream(
    app_name: str,
    user_id: str,
    session_id: str,
    message_text: str,
) -> AsyncGenerator[str, None]:
    """
    Run an agent with streaming and yield text chunks.
    """
    if settings.agent_mode == "in_process":
        runner = _get_runner(app_name)

        user_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=message_text)],
        )

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        yield part.text

    else:
        # Microservice mode -- proxy SSE
        port = _resolve_port(app_name)
        url = f"{settings.base_url}:{port}/run_sse"
        payload = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {"role": "user", "parts": [{"text": message_text}]},
            "streaming": True,
        }
        with requests.post(url, json=payload, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_lines():
                if chunk:
                    yield chunk.decode("utf-8")


# ---------------------------------------------------------------------------
# Port mapping (microservice mode only)
# ---------------------------------------------------------------------------

_PORT_MAP = {
    "chart_analyzer_agent": 8002,
    "chart_analyzer": 8002,
    "wealth_manager_agent": 8003,
    "wealth_manager": 8003,
    "loan_insurance_agent": 8004,
    "loan_insurance": 8004,
    "loan_advisor_agent": 8004,
    "net_worth_tracker_agent": 8005,
    "affordability_analysis_agent": 8006,
    "trade_execution_agent": 8007,
    "trade_execution": 8007,
    "news_analyzer": 8008,
    "financial_news_analyzer": 8008,
    "tax_advisor": 8009,
    "investment": 8010,
    "indicator_analysis": 8011,
}


def _resolve_port(app_name: str) -> int:
    return _PORT_MAP.get(app_name, 8001)
