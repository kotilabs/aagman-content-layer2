"""harness_content/judges/content_judge.py — Graph Engineering multi-lens judge.

Runs five dedicated parallel lenses over the research artifact and all produced
surface drafts. Each lens audits one dimension; any blocker-class issue fails the
draft. The judge produces a structured review file and returns a Verdict with
per-surface blocker lists so the correction loop knows what to fix.
"""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from harness_core.agent_base import Verdict


# Reuse the Layer 2 surface conventions.
from harness_content.layer2_full_agents import _SURFACE_FILE, _SURFACE_LABELS

RIA_NAME = "Koti Labs"
RIA_REG = "INA000021951"

_LENS_CONTRACT = (
    "\nBe SKEPTICAL BY DEFAULT. Judge ONLY the produced surfaces below. Do not see "
    "the research artifact; verify claims independently. SEVERITY: a factual error, "
    "misleading compression, cross-surface contradiction, or advisory framing is a "
    "BLOCKER; a style nit is should-fix (still pass). State your verdict on the FIRST "
    "line as exactly 'VERDICT: pass' or 'VERDICT: block'. If block, list every blocker "
    "in this exact format:\n\n"
    "BLOCKERS:\n"
    "- Surface: <exact surface label from below> | Issue: <one-line problem> | Fix: <specific correction>\n"
    "- Surface: <exact surface label from below> | Issue: <one-line problem> | Fix: <specific correction>\n\n"
    "Also list surfaces that have no blockers:\n"
    "PASSING SURFACES:\n"
    "- <exact surface label from below>\n\n"
    "Use ONLY the exact surface labels shown below.\n\n"
    "--- PRODUCED SURFACES ---\n{drafts}\n"
)

_LENS_PROMPTS = [
    (
        "factual-integrity",
        "You are the Aagman Layer-2 Markets Reviewer auditing ONE thing: FACTUAL "
        "INTEGRITY. Every checkable claim/number in every surface must trace to a "
        "verifiable source; no interpretation presented as fact; no stale data as "
        "current; no fabricated figure, source, or verdict."
        + _LENS_CONTRACT,
    ),
    (
        "reasoning-quality",
        "You are the Aagman Layer-2 Markets Reviewer auditing ONE thing: REASONING "
        "QUALITY. The argument in each surface must be valid in its own domain (monetary "
        "policy, commodities, geopolitics, cross-asset linkages, market structure); a "
        "valid conclusion built on invalid reasoning is still a blocker."
        + _LENS_CONTRACT,
    ),
    (
        "independent-gaps",
        "You are the Aagman Layer-2 Markets Reviewer auditing ONE thing: INDEPENDENT "
        "GAPS. Surface what the set of outputs misses — counterarguments not engaged, "
        "cross-asset signals that contradict the thesis, tail risks, and claims where "
        "the opposite case is stronger than presented."
        + _LENS_CONTRACT,
    ),
    (
        "consistency",
        "You are the Aagman Layer-2 Markets Reviewer auditing ONE thing: CONSISTENCY. "
        "All surfaces from this signal must claim the same thing about the world; no "
        "compression-distortion (a nuanced claim collapsed into a misleading line); "
        "every line survives being quoted alone."
        + _LENS_CONTRACT,
    ),
    (
        "voice-framing",
        "You are the Aagman Layer-2 Markets Reviewer auditing ONE thing: VOICE & "
        "FRAMING. Educational only; no buy/sell call, price target, urgency, hype "
        "adjective, engagement bait, or CTA; every surface must end on open cognitive "
        "tension, not a call-to-action. The mandatory SEBI disclosure must be present."
        + _LENS_CONTRACT,
    ),
]


class Layer2ContentJudge:
    """Graph-engineering content judge for the Layer 2 workflow."""

    def __init__(self, router: Any, workdir: str | Path,
                 memory_factory: Any | None = None):
        self.router = router
        self.workdir = Path(workdir)
        self.memory_factory = memory_factory

    def review_path(self, signal_id: str) -> Path:
        return self.workdir / "reviews" / f"{signal_id}-content-judge.md"

    def run(self, signal_id: str, surfaces: list[str]) -> Verdict:
        drafts = self._load_drafts(signal_id, surfaces)
        lessons = self._recall_lessons()

        draft_block = "\n\n".join(
            f"## {_SURFACE_LABELS[s]}\n\n{drafts[s]}"
            for s in surfaces if s in drafts
        )

        findings = self._run_lenses(draft_block, lessons)
        review_text = self._assemble_review(findings, lessons)
        review_file = self.review_path(signal_id)
        review_file.parent.mkdir(parents=True, exist_ok=True)
        review_file.write_text(review_text, encoding="utf-8")

        blockers = self._blocker_surfaces(findings, surfaces)
        return Verdict(
            verdict="pass" if not blockers else "block",
            issues=blockers,
            score=1.0 if not blockers else 0.0,
            meta={
                "review_text": review_text,
                "blocker_surfaces": blockers,
                "review_file": str(review_file),
                "findings": findings,
            },
        )

    def _run_lenses(self, draft_block: str,
                    lessons: str) -> dict[str, str]:
        """Run all lenses in parallel. Return {lens_name: response_text}."""
        def one(name_prompt):
            name, prompt_template = name_prompt
            prompt = prompt_template.format(drafts=draft_block)
            if lessons:
                prompt += f"\n\nLESSONS FROM PAST REJECTIONS:\n{lessons}\n"
            res = self.router.complete(
                "judge_panel", prompt, domain="content", step="judge")
            return name, res.get("text", "")

        with ThreadPoolExecutor(max_workers=len(_LENS_PROMPTS)) as ex:
            return dict(ex.map(one, _LENS_PROMPTS))

    def _assemble_review(self, findings: dict[str, str],
                         lessons: str) -> str:
        lines = ["# Content Judge Review", ""]
        if lessons:
            lines.append("## Lessons recalled")
            lines.append(lessons)
            lines.append("")
        lines.append("## Findings by lens")
        lines.append("")
        for name, text in findings.items():
            lines.append(f"### {name}")
            lines.append("")
            lines.append(text)
            lines.append("")
        return "\n".join(lines)

    def _blocker_surfaces(self, findings: dict[str, str],
                          surfaces: list[str]) -> list[str]:
        """Return surfaces that have at least one blocker across any lens.

        Parses the explicit BLOCKERS list each lens must emit. Surface labels are
        matched against _SURFACE_LABELS and mapped back to surface keys.
        """
        label_to_surface = {v.lower(): k for k, v in _SURFACE_LABELS.items()}
        blocked: set[str] = set()

        for text in findings.values():
            lower = text.lower()
            if "verdict: pass" in lower:
                continue
            # Find the BLOCKERS section.
            start = lower.find("blockers:")
            if start == -1:
                continue
            end = lower.find("passing surfaces:", start)
            block_section = text[start:end if end != -1 else None]
            for line in block_section.splitlines():
                line = line.strip()
                if not line.startswith("-") or "surface:" not in line.lower():
                    continue
                # Extract the surface label between "Surface:" and "|".
                m = re.search(r"surface:\s*([^|]+)", line, re.IGNORECASE)
                if not m:
                    continue
                label = m.group(1).strip().lower()
                surface_key = label_to_surface.get(label)
                if surface_key and surface_key in surfaces:
                    blocked.add(surface_key)
                elif label in surfaces:
                    blocked.add(label)

        return sorted(blocked)

    def _load_drafts(self, signal_id: str, surfaces: list[str]) -> dict[str, str]:
        drafts: dict[str, str] = {}
        for surface in surfaces:
            path = (self.workdir / "drafts" /
                    f"signal-{signal_id}-{_SURFACE_FILE[surface]}")
            if path.exists():
                drafts[surface] = self._read(path)
        return drafts

    def _recall_lessons(self) -> str:
        if not self.memory_factory:
            return ""
        mem = self.memory_factory("content", "judge")
        texts = []
        for lid in mem.top_k("content quality review", k=5):
            les = mem.get(lid)
            if les and les.text:
                texts.append(f"- {les.text}")
        return "\n".join(texts)

    @staticmethod
    def _read(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, TypeError):
            return ""
