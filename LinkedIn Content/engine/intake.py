"""Ticket intake + weekly brief."""
import re
from datetime import date
from pathlib import Path

from . import ledger, lessons, llm

ROOT = Path(__file__).resolve().parent.parent
TICKETS = ROOT / "tickets"
PLANS = ROOT / "plans"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:48] or "untitled"


def create_ticket(topic: str, take: str, category: str = "auto", source: str = "manual") -> str:
    # the take is the founder's own position — the engine must never draft
    # from an assumed or empty one
    if not take or len(take.strip()) < 20:
        raise ValueError(
            "Refusing to create a ticket without a real founder take "
            "(min ~20 chars). The take is the founder's position — ask him first."
        )
    ticket_id = f"{date.today().isoformat()}-{_slugify(topic)}"
    path = TICKETS / f"{ticket_id}.md"
    n = 2
    while path.exists():
        path = TICKETS / f"{ticket_id}-{n}.md"
        n += 1
    ticket_id = path.stem
    TICKETS.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
id: {ticket_id}
created: {date.today().isoformat()}
source: {source}
category: {category}
status: open
---

# Topic
{topic}

# Take
{take}
""",
        encoding="utf-8",
    )
    ledger.log({"event": "ticket_created", "ticket": ticket_id,
                "source": source, "category": category})
    return ticket_id


def load_ticket(ticket_id: str) -> dict:
    path = TICKETS / f"{ticket_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Ticket not found: {path}")
    text = path.read_text(encoding="utf-8")
    meta = {}
    fm = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    body = text
    if fm:
        for line in fm.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = fm.group(2)
    topic_m = re.search(r"^# Topic\n(.*?)(?=^# |\Z)", body, re.MULTILINE | re.DOTALL)
    take_m = re.search(r"^# Take\n(.*?)(?=^# |\Z)", body, re.MULTILINE | re.DOTALL)
    return {
        "id": meta.get("id", ticket_id),
        "created": meta.get("created", ""),
        "source": meta.get("source", "manual"),
        "category": meta.get("category", "auto"),
        "status": meta.get("status", "open"),
        "topic": topic_m.group(1).strip() if topic_m else "",
        "take": take_m.group(1).strip() if take_m else "",
        "path": str(path),
    }


def save_ticket(ticket: dict) -> None:
    Path(ticket["path"]).write_text(
        f"""---
id: {ticket['id']}
created: {ticket['created']}
source: {ticket['source']}
category: {ticket['category']}
status: {ticket['status']}
---

# Topic
{ticket['topic']}

# Take
{ticket['take']}
""",
        encoding="utf-8",
    )


def _parse_plan(plan_path: Path) -> dict:
    text = plan_path.read_text(encoding="utf-8")
    week_m = re.search(r"^# Week of (\S+)", text, re.MULTILINE)
    slots = re.findall(r"^- category: ([\w-]+), count: (\d+)", text, re.MULTILINE)
    budget_m = re.search(r"^reactive_budget: (\d+)", text, re.MULTILINE)
    notes_m = re.search(r"^notes: (.*)$", text, re.MULTILINE)
    return {
        "week": week_m.group(1) if week_m else date.today().isoformat(),
        "slots": [{"category": c, "count": int(n)} for c, n in slots],
        "reactive_budget": int(budget_m.group(1)) if budget_m else 0,
        "notes": notes_m.group(1).strip() if notes_m else "",
    }


def weekly(plan_path: str) -> str:
    plan = _parse_plan(Path(plan_path))
    events = ledger.all()
    tickets = [load_ticket(p.stem) for p in sorted(TICKETS.glob("*.md"))]

    # slot status: count tickets per category as filled slots
    lines = [f"# Week Brief — week of {plan['week']}", ""]
    lines.append("## Planned slots")
    for slot in plan["slots"]:
        filled = [t for t in tickets if t["category"].replace("auto", "") == slot["category"]
                  or slot["category"] in t["category"]]
        status = f"{min(len(filled), slot['count'])}/{slot['count']} filled"
        lines.append(f"- {slot['category']}: {slot['count']} planned — {status}"
                     + (f" ({', '.join(t['id'] for t in filled)})" if filled else " (open)"))
    lines.append(f"- reactive budget: {plan['reactive_budget']}")
    if plan["notes"]:
        lines.append(f"- notes: {plan['notes']}")
    lines.append("")

    lines.append("## Recent outcomes")
    outcomes = [e for e in events if e.get("event") in ("approved", "pushback")][-20:]
    if outcomes:
        for e in outcomes:
            lines.append(f"- {e.get('ts', '')[:10]} {e['event']}: {e.get('ticket', '')}"
                         + (f" — {e.get('reason', '')}" if e.get("reason") else ""))
    else:
        lines.append("- none recorded yet")
    lines.append("")

    lines.append("## Active lessons")
    act = lessons.active()
    if act:
        lines += [f"- {t}" for t in act]
    else:
        lines.append("- none active")
    lines.append("")

    evidence = "\n".join(lines)
    note = llm.complete(
        "You are a concise content strategist. Given a week brief's raw evidence, "
        "write a short 'what the evidence suggests' note: 3-6 sentences, plain, "
        "no hype. If evidence is thin, say so and say what to watch.",
        evidence,
    )
    lines.append("## What the evidence suggests")
    lines.append(note)
    lines.append("")

    out = PLANS / f"{date.today().isoformat()}-week-brief.md"
    PLANS.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return str(out)
