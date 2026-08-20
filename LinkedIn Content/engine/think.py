"""Think/shape pass: analyze the take, then shape the post. One LLM call."""
import re
from pathlib import Path

from . import llm

ROOT = Path(__file__).resolve().parent.parent
VOICE = ROOT / "voice" / "ajit_voice_base.md"
CATEGORIES = ROOT / "categories"
TICKETS = ROOT / "tickets"

SYSTEM = (
    "You are the thinking pass of a LinkedIn writing engine. You analyze a "
    "founder's raw take and decide what the post is FOR before anyone writes "
    "a word. Be rigorous and specific; everything you produce steers the "
    "writer and the judge."
)


def think_path(ticket_id: str) -> Path:
    return TICKETS / f"{ticket_id}.think.md"


def research_path(ticket_id: str) -> Path:
    return TICKETS / f"{ticket_id}.research.md"


def field(note: str, name: str) -> str:
    """Extract a '- NAME: ...' field's text (may span following bullet lines)."""
    m = re.search(
        rf"^\s*- {re.escape(name)}:\s*(.*?)(?=^\s*- [A-Z][A-Z -]+:|^# |\Z)",
        note, re.MULTILINE | re.DOTALL,
    )
    return m.group(1).strip() if m else ""


def wants_research(note: str) -> bool:
    return field(note, "RESEARCH").lower().startswith("yes")


def research_questions(note: str) -> str:
    return field(note, "RESEARCH QUESTIONS")


def clarify_questions(note: str) -> str:
    """Non-empty when the think pass stopped to ask the founder questions."""
    return field(note, "CLARIFY")


def _cards_block() -> str:
    parts = []
    for p in sorted(CATEGORIES.glob("*.md")):
        parts.append(f"--- CARD: {p.stem} ---\n{p.read_text(encoding='utf-8').strip()}")
    return "\n\n".join(parts)


def analyze(ticket: dict) -> str:
    voice = VOICE.read_text(encoding="utf-8")
    user = f"""Analyze this founder's take and shape the post. Do NOT write the post.

=== VOICE FILE (who is speaking, audience map) ===
{voice}

=== CATEGORY CARDS (move libraries — ground your selection here) ===
{_cards_block()}

=== RAW MATERIAL ===
Topic: {ticket['topic']}
Founder's take (verbatim): {ticket['take']}

Produce EXACTLY these sections, in this order:

# THINK NOTE
- ARGUMENTS: list each distinct point/argument in the founder's take, numbered.
- PURPOSE: what the reader should walk away knowing/feeling/doing. One paragraph.
- LOAD-BEARING: which numbered arguments are essential vs supporting, and why.
- POST COUNT: one post, or split into two — with the reason.
- RESEARCH: yes|no — yes for news/current events/market topics where verified
  facts and reader-context matter; no for personal stories, lessons, or
  opinions grounded in the founder's own experience.
- RESEARCH QUESTIONS: (only when RESEARCH is yes) 2-5 specific questions the
  writer would need answered — including any references in the take a general
  reader wouldn't understand (events, comparisons, jargon) and any factual
  claims in the take worth verifying.

If the take is genuinely ambiguous or missing something essential, instead
output:
- CLARIFY: one or more questions for the founder — and then STOP. Do not
  produce a shape note in that case.

# SHAPE NOTE
- SHAPE TAG: a free-form shape label like "news-mechanics + opinion-verdict"
  or "personal-story". Hybrids are explicitly allowed — do NOT force the
  post into a single card.
- SELECTED MOVES: 2-4 moves/techniques drawn from the card file(s) most
  relevant to the shape tag. Each with a one-line reason tied to THIS take.
- STRUCTURE SKETCH: a 4-8 bullet outline of the post's flow.
- LENGTH PLAN: target word count sized to the argument count. The card's
  range is a prior, not a limit.
"""
    note = llm.complete(SYSTEM, user)
    TICKETS.mkdir(parents=True, exist_ok=True)
    think_path(ticket["id"]).write_text(note, encoding="utf-8")
    return note
