"""Phase-3 TDD: the two real rules files load through ComplianceGate and carry
their mandatory contents.

These are integration tests over the SHIPPED domain rules files (not tmp_path
fixtures): they prove the genericity claim end-to-end — the SAME ComplianceGate
class enforces SEBI_RULES.md for the content domain and RISK_RULES.md for the
engineering domain, differing only by the rules file — and that each file
carries the spec-mandated contents (REQUIRED_STRINGS, the six SEBI rules, the
four engineering laws, the Indian-market invariants, the branch/regression laws).
"""
from pathlib import Path

from harness_core.gates import ComplianceGate

_REPO = Path(__file__).resolve().parents[2]
SEBI = _REPO / "harness_content" / "SEBI_RULES.md"
RISK = _REPO / "harness_engineering" / "RISK_RULES.md"

# Single source of truth for the mandatory disclosure (mirrors .env.example).
RIA_NAME = "Koti Labs"
RIA_REG = "INA000021951"


def _pass_panel(rules_text, artifact):
    return [{"verdict": "pass", "issues": []}]


# --------------------------------------------------------------------------- #
# Files exist and load via ComplianceGate (fail-fast if a config points nowhere)
# --------------------------------------------------------------------------- #
def test_both_rules_files_exist_and_load_through_compliancegate():
    ComplianceGate(rules_file=str(SEBI), panel=_pass_panel, threshold=1.0)
    ComplianceGate(rules_file=str(RISK), panel=_pass_panel, threshold=1.0)


# --------------------------------------------------------------------------- #
# SEBI_RULES.md — six rules + REQUIRED_STRINGS the gate enforces
# --------------------------------------------------------------------------- #
def test_sebi_rules_contains_the_six_rules():
    text = SEBI.read_text().lower()
    for concept in ("educational", "buy", "sell", "return", "3-month",
                    "reg", "label"):
        assert concept in text, f"SEBI_RULES.md missing concept: {concept}"


def test_sebi_rules_declares_required_strings_for_disclosure():
    text = SEBI.read_text()
    assert "REQUIRED_STRINGS" in text
    assert RIA_NAME in text
    assert RIA_REG in text


def test_sebi_gate_blocks_post_missing_mandatory_disclosure():
    gate = ComplianceGate(rules_file=str(SEBI), panel=_pass_panel, threshold=1.0)
    r = gate.check("Quick market note. Nifty looks interesting today.")
    assert r.verdict == "block"
    assert r.fixable is True
    assert any(RIA_REG in i for i in r.issues)


def test_sebi_gate_passes_post_with_disclosure_and_clean_panel():
    gate = ComplianceGate(rules_file=str(SEBI), panel=_pass_panel, threshold=1.0)
    post = (f"Educational only. {RIA_NAME}, SEBI RIA {RIA_REG}. "
            f"This is not investment advice.")
    assert gate.check(post).verdict == "pass"


# --------------------------------------------------------------------------- #
# RISK_RULES.md — Indian-market invariants + four laws + branch/regression laws
# --------------------------------------------------------------------------- #
def test_risk_rules_contains_indian_market_invariants():
    text = RISK.read_text()
    low = text.lower()
    assert "cnc" in low and "block" in low            # CNC equity short = BLOCK
    assert "f&o" in low or "fno" in low                # F&O naked short = ALLOW
    assert "rr_ratio" in low                           # rr = take_profit/stop_loss
    assert "risk-calculations.ts" in text              # layer law entrypoint
    assert "typescript" in low                         # layer law language


def test_risk_rules_contains_four_engineering_laws():
    low = RISK.read_text().lower()
    assert "pre-existing" in low                        # law (b)
    assert "root cause" in low                          # laws (a)/(b)
    assert "data-backed" in low or "data-back" in low   # law (c)
    # law (d): a fix is verified only by a test that failed before and passes after
    assert "failed before" in low and "passes after" in low


def test_risk_rules_contains_branch_and_regression_laws():
    text = RISK.read_text()
    low = text.lower()
    assert "ajit/fix-" in text                          # branch law
    assert "never" in low and "main" in low             # never on main
    assert "regression-testing/" in text                # regression law path


def test_risk_gate_blocks_a_stated_risk_violation():
    # GENERICITY: same class, engineering rules file, an injected risk panel.
    def risk_panel(rules_text, artifact):
        bad = "cnc short" in artifact.lower()
        return [{"verdict": "block" if bad else "pass",
                 "issues": ["CNC equity short is BLOCK"] if bad else []}]
    gate = ComplianceGate(rules_file=str(RISK), panel=risk_panel, threshold=1.0)
    assert gate.check("Recommend a CNC short on RELIANCE").verdict == "block"
