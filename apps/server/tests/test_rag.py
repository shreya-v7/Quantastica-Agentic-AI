"""Hybrid RAG: hashing embeddings + pgvector + BM25 fusion, FinanceBench sample overlap."""

from __future__ import annotations

import json
from pathlib import Path

from app.infra.factory import ProviderSlot
from app.providers.embeddings.hashing import HashingEmbeddings
from app.rag.chunking import chunk_text
from app.services.document_service import DocumentService

USER = "usr_seed_arjun"
EVAL_DIR = Path(__file__).resolve().parents[1] / "evals"


def _with_hashing(container) -> DocumentService:
    container.providers["embeddings"] = ProviderSlot(
        HashingEmbeddings(), True, [], "hashing"
    )
    return DocumentService(container)


async def test_chunking_splits_long_text():
    text = "India tax slabs change by assessment year. " * 80
    chunks = chunk_text(text)
    assert len(chunks) >= 2
    assert all(chunks)


async def test_hybrid_retrieve_finds_financebench_evidence(container):
    suite = json.loads((EVAL_DIR / "financebench_sample.json").read_text())
    svc = _with_hashing(container)
    for doc in suite["documents"]:
        ingested = await svc.ingest(USER, doc["title"], doc["text"])
        assert ingested["chunks"] > 0

    listed = await svc.list(USER)
    assert len(listed) >= 2

    for question in suite["questions"]:
        hits = await svc.retrieve(USER, question["question"], k=3)
        blob = " ".join(h["content"] for h in hits)
        assert question["evidenceMustContain"] in blob, question["id"]
