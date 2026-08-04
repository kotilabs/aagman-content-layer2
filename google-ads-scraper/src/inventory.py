"""Inventory output and image enrichment."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .kimi_client import KimiClient
from .models import ScrapeResult

logger = logging.getLogger(__name__)


def write_inventory(result: ScrapeResult, output_dir: Path) -> Path:
    """Write the raw inventory to inventory.json."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "inventory.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump(result.to_dict(), fh, indent=2, ensure_ascii=False)
    logger.info("Wrote inventory to %s", path)
    return path


def enrich_image_descriptions(result: ScrapeResult, client: KimiClient) -> None:
    """Call the vision model for every image ad that has an image_url."""
    image_ads = [ad for ad in result.ads if ad.format == "image" and ad.image_url]
    if not image_ads:
        logger.info("No image ads to describe.")
        return

    logger.info("Enriching %s image ads with vision descriptions.", len(image_ads))
    for idx, ad in enumerate(image_ads, 1):
        try:
            description = client.describe_image(ad.image_url)
            if description:
                ad.image_description = description
            logger.info("Described image ad %s/%s.", idx, len(image_ads))
        except Exception as exc:
            logger.warning("Failed to describe image %s: %s", ad.image_url, exc)
