# Google Ads Library Scraper

A standalone Python module that scrapes the [Google Ads Transparency Center](https://adstransparency.google.com/) for a given advertiser domain, extracts structured ad records, and generates deterministic stats plus a marketing analysis.

## Features

- Playwright-based browser automation (sync API).
- Domain normalization.
- Advertiser search and exact-match selection.
- Pagination through ad cards until no more load.
- Structured extraction: ad ID, advertiser, format, surface, copy, image URL, date range.
- Bot / CAPTCHA retry with a fresh browser context; raises `ScrapeBlockedError` on repeat failure.
- Optional `max_ads` limit.
- Deterministic `stats.json` + LLM `analysis.md` with deterministic fallback.

## Current Limitations (v1)

- **Image ad copy:** Google Ads Transparency Center image creatives contain their copy inside the image itself. Extracting that text requires an external vision/OCR API. The scraper currently saves the image URL and attempts to describe it via the Kimi Code OAuth token, but vision support is not guaranteed with that token (falls back gracefully).
- **Video ads:** Detected and counted, but copy/audio is not extracted yet.
- **Text/Search ads:** Copy is extracted only when it is visible in the card preview; cards that require opening a detail view may return empty copy fields.
- **No results:** If the advertiser cannot be found or no ad cards render, the scraper exits cleanly with an empty inventory.

## Setup

1. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

2. Copy the example environment file and adjust as needed:

```bash
cp .env.example .env
```

3. Ensure you have a valid Kimi credentials file. By default the scraper looks at:

```
~/.kimi-code/credentials/kimi-code.json
```

Override with `KIMI_CODE_CREDENTIALS` in `.env`.

## Usage

```bash
python main.py example.com
```

Optional flags:

```bash
python main.py example.com --limit 50 --headless --output-dir ./output
```

- `domain` — advertiser domain or full URL.
- `--limit` — maximum number of ads to extract (0 = unlimited).
- `--headless` / `--no-headless` — control browser visibility.
- `--output-dir` — base directory for results.

## Output

Each run creates a timestamped subdirectory under `OUTPUT_DIR`:

```
output/
  example.com_20240805_120000/
    inventory.json
    stats.json
    analysis.md
```

- `inventory.json` — raw scraped ad records with IDs, formats, surfaces, image URLs, and copy fields.
- `stats.json` — deterministic counts by format/surface, date ranges, top CTAs, top display URLs, copy presence.
- `analysis.md` — LLM-generated marketing analysis (or deterministic fallback if the LLM call fails).

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HEADLESS` | `true` | Run browser in headless mode. |
| `DELAY_SECONDS` | `2.0` | Pause between interactions. |
| `MAX_ADS` | `0` | Maximum ads to scrape (0 = unlimited). |
| `OUTPUT_DIR` | `output` | Base output directory. |
| `KIMI_CODE_CREDENTIALS` | `~/.kimi-code/credentials/kimi-code.json` | Path to Kimi OAuth credentials. |
| `KIMI_BASE_URL` | `https://api.kimi.com/coding/v1` | Kimi API base URL. |
| `KIMI_MODEL` | `k3` | Model name for Kimi chat completions. |

## Exit Codes

- `0` — success or no ads found.
- `1` — scrape blocked, timeout, missing credentials, or unexpected error.

## Project Structure

```
google-ads-scraper/
├── src/
│   ├── models.py        # Shared AdRecord / ScrapeResult models
│   ├── config.py        # Config loader
│   ├── exceptions.py    # ScrapeBlockedError / ScrapeTimeoutError
│   ├── scraper.py       # Playwright scraper
│   ├── kimi_client.py   # Kimi API client
│   ├── inventory.py     # Inventory output + image enrichment
│   ├── stats.py         # Deterministic stats generation
│   └── analysis.py      # LLM-based analysis generation
├── main.py              # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Future Work

- Replace the Kimi Code OAuth vision fallback with a dedicated external vision/OCR API for true image copy extraction.
- Detail-view extraction for text/search ads to pull headline, body, CTA, and display URL from the card overlay.
- Video/audio transcription for YouTube/video ads.
- Structured advertiser-level summaries (themes, surface strategy, spend estimate proxies).
