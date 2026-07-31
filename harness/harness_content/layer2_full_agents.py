"""layer2_full_agents.py — full content agents for the aagman-harness.

These agents implement the complete content workflow: signal scouting,
research, writing across surfaces, review, SEO, and publish. They read prompts
from harness_content/prompts/ and voice guides from harness_content/voice/,
call the harness router (routed through the Kimi Code bridge), and read/write
files according to the Layer 2 conventions.

All file paths are relative to a configurable workdir (normally
layer2_full_run/). The runner is responsible for human gates and sequencing.
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from harness_core.agent_base import Artifact, Idea, Signal, Verdict

RIA_NAME = "Koti Labs"
RIA_REG = "INA000021951"

_REPO = Path(__file__).resolve().parent.parent
_PROMPTS = _REPO / "harness_content" / "prompts"
_VOICE = _REPO / "harness_content" / "voice"

_SURFACES = {
    "blog": "blog_writer.md",
    "thread": "thread_writer.md",
    "carousel_linkedin": "carousel_writer_promo.md",
    "carousel_instagram": "carousel_writer_promo.md",
    "infographic": "infographic_ideator.md",
}

_SURFACE_LABELS = {
    "blog": "Substack blog",
    "thread": "X thread",
    "carousel_linkedin": "LinkedIn carousel",
    "carousel_instagram": "Instagram carousel",
    "infographic": "Infographic concepts",
}

_SURFACE_FILE = {
    "blog": "blog.md",
    "thread": "thread.md",
    "carousel_linkedin": "carousel-linkedin.md",
    "carousel_instagram": "carousel-instagram.md",
    "infographic": "infographic-concepts.md",
}


def _read(path: str | Path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, TypeError):
        return ""


def _read_prompt(name: str) -> str:
    return _read(_PROMPTS / name)


def _read_voice(name: str) -> str:
    return _read(_VOICE / name)


def _tokens(text: str) -> int:
    return int(len(text.split()) * 1.3)


def _disclosure() -> str:
    return (f"Educational content from {RIA_NAME} (SEBI RIA {RIA_REG}). "
            f"Not investment advice — no buy/sell recommendation.")


def _safe_id(raw: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", raw.lower()).strip("-")


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


# --------------------------------------------------------------------------- #
# Signal identifier — macro + realtime lenses
# --------------------------------------------------------------------------- #
@dataclass
class SignalCandidate:
    """One signal extracted from a digest."""
    id: str
    title: str
    lens: str  # macro | realtime
    why_now: str = ""
    angle: str = ""
    sources: list[str] = field(default_factory=list)
    raw_block: str = ""


class Layer2SignalIdentifier:
    """Run the macro and realtime signal identifier prompts and write a digest.

    Uses deterministic request IDs so the runner can resume after an assistant
    provides responses via the Kimi Code bridge. Passes timeout=0 to the router
    so it raises AwaitingResponseError instead of blocking.
    """

    def __init__(self, router, workdir: str | Path):
        self.router = router
        self.workdir = Path(workdir)

    def run(self, date: str | None = None) -> Path:
        date = date or _today()
        digest_dir = self.workdir / "signals"
        digest_dir.mkdir(parents=True, exist_ok=True)
        digest_path = digest_dir / f"{date}-digest.md"

        macro_req_id = f"layer2-signal-macro-{date}"
        realtime_req_id = f"layer2-signal-realtime-{date}"

        macro_text = self._run_lens(
            lens="macro",
            prompt_file="signal_identifier_macro.md",
            request_id=macro_req_id,
            date=date,
        )
        realtime_text = self._run_lens(
            lens="realtime",
            prompt_file="signal_identifier_realtime.md",
            request_id=realtime_req_id,
            date=date,
        )

        digest = self._assemble_digest(date, macro_text, realtime_text)
        digest_path.write_text(digest, encoding="utf-8")
        return digest_path

    def _run_lens(self, lens: str, prompt_file: str, request_id: str,
                  date: str) -> str:
        cache = self.workdir / "signals" / f".{date}-{lens}-response.md"
        if cache.exists():
            return cache.read_text(encoding="utf-8").strip()

        prompt = (
            f"{_read_prompt(prompt_file)}\n\n"
            "Run the full workflow above and produce the complete output. "
            "Include every required section."
        )
        res = self.router.complete(
            "complex_planning",
            prompt,
            domain="content",
            step=f"signal_{lens}",
            request_id=request_id,
            timeout=0,
        )
        text = res["text"].strip()
        cache.write_text(text, encoding="utf-8")
        return text

    def _assemble_digest(self, date: str, macro: str, realtime: str) -> str:
        return (
            f"# Aagman Layer 2 Signal Digest — {date}\n\n"
            f"> Macro lens (weekly) + realtime lens (daily) combined.\n\n"
            f"---\n\n"
            f"## Macro / Structural Lens\n\n{macro}\n\n"
            f"---\n\n"
            f"## Real-time Market Lens\n\n{realtime}\n\n"
            f"---\n\n"
            f"## Operator notes\n\n"
            f"- Review both lenses.\n"
            f"- Pick one signal and the surfaces to produce.\n"
            f"- Write selection to `state/tickets/{date}-<signal-id>.md`.\n"
        )


# --------------------------------------------------------------------------- #
# Research agent — canonical artifact from a ticket
# --------------------------------------------------------------------------- #
class Layer2ResearchAgentFull:
    """Produce the canonical research artifact for a selected signal."""

    def __init__(self, router, workdir: str | Path, memory_factory=None):
        self.router = router
        self.workdir = Path(workdir)
        self.memory_factory = memory_factory

    def run(self, ticket_path: str | Path) -> Path:
        ticket_path = Path(ticket_path)
        ticket = self._parse_ticket(ticket_path)
        signal_id = ticket["signal_id"]
        signal_title = ticket.get("title", signal_id)
        brief = ticket.get("brief", "")
        sources = ticket.get("sources", [])

        research_dir = self.workdir / "research"
        research_dir.mkdir(parents=True, exist_ok=True)
        research_file = research_dir / f"signal-{signal_id}.md"

        sources_block = ""
        if sources:
            sources_block = "SOURCE POINTERS FROM TICKET:\n" + "\n".join(
                f"- {s}" for s in sources) + "\n\n"

        lessons = self._recall_lessons(brief)
        lessons_block = f"LESSONS FROM PAST CYCLES:\n{lessons}\n\n" if lessons else ""

        prompt = (
            f"{_read_prompt('research_agent.md')}\n\n"
            f"---\n\n"
            f"SIGNAL ID: {signal_id}\n"
            f"SIGNAL TITLE: {signal_title}\n\n"
            f"SIGNAL BRIEF:\n{brief}\n\n"
            f"{sources_block}"
            f"{lessons_block}"
            f"Write the full research artifact to `research/signal-{signal_id}.md`."
        )
        res = self.router.complete("complex_planning", prompt,
                                   domain="content", step="ideate")
        research_file.write_text(res["text"].strip(), encoding="utf-8")
        return research_file

    def _recall_lessons(self, query: str) -> str:
        if not self.memory_factory:
            return ""
        mem = self.memory_factory("content", "ideate")
        texts = []
        for lid in mem.top_k(query, k=5):
            les = mem.get(lid)
            if les and les.text:
                texts.append(f"- {les.text}")
        return "\n".join(texts)

    @staticmethod
    def _parse_ticket(path: Path) -> dict:
        text = _read(path)
        out: dict[str, Any] = {
            "signal_id": "",
            "title": "",
            "date": "",
            "surfaces": [],
            "brief": "",
            "sources": [],
            "operator_notes": "",
        }
        # Simple YAML-ish frontmatter parse.
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm = parts[1].strip()
                body = parts[2].strip()
                try:
                    out.update(yaml.safe_load(fm) or {})
                except Exception:
                    pass
                out["brief"] = body
        else:
            out["brief"] = text

        # Normalize surfaces.
        surfaces = out.get("surfaces") or []
        if isinstance(surfaces, str):
            surfaces = [s.strip() for s in surfaces.split(",") if s.strip()]
        out["surfaces"] = surfaces

        sources = out.get("sources") or []
        if isinstance(sources, str):
            sources = [s.strip() for s in sources.splitlines() if s.strip()]
        out["sources"] = sources

        return out


# --------------------------------------------------------------------------- #
# Writer — fan-out surface creator / reviser
# --------------------------------------------------------------------------- #
class Layer2Writer:
    """Create or revise one surface draft from a research artifact."""

    def __init__(self, router, workdir: str | Path, memory_factory=None):
        self.router = router
        self.workdir = Path(workdir)
        self.memory_factory = memory_factory

    def draft_path(self, signal_id: str, surface: str) -> Path:
        return (self.workdir / "drafts" /
                f"signal-{signal_id}-{_SURFACE_FILE[surface]}")

    def create(self, signal_id: str, surface: str,
               mode: str = "promo") -> Path:
        prompt_file = _SURFACES[surface]
        label = _SURFACE_LABELS[surface]
        research = self._research(signal_id)

        voice_parts = [_read_voice("layer2_voice_base.md")]
        if "carousel" in surface:
            voice_parts.append(_read_voice("carousel_overlay.md"))
            # Use standalone prompt if there is no blog for this signal.
            blog_path = self.draft_path(signal_id, "blog")
            if not blog_path.exists() or mode == "standalone":
                prompt_file = "carousel_writer_standalone.md"
        elif surface == "thread":
            voice_parts.append(_read_voice("thread_overlay.md"))
        elif surface == "blog":
            voice_parts.append(_read_voice("substack_overlay.md"))
        voice_block = "\n\n".join(voice_parts)

        extra = ""
        if "carousel" in surface and prompt_file == "carousel_writer_promo.md":
            blog = _read(self.draft_path(signal_id, "blog"))
            extra = f"SOURCE BLOG DRAFT:\n{blog}\n\n"

        lessons = self._recall_lessons(surface)
        lessons_block = f"LESSONS FROM PAST CYCLES:\n{lessons}\n\n" if lessons else ""

        prompt = (
            f"{_read_prompt(prompt_file)}\n\n"
            f"---\n\n"
            f"BRAND VOICE:\n{voice_block}\n\n"
            f"SURFACE: {label}\n\n"
            f"RESEARCH ARTIFACT:\n{research}\n\n"
            f"{extra}"
            f"{lessons_block}"
            f"Write the {label} now."
        )
        res = self.router.complete("content_gen", prompt,
                                   domain="content", step="create")
        body = res["text"].strip()
        disclosure = _disclosure()
        if surface in ("blog", "thread", "carousel_linkedin", "carousel_instagram"):
            if not body.startswith(disclosure):
                body = f"{disclosure}\n\n{body}"

        draft_path = self.draft_path(signal_id, surface)
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(body, encoding="utf-8")
        return draft_path

    def revise(self, signal_id: str, surface: str,
               review_path: str | Path) -> Path:
        prompt_file = _SURFACES[surface]
        label = _SURFACE_LABELS[surface]
        draft_path = self.draft_path(signal_id, surface)
        body = _read(draft_path)
        review = _read(review_path)

        if "carousel" in surface:
            blog_path = self.draft_path(signal_id, "blog")
            if not blog_path.exists():
                prompt_file = "carousel_writer_standalone.md"

        lessons = self._recall_lessons(surface)
        lessons_block = f"LESSONS FROM PAST CYCLES:\n{lessons}\n\n" if lessons else ""

        prompt = (
            f"{_read_prompt(prompt_file)}\n\n"
            f"---\n\n"
            f"CORRECTION MODE. Read the content judge review below and revise the "
            f"{label}. Do not use the original research notes; fix the draft using "
            f"only the judge's feedback.\n\n"
            f"CONTENT JUDGE REVIEW:\n{review}\n\n"
            f"CURRENT DRAFT:\n{body}\n\n"
            f"{lessons_block}"
            f"Rewrite the full {label} with every blocker fixed. Preserve the "
            f"educational-only framing, brand voice, and mandatory disclosure. "
            f"Update the draft in place."
        )
        res = self.router.complete("content_gen", prompt,
                                   domain="content", step="create")
        new_body = res["text"].strip()
        disclosure = _disclosure()
        if surface in ("blog", "thread", "carousel_linkedin", "carousel_instagram"):
            if not new_body.startswith(disclosure):
                new_body = f"{disclosure}\n\n{new_body}"
        draft_path.write_text(new_body, encoding="utf-8")
        return draft_path

    def _recall_lessons(self, surface: str) -> str:
        if not self.memory_factory:
            return ""
        mem_create = self.memory_factory("content", "create")
        mem_analytics = self.memory_factory("content", "analytics")
        texts = []
        query = f"{surface} writing quality"
        for mem in (mem_create, mem_analytics):
            for lid in mem.top_k(query, k=3):
                les = mem.get(lid)
                if les and les.text:
                    texts.append(f"- {les.text}")
        return "\n".join(texts[:6])

    def _research(self, signal_id: str) -> str:
        return _read(self.workdir / "research" / f"signal-{signal_id}.md")


# --------------------------------------------------------------------------- #
# Markets reviewer — universal gate across all surfaces
# --------------------------------------------------------------------------- #
class Layer2MarketsReviewerFull:
    """Run the markets reviewer prompt on all produced surfaces for a signal.

    Returns a Verdict with the review text in meta['review_text'] and a list of
    blocker surfaces in meta['blocker_surfaces'].
    """

    def __init__(self, router, workdir: str | Path):
        self.router = router
        self.workdir = Path(workdir)

    def review_path(self, signal_id: str) -> Path:
        return self.workdir / "reviews" / f"{signal_id}-markets-review.md"

    def run(self, signal_id: str, surfaces: list[str]) -> Verdict:
        research = _read(self.workdir / "research" / f"signal-{signal_id}.md")
        drafts: list[str] = []
        for surface in surfaces:
            path = (self.workdir / "drafts" /
                    f"signal-{signal_id}-{_SURFACE_FILE[surface]}")
            if path.exists():
                drafts.append(
                    f"## {_SURFACE_LABELS[surface]}\n\n{_read(path)}\n\n"
                )

        draft_block = "\n".join(drafts)
        prompt = (
            f"{_read_prompt('markets_reviewer.md')}\n\n"
            f"---\n\n"
            f"RESEARCH ARTIFACT:\n{research}\n\n"
            f"PRODUCED SURFACES:\n\n{draft_block}\n\n"
            f"Write the full structured markets review now."
        )
        res = self.router.complete("judge_panel", prompt,
                                   domain="content", step="judge")
        review_text = res["text"].strip()
        review_file = self.review_path(signal_id)
        review_file.parent.mkdir(parents=True, exist_ok=True)
        review_file.write_text(review_text, encoding="utf-8")

        blockers = self._blocker_surfaces(review_text, surfaces)
        return Verdict(
            verdict="pass" if not blockers else "block",
            issues=blockers,
            score=1.0 if not blockers else 0.0,
            meta={"review_text": review_text,
                  "blocker_surfaces": blockers,
                  "review_file": str(review_file)},
        )

    @staticmethod
    def _blocker_surfaces(review_text: str, surfaces: list[str]) -> list[str]:
        """Return surfaces that have at least one blocker in the review."""
        blocked: list[str] = []
        lower = review_text.lower()
        # Detect explicit blocker markers in per-surface sections.
        section_map = {
            "blog": ["blog feedback", "blog"],
            "thread": ["thread feedback", "thread"],
            "carousel_linkedin": ["carousel feedback (linkedin)", "linkedin carousel"],
            "carousel_instagram": ["carousel feedback (instagram)", "instagram carousel"],
            "infographic": ["infographic feedback", "infographic"],
        }
        for surface in surfaces:
            for header in section_map.get(surface, [surface]):
                idx = lower.find(f"## {header}")
                if idx == -1:
                    idx = lower.find(f"### {header}")
                if idx == -1:
                    continue
                # Look for blocker markers in the next 3000 chars.
                chunk = lower[idx:idx + 3000]
                # Exclude verdict phrases like "0 blockers" or "no blockers".
                if "no blockers" in chunk or "0 blockers" in chunk:
                    continue
                # Require an explicit severity marker (table cell or tag).
                if "| blocker |" in chunk or "[blocker]" in chunk or "severity: blocker" in chunk:
                    blocked.append(surface)
                    break
        return blocked


# --------------------------------------------------------------------------- #
# Corrector — apply reviewer feedback to a specific surface
# --------------------------------------------------------------------------- #
class Layer2Corrector:
    """Thin wrapper around Layer2Writer.revise for the correction loop."""

    def __init__(self, writer: Layer2Writer):
        self.writer = writer

    def correct(self, signal_id: str, surface: str,
                review_path: str | Path) -> Path:
        return self.writer.revise(signal_id, surface, review_path)


# --------------------------------------------------------------------------- #
# SEO/AEO auditor + final corrector (blog only)
# --------------------------------------------------------------------------- #
class Layer2SEOAuditor:
    """Run the SEO/AEO audit prompt on the blog draft."""

    def __init__(self, router, workdir: str | Path):
        self.router = router
        self.workdir = Path(workdir)

    def audit_path(self, signal_id: str) -> Path:
        return self.workdir / "reviews" / f"{signal_id}-seo-aeo-audit.md"

    def run(self, signal_id: str) -> Path:
        blog = _read(self.workdir / "drafts" / f"signal-{signal_id}-blog.md")
        research = _read(self.workdir / "research" / f"signal-{signal_id}.md")
        prompt = (
            f"{_read_prompt('seo_aeo_audit.md')}\n\n"
            f"---\n\n"
            f"BLOG DRAFT:\n{blog}\n\n"
            f"RESEARCH ARTIFACT:\n{research[:8000]}\n\n"
            f"Write the full SEO/AEO audit now."
        )
        res = self.router.complete("complex_planning", prompt,
                                   domain="content", step="judge")
        audit_text = res["text"].strip()
        audit_file = self.audit_path(signal_id)
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        audit_file.write_text(audit_text, encoding="utf-8")
        return audit_file


class Layer2FinalCorrector:
    """Apply SEO/AEO audit recommendations to the blog draft."""

    def __init__(self, router, workdir: str | Path):
        self.router = router
        self.workdir = Path(workdir)

    def run(self, signal_id: str) -> Path:
        blog_path = self.workdir / "drafts" / f"signal-{signal_id}-blog.md"
        blog = _read(blog_path)
        audit = _read(self.workdir / "reviews" /
                       f"{signal_id}-seo-aeo-audit.md")
        research = _read(self.workdir / "research" / f"signal-{signal_id}.md")
        prompt = (
            f"{_read_prompt('blog_writer.md')}\n\n"
            f"---\n\n"
            f"FINAL PASS: apply the SEO/AEO audit recommendations below to the "
            f"blog draft. Preserve Layer 2 editorial voice, facts, and the "
            f"mandatory disclosure. Do not introduce clickbait, urgency, or "
            f"advice framing.\n\n"
            f"RESEARCH ARTIFACT:\n{research[:6000]}\n\n"
            f"SEO/AEO AUDIT:\n{audit}\n\n"
            f"CURRENT BLOG DRAFT:\n{blog}\n\n"
            f"Output the final corrected blog draft."
        )
        res = self.router.complete("content_gen", prompt,
                                   domain="content", step="create")
        body = res["text"].strip()
        body = f"{_disclosure()}\n\n{body}"
        blog_path.write_text(body, encoding="utf-8")
        return blog_path


# --------------------------------------------------------------------------- #
# Publisher — move approved surfaces from drafts/ to final/
# --------------------------------------------------------------------------- #
class Layer2PublisherFull:
    """Copy approved surface drafts from drafts/ to final/."""

    def __init__(self, workdir: str | Path):
        self.workdir = Path(workdir)

    def publish(self, signal_id: str, surfaces: list[str]) -> list[Path]:
        final_dir = self.workdir / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        copied: list[Path] = []
        for surface in surfaces:
            src = (self.workdir / "drafts" /
                   f"signal-{signal_id}-{_SURFACE_FILE[surface]}")
            dst = final_dir / f"signal-{signal_id}-{_SURFACE_FILE[surface]}"
            if src.exists():
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                copied.append(dst)
        return copied


# --------------------------------------------------------------------------- #
# Convenience: write parallel surfaces
# --------------------------------------------------------------------------- #
def write_all_surfaces(writer: Layer2Writer, signal_id: str,
                       surfaces: list[str], mode: str = "promo",
                       max_workers: int = 4) -> list[Path]:
    """Create drafts for all selected surfaces in parallel."""

    def one(surface: str) -> Path:
        return writer.create(signal_id, surface, mode=mode)

    with ThreadPoolExecutor(max_workers=min(max_workers, len(surfaces))) as ex:
        return list(ex.map(one, surfaces))


# --------------------------------------------------------------------------- #
# Digest parser — read a digest and return candidate signals
# --------------------------------------------------------------------------- #
def parse_digest_candidates(digest_path: str | Path) -> list[SignalCandidate]:
    """Extract candidate signals from a digest file.

    Looks for headings that introduce topics/signals under the macro and
    real-time sections and returns SignalCandidate objects the runner can
    present to the operator.
    """
    text = _read(digest_path)
    candidates: list[SignalCandidate] = []

    # Split the digest into macro and realtime sections.
    lower = text.lower()
    macro_start = lower.find("## macro")
    realtime_start = lower.find("## real-time")
    if realtime_start == -1:
        realtime_start = lower.find("## realtime")

    sections: list[tuple[str, str]] = []
    if macro_start != -1:
        end = realtime_start if realtime_start != -1 and realtime_start > macro_start else len(text)
        sections.append(("macro", text[macro_start:end]))
    if realtime_start != -1:
        sections.append(("realtime", text[realtime_start:]))
    if not sections:
        sections.append(("realtime", text))

    # Match headings that introduce actual signals or editorial candidates.
    signal_re = re.compile(
        r"#{1,4}\s*(?:Signal\s*[:\-]?\s*|Primary Editorial Candidate\s*)"
        r"(.*?)\n(.*?)(?="
        r"\n#{1,4}\s*(?:Signal\s*[:\-]?\s*|Primary Editorial Candidate\s*)|\Z)",
        re.DOTALL | re.IGNORECASE,
    )

    for lens, section in sections:
        for m in signal_re.finditer(section):
            title_line = m.group(1).strip()
            block = m.group(2).strip()
            # Drop the numeric prefix if present ("1: Title" -> "Title").
            title = re.sub(r"^\d+\.?\s*[:\-]?\s*", "", title_line).strip()
            if not title or len(title) < 8:
                continue
            # Skip known section headers that leaked through.
            low = title.lower()
            if any(low.startswith(h) for h in (
                "primary", "secondary", "historical", "curated",
                "operator", "phase ", "development ", "context",
            )):
                continue
            sid = _safe_id(title)[:60]
            # Try to find a one-line 'why this matters now'.
            why = ""
            for line in block.splitlines():
                lowl = line.lower()
                if "why this matters" in lowl or "why it matters" in lowl or \
                   "matters now" in lowl:
                    why = line.split(":", 1)[-1].strip().strip("-* ")
                    break
            candidates.append(SignalCandidate(
                id=sid,
                title=title,
                lens=lens,
                why_now=why,
                raw_block=block,
            ))
    return candidates
