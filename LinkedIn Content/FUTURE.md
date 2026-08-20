# Future Improvements — Ajit LinkedIn Engine

Ideas deliberately deferred. Each is designed, not built.

## 1. Add-source flow for the scout
Let the user add a new signal source without code changes.
- `run.py add-source <url>` → test-scrapes the URL with Playwright, prints a
  demo table of ~10 items (title, date, link), user approves interactively,
  source lands in `signals/sources.json` with a chosen cutoff window.
- Scout reads sources.json instead of a hardcoded list.
- Reject cleanly when a site can't be scraped (JS-heavy, blocked, 0 items).
- Started once, stopped — spec lives here.

## 2. Scout upgrades
- Visit each article page to recover dates ZeroHedge doesn't show on cards.
- Same-day digest runs append instead of overwrite.

## 3. First-run setup + portability (REQUIRED before anyone else runs this)
The engine must not assume a specific machine or browser.
- `run.py setup` flow: detect installed Chromium browser (Arc, Chrome, Edge,
  Brave via OS-specific paths) → launch it with the CDP debug port → open
  LinkedIn and CHECK LOGIN STATE → if logged out, notify the user and wait
  while they log in in that window → confirm session is live → write
  `config.json` (browser found, port, login verified timestamp).
- Every LinkedIn-touching component (profile scraper, analytics agent,
  anything future) checks setup state before running. Session dead or
  missing → stop and tell the user to re-run setup. Never scrape the
  logged-out version and produce garbage.
- v1 limitation, stated plainly: detect-and-attach only. Self-managed
  Playwright profile fallback and a wider browser matrix come later.
- Everything else stays portable: relative paths, env-var LLM backend,
  config-driven browser.

## 4. Analytics agent (end-of-experiment)
Design agreed, not built. Drives the user's own logged-in browser (via the
setup flow in #3) to his profile, collects per-post metrics incl.
impressions, screenshots each post, writes a visual description per post
(media type, above-fold text, visual density). Joins with the engine's
ledger/tracker (category, variant, hook, length) into
`analysis/<date>-review.md`. Read-only, gentle pacing, unmatched posts
logged as missing never guessed. Feeds the week-4 review.

## 5. API backend swap
Move engine LLM calls from kimi CLI to a real API (Anthropic/OpenAI/Moonshot)
— kills subprocess stall risk, enables parallel judge lenses (~15min → ~2min runs).

## 6. X (Twitter) expansion
Second surface after LinkedIn experiment concludes.

## 7. Periodic corpus refresh
Re-run the LinkedIn profile scraper (see `linkedin-scraper/`) on the creator
set every few months, re-derive category stats/evidence, and diff against the
current `performance/evidence.md` to detect platform drift — what's stopped
working, what's new. The scraper output feeds the evidence file; the engine
reads whatever is current.
