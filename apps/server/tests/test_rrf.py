from app.rag.rrf import rrf_fuse


def test_rrf_prefers_items_ranked_high_in_both_lists():
    fused = rrf_fuse([["a", "b", "c"], ["a", "d", "b"]])
    assert fused[0] == "a"
    assert "b" in fused
    assert set(fused) == {"a", "b", "c", "d"}


def test_rrf_empty():
    assert rrf_fuse([]) == []
    assert rrf_fuse([[], []]) == []
