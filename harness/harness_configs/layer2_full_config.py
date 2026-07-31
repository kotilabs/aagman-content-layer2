"""harness_configs/layer2_full_config.py — domain wiring for the full Layer 2 merger.

This config wires the full content-layer2 agents into the harness type system
so they can be used with GenericHarness if desired. The custom orchestrator in
run_layer2_full.py uses the underlying agents directly; the adapter classes here
make the agents satisfy the harness_core ABC contracts.
"""
from __future__ import annotations

from pathlib import Path

from harness_core.agent_base import (
    Artifact,
    CreateAgent,
    Idea,
    IdeateAgent,
    JudgeAgent,
    PublishAgent,
    Receipt,
    SenseAgent,
    Signal,
    Verdict,
)
from harness_core.domain_config import DomainConfig, StepConfig
from harness_core.gates import ComplianceGate, HumanGate
from harness_core.judgment_panel import JudgmentPanel
from harness_content.layer2_full_agents import (
    Layer2FinalCorrector,
    Layer2MarketsReviewerFull,
    Layer2PublisherFull,
    Layer2ResearchAgentFull,
    Layer2SEOAuditor,
    Layer2SignalIdentifier,
    Layer2Writer,
)

_CONTENT = Path(__file__).resolve().parent.parent / "harness_content"
SEBI_RULES = _CONTENT / "SEBI_RULES.md"

# Surface set used by the full Layer 2 workflow.
SURFACES = ["blog", "thread", "carousel_linkedin", "carousel_instagram", "infographic"]


# --------------------------------------------------------------------------- #
# Adapters so full agents satisfy the harness_core ABCs
# --------------------------------------------------------------------------- #
class _SignalIdentifierAdapter(SenseAgent):
    """Adapter exposing Layer2SignalIdentifier as a SenseAgent."""

    def __init__(self, identifier: Layer2SignalIdentifier):
        self.identifier = identifier

    def sense(self, sources) -> list:
        digest_path = self.identifier.run()
        return [Signal(
            id=f"layer2:{digest_path.stem}",
            domain="content",
            source=str(digest_path),
            payload={"digest_path": str(digest_path)},
        )]


class _ResearchAdapter(IdeateAgent):
    """Adapter exposing Layer2ResearchAgentFull as an IdeateAgent."""

    def __init__(self, researcher: Layer2ResearchAgentFull, ticket_path: str | Path):
        self.researcher = researcher
        self.ticket_path = Path(ticket_path)

    def ideate(self, signal) -> Idea:
        research_file = self.researcher.run(self.ticket_path)
        return Idea(
            summary=f"Research written to {research_file}",
            plan={"research_file": str(research_file)},
            confidence=0.85,
        )


class _WriterAdapter(CreateAgent):
    """Adapter exposing Layer2Writer as a CreateAgent."""

    def __init__(self, writer: Layer2Writer, signal_id: str, surface: str):
        self.writer = writer
        self.signal_id = signal_id
        self.surface = surface

    def create(self, idea) -> Artifact:
        path = self.writer.create(self.signal_id, self.surface)
        return Artifact(body=path.read_text(encoding="utf-8"),
                        kind=self.surface, meta={"surface": self.surface})

    def revise(self, artifact, issues) -> Artifact:
        # The corrector path needs a review path; this adapter is a stub because
        # run_layer2_full.py uses the corrector directly.
        path = self.writer.draft_path(self.signal_id, self.surface)
        return Artifact(body=path.read_text(encoding="utf-8"),
                        kind=self.surface, meta={"surface": self.surface})


class _ReviewerAdapter(JudgeAgent):
    """Adapter exposing Layer2MarketsReviewerFull as a JudgeAgent."""

    def __init__(self, reviewer: Layer2MarketsReviewerFull, signal_id: str,
                 surfaces: list[str]):
        self.reviewer = reviewer
        self.signal_id = signal_id
        self.surfaces = surfaces

    def judge(self, artifact, panel=None) -> Verdict:
        return self.reviewer.run(self.signal_id, self.surfaces)


class _PublisherAdapter(PublishAgent):
    """Adapter exposing Layer2PublisherFull as a PublishAgent."""

    def __init__(self, publisher: Layer2PublisherFull, signal_id: str,
                 surfaces: list[str]):
        self.publisher = publisher
        self.signal_id = signal_id
        self.surfaces = surfaces

    def publish(self, artifact, channels) -> Receipt:
        copied = self.publisher.publish(self.signal_id, self.surfaces)
        return Receipt(channel="final", ref=str(copied[0]) if copied else "",
                       meta={"copied": [str(p) for p in copied]})


# --------------------------------------------------------------------------- #
# Config builder
# --------------------------------------------------------------------------- #
def build_config(services=None) -> DomainConfig:
    router = services.router if services else None
    workdir = Path(services.workdir) if services else Path(".")
    env = services.env if services else {}
    notifier = (services.telegram.notifier()
                if services and services.telegram else None)

    ria = env.get("AAGMAN_RIA_NAME", "Koti Labs")
    reg = env.get("AAGMAN_SEBI_REG_NUMBER", "INA000021951")

    compliance = ComplianceGate(
        str(SEBI_RULES),
        panel=JudgmentPanel(router, "compliance_panel", threshold=1.0).vote,
        threshold=1.0,
    )

    identifier = Layer2SignalIdentifier(router, workdir)
    researcher = Layer2ResearchAgentFull(router, workdir)
    writer = Layer2Writer(router, workdir)
    reviewer = Layer2MarketsReviewerFull(router, workdir)
    publisher = Layer2PublisherFull(workdir)

    # The runner in run_layer2_full.py orchestrates the workflow directly. The
    # config below is a faithful harness representation using adapter classes.
    return DomainConfig(name="layer2_full", steps=[
        StepConfig("sense", _SignalIdentifierAdapter(identifier)),
        StepConfig(
            "ideate",
            _ResearchAdapter(researcher, workdir / "state" / "tickets" / "placeholder.md"),
            task_type="complex_planning",
            gates=[HumanGate("research_approval", timeout_hours=24, notifier=notifier)],
        ),
        StepConfig(
            "create",
            _WriterAdapter(writer, "placeholder", "blog"),
            task_type="content_gen",
            mode="parallel",
            fan_out=SURFACES,
            gates=[compliance],
        ),
        StepConfig(
            "judge",
            _ReviewerAdapter(reviewer, "placeholder", SURFACES),
            task_type="judge_panel",
            loop_limit=2,
        ),
        StepConfig(
            "publish",
            _PublisherAdapter(publisher, "placeholder", SURFACES),
            gates=[HumanGate("publish_approval", timeout_hours=48, notifier=notifier)],
        ),
    ])
