"""TDD for the budget-constrained PRIORITIZE selector (highest-impact-first, mandatory
safety tier, no silent truncation) and the engineering issue-scoring that turns store
work items into a reordered, budget-fitted, core-product queue using real usage weights."""
import json
from types import SimpleNamespace

from harness_engineering.prioritize import (
    WorkItem, select_within_budget,
    infer_domain, classify_issue, prioritize_work_items, make_prioritizer, est_tokens_for,
)


def _wi(**kw):
    base = dict(id=0, title="", kind="bug", safety=False, score=1.0, est_tokens=10, domain="")
    base.update(kw)
    return WorkItem(**base)


def test_safety_within_reserve_is_chosen():
    items = [_wi(id=1, safety=True, est_tokens=40, score=1),
             _wi(id=2, safety=False, est_tokens=10, score=100)]
    chosen, deferred, escalated = select_within_budget(items, budget=100, safety_reserve=0.5)
    assert {i.id for i in chosen} == {1, 2}        # safety(40) fits reserve(50) + discretionary
    assert escalated == []


def test_safety_over_reserve_is_escalated_not_force_included():
    # THE 62x-blowup fix: a safety item that exceeds the safety reserve is ESCALATED to a
    # human, not blindly force-included (which would blow the budget) nor silently deferred.
    items = [_wi(id=1, safety=True, est_tokens=500, score=1),
             _wi(id=2, safety=False, est_tokens=10, score=100)]
    chosen, deferred, escalated = select_within_budget(items, budget=100, safety_reserve=0.5)
    assert {i.id for i in escalated} == {1}
    assert {i.id for i in chosen} == {2}           # discretionary still fills
    assert sum(i.est_tokens for i in chosen) <= 100  # budget never blown


def test_safety_ranked_highest_first_within_reserve():
    items = [_wi(id=1, safety=True, est_tokens=60, score=5),
             _wi(id=2, safety=True, est_tokens=60, score=9),   # highest safety score
             _wi(id=3, safety=True, est_tokens=60, score=1)]
    chosen, deferred, escalated = select_within_budget(items, budget=200, safety_reserve=0.5)
    assert {i.id for i in chosen} == {2}           # only the top safety item fits reserve(100)
    assert {i.id for i in escalated} == {1, 3}


def test_highest_impact_first_beats_cheaper_lower_score():
    # a P0 (score 5, pricier) must lead a lower-severity but cheaper item when only
    # one fits — a priority backlog is impact-first, not max-total-impact-per-token.
    items = [_wi(id=1, score=5.0, est_tokens=90),
             _wi(id=2, score=4.0, est_tokens=60)]     # better score/token ratio
    chosen, deferred, escalated = select_within_budget(items, budget=90)
    assert {i.id for i in chosen} == {1}
    assert {i.id for i in deferred} == {2}


def test_ties_broken_by_cheaper_then_id():
    items = [_wi(id=1, score=5.0, est_tokens=90),
             _wi(id=2, score=5.0, est_tokens=60)]     # equal score → cheaper first
    chosen, _d, _e = select_within_budget(items, budget=60)
    assert {i.id for i in chosen} == {2}


def test_greedy_fill_within_budget():
    items = [_wi(id=1, safety=True, est_tokens=100, score=5),
             _wi(id=2, safety=False, est_tokens=50, score=100),
             _wi(id=3, safety=False, est_tokens=40, score=10),
             _wi(id=4, safety=False, est_tokens=1000, score=1)]
    chosen, deferred, escalated = select_within_budget(items, budget=200)   # reserve 0.5 -> 100
    assert {i.id for i in chosen} == {1, 2, 3}      # safety(100) fits reserve; then discretionary
    assert {i.id for i in deferred} == {4}


def test_no_silent_truncation_all_accounted():
    items = [_wi(id=i, est_tokens=60, score=i) for i in range(1, 6)]
    chosen, deferred, escalated = select_within_budget(items, budget=120)
    assert len(chosen) + len(deferred) + len(escalated) == 5   # nothing dropped


def test_empty_is_safe():
    assert select_within_budget([], 100) == ([], [], [])


# --------------------------------------------------------------------------- #
# Engineering issue scoring: store work items -> reordered core-product queue
# --------------------------------------------------------------------------- #
def test_infer_domain_from_title():
    assert infer_domain("NIFTY 500 backtest falsely blocked", []) == "STRATEGY"
    assert infer_domain("sector screener crashes", []) == "SCREENER"
    assert infer_domain("option greeks IV wrong", []) == "OPTIONS_STRATEGY"


def test_classify_issue_bug_feature_safety_severity():
    assert classify_issue("fix crash on load", ["bug", "p0"]) == ("bug", False, 5)
    assert classify_issue("add support for X", ["feature"])[0] == "feature"
    _, safety, _ = classify_issue("gateway BOLA cross-tenant", ["security"])
    assert safety is True


def _swi(num, title, labels):
    return SimpleNamespace(id=str(num),
                           signal_json=json.dumps({"number": num, "title": title, "labels": labels}))


def test_prioritize_work_items_core_only_impact_first():
    items = [
        _swi(1, "NIFTY 500 backtest falsely blocked no market data", ["bug", "p0"]),  # STRATEGY base5
        _swi(2, "screener crash on empty result", ["bug"]),                           # SCREENER bug
        _swi(3, "executor orphan position on stop", ["live-trading", "bug"]),         # excluded
    ]
    weights = {"STRATEGY": 1.0, "SCREENER": 0.4}
    chosen = prioritize_work_items(items, weights, budget=200_000, core_only=True)
    ids = [wi.id for wi in chosen]
    assert "3" not in ids            # live-trading excluded from core-product scope
    assert ids[0] == "1"             # STRATEGY p0 leads (highest impact)
    assert set(ids) == {"1", "2"}    # both core items fit the budget


def test_est_tokens_uses_effort_model():
    m = {"base": 48000, "p0": 73000, "feature": 53000}
    assert est_tokens_for("bug", 3, m) == 48000
    assert est_tokens_for("bug", 5, m) == 73000        # p0/critical severity
    assert est_tokens_for("feature", 2, m) == 53000


def test_est_tokens_default_loads_committed_snapshot():
    # the real-anchored snapshot loads; a base fix estimate is a sane positive int
    assert 20_000 <= est_tokens_for("bug", 3) <= 200_000


def test_make_prioritizer_returns_bound_callable():
    pri = make_prioritizer({"STRATEGY": 1.0}, budget=200_000)
    items = [_swi(1, "backtest broken no market data", ["bug", "p0"]),
             _swi(9, "executor orphan on stop", ["live-trading"])]
    assert [wi.id for wi in pri(items)] == ["1"]     # core-only + budget-fitted
