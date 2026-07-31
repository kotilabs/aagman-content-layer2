"""TDD: engineering agents record which lessons they RELIED on (provenance), so the
harness can credit/blame them after the outcome. Populates meta['relied']."""
import os
from pathlib import Path

from harness_core.agent_base import Idea, Signal
from harness_core.agent_memory import AgentMemory
from harness_core.domain_config import StepConfig
from harness_core.generic_harness import GenericHarness
from harness_core.llm_router import LLMRouter
from harness_core.agent_base import Artifact
from harness_engineering.agents import (
    RCAAgent, CodeFixAgent, FixMemory, AdversarialReview, _recall,
)

_REPO = Path(__file__).resolve().parents[2]
DIST = _REPO / "harness_engineering" / "distilled"
LAYER_GT = str(DIST / "layer_ground_truth.json")
FILE_REL = str(DIST / "file_relationships.json")
RISK = str(_REPO / "harness_engineering" / "RISK_RULES.md")
ADV_VOCAB = str(DIST / "adversarial_vocab.json")


def make_router(reply="plan"):
    return LLMRouter(completion_fn=lambda mdl, p, **k: {"text": reply, "tokens": 5},
                     cost_log_path=os.devnull)


def mf_factory(tmp_path):
    db = str(tmp_path / "m.db")
    return lambda d, s: AgentMemory(d, s, db_path=db)


def test_recall_returns_texts_and_provenance(tmp_path):
    mf = mf_factory(tmp_path)
    les = mf("engineering", "ideate").add("screener crash lesson")
    texts, relied = _recall(mf, "engineering", "ideate", "screener crash")
    assert "screener crash lesson" in texts
    assert ["engineering", "ideate", les.id] in relied


def test_recall_empty_without_memory():
    assert _recall(None, "engineering", "ideate", "q") == ([], [])


def test_rca_idea_records_relied_lessons(tmp_path):
    mf = mf_factory(tmp_path)
    li = mf("engineering", "ideate").add("prior RCA about risk calculations")
    ls = mf("engineering", "sense").add("similar screener issue seen before")
    idea = RCAAgent(make_router("plan"), mf, LAYER_GT, FILE_REL, RISK).ideate(
        Signal(id="eng:1", domain="engineering", source="github",
               payload={"title": "screener risk calculations bug", "body": "risk"}))
    ids = {tuple(r) for r in idea.meta.get("relied", [])}
    assert ("engineering", "ideate", li.id) in ids
    assert ("engineering", "sense", ls.id) in ids


def test_codefix_artifact_carries_idea_plus_create_relied(tmp_path):
    mf = mf_factory(tmp_path)
    lc = mf("engineering", "create").add("similar screener fix approach landed")
    idea = Idea(summary="screener rca",
                plan={"entry_file": "backend/src/x.ts", "issue": {"number": 1, "title": "screener"}},
                meta={"relied": [["engineering", "ideate", "engineering.ideate.9"]]})
    art = CodeFixAgent(runner_fn=lambda t, w: "done", workdir=str(tmp_path),
                       memory_factory=mf).create(idea)
    ids = {tuple(r) for r in art.meta.get("relied", [])}
    assert ("engineering", "ideate", "engineering.ideate.9") in ids   # carried from idea
    assert ("engineering", "create", lc.id) in ids                    # added at create


def test_adversarial_review_stamps_relied_on_verdict(tmp_path):
    mf = mf_factory(tmp_path)
    les = mf("engineering", "judge").add("check for sibling breakage")
    v = AdversarialReview(make_router("VERDICT: pass"), ADV_VOCAB).judge(
        Artifact(body="a fix that checks sibling breakage risk"), mf)
    assert any(r[2] == les.id for r in v.meta.get("relied", []))


def test_learn_scores_relied_lessons_end_to_end(tmp_path):
    """The money test: a REAL RCAAgent idea flows through the REAL harness _learn on a
    'published' outcome and actually moves the relied lesson's helped/confidence —
    proving self-evolution is ACTIVE in the live loop, not just unit-wired."""
    mf = mf_factory(tmp_path)
    seed = mf("engineering", "ideate").add("prior RCA about risk calculations that landed")
    idea = RCAAgent(make_router("plan"), mf, LAYER_GT, FILE_REL, RISK).ideate(
        Signal(id="eng:1", domain="engineering", source="github",
               payload={"title": "risk calculations bug", "body": "risk"}))
    assert any(r[2] == seed.id for r in idea.meta["relied"])          # relied captured

    class _Cfg:                                                       # minimal config: learn only
        def step(self, name):
            return StepConfig("learn", FixMemory(mf)) if name == "learn" else None

    sig = Signal(id="eng:1", domain="engineering", source="github", payload={"number": 1})
    GenericHarness(config=_Cfg(), store=None, memory_factory=mf)._learn(
        sig, {"signal": sig, "idea": idea, "artifact": None, "outcome": "published"})

    got = mf("engineering", "ideate").get(seed.id)
    assert got.helped == 1 and got.misled == 0 and got.confidence == 1.0
