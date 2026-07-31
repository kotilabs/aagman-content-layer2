"""Phase-6: genericity + extensibility proof.

The whole thesis: a THIRD domain plugs in with ZERO harness_core changes — just a
new harness_configs/<name>_config.py exposing build_config(services). Here we load
all three domains (content, engineering, distribution) through the same
run.load_domain + GenericHarness, and re-assert the same-gate-two-rules property.
"""
from pathlib import Path

from harness_core import run as runmod
from harness_core.domain_config import DomainConfig
from harness_core.generic_harness import GenericHarness
from harness_core.gates import ComplianceGate

_REPO = Path(__file__).resolve().parents[2]


def _svc(tmp_path):
    return runmod.build_services(env={}, workdir=str(tmp_path))


def test_all_three_domains_load_through_the_same_engine(tmp_path):
    svc = _svc(tmp_path)
    for name in ("content", "engineering", "distribution"):
        cfg = runmod.load_domain(name, svc)
        assert isinstance(cfg, DomainConfig) and cfg.name == name
        # the SAME generic engine drives every domain
        h = runmod.build_harness(cfg, services=svc, dry_run=True)
        assert isinstance(h, GenericHarness)


def test_distribution_stub_satisfies_all_six_abcs(tmp_path):
    cfg = runmod.load_domain("distribution", _svc(tmp_path))
    for step in ("sense", "ideate", "create", "judge", "publish", "learn"):
        assert cfg.step(step) is not None  # DomainConfig validated each agent's ABC


def test_same_compliancegate_class_serves_both_rules_files(tmp_path):
    # genericity: one class, two domains, only the rules file differs.
    sebi = _REPO / "harness_content" / "SEBI_RULES.md"
    risk = _REPO / "harness_engineering" / "RISK_RULES.md"
    panel = lambda c, a: [{"verdict": "pass", "issues": []}]
    g_sebi = ComplianceGate(str(sebi), panel=panel, threshold=1.0)
    g_risk = ComplianceGate(str(risk), panel=panel, threshold=1.0)
    assert type(g_sebi) is type(g_risk) is ComplianceGate
    assert g_sebi.rules_file != g_risk.rules_file
