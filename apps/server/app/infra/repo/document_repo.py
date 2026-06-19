"""Document and chunk persistence with pgvector similarity search, user-scoped."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.ids import new_id
from app.infra.db.models import DocumentChunkRow, DocumentRow


class DocumentRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sessions = session_factory

    async def create_document(
        self, user_id: str, title: str, content_type: str, location: str
    ) -> str:
        doc_id = new_id("doc")
        async with self._sessions() as session:
            session.add(
                DocumentRow(
                    id=doc_id,
                    user_id=user_id,
                    title=title,
                    content_type=content_type,
                    location=location,
                    created_at=datetime.now(UTC),
                )
            )
            await session.commit()
        return doc_id

    async def add_chunks(
        self, user_id: str, document_id: str, chunks: list[str], embeddings: list[list[float]]
    ) -> int:
        async with self._sessions() as session:
            for index, (content, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
                session.add(
                    DocumentChunkRow(
                        id=new_id("ch"),
                        user_id=user_id,
                        document_id=document_id,
                        chunk_index=index,
                        content=content,
                        embedding=embedding,
                    )
                )
            await session.commit()
        return len(chunks)

    async def list_documents(self, user_id: str) -> list[DocumentRow]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(DocumentRow)
                    .where(DocumentRow.user_id == user_id)
                    .order_by(DocumentRow.created_at.desc())
                )
            ).all()
        return list(rows)

    async def search(
        self, user_id: str, query_embedding: list[float], k: int = 5
    ) -> list[DocumentChunkRow]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(DocumentChunkRow)
                    .where(DocumentChunkRow.user_id == user_id)
                    .order_by(DocumentChunkRow.embedding.cosine_distance(query_embedding))
                    .limit(k)
                )
            ).all()
        return list(rows)
