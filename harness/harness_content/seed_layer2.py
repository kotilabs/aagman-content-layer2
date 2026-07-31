"""seed_layer2.py — Day-0 seeding for the content harness.

Seeds AgentMemory namespaces with voice rules, research standards, reviewer
standards, and SEO/AEO standards so the harness starts with accumulated
content knowledge.
"""
from __future__ import annotations

from pathlib import Path

from harness_core.agent_memory import AgentMemory

_REPO = Path(__file__).resolve().parent.parent
_VOICE_DIR = _REPO / "harness_content" / "voice"


def _voice_lessons() -> list[tuple[str, str, str]]:
    """Return (domain, step, text) lessons distilled from voice guides."""
    lessons: list[tuple[str, str, str]] = []

    voice_base = _VOICE_DIR / "layer2_voice_base.md"
    if voice_base.exists():
        text = voice_base.read_text(encoding="utf-8")
        # Content rules (hard constraints)
        lessons.append(("content", "create",
                        "Never include buy/sell recommendations, price targets, "
                        "return promises, urgency words, or engagement bait."))
        lessons.append(("content", "create",
                        "Every surface must end with an open cognitive tension, "
                        "not a conclusion or call to action."))
        lessons.append(("content", "create",
                        "Every claim must be sourced; distinguish facts, "
                        "mechanisms, interpretations, and opinions."))
        lessons.append(("content", "create",
                        "Assume SEBI scrutiny and institutional readership; "
                        "write so context loss does not cause harm."))

    carousel = _VOICE_DIR / "carousel_overlay.md"
    if carousel.exists():
        lessons.append(("content", "create",
                        "Carousels lead with concrete data first, then abstract "
                        "mechanism."))

    thread = _VOICE_DIR / "thread_overlay.md"
    if thread.exists():
        lessons.append(("content", "create",
                        "Threads need a strong hook, body beats, pivot thesis, "
                        "and open end."))

    substack = _VOICE_DIR / "substack_overlay.md"
    if substack.exists():
        lessons.append(("content", "create",
                        "Substack essays use the canonical structure: Context, "
                        "Mechanism, Signal/Deviation, Interpretation Spectrum, "
                        "Historical Memory, Implications, Open Question."))

    return lessons


def _research_lessons() -> list[tuple[str, str, str]]:
    """Lessons for the research/ideate step."""
    return [
        ("content", "ideate",
         "Every checkable fact must include a source name, direct URL, and date. "
         "No URL, no inclusion."),
        ("content", "ideate",
         "Read the full source before citing; headlines and summaries are not enough."),
        ("content", "ideate",
         "Prefer primary sources: central banks, exchanges, regulators, "
         "government filings, official data."),
        ("content", "ideate",
         "Include historical analogues for perspective, never prediction; "
         "state the key similarity, key difference, and why it is useful."),
        ("content", "ideate",
         "Explicitly separate known, unknown, and unknowable in every research artifact."),
        ("content", "ideate",
         "If a key fact is disputed, present the dispute; do not force a resolution."),
    ]


def _reviewer_lessons() -> list[tuple[str, str, str]]:
    """Lessons for the judge step from markets reviewer standards."""
    return [
        ("content", "judge",
         "Blockers: factual error, misleading compression, cross-surface "
         "contradiction, or unsupported advice framing."),
        ("content", "judge",
         "Check cross-surface consistency: all outputs from one signal must "
         "claim the same thing about the world."),
        ("content", "judge",
         "Blog: highest nuance standard; every strong claim needs support."),
        ("content", "judge",
         "Carousel: compression-distortion lens; slides must not collapse "
         "nuanced claims into misleading statements."),
        ("content", "judge",
         "Thread: every post must survive being quoted out of context."),
        ("content", "judge",
         "Infographic: every visualized number must trace to a source."),
        ("content", "judge",
         "SEO/AEO audit: every blog needs a clear keyword, answer target, "
         "and internal link opportunity."),
    ]


def seed_all(db_path: str | Path | None = None) -> dict[str, int]:
    """Seed all content namespaces and return counts."""
    counts: dict[str, int] = {}

    def seed_group(domain: str, step: str, lessons: list[str]):
        mem = AgentMemory(domain, step, db_path=db_path)
        n = 0
        for text in lessons:
            if text.strip():
                mem.add(text.strip())
                n += 1
        counts[f"{domain}/{step}"] = n

    voice = _voice_lessons()
    research = _research_lessons()
    reviewer = _reviewer_lessons()

    seed_group("content", "ideate",
               [t for _, s, t in research if s == "ideate"])
    seed_group("content", "create",
               [t for _, s, t in voice if s == "create"])
    seed_group("content", "judge",
               [t for _, s, t in reviewer if s == "judge"])

    return counts


if __name__ == "__main__":
    for ns, n in seed_all().items():
        print(f"seeded {ns}: {n} lessons")
