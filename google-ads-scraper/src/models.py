"""Shared data models for the Google Ads Library scraper."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AdCopy:
    headline: Optional[str] = None
    body: Optional[str] = None
    cta: Optional[str] = None
    display_url: Optional[str] = None


@dataclass
class AdRecord:
    ad_id: str
    advertiser_name: Optional[str] = None
    format: Optional[str] = None  # text, image, video
    surface: Optional[str] = None  # Search, YouTube, Display, etc.
    copy: AdCopy = field(default_factory=AdCopy)
    image_url: Optional[str] = None
    image_description: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "ad_id": self.ad_id,
            "advertiser_name": self.advertiser_name,
            "format": self.format,
            "surface": self.surface,
            "copy": {
                "headline": self.copy.headline,
                "body": self.copy.body,
                "cta": self.copy.cta,
                "display_url": self.copy.display_url,
            },
            "image_url": self.image_url,
            "image_description": self.image_description,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }


@dataclass
class ScrapeResult:
    domain: str
    advertiser: Optional[str] = None
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    total_ads: int = 0
    ads: list[AdRecord] = field(default_factory=list)

    def to_dict(self) -> dict:
        from collections import Counter
        return {
            "domain": self.domain,
            "advertiser": self.advertiser,
            "scraped_at": self.scraped_at,
            "total_ads": len(self.ads),
            "ads": [ad.to_dict() for ad in self.ads],
            "surface_analysis": dict(Counter([ad.surface for ad in self.ads if ad.surface])),
            "format_analysis": dict(Counter([ad.format for ad in self.ads if ad.format])),
        }
