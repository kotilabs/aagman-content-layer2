"""run_content_demo.py — one-shot content harness run using Kimi LLM.

- Loads API keys from aagman-qa-harness/.env
- Wires Kimi (VISION_API_KEY) as the OpenAI-compatible LLM
- Bypasses HumanGates so the loop completes in one shot
- Uses a real signal from aagman-content-layer2's 2026-07-03 digest
- Prints the artifact and the memory state after learning
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import litellm

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from harness_core.agent_memory import AgentMemory
from harness_core.budget import BudgetGuard
from harness_core.domain_config import DomainConfig, StepConfig
from harness_core.generic_harness import GenericHarness
from harness_core.gates import ComplianceGate
from harness_core.judgment_panel import JudgmentPanel
from harness_core.kill_switch import KillSwitch
from harness_core.llm_router import LLMRouter
from harness_core.run import Services, load_env
from harness_core.state import WorkItemStore
from harness_core.telegram import Telegram
from harness_content.agents import (
    ContentSensor, ContentStrategist, ContentCreator, ContentJudge,
    ContentPublisher, ContentMemory, RIA_NAME, RIA_REG,
)


def load_qa_env() -> dict:
    """Overlay aagman-qa-harness/.env onto current env without exposing values."""
    qa_env = Path('/Users/aryansinha/aagman-qa-harness/.env')
    env = dict(os.environ)
    for line in qa_env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env.setdefault(k.strip(), v.strip())
    return env


def kimi_completion_fn(model: str, prompt: str, **kw):
    """OpenAI-compatible Kimi endpoint; forces temperature=1 which the model requires."""
    resp = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        **kw,
    )
    text = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage") or {}
    tokens = usage.get("total_tokens", 0)
    return {"text": text, "tokens": tokens}


def build_content_config_no_human_gates(services) -> DomainConfig:
    """Same as harness_configs/content_config.py but without HumanGates."""
    router = services.router
    memory_factory = services.memory_factory
    env = services.env
    workdir = Path(services.workdir)

    content_dir = REPO / "harness_content"
    sebi_rules = content_dir / "SEBI_RULES.md"
    brand_voice = content_dir / "BRAND_VOICE.md"
    examples = content_dir / "distilled" / "examples.json"
    channel_rules = content_dir / "distilled" / "channel_rules.json"

    inbox = workdir / "inbox"
    outbox = workdir / "outbox"
    ria = env.get("AAGMAN_RIA_NAME", RIA_NAME)
    reg = env.get("AAGMAN_SEBI_REG_NUMBER", RIA_REG)

    compliance = ComplianceGate(
        str(sebi_rules),
        panel=JudgmentPanel(router, "compliance_panel", threshold=1.0).vote,
        threshold=1.0,
    )

    return DomainConfig(name="content", steps=[
        StepConfig("sense", ContentSensor(str(inbox))),
        StepConfig(
            "ideate",
            ContentStrategist(router, memory_factory, str(brand_voice), str(examples)),
            task_type="complex_planning",
        ),
        StepConfig(
            "create",
            ContentCreator(router, memory_factory, str(brand_voice),
                           str(channel_rules), ria, reg),
            task_type="content_gen", mode="parallel", fan_out=["text", "image"],
            gates=[compliance],
        ),
        StepConfig("judge", ContentJudge(router), task_type="judge_panel",
                   loop_limit=2),
        StepConfig("publish", ContentPublisher(str(outbox))),
        StepConfig("learn", ContentMemory(memory_factory)),
    ])


def main():
    env = load_qa_env()
    env["OPENAI_API_KEY"] = env["VISION_API_KEY"]
    env["OPENAI_API_BASE"] = "https://api.kimi.com/coding/v1"
    os.environ.update(env)

    workdir = REPO / "demo_run"
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
            "FIIs have reportedly sold ~₹208,000–260,000 crore of Indian equities "
            "year-to-date, while DIIs have infused ~₹271,000 crore. India VIX is "
            "compressed to sub-14 and the market is range-bound. Write educational "
            "content explaining what this divergence between foreign selling and "
            "domestic buying means for Indian market structure. No investment advice, "
            "no buy/sell call, no price targets."
        ),
        "channel": "linkedin",
        "source": "aagman-content-layer2 signal digest 2026-07-03",
    }
    (workdir / "inbox" / "india-fii-dii-divergence.json").write_text(
        json.dumps(brief, indent=2)
    )

    print("=" * 60)
    print("Running content harness once with Kimi LLM")
    print("Workdir:", workdir)
    print("Signal:", brief["source"])
    print("=" * 60)

    harness.run_once([str(workdir / "inbox")])

    # Show final work item state
    items = list(store.conn.execute("SELECT * FROM work_items").fetchall())
    print("\n--- Work item state ---")
    for row in items:
        print(f"ID: {row['id']}")
        print(f"Status: {row['status']}")
        print(f"Current step: {row['current_step']}")
        print(f"Cost USD: {row['cost_usd']}")

    # Show published artifact if any
    outbox = workdir / "outbox"
    print("\n--- Outbox files ---")
    for f in sorted(outbox.rglob("*")):
        if f.is_file():
            print(f"{f.relative_to(outbox)}:")
            print(f.read_text()[:1200])
            print("-" * 40)

    # Show memory state
    print("\n--- Memory state (lessons) ---")
    for domain_step in [("content", "ideate"), ("content", "create"), ("content", "judge")]:
        mem = memory_factory(*domain_step)
        lessons = mem.all(include_retired=True)
        print(f"\nNamespace {domain_step[0]}.{domain_step[1]} — {len(lessons)} lessons")
        for les in lessons:
            print(f"  {les.id}: helped={les.helped}, misled={les.misled}, "
                  f"confidence={les.confidence:.2f}, retired={les.retired}")
            print(f"    text: {les.text[:120]}...")

    # Show audit log
    print("\n--- Audit log ---")
    audits = list(store.conn.execute(
        "SELECT * FROM audit ORDER BY id"
    ).fetchall())
    for a in audits:
        print(f"  {a['gate_name']}: {a['verdict']} — {a['issues_json'][:200]}")


if __name__ == "__main__":
    main()
