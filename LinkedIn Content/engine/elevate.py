"""Elevate pass: a world-class editor improves the draft's craft, not its substance."""
import re
from pathlib import Path

from . import evidence, ledger, llm, think

ROOT = Path(__file__).resolve().parent.parent
VOICE = ROOT / "voice" / "ajit_voice_base.md"
DRAFTS = ROOT / "drafts"
EXEMPLARS = ROOT / "performance" / "exemplars"

SYSTEM = (
    "You are a world-class LinkedIn editor. You improve the craft of an "
    "existing draft without changing its substance. Output ONLY the improved "
    "post text — no commentary, no tracked changes, no explanation."
)

STOPWORDS = {"and", "or", "the", "of", "in", "to", "a", "an", "others"}


def _tokens(text: str) -> set:
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if t} - STOPWORDS


def _find_exemplar(ticket: dict, think_note: str) -> str:
    """Exemplar text for the post's category, or '' if none matches.

    Try the ticket's category slug first (strip the numeric prefix), then a
    token-overlap match on the shape tag. Exact normalized match wins; fuzzy
    requires at least half the exemplar's tokens to be present.
    """
    if not EXEMPLARS.exists():
        return ""
    files = {p.stem: p for p in sorted(EXEMPLARS.glob("*.md"))}

    def lookup(text: str) -> str:
        norm = re.sub(r"[^a-z0-9]", "", text.lower())
        for stem in files:
            if norm == re.sub(r"[^a-z0-9]", "", stem.lower()):
                return stem
        toks = _tokens(text)
        best, best_score = None, 0.0
        for stem in files:
            stoks = _tokens(stem)
            if not stoks:
                continue
            score = len(toks & stoks) / len(stoks)
            if score > best_score:
                best, best_score = stem, score
        return best if best_score >= 0.5 else ""

    category = ticket.get("category", "")
    stem = lookup(re.sub(r"^\d+-", "", category)) if category and category != "auto" else ""
    if not stem:
        m = re.search(r"SHAPE TAG:\s*(.+)", think_note)
        if m:
            stem = lookup(m.group(1))
    if not stem:
        return ""
    return files[stem].read_text(encoding="utf-8")


def elevate(ticket: dict, think_note: str) -> str:
    draft_path = DRAFTS / f"{ticket['id']}.md"
    if not draft_path.exists():
        raise FileNotFoundError(f"No draft for {ticket['id']} — run draft first.")
    draft = draft_path.read_text(encoding="utf-8")

    voice = VOICE.read_text(encoding="utf-8")
    exemplar = _find_exemplar(ticket, think_note)
    exemplar_block = (
        f"""
=== EXEMPLAR TOP POSTS (study for FLOW ONLY — never reuse their content, phrases, or structure verbatim) ===
{exemplar}
"""
        if exemplar else ""
    )
    ev = evidence.evidence_for(think_note)
    evidence_block = (
        f"""
=== PERFORMANCE EVIDENCE (apply only where it improves THIS draft; ignore the rest) ===
{ev}
"""
        if ev else ""
    )
    rpath = think.research_path(ticket["id"])
    research_block = ""
    if rpath.exists():
        research_block = f"""
=== RESEARCH (verified facts — may be used; UNVERIFIED items must not be stated as fact) ===
{rpath.read_text(encoding='utf-8')}
"""

    user = f"""Elevate this LinkedIn draft. Improve rhythm, pacing, opening
strength, the close, transitions, and line breaks. Change the craft, never
the substance:
- Every factual claim must remain traceable to the founder's take or the
  RESEARCH block — do not add facts, numbers, dates, or anecdotes from
  anywhere else. Facts marked UNVERIFIED must not be stated as fact.
- Preserve every load-bearing argument from the think note.
- Keep the voice: every sentence must still sound like the voice file.

=== VOICE FILE ===
{voice}

=== THINK NOTE + SHAPE NOTE (the shape tag is yours to use) ===
{think_note}
{exemplar_block}{evidence_block}{research_block}
=== FOUNDER'S TAKE (ground truth) ===
{ticket['take']}

=== CURRENT DRAFT ===
{draft}

Output ONLY the improved post text."""

    elevated = llm.complete(SYSTEM, user)
    draft_path.write_text(elevated, encoding="utf-8")
    ledger.log({"event": "elevated", "ticket": ticket["id"],
                "exemplar_used": bool(exemplar), "evidence_used": bool(ev)})
    return elevated
