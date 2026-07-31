"""reddit_cluster.py — CLI wrapper for the Reddit Scout agent.

Usage:
    ./venv/bin/python reddit_cluster.py fetch
    ./venv/bin/python reddit_cluster.py fetch --subreddits IndianStockMarket,DalalStreetTalks
    ./venv/bin/python reddit_cluster.py fetch --date 2026-07-31
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from harness_agents.reddit_scout_agent import RedditScoutAgent
from harness_configs.reddit_scout_agent_config import RedditScoutConfig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser("reddit_cluster.py")
    ap.add_argument("command", choices=["fetch"])
    ap.add_argument("--date", default=None, help="Override date (YYYY-MM-DD)")
    ap.add_argument(
        "--subreddits",
        default=None,
        help="Comma-separated subreddits to fetch (default: all configured)",
    )
    args = ap.parse_args(argv)

    dt = args.date or date.today().isoformat()
    subreddits = None
    if args.subreddits:
        subreddits = [s.strip() for s in args.subreddits.split(",") if s.strip()]

    config = RedditScoutConfig.default()
    agent = RedditScoutAgent(config)
    cluster_file = agent.run(dt=dt, subreddits=subreddits)
    print(f"\nDone: {cluster_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
