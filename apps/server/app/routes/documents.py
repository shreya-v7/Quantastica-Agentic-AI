"""Document upload and listing for RAG (Phase D). Requires the embeddings provider;
when it is not configured the endpoint returns a typed PROVIDER_NOT_CONFIGURED."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import Field

from app.core.dependencies import current_user_id, get_container
from app.core.envelope import success
from app.infra.factory import Container
from app.schemas.base import Contract
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents")


class IngestRequest(Contract):
    title: str = Field(min_length=1, max_length=255)
    text: str = Field(min_length=1)


@router.post("")
async def ingest(
    body: IngestRequest,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await DocumentService(container).ingest(user_id, body.title, body.text))


@router.get("")
async def list_documents(
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await DocumentService(container).list(user_id))
