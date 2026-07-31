"""harness_configs/engineering_config.py — the ENGINEERING domain wiring.

The aagman-v2 test harness is wired as TWO TestGates (Decision 6: the test suite
is a GATE, not a step) running the REAL run_all.sh commands discovered in
TEST_HARNESS.md:
  - create gate (inner loop, per fix): run_all.sh --fast, fixable=True -> a red
    suite bounces back to CodeFixAgent. This is the fail-before/pass-after proof.
  - judge gate (outer net, pre-PR): the FULL run_all.sh, fixable=False -> a red
    suite ESCALATES to a human (the fix looked right but broke a sibling).

Adversarial quality lives in the AdversarialReview AGENT (rca_panel), not a judge
gate, so a block drives create.revise (loop_limit) — same reasoning as content.

No 22-check verify suite exists in aagman-v2 (see TEST_HARNESS.md); if one is
added, wire it as a second judge TestGate.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from harness_core.domain_config import DomainConfig, StepConfig
from harness_core.gates import ComplianceGate, HumanGate, TestGate
from harness_core.judgment_panel import JudgmentPanel
from harness_core.llm_router import LLMRouter
from harness_engineering.agents import (
    IssueListener, RCAAgent, CodeFixAgent, AdversarialReview, PRAgent, FixMemory,
)
from harness_engineering.gates import CriticalApprovalGate
from harness_engineering.prioritize import make_prioritizer

_ENG = Path(__file__).resolve().parent.parent / "harness_engineering"
RISK_RULES = _ENG / "RISK_RULES.md"
DIST = _ENG / "distilled"
LAYER_GT = DIST / "layer_ground_truth.json"
FILE_REL = DIST / "file_relationships.json"
ADV_VOCAB = DIST / "adversarial_vocab.json"
ROUTE_INDEX = DIST / "route_index.json"     # retrieval router; regenerate via routing_eval build
USAGE_WEIGHTS = DIST / "usage_weights.json"  # usage-weighted PRIORITIZE; regenerate from prod usage

_DEFAULT_AAGMAN = str(Path.home() / "Documents" / "aagman-v2")


def build_config(services=None) -> DomainConfig:
    router = services.router if services else LLMRouter()
    memory_factory = services.memory_factory if services else None
    env = services.env if services else {}
    workdir = str(services.workdir) if services else "."
    notifier = (services.telegram.notifier()
                if services and services.telegram else None)

    aagman = env.get("AAGMAN_V2_PATH", _DEFAULT_AAGMAN)
    run_all = f"bash {aagman}/regression-testing/run_all.sh"

    config = DomainConfig(name="engineering", steps=[
        StepConfig("sense", IssueListener()),
        StepConfig(
            "ideate",
            RCAAgent(router, memory_factory, str(LAYER_GT), str(FILE_REL),
                     str(RISK_RULES), route_index_path=str(ROUTE_INDEX)),
            task_type="complex_planning",
            gates=[HumanGate("plan", timeout_hours=24, notifier=notifier)],
        ),
        StepConfig(
            "create",
            CodeFixAgent(workdir=aagman, router=router, memory_factory=memory_factory,
                         file_rel=str(FILE_REL)),
            task_type="code_execution", mode="serial",
            gates=[
                # No domain/step: compliance votes with rca_panel, not diverted by
                # the engineering.ideate generation override.
                ComplianceGate(str(RISK_RULES),
                               panel=JudgmentPanel(router, "rca_panel",
                                                   threshold=1.0).vote,
                               threshold=1.0),
                # inner loop: fast suite (skips integration), fixable -> re-fix
                TestGate(f"{run_all} --fast", cwd=aagman, fixable=True, timeout=1800),
            ],
            loop_limit=3,  # tester limit of 3 (spec)
        ),
        StepConfig(
            "judge",
            AdversarialReview(router, str(ADV_VOCAB)),
            task_type="rca_panel", loop_limit=2,
            gates=[
                # outer net: full suite (incl. integration); NOT fixable here ->
                # a downstream break escalates to a human, never silently loops.
                TestGate(run_all, cwd=aagman, fixable=False, timeout=3600),
            ],
        ),
        StepConfig(
            "publish",
            PRAgent(),
            gates=[
                CriticalApprovalGate(notifier=notifier),      # critical -> extra sign-off
                HumanGate("amit_merge", timeout_hours=48, notifier=notifier),
            ],
        ),
        StepConfig("learn", FixMemory(memory_factory)),
    ])

    # Usage-weighted, budget-fitted PRIORITIZE: run the highest-impact core-product
    # tickets first. Weights are a committed prod-usage snapshot; if absent, the loop
    # falls back to FIFO. Budget is per-cycle CREATE tokens (env-tunable).
    if USAGE_WEIGHTS.exists():
        weights = json.loads(USAGE_WEIGHTS.read_text())
        budget = int(env.get("PRIORITIZE_BUDGET_TOKENS", "300000"))
        config.prioritizer = make_prioritizer(weights, budget)
    return config
