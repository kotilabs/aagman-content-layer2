"""seed_memory.py — Day-0 seeding.

Reads the tracked distilled JSONs (harness_engineering/distilled + harness_content)
and populates the AgentMemory namespaces so the harness never boots with empty
memory — agents cannot tell a seed from live experience because it is written via
the same AgentMemory API. Reproducible: delete data/memory.db and re-run.

Namespace mapping follows Phase 2C of the build spec:
  engineering/sense  <- classifier_examples          (issue/severity patterns)
  engineering/ideate <- layer_ground_truth + file_relationships
  engineering/create <- fix_success_patterns
  engineering/judge  <- adversarial_vocab            (review objections)
  engineering/gate   <- sebi_patterns                (compliance flags)
  content/create     <- content examples
  content/judge      <- rejected/edited content patterns
"""
from __future__ import annotations

import json
from pathlib import Path

from harness_core.agent_memory import AgentMemory

_REPO = Path(__file__).resolve().parent
ENG = _REPO / "harness_engineering" / "distilled"
CON = _REPO / "harness_content" / "distilled"

_MAP = {
    ("engineering", "sense"): [ENG / "classifier_examples.json"],
    ("engineering", "ideate"): [ENG / "layer_ground_truth.json",
                                ENG / "file_relationships.json"],
    ("engineering", "create"): [ENG / "fix_success_patterns.json"],
    ("engineering", "judge"): [ENG / "adversarial_vocab.json"],
    ("engineering", "gate"): [ENG / "sebi_patterns.json"],
    ("content", "create"): [CON / "examples.json"],
    ("content", "judge"): [CON / "rejected_patterns.json"],
}


def _one(item) -> tuple:
    """Turn one distilled item into a (text, tags) lesson pair."""
    if isinstance(item, str):
        return item, ""
    if isinstance(item, dict):
        tags = str(item.get("label") or item.get("layer") or item.get("tags")
                   or item.get("flag") or "")
        parts = [f"{k}={v}" for k, v in item.items()
                 if isinstance(v, (str, int, float, bool)) and str(v).strip()]
        return (" | ".join(parts) or json.dumps(item)[:400]), tags
    return json.dumps(item)[:400], ""


def _entries(obj) -> list:
    """Flatten arbitrary distilled JSON into [(text, tags), ...]."""
    out = []
    if isinstance(obj, list):
        out = [_one(item) for item in obj]
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (list, dict)):
                out.extend(_entries(v))
            else:
                out.append((f"{k}: {v}", str(k)))
    return [(t, g) for (t, g) in out if str(t).strip()]


def seed_namespace(domain, step, files, db_path=None) -> int:
    mem = AgentMemory(domain, step, db_path=db_path)
    n = 0
    for f in files:
        p = Path(f)
        if not p.exists():
            continue
        try:
            obj = json.loads(p.read_text())
        except (ValueError, OSError):
            continue
        for text, tags in _entries(obj):
            mem.add(text, tags=tags)
            n += 1
    return n


def seed_all(db_path=None, mapping=None) -> dict:
    mapping = mapping or _MAP
    return {f"{d}/{s}": seed_namespace(d, s, files, db_path)
            for (d, s), files in mapping.items()}


if __name__ == "__main__":
    for ns, n in seed_all().items():
        print(f"seeded {ns}: {n} lessons")
