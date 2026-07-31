"""harness_configs/layer2_config.py — domain wiring for the content-layer2 merger.

This config plugs the Layer 2 agents into the generic harness loop. It uses the
Kimi Code bridge router, content-layer2 prompts/voice, and the harness memory +
gates.
"""
from __future__ import annotations

from pathlib import Path

from harness_core.domain_config import DomainConfig, StepConfig
from harness_core.gates import ComplianceGate, HumanGate
from harness_core.judgment_panel import JudgmentPanel
from harness_core.llm_router import LLMRouter
from harness_content.layer2_agents import (
    Layer2SignalReader,
    Layer2ResearchAgent,
    Layer2ContentCreator,
    Layer2MarketsReviewer,
    Layer2Publisher,
    Layer2Memory,
    RIA_NAME,
    RIA_REG,
)

_CONTENT = Path(__file__).resolve().parent.parent / "harness_content"
SEBI_RULES = _CONTENT / "SEBI_RULES.md"


def build_config(services=None) -> DomainConfig:
    router = services.router if services else LLMRouter()
    memory_factory = services.memory_factory if services else None
    env = services.env if services else {}
    workdir = Path(services.workdir) if services else Path(".")
    notifier = (services.telegram.notifier()
                if services and services.telegram else None)

    inbox = workdir / "inbox"
    outbox = workdir / "outbox"
    digest = env.get("LAYER2_DIGEST_PATH",
                     str(workdir / "signals" / "2026-07-03-digest.md"))
    surfaces = env.get("LAYER2_SURFACES",
                        "blog,thread,carousel_linkedin,carousel_instagram,infographic")
    fan_out = [s.strip() for s in surfaces.split(",") if s.strip()]
    ria = env.get("AAGMAN_RIA_NAME", RIA_NAME)
    reg = env.get("AAGMAN_SEBI_REG_NUMBER", RIA_REG)

    compliance = ComplianceGate(
        str(SEBI_RULES),
        panel=JudgmentPanel(router, "compliance_panel", threshold=1.0).vote,
        threshold=1.0,
    )

    return DomainConfig(name="layer2", steps=[
        StepConfig("sense", Layer2SignalReader(str(inbox), digest_path=digest)),
        StepConfig(
            "ideate",
            Layer2ResearchAgent(router, memory_factory, workdir),
            task_type="complex_planning",
            gates=[HumanGate("research_approval", timeout_hours=24, notifier=notifier)],
        ),
        StepConfig(
            "create",
            Layer2ContentCreator(router, memory_factory),
            task_type="content_gen",
            mode="parallel",
            fan_out=fan_out,
            gates=[compliance],
        ),
        StepConfig(
            "judge",
            Layer2MarketsReviewer(router),
            task_type="judge_panel",
            loop_limit=2,
        ),
        StepConfig(
            "publish",
            Layer2Publisher(str(outbox)),
            gates=[HumanGate("publish_approval", timeout_hours=48, notifier=notifier)],
        ),
        StepConfig("learn", Layer2Memory(memory_factory)),
    ])
