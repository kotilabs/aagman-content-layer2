"""Marketing analysis generation for a scraped ad inventory."""
from __future__ import annotations

import logging
from pathlib import Path

from .kimi_client import KimiClient
from .models import ScrapeResult

logger = logging.getLogger(__name__)


def build_inventory_text(result: ScrapeResult) -> str:
    """Build a compact text representation of the inventory for the LLM."""
    lines = [
        f"Advertiser: {result.advertiser or result.domain}",
        f"Domain: {result.domain}",
        f"Total ads: {len(result.ads)}",
        "",
        "Ads:",
    ]
    for ad in result.ads:
        lines.append(f"- ID: {ad.ad_id}")
        lines.append(f"  Format: {ad.format or 'unknown'}")
        lines.append(f"  Surface: {ad.surface or 'unknown'}")
        if ad.copy:
            if ad.copy.headline:
                lines.append(f"  Headline: {ad.copy.headline}")
            if ad.copy.body:
                body = ad.copy.body.replace('\n', ' ')
                lines.append(f"  Body: {body}")
            if ad.copy.cta:
                lines.append(f"  CTA: {ad.copy.cta}")
            if ad.copy.display_url:
                lines.append(f"  Display URL: {ad.copy.display_url}")
        if ad.image_url:
            lines.append(f"  Image URL: {ad.image_url}")
        if ad.first_seen or ad.last_seen:
            lines.append(f"  Dates: {ad.first_seen or '?'} -> {ad.last_seen or '?'}")
        lines.append("")
    return "\n".join(lines)


def _deterministic_summary(result: ScrapeResult) -> str:
    """Fallback deterministic summary when the LLM call fails."""
    from collections import Counter

    ads = result.ads
    formats = Counter(ad.format for ad in ads if ad.format)
    surfaces = Counter(ad.surface for ad in ads if ad.surface)
    ctas = Counter(ad.copy.cta for ad in ads if ad.copy and ad.copy.cta)
    urls = Counter(ad.copy.display_url for ad in ads if ad.copy and ad.copy.display_url)

    lines = [
        f"# Marketing Analysis: {result.advertiser or result.domain}",
        "",
        f"**Domain:** {result.domain}",
        f"**Total ads:** {len(ads)}",
        "",
        "## Format breakdown",
    ]
    for fmt, count in formats.most_common():
        lines.append(f"- {fmt}: {count}")
    lines.append("")
    lines.append("## Surface breakdown")
    for surface, count in surfaces.most_common():
        lines.append(f"- {surface}: {count}")
    lines.append("")
    lines.append("## Top CTAs")
    for cta, count in ctas.most_common(5):
        lines.append(f"- {cta}: {count}")
    lines.append("")
    lines.append("## Top display URLs")
    for url, count in urls.most_common(5):
        lines.append(f"- {url}: {count}")
    lines.append("")
    lines.append(
        "_This summary was generated deterministically because the LLM call failed._"
    )
    return "\n".join(lines)


def write_analysis(result: ScrapeResult, client: KimiClient, output_dir: Path) -> Path:
    """Generate and write analysis.md for the inventory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory_text = build_inventory_text(result)
    analysis = None
    try:
        analysis = client.summarize_inventory(inventory_text)
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM analysis call raised an error: %s", exc)

    if not analysis:
        logger.warning("LLM analysis failed; using deterministic fallback.")
        analysis = _deterministic_summary(result)

    path = output_dir / "analysis.md"
    with path.open("w", encoding="utf-8") as fh:
        fh.write(analysis)
    logger.info("Wrote analysis to %s", path)
    return path
