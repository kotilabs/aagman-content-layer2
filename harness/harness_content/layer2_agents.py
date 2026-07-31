"""layer2_agents.py — content agents wired into the aagman-harness loop.

These agents read prompts from harness_content/prompts/ and voice guides from
harness_content/voice/, then call the harness router (which routes to the Kimi
Code bridge). They also recall namespaced lessons and stamp provenance so the
harness can score them.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from harness_core.agent_base import (
    Artifact, Idea, Receipt, Signal, Verdict,
    SenseAgent, IdeateAgent, CreateAgent, JudgeAgent, PublishAgent, LearnAgent,
)
from harness_core.judgment_panel import JudgmentPanel

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


def _recall(memory_factory, domain: str, step: str, query: str, k: int = 5):
    """Return (lesson_texts, provenance_entries)."""
    if not memory_factory:
        return [], []
    mem = memory_factory(domain, step)
    texts, relied = [], []
    for lid in mem.top_k(query, k=k):
        les = mem.get(lid)
        if les and les.text:
            texts.append(les.text)
            relied.append([domain, step, lid])
    return texts, relied


def _disclosure() -> str:
    return (f"Educational content from {RIA_NAME} (SEBI RIA {RIA_REG}). "
            f"Not investment advice — no buy/sell recommendation.")


# --------------------------------------------------------------------------- #
# SENSE — read a signal from the content-layer2 digest or from an inbox file
# --------------------------------------------------------------------------- #
class Layer2SignalReader(SenseAgent):
    def __init__(self, inbox_dir: str | Path, digest_path: str | Path | None = None):
        self.inbox_dir = Path(inbox_dir)
        self.digest_path = Path(digest_path) if digest_path else None

    def sense(self, sources=None) -> list:
        signals = []
        # First, read any inbox files.
        dirs = [Path(s) for s in sources] if sources else [self.inbox_dir]
        for d in dirs:
            if not d.exists():
                continue
            for f in sorted(d.iterdir()):
                if f.suffix.lower() in (".md", ".txt", ".json"):
                    payload = self._payload(f)
                    signals.append(Signal(
                        id=f"layer2:{f.stem}",
                        domain="content",
                        source="inbox",
                        payload=payload,
                    ))
        # If no inbox signals and a digest is configured, parse it.
        if not signals and self.digest_path and self.digest_path.exists():
            sig = self._parse_digest()
            if sig:
                signals.append(sig)
        return signals

    @staticmethod
    def _payload(f: Path) -> dict:
        raw = f.read_text(encoding="utf-8")
        if f.suffix.lower() == ".json":
            try:
                obj = json.loads(raw)
                if isinstance(obj, dict):
                    obj.setdefault("brief", obj.get("brief", ""))
                    return obj
            except ValueError:
                pass
        return {"brief": raw.strip(), "file": f.name}

    def _parse_digest(self) -> Signal | None:
        text = self.digest_path.read_text(encoding="utf-8")
        # Find the first signal heading like "### Signal: ..." or "- **Signal** ...".
        m = re.search(r"#{1,4}\s*Signal[^\n]*\n(.*?)(?=\n#{1,4}\s*Signal|\Z)",
                      text, re.DOTALL | re.IGNORECASE)
        if not m:
            # Fallback: take first paragraph that looks like a signal.
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and len(line) > 40:
                    return Signal(
                        id="layer2:digest-first",
                        domain="content",
                        source=str(self.digest_path),
                        payload={"brief": line, "surfaces": ["blog", "thread"]},
                    )
            return None
        block = m.group(1).strip()
        title_line = m.group(0).splitlines()[0]
        title = re.sub(r"^#+\s*Signal[:\-]?\s*", "", title_line, flags=re.I).strip()
        return Signal(
            id=f"layer2:{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')}"[:60],
            domain="content",
            source=str(self.digest_path),
            payload={"brief": f"{title}\n\n{block}", "surfaces": ["blog", "thread"]},
        )


# --------------------------------------------------------------------------- #
# IDEATE — produce the canonical research artifact
# --------------------------------------------------------------------------- #
class Layer2ResearchAgent(IdeateAgent):
    def __init__(self, router, memory_factory, workdir: str | Path):
        self.router = router
        self.memory_factory = memory_factory
        self.workdir = Path(workdir)

    def ideate(self, signal) -> Idea:
        brief = signal.payload.get("brief", "")
        lessons, relied = _recall(self.memory_factory, "content", "ideate", brief)
        lessons_block = ""
        if lessons:
            lessons_block = "LESSONS FROM PAST RESEARCH:\n" + "\n".join(
                f"- {t}" for t in lessons) + "\n\n"
        prompt = (
            f"{_read_prompt('research_agent.md')}\n\n"
            f"---\n\n"
            f"SELECTED SIGNAL:\n{brief}\n\n"
            f"{lessons_block}"
            "Write the full research artifact now."
        )
        res = self.router.complete("complex_planning", prompt,
                                   domain="content", step="ideate")
        artifact_text = res["text"].strip()

        # Persist the research artifact so downstream agents can read it.
        research_dir = self.workdir / "research"
        research_dir.mkdir(parents=True, exist_ok=True)
        safe_id = re.sub(r"[^a-z0-9_-]+", "-", signal.id).strip("-")
        research_file = research_dir / f"signal-{safe_id}.md"
        research_file.write_text(artifact_text, encoding="utf-8")

        return Idea(
            summary=artifact_text[:500],
            plan={
                "brief": brief,
                "research_file": str(research_file),
                "surfaces": signal.payload.get("surfaces", ["blog", "thread"]),
            },
            confidence=0.85,
            meta={"model": res.get("model", ""), "relied": relied},
        )


# --------------------------------------------------------------------------- #
# CREATE — fan-out writer for blog, thread, carousel, infographic
# --------------------------------------------------------------------------- #
class Layer2ContentCreator(CreateAgent):
    def __init__(self, router, memory_factory):
        self.router = router
        self.memory_factory = memory_factory

    def create(self, idea) -> Artifact:
        modality = idea.meta.get("fan_out", "blog")
        surface = str(modality)
        prompt_file = _SURFACES.get(surface, "blog_writer.md")
        label = _SURFACE_LABELS.get(surface, surface)
        brief = idea.plan.get("brief", "")
        research_file = idea.plan.get("research_file", "")
        research = _read(research_file) if research_file else ""

        lessons, relied = _recall(self.memory_factory, "content", "create",
                                  f"{surface} {brief}")

        voice_parts = [
            _read_voice("layer2_voice_base.md"),
        ]
        if "carousel" in surface:
            voice_parts.append(_read_voice("carousel_overlay.md"))
        elif surface == "thread":
            voice_parts.append(_read_voice("thread_overlay.md"))
        elif surface == "blog":
            voice_parts.append(_read_voice("substack_overlay.md"))
        voice_block = "\n\n".join(voice_parts)

        lessons_block = ""
        if lessons:
            lessons_block = "LESSONS FROM PAST CREATION:\n" + "\n".join(
                f"- {t}" for t in lessons) + "\n\n"

        prompt = (
            f"{_read_prompt(prompt_file)}\n\n"
            f"---\n\n"
            f"BRAND VOICE:\n{voice_block}\n\n"
            f"SURFACE: {label}\n\n"
            f"RESEARCH ARTIFACT:\n{research[:6000]}\n\n"
            f"{lessons_block}"
            f"Write the {label} now."
        )
        res = self.router.complete("content_gen", prompt,
                                   domain="content", step="create")
        body = res["text"].strip()
        if surface in ("blog", "thread", "carousel_linkedin", "carousel_instagram"):
            body = f"{_disclosure()}\n\n{body}"

        return Artifact(
            body=body,
            kind=surface,
            meta={
                "surface": surface,
                "label": label,
                "model": res.get("model", ""),
                "relied": relied,
            },
        )

    def revise(self, artifact, issues) -> Artifact:
        surface = artifact.meta.get("surface", "blog")
        label = artifact.meta.get("label", surface)
        prompt = (
            f"You are revising a {label} for Aagman Layer 2.\n\n"
            f"ISSUES TO FIX:\n" + "\n".join(f"- {i}" for i in issues) + "\n\n"
            f"CURRENT DRAFT:\n{artifact.body}\n\n"
            f"Rewrite the full {label} with the issues fixed. Preserve the "
            f"educational-only framing, brand voice, and mandatory disclosure."
        )
        res = self.router.complete("content_gen", prompt,
                                   domain="content", step="create")
        body = res["text"].strip()
        if surface in ("blog", "thread", "carousel_linkedin", "carousel_instagram"):
            body = f"{_disclosure()}\n\n{body}"
        return Artifact(
            body=body,
            kind=artifact.kind,
            meta={**artifact.meta, "revised": True},
        )


# --------------------------------------------------------------------------- #
# JUDGE — markets reviewer across all surfaces
# --------------------------------------------------------------------------- #
class Layer2MarketsReviewer(JudgeAgent):
    def __init__(self, router, threshold: float = 0.66):
        self.panel = JudgmentPanel(router, "judge_panel", threshold=threshold)

    def judge(self, artifact, memory_factory=None) -> Verdict:
        lessons, relied = _recall(memory_factory, "content", "judge", artifact.body)
        research = ""
        # Try to find the research file from the artifact context if available.
        # The artifact body may be a concatenation of surfaces; we cannot recover
        # the research file here, so the prompt instructs the reviewer to judge
        # based on the surfaces alone and flag missing research context.
        lessons_block = ""
        if lessons:
            lessons_block = "\n\nLESSONS FROM PAST REVIEWS:\n" + "\n".join(
                f"- {t}" for t in lessons)
        criteria = (
            f"{_read_prompt('markets_reviewer.md')}\n\n"
            "You are reviewing ALL produced surfaces from one signal. "
            "Evaluate factual integrity, reasoning quality, cross-surface "
            "consistency, and format-specific severity. Reply 'pass' only if "
            "there are no blockers."
            f"{lessons_block}"
        )
        v = self.panel.decide(criteria, artifact.body)
        v.meta = {**(v.meta or {}), "relied": relied}
        return v


# --------------------------------------------------------------------------- #
# PUBLISH — write each surface to its own file in outbox/
# --------------------------------------------------------------------------- #
class Layer2Publisher(PublishAgent):
    def __init__(self, outbox_dir: str | Path):
        self.outbox_dir = Path(outbox_dir)

    def publish(self, artifact, channels) -> Receipt:
        d = self.outbox_dir / artifact.meta.get("surface", "outbox")
        d.mkdir(parents=True, exist_ok=True)
        name = artifact.meta.get("surface", "artifact")
        path = d / f"{name}.md"
        meta = {
            "kind": artifact.kind,
            **artifact.meta,
        }
        path.write_text(
            f"---\n{json.dumps(meta, indent=2)}\n---\n\n{artifact.body}\n",
            encoding="utf-8",
        )
        return Receipt(channel=artifact.meta.get("surface", "outbox"),
                       ref=str(path), meta=meta)


# --------------------------------------------------------------------------- #
# LEARN — record outcomes into content memory
# --------------------------------------------------------------------------- #
class Layer2Memory(LearnAgent):
    def __init__(self, memory_factory):
        self.memory_factory = memory_factory

    def record(self, signal, idea, artifact, outcome) -> None:
        if not self.memory_factory:
            return
        brief = signal.payload.get("brief", "")[:120] if signal else ""
        surfaces = []
        if artifact and artifact.meta:
            surfaces.append(artifact.meta.get("surface", "unknown"))
        # Record a generic outcome lesson.
        self.memory_factory("content", "create").add(
            f"outcome={outcome} | surfaces={','.join(surfaces)} | brief={brief}",
            tags=str(outcome))
