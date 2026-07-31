"""gates.py — domain-agnostic decision gates.

Every gate returns a GateResult(verdict, issues, fixable) where verdict is one of
pass | block | escalate. Gates attach to any step of the loop via config.

ComplianceGate and QualityGate take an INJECTED `panel` callable so harness_core
stays LLM-agnostic and deterministically testable. The panel contract:

    panel(criteria_text: str, artifact: str) -> list[dict]
        each dict: {"verdict": "pass"|"block", "issues": [str], ...}

The single most important property, enforced by the genericity grep and proven in
tests: the SAME ComplianceGate class enforces one rules file for one domain and a
different rules file for another — only the rules file differs.
"""
from __future__ import annotations

import subprocess
import time as _time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

Verdict = str  # "pass" | "block" | "escalate"
Panel = Callable[[str, str], list[dict]]


@dataclass
class GateResult:
    """Universal gate return value."""
    verdict: Verdict
    issues: list[str] = field(default_factory=list)
    fixable: bool = False


class Gate(ABC):
    """A decision applied to a step's output. Subclasses implement check()."""

    @abstractmethod
    def check(self, payload: Any, ctx: dict | None = None) -> GateResult:
        ...


class TestGate(Gate):
    """Deterministic gate: runs a shell command; exit 0 == pass.

    fixable=True  -> a failure is a retryable block (inner fix loop)
    fixable=False -> a failure escalates to a human (outer safety net)
    """

    __test__ = False  # not a pytest test class (name collides with Test*)

    def __init__(self, test_command: str, cwd: str, fixable: bool = True,
                 timeout: int = 1800):
        self.test_command = test_command
        self.cwd = cwd
        self.fixable = fixable
        self.timeout = timeout

    def check(self, payload: Any = None, ctx: dict | None = None) -> GateResult:
        proc = subprocess.run(
            self.test_command, shell=True, cwd=self.cwd,
            capture_output=True, text=True, timeout=self.timeout,
        )
        if proc.returncode == 0:
            return GateResult(verdict="pass")
        out = (proc.stdout or "") + (proc.stderr or "")
        issues = [ln for ln in out.splitlines() if ln.strip()][-40:] or [
            f"command failed with exit {proc.returncode}"
        ]
        if self.fixable:
            return GateResult(verdict="block", issues=issues, fixable=True)
        return GateResult(verdict="escalate", issues=issues, fixable=False)


class ComplianceGate(Gate):
    """LLM-vs-rules-file gate. Reads rules_file once (fail fast if missing), asks
    the panel whether the artifact violates it, blocks below `threshold`
    pass-fraction. Compliance uses threshold=1.0 (unanimous).

    DETERMINISTIC layer: if the rules file declares a `REQUIRED_STRINGS` section
    (bulleted list under a `## REQUIRED_STRINGS` heading), every one of those
    strings MUST appear verbatim in the artifact — checked in code, BEFORE and
    independent of the panel. A mandatory legal disclosure (e.g. RIA name + reg
    number) must never depend on an LLM noticing its absence. A missing string
    is a fixable block (add the disclosure and retry)."""

    def __init__(self, rules_file: str, panel: Panel, threshold: float = 1.0):
        self.rules_text = Path(rules_file).read_text()  # FileNotFoundError if absent
        self.rules_file = rules_file
        self.panel = panel
        self.threshold = threshold
        self.required_strings = _parse_required_strings(self.rules_text)

    def check(self, payload: Any, ctx: dict | None = None) -> GateResult:
        artifact = payload if isinstance(payload, str) else str(payload)
        missing = [s for s in self.required_strings if s not in artifact]
        if missing:
            return GateResult(
                verdict="block",
                issues=[f"missing required string: {s}" for s in missing],
                fixable=True,
            )
        return _tally(self.panel(self.rules_text, artifact), self.threshold)


class QualityGate(Gate):
    """Multi-model quality vote. Passes when pass-fraction >= threshold."""

    def __init__(self, panel: Panel, threshold: float = 0.66, criteria: str = ""):
        self.panel = panel
        self.threshold = threshold
        self.criteria = criteria

    def check(self, payload: Any, ctx: dict | None = None) -> GateResult:
        artifact = payload if isinstance(payload, str) else str(payload)
        return _tally(self.panel(self.criteria, artifact), self.threshold)


class HumanGate(Gate):
    """Human approval via Telegram + an approval file. ASYNC by design: it does
    NOT block-poll for hours. On first encounter it writes a REQUESTED marker,
    pings the notifier once, and returns 'escalate' (the loop parks the work item
    at status awaiting_gate:<name>). On resume it reads the approval file:

        APPROVED present -> pass
        REJECTED present -> block (not fixable; a human said no)
        neither          -> escalate (still waiting; flags timeout in issues)

    ctx must carry 'gate_dir' = workdir/gates/{work_item_id}/{gate_name}.
    notifier(text) and now() are injected so this is deterministically testable.
    """

    def __init__(self, gate_name: str, timeout_hours: float = 24,
                 notifier: Callable[[str], Any] | None = None,
                 now: Callable[[], float] | None = None):
        self.gate_name = gate_name
        self.timeout_hours = timeout_hours
        self.notifier = notifier or (lambda text: None)
        self.now = now or _time.time

    def check(self, payload: Any, ctx: dict | None = None) -> GateResult:
        ctx = ctx or {}
        gate_dir = Path(ctx["gate_dir"])
        gate_dir.mkdir(parents=True, exist_ok=True)
        if (gate_dir / "APPROVED").exists():
            return GateResult(verdict="pass")
        if (gate_dir / "REJECTED").exists():
            return GateResult(verdict="block",
                              issues=[f"human rejected gate '{self.gate_name}'"],
                              fixable=False)
        requested = gate_dir / "REQUESTED"
        if not requested.exists():
            requested.write_text(str(self.now()))
            self.notifier(
                f"[gate:{self.gate_name}] approval needed.\n"
                f"Approve: touch {gate_dir / 'APPROVED'}\n"
                f"Reject:  touch {gate_dir / 'REJECTED'}\n\n"
                f"{str(payload)[:1500]}"
            )
            return GateResult(verdict="escalate",
                              issues=[f"awaiting human gate '{self.gate_name}'"])
        try:
            requested_at = float(requested.read_text().strip())
        except ValueError:
            requested_at = self.now()
        issues = [f"awaiting human gate '{self.gate_name}'"]
        if self.now() - requested_at > self.timeout_hours * 3600:
            issues.append(
                f"timeout: gate '{self.gate_name}' pending > {self.timeout_hours}h")
        return GateResult(verdict="escalate", issues=issues)


def _parse_required_strings(rules_text: str) -> list[str]:
    """Extract the bulleted items under a `## REQUIRED_STRINGS` heading.

    Generic markdown parse (no domain knowledge): find the heading whose text is
    REQUIRED_STRINGS (case-insensitive, '_' or space), then take every bullet
    (`- ` / `* `) until the next heading. Surrounding backticks are stripped so
    `- \\`INA000021951\\`` yields INA000021951. Absent section => [] (gate then
    behaves as a pure panel gate)."""
    lines = rules_text.splitlines()
    out: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip().replace("_", " ").upper()
            in_section = heading == "REQUIRED STRINGS"
            continue
        # A real markdown bullet is a '-'/'*' followed by a space; this excludes
        # horizontal rules ('---', '***') and bare markers.
        if in_section and stripped[:2] in ("- ", "* "):
            item = stripped[2:].strip().strip("`").strip()
            if item:
                out.append(item)
    return out


def _tally(votes: list[dict], threshold: float) -> GateResult:
    """Aggregate panel votes into a GateResult by pass-fraction vs threshold."""
    if not votes:
        # The panel could not run (every panelist errored: auth/infra/outage).
        # That is absence of expected data, not a defect in the artifact — escalate
        # to a human; a fixable block would burn revise cycles that cannot fix an outage.
        return GateResult(verdict="escalate",
                          issues=["no panel votes — panel unavailable"])
    passes = sum(1 for v in votes if v.get("verdict") == "pass")
    if passes / len(votes) >= threshold:
        return GateResult(verdict="pass")
    issues = [i for v in votes for i in v.get("issues", [])]
    return GateResult(verdict="block", issues=issues, fixable=True)
