"""Phase-1 TDD: llm_router.py — models.yaml is the single source of truth.

IMPORTANT: these tests use FAKE model names (alpha/beta/gamma). No real model
string may appear in any .py file — the Phase-1 single-source grep forbids it;
real model names live only in harness_configs/models.yaml.

Covered: startup pricing check (refuse to start if a chain model lacks pricing),
resolution order overrides -> panels -> defaults, the resolver stub (primary =
chain[0]), fallback on transient error, and cost logging to logs/cost_log.jsonl.
"""
import json

import pytest

from harness_core.llm_router import LLMRouter

FAKE_YAML = """
defaults:
  classification: [alpha, beta]
  planning: [beta, gamma]
panels:
  judge: [beta, gamma]
overrides:
  content.create: [gamma, alpha]
pricing_per_1k:
  alpha: 0.001
  beta: 0.010
  gamma: 0.100
"""


def _router(tmp_path, completion_fn=None):
    y = tmp_path / "models.yaml"
    y.write_text(FAKE_YAML)
    return LLMRouter(models_yaml_path=str(y),
                     completion_fn=completion_fn,
                     cost_log_path=str(tmp_path / "cost_log.jsonl"))


def test_resolve_default_chain(tmp_path):
    r = _router(tmp_path)
    assert r.resolve("classification") == ["alpha", "beta"]


def test_resolve_panel_chain(tmp_path):
    r = _router(tmp_path)
    assert r.resolve("judge") == ["beta", "gamma"]


def test_override_wins_over_task_type(tmp_path):
    r = _router(tmp_path)
    # domain.step override matches regardless of task_type
    assert r.resolve("planning", domain="content", step="create") == ["gamma", "alpha"]


def test_resolve_unknown_task_raises(tmp_path):
    r = _router(tmp_path)
    with pytest.raises(KeyError):
        r.resolve("does_not_exist")


def test_primary_is_first_of_chain_resolver_stub(tmp_path):
    r = _router(tmp_path)
    assert r.primary("classification") == "alpha"


def test_startup_check_refuses_when_chain_model_lacks_pricing(tmp_path):
    bad = tmp_path / "models.yaml"
    bad.write_text("""
defaults:
  classification: [alpha, unpriced_model]
pricing_per_1k:
  alpha: 0.001
""")
    with pytest.raises(ValueError) as ei:
        LLMRouter(models_yaml_path=str(bad))
    assert "unpriced_model" in str(ei.value)


def test_complete_uses_primary_and_logs_cost(tmp_path):
    def fake(model, prompt, **kw):
        return {"text": f"reply from {model}", "tokens": 1000}
    r = _router(tmp_path, completion_fn=fake)
    out = r.complete("classification", "hello", domain="engineering", step="sense")
    assert out["model"] == "alpha"
    assert out["text"] == "reply from alpha"
    assert out["cost_usd"] == pytest.approx(0.001)  # 0.001/1k * 1000 tok
    lines = (tmp_path / "cost_log.jsonl").read_text().strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["model"] == "alpha"
    assert rec["task_type"] == "classification"
    assert rec["cost_usd"] == pytest.approx(0.001)


def test_complete_falls_back_on_transient_error(tmp_path):
    calls = []
    def flaky(model, prompt, **kw):
        calls.append(model)
        if model == "alpha":
            raise RuntimeError("429 rate limited")
        return {"text": "ok", "tokens": 500}
    r = _router(tmp_path, completion_fn=flaky)
    out = r.complete("classification", "hi")
    assert calls == ["alpha", "beta"]  # tried primary, fell back
    assert out["model"] == "beta"


def test_complete_raises_when_whole_chain_fails(tmp_path):
    def dead(model, prompt, **kw):
        raise RuntimeError("500 server error")
    r = _router(tmp_path, completion_fn=dead)
    with pytest.raises(RuntimeError):
        r.complete("classification", "hi")


def test_real_shipped_models_yaml_passes_startup_check():
    # the actual harness_configs/models.yaml must be internally consistent:
    # every model in every chain has a pricing entry, else this raises.
    LLMRouter()  # default path


def test_call_model_targets_a_specific_model_and_logs_cost(tmp_path):
    def fake(model, prompt, **kw):
        return {"text": f"from {model}", "tokens": 2000}
    r = _router(tmp_path, completion_fn=fake)
    out = r.call_model("beta", "judge", "hi")
    assert out["model"] == "beta"
    assert out["cost_usd"] == pytest.approx(0.010 * 2000 / 1000)  # beta priced 0.010

