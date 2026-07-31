"""Phase-4 TDD: harness_configs/content_config.build_config(services).

Proves the declarative wiring: six steps, the right gates on the right steps
(HumanGate brief/publish, ComplianceGate over the REAL SEBI_RULES.md on create),
parallel text/image fan-out, judge loop_limit 2. Construction alone also proves
every agent satisfies its ABC (DomainConfig validates at load time).
"""
from pathlib import Path

from harness_core import run as runmod
from harness_core.domain_config import DomainConfig
from harness_core.gates import ComplianceGate, HumanGate
from harness_configs import content_config

_REPO = Path(__file__).resolve().parents[2]


def _config(tmp_path):
    svc = runmod.build_services(env={}, workdir=str(tmp_path))
    return content_config.build_config(svc)


def test_build_config_returns_content_domain_with_six_steps(tmp_path):
    cfg = _config(tmp_path)
    assert isinstance(cfg, DomainConfig)
    assert cfg.name == "content"
    for step in ("sense", "ideate", "create", "judge", "publish", "learn"):
        assert cfg.step(step) is not None, f"missing step {step}"


def test_create_step_is_parallel_text_image_with_compliance_gate(tmp_path):
    create = _config(tmp_path).step("create")
    assert create.mode == "parallel"
    assert create.fan_out == ["text", "image"]
    gates = [g for g in create.gates if isinstance(g, ComplianceGate)]
    assert len(gates) == 1
    assert gates[0].rules_file.endswith("SEBI_RULES.md")
    # the RIA disclosure strings are enforced deterministically by this gate
    assert "INA000021951" in gates[0].required_strings or \
           any("INA000021951" in s for s in gates[0].required_strings)


def test_ideate_and_publish_have_human_gates(tmp_path):
    cfg = _config(tmp_path)
    ideate_gates = {g.gate_name for g in cfg.step("ideate").gates
                    if isinstance(g, HumanGate)}
    publish_gates = {g.gate_name for g in cfg.step("publish").gates
                     if isinstance(g, HumanGate)}
    assert "brief" in ideate_gates
    assert "publish" in publish_gates


def test_judge_step_has_loop_limit_two(tmp_path):
    assert _config(tmp_path).step("judge").loop_limit == 2


def test_compliance_gate_votes_with_compliance_panel_not_create_override(tmp_path):
    # A gate attached to CREATE must NOT be diverted by the content.create
    # GENERATION override; compliance must be judged by the compliance_panel.
    comp = [g for g in _config(tmp_path).step("create").gates
            if isinstance(g, ComplianceGate)][0]
    panel = comp.panel.__self__  # JudgmentPanel behind the bound vote() callable
    r = panel.router
    chain = r.resolve(panel.task_type, panel.domain, panel.step)
    assert chain == r.resolve("compliance_panel")
    assert chain != r.resolve("content_gen", "content", "create")


def test_judge_panel_votes_with_judge_panel_chain(tmp_path):
    panel = _config(tmp_path).step("judge").agent.panel
    r = panel.router
    chain = r.resolve(panel.task_type, panel.domain, panel.step)
    assert chain == r.resolve("judge_panel")


def test_build_config_none_services_uses_defaults(tmp_path, monkeypatch):
    # run.py may call build_config(None) in edge paths; must not crash.
    monkeypatch.chdir(tmp_path)
    cfg = content_config.build_config(None)
    assert cfg.name == "content"
