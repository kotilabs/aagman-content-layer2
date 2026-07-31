# HARNESS_STATUS.md — Aagman Harness build handover

**Status:** Phases 0–6 complete and committed. **Paused at Phase 7** (live runs —
human-in-the-loop, needs a valid Anthropic key). Repo: `~/Documents/aagman-harness`
(separate git repo, local commits only, **no remote** — nothing pushed).
Date: 2026-07-03. Source of truth for the build: `AAGMAN_HARNESS_FINAL-5.md`.

---

## What it is

A generic agentic loop — **SENSE → IDEATE → CREATE → JUDGE → PUBLISH → LEARN** — with
a domain-agnostic core (`harness_core/`) and pluggable domains. Two domains shipped
(**content**, **engineering**) plus a **distribution** stub proving extensibility.
Phase-gated, resumable, loop-mode, instrumented for self-evolution from day one.

- `harness_core/` — the engine. ~2,200 LOC production. **Zero domain logic** (grep-enforced).
- `harness_content/` — SEBI-safe educational content on aagman-content-layer2 voice.
- `harness_engineering/` — RCA → fix → PR against aagman-v2, gated by its real test suite.
- `harness_configs/` — `models.yaml` (single source of truth for models) + one
  `<domain>_config.py` per domain (content, engineering, distribution).

## What runs today (verified)

- **173 tests green** (TDD throughout; core + both domains + extensibility).
- **Genericity proven**: no `sebi|linkedin|github|content` in `harness_core/*.py`
  (beyond the benign litellm `role/content` API key); no model strings outside
  `models.yaml`; the same `ComplianceGate` class enforces `SEBI_RULES.md` and
  `RISK_RULES.md`, differing only by rules file; all three domains load through one
  `GenericHarness`.
- **700 Day-0 lessons seeded** into namespaced memory from BOTH repos + local
  non-git session learnings (engineering sense 206 / ideate 380 / create 37 /
  judge 39 / gate 10; content create 15 / judge 13). The harness never boots blind.
- **Live wiring proven (real LLM calls, not mocks):**
  - Content: inbox brief → real on-brand educational draft (gpt-4o) → `brief`
    HumanGate fires + parks → approve → parallel create (text + image, disclosure
    prepended) → parks at the compliance panel. Real gate fire/park/resume,
    work-item state machine + audit trail, real generation.
  - Engineering: `IssueListener` fetched **50 real open issues** assigned to
    ajitk2003 → RCA attempted → fault-isolation contained the Anthropic-auth
    failure on every item (marked `failed` + audited the exact error) → loop
    finished clean (no crash). Real gh sense + dedup + fault containment.

## Costs so far

Trivial — a few real gpt-4o calls across the dry runs (~$0.5 total, order of
magnitude). Budget guard is wired at **$5.00/day** (`DAILY_BUDGET_USD`), auto-writes
`PAUSED` and pings Telegram once on breach. Cost ledger: `logs/cost_log.jsonl`
(gitignored). Every model call logs tokens + cost and records against the guard.

---

## BLOCKERS (what Phase 7 needs from Ajit)

1. **A valid `ANTHROPIC_API_KEY`.** RCA verified: the ambient Anthropic key errors
   `authentication_error: invalid x-api-key`, so every Claude 4.x model fails.
   Chains with a gpt-4o fallback survive (content ideate/create), but the
   **Anthropic-only panels** — `judge_panel` and `compliance_panel` = `[sonnet, opus]`,
   and the `engineering.ideate` override `[opus, sonnet]` — cannot run. This blocks
   content compliance/judge and engineering RCA. **It is a config/secret issue, not
   code** (offline unit tests prove the panel + RCA logic). Put a valid key in `.env`.
   - *Optional resilience (your call):* add `gpt-4o` as a last fallback to
     `judge_panel`, `compliance_panel`, and `engineering.ideate` in `models.yaml`
     (one line each). Every other chain already has a cross-provider fallback; these
     three do not. That would also let the harness run live on OpenAI alone.
2. **aagman-v2 test environment** for the engineering TestGates (`run_all.sh` needs
   `uv`, `dotenvx`, `.env`, and the DB per aagman-v2's setup). The gates are wired
   with the **real** commands (see `harness_engineering/TEST_HARNESS.md`); they just
   need the target repo runnable.
3. **Channel creds** (optional) for real content posting; Phase-1 publish writes to
   `outbox/{channel}/` and manual copy-paste is an acceptable Phase-1 publish.

## Phase 7 — what remains (paused, needs the above + your approvals)

- Content: process ONE real brief end-to-end; you approve `brief` + `publish` via
  Telegram/files; artifact lands in `outbox/` with disclosure; `rules_version` in audit.
- Engineering: process ONE real assigned issue; you approve the `plan`; fix passes the
  scoped TestGate; PR raised on `ajit/fix-{n}`; amit-kotidev assigned. (Raises a REAL
  PR — outward-facing, so it waits for your go.)
- ~~Activate self-evolution scoring~~ **DONE** — see "Self-evolution ACTIVE" below.
- Kill-switch drill (arm mid-cycle → clean stop → disarm → resume). Mechanics are
  unit-tested; the live drill is Phase 7.
- Persistent mode: `bash harness_core/run.sh <domain>` under tmux; morning digest cron.

## Self-evolution ACTIVE (scoring flipped on)

The lesson columns (`helped`/`misled`/`confidence`) and `attribute()` shipped in Phase 1;
they are now **wired into the live loop**. Generic mechanism (no domain logic in core):
- Agents stamp **provenance** — `idea.meta['relied']` / `artifact.meta['relied']` =
  `[[domain, step, id], ...]` for the lessons a cycle actually recalled (`_recall` in
  the engineering agents; RCA records `sense`+`ideate`, CREATE carries them forward and
  adds `create`).
- `GenericHarness._attribute()` runs in `_learn`: on a terminal outcome it credits
  (`published`) or blames (`rejected`) exactly those lessons; parked/`incomplete`/`failed`
  cycles score nothing (not the lesson's fault). Fixed a latent bug — `published` was
  missing from the credit set, so success would have *blamed* its lessons.
- `top_k` already ranks by relevance × confidence, so proven lessons surface and
  misleading ones sink (auto-retire < 0.3 after ≥ 5 uses).

Proven live (offline demo): a seeded lesson moved `confidence 0.50 → 1.00` over two
`published` cycles, then `→ 0.67` after a `rejected` one. **Both domains** stamp `relied`
(engineering: `sense`+`ideate`+`create`; content: `ideate`), so both self-evolve. 13 TDD
tests (`test_self_evolution.py` across core + engineering + content, incl. end-to-end
`_learn` proofs). *Judge-step lessons aren't attributed yet (verdict isn't carried to
`_learn`); a minor follow-up.*

## Seed → prompt wiring closed (coding agents now repo-aware)

Audit finding: two of the highest-value engineering corpora were *seeded but never
read into any prompt*. Fixed (TDD, `tests/test_fix_context.py`):
- **CREATE** (`CodeFixAgent`) now recalls `fix_success_patterns` ("similar fixes
  that landed") and the routed entry file's **co-change siblings** (blast-radius)
  and injects both into the fix task — was nuance-blind before.
- **IDEATE** (`RCAAgent`) now recalls **similar past issues** from the 206-exemplar
  `classifier_examples` corpus (previously orphaned in `engineering/sense`).
- **Routing** now trusts the model's *stated* `ENTRY_FILE:`/`LAYER:` (the RCA prompt
  already demands them) instead of only 4 hardcoded risk keywords; keyword route is
  the fallback. Any non-risk issue can now route to a real layer/entry file → the
  recurrence/architectural-review flag also fires beyond the risk layer.

Still not wired into prompts (Phase-2 backlog): full PR **diffs** as retrievable fix
exemplars, and the older-PR/older-issue window (see distillation coverage below).

## Routing eval + retrieval router (built, measured, wired)

**The measurement backbone.** `harness_engineering/evals/routing_eval.py` scores
routing against merged-PR ground truth (the files a merging PR touched reveal the
true 2-seg area). Deterministic, **no LLM budget**. PR→issue linkage uses this repo's
trailing `(#N)` title convention (the GitHub closingIssues graph is unused). Rebuild
the index from real PRs: `python3 -m harness_engineering.evals.routing_eval build 400`
→ `report`.

**The retrieval router** (`harness_engineering/route_index.py`, `RouteIndex`) is a
token-Jaccard k-NN over a committed index of real `issue→area,entry_file` pairs
(`distilled/route_index.json`, **96 unique-issue records** from an 800-PR window,
title+snippet → redaction-safe; deduped by issue, strict-majority area labels). Wired
into `RCAAgent` as the pre-route prior (`ROUTE_K=1`): retrieval first, keyword
`_route_layer` fallback, model's STATED `ENTRY_FILE:` still wins.

**Honest numbers (deduped 96-issue index, 4-fold CV, leakage-free):**
| Router | CV area accuracy |
|---|---|
| keyword `_route_layer` (4 risk keywords) | **0%** |
| majority-class baseline (always `backend/src`) | 26.0% |
| retrieval nn k=1 (production) | **36.5%** (per-fold 25–42%) |

Retrieval clears the majority-class bar by ~10pp on genuinely leakage-free held-out
issues (all 96 test items are <0.9 similar to their nearest train neighbour). `k` is
within noise (k∈{1,2,3,5} span 34–36.5%). Rebuild: `routing_eval build 800` → `report`.

> ⚠️ **Correction (adversarial-verify caught it).** An earlier internal figure of "45%"
> was **wrong** — inflated by (1) train/test **leakage**: the index had duplicate rows
> for issues closed by multiple PRs (160 rows / 110 issues), so identical issue_text
> straddled the split; (2) a **label bug** — `"test" in path` matched "back**TEST**er",
> mislabelling backtester PRs; (3) a **cherry-picked fold** (45% was the max of 15
> splits; k=5 tied k=1 under CV). Fixes: dedup by issue_number, a real test-path regex,
> strict-majority labels, and 4-fold CV reporting with a leakage-free generalization
> column. The honest number is ~36%. **Lesson logged: always CV + group-dedup + verify
> before quoting an eval number.**

**Embedding retrieval — TESTED, did NOT help (negative result).** `embeddings.py`
(OpenAI `text-embedding-3-small`, disk-cached) + `VectorRouteIndex` (cosine k-NN) +
`routing_eval embed [k]`. On the identical leakage-free CV, embedding cosine **loses to
token-Jaccard at every k** (k=1: 31.2% vs 36.5%; k=3: 33.3% vs 34.4%; k=5: 28.1% vs
35.4%). The routing signal here is **lexical/jargon** (component names, error strings,
`risk_blocked`, tickers) — exact rare-token overlap Jaccard rewards and embeddings smear
into topicality. So embeddings are NOT wired into production (would add cost+latency+dep
for worse accuracy); token-Jaccard stays. The `evaluate_embed` tool remains for re-testing
if the index ever carries richer text than title+snippet.

**Coverage ceiling:** 561/800 merged PRs carry no `#ref` (the `(#N)` title convention
covers ~30%); branch names are descriptive slugs, not issue numbers — unrecoverable
without corrupting ground truth. **What's actually left (the similarity-metric lever is
tapped out at ~36% for both lexical and semantic):** in production the retrieval is only
a *prior* — the RCA model's STATED `ENTRY_FILE:` is the real router — so the higher-value
work is measuring/improving the LLM route and activating outcome-scored self-evolution
(`attribute()`), not squeezing the token-NN prior further.

## Recurrence → architectural-review escalation (built)

When an *area* keeps needing fixes, the harness stops proposing silent patch N+1 and
flags the plan for a design review. `FixMemory` logs every fix outcome into an
`engineering/fixlog` namespace tagged by area (first two path segments of the routed
entry file). `RCAAgent`, at ideate, reads that history for the routed area; if
`total ≥ 3` **or** `reopened/bounced ≥ 2`, it stamps `plan["architectural_review"]=True`,
prepends an "⚠️ ARCHITECTURAL REVIEW RECOMMENDED" banner to the plan, and feeds the
recurrence into the RCA prompt so the model weighs a structural fix. The banner
surfaces at the existing `HumanGate("plan")` — the human makes the patch-vs-rearchitect
call. v1 limits (documented, easy to extend): count-based (no time window yet); area is
a 2-segment path key; `unknown`/unrouted areas are never flagged.

## Known gaps / deferred (Phase-2 backlog — intentionally NOT built)

Dynamic model router (stub only today) · recursive steps (schema present, OFF) ·
semantic/vector memory (current recall is keyword relevance × confidence) · video
generation · Instagram/YouTube publishing · the weekly PROMOTER agent + self-accuracy
trend digest (need scored lessons from a couple of live weeks first) · per-area
dynamic TestGate scoping (today: `--fast` inner vs full outer) · the 22-check
verify.sh (does not exist in aagman-v2 — see TEST_HARNESS.md).

## How to run

```bash
cd ~/Documents/aagman-harness
# put real keys in .env first (cp .env.example .env; fill ANTHROPIC/OPENAI/GOOGLE + TELEGRAM)
PYTHONPATH=. ./venv312/bin/python3 harness_core/run.py --domain content --dry-run --once
# drop a brief first: echo "..." > inbox/my_brief.md   (or a {"brief","channel"} .json)
# engineering: --domain engineering  (polls real gh issues; needs a valid Anthropic key for RCA)
# resume/full loop: bash harness_core/run.sh <domain>   ·   stop: touch KILL
PYTHONPATH=. ./venv312/bin/python3 -m pytest harness_core/tests harness_content/tests harness_engineering/tests -q
```

Rebuild Day-0 memory anytime: `PYTHONPATH=. ./venv312/bin/python3 seed_memory.py`.
Resume the build from `PROGRESS.md` (per-phase notes + the exact blocker state).

## Future work / things to be done

- **India news scout (wired into main runner):** `harness_content/scouts/india_news_scout.py` runs the India-news signal prompt and writes `signals/<date>-india-news-digest.md`. It is callable from the Layer 2 orchestrator via `python run_layer2_full.py india_news_scout` and appears as a selectable digest source in `select_signal`. The prompt currently accepts Tier 1/Tier 2 sources by instruction, but the enforcement is soft. Future work: add a source validation step (post-scout) that flags any candidate citing Tier 3 sources before it reaches selection; consider wiring a web-search tool directly into the scout so sources are fetched and cited automatically rather than relying on the LLM's recall.

- **Signal selection now supports multiple digest sources:** `python run_layer2_full.py select_signal` lists every digest that exists for the date (`combined`, `macro`, `india_news`, `x`, `reddit`) and asks you to pick a `digest_source` plus a `signal_id`. This lets you start the harness from any scout lens without cross-scout ranking or automatic merging.

- **Reddit Scout agent (wired into main runner):** `harness_agents/reddit_scout_agent.py` clusters posts from `r/IndianStockMarket`, `r/DalalStreetTalks`, `r/IndianStocks`, `r/IndianStreetBets`, and `r/MutualfundsIndia`. It is now callable directly from the Layer 2 orchestrator via `python run_layer2_full.py reddit_scout`. The cluster output is converted into a digest file (`signals/<date>-reddit-digest.md`) that `select_signal` can read alongside macro, India-news, and X digests. You can still run it standalone with `PYTHONPATH=. ./venv/bin/python harness_core/run.py --domain reddit_scout --once` or `reddit_cluster.py fetch --subreddits ... --date ...`. It sorts each subreddit by **hot** and **new**, fetches full post text, and clusters them by theme. A 20-second pause between subreddits was added to avoid rate-limit failures. The agent supports a direct OpenAI-compatible LLM path via `.env` keys `OPENAI_COMPATIBLE_API_KEY`, `OPENAI_COMPATIBLE_BASE_URL`, and `LLM_MODEL`; DeepSeek (`deepseek-chat`) is configured and tested. Provider order: `OPENAI_API_KEY` → `OPENAI_COMPATIBLE_API_KEY`+`OPENAI_COMPATIBLE_BASE_URL` → manual bridge fallback.

  **LLM evaluation notes for clustering:** Clustering is a good, cheap benchmark for model selection before using a model for long-form drafting. Key criteria, in order of importance: cluster quality (themes specific, posts actually belong together), noise handling (does the model over-use an "Other / Noise" bucket?), format adherence, ticker/theme recall, cost, availability from India, and latency. Current default is **DeepSeek `deepseek-chat`** — cheap, fast, reachable from India, but slightly aggressive on the "Other / Noise" bucket and occasionally verbose. Alternatives to test: **OpenAI `gpt-4o-mini`** (stronger instruction following, less over-noising, better ticker extraction, more expensive); **`gpt-4o`** (best quality, overkill cost); **Kimi/Moonshot** (non-US option, availability/pricing from India unclear); **local models** (privacy win, usually worse quality/speed). Suggested workflow: run the same raw post set through 2–3 models, score 1–5 on the criteria, track cost/latency, pick the cheapest model that produces clusters you trust, and re-evaluate quarterly. Open questions: whether DeepSeek v3 reduces over-noising; whether a two-stage prompt (extract tags → cluster) improves quality; whether to reassign borderline noise posts to existing clusters post-hoc.

- **X home-feed scout agent (wired into main runner):** `harness_agents/x_scout_agent.py` scrolls the logged-in user's X home feed via `browser-use` (same stack as Reddit), extracts ~60 tweets, uses an LLM to screen them for relevance to Indian finance/markets, expands the selected ones by opening their permalinks, and clusters the result. It is now callable directly from the Layer 2 orchestrator via `python run_layer2_full.py x_scout`, which converts clusters into a digest (`signals/<date>-x-digest.md`) readable by `select_signal`. You can still run it standalone with `PYTHONPATH=. ./venv/bin/python harness_core/run.py --domain x_scout --once` or `x_cluster.py fetch --date ...`. Requires the user to be logged in to X in the browser profile. No API cost, but dependent on browser session. Future work: consider shifting to an X MCP server (e.g., TwitterAPI.io or official X API) for a more durable, higher-throughput approach that can fetch more data without browser-session fragility; test selector robustness across X UI changes; add a manual relevance gate so the human picks which tweets to expand; evaluate whether expanding threads (vs. single tweets) improves cluster quality.

- **Postiz analytics loop (deferred):** Once Postiz is self-hosted on a VPS and used as the publishing layer, build a 14-day analytics job that reads Postiz post IDs from publish receipts, fetches per-post and per-platform metrics via the Postiz API (`/public/v1/analytics/post`, `/public/v1/analytics/platform`), normalizes performance by surface, analyzes patterns, and — after human review — writes approved patterns into `AgentMemory` so scouts, research, and writer agents recall them. This is intentionally deferred until Postiz is live; until then, lessons should be derived from basic analytics of initiatives already carried out.

- **Analytics agent design (under construction / prompt drafted):** A first-draft prompt is at `harness_content/prompts/analytics_agent.md`, but the whole analytics layer is still being designed. The analytics agent will eventually have three separable parts: (1) a **collection layer** that fetches normalized metrics from Postiz (and later other sources), (2) an **analysis layer** that compares performance, surfaces patterns, and proposes lessons, and (3) an **experiment layer** that turns uncertain patterns into ranked, tracked experiments. The analysis prompt should be customizable per review cycle. A useful future enhancement: for each published post, also capture the actual rendered asset (image/screenshot), write a short description of what it is, and feed both the visual description and the metrics into the analyzer so it can learn which creative formats, hooks, and visual structures perform best. The prompt is a starting point and needs iteration once real data flows through it.

  **First simulation already run:** We fed the analytics agent a one-off batch of real CSV exports — Substack email stats + traffic sources, LinkedIn company-page post metrics, and a handful of screenshots of top-performing posts. The agent surfaced the same outlier pattern we had spotted manually (a single-image rupee–equity infographic on LinkedIn reached ~10× median impressions) and proposed two concrete experiments: (a) a 3–4 week India-market format test comparing single-image infographics vs. carousels vs. short text-first posts, and (b) a topic test pitting India-market angles against global-macro angles. These are logged in `experiments/2026-07-31-india-infographic-vs-carousel.md`. This proved the analysis prompt can turn raw CSVs into testable hypotheses, but it is still a manual, one-off run — not an automated pipeline.

- **Experiment loop (under construction / needs proper design):** This is a rough sketch, not a finished system. The idea is that analytics should produce not only lessons but also a ranked backlog of experiments. Each experiment would be logged with hypothesis, variant A, variant B, surface, primary metric, minimum sample, effort, and expected impact. The operator would select which experiments to run; the harness would track them in `experiments/` (template at `experiments/experiment_template.md`) and, when the next analytics cycle runs, match results back to the experiment. Only experiments that reach their minimum sample and show a consistent effect would become lessons written to `AgentMemory`. The matching logic, prioritization scoring, and handoff from analytics to experiment log still need to be designed and built.

- **Basic analytics observation → controlled experiment (in progress):** Early LinkedIn data from the company page (94 followers, 11 organic posts) is too thin to write durable lessons. One outlier stands out — a single-image infographic on the rupee–equity divergence reached 1,208 impressions, roughly 10× the median post. Carousels (China two-speeds, gold export) showed high engagement rates (13–17%) but low reach. Text-heavy posts with a Substack link preview performed weakest. However, the sample is heavily skewed toward global macro topics and mixed formats. Rather than storing these as lessons now, the next step is a 3–4 week controlled experiment: run India-market-focused content across single-image infographics, carousels, and short-copy posts, then compare format-vs-format and topic-vs-topic before writing approved patterns into `AgentMemory`. Substack remains too early to judge.
