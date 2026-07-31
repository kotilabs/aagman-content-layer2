"""run.py — CLI entry.

Usage: PYTHONPATH=. ./venv312/bin/python3 harness_core/run.py --domain <name>
                    [--dry-run] [--once] [--sources ...]

Writes a PID file, clears a stale KILL, loads the named domain config from
harness_configs/<name>_config.py, wires the shared services (store/router/budget/
kill-switch/telegram), and runs GenericHarness — once, or persistently with an
interruptible sleep.
"""
from __future__ import annotations

import argparse
import importlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from harness_core.agent_memory import AgentMemory
from harness_core.budget import BudgetGuard
from harness_core.generic_harness import GenericHarness
from harness_core.kill_switch import KillSwitch
from harness_core.llm_router import LLMRouter
from harness_core.state import WorkItemStore
from harness_core.telegram import Telegram

_REPO = Path(__file__).resolve().parent.parent


@dataclass
class Services:
    """The shared services a domain config needs to construct its agents. Built
    once, injected into build_config(services) AND the harness so agents and the
    loop share one router/store/budget/memory. No domain knowledge lives here."""
    router: Any
    store: Any
    budget: Any
    kill: Any
    telegram: Any
    memory_factory: Callable[[str, str], AgentMemory]
    env: dict
    workdir: str
    dry_run: bool = False


def build_services(env=None, workdir=None, dry_run=False) -> Services:
    env = env or {}
    workdir = Path(workdir or _REPO)
    cost_log = str(workdir / "logs" / "cost_log.jsonl")
    mem_db = str(workdir / "data" / "memory.db")
    telegram = Telegram(env.get("TELEGRAM_BOT_TOKEN"), env.get("TELEGRAM_CHAT_ID"))
    budget = BudgetGuard(float(env.get("DAILY_BUDGET_USD", "5.00")), cost_log,
                         notifier=telegram.notifier(),
                         paused_path=str(workdir / "PAUSED"))
    router = LLMRouter(cost_log_path=cost_log, budget=budget)
    store = WorkItemStore(str(workdir / "data" / "state.db"))
    kill = KillSwitch(str(workdir / "KILL"), pid_path=str(workdir / "PID"))
    return Services(
        router=router, store=store, budget=budget, kill=kill, telegram=telegram,
        memory_factory=lambda domain, step: AgentMemory(domain, step, db_path=mem_db),
        env=dict(env), workdir=str(workdir), dry_run=dry_run,
    )


def load_env(path=None) -> dict:
    """Overlay a .env file onto os.environ (os.environ wins). Minimal parser so we
    don't hard-depend on python-dotenv at import time."""
    env = dict(os.environ)
    p = Path(path) if path else _REPO / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env.setdefault(k.strip(), v.strip())
    return env


def load_domain(name, services=None):
    """Import harness_configs/<name>_config.py and call build_config(services)."""
    try:
        mod = importlib.import_module(f"harness_configs.{name}_config")
    except ModuleNotFoundError as e:
        raise SystemExit(
            f"domain '{name}' has no config (harness_configs/{name}_config.py); "
            f"it is wired in a later phase. [{e}]")
    return mod.build_config(services)


def build_harness(config, *, workdir=None, dry_run=False, env=None,
                  services=None) -> GenericHarness:
    if services is None:
        services = build_services(env or {}, workdir, dry_run)
    harness = GenericHarness(config, services.store, kill_switch=services.kill,
                             budget=services.budget,
                             memory_factory=services.memory_factory,
                             workdir=services.workdir, dry_run=dry_run,
                             prioritizer=getattr(config, "prioritizer", None))
    harness.router = services.router
    harness.telegram = services.telegram
    return harness


def main(argv=None) -> int:
    ap = argparse.ArgumentParser("aagman-harness")
    ap.add_argument("--domain", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--sources", nargs="*", default=[])
    args = ap.parse_args(argv)

    env = load_env()
    services = build_services(env, _REPO, dry_run=args.dry_run)
    config = load_domain(args.domain, services)
    harness = build_harness(config, dry_run=args.dry_run, services=services)
    harness.kill_switch.write_pid(os.getpid())
    harness.kill_switch.disarm()  # clear a stale KILL from a previous run

    if args.once:
        harness.run_once(args.sources)
        return 0
    while not harness.kill_switch.is_killed():
        harness.run_once(args.sources)
        if harness.kill_switch.sleep_interruptible(30, chunk=10):
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
