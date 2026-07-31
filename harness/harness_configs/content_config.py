"""harness_configs/content_config.py — the CONTENT domain wiring.

Declarative only: which agent runs each step, which gates guard it, which
task_type each step resolves through models.yaml. `build_config(services)` is
called by run.load_domain with the shared Services bundle (router/memory/env);
services=None falls back to a default router so the config still loads for
inspection.

Design note — the quality panel lives INSIDE ContentJudge.judge (task_type
judge_panel), not as a judge-gate. In the core, a gate `block` parks the item
(no repair path), whereas a judge-agent `block` bounces to create.revise up to
loop_limit. Putting the quality vote in the agent is what gives content its
adversarial revise loop; a redundant judge-gate QualityGate would double-spend.
"""
from __future__ import annotations

from pathlib import Path

from harness_core.domain_config import DomainConfig, StepConfig
from harness_core.gates import ComplianceGate, HumanGate
from harness_core.judgment_panel import JudgmentPanel
from harness_core.llm_router import LLMRouter
from harness_content.agents import (
    ContentSensor, ContentStrategist, ContentCreator, ContentJudge,
    ContentPublisher, ContentMemory, RIA_NAME, RIA_REG,
)

_CONTENT = Path(__file__).resolve().parent.parent / "harness_content"
SEBI_RULES = _CONTENT / "SEBI_RULES.md"
BRAND_VOICE = _CONTENT / "BRAND_VOICE.md"
EXAMPLES = _CONTENT / "distilled" / "examples.json"
CHANNEL_RULES = _CONTENT / "distilled" / "channel_rules.json"


def build_config(services=None) -> DomainConfig:
    router = services.router if services else LLMRouter()
    memory_factory = services.memory_factory if services else None
    env = services.env if services else {}
    workdir = Path(services.workdir) if services else Path(".")
    notifier = (services.telegram.notifier()
                if services and services.telegram else None)

    inbox = workdir / "inbox"
    outbox = workdir / "outbox"
    ria = env.get("AAGMAN_RIA_NAME", RIA_NAME)
    reg = env.get("AAGMAN_SEBI_REG_NUMBER", RIA_REG)

    # No domain/step here: a gate must vote with its PANEL chain, not be diverted
    # by the content.create GENERATION override (which resolve() would otherwise
    # prefer). Compliance is safety-critical — it is judged by compliance_panel.
    compliance = ComplianceGate(
        str(SEBI_RULES),
        panel=JudgmentPanel(router, "compliance_panel", threshold=1.0).vote,
        threshold=1.0,
    )

    return DomainConfig(name="content", steps=[
        StepConfig("sense", ContentSensor(str(inbox))),
        StepConfig(
            "ideate",
            ContentStrategist(router, memory_factory, str(BRAND_VOICE), str(EXAMPLES)),
            task_type="complex_planning",
            gates=[HumanGate("brief", timeout_hours=24, notifier=notifier)],
        ),
        StepConfig(
            "create",
            ContentCreator(router, memory_factory, str(BRAND_VOICE),
                           str(CHANNEL_RULES), ria, reg),
            task_type="content_gen", mode="parallel", fan_out=["text", "image"],
            gates=[compliance],
        ),
        StepConfig("judge", ContentJudge(router), task_type="judge_panel",
                   loop_limit=2),
        StepConfig(
            "publish",
            ContentPublisher(str(outbox)),
            gates=[HumanGate("publish", timeout_hours=48, notifier=notifier)],
        ),
        StepConfig("learn", ContentMemory(memory_factory)),
    ])
