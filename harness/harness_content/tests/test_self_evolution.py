"""TDD: content agents stamp relied provenance so the CONTENT domain self-evolves
too (same mechanism as engineering; the harness _attribute() is already generic)."""
import os
from pathlib import Path

from harness_core.agent_base import Signal
from harness_core.agent_memory import AgentMemory
from harness_core.domain_config import StepConfig
from harness_core.generic_harness import GenericHarness
from harness_core.llm_router import LLMRouter
from harness_core.agent_base import Artifact
from harness_content.agents import ContentStrategist, ContentJudge, ContentMemory, _recall

_REPO = Path(__file__).resolve().parents[2]
BRAND = str(_REPO / "harness_content" / "SEBI_RULES.md")            # any readable file
EXAMPLES = str(_REPO / "harness_content" / "distilled" / "examples.json")


def make_router(reply="angle"):
    return LLMRouter(completion_fn=lambda mdl, p, **k: {"text": reply, "tokens": 5},
                     cost_log_path=os.devnull)


def mf_factory(tmp_path):
    db = str(tmp_path / "m.db")
    return lambda d, s: AgentMemory(d, s, db_path=db)


def test_content_recall_returns_texts_and_provenance(tmp_path):
    mf = mf_factory(tmp_path)
    les = mf("content", "ideate").add("options education angle worked well")
    texts, relied = _recall(mf, "content", "ideate", "options education")
    assert "options education angle worked well" in texts
    assert ["content", "ideate", les.id] in relied


def test_content_ideate_stamps_relied(tmp_path):
    mf = mf_factory(tmp_path)
    seed = mf("content", "ideate").add("options education angle that landed")
    idea = ContentStrategist(make_router("angle"), mf, BRAND, EXAMPLES).ideate(
        Signal(id="content:x", domain="content", source="inbox",
               payload={"brief": "explain options education", "channel": "linkedin"}))
    assert any(r[2] == seed.id for r in idea.meta.get("relied", []))


def test_content_judge_stamps_relied_on_verdict(tmp_path):
    mf = mf_factory(tmp_path)
    les = mf("content", "judge").add("past rejection: ended on a CTA")
    v = ContentJudge(make_router("VERDICT: pass")).judge(
        Artifact(body="educational post ending on an open question", kind="text"), mf)
    assert any(r[2] == les.id for r in v.meta.get("relied", []))


def test_content_self_evolves_end_to_end(tmp_path):
    mf = mf_factory(tmp_path)
    seed = mf("content", "ideate").add("explain options education clearly and simply")
    idea = ContentStrategist(make_router("angle"), mf, BRAND, EXAMPLES).ideate(
        Signal(id="content:x", domain="content", source="inbox",
               payload={"brief": "explain options education", "channel": "linkedin"}))

    class _Cfg:
        def step(self, name):
            return StepConfig("learn", ContentMemory(mf)) if name == "learn" else None

    sig = Signal(id="content:x", domain="content", source="inbox",
                 payload={"brief": "explain options"})
    GenericHarness(config=_Cfg(), store=None, memory_factory=mf)._learn(
        sig, {"signal": sig, "idea": idea, "artifact": None, "outcome": "published"})
    got = mf("content", "ideate").get(seed.id)
    assert got.helped == 1 and got.confidence == 1.0
