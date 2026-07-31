"""x_scout_config.py — configuration for the X (Twitter) Home-Feed Scout agent.

The X Scout agent scrolls the logged-in user's home feed via browser automation,
skims tweets for relevance, expands the interesting ones, and clusters topics
using an LLM. It can run standalone or be wired into the harness runner.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class XScoutConfig:
    """Configuration for XScoutAgent."""

    # Browser profile to use (must exist in browser-use profile list).
    browser_profile: str = "kotilabs.com"

    # Whether to run the browser in headed mode (visible window).
    headed: bool = True

    # Home feed URL.
    home_url: str = "https://x.com/home"

    # Target tweets to collect from the home feed.
    target_tweets: int = 60

    # Max tweets to expand (open detail page / click Show more) after relevance screening.
    expand_limit: int = 20

    # Number of times to scroll the feed to load more tweets.
    feed_scrolls: int = 8

    # Pixels to scroll per feed scroll.
    scroll_amount: int = 900

    # Seconds to pause between feed scrolls.
    pause_between_scrolls: float = 1.5

    # Seconds to pause between opening individual tweet detail pages.
    pause_between_expansions: float = 1.5

    # Working directory for outputs (raw tweets, clusters, notes).
    workdir: str | Path = "x_run"

    # LLM settings.
    llm_model: str = "deepseek-chat"
    llm_temperature: float = 0.5
    llm_max_tokens: int = 4096

    # Prompt sent to the LLM to screen tweets for relevance.
    relevance_prompt_template: str = (
        "You are skimming a Twitter/X home feed for posts relevant to Indian finance, "
        "investing, trading, macro, policy, or markets.\n"
        "\n"
        "For each tweet below you have:\n"
        "- author name and handle\n"
        "- tweet text (may be truncated)\n"
        "- engagement counts\n"
        "- permalink\n"
        "\n"
        "Return ONLY a JSON array of permalinks for tweets that deserve to be expanded/read fully. "
        "Pick tweets that are likely to contain substantive market signal, analysis, data, news, "
        "or original commentary. Skip memes, personal updates, off-topic banter, and generic "
        "quote-tweets without added value. Aim for roughly one-third of the list unless quality is poor.\n"
        "\n"
        "If nothing looks relevant, return an empty array.\n"
        "\n"
        "--- TWEETS ---\n"
        "\n"
        "{tweets}"
        "\n"
        "---\n"
        "\n"
        "Output: [\"https://x.com/...\", \"https://x.com/...\"]"
    )

    # Prompt sent to the LLM for clustering expanded tweets.
    clustering_prompt_template: str = (
        "You are clustering tweets from an X home feed about Indian finance, investing, "
        "trading, macro, policy, or markets.\n"
        "\n"
        "For each tweet below you have:\n"
        "- author name and handle\n"
        "- full tweet text (expanded)\n"
        "- engagement counts\n"
        "- permalink\n"
        "\n"
        "Group the tweets into 3-7 topic clusters. For each cluster, provide:\n"
        "1. Cluster name (short, specific, descriptive)\n"
        "2. Number of tweets in the cluster\n"
        "3. 2-3 representative tweet summaries (one line each)\n"
        "4. Key tickers, companies, sectors, or themes mentioned\n"
        "5. A 2-3 sentence summary of what the cluster is about and why the tweets belong together\n"
        "6. Permalinks to the representative tweets\n"
        "\n"
        "Only cluster tweets that genuinely belong together. "
        "If a tweet is noise, off-topic, or low-context, put it in an 'Other / Noise' bucket and briefly explain why.\n"
        "\n"
        "--- TWEETS ---\n"
        "\n"
        "{tweets}"
        "\n"
        "---\n"
        "\n"
        "Output the clusters in markdown format."
    )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "XScoutConfig":
        """Build config from a dict, ignoring unknown keys."""
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})

    @classmethod
    def default(cls) -> "XScoutConfig":
        return cls()
