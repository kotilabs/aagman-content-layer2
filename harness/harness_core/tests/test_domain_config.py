"""Phase-1 TDD: domain_config.py — StepConfig / GateConfig / DomainConfig.

The load-time contract: a StepConfig whose agent is the wrong role, an unknown
step, or recursive=True (forbidden this build) must raise at CONSTRUCTION — never
surface mid-cycle. Decision 7: recursive=False EVERYWHERE.
"""
import pytest

from harness_core.agent_base import SenseAgent, IdeateAgent, CreateAgent, Artifact
from harness_core.domain_config import StepConfig, GateConfig, DomainConfig


class _Sense(SenseAgent):
    def sense(self, sources):
        return []


class _Ideate(IdeateAgent):
    def ideate(self, signal):
        return None


class _Create(CreateAgent):
    def create(self, idea):
        return Artifact()
    def revise(self, artifact, issues):
        return artifact


def test_stepconfig_defaults_serial_nonrecursive():
    sc = StepConfig(step="sense", agent=_Sense(), task_type="classification")
    assert sc.mode == "serial"
    assert sc.recursive is False
    assert sc.fan_out == []
    assert sc.gates == []
    assert sc.task_type == "classification"


def test_parallel_step_carries_fan_out():
    sc = StepConfig(step="create", agent=_Create(), mode="parallel",
                    fan_out=["text", "image"])
    assert sc.mode == "parallel"
    assert sc.fan_out == ["text", "image"]


def test_stepconfig_rejects_wrong_role_agent_at_load():
    # a SenseAgent assigned to the 'ideate' step must fail immediately
    with pytest.raises(TypeError):
        StepConfig(step="ideate", agent=_Sense())


def test_stepconfig_rejects_unknown_step():
    with pytest.raises(ValueError):
        StepConfig(step="frobnicate", agent=_Sense())


def test_stepconfig_rejects_recursive_true_this_build():
    with pytest.raises(ValueError):
        StepConfig(step="sense", agent=_Sense(), recursive=True)


def test_stepconfig_rejects_bad_mode():
    with pytest.raises(ValueError):
        StepConfig(step="sense", agent=_Sense(), mode="quantum")


def test_gateconfig_holds_kind_and_params():
    g = GateConfig(kind="human", params={"gate_name": "plan", "timeout_hours": 24})
    assert g.kind == "human"
    assert g.params["gate_name"] == "plan"


def test_domainconfig_indexes_steps_by_name():
    dc = DomainConfig(name="content", steps=[
        StepConfig(step="sense", agent=_Sense()),
        StepConfig(step="ideate", agent=_Ideate()),
    ])
    assert dc.name == "content"
    assert isinstance(dc.step("sense").agent, _Sense)
    assert dc.step("ideate") is not None
    assert dc.step("nope") is None


def test_domainconfig_rejects_duplicate_step():
    with pytest.raises(ValueError):
        DomainConfig(name="dup", steps=[
            StepConfig(step="sense", agent=_Sense()),
            StepConfig(step="sense", agent=_Sense()),
        ])
