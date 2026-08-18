"""run_signal.py — drive one selected signal through research -> write -> review -> correct.

Bypasses the runner's single-signal state file so multiple signals can run
concurrently. LLM calls go through the Kimi Code bridge: this script blocks
(polls) until a response file appears in gates/llm_responses/ for each request
written to gates/llm_requests/. The operator (or an agent) fulfills requests.

Usage:
    python3 run_signal.py --ticket <ticket.md> --surfaces blog,infographic \
        [--carousel-mode standalone|promo] [--skip-review]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from harness_core.run import load_env
from run_layer2_full import build_services, ensure_workdir, WORKDIR_NAME
from harness_content.layer2_full_agents import (
    Layer2MarketsReviewerFull,
    Layer2ResearchAgentFull,
    Layer2Writer,
)


def main() -> int:
    ap = argparse.ArgumentParser("run_signal.py")
    ap.add_argument("--ticket", required=True)
    ap.add_argument("--surfaces", required=True, help="comma-separated")
    ap.add_argument("--carousel-mode", default="standalone",
                    choices=["standalone", "promo"])
    ap.add_argument("--skip-review", action="store_true")
    args = ap.parse_args()

    workdir = REPO / WORKDIR_NAME
    ensure_workdir(workdir)
    env = load_env(str(REPO / ".env")) if (REPO / ".env").exists() else {}
    services = build_services(workdir, env)

    researcher = Layer2ResearchAgentFull(services.router, workdir,
                                         services.memory_factory)
    writer = Layer2Writer(services.router, workdir, services.memory_factory)
    reviewer = Layer2MarketsReviewerFull(services.router, workdir)

    ticket = researcher._parse_ticket(Path(args.ticket))
    sid = ticket["signal_id"]
    if not sid:
        print("ERROR: ticket has no signal_id", flush=True)
        return 1
    print(f"SIGNAL_ID {sid}", flush=True)

    surfaces = [s.strip() for s in args.surfaces.split(",") if s.strip()]

    # Research (skip if artifact already exists)
    research_file = workdir / "research" / f"signal-{sid}.md"
    if research_file.exists():
        print(f"RESEARCH_EXISTS {research_file}", flush=True)
    else:
        research_file = researcher.run(args.ticket)
        print(f"RESEARCH_DONE {research_file}", flush=True)

    # Write surfaces; blog first so promo carousels can source it.
    ordered = sorted(surfaces,
                     key=lambda s: (0 if s == "blog" else 1 if "carousel" in s else 2))
    for surface in ordered:
        draft = writer.draft_path(sid, surface)
        if draft.exists():
            print(f"DRAFT_EXISTS {draft}", flush=True)
            continue
        mode = ("promo" if surface.startswith("carousel") and "blog" in surfaces
                else args.carousel_mode)
        p = writer.create(sid, surface, mode=mode)
        print(f"WROTE {p}", flush=True)

    if args.skip_review:
        print(f"SIGNAL_DONE {sid}", flush=True)
        return 0

    verdict = reviewer.run(sid, surfaces)
    print(f"REVIEW {verdict.verdict} blockers={verdict.meta.get('blocker_surfaces')}",
          flush=True)
    if verdict.verdict == "block":
        for s in verdict.meta.get("blocker_surfaces", []):
            writer.revise(sid, s, verdict.meta["review_file"])
            print(f"REVISED {s}", flush=True)
        verdict2 = reviewer.run(sid, surfaces)
        print(f"REVIEW2 {verdict2.verdict} blockers={verdict2.meta.get('blocker_surfaces')}",
              flush=True)

    print(f"SIGNAL_DONE {sid}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
