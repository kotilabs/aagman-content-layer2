"""domain_config.py — declarative config for a domain's loop.

A DomainConfig is a set of StepConfigs, one per loop step. Validation is
LOAD-TIME: a misshapen config (wrong-role agent, unknown step, recursive=True,
bad mode, duplicate step) raises at construction so it can never surface
mid-cycle. Model choices are carried as `task_type` strings only — the router
resolves them via harness_configs/models.yaml (no model strings live here).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from harness_core.agent_base import ROLE_ABCS

_MODES = {"serial", "parallel"}


@dataclass
class GateConfig:
    """A gate to attach to a step. kind in {compliance, human, quality, test}."""
    kind: str
    params: dict = field(default_factory=dict)


@dataclass
class StepConfig:
    step: str            # sense | ideate | create | judge | publish | learn
    agent: object        # instance implementing ROLE_ABCS[step]
    task_type: str = ""  # resolves through models.yaml
    mode: str = "serial"  # serial | parallel
    fan_out: list = field(default_factory=list)
    gates: list = field(default_factory=list)
    loop_limit: int = 2  # fixable-retry cap for this step's gates
    # recursion is in the schema but OFF this build (Decision 7)
    recursive: bool = False
    recursion_trigger: str = ""
    max_recursion_depth: int = 2

    def __post_init__(self):
        if self.step not in ROLE_ABCS:
            raise ValueError(
                f"unknown step '{self.step}' (expected one of {sorted(ROLE_ABCS)})")
        if self.mode not in _MODES:
            raise ValueError(f"invalid mode '{self.mode}' (expected serial|parallel)")
        if self.recursive:
            raise ValueError(
                "recursive=True is forbidden in this build (Decision 7: flat loop only)")
        abc = ROLE_ABCS[self.step]
        if not isinstance(self.agent, abc):
            raise TypeError(
                f"step '{self.step}' requires a {abc.__name__} instance, "
                f"got {type(self.agent).__name__}")


@dataclass
class DomainConfig:
    name: str
    steps: list = field(default_factory=list)
    # optional callable(list[work_item]) -> list[work_item]; the harness applies it to
    # reorder/subset the open queue before the pipeline. Generic — any domain may set it.
    prioritizer: object = None

    def __post_init__(self):
        self._by_step: dict = {}
        for sc in self.steps:
            if sc.step in self._by_step:
                raise ValueError(
                    f"duplicate step '{sc.step}' in domain '{self.name}'")
            self._by_step[sc.step] = sc

    def step(self, name: str):
        return self._by_step.get(name)
