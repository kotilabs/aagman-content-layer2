# LinkedIn Content — Founder Content Engine

An agentic workflow that turns signals + a founder's raw take into
publication-ready LinkedIn posts in his voice — then learns from what happens
to them. Built around a multi-agent pipeline, a lesson memory, and a
closed analytics loop.

The engine is **local-agnostic**: clone, add an API key, run setup, go.

---

## Quickstart

```sh
git clone <repo-url> && cd "LinkedIn Content"

npm install                 # playwright + ws for the signal scout
npx playwright install chromium

cp .env.example .env        # add ANTHROPIC_API_KEY or OPENAI_API_KEY
                            # (or skip: falls back to a locally installed kimi CLI)

python3 run.py setup        # guided first-run: browser + LinkedIn login
python3 run.py status       # should print READY
```

The first time you run any command, a one-time wizard walks you through the
LLM backend and browser/LinkedIn setup automatically.

Requires Python 3.8+, Node.js, and a Chromium browser (Arc, Chrome, Edge, or Brave).

---

## How it works — the agents

The workflow is a directed graph of small specialist agents. Each has a narrow
contract; artifacts flow between them as files; all state lives outside the
agents (ledger, lessons, seen-store), which is what makes the system
self-evolving without any model retraining.

```
SCOUT ──→ human picks signal ──→ TICKET (topic + founder's take)
                                     │
         THINK → CLARIFY? → RESEARCH? → WRITE → ELEVATE → JUDGE ⇄ revise → DE-AI
                                     │
                              approve / pushback (human gate)
                                     │
                              posted → ANALYTICS (metrics + visuals)
                                     │
                              LESSONS / EVIDENCE updated → next run is smarter
```

### Input side

**1. Scout** — scrapes Pulse by Zerodha (3-day window), ZeroHedge and
Armstrong Economics (14-day), filters junk (nav pages, promos, ad cards,
sponsored posts), dedupes against a persistent seen-store, ranks by
beat-keyword relevance, and writes a digest: title + age + source + link.
No LLM inside — ranking is inspectable keyword math.

**2. Intake** — creates a ticket (markdown + YAML frontmatter) holding the
topic and the founder's raw take. Hard rule: no real take, no ticket. The
engine never invents the founder's opinion.

### Production line

**3. Think** — reasons over the take before any writing: extracts every
distinct argument, names the post's purpose (what the reader walks away
with), marks load-bearing vs supporting points, decides one post or two,
picks a free-form shape tag (hybrids like `market-analysis + contrarian`
are allowed — no mold), selects only the moves from the category cards that
serve *this* take, and sketches structure + length. If the take is ambiguous
it stops and asks the founder clarifying questions instead of guessing.

**4. Research** — fires only when the material needs it (news/market topics).
Verifies facts, marks anything uncertain as UNVERIFIED rather than
hallucinating. Personal stories skip it entirely.

**5. Writer** — free-writes the truest version of the take: voice file +
take + think note + active lessons. No template is imposed — structure
emerges from the material. If the material is genuinely insufficient, it
replies NEEDS_INPUT with the specific question instead of fabricating.

**6. Elevate (editor)** — a separate pass with a different job: improve the
craft of what exists — rhythm, opening, close, transitions — without touching
substance. It calibrates against the exemplar bank (the actual top-scoring
posts from the 550-post study, used for flow only) and the weighted evidence
file (advisory).

**7. Judge** — six inspectors, each with one narrow job:
- **voice_fidelity** — does every sentence sound like the voice file?
- **ban_list** — tips, predictions, price targets, hype, P&L flexing: automatic block
- **coverage** — every load-bearing argument present; every claim traceable to take or research (the anti-fabrication guard)
- **clarity** — could the reader state the point after one read?
- **performance** — scores the draft against the study's findings; blocks only the four proven losers (question-opener, hashtag wall, text walls, engagement-bait CTA), reports everything else as advisory notes
- **pull** — does the opening earn the scroll-stop?

Blockers trigger a targeted revise loop (max 2), then it escalates to a human
instead of looping forever.

**8. De-AI** — the permanent final polish: strips AI writing patterns (binary
contrasts, fragment monotony, pull-quote lines, meta-narration, em dashes,
passive voice) while leaving facts, voice, and the line-beat layout untouched.

### Output & learning side

**9. Human gate** — `approve` ships the draft to `final/`; `pushback "<reason>"`
turns the objection into a lesson candidate.

**10. Analytics** *(built & validated, activates when posts are live)* — from
stored post links: an in-feed screenshot + visual description (media type,
above-fold text) plus the full View-analytics panel (impressions with
in/out-of-network split, members reached, profile viewers, followers gained).

---

## How it self-improves

Three loops at three timescales:

**Within a post** — the judge's revise loop. Each draft measurably improves
inside its own run.

**Within the experiment** — every pushback becomes a **lesson candidate**
(`memory/lessons.md`, tagged by source/category/stage). Activating one
(`lesson-activate <id>`) injects it into the writer's and judge's prompts on
every future run. Your taste compounds: one sentence of feedback permanently
changes how the engine writes. `lesson-retire` kills any lesson that misfires.

**Across experiments** — the analytics agent feeds outcomes back:
per-category scores against the founder's rolling baseline, per-format reads
(image vs text, hook above the fold), lesson reinforcement/retirement, and
the evidence file itself gets updated — the 550-creator prior is gradually
overridden by the founder's own account data.

Hard boundary: the engine **proposes**, humans **dispose**. It never rewrites
the voice file or the category cards on its own — identity doesn't drift.

---

## The knowledge base it was trained on

The engine's instincts come from a forensic analysis of **550 posts across 11
finance/startup creators**, each scored against its own creator's baseline
(the `linkedin-scraper/` subfolder is the tool that produced this corpus):

- `performance/evidence.md` — every finding with an effect size and a
  confidence tag (STRONG / DIRECTIONAL / WEAK): first-person hooks beat
  question-openers 131 vs 75; one sentence per line is universal in winners;
  personal stories outperformed everything (2.45× baseline); market analysis
  is the most-produced and worst-performing category (0.72×) unless it inverts.
- `performance/exemplars/` — the top 2–3 real posts per category, used by the
  editor for flow calibration (never copied).
- `categories/` — 14 cards rewritten as *thinking tools*, not templates:
  reader outcome → available moves with use-when/skip-when conditions →
  failure modes → a data-backed length prior.

---

## A sample run

A founder's take on SEBI's F&O expiry restructuring went through the pipeline:

**Think note** (abbreviated, `tickets/<id>.think.md`):

```
- ARGUMENTS: 6 distinct points extracted (volatility herding, two-day window,
  broker haircut, Korea rebuttal, identity reframe, participation risk)
- PURPOSE: reader leaves with an independent mental model — "risk reduction"
  is better understood as risk redistribution
- LOAD-BEARING: none of the six are disposable — they form a single chain
- SHAPE TAG: market-analysis + contrarian-opinion
- SELECTED MOVES: inversion opening, fact blocks, self-implication, verdict close
- LENGTH PLAN: 240–310 words (sized to argument count, not a template range)
```

**Final post** (after write → elevate → judge → de-AI):

> SEBI didn't make F&O safer. It just moved the fire around.
>
> From September, each exchange gets one weekly index expiry.
> NSE: Tuesday. BSE: Thursday.
>
> Bank Nifty, FinNifty, Midcap Nifty weeklies are gone.
> So retail speculative energy gets herded into Nifty 50 and Sensex.
>
> ...
>
> Verdict: this isn't a safer market.
> It's a smaller, more concentrated one.
> And smaller markets carry their own risks.

Every one of the founder's six arguments survived, in his logic order, with
zero invented facts — the earlier template-driven version of the same take had
amputated three of them. The judge's review file shows the revise trail
(`reviews/<id>.md`).

---

## Current experiment

`plans/experiment-01.json` (machine-readable tracker): a 4-week, 12-post
experiment on the founder's account — 8 brand posts from this engine + 4
product posts from a separate workflow (67/33 split).

- **4 boxes tested, 2 posts each:** personal story (trading scars), trader
  psychology (riding the opinion card), market/macro analysis, social critique.
  Two posts per box because a category can't be read from one post.
- **Within-box style variants:** scar story vs turning-point story;
  confession-style vs observer-style psychology — the experiment reads both
  topic and craft.
- **News-reaction is a floater:** real events preempt scheduled slots.
- **Conclusion:** open by design — weekly metrics collection (impressions +
  engagement via the analytics agent), a full read at the end of week 4, and
  the month-2 calendar written from what actually won.

Weekly plan files (`plans/week-01…04.md`) feed the `week` command, which
produces a brief combining the plan, the ledger, and active lessons.

---

## All commands

```sh
python3 run.py scout                          # news → signals/<date>-digest.md
python3 run.py ticket "topic" --take "raw take" [--category <slug>] [--source manual|planned|reactive]
python3 run.py draft <ticket-id>              # full pipeline: think → research → write → elevate → judge → de-AI
python3 run.py think <ticket-id>              # think pass only
python3 run.py research <ticket-id>           # research pass only
python3 run.py elevate <ticket-id>            # editor pass only
python3 run.py deai <ticket-id>               # de-AI pass only
python3 run.py review <ticket-id>             # print the judge's review
python3 run.py approve <ticket-id>            # draft → final/
python3 run.py pushback <ticket-id> "reason"  # → lesson candidate
python3 run.py lessons [--candidates]
python3 run.py lesson-activate <id>
python3 run.py lesson-retire <id>
python3 run.py week [--plan plans/plan.md]
python3 run.py add-source <url>               # test-scrape + interactively add a signal source
python3 run.py setup                          # first-run browser/LinkedIn setup
python3 run.py status                         # readiness check
```

## Layout

- `voice/ajit_voice_base.md` — who is speaking (persona, tone, lexicon, ban list)
- `categories/` — 14 principle-based category cards
- `performance/` — `evidence.md` + `exemplars/` (the 550-post knowledge base)
- `tickets/` → `drafts/` → `reviews/` → `final/` — post lifecycle
- `memory/ledger.jsonl` — append-only event log (every step, every run)
- `memory/lessons.md` — lesson store (candidate → active → retired)
- `signals/` — scout digests, seen-store, `sources.json`
- `plans/` — weekly plans + experiment tracker + generated briefs
- `scouts/` — Node/Playwright scraper used by the scout
- `linkedin-scraper/` — the standalone profile scraper that produced the corpus
- `FUTURE.md` — deferred work: add-source flow, analytics agent assembly,
  API backend swap, periodic corpus refresh, X expansion
