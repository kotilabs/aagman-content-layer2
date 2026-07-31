"""harness_engineering/route_index.py — retrieval router for issue -> area/file.

The measured baseline (routing_eval) showed the 4-keyword _route_layer routes only
~3% of issues, while nearest-neighbour over past issues hits ~48%. This is the
production side of that: a tiny token-Jaccard k-NN over a distilled index of real
(issue_text -> area, entry_file) pairs mined from merged PRs. No model call.

ONE retrieval definition lives here so production (RCAAgent) and the eval score the
exact same thing. Degrades to ('', '') when the index is absent or nothing matches,
so RCAAgent's keyword route remains the last-resort fallback.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


def _tokens(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(w) >= 3}


def jaccard(a: set, b: set) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def cosine(a, b) -> float:
    """Pure-Python cosine (no numpy in this env). 0 for a zero vector."""
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


class RouteIndex:
    """k-NN over (issue_text -> area, entry_file). predict() returns the majority
    area of the k nearest past issues and a representative entry file for it."""

    def __init__(self, examples):
        self.items = [(_tokens(e.get("issue_text", "")), e)
                      for e in (examples or []) if e.get("area")]

    @classmethod
    def load(cls, path):
        try:
            data = json.loads(Path(path).read_text())
        except (OSError, ValueError, TypeError):
            data = []
        return cls(data if isinstance(data, list) else [])

    def predict(self, issue_text: str, k: int = 3) -> tuple:
        q = _tokens(issue_text)
        if not q or not self.items:
            return ("", "")
        ranked = sorted(((jaccard(q, toks), e) for toks, e in self.items),
                        key=lambda x: -x[0])
        top = [e for s, e in ranked[:k] if s > 0]
        if not top:
            return ("", "")
        area = Counter(e["area"] for e in top).most_common(1)[0][0]
        entry = next((e.get("entry_file", "") for e in top if e.get("area") == area), "")
        return (area, entry)


class VectorRouteIndex:
    """Same k-NN routing as RouteIndex, but ranks by embedding cosine instead of
    token Jaccard. Embeddings are supplied precomputed (parallel to `examples`) so the
    index stays pure and testable — the API/caching lives in embeddings.py."""

    def __init__(self, examples, vectors):
        self.items = [(v, e) for v, e in zip(vectors, examples) if e.get("area") and v]

    def predict_vec(self, qvec, k: int = 3) -> tuple:
        if not qvec or not self.items:
            return ("", "")
        ranked = sorted(((cosine(qvec, v), e) for v, e in self.items), key=lambda x: -x[0])
        top = [e for s, e in ranked[:k] if s > 0]
        if not top:
            return ("", "")
        area = Counter(e["area"] for e in top).most_common(1)[0][0]
        entry = next((e.get("entry_file", "") for e in top if e.get("area") == area), "")
        return (area, entry)
