"""x_scout_domain_config.py — harness domain wiring for the X home-feed scout.

Run with:
    PYTHONPATH=. ./venv/bin/python harness_core/run.py --domain x_scout --once

This domain runs only the SENSE step: it scrolls the logged-in user's X home
feed, expands relevant tweets, clusters them, and stores the result as a Signal.
Downstream steps (ideate/create/judge/publish) can be added later to turn the
clusters into content.
"""
from __future__ import annotations

from harness_core.domain_config import DomainConfig, StepConfig
from harness_agents.x_scout_harness_agent import XScoutSenseAgent
from harness_configs.x_scout_agent_config import XScoutConfig


def build_config(services=None) -> DomainConfig:
    config = XScoutConfig.default()
    dry_run = bool(services and getattr(services, "dry_run", False))

    return DomainConfig(name="x_scout", steps=[
        StepConfig("sense", XScoutSenseAgent(config, dry_run=dry_run)),
    ])
