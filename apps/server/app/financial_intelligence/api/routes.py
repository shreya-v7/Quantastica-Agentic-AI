import json
import os
from datetime import datetime, timezone

import jwt
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.financial_intelligence.ai.ask import ask_financial_question
from app.financial_intelligence.cloud.index import cloud
from app.financial_intelligence.core.insight import generate_insights
from app.financial_intelligence.core.types import FinancialSnapshot
from app.financial_intelligence.events.bus import emit
from app.financial_intelligence.ingestion.sync import normalize_snapshot
from app.contracts.models import AskResponse, FinancialSummary, InsightsGetResponse, SummarySyncResponse

router = APIRouter()


JWT_SECRET = os.getenv("FI_JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("FI_JWT_ALGORITHM", "HS256")
FERNET_KEY = os.getenv("FI_ENCRYPTION_KEY", "")
_fernet = Fernet(FERNET_KEY.encode()) if FERNET_KEY else None


def _auth_guard(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc
    return claims


def _snapshot_key(user_id: str) -> str:
    return f"user:{user_id}:snapshot"


def _history_key(user_id: str) -> str:
    return f"user:{user_id}:history"


def _serialize_snapshot(snapshot: FinancialSnapshot) -> str:
    raw = json.dumps(snapshot.model_dump(), ensure_ascii=True)
    if _fernet:
        return _fernet.encrypt(raw.encode()).decode()
    return raw


def _deserialize_snapshot(blob: str | None) -> FinancialSnapshot | None:
    if not blob:
        return None
    data = blob
    if _fernet:
        try:
            data = _fernet.decrypt(blob.encode()).decode()
        except InvalidToken as exc:
            raise HTTPException(status_code=500, detail="Encrypted snapshot unreadable") from exc
    return FinancialSnapshot.model_validate(json.loads(data))


class SyncRequest(BaseModel):
    user_id: str = Field(min_length=1)
    raw: dict
    write_history: bool = False


class AskRequest(BaseModel):
    user_id: str = Field(min_length=1)
    question: str = Field(min_length=1)


def _insights_to_model(insights: dict) -> FinancialSummary:
    return FinancialSummary(
        net_worth=insights["net_worth"],
        risk_exposure=float(insights["risk_exposure"]),
        debt_load=insights["debt_load"],
    )


@router.post("/summary", response_model=SummarySyncResponse)
async def create_summary(payload: SyncRequest, _: dict = Depends(_auth_guard)):
    snapshot = normalize_snapshot(payload.user_id, payload.raw)
    insights = generate_insights(snapshot)

    await cloud.store(_snapshot_key(payload.user_id), _serialize_snapshot(snapshot))
    if payload.write_history:
        history = await cloud.fetch(_history_key(payload.user_id)) or []
        history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "net_worth": insights["net_worth"],
                "debt_load": insights["debt_load"],
            }
        )
        await cloud.store(_history_key(payload.user_id), history)

    await emit(
        "INSIGHT_READY",
        {
            "user_id": payload.user_id,
            "net_worth": insights["net_worth"],
            "risk_exposure": insights["risk_exposure"],
            "debt_load": insights["debt_load"],
        },
    )

    return SummarySyncResponse(user_id=payload.user_id, summary=_insights_to_model(insights))


@router.get("/insights", response_model=InsightsGetResponse)
async def get_insights(user_id: str, _: dict = Depends(_auth_guard)):
    snapshot_blob = await cloud.fetch(_snapshot_key(user_id))
    snapshot = _deserialize_snapshot(snapshot_blob)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    raw = generate_insights(snapshot)
    return InsightsGetResponse(user_id=user_id, insights=_insights_to_model(raw))


@router.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest, _: dict = Depends(_auth_guard)):
    snapshot_blob = await cloud.fetch(_snapshot_key(payload.user_id))
    snapshot = _deserialize_snapshot(snapshot_blob)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    answer = await ask_financial_question(payload.question, snapshot)
    return AskResponse(user_id=payload.user_id, answer=answer)
