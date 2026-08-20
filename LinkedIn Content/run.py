#!/usr/bin/env python3
"""CLI for Ajit's LinkedIn post-writing engine."""
import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def _load_dotenv() -> None:
    """Read KEY=VALUE lines from .env at the project root (no deps)."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

from engine import classify, deai, elevate, intake, judge, ledger, lessons, research, think, write  # noqa: E402


def cmd_ticket(args):
    tid = intake.create_ticket(args.topic, args.take, category=args.category, source=args.source)
    print(f"Created ticket: {tid}")
    print(f"  {ROOT / 'tickets' / (tid + '.md')}")


def cmd_think(args):
    ticket = intake.load_ticket(args.ticket_id)
    note = think.analyze(ticket)
    print(f"Think note written: tickets/{ticket['id']}.think.md\n")
    print(note)


def _load_or_make_think_note(ticket: dict) -> str:
    """Reuse tickets/<id>.think.md if present, otherwise run the think pass."""
    tpath = think.think_path(ticket["id"])
    if tpath.exists():
        print(f"Using existing think note: tickets/{ticket['id']}.think.md")
        return tpath.read_text(encoding="utf-8")
    note = think.analyze(ticket)
    print(f"Think note written: tickets/{ticket['id']}.think.md")
    return note


def _check_clarify(ticket: dict, think_note: str) -> None:
    """Exit with guidance when the think pass asked the founder questions."""
    questions = think.clarify_questions(think_note)
    if questions:
        print("The think pass needs clarification before this post can be written:\n")
        print(questions)
        print("\nAnswer by editing the take in tickets/"
              f"{ticket['id']}.md (delete tickets/{ticket['id']}.think.md afterward), "
              "or re-run `ticket` with more detail.")
        sys.exit(1)


def cmd_research(args):
    ticket = intake.load_ticket(args.ticket_id)
    tpath = think.think_path(ticket["id"])
    if not tpath.exists():
        sys.exit(f"No think note for {ticket['id']} — run think or draft first.")
    result = research.research(ticket, tpath.read_text(encoding="utf-8"))
    if result is None:
        print("Think note says RESEARCH: no — nothing to do.")
    else:
        print(f"Research written: tickets/{ticket['id']}.research.md")


def cmd_deai(args):
    ticket = intake.load_ticket(args.ticket_id)
    tpath = think.think_path(ticket["id"])
    if not tpath.exists():
        sys.exit(f"No think note for {ticket['id']} — run think or draft first.")
    deai.deai(ticket, tpath.read_text(encoding="utf-8"))
    print(f"De-AI'd draft: drafts/{ticket['id']}.md")


def cmd_elevate(args):
    ticket = intake.load_ticket(args.ticket_id)
    tpath = think.think_path(ticket["id"])
    if not tpath.exists():
        sys.exit(f"No think note for {ticket['id']} — run think or draft first.")
    elevate.elevate(ticket, tpath.read_text(encoding="utf-8"))
    print(f"Elevated draft: drafts/{ticket['id']}.md")


def cmd_draft(args):
    ticket = intake.load_ticket(args.ticket_id)
    if ticket["category"] == "auto":
        slug, reasoning = classify.classify(ticket["topic"], ticket["take"])
        ticket["category"] = slug
        intake.save_ticket(ticket)
        print(f"Classified as: {slug}")
        print(f"  {reasoning}\n")
    think_note = _load_or_make_think_note(ticket)
    _check_clarify(ticket, think_note)
    if research.research(ticket, think_note) is not None:
        print(f"Research written: tickets/{ticket['id']}.research.md")
    draft = write.write_draft(ticket, think_note)
    if draft.strip().upper().startswith("NEEDS_INPUT:"):
        print(draft.strip())
        sys.exit(1)
    print(f"Draft written: drafts/{ticket['id']}.md")
    elevate.elevate(ticket, think_note)
    print(f"Draft elevated: drafts/{ticket['id']}.md")
    result = judge.judge(ticket, think_note)
    print(f"Judge: {result['status']} — review at {result['review']}")
    deai.deai(ticket, think_note)
    print(f"De-AI'd draft: drafts/{ticket['id']}.md")
    if result["status"] != "passed":
        sys.exit(1)


def cmd_review(args):
    path = ROOT / "reviews" / f"{args.ticket_id}.md"
    if not path.exists():
        sys.exit(f"No review found for {args.ticket_id}")
    print(path.read_text(encoding="utf-8"))


def cmd_approve(args):
    draft = ROOT / "drafts" / f"{args.ticket_id}.md"
    if not draft.exists():
        sys.exit(f"No draft for {args.ticket_id}")
    dest = ROOT / "final" / draft.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(draft, dest)
    try:
        ticket = intake.load_ticket(args.ticket_id)
        ticket["status"] = "approved"
        intake.save_ticket(ticket)
    except FileNotFoundError:
        pass
    ledger.log({"event": "approved", "ticket": args.ticket_id})
    print(f"Approved → final/{draft.name}")


def cmd_pushback(args):
    ticket = intake.load_ticket(args.ticket_id)
    category = ticket["category"] if ticket["category"] != "auto" else "all"
    lesson_id = lessons.add(args.reason, source="pushback", category=category)
    ticket["status"] = "pushed_back"
    intake.save_ticket(ticket)
    ledger.log({"event": "pushback", "ticket": args.ticket_id, "reason": args.reason})
    print(f"Pushback recorded; lesson candidate {lesson_id} (category: {category})")


def _print_lessons(items):
    if not items:
        print("(none)")
        return
    for l in items:
        print(f"[{l['id']}] ({l['status']}) {l['category']}/{l['stage']} — {l['text']}")


def cmd_lessons(args):
    _print_lessons(lessons.candidates() if args.candidates else lessons.all_lessons())


def cmd_lesson_activate(args):
    if lessons.activate(args.lesson_id):
        print(f"Activated {args.lesson_id}")
    else:
        sys.exit(f"Lesson not found: {args.lesson_id}")


def cmd_lesson_retire(args):
    if lessons.retire(args.lesson_id):
        print(f"Retired {args.lesson_id}")
    else:
        sys.exit(f"Lesson not found: {args.lesson_id}")


def cmd_week(args):
    out = intake.weekly(args.plan)
    print(f"Week brief written: {out}")


def cmd_scout(args):
    from engine import scout
    path = scout.run_scout()
    print(f"\nDigest written: {path}")


def cmd_setup(args):
    from engine import browser_setup
    browser_setup.run_setup()


def cmd_status(args):
    from engine import browser_setup
    result = browser_setup.check_ready()
    if result is True:
        print("READY — config.json present, CDP up, LinkedIn logged in.")
    else:
        print(f"NOT READY — {result}")
        sys.exit(1)


def cmd_add_source(args):
    import json
    import re
    from urllib.parse import urlparse

    from engine import scout

    url = args.url.strip()
    if not re.match(r"^https?://", url):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.netloc:
        sys.exit(f"Not a valid URL: {args.url}")
    name = re.sub(r"^www\.", "", parsed.netloc).split(".")[0]
    print(f"Test-scraping {url} (source name: {name}) ...")

    items = scout.scrape_source(url, name)
    if not items:
        print("\nNo items found — this site can't be scraped effectively with the "
              "generic extractor (it may be JS-heavy, blocked, or unusually marked up).")
        sys.exit(1)

    print(f"\nScraped {len(items)} items. First 10:\n")
    for i, it in enumerate(items[:10], 1):
        date = (it.get("published") or "")[:10] or "date unknown"
        title = it["title"] if len(it["title"]) <= 80 else it["title"][:77] + "..."
        print(f"{i:2}. [{date}] {title}")
        print(f"    {it['url']}")

    answer = input("\nDoes this look right? Add permanently? [y/n] ").strip().lower()
    if answer != "y":
        print("Discarded — source not added.")
        return
    cutoff_raw = input("Cutoff days (keep items newer than this) [14]: ").strip()
    cutoff = int(cutoff_raw) if cutoff_raw else 14

    sources_path = scout.SOURCES_JSON
    sources = scout.load_sources()
    if any(s["url"].rstrip("/") == url.rstrip("/") for s in sources):
        sys.exit("That URL is already in sources.json — not adding a duplicate.")
    sources.append({"name": name, "url": url, "cutoff_days": cutoff, "enabled": True})
    sources_path.parent.mkdir(parents=True, exist_ok=True)
    sources_path.write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")
    print(f"Added '{name}' (cutoff {cutoff}d) to {sources_path}")


def _first_run_gate(command: str) -> None:
    """On the very first run on a machine, walk the user through setup."""
    if command in ("setup", "status"):
        return
    marker = ROOT / ".setup-done"
    if marker.exists():
        return
    print("== First run — let's set you up ==")
    # 1. LLM backend
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        print("LLM backend: API key found ✓")
    elif shutil.which("kimi"):
        print("LLM backend: kimi CLI found ✓ (set ANTHROPIC_API_KEY/OPENAI_API_KEY in .env later for speed)")
    else:
        print("LLM backend: NONE found. Add ANTHROPIC_API_KEY or OPENAI_API_KEY to .env, or install the kimi CLI.")
    # 2. Browser / LinkedIn setup (needed by LinkedIn-touching agents)
    if not (ROOT / "config.json").exists():
        try:
            ans = input("\nRun browser + LinkedIn setup now? [Y/n] ").strip().lower()
        except EOFError:
            ans = "n"
        if ans in ("", "y", "yes"):
            from engine import browser_setup
            browser_setup.run_setup()
    marker.write_text("done\n")
    print("Setup complete. Run `python3 run.py status` anytime to re-check.\n")


def main():
    p = argparse.ArgumentParser(prog="run.py", description="Ajit's LinkedIn post-writing engine")
    sub = p.add_subparsers(dest="command", required=True)

    t = sub.add_parser("ticket", help="Create an intake ticket")
    t.add_argument("topic")
    t.add_argument("--take", required=True)
    t.add_argument("--category", default="auto")
    t.add_argument("--source", default="manual", choices=["manual", "planned", "reactive"])
    t.set_defaults(func=cmd_ticket)

    th = sub.add_parser("think", help="Run only the think/shape pass for a ticket")
    th.add_argument("ticket_id")
    th.set_defaults(func=cmd_think)

    d = sub.add_parser("draft", help="Classify (if auto), think, research, write, elevate, judge, de-AI")
    d.add_argument("ticket_id")
    d.set_defaults(func=cmd_draft)

    rs = sub.add_parser("research", help="Run only the research pass for a ticket")
    rs.add_argument("ticket_id")
    rs.set_defaults(func=cmd_research)

    da = sub.add_parser("deai", help="Run only the de-AI pass on an existing draft")
    da.add_argument("ticket_id")
    da.set_defaults(func=cmd_deai)

    el = sub.add_parser("elevate", help="Run only the editor pass on an existing draft")
    el.add_argument("ticket_id")
    el.set_defaults(func=cmd_elevate)

    r = sub.add_parser("review", help="Print the review for a ticket")
    r.add_argument("ticket_id")
    r.set_defaults(func=cmd_review)

    a = sub.add_parser("approve", help="Copy draft to final/ and log approval")
    a.add_argument("ticket_id")
    a.set_defaults(func=cmd_approve)

    pb = sub.add_parser("pushback", help="Record pushback; creates a lesson candidate")
    pb.add_argument("ticket_id")
    pb.add_argument("reason")
    pb.set_defaults(func=cmd_pushback)

    ls = sub.add_parser("lessons", help="List lessons")
    ls.add_argument("--candidates", action="store_true", help="Only candidates")
    ls.set_defaults(func=cmd_lessons)

    la = sub.add_parser("lesson-activate", help="Activate a lesson")
    la.add_argument("lesson_id")
    la.set_defaults(func=cmd_lesson_activate)

    lr = sub.add_parser("lesson-retire", help="Retire a lesson")
    lr.add_argument("lesson_id")
    lr.set_defaults(func=cmd_lesson_retire)

    w = sub.add_parser("week", help="Generate the weekly brief")
    w.add_argument("--plan", default=str(ROOT / "plans" / "plan.md"))
    w.set_defaults(func=cmd_week)

    sc = sub.add_parser("scout", help="Scrape news sources and write a ranked signal digest")
    sc.set_defaults(func=cmd_scout)

    ads = sub.add_parser("add-source", help="Test-scrape a URL and optionally add it as a source")
    ads.add_argument("url")
    ads.set_defaults(func=cmd_add_source)

    st = sub.add_parser("setup", help="First-run setup: detect browser, CDP, LinkedIn login")
    st.set_defaults(func=cmd_setup)

    ss = sub.add_parser("status", help="Check setup readiness (config, CDP, LinkedIn)")
    ss.set_defaults(func=cmd_status)

    args = p.parse_args()
    _first_run_gate(args.command)
    try:
        args.func(args)
    except RuntimeError as e:
        sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
