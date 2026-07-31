"""TDD: ACTIVATE self-evolution scoring in the live loop.

The columns (helped/misled/confidence) + attribute() shipped in Phase 1. This wires
them into the harness: after a cycle, credit/blame the lessons it RELIED on, keyed by
the terminal outcome. Generic — the harness only knows the meta['relied'] provenance
contract ([[domain, step, id], ...]); domains decide which namespaces to recall from.
"""
import harness_core.agent_memory as m
from harness_core.agent_base import Artifact, Idea, Verdict
from harness_core.agent_memory import AgentMemory
from harness_core.generic_harness import GenericHarness


def mf_factory(tmp_path):
    db = str(tmp_path / "m.db")
    return lambda d, s: AgentMemory(d, s, db_path=db)


def _harness(mf):
    # _attribute only touches memory_factory + ctx; config/store are irrelevant here.
    return GenericHarness(config=None, store=None, memory_factory=mf)


def test_credit_set_includes_published():
    assert "published" in m._CREDIT      # the harness success outcome must credit, not blame


def test_attribute_credits_relied_lessons_on_published(tmp_path):
    mf = mf_factory(tmp_path)
    les = mf("engineering", "ideate").add("a good RCA lesson")
    _harness(mf)._attribute({"idea": Idea(meta={"relied": [["engineering", "ideate", les.id]]}),
                             "artifact": None, "outcome": "published"})
    got = mf("engineering", "ideate").get(les.id)
    assert got.helped == 1 and got.misled == 0 and got.confidence == 1.0


def test_attribute_blames_relied_lessons_on_rejected(tmp_path):
    mf = mf_factory(tmp_path)
    les = mf("engineering", "create").add("a misleading approach")
    art = Artifact(meta={"relied": [["engineering", "create", les.id]]})
    _harness(mf)._attribute({"idea": None, "artifact": art, "outcome": "rejected"})
    assert mf("engineering", "create").get(les.id).misled == 1


def test_attribute_merges_idea_and_artifact_and_dedups(tmp_path):
    mf = mf_factory(tmp_path)
    a = mf("engineering", "ideate").add("ideate lesson")
    b = mf("engineering", "create").add("create lesson")
    idea = Idea(meta={"relied": [["engineering", "ideate", a.id]]})
    art = Artifact(meta={"relied": [["engineering", "ideate", a.id],        # dup of idea's
                                    ["engineering", "create", b.id]]})
    _harness(mf)._attribute({"idea": idea, "artifact": art, "outcome": "published"})
    assert mf("engineering", "ideate").get(a.id).helped == 1                # credited once
    assert mf("engineering", "create").get(b.id).helped == 1


def test_attribute_credits_judge_verdict_relied(tmp_path):
    mf = mf_factory(tmp_path)
    les = mf("engineering", "judge").add("a review objection that held")
    v = Verdict(verdict="pass", meta={"relied": [["engineering", "judge", les.id]]})
    _harness(mf)._attribute({"idea": None, "artifact": None, "verdict": v,
                             "outcome": "published"})
    assert mf("engineering", "judge").get(les.id).helped == 1


def test_attribute_skips_non_terminal_outcomes(tmp_path):
    mf = mf_factory(tmp_path)
    les = mf("engineering", "ideate").add("a lesson")
    for oc in ("incomplete", "escalate", "failed"):     # parked/errored -> no signal
        _harness(mf)._attribute({"idea": Idea(meta={"relied": [["engineering", "ideate", les.id]]}),
                                 "artifact": None, "outcome": oc})
    got = mf("engineering", "ideate").get(les.id)
    assert got.helped == 0 and got.misled == 0
