"""Phase-1 TDD: gates.py — Gate ABC, GateResult, and the four concrete gates.

Gates are the domain-agnostic decision primitives. ComplianceGate/QualityGate
take an INJECTED panel callable (no real LLM here) so they are deterministic and
offline-testable. The headline genericity proof: the *same* ComplianceGate class
blocks a SEBI violation with SEBI_RULES.md and a risk violation with RISK_RULES.md.
"""
import pytest

from harness_core.gates import (
    Gate,
    GateResult,
    TestGate,
    ComplianceGate,
    QualityGate,
    HumanGate,
)


# --------------------------------------------------------------------------- #
# GateResult — the universal return type (verdict pass|block|escalate)
# --------------------------------------------------------------------------- #
def test_gateresult_holds_verdict_issues_fixable():
    r = GateResult(verdict="block", issues=["bad"], fixable=True)
    assert r.verdict == "block"
    assert r.issues == ["bad"]
    assert r.fixable is True


def test_gateresult_defaults_to_empty_issues_and_not_fixable():
    r = GateResult(verdict="pass")
    assert r.issues == []
    assert r.fixable is False


def test_gate_is_abstract():
    with pytest.raises(TypeError):
        Gate()  # abstract: cannot instantiate directly


# --------------------------------------------------------------------------- #
# TestGate — deterministic, runs a real shell command (no LLM)
# --------------------------------------------------------------------------- #
def test_testgate_passes_when_command_exits_zero(tmp_path):
    r = TestGate(test_command="exit 0", cwd=str(tmp_path)).check(None)
    assert r.verdict == "pass"


def test_testgate_blocks_and_is_fixable_when_command_fails(tmp_path):
    r = TestGate(test_command="exit 1", cwd=str(tmp_path), fixable=True).check(None)
    assert r.verdict == "block"
    assert r.fixable is True


def test_testgate_escalates_when_not_fixable(tmp_path):
    r = TestGate(test_command="exit 1", cwd=str(tmp_path), fixable=False).check(None)
    assert r.verdict == "escalate"
    assert r.fixable is False


def test_testgate_captures_failure_output_in_issues(tmp_path):
    r = TestGate(test_command="echo BOOM_FAILURE >&2; exit 1", cwd=str(tmp_path)).check(None)
    assert any("BOOM_FAILURE" in i for i in r.issues)


# --------------------------------------------------------------------------- #
# ComplianceGate — LLM-vs-rules-file; panel injected; GENERICITY PROOF
# --------------------------------------------------------------------------- #
def _violation_panel(bad_marker):
    """Fake panel: each member blocks iff the artifact contains bad_marker."""
    def panel(rules_text, artifact):
        blocked = bad_marker in artifact
        return [{
            "verdict": "block" if blocked else "pass",
            "issues": [f"violates rule re: {bad_marker}"] if blocked else [],
        }]
    return panel


def test_compliancegate_blocks_sebi_violation(tmp_path):
    rules = tmp_path / "SEBI_RULES.md"
    rules.write_text("No return claims.")
    gate = ComplianceGate(rules_file=str(rules),
                          panel=_violation_panel("guaranteed returns"),
                          threshold=1.0)
    r = gate.check("Buy now for guaranteed returns!")
    assert r.verdict == "block"
    assert r.fixable is True
    assert r.issues


def test_same_compliancegate_class_blocks_risk_violation(tmp_path):
    # GENERICITY: identical class + method, different rules file & domain.
    rules = tmp_path / "RISK_RULES.md"
    rules.write_text("CNC equity short = BLOCK.")
    gate = ComplianceGate(rules_file=str(rules),
                          panel=_violation_panel("CNC short"),
                          threshold=1.0)
    r = gate.check("Place a CNC short on RELIANCE")
    assert r.verdict == "block"


def test_compliancegate_passes_clean_artifact(tmp_path):
    rules = tmp_path / "SEBI_RULES.md"
    rules.write_text("No return claims.")
    gate = ComplianceGate(rules_file=str(rules),
                          panel=_violation_panel("guaranteed returns"),
                          threshold=1.0)
    r = gate.check("Educational note on diversification.")
    assert r.verdict == "pass"
    assert r.issues == []


def test_compliancegate_reads_rules_file_and_feeds_panel(tmp_path):
    rules = tmp_path / "R.md"
    rules.write_text("SECRET_RULE_TOKEN")
    seen = {}

    def panel(rules_text, artifact):
        seen["rules"] = rules_text
        return [{"verdict": "pass", "issues": []}]

    ComplianceGate(rules_file=str(rules), panel=panel, threshold=1.0).check("hi")
    assert "SECRET_RULE_TOKEN" in seen["rules"]


def test_compliancegate_missing_rules_file_raises(tmp_path):
    # Fail fast: a config pointing at a nonexistent rules file must not silently pass.
    with pytest.raises(FileNotFoundError):
        ComplianceGate(rules_file=str(tmp_path / "nope.md"),
                       panel=_violation_panel("x"),
                       threshold=1.0)


# --------------------------------------------------------------------------- #
# ComplianceGate REQUIRED_STRINGS — DETERMINISTIC mandatory-disclosure enforce
# A legally-required disclaimer (RIA name + reg number) must NOT depend on an
# LLM panel noticing its absence. If the rules file declares a REQUIRED_STRINGS
# section, every one of those strings must appear verbatim or the gate blocks —
# before, and independent of, the panel vote. No section => behaviour unchanged.
# --------------------------------------------------------------------------- #
_REQ_RULES = (
    "# Rules\nNo return claims.\n\n"
    "## REQUIRED_STRINGS\n"
    "Every artifact must contain these verbatim:\n"
    "- Koti Labs\n"
    "- `INA000021951`\n\n"
    "## Other\nmore prose\n"
)


def _pass_panel():
    def panel(rules_text, artifact):
        return [{"verdict": "pass", "issues": []}]
    return panel


def test_compliancegate_blocks_when_required_string_missing(tmp_path):
    rules = tmp_path / "SEBI_RULES.md"
    rules.write_text(_REQ_RULES)
    gate = ComplianceGate(rules_file=str(rules), panel=_pass_panel(), threshold=1.0)
    r = gate.check("Educational note. Koti Labs.")  # missing reg number
    assert r.verdict == "block"
    assert r.fixable is True
    assert any("INA000021951" in i for i in r.issues)


def test_compliancegate_required_strings_block_even_if_panel_would_pass(tmp_path):
    # Determinism: pass-panel cannot rescue an artifact missing a mandatory string.
    rules = tmp_path / "SEBI_RULES.md"
    rules.write_text(_REQ_RULES)
    gate = ComplianceGate(rules_file=str(rules), panel=_pass_panel(), threshold=1.0)
    assert gate.check("nothing here").verdict == "block"


def test_compliancegate_passes_when_required_strings_present_and_panel_passes(tmp_path):
    rules = tmp_path / "SEBI_RULES.md"
    rules.write_text(_REQ_RULES)
    gate = ComplianceGate(rules_file=str(rules), panel=_pass_panel(), threshold=1.0)
    r = gate.check("Educational. Koti Labs, SEBI RIA INA000021951. Not advice.")
    assert r.verdict == "pass"


def test_compliancegate_no_required_section_skips_string_enforcement(tmp_path):
    # Backward compatible: rules file without a REQUIRED_STRINGS section => panel governs.
    rules = tmp_path / "R.md"
    rules.write_text("No return claims.")
    gate = ComplianceGate(rules_file=str(rules), panel=_pass_panel(), threshold=1.0)
    assert gate.check("anything at all").verdict == "pass"


def test_compliancegate_ignores_horizontal_rule_in_required_section(tmp_path):
    # A '---' hr after the bullets must NOT be parsed as a required string '--'.
    rules = tmp_path / "SEBI_RULES.md"
    rules.write_text("## REQUIRED_STRINGS\n- Koti Labs\n\n---\n\n## Next\nx\n")
    gate = ComplianceGate(rules_file=str(rules), panel=_pass_panel(), threshold=1.0)
    assert gate.required_strings == ["Koti Labs"]
    assert gate.check("hi from Koti Labs").verdict == "pass"


# --------------------------------------------------------------------------- #
# QualityGate — multi-model vote vs threshold
# --------------------------------------------------------------------------- #
def test_qualitygate_passes_when_pass_fraction_meets_threshold():
    def panel(criteria, artifact):
        return [{"verdict": "pass", "issues": []},
                {"verdict": "pass", "issues": []},
                {"verdict": "block", "issues": ["weak"]}]
    r = QualityGate(panel=panel, threshold=0.66).check("content")
    assert r.verdict == "pass"  # 2/3 = 0.666 >= 0.66


def test_gate_escalates_when_panel_cannot_vote():
    # No votes == the panel could not run (auth/infra outage), NOT a content
    # defect. It must ESCALATE to a human, never block-fixable — a revise loop
    # cannot fix an outage and just burns budget (RISK law a: absence of
    # expected data is investigated, not silently retried).
    r = QualityGate(panel=lambda c, a: [], threshold=0.66).check("anything")
    assert r.verdict == "escalate"
    assert r.fixable is False


def test_compliancegate_escalates_when_panel_cannot_vote(tmp_path):
    rules = tmp_path / "R.md"
    rules.write_text("some rule")
    r = ComplianceGate(rules_file=str(rules), panel=lambda c, a: [],
                       threshold=1.0).check("clean artifact")
    assert r.verdict == "escalate"


def test_qualitygate_blocks_and_aggregates_issues_below_threshold():
    def panel(criteria, artifact):
        return [{"verdict": "block", "issues": ["a"]},
                {"verdict": "block", "issues": ["b"]},
                {"verdict": "pass", "issues": []}]
    r = QualityGate(panel=panel, threshold=0.66).check("weak content")
    assert r.verdict == "block"
    assert r.fixable is True
    assert set(r.issues) >= {"a", "b"}


# --------------------------------------------------------------------------- #
# HumanGate — Telegram request + approval-file; async (parks, does not block)
# --------------------------------------------------------------------------- #
def test_humangate_passes_when_approved_file_present(tmp_path):
    gate_dir = tmp_path / "gates" / "wi1" / "plan"
    gate_dir.mkdir(parents=True)
    (gate_dir / "APPROVED").write_text("ok")
    sent = []
    r = HumanGate("plan", timeout_hours=24, notifier=sent.append).check(
        "the plan", ctx={"gate_dir": str(gate_dir)})
    assert r.verdict == "pass"
    assert sent == []  # already approved -> no ping


def test_humangate_blocks_when_rejected_file_present(tmp_path):
    gate_dir = tmp_path / "g"
    gate_dir.mkdir()
    (gate_dir / "REJECTED").write_text("no")
    r = HumanGate("plan", 24, notifier=lambda t: None).check(
        "x", ctx={"gate_dir": str(gate_dir)})
    assert r.verdict == "block"
    assert r.fixable is False


def test_humangate_escalates_and_notifies_when_pending(tmp_path):
    gate_dir = tmp_path / "g"
    gate_dir.mkdir()
    sent = []
    r = HumanGate("plan", 24, notifier=sent.append).check(
        "please review THIS", ctx={"gate_dir": str(gate_dir)})
    assert r.verdict == "escalate"
    assert len(sent) == 1
    assert "plan" in sent[0]


def test_humangate_notifies_only_once_across_resume_polls(tmp_path):
    gate_dir = tmp_path / "g"
    gate_dir.mkdir()
    sent = []
    gate = HumanGate("plan", 24, notifier=sent.append)
    gate.check("x", ctx={"gate_dir": str(gate_dir)})
    gate.check("x", ctx={"gate_dir": str(gate_dir)})  # resume poll, same pending gate
    assert len(sent) == 1  # REQUESTED marker prevents re-notifying


def test_humangate_flags_timeout_in_issues(tmp_path):
    gate_dir = tmp_path / "g"
    gate_dir.mkdir()
    clock = [1000.0]
    gate = HumanGate("plan", timeout_hours=1, notifier=lambda t: None,
                     now=lambda: clock[0])
    gate.check("x", ctx={"gate_dir": str(gate_dir)})  # requested at t=1000
    clock[0] += 3600 * 2  # +2h, exceeds 1h timeout
    r = gate.check("x", ctx={"gate_dir": str(gate_dir)})
    assert r.verdict == "escalate"
    assert any("timeout" in i.lower() for i in r.issues)
