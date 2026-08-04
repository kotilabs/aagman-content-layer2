"""Google Ads Transparency Center scraper.

Uses Playwright to land on the Google Ads Transparency Center, search for an
advertiser, and then calls the internal ``SearchCreatives`` RPC directly to
fetch the complete ad inventory. This avoids the SPA's lazy DOM pagination,
which only renders a handful of creatives in the page and loads the rest over
the RPC.
"""
from __future__ import annotations

import json
import logging
import re
import time
import urllib.parse
from datetime import datetime, timezone

import requests
from playwright.sync_api import (
    Page,
    Playwright,
    Browser,
    BrowserContext,
    sync_playwright,
    TimeoutError as PlaywrightTimeout,
    Error as PlaywrightError,
)

from .config import Config
from .exceptions import ScrapeBlockedError, ScrapeTimeoutError
from .models import AdCopy, AdRecord, ScrapeResult

logger = logging.getLogger(__name__)

GOOGLE_ADS_TRANSPARENCY_URL = "https://adstransparency.google.com/"
SEARCH_CREATIVES_RPC = (
    "https://adstransparency.google.com/anji/_/rpc/SearchService/SearchCreatives?authuser="
)
DEFAULT_PAGE_SIZE = 40

# Common selectors used by the Google Ads Transparency Center SPA. These are
# best-effort and grouped so the scraper can drive the search UI.
SEARCH_INPUT_SELECTORS = [
    'input.input-area',
    'input[aria-label*="earch advertiser" i]',
    'input[placeholder*="earch" i]',
    'input[type="search"]',
    'input[aria-label*="dvertiser" i]',
    'search-bar input',
    'ads-transparency-search input',
]

SEARCH_RESULT_SELECTORS = [
    'material-select-item[role="option"]',
    '[role="listbox"] [role="option"]',
    '[data-test-id*="search-result" i]',
    '.search-result',
    'a[href*="advertiser" i]',
    '[role="dialog"] a',
]

BLOCKED_INDICATORS = [
    "recaptcha",
    "captcha",
    "unusual traffic",
    "before you continue",
    "automated requests",
    "sorry",
    "verify you're a human",
]


def _normalize_domain(domain: str) -> str:
    """Return a lower-case domain without scheme, path, port or www prefix."""
    from urllib.parse import urlparse

    domain = domain.strip().lower()
    if domain.startswith("http://") or domain.startswith("https://"):
        parsed = urlparse(domain)
        domain = parsed.netloc or parsed.path
    domain = domain.removeprefix("www.")
    domain = domain.split(":")[0]
    domain = domain.strip("/")
    if not domain or "." not in domain:
        raise ValueError(f"Invalid domain: {domain!r}")
    return domain


class Scraper:
    """Scraper for Google Ads Transparency Center."""

    def __init__(self, config: Config):
        self.config = config
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None

    def _start_browser(self) -> None:
        if self.playwright is not None:
            return
        logger.info("Starting Playwright browser.")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )

    def _stop_browser(self) -> None:
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None

    def _create_context(self) -> BrowserContext:
        """Create a fresh browser context with human-like settings."""
        if not self.browser:
            raise RuntimeError("Browser not started")
        return self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/New_York",
        )

    def _delay(self) -> None:
        """Pause for the configured delay between interactions."""
        if self.config.delay_seconds > 0:
            time.sleep(self.config.delay_seconds)

    @staticmethod
    def _looks_blocked(page: Page) -> bool:
        """Check page content for CAPTCHA / bot challenge indicators."""
        text = ""
        try:
            text = page.content().lower()
        except PlaywrightError:
            pass
        title = ""
        try:
            title = (page.title() or "").lower()
        except PlaywrightError:
            pass
        combined = f"{title} {text}"
        return any(indicator in combined for indicator in BLOCKED_INDICATORS)

    def _wait_for_stable_page(self, page: Page) -> None:
        """Wait until the page looks loaded and not blocked."""
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            page.wait_for_load_state("networkidle", timeout=15000)
        except PlaywrightTimeout:
            pass

        deadline = time.time() + 30
        while time.time() < deadline:
            if self._looks_blocked(page):
                return
            ready_state = page.evaluate("document.readyState")
            if ready_state == "complete":
                return
            time.sleep(0.5)
        raise ScrapeTimeoutError("Page did not stabilize within 30 seconds.")

    def _dismiss_overlays(self, page: Page) -> None:
        """Click away common cookie / consent dialogs."""
        consent_selectors = [
            'button:has-text("Accept all")',
            'button:has-text("I agree")',
            'button:has-text("Got it")',
            'button:has-text("No thanks")',
            '[aria-label*="Accept" i]',
        ]
        for selector in consent_selectors:
            try:
                button = page.locator(selector).first
                if button.is_visible(timeout=2000):
                    button.click(timeout=5000)
                    self._delay()
                    return
            except PlaywrightError:
                continue

    def _find_search_input(self, page: Page):
        """Locate the advertiser search input, returning its locator."""
        for selector in SEARCH_INPUT_SELECTORS:
            locator = page.locator(selector).first
            try:
                if locator.is_visible(timeout=2000):
                    return locator
            except PlaywrightError:
                continue
        raise ScrapeTimeoutError("Could not find search input on homepage.")

    def _find_search_results(self, page: Page):
        """Return visible search result locators."""
        for selector in SEARCH_RESULT_SELECTORS:
            locators = page.locator(selector)
            try:
                if locators.count() > 0 and locators.first.is_visible(timeout=2000):
                    return locators
            except PlaywrightError:
                continue
        return page.locator("body").locator("*").filter(
            has_text=re.compile(r"advertiser", re.IGNORECASE)
        )

    def _search_advertiser(self, page: Page, domain: str):
        """Type the domain into the search box and wait for results."""
        search_input = self._find_search_input(page)
        logger.info("Typing domain %r into search input.", domain)
        search_input.click(timeout=10000)
        search_input.fill(domain)
        self._delay()
        search_input.press("Enter")
        self._delay()

        try:
            page.wait_for_timeout(2000)
        except PlaywrightError:
            pass

        # Wait a bit longer for async suggestions.
        for _ in range(10):
            results = self._find_search_results(page)
            if results.count() > 0:
                return results
            time.sleep(0.5)
        return None

    def _select_exact_match(self, page: Page, domain: str) -> str | None:
        """Select the search result whose text best matches the domain."""
        results = self._find_search_results(page)
        count = results.count()
        if count == 0:
            return None

        base_name = domain.split(".")[0]

        best_index = -1
        best_score = -1
        for i in range(count):
            try:
                text = (results.nth(i).text_content() or "").lower()
            except PlaywrightError:
                continue
            score = 0
            if domain in text:
                score += 20
            if base_name in text:
                score += 10
            if text.startswith(domain) or text.startswith(base_name):
                score += 5
            if "." in text:
                score += 1
            if score > best_score:
                best_score = score
                best_index = i

        if best_index < 0 or best_score < 10:
            logger.info(
                "No strong advertiser match for %r; treating as no results.", domain
            )
            return None

        selected = results.nth(best_index)
        advertiser_name = (selected.text_content() or "").strip().split("\n")[0].strip()
        logger.info("Selecting advertiser: %s", advertiser_name)
        selected.click(timeout=10000)
        self._delay()
        return advertiser_name

    @staticmethod
    def _extract_img_src_and_dims(html: str) -> tuple[str | None, tuple[int | None, int | None]]:
        """Return the first meaningful image src and (width, height) from an HTML snippet."""
        src_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
        src = src_match.group(1) if src_match else None
        if src and src.startswith("data:"):
            src = None

        width = height = None
        w_match = re.search(r'width=["\']([\d.]+)["\']', html, re.IGNORECASE)
        h_match = re.search(r'height=["\']([\d.]+)["\']', html, re.IGNORECASE)
        try:
            width = int(float(w_match.group(1))) if w_match else None
        except ValueError:
            pass
        try:
            height = int(float(h_match.group(1))) if h_match else None
        except ValueError:
            pass
        return src, (width, height)

    @staticmethod
    def _extract_preview_image_from_js(js_url: str, session: requests.Session) -> str | None:
        """Fetch a Google preview content.js and extract the preview image URL."""
        try:
            resp = session.get(js_url, timeout=30)
            resp.raise_for_status()
            text = resp.text
            # previewservice.insertPreviewImageContent(parentId, elementId, imageUrl, width, height)
            m = re.search(
                r"insertPreviewImageContent\([^,]+,\s*[^,]+,\s*['\"]([^'\"]+)['\"]",
                text,
            )
            if m:
                return m.group(1)
            # Fallback: generic image URL in the last part of the script.
            m = re.search(r"https?://[^\s'\"<>]+\.(?:jpg|jpeg|png|gif)", text)
            if m:
                return m.group(0)
        except Exception as exc:
            logger.warning("Failed to fetch preview JS %s: %s", js_url, exc)
        return None

    @staticmethod
    def _format_timestamp(field: dict | None) -> str | None:
        """Convert a SearchCreatives timestamp object to an ISO date string."""
        if not field:
            return None
        try:
            seconds = int(field["1"])
            nanos = int(field.get("2", 0))
            dt = datetime.fromtimestamp(seconds + nanos / 1e9, tz=timezone.utc)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None

    @staticmethod
    def _build_search_payload(domain: str, token: str | None = None, page_size: int = 40) -> str:
        """Build the x-www-form-urlencoded payload for SearchCreatives."""
        data = {
            "2": page_size,
            "3": {
                "8": [2356],
                "12": {"1": domain, "2": True},
            },
            "7": {"1": 1, "2": 0, "3": 2356},
        }
        if token:
            data["4"] = token
        return urllib.parse.urlencode(
            {"f.req": json.dumps(data, separators=(",", ":"))}
        )

    def _api_session_for_page(self, page: Page) -> requests.Session:
        """Create a requests session seeded with the current browser cookies."""
        session = requests.Session()
        session.headers.update({
            "content-type": "application/x-www-form-urlencoded",
            "referer": f"https://adstransparency.google.com/?region=IN&domain={self._current_domain}",
            "x-same-domain": "1",
            "user-agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "x-framework-xsrf-token": "",
        })
        cookies = {c["name"]: c["value"] for c in page.context.cookies()}
        session.cookies.update(cookies)
        return session

    def _parse_api_item(
        self,
        item: dict,
        advertiser_name: str | None,
        session: requests.Session,
    ) -> AdRecord:
        """Convert a single SearchCreatives result entry into an AdRecord."""
        ad_id = item.get("2") or item.get("1", "unknown")
        advertiser = advertiser_name or item.get("12")
        content = item.get("3", {})

        first_seen = self._format_timestamp(item.get("6"))
        last_seen = self._format_timestamp(item.get("7"))

        image_url: str | None = None
        fmt: str | None = None
        surface: str | None = None

        # Direct image creative.
        img_html = content.get("3", {}).get("2")
        if img_html:
            image_url, (width, height) = self._extract_img_src_and_dims(img_html)
            fmt = "image"
            if width and height:
                if height > width * 1.5:
                    surface = "YouTube"
                elif width >= height:
                    surface = "Display"
                else:
                    surface = "Display"
            else:
                surface = "Display"

        # Deferred creative preview (often video / responsive ads).
        deferred_js = content.get("1", {}).get("4")
        if deferred_js and not image_url:
            preview_url = self._extract_preview_image_from_js(deferred_js, session)
            if preview_url:
                image_url = preview_url
                is_youtube = "ytimg.com" in image_url or "youtube.com" in image_url
                fmt = "video" if is_youtube else "image"
                surface = "YouTube" if is_youtube else "Display"

        # Fallback to the numeric format hint if we couldn't classify above.
        if fmt is None:
            fmt = {1: "image", 2: "image", 3: "video"}.get(item.get("4"), "unknown")
        if surface is None:
            surface = "Search" if fmt == "text" else "Display"

        return AdRecord(
            ad_id=str(ad_id),
            advertiser_name=advertiser,
            format=fmt,
            surface=surface,
            copy=AdCopy(),
            image_url=image_url,
            first_seen=first_seen,
            last_seen=last_seen,
        )

    def _fetch_ads_via_api(self, page: Page, advertiser_name: str | None) -> list[AdRecord]:
        """Fetch the full ad inventory through the SearchCreatives RPC."""
        domain = self._current_domain
        session = self._api_session_for_page(page)

        ads: list[AdRecord] = []
        seen_ids: set[str] = set()
        token: str | None = None
        total: int | None = None
        page_num = 0

        while True:
            page_num += 1
            payload = self._build_search_payload(domain, token, DEFAULT_PAGE_SIZE)
            logger.debug("SearchCreatives page %s payload: %s", page_num, payload[:200])

            try:
                resp = session.post(SEARCH_CREATIVES_RPC, data=payload, timeout=60)
                resp.raise_for_status()
            except requests.RequestException as exc:
                logger.error("SearchCreatives request failed: %s", exc)
                break

            try:
                data = resp.json()
            except json.JSONDecodeError as exc:
                logger.error("SearchCreatives response is not JSON: %s", exc)
                break

            items = data.get("1", [])
            if total is None:
                total = int(data.get("4", data.get("5", 0)))
                logger.info("SearchCreatives reports %s total ads.", total)

            logger.info("SearchCreatives page %s returned %s items.", page_num, len(items))

            for raw in items:
                record = self._parse_api_item(raw, advertiser_name, session)
                if record.ad_id in seen_ids:
                    continue
                seen_ids.add(record.ad_id)
                ads.append(record)

                if self.config.max_ads and len(ads) >= self.config.max_ads:
                    break

            if self.config.max_ads and len(ads) >= self.config.max_ads:
                logger.info("Reached configured max_ads limit: %s", self.config.max_ads)
                break

            token = data.get("2")
            if not token or not items:
                logger.info("No more SearchCreatives pages.")
                break
            if total and len(ads) >= total:
                logger.info("Fetched all reported ads.")
                break

            self._delay()

        return ads

    def _run_scrape_once(self, domain: str) -> ScrapeResult:
        """Single scrape attempt in a fresh browser context."""
        self._current_domain = domain
        context = self._create_context()
        page = context.new_page()
        result = ScrapeResult(domain=domain)

        try:
            logger.info("Navigating to %s", GOOGLE_ADS_TRANSPARENCY_URL)
            page.goto(GOOGLE_ADS_TRANSPARENCY_URL, timeout=60000)
            self._wait_for_stable_page(page)

            if self._looks_blocked(page):
                raise ScrapeBlockedError("Bot/CAPTCHA detected on homepage.")

            self._dismiss_overlays(page)

            results = self._search_advertiser(page, domain)
            if results is None or results.count() == 0:
                logger.info("No advertiser search results for %r.", domain)
                return result

            advertiser_name = self._select_exact_match(page, domain)
            if advertiser_name is None:
                return result

            result.advertiser = advertiser_name
            self._wait_for_stable_page(page)
            self._dismiss_overlays(page)

            if self._looks_blocked(page):
                raise ScrapeBlockedError("Bot/CAPTCHA detected after selecting advertiser.")

            ads = self._fetch_ads_via_api(page, advertiser_name)
            result.ads = ads
            logger.info("Extracted %s ads for %r.", len(ads), domain)
            return result
        finally:
            context.close()

    def scrape(self, domain: str) -> ScrapeResult:
        """Scrape Google Ads Library for a given domain.

        Retries once with a fresh browser context on bot/CAPTCHA detection.
        Raises ScrapeBlockedError on repeat failure.
        """
        normalized = _normalize_domain(domain)
        logger.info("Starting scrape for normalized domain: %s", normalized)
        self._start_browser()

        attempts = 0
        last_error: Exception | None = None
        while attempts < 2:
            attempts += 1
            try:
                return self._run_scrape_once(normalized)
            except (ScrapeBlockedError, ScrapeTimeoutError) as exc:
                last_error = exc
                logger.warning("Scrape attempt %s failed: %s", attempts, exc)
                if attempts < 2:
                    logger.info("Retrying with a fresh browser context.")
                    time.sleep(self.config.delay_seconds * 2)
            except Exception as exc:
                logger.exception("Unexpected error during scrape attempt %s", attempts)
                last_error = exc
                break

        self._stop_browser()
        if isinstance(last_error, ScrapeBlockedError):
            raise last_error
        if isinstance(last_error, ScrapeTimeoutError):
            raise last_error
        raise ScrapeBlockedError(f"Scraper failed after {attempts} attempts: {last_error}")

    def __enter__(self):
        self._start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop_browser()
        return False
