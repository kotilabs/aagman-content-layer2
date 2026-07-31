"""harness_engineering/embeddings.py — OpenAI embeddings via litellm, disk-cached.

Embeddings are deterministic in (text, model), so we hash-cache them and never pay
the API twice. The network backend is injectable so eval/tests can run offline.
No numpy in this env — vectors are plain Python lists (cosine lives in route_index).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

MODEL = "text-embedding-3-small"
_CACHE = Path(__file__).resolve().parent / "distilled" / "embed_cache.json"


def _key(text: str, model: str) -> str:
    return hashlib.sha1(f"{model}\x00{text}".encode("utf-8")).hexdigest()


def _litellm_backend(texts, model):
    """Default backend: batch call to OpenAI embeddings. Ensures the key is in env
    (load_env does not push to os.environ)."""
    if not os.environ.get("OPENAI_API_KEY"):
        try:
            from harness_core.run import load_env
            os.environ["OPENAI_API_KEY"] = load_env().get("OPENAI_API_KEY", "")
        except Exception:
            pass
    import litellm
    resp = litellm.embedding(model=model, input=list(texts))
    return [d["embedding"] for d in resp["data"]]


def embed(texts, model: str = MODEL, cache_path=None, backend=None):
    """Return one vector per text, hitting the backend only for cache misses and
    persisting new vectors. Order/length matches `texts`."""
    texts = list(texts)
    if not texts:
        return []
    path = Path(cache_path or _CACHE)
    try:
        cache = json.loads(path.read_text())
    except (OSError, ValueError):
        cache = {}
    miss = [t for t in texts if _key(t, model) not in cache]
    if miss:
        vecs = (backend or _litellm_backend)(miss, model)
        for t, v in zip(miss, vecs):
            cache[_key(t, model)] = v
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache))
    return [cache[_key(t, model)] for t in texts]
