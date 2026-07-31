"""Phase-1 TDD: judgment_panel.py — multi-model vote, escalate on split.

A panel queries each model in its chain (via router.call_model, so cost is logged),
parses each reply to pass/block, then tallies: pass >= threshold -> pass; block
consensus (pass-frac <= 1-threshold) -> block; anything in between is a genuine
split -> escalate. vote() also satisfies the gate panel signature.

Fake models alpha/beta/gamma keep real model strings out of .py files.
"""
import pytest

from harness_core.llm_router import LLMRouter
from harness_core.judgment_panel import JudgmentPanel

PANEL_YAML = """
panels:
  judge: [alpha, beta, gamma]
pricing_per_1k:
  alpha: 0.0
  beta: 0.0
  gamma: 0.0
"""


def _router(tmp_path, replies, yaml_text=PANEL_YAML):
    y = tmp_path / "m.yaml"
    y.write_text(yaml_text)

    def fake(model, prompt, **kw):
        r = replies[model]
        if isinstance(r, Exception):
            raise r
        return {"text": r, "tokens": 0}

    return LLMRouter(models_yaml_path=str(y), completion_fn=fake,
                     cost_log_path=str(tmp_path / "c.jsonl"))


def test_vote_collects_one_vote_per_member(tmp_path):
    r = _router(tmp_path, {"alpha": "pass", "beta": "pass", "gamma": "block weak"})
    assert len(JudgmentPanel(r, "judge").vote("criteria", "artifact")) == 3


def test_decide_passes_on_majority(tmp_path):
    r = _router(tmp_path, {"alpha": "pass", "beta": "pass", "gamma": "block bad"})
    assert JudgmentPanel(r, "judge", threshold=0.66).decide("c", "a").verdict == "pass"


def test_decide_blocks_on_consensus_and_aggregates_issues(tmp_path):
    r = _router(tmp_path, {"alpha": "block A", "beta": "block B", "gamma": "block C"})
    v = JudgmentPanel(r, "judge", threshold=0.66).decide("c", "a")
    assert v.verdict == "block"
    assert v.issues


def test_decide_escalates_on_split(tmp_path):
    two = "panels:\n  judge: [alpha, beta]\npricing_per_1k:\n  alpha: 0.0\n  beta: 0.0\n"
    r = _router(tmp_path, {"alpha": "pass", "beta": "block x"}, yaml_text=two)
    assert JudgmentPanel(r, "judge", threshold=0.66).decide("c", "a").verdict == "escalate"


def test_dead_panelist_does_not_sink_the_vote(tmp_path):
    r = _router(tmp_path, {"alpha": "pass", "beta": RuntimeError("500"), "gamma": "pass"})
    votes = JudgmentPanel(r, "judge").vote("c", "a")
    assert len(votes) == 2  # beta skipped, alpha+gamma still voted


def test_vote_is_usable_as_a_gate_panel_callable(tmp_path):
    from harness_core.gates import QualityGate
    r = _router(tmp_path, {"alpha": "pass", "beta": "pass", "gamma": "pass"})
    gate = QualityGate(panel=JudgmentPanel(r, "judge").vote, threshold=0.66)
    assert gate.check("artifact").verdict == "pass"


# ---- verdict parsing: read the stated verdict, not scary words in the rationale --
from harness_core.judgment_panel import _default_parse


def test_parse_pass_even_when_rationale_mentions_violations():
    # REAL failure from a live compliance run: panelist APPROVED but its reasoning
    # said "does not violate ... nothing to reject" -> was misread as block.
    txt = ("**pass**\n\nBoth artifacts clear every gate. No buy/sell language, "
           "nothing that violates SEBI rules, and nothing to reject.")
    assert _default_parse(txt)["verdict"] == "pass"


def test_parse_structured_verdict_block():
    assert _default_parse("VERDICT: block\n\nThe post implies a guaranteed return.")["verdict"] == "block"


def test_parse_structured_verdict_pass():
    assert _default_parse("VERDICT: pass\nEducational; does not violate any rule.")["verdict"] == "pass"


def test_parse_leading_bare_block_token():
    assert _default_parse("block weak sourcing")["verdict"] == "block"


def test_parse_leading_bare_pass_token():
    assert _default_parse("pass")["verdict"] == "pass"
