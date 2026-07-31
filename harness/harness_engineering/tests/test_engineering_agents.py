"""Phase-5 TDD: the six engineering-domain agents.

External effects (GitHub via gh, the Claude Code subprocess, PR creation) are
injected as callables so the agents are exercised offline and deterministically.
The router's network boundary is stubbed the same way as the content tests. What
is tested for real: signal shape, RCA prompt carries the four laws + layer
routing, the create->revise contract, adversarial objections reach the panel,
branch naming, memory writes.
"""
import json
import os
from pathlib import Path

from harness_core.agent_base import (
    Signal, Idea, Artifact, Verdict, Receipt,
    SenseAgent, IdeateAgent, CreateAgent, JudgeAgent, PublishAgent, LearnAgent,
)
from harness_core.agent_memory import AgentMemory
from harness_core.llm_router import LLMRouter
from harness_engineering.agents import (
    IssueListener, RCAAgent, CodeFixAgent, AdversarialReview, PRAgent, FixMemory,
)

_REPO = Path(__file__).resolve().parents[2]
DIST = _REPO / "harness_engineering" / "distilled"
LAYER_GT = str(DIST / "layer_ground_truth.json")
FILE_REL = str(DIST / "file_relationships.json")
ADV_VOCAB = str(DIST / "adversarial_vocab.json")
RISK_RULES = str(_REPO / "harness_engineering" / "RISK_RULES.md")


def make_router(reply="ok", record=None):
    def fn(model, prompt, **kw):
        if record is not None:
            record.append({"model": model, "prompt": prompt})
        return {"text": reply(model, prompt) if callable(reply) else reply, "tokens": 5}
    return LLMRouter(completion_fn=fn, cost_log_path=os.devnull)


def mem_factory(tmp_path):
    db = str(tmp_path / "memory.db")
    return lambda d, s: AgentMemory(d, s, db_path=db)


# --------------------------------------------------------------------------- #
# IssueListener (sense) — polls gh issues assigned to ajitk2003 (fetch injected)
# --------------------------------------------------------------------------- #
def test_issuelistener_maps_issues_to_signals():
    issues = [{"number": 2321, "title": "backtest falsely blocked",
               "body": "coverage keys on venue", "labels": [{"name": "bug"}, {"name": "p1"}]}]
    listener = IssueListener(fetch_fn=lambda repo, assignee: issues)
    sigs = listener.sense(None)
    assert isinstance(listener, SenseAgent)
    assert len(sigs) == 1
    s = sigs[0]
    assert s.domain == "engineering" and s.id == "eng:2321"
    assert s.payload["title"] == "backtest falsely blocked"
    assert "bug" in s.payload["labels"]


def test_issuelistener_empty_when_no_issues():
    assert IssueListener(fetch_fn=lambda r, a: []).sense(None) == []


# --------------------------------------------------------------------------- #
# RCAAgent (ideate) — four laws + layer routing + second pass on low confidence
# --------------------------------------------------------------------------- #
def _rca(router, tmp_path):
    return RCAAgent(router, mem_factory(tmp_path), LAYER_GT, FILE_REL, RISK_RULES)


def test_rca_prompt_carries_four_laws_and_issue(tmp_path):
    rec = []
    rca = _rca(make_router("root cause: X. layer: typescript. tasks: 1,2", rec), tmp_path)
    idea = rca.ideate(Signal(id="eng:1", domain="engineering", source="github",
                             payload={"title": "risk_blocked on RELIANCE", "body": "rule 6.1.1"}))
    assert isinstance(rca, IdeateAgent) and isinstance(idea, Idea)
    p = rec[0]["prompt"].lower()
    assert "pre-existing" in p            # law (b) present in the RCA prompt
    assert "root cause" in p              # laws a/b
    assert "risk_blocked" in p            # the issue text is in the prompt


def test_rca_routes_risk_blocked_to_typescript_layer(tmp_path):
    idea = _rca(make_router("ok"), tmp_path).ideate(
        Signal(id="eng:1", domain="engineering", source="github",
               payload={"title": "risk_blocked", "body": "rule 6.2.1 maxDD"}))
    assert idea.plan.get("layer") == "typescript"
    assert "risk-calculations.ts" in idea.plan.get("entry_file", "")


def test_rca_second_pass_when_confidence_low(tmp_path):
    # reply signals low confidence first, higher on the retry
    calls = {"n": 0}
    def reply(model, prompt):
        calls["n"] += 1
        return "confidence: 0.5 uncertain" if calls["n"] == 1 else "confidence: 0.9 firm"
    idea = _rca(make_router(reply), tmp_path).ideate(
        Signal(id="eng:1", domain="engineering", source="github",
               payload={"title": "weird bug", "body": "unclear"}))
    assert calls["n"] >= 2  # a second pass ran


# --------------------------------------------------------------------------- #
# CodeFixAgent (create) — Claude Code runner injected; serial; test-first framing
# --------------------------------------------------------------------------- #
def test_codefix_invokes_runner_and_returns_patch(tmp_path):
    seen = {}
    def runner(task, workdir):
        seen["task"] = task
        return "wrote failing test + fix in risk-calculations.ts"
    agent = CodeFixAgent(runner_fn=runner, workdir=str(tmp_path))
    idea = Idea(summary="fix risk calc", plan={"layer": "typescript",
                "entry_file": "risk-calculations.ts", "issue": {"number": 42}})
    art = agent.create(idea)
    assert isinstance(agent, CreateAgent) and isinstance(art, Artifact)
    assert art.kind == "patch" and art.body
    assert "test" in seen["task"].lower()  # runner told to write the test first


def test_codefix_revise_passes_issues_to_runner(tmp_path):
    seen = {}
    agent = CodeFixAgent(runner_fn=lambda task, wd: seen.setdefault("t", task) or "patched",
                         workdir=str(tmp_path))
    agent.revise(Artifact(body="old", kind="patch", meta={"issue_number": 42}),
                 ["reviewer: patch not root fix"])
    assert "patch not root fix" in seen["t"]


# --------------------------------------------------------------------------- #
# AdversarialReview (judge) — objections vocabulary reaches the panel
# --------------------------------------------------------------------------- #
def test_adversarial_review_passes_clean_fix(tmp_path):
    review = AdversarialReview(make_router("pass"), ADV_VOCAB)
    v = review.judge(Artifact(body="root-cause fix with test", kind="patch"),
                     mem_factory(tmp_path))
    assert isinstance(review, JudgeAgent) and isinstance(v, Verdict)
    assert v.verdict == "pass"


def test_adversarial_review_blocks_and_loads_objections(tmp_path):
    rec = []
    review = AdversarialReview(make_router("block: this is a patch not a root fix", rec), ADV_VOCAB)
    v = review.judge(Artifact(body="quick patch", kind="patch"), mem_factory(tmp_path))
    assert v.verdict == "block"
    # the adversarial objection vocabulary is injected into the review prompt
    assert any("objection" in c["prompt"].lower() or "root" in c["prompt"].lower()
               for c in rec)


# --------------------------------------------------------------------------- #
# PRAgent (publish) — branch ajit/fix-{n}, assign amit-kotidev (gh injected)
# --------------------------------------------------------------------------- #
def test_pragent_opens_branch_and_assigns(tmp_path):
    seen = {}
    def pr_fn(branch, title, body, assignee):
        seen.update(branch=branch, assignee=assignee, body=body)
        return "https://github.com/kotilabs/aagman-v2/pull/999"
    agent = PRAgent(pr_fn=pr_fn)
    art = Artifact(body="the fix + RCA evidence", kind="patch",
                   meta={"issue_number": 2321, "rca": "root cause X"})
    receipt = agent.publish(art, ["github"])
    assert isinstance(agent, PublishAgent) and isinstance(receipt, Receipt)
    assert seen["branch"] == "ajit/fix-2321"
    assert seen["assignee"] == "amit-kotidev"
    assert receipt.ref.endswith("/999")


# --------------------------------------------------------------------------- #
# FixMemory (learn) — outcomes into engineering learn namespaces
# --------------------------------------------------------------------------- #
def test_fixmemory_records_outcome_into_namespaces(tmp_path):
    mf = mem_factory(tmp_path)
    before = mf("engineering", "ideate").count()
    FixMemory(mf).record(
        Signal(id="eng:1", domain="engineering", source="github",
               payload={"title": "bug", "number": 1}),
        Idea(summary="rca", plan={"layer": "typescript"}),
        Artifact(body="fix", kind="patch"), "published")
    assert isinstance(FixMemory(mf), LearnAgent)
    assert mf("engineering", "ideate").count() == before + 1
