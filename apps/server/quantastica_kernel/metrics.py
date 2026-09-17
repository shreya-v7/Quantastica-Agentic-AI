"""Eval metrics used as release gates. Deterministic; no LLM-as-judge here."""
from __future__ import annotations

import math


def precision_recall_f1(true_positive: int, false_positive: int, false_negative: int) -> dict:
    denom_p = true_positive + false_positive
    denom_r = true_positive + false_negative
    precision = true_positive / denom_p if denom_p else 0.0
    recall = true_positive / denom_r if denom_r else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def expected_calibration_error(
    pairs: list[tuple[float, bool]], bins: int = 10
) -> float:
    """10-bin ECE: weighted |confidence - accuracy| per bin."""
    if not pairs or bins < 1:
        return 0.0
    buckets: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for confidence, correct in pairs:
        index = min(bins - 1, max(0, int(confidence * bins)))
        buckets[index].append((confidence, correct))
    total = len(pairs)
    error = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        avg_conf = sum(item[0] for item in bucket) / len(bucket)
        avg_acc = sum(1.0 for item in bucket if item[1]) / len(bucket)
        error += (len(bucket) / total) * abs(avg_conf - avg_acc)
    return error


def bcubed(predicted: list[str], gold: list[str]) -> dict:
    """Record-centered clustering scores. predicted/gold are cluster ids per record."""
    if len(predicted) != len(gold) or not predicted:
        return {"precision": 0.0, "recall": 0.0}
    precision_sum = 0.0
    recall_sum = 0.0
    for pred, truth in zip(predicted, gold, strict=True):
        pred_members = [i for i, label in enumerate(predicted) if label == pred]
        gold_members = [i for i, label in enumerate(gold) if label == truth]
        overlap = len(set(pred_members) & set(gold_members))
        precision_sum += overlap / len(pred_members)
        recall_sum += overlap / len(gold_members)
    n = len(predicted)
    return {"precision": precision_sum / n, "recall": recall_sum / n}


def recall_at_k(relevant: set[str], ranked: list[str], k: int) -> float:
    if not relevant:
        return 1.0
    hit = len(relevant.intersection(ranked[:k]))
    return hit / len(relevant)


def ndcg_at_k(gains: list[float], k: int) -> float:
    window = gains[:k]

    def dcg(values: list[float]) -> float:
        return sum(gain / math.log2(rank + 2) for rank, gain in enumerate(values))

    ideal = sorted(window, reverse=True)
    denom = dcg(ideal)
    return 0.0 if denom == 0 else dcg(window) / denom


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref = reference.split()
    hyp = hypothesis.split()
    if not ref:
        return 0.0 if not hyp else 1.0
    return _levenshtein(ref, hyp) / len(ref)


def _levenshtein(left: list[str], right: list[str]) -> int:
    prev = list(range(len(right) + 1))
    for i, token in enumerate(left, start=1):
        current = [i]
        for j, other in enumerate(right, start=1):
            insert = current[j - 1] + 1
            delete = prev[j] + 1
            replace = prev[j - 1] + (token != other)
            current.append(min(insert, delete, replace))
        prev = current
    return prev[-1]


def trajectory_score(expected: list[str], actual: list[str]) -> dict:
    if not expected:
        return {"tool_trajectory_avg_score": 1.0, "response_match": 1.0}
    matched = sum(1 for a, b in zip(expected, actual, strict=False) if a == b)
    prefix = matched / len(expected)
    overlap = len(set(expected) & set(actual)) / len(set(expected))
    return {
        "tool_trajectory_avg_score": prefix,
        "response_match": overlap,
    }
