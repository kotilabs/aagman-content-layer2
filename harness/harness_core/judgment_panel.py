"""judgment_panel.py — multi-model vote with escalate-on-split.

Queries every model in the task's chain (via router.call_model, so each panelist's
cost is logged), parses replies to pass/block, and tallies:

    pass-fraction >= threshold        -> pass
    pass-fraction <= 1 - threshold    -> block   (consensus against)
    anything in between               -> escalate (a genuine split; ask a human)

vote() matches the gate panel signature panel(criteria, artifact) -> list[dict], so
a panel can back a ComplianceGate/QualityGate directly.
"""
from __future__ import annotations

import re

from harness_core.agent_base import Verdict

_BLOCK_MARKERS = ("block", "fail", "reject", "violat")
_VERDICT_RE = re.compile(r"\bverdict\b[:\s\-]*\**\s*(pass|block|fail|reject)", re.I)


def _default_parse(text: str) -> dict:
    """Read the STATED verdict, not scary words in the rationale.

    A compliance/quality reviewer's reasoning routinely contains "does not
    violate", "nothing to reject", "no failures" — scanning the whole body for
    block markers (the old behaviour) misread every such approval as a block, so
    at threshold 1.0 the gate could never pass. Instead: honour a structured
    'VERDICT: pass|block' line, else the leading token of the first line, and only
    fall back to scanning that FIRST line (never the whole rationale)."""
    t = (text or "").strip()
    block = {"verdict": "block", "issues": [t[:300]]}
    passed = {"verdict": "pass", "issues": []}
    m = _VERDICT_RE.search(t)
    if m:
        return passed if m.group(1).lower() == "pass" else block
    first = (t.splitlines()[0].strip().strip("*#>-_`. \t").lower() if t else "")
    if first.startswith("pass"):
        return passed
    if any(first.startswith(x) for x in _BLOCK_MARKERS):
        return block
    if any(marker in first for marker in _BLOCK_MARKERS):
        return block
    return passed


class JudgmentPanel:
    def __init__(self, router, task_type, threshold=0.66, domain=None, step=None,
                 parse=None):
        self.router = router
        self.task_type = task_type
        self.threshold = threshold
        self.domain = domain
        self.step = step
        self.parse = parse or _default_parse

    def vote(self, criteria, artifact) -> list:
        chain = self.router.resolve(self.task_type, self.domain, self.step)
        prompt = (f"{criteria}\n\n--- ARTIFACT ---\n{artifact}\n\n"
                  f"State your verdict on the FIRST line as exactly "
                  f"'VERDICT: pass' or 'VERDICT: block'. If block, follow with the "
                  f"specific reason(s).")
        votes = []
        for model in chain:
            try:
                res = self.router.call_model(model, self.task_type, prompt)
            except Exception:
                continue  # a dead panelist doesn't sink the vote
            votes.append(self.parse(res.get("text", "")))
        return votes

    def decide(self, criteria, artifact) -> Verdict:
        return self._tally(self.vote(criteria, artifact))

    def _tally(self, votes) -> Verdict:
        if not votes:
            return Verdict(verdict="escalate", issues=["no panel votes"], score=0.0)
        passes = sum(1 for v in votes if v.get("verdict") == "pass")
        frac = passes / len(votes)
        issues = [i for v in votes for i in v.get("issues", [])]
        if frac >= self.threshold:
            return Verdict(verdict="pass", score=frac)
        if frac <= 1 - self.threshold:
            return Verdict(verdict="block", issues=issues, score=frac)
        return Verdict(verdict="escalate", issues=issues, score=frac)
