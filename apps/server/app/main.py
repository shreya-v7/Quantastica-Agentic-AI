"""
Quantastica API -- FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload --port 8000
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

log = logging.getLogger(__name__)

app = FastAPI(
    title="Quantastica API",
    description="Unified AI-powered financial intelligence platform",
    version="1.0.0",
)

# -- CORS --
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Core ADK routes (always loaded) --
from app.routes import prompt, sessions, data  # noqa: E402
from app.routes import config as config_routes  # noqa: E402
from app.routes import demo as demo_routes  # noqa: E402
from app.financial_intelligence.api import routes as fi_routes  # noqa: E402
from app.contracts.version import CONTRACT_VERSION  # noqa: E402

app.include_router(config_routes.router)
app.include_router(demo_routes.router)
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(prompt.router, prefix="/prompt", tags=["Prompt"])
app.include_router(data.router, prefix="/data", tags=["Data"])
app.include_router(fi_routes.router, tags=["Financial Intelligence"])

# -- Optional: Firestore (requires firebase-admin + credentials) --
try:
    from app.routes import firestore  # noqa: E402

    app.include_router(firestore.router, prefix="/firestore", tags=["Firestore"])
    log.info("Firestore route loaded.")
except Exception as exc:
    log.warning("Firestore route not loaded (Firebase credentials missing or "
                "firebase-admin not installed): %s", exc)

# -- Optional: WebSocket streaming (requires yfinance) --
try:
    from app.routes import streaming  # noqa: E402

    app.include_router(streaming.router, tags=["Streaming"])
    log.info("Streaming route loaded.")
except Exception as exc:
    log.warning("Streaming route not loaded (yfinance not installed): %s", exc)


@app.get("/health")
def health_check():
    """Simple health-check endpoint."""
    return {
        "status": "ok",
        "service": "quantastica-api",
        "version": CONTRACT_VERSION,
    }
