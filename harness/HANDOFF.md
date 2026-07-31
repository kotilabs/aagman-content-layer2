# HANDOFF — Usage-Driven Prioritization workstream

For any Claude Code session picking this up. Read this first, then
`docs/USAGE_PRIORITIZATION.md` for the capability detail and `PROGRESS.md` /
`HARNESS_STATUS.md` for the wider harness.

**Branch:** `feat/usage-driven-prioritization` (off `main`; the 5 feature commits below
are shared history on both).

## What this workstream is

The engineering harness now turns **real aagman-v2 product usage** into a
**token-budget-fitted bug/feature priority queue**. It reads the live NL-interaction
tables, learns per-domain usage weights + personas, scores the open-ticket backlog by
`severity × usage`, and selects the highest-impact core-product work within a per-cycle
token budget — with a bounded safety tier. Prod-validated against 1,257 real interactions
(48 users) and all 765 open tickets.

## State — all committed, TDD, 268 tests green

```
1d0339c  enrichment P0        real usage → clusters / personas / problem-signals
43a97c8  PRIORITIZE wired     run_once ranks the backlog by usage within a budget
d5840d4  calibrated           est_tokens anchored on real merged-PR diff sizes
0a58279  self-measuring       CREATE logs its own fix cost (LLMRouter.log_external_cost)
bfa688a  bounded safety       reserve + escalate — no budget blowup
```
Plus **issue #2390** raised on aagman-v2 = the PostHog product-event contract this is
designed to consume when it lands.

## Verify (do this first)

```bash
cd ~/Documents/aagman-harness
./venv312/bin/python -m pytest -q          # expect 268 passed
PYTHONPATH=. ./venv312/bin/python harness_engineering/tools/show_recommendations.py --since 2026-06-26 --top 10
```

## What's next (priority order — all are refinements now, not fixes)

1. **PR-dedup inside the loop.** `show_recommendations.py` dedups against open PRs, but
   `prioritize_work_items` doesn't. Move that filter into the prioritizer so the harness never
   picks an already-in-flight ticket.
2. **Segment-diversity term** in the score, so the #2/#3 user segments (SCREENER, OPTIONS)
   surface instead of the busiest domain sweeping every tie.
3. **Activation weighting.** External/blocked-user (activation) tickets are under-weighted
   because those users aren't in `mastra_messages`. Add an activation/business signal (comes
   naturally with PostHog #2390 funnel data).
4. **Recalibrate est_tokens from measured cost.** Once `logs/cost_log.jsonl` has
   `task_type=code_execution` rows (CREATE now logs them), extend `gen_effort_model.py` to use
   them and set `create_samples`. ⚠️ CREATE hasn't run live yet — blocked by the org opus
   rate-limit (see project memory); point the CREATE runner at a lower-TPM model to unblock.
5. **Escalation → Telegram.** Safety overflow is `_log.warning` only; wire it to the notifier.
6. **Engagement-weighting** once PostHog #2390 ships (weights become engagement, not just frequency).
7. **Content-domain lift.** The generic half (`QueryInteraction`, PG adapter, clusters/personas,
   `select_within_budget`) is reusable; lift into a shared `harness_audience` module when content
   builds usage-driven SENSE. Note: content generation goes through the router, so its effort is
   calibratable from cost_log today (unlike CREATE).

## Gotchas

- **venv:** `./venv312/bin/python` (py3.12). Run modules with `PYTHONPATH=.`.
- **Snapshots are committed** (`distilled/usage_weights.json`, `distilled/effort_model.json`).
  Regenerate with the `tools/` scripts — don't hand-edit. `gen_usage_weights` needs a prod
  read-only DSN in `HARNESS_PG_DSN`; `gen_effort_model` / `show_recommendations` need only `gh`.
- **Never commit secrets.** Before every commit run the secret gate (see the user's global
  rules for the exact grep): scan the staged diff for the usual provider API-key prefixes
  (Anthropic / OpenAI / Google / GitHub), PEM private-key headers, and the prod read-only DB
  credential var names — the result must be empty. Add files by name, never `git add -A`.
  Don't push (no remote wired; user owns that).
- **Live LLM runs:** `export ANTHROPIC_API_KEY=...` (and any provider key) into the env before
  running — `run.py`'s `load_env` overlays `.env` but doesn't auto-export for litellm.
- **harness_core stays domain-free** (grep-enforced). The `prioritizer` hook is generic; all
  scoring lives in `harness_engineering`.
- **TDD is mandatory** — failing test first, watch RED, minimal GREEN.

## Pointers

- Capability README: `docs/USAGE_PRIORITIZATION.md`
- Wider harness state: `HARNESS_STATUS.md`, `PROGRESS.md`, spec `AAGMAN_HARNESS_FINAL-5.md`
- PostHog contract this consumes: aagman-v2 issue **#2390**
