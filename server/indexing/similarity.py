from __future__ import annotations

from math import sqrt


def cosine_similarity(dot: float, norm_a: float, norm_b: float) -> float:
    """Compute cosine similarity given dot product and norms."""
    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def dot_product_sparse(a: dict[str, float], b: dict[str, float]) -> float:
    """Dot product between two sparse vectors."""
    if not a or not b:
        return 0.0
    if len(a) > len(b):
        a, b = b, a
    return sum(weight * b.get(term, 0.0) for term, weight in a.items())

