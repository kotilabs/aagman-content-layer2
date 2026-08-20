# linkedin-scraper

The standalone LinkedIn profile scraper that produced the 550-post corpus
behind `../performance/evidence.md` and the category cards — plus the raw-CDP
capture utilities built afterward for screenshots and post analytics.

Independent of the engine: its own `package.json`, its own `node_modules`.

## Setup

```sh
cd linkedin-scraper
npm install
npx playwright install chromium
```

## Auth

Two ways to get a logged-in LinkedIn session:

- **`node login.js`** — opens a headed browser; log in manually; the session
  is saved to `auth.json` (Playwright storage state). Used by `scraper.js`
  and `probe.js`.
- **`node capture-arc.js`** — attaches over CDP to your real, already-logged-in
  browser running with `--remote-debugging-port=9222` and captures the session
  from there. Preferred when LinkedIn bot-checks fresh Playwright profiles.

The `cdp-*.js` utilities skip `auth.json` entirely and drive the live CDP
browser directly over a raw websocket (`ws`).

## Commands

```sh
node login.js                              # one-time manual login → auth.json
node capture-arc.js                        # capture session from the CDP browser
node scraper.js profiles.txt [--max 50] [--headed]   # scrape profile posts → output/
node probe.js                              # dump candidate selectors from a live activity page
node merge.js                              # output/*.json → all-posts.json + all-posts.csv
node analyze.js                            # categorize posts, extract features, join engagement
node cdp-shot.js <post-url> <out.png>      # screenshot a post via raw CDP
node cdp-analytics.js <post-url> <out.png> # open "View analytics", screenshot the panel
node cdp-full.js                           # full CDP capture pass (posts + analytics)
```

`profiles.txt`: one LinkedIn profile URL or handle per line.

## Notes

- `auth.json`, `output/`, and all scraped data are deliberately not committed.
- The engine's own setup flow (`python3 run.py setup` at the project root)
  verifies the same CDP port these utilities attach to.
