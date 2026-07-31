"""run_content_demo_seeded.py — demonstrate self-evolution with a seeded lesson.

Same wiring as run_content_demo.py, but before the run we seed a lesson in the
content.ideate namespace. The ContentStrategist recalls it, stamps provenance,
and after the final publish the GenericHarness._attribute() credits the lesson.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import litellm

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from run_content_demo import (
    load_qa_env, kimi_completion_fn, build_content_config_no_human_gates
)
from harness_core.agent_memory import AgentMemory
from harness_core.budget import BudgetGuard
from harness_core.generic_harness import GenericHarness
from harness_core.kill_switch import KillSwitch
from harness_core.llm_router import LLMRouter
from harness_core.run import Services
from harness_core.state import WorkItemStore
from harness_core.telegram import Telegram


def main():
    env = load_qa_env()
    env["OPENAI_API_KEY"] = env["VISION_API_KEY"]
    env["OPENAI_API_BASE"] = "https://api.kimi.com/coding/v1"
    os.environ.update(env)

    workdir = REPO / "demo_run_seeded"
    workdir.mkdir(exist_ok=True)
    (workdir / "inbox").mkdir(exist_ok=True)
    (workdir / "outbox").mkdir(exist_ok=True)
    (workdir / "logs").mkdir(exist_ok=True)
    (workdir / "data").mkdir(exist_ok=True)

    cost_log = str(workdir / "logs" / "cost_log.jsonl")
    mem_db = str(workdir / "data" / "memory.db")

    telegram = Telegram(env.get("TELEGRAM_BOT_TOKEN"), env.get("TELEGRAM_CHAT_ID"))
    budget = BudgetGuard(float(env.get("DAILY_BUDGET_USD", "5.00")), cost_log,
                         notifier=telegram.notifier(),
                         paused_path=str(workdir / "PAUSED"))
    router = LLMRouter(
        models_yaml_path=str(REPO / "demo_models.yaml"),
        completion_fn=kimi_completion_fn,
        cost_log_path=cost_log,
        budget=budget,
    )
    store = WorkItemStore(str(workdir / "data" / "state.db"))
    kill = KillSwitch(str(workdir / "KILL"), pid_path=str(workdir / "PID"))

    memory_factory = lambda domain, step: AgentMemory(domain, step, db_path=mem_db)
    services = Services(
        router=router, store=store, budget=budget, kill=kill, telegram=telegram,
        memory_factory=memory_factory, env=dict(env), workdir=str(workdir),
        dry_run=False,
    )

    # Seed a lesson BEFORE the run
    ideate_mem = memory_factory("content", "ideate")
    seed = ideate_mem.add(
        text=(
            "For Indian market-flow stories, open with a concrete, dated statistic "
            "(e.g., a net FII/DII figure) rather than a narrative judgment. This "
            "frames the piece as educational market mechanics, not advice."
        ),
        tags="approved, hook, fii-dii, india",
    )
    print("=" * 60)
    print("Seeded lesson:", seed.id)
    print("Text:", seed.text)
    print("Initial confidence:", seed.confidence)
    print("=" * 60)

    config = build_content_config_no_human_gates(services)
    harness = GenericHarness(
        config, services.store, kill_switch=services.kill,
        budget=services.budget, memory_factory=services.memory_factory,
        workdir=services.workdir, dry_run=False,
    )
    harness.router = services.router
    harness.telegram = services.telegram

    brief = {
        "brief": (
            "Domestic institutional investors have bought roughly ₹271,000 crore of "
            "Indian equities this year while foreign portfolio investors have sold "
            "in the ₹208,000–260,000 crore range. India VIX is in a low-volatility "
            "zone. Explain what this domestic-foreign flow divergence means for "
            "market structure, without any buy/sell recommendation or price target."
        ),
        "channel": "linkedin",
        "source": "aagman-content-layer2 signal digest 2026-07-03 — seeded run",
    }
    (workdir / "inbox" / "india-flow-divergence-seeded.json").write_text(
        json.dumps(brief, indent=2)
    )

    print("\nRunning content harness once with seeded lesson...")
    harness.run_once([str(workdir / "inbox")])

    # Show final work item state
    items = list(store.conn.execute("SELECT * FROM work_items").fetchall())
    print("\n--- Work item state ---")
    for row in items:
        print(f"ID: {row['id']}")
        print(f"Status: {row['status']}")
        print(f"Current step: {row['current_step']}")

    # Show memory state
    print("\n--- Memory state after run ---")
    for domain_step in [("content", "ideate"), ("content", "create"), ("content", "judge")]:
        mem = memory_factory(*domain_step)
        lessons = mem.all(include_retired=True)
        print(f"\nNamespace {domain_step[0]}.{domain_step[1]} — {len(lessons)} lessons")
        for les in lessons:
            print(f"  {les.id}: helped={les.helped}, misled={les.misled}, "
                  f"confidence={les.confidence:.2f}, retired={les.retired}")
            print(f"    text: {les.text[:140]}...")

    # Verify the seeded lesson was credited
    seed_after = ideate_mem.get(seed.id)
    print(f"\n--- Seeded lesson outcome ---")
    print(f"Before: helped={seed.helped}, misled={seed.misled}, confidence={seed.confidence:.2f}")
    print(f"After:  helped={seed_after.helped}, misled={seed_after.misled}, confidence={seed_after.confidence:.2f}")
    if seed_after.helped > seed.helped:
        print("✅ Self-evolution attribution worked: the recalled lesson was credited on publish.")
    else:
        print("⚠️ The seeded lesson was NOT credited. It may not have been recalled/re relied on.")

    # Show published artifact
    outbox = workdir / "outbox"
    print("\n--- Published artifact ---")
    for f in sorted(outbox.rglob("*.md")):
        print(f.read_text()[:1500])

    # Total cost
    total = 0.0
    with open(cost_log) as f:
        for line in f:
            total += json.loads(line).get("cost_usd", 0)
    print(f"\nTotal cost USD: ${total:.4f}")


if __name__ == "__main__":
    main()
