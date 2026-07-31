"""TDD: embeddings provider — deterministic on-disk cache, injectable backend.

Embeddings are pure functions of (text, model), so we cache them and never pay the
API twice. The backend is injectable so this test never touches the network.
"""
from harness_engineering.embeddings import embed


def test_embed_caches_and_only_calls_backend_on_miss(tmp_path):
    calls = []

    def fake_backend(texts, model):
        calls.append(list(texts))
        return [[float(len(t)), 0.0] for t in texts]

    cache = str(tmp_path / "emb.json")
    v1 = embed(["a", "bb"], cache_path=cache, backend=fake_backend)
    assert v1 == [[1.0, 0.0], [2.0, 0.0]]

    # second call: "a"/"bb" are cached, only "ccc" is a miss
    v2 = embed(["a", "bb", "ccc"], cache_path=cache, backend=fake_backend)
    assert len(v2) == 3 and v2[2] == [3.0, 0.0]
    assert calls == [["a", "bb"], ["ccc"]]          # backend saw only the misses


def test_embed_empty_input_no_backend_call(tmp_path):
    calls = []
    embed([], cache_path=str(tmp_path / "e.json"), backend=lambda t, m: calls.append(t) or [])
    assert calls == []
