"""Phase-4 TDD: the six content-domain agents.

The network boundary (the actual model call) is the ONLY thing stubbed — via an
injected completion_fn on a REAL LLMRouter. Everything else is exercised for
real: chain resolution from models.yaml, prompt construction, the mandatory RIA
disclosure prepend, the multi-model panel tally, outbox writing, memory writes.
This is dependency-injection testing of wiring + logic, not a content-quality
claim (that needs live keys, Phase 7).
"""
import json
import os
from pathlib import Path

from harness_core.agent_base import (
    Signal, Idea, Artifact, Verdict,
    SenseAgent, IdeateAgent, CreateAgent, JudgeAgent, PublishAgent, LearnAgent,
)
from harness_core.agent_memory import AgentMemory
from harness_core.llm_router import LLMRouter
from harness_content.agents import (
    ContentSensor, ContentStrategist, ContentCreator, ContentJudge,
    ContentPublisher, ContentMemory, RIA_NAME, RIA_REG,
)

_REPO = Path(__file__).resolve().parents[2]
BRAND = str(_REPO / "harness_content" / "BRAND_VOICE.md")
EXAMPLES = str(_REPO / "harness_content" / "distilled" / "examples.json")
CHANNELS = str(_REPO / "harness_content" / "distilled" / "channel_rules.json")


def make_router(reply="ok", record=None):
    """Real LLMRouter, fake completion. `reply` is str or fn(model, prompt)->str."""
    def fn(model, prompt, **kw):
        if record is not None:
            record.append({"model": model, "prompt": prompt})
        text = reply(model, prompt) if callable(reply) else reply
        return {"text": text, "tokens": 5}
    # cost log -> devnull so tests never pollute the real budget ledger
    return LLMRouter(completion_fn=fn, cost_log_path=os.devnull)


def mem_factory(tmp_path):
    db = str(tmp_path / "memory.db")
    return lambda d, s: AgentMemory(d, s, db_path=db)


# --------------------------------------------------------------------------- #
# ContentSensor — briefs inbox folder is the Phase-1 sensor
# --------------------------------------------------------------------------- #
def test_sensor_reads_briefs_from_inbox(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "a.md").write_text("Explain rate cuts to retail investors")
    (inbox / "b.json").write_text(json.dumps({"brief": "Nifty PE explainer",
                                              "channel": "linkedin"}))
    (inbox / "ignore.png").write_bytes(b"\x89PNG")
    sensor = ContentSensor(str(inbox))
    signals = sensor.sense(None)
    assert isinstance(sensor, SenseAgent)
    assert len(signals) == 2
    assert all(isinstance(s, Signal) and s.domain == "content" for s in signals)
    briefs = {s.payload["brief"] for s in signals}
    assert "Explain rate cuts to retail investors" in briefs
    assert any(s.payload.get("channel") == "linkedin" for s in signals)


def test_sensor_empty_inbox_returns_nothing(tmp_path):
    (tmp_path / "inbox").mkdir()
    assert ContentSensor(str(tmp_path / "inbox")).sense(None) == []


def test_sensor_distinct_briefs_get_distinct_fingerprints(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "a.md").write_text("brief one")
    (inbox / "b.md").write_text("brief two")
    sigs = ContentSensor(str(inbox)).sense(None)
    assert len({s.fingerprint for s in sigs}) == 2


# --------------------------------------------------------------------------- #
# ContentStrategist (ideate) — Sonnet, educational framing, uses brand voice + memory
# --------------------------------------------------------------------------- #
def test_strategist_produces_idea_with_educational_framing(tmp_path):
    rec = []
    router = make_router(reply="ANGLE: explain the mechanism, no calls", record=rec)
    strat = ContentStrategist(router, mem_factory(tmp_path), BRAND, EXAMPLES)
    idea = strat.ideate(Signal(id="x", domain="content", source="inbox",
                               payload={"brief": "rate cuts", "channel": "linkedin"}))
    assert isinstance(strat, IdeateAgent)
    assert isinstance(idea, Idea) and idea.summary
    assert idea.plan.get("channel") == "linkedin"
    # the prompt carried the educational-only framing and the brief
    assert "educational" in rec[0]["prompt"].lower()
    assert "rate cuts" in rec[0]["prompt"]


def test_strategist_injects_memory_lessons_into_prompt(tmp_path):
    mf = mem_factory(tmp_path)
    mf("content", "ideate").add("Lead with the sourced number, never a hype adjective",
                                tags="voice")
    rec = []
    router = make_router(reply="ok", record=rec)
    ContentStrategist(router, mf, BRAND, EXAMPLES).ideate(
        Signal(id="x", domain="content", source="inbox", payload={"brief": "hype adjective"}))
    assert "sourced number" in rec[0]["prompt"]


# --------------------------------------------------------------------------- #
# ContentCreator (create) — parallel fan_out text/image; text begins w/ disclosure
# --------------------------------------------------------------------------- #
def _idea(channel="linkedin", fan="text"):
    return Idea(summary="explain rate cuts", plan={"channel": channel},
                confidence=0.9, meta={"fan_out": fan})


def test_creator_text_artifact_begins_with_ria_disclosure(tmp_path):
    router = make_router(reply="Here is an educational note on rate cuts.")
    art = ContentCreator(router, mem_factory(tmp_path), BRAND, CHANNELS).create(_idea(fan="text"))
    assert isinstance(art, Artifact) and art.kind == "text"
    assert RIA_NAME in art.body and RIA_REG in art.body
    # disclosure is at the START (mandatory RIA id at start of every post)
    assert RIA_NAME in art.body.split("\n\n", 1)[0]


def test_creator_image_artifact_is_prompt_only(tmp_path):
    router = make_router(reply="A clean line chart of the repo rate over 12 months")
    art = ContentCreator(router, mem_factory(tmp_path), BRAND, CHANNELS).create(_idea(fan="image"))
    assert art.kind == "image"
    assert art.body


def test_creator_revise_keeps_disclosure_and_addresses_issues(tmp_path):
    rec = []
    router = make_router(reply="Revised educational note.", record=rec)
    creator = ContentCreator(router, mem_factory(tmp_path), BRAND, CHANNELS)
    art = Artifact(body="old", kind="text", meta={"channel": "linkedin"})
    revised = creator.revise(art, ["too promotional", "add a source"])
    assert RIA_NAME in revised.body and RIA_REG in revised.body
    assert "too promotional" in rec[0]["prompt"]


# --------------------------------------------------------------------------- #
# ContentJudge (judge) — multi-model quality panel; drives loop_limit-2 revise
# --------------------------------------------------------------------------- #
def test_judge_passes_clean_artifact(tmp_path):
    router = make_router(reply="pass")
    judge = ContentJudge(router)
    v = judge.judge(Artifact(body="clean educational post", kind="text"), mem_factory(tmp_path))
    assert isinstance(judge, JudgeAgent)
    assert isinstance(v, Verdict) and v.verdict == "pass"


def test_judge_blocks_when_panel_rejects(tmp_path):
    router = make_router(reply="block: reads like a buy recommendation")
    v = ContentJudge(router).judge(Artifact(body="buy this now", kind="text"),
                                   mem_factory(tmp_path))
    assert v.verdict == "block"
    assert v.issues


def test_judge_injects_judge_lessons_into_criteria(tmp_path):
    mf = mem_factory(tmp_path)
    mf("content", "judge").add("Reject content that ends on a call-to-action", tags="rejected")
    rec = []
    router = make_router(reply="pass", record=rec)
    ContentJudge(router).judge(Artifact(body="call-to-action", kind="text"), mf)
    assert any("call-to-action" in c["prompt"] for c in rec)


# --------------------------------------------------------------------------- #
# ContentPublisher (publish) — writes final artifact to outbox/{channel}/
# --------------------------------------------------------------------------- #
def test_publisher_writes_to_outbox_with_metadata(tmp_path):
    outbox = tmp_path / "outbox"
    pub = ContentPublisher(str(outbox))
    art = Artifact(body="final post body", kind="text", meta={"channel": "linkedin"})
    receipt = pub.publish(art, ["linkedin"])
    assert isinstance(pub, PublishAgent)
    assert receipt.channel == "linkedin"
    written = Path(receipt.ref)
    assert written.exists() and written.parent.name == "linkedin"
    assert "final post body" in written.read_text()


# --------------------------------------------------------------------------- #
# ContentMemory (learn) — outcome-based lessons into content namespaces
# --------------------------------------------------------------------------- #
def test_memory_records_outcome_lesson(tmp_path):
    mf = mem_factory(tmp_path)
    before = mf("content", "create").count()
    ContentMemory(mf).record(
        Signal(id="x", domain="content", source="inbox", payload={"brief": "rate cuts"}),
        _idea(), Artifact(body="post", kind="text"), "published")
    assert isinstance(ContentMemory(mf), LearnAgent)
    assert mf("content", "create").count() == before + 1
