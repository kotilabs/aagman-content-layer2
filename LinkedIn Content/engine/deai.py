"""De-AI pass: strip AI writing patterns from a judged draft. Final pipeline stage."""
from pathlib import Path

from . import ledger, llm

ROOT = Path(__file__).resolve().parent.parent
VOICE = ROOT / "voice" / "ajit_voice_base.md"
DRAFTS = ROOT / "drafts"

SYSTEM = (
    "You are a prose editor who removes AI writing patterns from a finished "
    "draft while preserving the author's voice, the facts, and the story's "
    "flow. You change wording and rhythm, never substance."
)

RULES = """De-AI rules to enforce:
- Binary contrasts ("Sounded smart. It wasn't.", "not X, it's Y") — state
  the thing directly.
- Dramatic fragment machine-gunning (3+ consecutive one-line dramatic
  fragments) — merge into varied rhythm; some short lines are fine,
  monotony is not.
- Pull-quote lines (a sentence styled as a standalone quotable) — fold
  into the prose or cut.
- Meta-narration ("The real punchline came...", "Here's the thing...") —
  just say the thing.
- Throat-clearing openers and emphasis crutches — cut.
- Adverbs doing vague work — cut.
- Em dashes — rewrite with commas or restructure.
- Passive voice — make the human the subject.
- Vague declaratives ("The implications are significant") — name the
  specific thing.
- Every paragraph ending on a punchy one-liner — vary the endings.

Hard constraints:
- Preserve every factual claim exactly: numbers, dates, and names must
  not change.
- Preserve the author's voice per the voice file — his dry wit, lexicon,
  and candor stay.
- LAYOUT IS OFF-LIMITS: do not merge, split, or reflow lines. Deliberate
  one-line beats are the LinkedIn format, not "dramatic fragments" — only
  merge a fragment sequence when 4+ consecutive fragments are doing the
  same rhetorical job, and never create a paragraph of 4+ sentences.
  Change wording within lines, never the line structure.
- A genuinely earned closing aphorism may stay; a decorative one may not."""


def deai(ticket: dict, think_note: str) -> str:
    draft_path = DRAFTS / f"{ticket['id']}.md"
    if not draft_path.exists():
        raise FileNotFoundError(f"No draft for {ticket['id']} — run draft first.")
    draft = draft_path.read_text(encoding="utf-8")
    voice = VOICE.read_text(encoding="utf-8")

    user = f"""Remove AI writing patterns from this LinkedIn draft.

=== VOICE FILE (the author's voice — preserve it) ===
{voice}

=== {RULES}

=== DRAFT ===
{draft}

Output ONLY the rewritten post text."""

    cleaned = llm.complete(SYSTEM, user)
    draft_path.write_text(cleaned, encoding="utf-8")
    ledger.log({"event": "deai", "ticket": ticket["id"]})
    return cleaned
