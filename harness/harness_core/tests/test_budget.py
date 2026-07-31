"""Phase-1 TDD: budget.py — daily spend guard, auto-pause on breach.

Authoritative spend = sum of TODAY's entries in logs/cost_log.jsonl (survives a
restart / boot recovery). On breach it writes a PAUSED file and pings once. This
is automatic and distinct from the manual kill switch.
"""
import json

from harness_core.budget import BudgetGuard

NOW = 1_700_000_000.0  # fixed epoch for deterministic "today"


def _log(tmp_path, entries):
    p = tmp_path / "cost_log.jsonl"
    p.write_text("".join(json.dumps(e) + "\n" for e in entries))
    return str(p)


def test_spent_today_sums_only_todays_entries(tmp_path):
    p = _log(tmp_path, [
        {"ts": NOW, "cost_usd": 1.0},
        {"ts": NOW - 10, "cost_usd": 0.5},
        {"ts": NOW - 86400, "cost_usd": 9.0},  # yesterday -> excluded
    ])
    g = BudgetGuard(daily_usd=5.0, cost_log_path=p, now=lambda: NOW)
    assert g.spent_today() == 1.5


def test_is_breached_at_or_over_limit(tmp_path):
    p = _log(tmp_path, [{"ts": NOW, "cost_usd": 5.0}])
    assert BudgetGuard(5.0, p, now=lambda: NOW).is_breached() is True


def test_not_breached_under_limit(tmp_path):
    p = _log(tmp_path, [{"ts": NOW, "cost_usd": 4.99}])
    assert BudgetGuard(5.0, p, now=lambda: NOW).is_breached() is False


def test_missing_cost_log_means_zero_spend(tmp_path):
    g = BudgetGuard(5.0, str(tmp_path / "nope.jsonl"), now=lambda: NOW)
    assert g.spent_today() == 0.0
    assert g.is_breached() is False


def test_enforce_writes_paused_and_notifies_once(tmp_path):
    p = _log(tmp_path, [{"ts": NOW, "cost_usd": 6.0}])
    sent = []
    paused = tmp_path / "PAUSED"
    g = BudgetGuard(5.0, p, now=lambda: NOW, notifier=sent.append,
                    paused_path=str(paused))
    assert g.enforce() is True
    assert paused.exists()
    assert len(sent) == 1
    g.enforce()  # still breached but already paused -> no second ping
    assert len(sent) == 1


def test_clear_removes_paused(tmp_path):
    p = _log(tmp_path, [{"ts": NOW, "cost_usd": 6.0}])
    paused = tmp_path / "PAUSED"
    g = BudgetGuard(5.0, p, now=lambda: NOW, paused_path=str(paused))
    g.enforce()
    assert g.is_paused()
    g.clear()
    assert not g.is_paused()


def test_record_triggers_pause_when_new_cost_tips_over(tmp_path):
    p = _log(tmp_path, [{"ts": NOW, "cost_usd": 4.0}])
    sent = []
    paused = tmp_path / "PAUSED"
    g = BudgetGuard(5.0, p, now=lambda: NOW, notifier=sent.append,
                    paused_path=str(paused))
    # router logs the new cost to the file, then calls record()
    with open(p, "a") as f:
        f.write(json.dumps({"ts": NOW, "cost_usd": 2.0}) + "\n")
    g.record(2.0)
    assert paused.exists()  # 6.0 >= 5.0
