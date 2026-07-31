"""x_scout_harness_agent.py — harness SenseAgent wrapper for the X home-feed scout.

Runs the browser-based X scout and emits a Signal that downstream harness steps
(can research / create content from. The Signal payload carries the clustered
tweets markdown plus structured metadata.
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
from harness_configs.x_scout_agent_config import XScoutConfig
from harness_agents.x_scout_agent import XScoutAgent


class XScoutSenseAgent(SenseAgent):
    """SenseAgent that scrolls the user's X home feed and returns clustered signals."""

    def __init__(self, config: XScoutConfig | None = None, dry_run: bool = False):
        self.config = config or XScoutConfig.default()
        self.agent = XScoutAgent(self.config)
        self.dry_run = dry_run

    def sense(self, sources=None) -> list:
        dt = date.today().isoformat()

        if self.dry_run:
            return [Signal(
                id=f"x_scout:{dt}",
                domain="x_scout",
                source="x_home_feed",
                payload={
                    "brief": f"[DRY RUN] X home-feed clusters for {dt}",
                    "clusters_markdown": "_Dry run: browser automation skipped._",
                    "dt": dt,
                    "tweets_skimmed": 0,
                    "cluster_file": "",
                    "raw_tweets_file": "",
                },
            )]

        cluster_file = self.agent.run(dt=dt)
        cluster_text = cluster_file.read_text(encoding="utf-8") if cluster_file.exists() else ""

        # Load raw tweets for structured metadata.
        expanded_path = Path(self.config.workdir) / "raw" / f"{dt}_raw_tweets.json"
        raw_tweets = []
        if expanded_path.exists():
            try:
                raw_tweets = json.loads(expanded_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        payload = {
            "brief": f"X home-feed clusters for {dt}",
            "clusters_markdown": cluster_text,
            "dt": dt,
            "tweets_skimmed": len(raw_tweets),
            "cluster_file": str(cluster_file),
            "raw_tweets_file": str(expanded_path),
        }

        return [Signal(
            id=f"x_scout:{dt}",
            domain="x_scout",
            source="x_home_feed",
            payload=payload,
        )]
