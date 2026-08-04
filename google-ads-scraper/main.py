#!/usr/bin/env python3
"""CLI entry point for the Google Ads Library scraper."""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.config import Config
from src.exceptions import ScrapeBlockedError, ScrapeTimeoutError
from src.kimi_client import KimiClient
from src.scraper import Scraper
from src.stats import write_stats
from src.analysis import write_analysis
from src.inventory import write_inventory, enrich_image_descriptions


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape Google Ads Transparency Center for a domain."
    )
    parser.add_argument("domain", help="Domain or URL of the advertiser to scrape.")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maximum number of ads to scrape (0 = unlimited).",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Run browser in headless mode (default from env/Config).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Base output directory (default from Config).",
    )
    return parser.parse_args()


def make_output_dir(base_dir: Path, domain: str) -> Path:
    """Create a timestamped output directory for this scrape run."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_domain = "".join(c if c.isalnum() or c in "-." else "_" for c in domain)
    out = base_dir / f"{safe_domain}_{timestamp}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def main() -> int:
    setup_logging()
    logger = logging.getLogger("main")
    args = parse_args()

    config = Config()
    if args.limit:
        config.max_ads = args.limit
    if args.headless is not None:
        config.headless = args.headless
    if args.output_dir:
        config.output_dir = args.output_dir

    try:
        config.validate()
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1

    output_dir = make_output_dir(config.output_dir, args.domain)
    logger.info("Output directory: %s", output_dir)

    try:
        scraper = Scraper(config)
        result = scraper.scrape(args.domain)
    except (ScrapeBlockedError, ScrapeTimeoutError) as exc:
        logger.error("Scrape blocked or timed out: %s", exc)
        return 1
    except Exception as exc:
        logger.exception("Unexpected scraper error: %s", exc)
        return 1

    if not result.ads:
        logger.info("No ads found for %r. Exiting cleanly.", result.domain)
        return 0

    logger.info("Scraped %s ads for %r.", len(result.ads), result.domain)

    try:
        write_inventory(result, output_dir)
    except Exception as exc:
        logger.exception("Failed to write inventory: %s", exc)
        return 1

    try:
        write_stats(result, output_dir)
    except Exception as exc:
        logger.exception("Failed to write stats: %s", exc)
        return 1

    try:
        client = KimiClient(config)
        enrich_image_descriptions(result, client)
        write_analysis(result, client, output_dir)
    except Exception as exc:
        logger.exception("Failed to generate analysis: %s", exc)
        return 1

    logger.info("Done. Results written to %s", output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
