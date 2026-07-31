# Usage-Driven Prioritization

Turn **real product usage** into a **token-budget-fitted bug/feature do-list** for
aagman-v2. The engineering harness reads what users actually do, ranks the open-ticket
backlog by where they are, fits a per-cycle token budget, and (once wired) feeds the
top items into the SENSE→IDEATE→CREATE loop.

Built + prod-validated 2026-07-05. Branch `feat/usage-driven-prioritization`.

## What it does, in one line

`real usage → clusters / personas / usage-weights → score open tickets (severity × usage) → budget-fitted, impact-first, bounded-safety queue`

## Data flow

```
mastra.mastra_messages  ─┐
mastra.aagman_sessions  ─┴─►  QueryInteraction  ─►  Enrichment
   (prod, read-only)            (normalized row)      ├─ nl_clusters   (what users ask)
                                                      ├─ personas      (who users are)
                                                      ├─ usage_weights (domain → [0,1])
                                                      └─ problem_signals (bug|feature)
                                                                 │
 open GitHub issues ──► prioritize_work_items ──► select_within_budget ──► ranked queue
                        (severity × usage, core-only)   (impact-first,       │
                                                          bounded safety)    ▼
                                          GenericHarness.run_once(prioritizer hook)
```

## Files

| File | What |
|---|---|
| `harness_engineering/enrichment.py` | `Enrichment` core (pure): clusters, personas, problem-signals, `usage_weights()` |
| `harness_engineering/enrichment_pg.py` | Postgres adapter: `load_interactions`, `extract_text`, `outcome_from_state` (coarse outcome pending #2390) |
| `harness_engineering/prioritize.py` | `select_within_budget` (impact-first + bounded safety), issue scoring (`infer_domain`/`classify_issue`/`est_tokens_for`), `prioritize_work_items`, `make_prioritizer` |
| `harness_engineering/distilled/usage_weights.json` | **committed snapshot** of per-domain usage weights (regen from prod) |
| `harness_engineering/distilled/effort_model.json` | **committed snapshot** of est_tokens, anchored on real PR sizes |
| `harness_core/generic_harness.py` | `run_once` applies the optional `prioritizer` hook (domain-free) |
| `harness_core/domain_config.py` | `DomainConfig.prioritizer` field |
| `harness_core/run.py` | `build_harness` forwards `config.prioritizer` |
| `harness_core/llm_router.py` | `log_external_cost` — logs the nested `claude -p` CREATE tokens |
| `harness_configs/engineering_config.py` | wires `make_prioritizer(weights, budget)` + passes router to `CodeFixAgent` |
| `harness_engineering/tools/` | regeneration + inspection scripts (below) |

## Scoring model

- **score** = `base_severity × (0.25 + 0.75 × usage_weight[domain])` — severity from labels
  (p0/critical=5, p1=4, bug=3, …), usage_weight from the committed snapshot.
- **est_tokens** — from `effort_model.json` (base 48k / p0 73k / feature 53k), anchored on the
  real merged-PR size distribution.
- **selection** — highest-impact-first (a priority backlog leads with the most important work,
  not best impact-per-token); token cost breaks ties.
- **safety tier** — security / live-trading work is ranked and filled within a reserved budget
  fraction (default 50%); overflow is **escalated to a human** (logged), never force-included
  (which blew the budget ~34× on the real backlog) nor silently deferred.
- **scope** — core product only by default (`live-trading` / `EXECUTION` excluded); flip with
  `--all-scope` / `core_only=False`.

## Run it

```bash
# what would the harness work on right now? (needs only gh + the snapshot)
PYTHONPATH=. ./venv312/bin/python harness_engineering/tools/show_recommendations.py
PYTHONPATH=. ./venv312/bin/python harness_engineering/tools/show_recommendations.py --since 2026-06-26 --top 10

# regenerate the committed snapshots
export HARNESS_PG_DSN="host=<prod-ro> port=5432 dbname=aagman user=<ro-user> password=<ro-pass>"
PYTHONPATH=. ./venv312/bin/python harness_engineering/tools/gen_usage_weights.py   # needs DB
./venv312/bin/python harness_engineering/tools/gen_effort_model.py                 # needs gh only

# tests
./venv312/bin/python -m pytest harness_engineering/tests/test_enrichment.py \
    harness_engineering/tests/test_prioritize.py harness_core/tests/test_prioritize_hook.py -q
```

## Known limitations / roadmap (see HANDOFF.md for detail)

1. **PR-dedup is a tool, not in the loop** — `run_once` doesn't yet skip tickets with an open PR.
2. **Usage-weight sweep** — the busiest domain dominates ties; add a **segment-diversity** term.
3. **Activation blind spot** — external/blocked users aren't in usage data, so activation-blocking
   tickets are under-weighted. Needs an activation/business signal (PostHog funnel, #2390).
4. **Engagement not yet real** — weights are usage-frequency, not engagement/KPI (blocked on PostHog #2390).
5. **est_tokens is a proxy** — recalibrate from measured CREATE cost once `code_execution` rows accrue.
6. **Escalation is log-only** — wire it to the Telegram notifier.
7. **Content domain** — the generic half (interactions/clusters/personas/`select_within_budget`) is
   reusable; lift it into a shared module when content builds usage-driven SENSE.
