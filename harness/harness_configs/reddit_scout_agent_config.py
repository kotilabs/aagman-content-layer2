"""reddit_scout_config.py — configuration for the Reddit Scout agent.

The Reddit Scout agent reads Indian finance/investing subreddits via browser
automation, extracts posts + comments, and clusters them into themes using an
LLM. It can run standalone or be invoked by the harness runner.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RedditScoutConfig:
    """Configuration for RedditScoutAgent."""

    # Browser profile to use (must exist in browser-use profile list).
    browser_profile: str = "kotilabs.com"

    # Whether to run the browser in headed mode (visible window).
    # Headed mode is more resistant to Reddit anti-bot detection.
    headed: bool = True

    # Subreddits to scout.
    subreddits: list[str] = field(default_factory=lambda: [
        "IndianStockMarket",
        "DalalStreetTalks",
        "IndianStocks",
        "IndianStreetBets",
        "MutualfundsIndia",
    ])

    # Sort orders to fetch per subreddit.
    sorts: list[str] = field(default_factory=lambda: ["new", "hot"])

    # Posts to extract per subreddit per sort.
    limit: int = 10

    # Comments to read per post.
    comments_per_post: int = 5

    # Seconds to pause after finishing both sorts for a subreddit.
    pause_between_subreddits: float = 20.0

    # Seconds to pause between opening individual post detail pages.
    pause_between_posts: float = 1.0

    # Number of times to scroll a feed page to load more posts.
    feed_scrolls: int = 3

    # Working directory for outputs (raw posts, clusters, notes).
    workdir: str | Path = "reddit_run"

    # LLM clustering settings.
    # If a direct OpenAI-compatible API is configured in env, it is used first;
    # otherwise the agent falls back to the kimi_code_bridge.
    llm_model: str = "deepseek-chat"
    llm_temperature: float = 0.5
    llm_max_tokens: int = 4096

    # Prompt sent to the LLM for clustering.
    clustering_prompt_template: str = (
        "You are clustering Reddit posts from Indian finance/investing subreddits.\n"
        "Sort order: {sort_upper}\n"
        "\n"
        "For each post below you have:\n"
        "- subreddit\n"
        "- title\n"
        "- post body or preview\n"
        "- up to {comments_per_post} top comments\n"
        "- permalink\n"
        "\n"
        "Group the posts into 3-7 topic clusters. For each cluster, provide:\n"
        "1. Cluster name (short, specific, descriptive)\n"
        "2. Number of posts in the cluster\n"
        "3. 2-3 representative post titles\n"
        "4. Key tickers, companies, or themes mentioned\n"
        "5. A 2-3 sentence summary of what the cluster is about and why the posts belong together\n"
        "6. Permalinks to the representative posts\n"
        "\n"
        "Only cluster posts that genuinely belong together. "
        "If a post is noise, off-topic, or low-context, put it in an 'Other / Noise' bucket and briefly explain why.\n"
        "\n"
        "--- POSTS ---\n"
        "\n"
        "{posts}"
        "\n"
        "---\n"
        "\n"
        "Output the clusters in markdown format."
    )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RedditScoutConfig":
        """Build config from a dict, ignoring unknown keys."""
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})

    @classmethod
    def default(cls) -> "RedditScoutConfig":
        return cls()
