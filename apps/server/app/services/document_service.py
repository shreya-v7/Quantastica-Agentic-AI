"""Document ingestion and retrieval for RAG.

LlamaIndex sentence-splits uploaded text, Voyage (or a test embedding provider) embeds
chunks, and Postgres stores them in pgvector. Retrieval is user-scoped hybrid search:
dense cosine plus BM25, fused with reciprocal rank fusion.
"""

from __future__ import annotations

from app.agents.base import RetrievedPassage
from app.infra.factory import Container
from app.infra.repo.document_repo import DocumentRepository
from app.providers.embeddings.voyage import EmbeddingsProvider
from app.rag.chunking import chunk_text


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
        passages = await self.retrieve_passages(user_id, query, k)
        return [
            {"documentId": p.document_id, "content": p.content, "score": p.score}
            for p in passages
        ]

    async def retrieve_passages(
        self, user_id: str, query: str, k: int = 5
    ) -> list[RetrievedPassage]:
        vectors = await self._embeddings().embed([query])
        rows = await self._repo.search_hybrid(user_id, query, vectors[0], k)
        return [
            RetrievedPassage(document_id=r.document_id, content=r.content)
            for r in rows
        ]
