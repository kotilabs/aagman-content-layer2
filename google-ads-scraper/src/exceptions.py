"""Custom exceptions for the Google Ads Library scraper."""


class ScrapeBlockedError(Exception):
    """Raised when the scraper is blocked by a bot/CAPTCHA challenge repeatedly."""


class ScrapeTimeoutError(Exception):
    """Raised when a scrape operation exceeds the allowed time."""
