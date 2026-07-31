"""reddit_scout_config.py — harness domain wiring for the Reddit scout.

Run with:
    PYTHONPATH=. ./venv/bin/python harness_core/run.py --domain reddit_scout --once

This domain runs only the SENSE step: it fetches posts from configured Indian
finance/investing subreddits, clusters them, and stores the result as a Signal.
Downstream steps (ideate/create/judge/publish) can be added later to turn the
clusters into content.
"""
from __future__ import annotations

from harness_core.domain_config import DomainConfig, StepConfig
from harness_agents.reddit_scout_harness_agent import RedditScoutSenseAgent
from harness_configs.reddit_scout_agent_config import RedditScoutConfig


def build_config(services=None) -> DomainConfig:
    config = RedditScoutConfig.default()
    dry_run = bool(services and getattr(services, "dry_run", False))

    return DomainConfig(name="reddit_scout", steps=[
        StepConfig("sense", RedditScoutSenseAgent(config, dry_run=dry_run)),
    ])
