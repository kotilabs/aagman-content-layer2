"""Phase-7 feature TDD: recurrence -> architectural-review escalation.

When an AREA is fixed again and again (a recurring issue arriving as variations),
the harness should stop proposing patch N+1 silently and instead FLAG the plan for
an architectural review — surfaced at the existing HumanGate('plan') so a human
decides patch-vs-rearchitect. FixMemory logs fix outcomes per area; RCAAgent reads
that history and stamps the flag when an area crosses a recurrence threshold.
"""
import os
from pathlib import Path

from harness_core.agent_base import Idea, Signal
from harness_core.agent_memory import AgentMemory
from harness_core.llm_router import LLMRouter
from harness_engineering.agents import (
    RCAAgent, FixMemory, _area_of, _recurrence_stats,
    RECURRENCE_THRESHOLD, RECURRENCE_ADVERSE_THRESHOLD,
)

_REPO = Path(__file__).resolve().parents[2]
DIST = _REPO / "harness_engineering" / "distilled"
LAYER_GT = str(DIST / "layer_ground_truth.json")
FILE_REL = str(DIST / "file_relationships.json")
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


def _log_fix(mf, entry_file, outcome, issue):
    """Simulate a completed fix by recording its outcome via FixMemory."""
    FixMemory(mf).record(
        Signal(id=f"eng:{issue}", domain="engineering", source="github",
               payload={"number": issue}),
        Idea(summary="rca", plan={"entry_file": entry_file, "layer": "typescript"}),
        None, outcome)


# --------------------------------------------------------------------------- #
# area key + stats
# --------------------------------------------------------------------------- #
def test_area_of_uses_two_segment_path_key():
    assert _area_of("backend/src/mastra/utils/risk-calculations.ts", "typescript") == "backend/src"
    assert _area_of("", "python") == "python"
    assert _area_of("", "") == "unknown"


def test_fixmemory_logs_fix_event_tagged_by_area(tmp_path):
    mf = mem_factory(tmp_path)
    _log_fix(mf, "backend/src/mastra/utils/risk-calculations.ts", "published", 1)
    events = mf("engineering", "fixlog").all()
    assert len(events) == 1
    assert events[0].tags == "backend/src"


def test_recurrence_stats_counts_total_and_adverse_by_area(tmp_path):
    mf = mem_factory(tmp_path)
    _log_fix(mf, "backend/src/a.ts", "published", 1)
    _log_fix(mf, "backend/src/b.ts", "rejected", 2)
    _log_fix(mf, "backend/src/c.ts", "failed", 3)
    _log_fix(mf, "backtester/packages/x.py", "published", 4)
    s = _recurrence_stats(mf, "backend/src")
    assert s["total"] == 3 and s["adverse"] == 2  # rejected + failed
    assert _recurrence_stats(mf, "backtester/packages")["total"] == 1


# --------------------------------------------------------------------------- #
# RCAAgent flags architectural review
# --------------------------------------------------------------------------- #
def _risk_issue():
    return Signal(id="eng:99", domain="engineering", source="github",
                  payload={"title": "risk_blocked on RELIANCE", "body": "rule 6.1.1"})


def test_rca_flags_architectural_review_when_area_recurs(tmp_path):
    mf = mem_factory(tmp_path)
    # risk_blocked routes to backend/src (risk-calculations.ts) — seed 3 prior fixes there
    for i in range(RECURRENCE_THRESHOLD):
        _log_fix(mf, "backend/src/mastra/utils/risk-calculations.ts", "published", i)
    rec = []
    idea = RCAAgent(make_router("plan", rec), mf, LAYER_GT, FILE_REL, RISK_RULES).ideate(_risk_issue())
    assert idea.plan["architectural_review"] is True
    assert idea.plan["area"] == "backend/src"
    assert "ARCHITECTURAL REVIEW" in idea.summary.upper()
    # recurrence context also reached the RCA prompt
    assert any("recurr" in c["prompt"].lower() for c in rec)


def test_rca_no_flag_below_threshold(tmp_path):
    mf = mem_factory(tmp_path)
    _log_fix(mf, "backend/src/mastra/utils/risk-calculations.ts", "published", 1)  # only 1
    idea = RCAAgent(make_router("plan"), mf, LAYER_GT, FILE_REL, RISK_RULES).ideate(_risk_issue())
    assert idea.plan["architectural_review"] is False
    assert "ARCHITECTURAL REVIEW" not in idea.summary.upper()


def test_rca_flags_on_adverse_recurrence_even_below_total(tmp_path):
    mf = mem_factory(tmp_path)
    # 2 reopened/bounced fixes (>= adverse threshold) but total < RECURRENCE_THRESHOLD
    for i in range(RECURRENCE_ADVERSE_THRESHOLD):
        _log_fix(mf, "backend/src/mastra/utils/risk-calculations.ts", "rejected", i)
    idea = RCAAgent(make_router("plan"), mf, LAYER_GT, FILE_REL, RISK_RULES).ideate(_risk_issue())
    assert idea.plan["architectural_review"] is True


def test_rca_does_not_flag_unknown_area(tmp_path):
    mf = mem_factory(tmp_path)
    # an issue that doesn't route to a known layer -> area unknown -> never flagged
    for i in range(5):
        _log_fix(mf, "", "rejected", i)  # area falls back to layer 'typescript' here
    unrouted = Signal(id="eng:1", domain="engineering", source="github",
                      payload={"title": "some vague UI glitch", "body": "unclear"})
    idea = RCAAgent(make_router("plan"), mf, LAYER_GT, FILE_REL, RISK_RULES).ideate(unrouted)
    assert idea.plan["architectural_review"] is False
