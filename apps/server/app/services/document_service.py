"""Document ingestion and retrieval for RAG. Uploaded text is chunked, embedded via the
embeddings provider, and stored with pgvector. Retrieval is user-scoped cosine search.
"""

from __future__ import annotations

from app.infra.factory import Container
from app.infra.repo.document_repo import DocumentRepository
from app.providers.embeddings.voyage import EmbeddingsProvider

CHUNK_CHARS = 800
CHUNK_OVERLAP = 100


def chunk_text(text: str, size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + size)
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = end - overlap
    return chunks


class DocumentService:
    def __init__(self, container: Container):
        self._c = container
        self._repo = DocumentRepository(container.session_factory)

    def _embeddings(self) -> EmbeddingsProvider:
        return self._c.provider("embeddings")  # type: ignore[return-value]

    async def ingest(self, user_id: str, title: str, text: str) -> dict:
        chunks = chunk_text(text)
        if not chunks:
            return {"documentId": None, "chunks": 0}
        location = await self._c.storage.put(
            f"documents/{user_id}/{title}", text.encode("utf-8"), "text/plain"
        )
        doc_id = await self._repo.create_document(user_id, title, "text/plain", location)
        vectors = await self._embeddings().embed(chunks)
        count = await self._repo.add_chunks(user_id, doc_id, chunks, vectors)
        return {"documentId": doc_id, "chunks": count}

    async def list(self, user_id: str) -> list[dict]:
        rows = await self._repo.list_documents(user_id)
        return [
            {
                "id": r.id,
                "title": r.title,
                "contentType": r.content_type,
                "createdAt": r.created_at.isoformat(),
            }
            for r in rows
        ]

    async def retrieve(self, user_id: str, query: str, k: int = 5) -> list[dict]:
        vectors = await self._embeddings().embed([query])
        rows = await self._repo.search(user_id, vectors[0], k)
        return [{"documentId": r.document_id, "content": r.content} for r in rows]
