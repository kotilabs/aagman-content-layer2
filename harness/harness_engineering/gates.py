"""harness_engineering/gates.py — engineering-specific gates.

CriticalApprovalGate is a thin domain gate: a fix for a CRITICAL-labelled issue
(p0 / ship-blocker / critical) needs an EXTRA human sign-off before the PR is
raised, on top of the normal amit_merge gate. Non-critical issues pass straight
through. It reads the issue labels off the work item and, when critical,
delegates to a HumanGate("approve_critical").
"""
from __future__ import annotations

import json

from harness_core.gates import GateResult, HumanGate

_CRITICAL = {"critical", "p0", "ship-blocker", "blocker"}


class CriticalApprovalGate:
    gate_name = "approve_critical"

    def __init__(self, notifier=None, now=None, timeout_hours: float = 48):
        self._human = HumanGate("approve_critical", timeout_hours=timeout_hours,
                                notifier=notifier, now=now)

    def check(self, payload, ctx=None) -> GateResult:
        labels = self._labels((ctx or {}).get("work_item"))
        if not (labels & _CRITICAL):
            return GateResult(verdict="pass")
        return self._human.check(payload, ctx)

    @staticmethod
    def _labels(wi) -> set:
        if wi is None:
            return set()
        try:
            raw = json.loads(getattr(wi, "signal_json", "") or "{}").get("labels", [])
        except (ValueError, TypeError):
            return set()
        return {str(l).lower() for l in raw}
