"""reddit_scout_harness_agent.py — harness SenseAgent wrapper for the Reddit scout.

Runs the browser-based Reddit scout and emits a Signal that downstream harness
steps can research / create content from. The Signal payload carries the clustered
posts markdown plus structured metadata.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from harness_core.agent_base import SenseAgent, Signal
from harness_configs.reddit_scout_agent_config import RedditScoutConfig
from harness_agents.reddit_scout_agent import RedditScoutAgent


class RedditScoutSenseAgent(SenseAgent):
    """SenseAgent that scouts configured subreddits and returns clustered signals."""

    def __init__(self, config: RedditScoutConfig | None = None, dry_run: bool = False):
        self.config = config or RedditScoutConfig.default()
        self.agent = RedditScoutAgent(self.config)
        self.dry_run = dry_run

    def sense(self, sources=None) -> list:
        dt = date.today().isoformat()

        if self.dry_run:
            return [Signal(
                id=f"reddit_scout:{dt}",
                domain="reddit_scout",
                source="reddit_subreddits",
                payload={
                    "brief": f"[DRY RUN] Reddit clusters for {dt}",
                    "clusters_markdown": "_Dry run: browser automation skipped._",
                    "dt": dt,
                    "posts_skimmed": 0,
                    "cluster_file": "",
                    "raw_posts_file": "",
                },
            )]

        cluster_file = self.agent.run(dt=dt)
        cluster_text = cluster_file.read_text(encoding="utf-8") if cluster_file.exists() else ""

        # Load raw posts for structured metadata.
        raw_path = Path(self.config.workdir) / "raw" / f"{dt}_raw_posts.json"
        raw_posts: dict[str, list] = {}
        if raw_path.exists():
            try:
                raw_posts = json.loads(raw_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        total_posts = sum(len(v) for v in raw_posts.values())

        payload = {
            "brief": f"Reddit clusters for {dt}",
            "clusters_markdown": cluster_text,
            "dt": dt,
            "posts_skimmed": total_posts,
            "subreddits": self.config.subreddits,
            "sorts": self.config.sorts,
            "cluster_file": str(cluster_file),
            "raw_posts_file": str(raw_path),
        }

        return [Signal(
            id=f"reddit_scout:{dt}",
            domain="reddit_scout",
            source="reddit_subreddits",
            payload=payload,
        )]
