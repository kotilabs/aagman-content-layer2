"""TDD: make the distilled repo nuance actually REACH the code/fix/RCA prompts.

Three gaps this locks down (all found by tracing agents.py):
  1. CodeFixAgent never recalled fix_success_patterns nor co-change siblings —
     the fix step was nuance-blind. It must now inject both.
  2. classifier_examples (206 real issues) were seeded to engineering/sense but
     NO agent read them. RCAAgent must recall similar past issues into its prompt.
  3. _route_layer only matched 4 hardcoded risk keywords; every non-risk issue
     routed to layer='' entry_file=''. Routing must use the LLM's STATED entry
     file (the RCA prompt already asks for it), keyword route as fallback.
"""
import json
import os

from harness_core.agent_base import Idea, Signal
from harness_core.agent_memory import AgentMemory
from harness_core.llm_router import LLMRouter
from harness_engineering.agents import RCAAgent, CodeFixAgent

from pathlib import Path

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


def _issue(title, body=""):
    return Signal(id="eng:1", domain="engineering", source="github",
                  payload={"title": title, "body": body})


# --------------------------------------------------------------------------- #
# 1. CodeFixAgent injects fix_success_patterns + co-change siblings
# --------------------------------------------------------------------------- #
def test_fix_prompt_carries_recalled_fix_patterns_and_cochange(tmp_path):
    mf = mem_factory(tmp_path)
    mf("engineering", "create").add(
        "approach=fix(screener): guard e.toFixed non-number (#2288) | merged_first_try=True")
    file_rel = {
        "areas": {"backend/src": ["backend/src/x.ts"]},
        "co_change": [["backend/src/mastra/utils/risk-calculations.ts",
                       "backend/src/mastra/agents/aagman-risk-agent.ts"]],
    }
    rel = tmp_path / "rel.json"
    rel.write_text(json.dumps(file_rel))

    seen = []
    agent = CodeFixAgent(runner_fn=lambda task, wd: seen.append(task) or "done",
                         workdir=str(tmp_path), memory_factory=mf, file_rel=str(rel))
    agent.create(Idea(summary="screener crash toFixed rca", plan={
        "layer": "typescript",
        "entry_file": "backend/src/mastra/utils/risk-calculations.ts",
        "issue": {"number": 2288, "title": "screener crashes toFixed"}}))

    task = seen[0]
    assert "e.toFixed" in task                      # recalled fix pattern reached the prompt
    assert "aagman-risk-agent.ts" in task           # co-change sibling surfaced for blast-radius


def test_fix_prompt_no_context_blocks_when_unseeded(tmp_path):
    seen = []
    CodeFixAgent(runner_fn=lambda task, wd: seen.append(task) or "ok",
                 workdir=str(tmp_path)).create(
        Idea(summary="x", plan={"entry_file": "", "issue": {"number": 1}}))
    assert "CO-CHANGE" not in seen[0] and "SIMILAR FIXES" not in seen[0]


# --------------------------------------------------------------------------- #
# 2. RCAAgent recalls similar past issues (classifier_examples now alive)
# --------------------------------------------------------------------------- #
def test_rca_prompt_includes_similar_past_issues(tmp_path):
    mf = mem_factory(tmp_path)
    mf("engineering", "sense").add(
        "title=Sector screener crashes with e.toFixed is not a function | label=screener")
    rec = []
    RCAAgent(make_router("plan", rec), mf, LAYER_GT, FILE_REL, RISK_RULES).ideate(
        _issue("screener crashes toFixed", "any sector query crashes"))
    assert any("similar" in c["prompt"].lower() and "screener" in c["prompt"].lower()
               for c in rec)


# --------------------------------------------------------------------------- #
# 3. Routing uses the LLM's stated entry file for a non-risk issue
# --------------------------------------------------------------------------- #
def test_routing_uses_llm_stated_entry_file(tmp_path):
    mf = mem_factory(tmp_path)
    reply = ("RCA: chart y-axis mis-scaled.\n"
             "LAYER: typescript\n"
             "ENTRY_FILE: backend/src/mastra/tools/charts/chart-tool.ts\n"
             "confidence: 0.9")
    idea = RCAAgent(make_router(reply), mf, LAYER_GT, FILE_REL, RISK_RULES).ideate(
        _issue("chart axis wrong", "y-axis broken on line chart"))
    assert idea.plan["entry_file"] == "backend/src/mastra/tools/charts/chart-tool.ts"
    assert idea.plan["layer"] == "typescript"
    assert idea.plan["area"] == "backend/src"


def test_rca_uses_retrieval_route_when_index_present(tmp_path):
    # a non-risk issue the keyword router can't handle; retrieval index supplies it
    idx = tmp_path / "route_index.json"
    idx.write_text(json.dumps([
        {"issue_text": "chart y-axis mis-scaled on line chart", "area": "frontend/src",
         "entry_file": "frontend/src/charts/axis.tsx"},
        {"issue_text": "chart axis broken scaling wrong values", "area": "frontend/src",
         "entry_file": "frontend/src/charts/axis.tsx"},
    ]))
    mf = mem_factory(tmp_path)
    idea = RCAAgent(make_router("plan"), mf, LAYER_GT, FILE_REL, RISK_RULES,
                    route_index_path=str(idx)).ideate(
        _issue("chart y-axis wrong", "axis scaling looks broken on the line chart"))
    assert idea.plan["entry_file"] == "frontend/src/charts/axis.tsx"
    assert idea.plan["area"] == "frontend/src"
    assert idea.plan["layer"] == "typescript"


def test_routing_layer_stays_consistent_with_entry_file_despite_markdown(tmp_path):
    # live-run bug: RCA wrote '**LAYER: typescript-backend**' / '**ENTRY_FILE: ...ts**';
    # the ** defeated the layer regex so layer fell back stale while entry_file parsed.
    mf = mem_factory(tmp_path)
    reply = ("RCA: backend coverage bug.\n"
             "**LAYER: typescript-backend**\n"
             "**ENTRY_FILE: backend/src/mastra/tools/supervisor/handlers/strategy.handler.ts**\n"
             "confidence: 0.9")
    idea = RCAAgent(make_router(reply), mf, LAYER_GT, FILE_REL, RISK_RULES).ideate(
        _issue("NIFTY 500 backtest falsely blocked", "coverage pre-check no market data"))
    assert idea.plan["entry_file"].endswith("strategy.handler.ts")
    assert idea.plan["layer"] == "typescript"     # derived from the .ts file, not a stale prior


def test_routing_falls_back_to_keyword_when_llm_states_nothing(tmp_path):
    mf = mem_factory(tmp_path)
    # keyword route still handles the canonical risk case when the model is terse
    idea = RCAAgent(make_router("plan"), mf, LAYER_GT, FILE_REL, RISK_RULES).ideate(
        _issue("risk_blocked on RELIANCE", "rule 6.1.1"))
    assert idea.plan["entry_file"] == "backend/src/mastra/utils/risk-calculations.ts"
    assert idea.plan["layer"] == "typescript"
