"""budget.py — daily spend guard with automatic pause on breach.

Authoritative spend is the sum of TODAY's entries in logs/cost_log.jsonl (the
router writes there), so it survives a restart. On breach it writes a PAUSED file
and pings the notifier once. This is automatic and distinct from the manual kill
switch: PAUSED lifts when a human clears it or at midnight (a new day resets the
running total naturally, since spent_today only counts today's rows).
"""
from __future__ import annotations

import datetime as _dt
import json
import time as _time
from pathlib import Path


class BudgetGuard:
    def __init__(self, daily_usd, cost_log_path, now=None, notifier=None,
                 paused_path=None):
        self.daily_usd = float(daily_usd)
        self.cost_log_path = Path(cost_log_path)
        self.now = now or _time.time
        self.notifier = notifier or (lambda text: None)
        self.paused_path = (Path(paused_path) if paused_path
                            else self.cost_log_path.parent.parent / "PAUSED")

    def spent_today(self) -> float:
        if not self.cost_log_path.exists():
            return 0.0
        today = _dt.date.fromtimestamp(self.now())
        total = 0.0
        for line in self.cost_log_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if _dt.date.fromtimestamp(float(rec["ts"])) == today:
                    total += float(rec.get("cost_usd", 0.0))
            except (ValueError, KeyError):
                continue
        return total

    def is_breached(self) -> bool:
        return self.spent_today() >= self.daily_usd

    def is_paused(self) -> bool:
        return self.paused_path.exists()

    def record(self, cost: float = 0.0) -> bool:
        """Called by the router after each logged call; re-check + auto-pause."""
        return self.enforce()

    def enforce(self) -> bool:
        if not self.is_breached():
            return False
        if not self.is_paused():
            spent = self.spent_today()
            self.paused_path.parent.mkdir(parents=True, exist_ok=True)
            self.paused_path.write_text(
                f"budget breach: spent ${spent:.2f} >= ${self.daily_usd:.2f} "
                f"on {_dt.date.fromtimestamp(self.now())}")
            self.notifier(
                f"⛔ BUDGET PAUSED: today's spend ${spent:.2f} hit the "
                f"${self.daily_usd:.2f} daily cap. Harness paused until cleared "
                f"or midnight reset.")
        return True

    def clear(self):
        if self.paused_path.exists():
            self.paused_path.unlink()
