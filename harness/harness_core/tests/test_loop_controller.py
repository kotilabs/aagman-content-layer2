"""Phase-1 TDD: loop_controller.py — fixable-retry accounting per step/gate.

Operates on a work item's loop_counts dict ({"adversarial":1,"tester":0}); pure and
immutable so it is trivially resumable and testable.
"""
from harness_core.loop_controller import LoopController


def test_should_retry_under_limit():
    lc = LoopController()
    assert lc.should_retry({}, "tester", limit=2) is True
    assert lc.should_retry({"tester": 1}, "tester", limit=2) is True
    assert lc.should_retry({"tester": 2}, "tester", limit=2) is False


def test_record_increments_immutably():
    lc = LoopController()
    c0 = {}
    c1 = lc.record(c0, "adversarial")
    assert c1 == {"adversarial": 1}
    assert c0 == {}  # original untouched
    assert lc.record(c1, "adversarial") == {"adversarial": 2}


def test_default_limit_when_unspecified():
    lc = LoopController(default_limit=3)
    assert lc.should_retry({"x": 2}, "x") is True
    assert lc.should_retry({"x": 3}, "x") is False


def test_keys_are_independent():
    lc = LoopController()
    counts = {"tester": 2, "adversarial": 0}
    assert lc.should_retry(counts, "tester", 2) is False
    assert lc.should_retry(counts, "adversarial", 2) is True
