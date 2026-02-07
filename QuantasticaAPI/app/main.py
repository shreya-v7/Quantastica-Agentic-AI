"""
Quantastica API -- FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# -- Routes --
from app.routes import prompt, sessions, data, firestore, streaming  # noqa: E402

app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(prompt.router, prefix="/prompt", tags=["Prompt"])
app.include_router(data.router, prefix="/data", tags=["Data"])
app.include_router(firestore.router, prefix="/firestore", tags=["Firestore"])
app.include_router(streaming.router, tags=["Streaming"])


@app.get("/health")
def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok", "service": "quantastica-api"}
