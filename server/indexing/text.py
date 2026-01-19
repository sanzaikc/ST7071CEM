from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from math import log, sqrt
from typing import Iterable


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric tokens.

    Args:
        text: Raw input text.

    Returns:
        List of normalized tokens.
    """
    return [m.group(0).lower() for m in _TOKEN_RE.finditer(text or "")]


def term_frequencies(tokens: Iterable[str]) -> dict[str, int]:
    """Count term frequencies."""
    return dict(Counter(t for t in tokens if t))


def tf_weight(tf: int) -> float:
    """Compute a log-scaled TF weight."""
    if tf <= 0:
        return 0.0
    return 1.0 + log(tf)


def vector_weights(term_freqs: dict[str, int]) -> dict[str, float]:
    """Convert term frequencies into a sparse weight vector."""
    return {term: tf_weight(tf) for term, tf in term_freqs.items() if tf > 0}


def l2_norm(weights: dict[str, float]) -> float:
    """Compute L2 norm of a sparse weight vector."""
    return sqrt(sum(w * w for w in weights.values()))

