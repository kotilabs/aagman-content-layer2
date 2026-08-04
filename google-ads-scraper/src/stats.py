"""Deterministic statistics generation from a ScrapeResult."""
from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path

from .models import ScrapeResult

logger = logging.getLogger(__name__)


def build_stats(result: ScrapeResult) -> dict:
    """Return a deterministic stats dict for the scraped inventory."""
    ads = result.ads
    formats = Counter(ad.format for ad in ads if ad.format)
    surfaces = Counter(ad.surface for ad in ads if ad.surface)

    ctas = Counter(
        ad.copy.cta for ad in ads if ad.copy and ad.copy.cta
    )
    display_urls = Counter(
        ad.copy.display_url for ad in ads if ad.copy and ad.copy.display_url
    )

    first_seen_dates = [ad.first_seen for ad in ads if ad.first_seen]
    last_seen_dates = [ad.last_seen for ad in ads if ad.last_seen]

    copy_present = {
        "with_headline": sum(1 for ad in ads if ad.copy and ad.copy.headline),
        "with_body": sum(1 for ad in ads if ad.copy and ad.copy.body),
        "with_cta": sum(1 for ad in ads if ad.copy and ad.copy.cta),
        "with_display_url": sum(1 for ad in ads if ad.copy and ad.copy.display_url),
        "with_image": sum(1 for ad in ads if ad.image_url),
    }

    return {
        "domain": result.domain,
        "advertiser": result.advertiser,
        "scraped_at": result.scraped_at,
        "total_ads": len(ads),
        "formats": dict(formats),
        "surfaces": dict(surfaces),
        "date_range": {
            "first_seen_earliest": min(first_seen_dates) if first_seen_dates else None,
            "last_seen_latest": max(last_seen_dates) if last_seen_dates else None,
        },
        "top_ctas": dict(ctas.most_common(10)),
        "top_display_urls": dict(display_urls.most_common(10)),
        "copy_presence": copy_present,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def write_stats(result: ScrapeResult, output_dir: Path) -> Path:
    """Build stats and write them to stats.json in the output directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stats = build_stats(result)
    path = output_dir / "stats.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)
    logger.info("Wrote stats to %s", path)
    return path
