"""TDD for the Postgres adapter's pure helpers (no DB): parse the mastra_messages
content shape and reconstruct a coarse outcome from aagman_sessions.state.
The SQL execution itself is IO, verified by running against prod."""
from harness_engineering.enrichment_pg import extract_text, outcome_from_state


def test_extract_text_from_mastra_parts():
    assert extract_text('{"format":2,"parts":[{"type":"text","text":"run backtest"}]}') == "run backtest"


def test_extract_text_joins_multiple_text_parts():
    assert extract_text({"parts": [{"type": "text", "text": "hi"},
                                   {"type": "text", "text": "there"}]}) == "hi there"


def test_extract_text_fallbacks():
    assert extract_text("plain string") == "plain string"   # non-JSON string passthrough
    assert extract_text(None) == ""
    assert extract_text('{"parts":[]}') == ""


def test_outcome_from_state_needs_clarification():
    assert outcome_from_state({"pendingQuestions": ["what timeframe?"]}) == "NEEDS_CLARIFICATION"


def test_outcome_from_state_ready_when_complete_confirmed():
    assert outcome_from_state({"stage": "complete", "confirmed": True}) == "READY"


def test_outcome_from_state_unknown_stays_blank():
    assert outcome_from_state({"stage": "strategy", "confirmed": False}) == ""
    assert outcome_from_state(None) == ""
