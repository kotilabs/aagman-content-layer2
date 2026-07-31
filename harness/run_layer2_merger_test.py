"""run_layer2_merger_test.py — end-to-end test of the content-layer2 + harness merger.

Runs the Layer 2 content loop once with Kimi Code as the LLM provider. The harness
pauses at each LLM call and writes a request file; Kimi Code provides the response.

For a faster first test, set LAYER2_SURFACES=blog,thread and LAYER2_AUTO_APPROVE=1.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from harness_core.agent_memory import AgentMemory
from harness_core.budget import BudgetGuard
from harness_core.generic_harness import GenericHarness
from harness_core.kill_switch import KillSwitch
from harness_core.llm_router import LLMRouter
from harness_core.run import Services, load_env
from harness_core.state import WorkItemStore
from harness_core.telegram import Telegram
from harness_configs.kimi_code_bridge import make_kimi_code_bridge
from harness_configs.layer2_config import build_config
from harness_content.seed_layer2 import seed_all


WORKDIR_NAME = "layer2_demo_run"


def load_or_create_env():
    """Load harness .env if present; otherwise use empty env. No secrets needed."""
    env_path = REPO / ".env"
    if env_path.exists():
        return load_env(str(env_path))
    return {}


def ensure_gate_approval(workdir: Path, work_item_id: str, gate_name: str):
    """Create an APPROVED marker so the HumanGate passes without blocking."""
    gate_dir = workdir / "gates" / work_item_id / gate_name
    gate_dir.mkdir(parents=True, exist_ok=True)
    (gate_dir / "APPROVED").write_text("auto-approved for test run\n")


def main():
    env = load_or_create_env()
    env.setdefault("LAYER2_DIGEST_PATH",
                   str(REPO / WORKDIR_NAME / "signals" / "2026-07-03-digest.md"))
    # First test: blog + thread only, auto-approve gates.
    env.setdefault("LAYER2_SURFACES", "blog,thread")
    auto_approve = os.environ.get("LAYER2_AUTO_APPROVE", "1") == "1"

    workdir = REPO / WORKDIR_NAME
    workdir.mkdir(exist_ok=True)
    (workdir / "inbox").mkdir(exist_ok=True)
    (workdir / "outbox").mkdir(exist_ok=True)
    (workdir / "logs").mkdir(exist_ok=True)
    (workdir / "data").mkdir(exist_ok=True)
    (workdir / "gates" / "llm_requests").mkdir(parents=True, exist_ok=True)
    (workdir / "gates" / "llm_responses").mkdir(parents=True, exist_ok=True)

    # Seed memory from content-layer2 artifacts.
    mem_db = str(workdir / "data" / "memory.db")
    print("Seeding Layer 2 memory...")
    seed_counts = seed_all(db_path=mem_db)
    for ns, n in seed_counts.items():
        print(f"  {ns}: {n} lessons")

    # Set up the Kimi Code bridge.
    request_dir = workdir / "gates" / "llm_requests"
    response_dir = workdir / "gates" / "llm_responses"
    bridge = make_kimi_code_bridge(request_dir, response_dir, poll_interval=2.0)

    cost_log = str(workdir / "logs" / "cost_log.jsonl")
    router = LLMRouter(
        models_yaml_path=str(REPO / "harness_configs" / "models_kimi.yaml"),
        completion_fn=bridge,
        cost_log_path=cost_log,
    )
    # Override pricing to zero since Kimi Code is the runtime.
    router.pricing = {m: 0.0 for m in router.pricing}

    store = WorkItemStore(str(workdir / "data" / "state.db"))
    kill = KillSwitch(str(workdir / "KILL"), pid_path=str(workdir / "PID"))
    telegram = Telegram(env.get("TELEGRAM_BOT_TOKEN"), env.get("TELEGRAM_CHAT_ID"))
    budget = BudgetGuard(float(env.get("DAILY_BUDGET_USD", "5.00")), cost_log,
                         notifier=telegram.notifier(),
                         paused_path=str(workdir / "PAUSED"))

    memory_factory = lambda domain, step: AgentMemory(domain, step, db_path=mem_db)
    services = Services(
        router=router, store=store, budget=budget, kill=kill, telegram=telegram,
        memory_factory=memory_factory, env=dict(env), workdir=str(workdir),
        dry_run=False,
    )

    config = build_config(services)
    harness = GenericHarness(
        config, services.store, kill_switch=services.kill,
        budget=services.budget, memory_factory=services.memory_factory,
        workdir=services.workdir, dry_run=False,
    )

    # Pre-approve gates if requested.
    work_item_id = "layer2:layer2-test-signal"
    if auto_approve:
        ensure_gate_approval(workdir, work_item_id, "research_approval")
        ensure_gate_approval(workdir, work_item_id, "publish_approval")
        print("Auto-approved research_approval and publish_approval gates.")

    # Create a test inbox signal (fallback if digest parsing fails).
    test_signal = {
        "brief": (
            "FIIs have sold heavily in Indian equities year-to-date while DIIs "
            "have absorbed the selling, keeping the market range-bound. India VIX "
            "is compressed. Explain what this foreign-domestic divergence means "
            "for Indian market structure. No investment advice, no buy/sell call, "
            "no price targets."
        ),
        "surfaces": env["LAYER2_SURFACES"].split(","),
        "source": "layer2 merger test",
    }
    (workdir / "inbox" / "layer2-test-signal.json").write_text(
        json.dumps(test_signal, indent=2), encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("Running Layer 2 merger test with Kimi Code bridge")
    print(f"Workdir: {workdir}")
    print(f"Surfaces: {env['LAYER2_SURFACES']}")
    print("=" * 60)
    print("\nWhen you see a request path, read it, write the response to the")
    print("given response path, and the harness will continue.\n")

    harness.run_once([str(workdir / "inbox")])

    # Report state.
    items = list(store.conn.execute("SELECT * FROM work_items").fetchall())
    print("\n--- Work item state ---")
    for row in items:
        print(f"ID: {row['id']}")
        print(f"Status: {row['status']}")
        print(f"Current step: {row['current_step']}")
        print(f"Cost USD: {row['cost_usd']}")

    print("\n--- Outbox files ---")
    outbox = workdir / "outbox"
    files = list(outbox.rglob("*.md"))
    if not files:
        print("  (none)")
    for f in sorted(files):
        print(f"\n{f.relative_to(outbox)}:")
        print(f.read_text(encoding="utf-8")[:1200])
        print("-" * 40)

    print("\n--- Memory state (lessons) ---")
    for domain_step in [("content", "ideate"), ("content", "create"), ("content", "judge")]:
        mem = memory_factory(*domain_step)
        lessons = mem.all(include_retired=True)
        print(f"\nNamespace {domain_step[0]}.{domain_step[1]} — {len(lessons)} lessons")
        for les in lessons:
            print(f"  {les.id}: helped={les.helped}, misled={les.misled}, "
                  f"confidence={les.confidence:.2f}, retired={les.retired}")
            print(f"    text: {les.text[:120]}...")

    print("\n--- Audit log ---")
    audits = list(store.conn.execute("SELECT * FROM audit ORDER BY id").fetchall())
    if not audits:
        print("  (none)")
    for a in audits:
        print(f"  {a['gate_name']}: {a['verdict']} — {a['issues_json'][:200]}")


if __name__ == "__main__":
    main()
