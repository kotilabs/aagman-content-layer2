"""agent_base.py — the agent contract.

Six ABCs, one per loop step. Every domain agent implements exactly one. The loop
data types (Signal/Idea/Artifact/Verdict/Receipt) are the payloads passed between
steps. ABC enforcement is load-time: a config naming an agent that misses a
required method fails when instantiated, never mid-cycle (see domain_config).
"""
from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


def _fingerprint(*parts: Any) -> str:
    blob = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


# --------------------------------------------------------------------------- #
# Loop data types
# --------------------------------------------------------------------------- #
@dataclass
class Signal:
    """A sensed unit of work. `fingerprint` is the dedup key (derived if unset)."""
    id: str
    domain: str
    source: str
    payload: dict = field(default_factory=dict)
    fingerprint: str = ""

    def __post_init__(self):
        if not self.fingerprint:
            self.fingerprint = _fingerprint(self.domain, self.source, self.payload)


@dataclass
class Idea:
    summary: str = ""
    plan: dict = field(default_factory=dict)
    confidence: float = 1.0
    meta: dict = field(default_factory=dict)


@dataclass
class Artifact:
    body: str = ""
    kind: str = "text"
    meta: dict = field(default_factory=dict)


@dataclass
class Verdict:
    verdict: str = "pass"  # pass | block | escalate
    issues: list = field(default_factory=list)
    score: float = 1.0
    meta: dict = field(default_factory=dict)


@dataclass
class Receipt:
    channel: str = ""
    ref: str = ""
    meta: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Agent ABCs — one per SENSE / IDEATE / CREATE / JUDGE / PUBLISH / LEARN
# --------------------------------------------------------------------------- #
class SenseAgent(ABC):
    @abstractmethod
    def sense(self, sources) -> list:
        ...


class IdeateAgent(ABC):
    @abstractmethod
    def ideate(self, signal):
        ...


class CreateAgent(ABC):
    @abstractmethod
    def create(self, idea):
        ...

    @abstractmethod
    def revise(self, artifact, issues):
        ...


class JudgeAgent(ABC):
    @abstractmethod
    def judge(self, artifact, panel):
        ...


class PublishAgent(ABC):
    @abstractmethod
    def publish(self, artifact, channels):
        ...


class LearnAgent(ABC):
    @abstractmethod
    def record(self, signal, idea, artifact, outcome):
        ...


ROLE_ABCS = {
    "sense": SenseAgent,
    "ideate": IdeateAgent,
    "create": CreateAgent,
    "judge": JudgeAgent,
    "publish": PublishAgent,
    "learn": LearnAgent,
}
