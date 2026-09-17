"""Document chunking via LlamaIndex sentence splitting, with a character fallback."""

from __future__ import annotations

FALLBACK_SIZE = 800
FALLBACK_OVERLAP = 100


def chunk_text(text: str, size: int = 512, overlap: int = 80) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    try:
        from llama_index.core.node_parser import SentenceSplitter
        from llama_index.core.schema import Document

        splitter = SentenceSplitter(chunk_size=size, chunk_overlap=overlap)
        nodes = splitter.get_nodes_from_documents([Document(text=cleaned)])
        chunks = [node.get_content().strip() for node in nodes if node.get_content().strip()]
        if chunks:
            return chunks
    except Exception:
        pass
    return _fallback_chunk(cleaned, FALLBACK_SIZE, FALLBACK_OVERLAP)


def _fallback_chunk(cleaned: str, size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + size)
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = end - overlap
    return chunks
