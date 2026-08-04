"""Google Ads Transparency Center scraper.

Uses Playwright (sync API) to search an advertiser by domain, load its ad
library, paginate through ad cards, and extract structured AdRecords.
"""
from __future__ import annotations

import logging
import re
import time
from urllib.parse import urlparse

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

# Common selectors used by the Google Ads Transparency Center SPA. These are
# best-effort and grouped so the scraper can try alternatives.
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

AD_CARD_SELECTORS = [
    'creative-preview',
    'article',
    '[data-test-id*="ad-card" i]',
    '.ad-card',
    '.creative-card',
]

SHOW_MORE_SELECTORS = [
    'button:has-text("Show more")',
    'button:has-text("Load more")',
    'button:has-text("See more")',
    '[data-test-id*="show-more" i]',
    '[data-test-id*="load-more" i]',
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

    def _find_search_input(self, page: Page) -> None:
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

    def _search_advertiser(self, page: Page, domain: str) -> str | None:
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

        # Base name without TLD, e.g. groww.in -> groww
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

        # Require a reasonable match; do not fall back to help/search UI entries.
        if best_index < 0 or best_score < 10:
            logger.info("No strong advertiser match for %r; treating as no results.", domain)
            return None

        selected = results.nth(best_index)
        advertiser_name = (selected.text_content() or "").strip().split("\n")[0].strip()
        logger.info("Selecting advertiser: %s", advertiser_name)
        selected.click(timeout=10000)
        self._delay()
        return advertiser_name

    @staticmethod
    def _extract_card_data(card, index: int) -> dict:
        """Extract all ad data from a card in one JS evaluation for speed."""
        try:
            data = card.evaluate("""(el) => {
                // Deep query that pierces open shadow roots.
                function deepQuery(root, selector) {
                    const queue = [root];
                    while (queue.length) {
                        const node = queue.shift();
                        if (!node) continue;
                        if (node.matches && node.matches(selector)) return node;
                        let children = Array.from(node.querySelectorAll(selector));
                        if (children.length) return children[0];
                        const shadow = node.shadowRoot;
                        if (shadow) queue.push(...shadow.children);
                        if (node.children) queue.push(...node.children);
                    }
                    return null;
                }
                function deepQueryAll(root, selector) {
                    const found = [];
                    const queue = [root];
                    while (queue.length) {
                        const node = queue.shift();
                        if (!node) continue;
                        if (node.matches && node.matches(selector)) found.push(node);
                        const shadow = node.shadowRoot;
                        if (shadow) queue.push(...shadow.children);
                        if (node.children) queue.push(...node.children);
                        try {
                            found.push(...Array.from(node.querySelectorAll(selector)));
                        } catch (e) {}
                    }
                    return found;
                }
                function deepText(root) {
                    const texts = [];
                    const queue = [root];
                    while (queue.length) {
                        const node = queue.shift();
                        if (!node) continue;
                        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                            texts.push(node.textContent.trim());
                        }
                        const shadow = node.shadowRoot;
                        if (shadow) queue.push(...shadow.childNodes);
                        if (node.childNodes) queue.push(...node.childNodes);
                    }
                    return texts;
                }

                const result = {
                    ad_id: null,
                    advertiser_name: null,
                    format: null,
                    surface: null,
                    headline: null,
                    body: null,
                    cta: null,
                    display_url: null,
                    image_url: null,
                    first_seen: null,
                    last_seen: null,
                };

                // Ad ID from the first anchor href (deep query).
                const links = deepQueryAll(el, 'a[href*="/creative/"]');
                const anyLink = links[0] || deepQuery(el, 'a');
                if (anyLink) {
                    const href = anyLink.getAttribute('href') || '';
                    const m = href.match(/\/creative\/([^/?]+)/);
                    if (m) result.ad_id = m[1];
                }

                // Advertiser name.
                const advertiserEl = deepQuery(el, '.advertiser-name');
                if (advertiserEl) result.advertiser_name = advertiserEl.textContent.trim();

                // Format detection (deep query + heuristics).
                const cls = el.className || '';
                const rawTextLower = (el.textContent || '').toLowerCase();
                const hasVideoTag = !!deepQuery(el, 'video');
                const hasVideoIcon = rawTextLower.includes('videocam') || rawTextLower.includes('play_arrow');
                const hasVideoClass = /video|youtube|motion/i.test(cls);
                const hasVideo = hasVideoTag || hasVideoIcon || hasVideoClass;
                const imgEls = deepQueryAll(el, 'img');
                if (hasVideo) {
                    result.format = 'video';
                } else if (imgEls.length > 0) {
                    result.format = 'image';
                } else {
                    result.format = 'text';
                }

                // Surface inference from card classes and format.
                if (cls.includes('tallAllAds') || hasVideo) result.surface = 'YouTube';
                else if (cls.includes('wide')) result.surface = 'Display';
                else if (result.format === 'text') result.surface = 'Search';
                else result.surface = 'Display';

                // Image URL: prefer first meaningful image.
                for (const img of imgEls) {
                    const src = img.getAttribute('src');
                    if (src && !src.includes('data:')) {
                        result.image_url = src;
                        break;
                    }
                }

                // Copy extraction: try structured selectors first, then fall back to text lines.
                const headlineEl = deepQuery(el, '.headline, [data-test-id*="headline"], h1, h2, h3');
                const bodyEl = deepQuery(el, '.description, [data-test-id*="description"], .body');
                const ctaEl = deepQuery(el, '.call-to-action, [data-test-id*="cta"], .cta, button');
                const urlEl = deepQuery(el, '.display-url, [data-test-id*="url"], .url');

                if (headlineEl) result.headline = headlineEl.textContent.trim();
                if (bodyEl) result.body = bodyEl.textContent.trim();
                if (ctaEl) result.cta = ctaEl.textContent.trim();
                if (urlEl) result.display_url = urlEl.textContent.trim();

                // Fallback: collect all visible text lines and drop UI labels / code.
                if (!result.headline || !result.body) {
                    const allTexts = deepText(el);
                    const adNameLower = (result.advertiser_name || '').toLowerCase();
                    const lines = allTexts.filter(s =>
                        s.length > 1 &&
                        s.length < 300 &&
                        !/^(verified|advertisement|sponsored|ad\s*info|more info|report ad|about|videocam|play_arrow)$/i.test(s) &&
                        !/[@#;\.]{5,}/.test(s) &&
                        !s.toLowerCase().startsWith(adNameLower) &&
                        !s.toLowerCase().includes('gbar_') &&
                        !s.toLowerCase().includes('import url')
                    );
                    // Heuristic: first substantial line is often headline, next lines are body.
                    if (!result.headline && lines.length > 0) result.headline = lines[0];
                    if (!result.body && lines.length > 1) result.body = lines.slice(1, 5).join(' ');
                }

                // Date range.
                const allText = deepText(el).join(' ');
                const dateMatch = allText.match(/(\w{3,9}\s+\d{1,2},?\s+\d{4})\s*[-–]\s*(\w{3,9}\s+\d{1,2},?\s+\d{4})/);
                if (dateMatch) {
                    result.first_seen = dateMatch[1].trim();
                    result.last_seen = dateMatch[2].trim();
                }

                return result;
            }""")
            return data
        except PlaywrightError as exc:
            logger.warning("Failed to evaluate card %s: %s", index, exc)
            return {"ad_id": f"ad-{index:05d}"}

    def _extract_ads(self, page: Page, advertiser_name: str | None) -> list[AdRecord]:
        """Extract all visible ad cards, paginating until no more load."""
        ads: list[AdRecord] = []
        seen_ids: set[str] = set()
        last_count = -1
        stall_count = 0

        while True:
            if self.config.max_ads and len(ads) >= self.config.max_ads:
                logger.info("Reached configured max_ads limit: %s", self.config.max_ads)
                break

            cards = page.locator(", ".join(AD_CARD_SELECTORS))
            count = cards.count()
            logger.debug("Found %s ad cards on current page view.", count)

            for i in range(count):
                if self.config.max_ads and len(ads) >= self.config.max_ads:
                    break
                try:
                    card = cards.nth(i)
                    data = self._extract_card_data(card, i)
                    ad_id = data.get("ad_id") or f"ad-{len(ads):05d}"
                    if ad_id in seen_ids:
                        continue
                    seen_ids.add(ad_id)

                    copy = AdCopy(
                        headline=data.get("headline"),
                        body=data.get("body"),
                        cta=data.get("cta"),
                        display_url=data.get("display_url"),
                    )
                    record = AdRecord(
                        ad_id=ad_id,
                        advertiser_name=advertiser_name or data.get("advertiser_name"),
                        format=data.get("format"),
                        surface=data.get("surface"),
                        copy=copy,
                        image_url=data.get("image_url"),
                        first_seen=data.get("first_seen"),
                        last_seen=data.get("last_seen"),
                    )
                    ads.append(record)
                except Exception as exc:
                    logger.warning("Failed to extract ad card %s: %s", i, exc)
                    continue

            if self.config.max_ads and len(ads) >= self.config.max_ads:
                break

            # Try pagination.
            more_clicked = False
            for selector in SHOW_MORE_SELECTORS:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=2000):
                        button.click(timeout=10000)
                        self._delay()
                        more_clicked = True
                        break
                except PlaywrightError:
                    continue

            if not more_clicked:
                # Scroll to bottom to trigger infinite scroll if present.
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self._delay()

            # Detect pagination stall.
            if len(ads) == last_count:
                stall_count += 1
                if stall_count >= 3:
                    logger.info("No new ads loaded after %s attempts; stopping pagination.", stall_count)
                    break
            else:
                stall_count = 0
            last_count = len(ads)

        return ads

    def _run_scrape_once(self, domain: str) -> ScrapeResult:
        """Single scrape attempt in a fresh browser context."""
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

            ads = self._extract_ads(page, advertiser_name)
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
