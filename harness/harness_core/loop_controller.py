"""loop_controller.py — fixable-retry accounting.

Pure + immutable helpers over a work item's loop_counts dict. A gate that returns
fixable=True lets the step retry until should_retry() is False (loop_limit reached),
after which the item escalates instead of looping forever.
"""
from __future__ import annotations


class LoopController:
    def __init__(self, default_limit: int = 2):
        self.default_limit = default_limit

    def should_retry(self, counts: dict, key: str, limit: int | None = None) -> bool:
        limit = self.default_limit if limit is None else limit
        return counts.get(key, 0) < limit

    def record(self, counts: dict, key: str) -> dict:
        updated = dict(counts)
        updated[key] = updated.get(key, 0) + 1
        return updated
