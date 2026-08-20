"""Judge: sequential review lenses over a draft, with a revise loop."""
import re
from pathlib import Path

from . import evidence, ledger, llm, think, write

ROOT = Path(__file__).resolve().parent.parent
VOICE = ROOT / "voice" / "ajit_voice_base.md"
DRAFTS = ROOT / "drafts"
REVIEWS = ROOT / "reviews"

MAX_LOOPS = 2  # max revise loops; the final pass is a verification, not a revision

PERFORMANCE_INSTRUCTION = (
    "Score the draft against the evidence file's STRONG findings. Report a "
    "short scorecard. Treat evidence as advisory EXCEPT these blocking "
    "anti-patterns, which are always blockers: (a) the post opens with a "
    "question, (b) a hashtag block/wall, (c) paragraphs of 4+ sentences "
    "(wall of text), (d) explicit engagement-bait CTA (\"comment X\", "
    "\"what do you think?\"). For non-blocking deltas vs the evidence, emit "
    "them as NOTE: lines — one per observation — instead of BLOCKERS: lines."
)

# (name, instruction, inject_evidence)
LENSES = [
    ("voice_fidelity", "Does every sentence sound like the voice file defines? "
     "Flag any line that breaks persona, tone, or audience fit.", False),
    ("ban_list", "Does the post violate anything in the voice file's ban list? "
     "Flag every banned pattern found.", False),
    ("coverage", "Given the think note's ARGUMENTS and LOAD-BEARING lists: flag "
     "any load-bearing argument that is missing from the draft, distorted, or so "
     "compressed it lost its meaning. Also flag any factual claim in the draft "
     "that is traceable to NEITHER the founder's take NOR the research file "
     "(when one is present), and any research fact marked UNVERIFIED that the "
     "draft states as fact.", False),
    ("clarity", "Would the target reader (per the voice file's audience map) be "
     "able to state the post's main point after one read? Flag muddy, buried, "
     "or confusing parts.", False),
    ("performance", PERFORMANCE_INSTRUCTION, True),
    ("pull", "Does the first line earn a scroll-stop? Does the close land? "
     "Flag weak opens and weak closes.", False),
]

JUDGE_SYSTEM = (
    "You are a strict reviewer for a LinkedIn writing engine. You check one "
    "lens at a time. Reply PASS if the draft passes the lens, otherwise reply "
    "BLOCKERS: followed by one line per concrete problem. Be specific — quote "
    "the offending text. Do not invent issues; PASS is the default when in doubt."
)


def _run_lens(lens_name: str, instruction: str, use_evidence: bool,
              ticket: dict, think_note: str, draft: str) -> tuple[list[str], list[str]]:
    """Returns (blockers, notes)."""
    voice = VOICE.read_text(encoding="utf-8")
    evidence_block = ""
    if use_evidence:
        ev = evidence.evidence_for(think_note)
        if ev:
            evidence_block = f"""
=== PERFORMANCE EVIDENCE (550 analyzed posts) ===
{ev}
"""
    research_block = ""
    rpath = think.research_path(ticket["id"])
    if rpath.exists():
        research_block = f"""
=== RESEARCH (verified facts for this post) ===
{rpath.read_text(encoding='utf-8')}
"""
    user = f"""Lens: {lens_name}
{instruction}

=== VOICE FILE ===
{voice}

=== THINK NOTE + SHAPE NOTE ===
{think_note}
{evidence_block}{research_block}
=== FOUNDER'S TAKE (raw material) ===
{ticket['take']}

=== DRAFT ===
{draft}

Reply PASS, or BLOCKERS: with one line per problem."""
    resp = llm.complete(JUDGE_SYSTEM, user).strip()
    if resp.upper().startswith("PASS"):
        return [], []
    blockers, notes = [], []
    current = None
    for raw in resp.splitlines():
        line = raw.strip().lstrip("- ").strip()
        if not line:
            continue
        m = re.match(r"(?i)^(BLOCKERS|NOTE)\s*:\s*(.*)$", line)
        if m:
            current = m.group(1).upper()
            rest = m.group(2).strip()
            if rest:
                (blockers if current == "BLOCKERS" else notes).append(rest)
        elif current == "NOTE":
            notes.append(line)
        else:
            blockers.append(line)
    return ([f"[{lens_name}] {b}" for b in blockers],
            [f"[{lens_name}] {n}" for n in notes])


def judge(ticket: dict, think_note: str) -> dict:
    """Run the lens loop. Returns {'status': 'passed'|'needs_human', 'review': path}."""
    draft_path = DRAFTS / f"{ticket['id']}.md"
    if not draft_path.exists():
        raise FileNotFoundError(f"No draft for {ticket['id']} — run draft first.")

    history = []
    status = "passed"
    for loop in range(MAX_LOOPS + 1):
        draft = draft_path.read_text(encoding="utf-8")
        blockers = []
        for name, instruction, use_evidence in LENSES:
            found, notes = _run_lens(name, instruction, use_evidence,
                                     ticket, think_note, draft)
            blockers.extend(found)
            history.append({"loop": loop + 1, "lens": name,
                            "result": "PASS" if not found else f"{len(found)} blockers",
                            "blockers": found, "notes": notes})
            ledger.log({"event": "judged", "ticket": ticket["id"],
                        "lens": name, "loop": loop + 1,
                        "passed": not found, "notes": len(notes)})
        if not blockers:
            status = "passed"
            break
        if loop == MAX_LOOPS:
            status = "needs_human"
            break
        write.revise_draft(ticket, think_note, blockers)
        if not draft_path.exists():
            # writer returned NEEDS_INPUT instead of a draft — human must step in
            status = "needs_human"
            history.append({"loop": loop + 1, "lens": "writer",
                            "result": "NEEDS_INPUT", "blockers": [], "notes": []})
            break

    lines = [f"# Review — {ticket['id']}", f"Status: {status}", ""]
    for h in history:
        lines.append(f"## Loop {h['loop']} — {h['lens']}: {h['result']}")
        for b in h["blockers"]:
            lines.append(f"- {b}")
        if h["notes"]:
            lines.append("")
            lines.append("Notes:")
            for n in h["notes"]:
                lines.append(f"- {n}")
        lines.append("")
    if status == "needs_human":
        lines.append("Max revise loops reached. Leaving for human review.")

    REVIEWS.mkdir(parents=True, exist_ok=True)
    review_path = REVIEWS / f"{ticket['id']}.md"
    review_path.write_text("\n".join(lines), encoding="utf-8")
    return {"status": status, "review": str(review_path)}
