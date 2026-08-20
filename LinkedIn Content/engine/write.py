"""Draft writer: free write from voice + think note + take + active lessons."""
import re
from pathlib import Path

from . import ledger, lessons, llm, think

ROOT = Path(__file__).resolve().parent.parent
VOICE = ROOT / "voice" / "ajit_voice_base.md"
DRAFTS = ROOT / "drafts"

SYSTEM = (
    "You are a ghostwriter producing a LinkedIn post for a founder. "
    "Follow the brief exactly. Output ONLY the post text — no preamble, "
    "no commentary, no markdown headers. The only allowed trailing lines "
    "are CUT: notes, or a NEEDS_INPUT: line instead of a post."
)


def _think_only(think_note: str) -> str:
    """The THINK NOTE section without the SHAPE NOTE (shaping is the editor's job)."""
    return re.split(r"^# SHAPE NOTE", think_note, flags=re.MULTILINE)[0].strip()


def _build_prompt(ticket: dict, think_note: str, blockers: list[str] = None) -> str:
    voice = VOICE.read_text(encoding="utf-8")
    active = lessons.active(ticket["category"])
    lesson_block = "\n".join(f"- {t}" for t in active) if active else "- (none active)"

    rpath = think.research_path(ticket["id"])
    research_block = ""
    if rpath.exists():
        research_block = f"""
=== RESEARCH (verified facts — may be used; UNVERIFIED items must not be stated as fact) ===
{rpath.read_text(encoding='utf-8')}
"""

    prompt = f"""Write a LinkedIn post for this founder.

=== VOICE FILE (governs TONE of every sentence) ===
{voice}

=== THINK NOTE (the post's arguments, purpose, load-bearing points, post count) ===
{_think_only(think_note)}

=== RAW MATERIAL ===
Topic: {ticket['topic']}
Founder's take (verbatim raw material): {ticket['take']}
{research_block}
=== ACTIVE LESSONS (must be applied) ===
{lesson_block}

=== RULES (in priority order) ===
1. The ban list in the voice file overrides EVERYTHING. Never violate it.
2. The post may use the founder's take and the RESEARCH block ONLY — nothing
   else. NEVER invent biographical facts, dates, years, incidents, numbers,
   or anecdotes that appear in neither. Facts marked UNVERIFIED in the
   research must not be stated as fact. Do not fabricate a scar.
3. Every LOAD-BEARING argument from the think note must survive in the
   draft. If one genuinely cannot be made to work, cut it explicitly:
   end the draft with "CUT: <point> — <reason>".
4. Write the truest, clearest version of the argument in his voice.
   Natural flow over any imposed structure — do not force a skeleton.
5. Apply every active lesson that is relevant to this post.

=== IF MATERIAL IS INSUFFICIENT ===
If the take genuinely lacks the material the post needs, do NOT fill the
gap by inventing facts. Instead output a line starting with
"NEEDS_INPUT:" followed by the specific question for the founder, then
stop.
"""
    if blockers:
        bl = "\n".join(f"- {b}" for b in blockers)
        prompt += f"""
=== REVISION MODE ===
The previous draft was blocked on the following issues. Rewrite the post
to fix ONLY these blockers; keep everything else that already worked:
{bl}
"""
    return prompt


def _write(ticket: dict, prompt: str, revision: bool) -> str:
    draft = llm.complete(SYSTEM, prompt)
    if draft.strip().upper().startswith("NEEDS_INPUT:"):
        ledger.log({"event": "needs_input", "ticket": ticket["id"],
                    "question": draft.strip()})
        return draft  # surfaced to the human; not saved as a draft
    DRAFTS.mkdir(parents=True, exist_ok=True)
    (DRAFTS / f"{ticket['id']}.md").write_text(draft, encoding="utf-8")
    event = {"event": "draft_written", "ticket": ticket["id"],
             "category": ticket["category"]}
    if revision:
        event["revision"] = True
    ledger.log(event)
    return draft


def write_draft(ticket: dict, think_note: str) -> str:
    return _write(ticket, _build_prompt(ticket, think_note), revision=False)


def revise_draft(ticket: dict, think_note: str, blockers: list[str]) -> str:
    return _write(ticket, _build_prompt(ticket, think_note, blockers=blockers),
                  revision=True)
