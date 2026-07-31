"""Phase-1 TDD: run.py — CLI wiring (build_harness / load_domain / load_env)."""
import pytest

from harness_core import run as runmod
from harness_core.generic_harness import GenericHarness
from harness_core.domain_config import DomainConfig, StepConfig
from harness_core.agent_base import SenseAgent, LearnAgent


class _S(SenseAgent):
    def sense(self, sources):
        return []


class _L(LearnAgent):
    def record(self, signal, idea, artifact, outcome):
        pass


def _min_config():
    return DomainConfig(name="content", steps=[
        StepConfig(step="sense", agent=_S()),
        StepConfig(step="learn", agent=_L()),
    ])


def test_build_harness_wires_services(tmp_path):
    h = runmod.build_harness(_min_config(), workdir=str(tmp_path), dry_run=True,
                             env={"DAILY_BUDGET_USD": "3.0"})
    assert isinstance(h, GenericHarness)
    assert h.dry_run is True
    assert h.budget.daily_usd == 3.0
    assert h.kill_switch is not None
    assert h.store is not None


def test_load_domain_missing_raises_clear_error():
    with pytest.raises(SystemExit):
        runmod.load_domain("nonexistent_domain_xyz")


def test_load_env_reads_file(tmp_path):
    (tmp_path / ".env").write_text("FOO=bar\n# comment\nBAZ = qux \n\n")
    env = runmod.load_env(str(tmp_path / ".env"))
    assert env["FOO"] == "bar"
    assert env["BAZ"] == "qux"


# --------------------------------------------------------------------------- #
# Phase-4 wiring: Services bundle + injection into build_config / build_harness
# --------------------------------------------------------------------------- #
def test_build_services_provides_router_budget_and_memory_factory(tmp_path):
    svc = runmod.build_services(env={"DAILY_BUDGET_USD": "2.0"}, workdir=str(tmp_path))
    from harness_core.agent_memory import AgentMemory
    assert svc.router is not None
    assert svc.budget.daily_usd == 2.0
    assert isinstance(svc.memory_factory("content", "judge"), AgentMemory)


def test_build_harness_uses_injected_services(tmp_path):
    svc = runmod.build_services(env={}, workdir=str(tmp_path))
    h = runmod.build_harness(_min_config(), services=svc, dry_run=True)
    assert h.store is svc.store
    assert h.router is svc.router
    assert h.memory_factory is svc.memory_factory


def test_load_domain_passes_services_to_build_config(tmp_path, monkeypatch):
    seen = {}

    class _FakeMod:
        @staticmethod
        def build_config(services):
            seen["services"] = services
            return _min_config()

    monkeypatch.setattr(runmod.importlib, "import_module", lambda name: _FakeMod)
    svc = runmod.build_services(env={}, workdir=str(tmp_path))
    runmod.load_domain("anything", svc)
    assert seen["services"] is svc
