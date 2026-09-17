"""Reciprocal Rank Fusion for hybrid dense + sparse retrieval."""

from __future__ import annotations

from collections.abc import Sequence


def rrf_fuse(ranked_id_lists: Sequence[Sequence[str]], k: int = 60) -> list[str]:
    """Merge several ranked id lists. Higher score is better. Stable for ties."""
    scores: dict[str, float] = {}
    for ranked in ranked_id_lists:
        for rank, item_id in enumerate(ranked):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank + 1)
    return [item_id for item_id, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))]
