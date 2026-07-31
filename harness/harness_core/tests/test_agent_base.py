"""Phase-1 TDD: agent_base.py — the agent contract (ABCs) + loop data types.

Every domain agent implements exactly one ABC. A config naming a misshapen agent
(missing a required method) must fail AT LOAD — enforced here by ABC instantiation
raising TypeError, which domain_config's loader relies on.
"""
import pytest

from harness_core.agent_base import (
    Signal, Idea, Artifact, Verdict, Receipt,
    SenseAgent, IdeateAgent, CreateAgent, JudgeAgent, PublishAgent, LearnAgent,
)


# ---- data types ----------------------------------------------------------- #
def test_signal_derives_stable_fingerprint_for_dedup():
    s1 = Signal(id="eng-issue-1", domain="engineering", source="github",
                payload={"title": "bug"})
    s2 = Signal(id="eng-issue-1", domain="engineering", source="github",
                payload={"title": "bug"})
    assert s1.fingerprint  # non-empty
    assert s1.fingerprint == s2.fingerprint  # same content -> same dedup key


def test_signal_fingerprint_changes_with_payload():
    a = Signal(id="x", domain="d", source="s", payload={"t": "a"})
    b = Signal(id="x", domain="d", source="s", payload={"t": "b"})
    assert a.fingerprint != b.fingerprint


def test_artifact_defaults():
    art = Artifact(body="hello", kind="text")
    assert art.body == "hello"
    assert art.kind == "text"
    assert art.meta == {}


def test_verdict_and_receipt_defaults():
    assert Verdict().verdict == "pass"
    assert Receipt(channel="linkedin", ref="123").ref == "123"


# ---- ABC enforcement (the "fail at load" guarantee) ----------------------- #
def test_sense_agent_is_abstract():
    with pytest.raises(TypeError):
        SenseAgent()


def test_incomplete_sense_agent_cannot_instantiate():
    class Bad(SenseAgent):
        pass
    with pytest.raises(TypeError):
        Bad()

    class Good(SenseAgent):
        def sense(self, sources):
            return []
    assert Good().sense([]) == []


def test_create_agent_requires_both_create_and_revise():
    class OnlyCreate(CreateAgent):
        def create(self, idea):
            return Artifact("x", "text")
    with pytest.raises(TypeError):
        OnlyCreate()  # missing revise()

    class Full(CreateAgent):
        def create(self, idea):
            return Artifact("x", "text")
        def revise(self, artifact, issues):
            return artifact
    assert isinstance(Full().create(None), Artifact)


def test_all_role_abcs_enforce_their_method():
    for abc_cls in (IdeateAgent, JudgeAgent, PublishAgent, LearnAgent):
        with pytest.raises(TypeError):
            abc_cls()
