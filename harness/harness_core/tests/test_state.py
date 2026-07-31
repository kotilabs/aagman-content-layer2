"""Phase-1 TDD: state.py — crash-safe work-item store (dedup, resume, audit).

Dedup: a signal whose fingerprint matches an OPEN item is skipped (a matching but
terminal item does not block re-sensing). Resume: open_items() returns everything
not in a terminal state. Every gate decision writes an audit row with rules_version.
"""
import json

from harness_core.agent_base import Signal
from harness_core.state import WorkItemStore, WorkItem, TERMINAL


def _store(tmp_path):
    return WorkItemStore(str(tmp_path / "state.db"), now=lambda: 1_700_000_000.0)


def test_create_persists_workitem(tmp_path):
    s = Signal(id="eng-issue-1", domain="engineering", source="github", payload={"n": 1})
    st = _store(tmp_path)
    wi = st.create(s)
    assert wi.id == "eng-issue-1"
    assert wi.domain == "engineering"
    assert wi.status == "sensed"
    assert wi.fingerprint == s.fingerprint
    assert wi.created_at and wi.updated_at
    got = st.get("eng-issue-1")
    assert json.loads(got.signal_json) == {"n": 1}


def test_create_is_idempotent_by_id_preserving_progress(tmp_path):
    s = Signal(id="x", domain="d", source="s", payload={})
    st = _store(tmp_path)
    st.create(s)
    st.update("x", status="ideated")
    again = st.create(s)  # re-sense same id
    assert again.status == "ideated"  # progress preserved, not reset to sensed


def test_is_duplicate_true_for_open_item(tmp_path):
    s = Signal(id="a", domain="d", source="s", payload={"k": 1})
    st = _store(tmp_path)
    st.create(s)
    assert st.is_duplicate(s.fingerprint) is True


def test_is_duplicate_false_when_match_is_terminal(tmp_path):
    s = Signal(id="a", domain="d", source="s", payload={"k": 1})
    st = _store(tmp_path)
    st.create(s)
    st.update("a", status="published")
    assert st.is_duplicate(s.fingerprint) is False  # closed -> can re-sense


def test_update_sets_fields_and_bumps_updated_at(tmp_path):
    st = _store(tmp_path)
    st.create(Signal(id="x", domain="d", source="s"))
    wi = st.update("x", status="creating", current_step="create", cost_usd=0.25)
    assert wi.status == "creating"
    assert wi.current_step == "create"
    assert wi.cost_usd == 0.25


def test_open_items_excludes_terminal_states(tmp_path):
    st = _store(tmp_path)
    st.create(Signal(id="a", domain="d", source="s", payload={"i": 1}))
    st.create(Signal(id="b", domain="d", source="s", payload={"i": 2}))
    st.update("b", status="failed")
    assert {wi.id for wi in st.open_items()} == {"a"}


def test_awaiting_gate_status_counts_as_open_for_resume(tmp_path):
    st = _store(tmp_path)
    st.create(Signal(id="a", domain="d", source="s"))
    st.update("a", status="awaiting_gate:plan")
    assert {wi.id for wi in st.open_items()} == {"a"}


def test_audit_rows_recorded_with_rules_version(tmp_path):
    st = _store(tmp_path)
    st.create(Signal(id="a", domain="d", source="s"))
    st.audit("a", "compliance", "block", rules_version="sha123", issues=["x"])
    rows = st.audits("a")
    assert len(rows) == 1
    assert rows[0]["gate_name"] == "compliance"
    assert rows[0]["verdict"] == "block"
    assert rows[0]["rules_version"] == "sha123"


def test_relied_lessons_roundtrip(tmp_path):
    st = _store(tmp_path)
    st.create(Signal(id="a", domain="d", source="s"))
    st.update("a", relied_lessons_json=json.dumps(["L1", "L2"]))
    assert json.loads(st.get("a").relied_lessons_json) == ["L1", "L2"]


def test_terminal_set_is_the_three_closed_states():
    assert TERMINAL == {"published", "failed", "rejected"}


def test_get_missing_returns_none(tmp_path):
    assert _store(tmp_path).get("ghost") is None
