"""Phase-5 TDD: engineering_config.build_config + CriticalApprovalGate.

Proves the wiring: RCA/fix/review/PR agents on the right steps; the test harness
wired as TWO TestGates (fast scoped on create=fixable, full on judge=escalate)
running REAL run_all.sh commands against ~/Documents/aagman-v2; ComplianceGate
over RISK_RULES on rca_panel (not diverted by an override); HumanGate(plan) and
HumanGate(amit_merge); and the approve_critical gate that only engages for
critical-labelled issues.
"""
import json
from pathlib import Path

from harness_core import run as runmod
from harness_core.domain_config import DomainConfig
from harness_core.gates import ComplianceGate, HumanGate, TestGate
from harness_engineering.agents import RCAAgent, CodeFixAgent, AdversarialReview, PRAgent
from harness_engineering.gates import CriticalApprovalGate
from harness_configs import engineering_config


def _config(tmp_path):
    svc = runmod.build_services(env={}, workdir=str(tmp_path))
    return engineering_config.build_config(svc)


def test_build_config_engineering_six_steps(tmp_path):
    cfg = _config(tmp_path)
    assert isinstance(cfg, DomainConfig) and cfg.name == "engineering"
    for step in ("sense", "ideate", "create", "judge", "publish", "learn"):
        assert cfg.step(step) is not None
    assert isinstance(cfg.step("ideate").agent, RCAAgent)
    assert isinstance(cfg.step("create").agent, CodeFixAgent)
    assert isinstance(cfg.step("judge").agent, AdversarialReview)
    assert isinstance(cfg.step("publish").agent, PRAgent)


def test_ideate_has_plan_human_gate(tmp_path):
    names = {g.gate_name for g in _config(tmp_path).step("ideate").gates
             if isinstance(g, HumanGate)}
    assert "plan" in names


def test_create_has_risk_compliance_and_fast_testgate(tmp_path):
    create = _config(tmp_path).step("create")
    comp = [g for g in create.gates if isinstance(g, ComplianceGate)]
    tests = [g for g in create.gates if isinstance(g, TestGate)]
    assert comp and comp[0].rules_file.endswith("RISK_RULES.md")
    assert tests and "run_all.sh" in tests[0].test_command
    assert tests[0].fixable is True                     # inner loop: retry the fix
    assert "aagman-v2" in tests[0].cwd


def test_create_compliance_uses_rca_panel_not_override(tmp_path):
    comp = [g for g in _config(tmp_path).step("create").gates
            if isinstance(g, ComplianceGate)][0]
    panel = comp.panel.__self__
    r = panel.router
    chain = r.resolve(panel.task_type, panel.domain, panel.step)
    assert chain == r.resolve("rca_panel")
    assert chain != r.resolve("complex_planning", "engineering", "ideate")


def test_judge_has_full_testgate_that_escalates(tmp_path):
    tests = [g for g in _config(tmp_path).step("judge").gates if isinstance(g, TestGate)]
    assert tests and "run_all.sh" in tests[0].test_command
    assert tests[0].fixable is False                    # outer net: escalate to human
    # full suite != the --fast inner command
    create_tests = [g for g in _config(tmp_path).step("create").gates
                    if isinstance(g, TestGate)]
    assert tests[0].test_command != create_tests[0].test_command


def test_publish_has_amit_merge_and_critical_gate(tmp_path):
    publish = _config(tmp_path).step("publish")
    assert any(isinstance(g, HumanGate) and g.gate_name == "amit_merge"
               for g in publish.gates)
    assert any(isinstance(g, CriticalApprovalGate) for g in publish.gates)


# --------------------------------------------------------------------------- #
# CriticalApprovalGate — extra human sign-off ONLY for critical-labelled issues
# --------------------------------------------------------------------------- #
class _WI:
    def __init__(self, labels):
        self.id = "eng:1"
        self.signal_json = json.dumps({"labels": labels})


def test_critical_gate_passes_non_critical_issue(tmp_path):
    g = CriticalApprovalGate()
    r = g.check("pr body", {"work_item": _WI(["bug", "p1"]),
                            "gate_dir": str(tmp_path / "g")})
    assert r.verdict == "pass"


def test_critical_gate_requires_approval_for_critical_issue(tmp_path):
    sent = []
    g = CriticalApprovalGate(notifier=sent.append)
    r = g.check("pr body", {"work_item": _WI(["p0", "ship-blocker"]),
                            "gate_dir": str(tmp_path / "g")})
    assert r.verdict == "escalate"
    assert len(sent) == 1
