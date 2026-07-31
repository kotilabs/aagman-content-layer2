"""harness_configs/distribution_config.py — extensibility STUB (Phase 6).

Proof that a NEW domain plugs into the generic engine with ZERO harness_core
changes: this file alone — placeholder agents satisfying the six ABCs plus a
build_config(services) — makes `--domain distribution` a loadable domain. A real
distribution domain (repurpose approved content into new channels/formats,
schedule, cross-post) would flesh these agents out; the engine does not change.
"""
from __future__ import annotations

from harness_core.agent_base import (
    Artifact, Idea, Receipt, Signal, Verdict,
    SenseAgent, IdeateAgent, CreateAgent, JudgeAgent, PublishAgent, LearnAgent,
)
from harness_core.domain_config import DomainConfig, StepConfig


class _Sense(SenseAgent):
    def sense(self, sources=None) -> list:
        return []  # a real sensor would list approved artifacts awaiting redistribution


class _Ideate(IdeateAgent):
    def ideate(self, signal) -> Idea:
        return Idea(summary="stub redistribution plan", plan={}, confidence=1.0)


class _Create(CreateAgent):
    def create(self, idea) -> Artifact:
        return Artifact(body="stub repurposed asset", kind="text")

    def revise(self, artifact, issues) -> Artifact:
        return artifact


class _Judge(JudgeAgent):
    def judge(self, artifact, memory_factory=None) -> Verdict:
        return Verdict(verdict="pass")


class _Publish(PublishAgent):
    def publish(self, artifact, channels) -> Receipt:
        return Receipt(channel="stub", ref="")


class _Learn(LearnAgent):
    def record(self, signal, idea, artifact, outcome) -> None:
        return None


def build_config(services=None) -> DomainConfig:
    return DomainConfig(name="distribution", steps=[
        StepConfig("sense", _Sense()),
        StepConfig("ideate", _Ideate()),
        StepConfig("create", _Create()),
        StepConfig("judge", _Judge()),
        StepConfig("publish", _Publish()),
        StepConfig("learn", _Learn()),
    ])
