"""x_cluster.py — CLI wrapper for the X Home-Feed Scout agent.

Usage:
    ./venv/bin/python x_cluster.py fetch
    ./venv/bin/python x_cluster.py fetch --date 2026-07-31
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from harness_agents.x_scout_agent import XScoutAgent
from harness_configs.x_scout_agent_config import XScoutConfig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser("x_cluster.py")
    ap.add_argument("command", choices=["fetch"])
    ap.add_argument("--date", default=None, help="Override date (YYYY-MM-DD)")
    args = ap.parse_args(argv)

    dt = args.date or date.today().isoformat()

    config = XScoutConfig.default()
    agent = XScoutAgent(config)
    cluster_file = agent.run(dt=dt)
    print(f"\nDone: {cluster_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
