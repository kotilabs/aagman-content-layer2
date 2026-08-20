# Ajit's LinkedIn Post-Writing Engine

A Python CLI (stdlib only, no pip deps) that turns a topic + the founder's raw
take into a publication-ready LinkedIn post, in Ajit's voice.

## Quickstart

```sh
git clone <repo-url> && cd ajit-linkedin-engine

npm install                 # playwright + ws for the signal scout
npx playwright install chromium

cp .env.example .env        # then add ANTHROPIC_API_KEY or OPENAI_API_KEY
                            # (or skip: falls back to a locally installed kimi CLI)

python3 run.py setup        # detect browser, attach CDP :9222, verify LinkedIn login
python3 run.py status       # should print READY
```

Core commands:

```sh
python3 run.py scout                          # scrape news sources → ranked signal digest
python3 run.py ticket "topic" --take "your raw take"
python3 run.py draft <ticket-id>              # think → research → write → elevate → judge → de-AI
python3 run.py pushback <ticket-id> "what's wrong with it"
python3 run.py lessons [--candidates]
python3 run.py week                           # weekly brief from plans/plan.md
python3 run.py approve <ticket-id>            # ship draft → final/
```

Requires Python 3.8+, Node.js, and a Chromium browser (Arc, Chrome, Edge, or
Brave). `ticket`, `lessons`, `lesson-*`, `review`, `approve`, and `pushback`
work with no API key and no browser.

## Pipeline

1. **Intake** — `ticket` creates a markdown ticket (YAML frontmatter) in `tickets/`.
2. **Classify** — if the ticket's category is `auto`, the LLM picks one of the
   14 category cards in `categories/`, by post *purpose*, not surface ingredients.
3. **Think/shape** — `think` (or the start of `draft`) runs one analysis pass:
   it extracts the take's arguments, defines the post's purpose, picks a
   free-form shape tag (hybrids allowed), selects 2-4 moves from the relevant
   cards, and sketches structure + length. Written to `tickets/<id>.think.md`.
4. **Research** — when the think note says RESEARCH: yes, `engine/research.py`
   answers its research questions with verified facts (uncertain ones marked
   UNVERIFIED) into `tickets/<id>.research.md`. If the think note instead
   outputs CLARIFY questions, the pipeline stops and asks the founder.
5. **Write** — `engine/write.py` free-writes from the voice file, the think
   note, the take, optional research, and active lessons. If the material is
   insufficient the writer replies NEEDS_INPUT.
6. **Elevate** — `engine/elevate.py`, a world-class editor pass: improves
   rhythm, pacing, opening, close, and transitions using exemplar top posts
   (flow only) and performance evidence. Substance never changes.
7. **Judge** — 6 sequential LLM lenses (voice fidelity, ban list, coverage of
   load-bearing arguments, clarity, performance, pull). Blockers trigger an
   automatic revise loop (max 2 loops), then it's left for human review in
   `reviews/`.
8. **De-AI** — `engine/deai.py`, the permanent final polish: strips AI
   writing patterns (binary contrasts, fragment machine-gunning, pull-quotes,
   meta-narration, em dashes, passive voice…) while preserving facts, voice,
   and one-beat-per-line readability. Runs even when the judge needs a human.
9. **Human** — `approve` ships the draft to `final/`; `pushback "<reason>"`
   records the objection as a lesson candidate.
10. **Learn** — lesson candidates can be activated (`lesson-activate`) and then
    apply to every future draft for that category (or all).
11. **Weekly** — `week` reads `plans/plan.md`, the ledger, and active lessons,
    and writes a week brief to `plans/<date>-week-brief.md`.

Every step is logged to `memory/ledger.jsonl`.

## LLM backend

Set one key in `.env` (see `.env.example`) or in your environment:

```sh
ANTHROPIC_API_KEY=...   # uses claude-sonnet-4-5
# or
OPENAI_API_KEY=...      # uses gpt-4o
```

If neither is set, the engine falls back to the local `kimi` CLI.

## Browser setup (for LinkedIn-touching components)

`python3 run.py setup` once, then `python3 run.py status` to verify.

v1 supports **detect-and-attach only**: it finds an installed Chromium browser
(Arc / Chrome / Edge / Brave / Chromium), attaches to a running instance that
already exposes `--remote-debugging-port=9222` (it never relaunches your
browser), or launches it with that port when needed, then verifies the
LinkedIn session via the raw CDP `/json/*` endpoints. The result is cached in
`config.json`. Any future LinkedIn-touching component (analytics, profile
scraping) must call `engine.browser_setup.check_ready()` first and abort with
the returned reason unless it is `True`. The signal scout does NOT touch
LinkedIn and needs no setup — but it does need `npm install` (its Playwright
lives in the project's own `node_modules`).

## All commands

```sh
python3 run.py ticket "F&O expiry day discipline" --take "most losses happen in the last 2 hours" [--category 05-market-business-analysis] [--source manual|planned|reactive]
python3 run.py think <ticket-id>          # think/shape pass only → tickets/<id>.think.md
python3 run.py research <ticket-id>       # research pass only → tickets/<id>.research.md
python3 run.py draft <ticket-id>          # full pipeline → drafts/<id>.md + reviews/<id>.md
python3 run.py elevate <ticket-id>        # editor pass alone on an existing draft
python3 run.py deai <ticket-id>           # de-AI pass alone on an existing draft
python3 run.py review <ticket-id>         # print the judge's review
python3 run.py approve <ticket-id>        # draft → final/
python3 run.py pushback <ticket-id> "too hypey, no numbers"
python3 run.py lessons [--candidates]
python3 run.py lesson-activate <id>
python3 run.py lesson-retire <id>
python3 run.py week [--plan plans/plan.md]
python3 run.py scout                      # news → signals/<date>-digest.md
python3 run.py add-source <url>           # test-scrape + interactively add a source
python3 run.py setup                      # first-run browser/LinkedIn setup
python3 run.py status                     # readiness check
```

## Layout

- `voice/ajit_voice_base.md` — who is speaking (tone, bans)
- `categories/` — 14 writing-principle cards (structure + moves)
- `performance/` — `evidence.md` (what outperformed across 550 posts) + `exemplars/` (top posts per category)
- `tickets/` → `drafts/` → `reviews/` → `final/` — post lifecycle
- `memory/ledger.jsonl` — append-only event log
- `memory/lessons.md` — lesson store (candidate/active/retired)
- `signals/` — scout digests, seen-store, `sources.json`
- `plans/` — weekly plan + generated week briefs
- `scouts/` — Node/Playwright scraper used by the scout
- `linkedin-scraper/` — the standalone profile scraper that produced the 550-post corpus
