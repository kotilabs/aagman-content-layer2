# Phase 2A — Engineering Distillation Report

Generated 2026-07-03. All artifacts under `harness_engineering/distilled/`. **Real data only** — extracted from GitHub `kotilabs/aagman-v2`, the repo rules files, and local non-git session memories. No fabricated entries.

## Counts per file

| File | Entries | Non-empty | Primary source |
|------|---------|-----------|----------------|
| `classifier_examples.json` | 206 | ✅ | 600 GitHub issues (labels+title+body → inferred type) |
| `file_relationships.json` | 39 areas + 60 co-change pairs | ✅ | PR file lists (≤18-file PRs, co-change frequency) |
| `layer_ground_truth.json` | 12 | ✅ | repo CLAUDE.md/AGENTS.md/docs + codebase grep |
| `adversarial_vocab.json` | 39 (9 real Amit review quotes + 30 distilled rules) | ✅ | Amit review bodies + local `feedback_*.md` |
| `fix_success_patterns.json` | 37 (9 that took review rounds + 28 clean) | ✅ | 339 MERGED PRs × Amit verdicts |
| `loop_counts.json` | dist over 86 reviewed PRs, p90=1 | ✅ | Amit review verdict rounds per PR |
| `sebi_patterns.json` | 10 | ✅ | portfolio-audit + mood + entity-credentials memories |

## Top sources used
1. **GitHub `kotilabs/aagman-v2`** — 600 issues (all states), 500 PRs (339 MERGED / 94 OPEN / 67 CLOSED). Top issue labels: live-trading (145), p1 (138), bug (89), backtesting (75), data (54), p0 (50).
2. **Repo rules** — `CLAUDE.md`/`AGENTS.md` (identical 187-line file; the Safety-Critical Code + Multi-Broker sections are the richest objection source), `docs/risk/Risk-README.md` (the risk-layer law), `backend/AGENTS.md`.
3. **Local session memories** (NOT in git) — 35 `feedback_*.md` + `project_portfolio_agent_institutional_audit.md`, `project_mood_institutional.md`, `reference_aagman_entity_credentials.md`, plus 34 aagman-v2-scoped feedback files. These carried the durable engineering laws.

## Key extraction facts
- **Amit reviews via COMMENTED, not CHANGES_REQUESTED.** Only 1 formal `CHANGES_REQUESTED` exists in 500 PRs; Amit (154 reviews) posts verdicts as COMMENTED bodies with emoji markers (🔴 BLOCK / 🟡 REQUEST CHANGES / 🟢 CLEAN). Loop counts were derived from the Verdict/TL;DR line, not the GitHub review state — the naive `state==CHANGES_REQUESTED` count would have been wrong (=1).
- **Loop distribution:** {0: 74, 1: 10, 2: 1, 3: 1} PRs. p50=0, **p90=1**, max=3. Most PRs land clean on Amit's read (heavy pre-PR self-review + TDD); the 2–3-round tail is money-path/executor and de-hallucination work.
- **The canonical risk-layer law is confirmed in source:** `docs/risk/Risk-README.md` — *all* risk calc is TypeScript (`backend/src/mastra/utils/risk-calculations.ts`), pre-computed by the Supervisor Tool; the Risk Agent (LLM) has no tools. `rule 6.1.1` (LIVE-without-SL block) / `rule 6.2.1` (maxDD>20% warning) live in `aagman-risk-agent.ts`. `risk_blocked` → TypeScript, never Python.

## 5–10 most valuable lessons (mined from LOCAL memories)
1. **Mock-on-mock green does not qualify a PR** (`feedback_real_data_validation_for_pr`). #2246 was closed for mocking `MarketDataClient`/`BacktesterClient` to fix a 5s timeout — "only real-data passes go to PR." A hanging real-service test is a *signal* the path is uncovered, not a thing to stub green.
2. **No pre-existing excuse / deterministic RCA always** (`feedback_no_preexisting_excuse`, `feedback_deterministic_rca_always`). "Pre-existing", "stale DB", "LLM non-determinism, can't repro" are banned. Every bug has a code-path RCA — trace where the working vs failing flow diverges; reproduce red-on-revert before fixing.
3. **Fix, don't file** (`feedback_fix_dont_file`). Default is rca→fix→test→verify→PR. #2287 was wrongly filed claiming "engine source isn't in this checkout" — false after one narrow grep; the raise-site was `backtest_adapter.py:646`. "Big/risky" means fix *carefully*, not punt.
4. **Verify a blocker with 2 independent agents** (`feedback_verify_blocker_with_agents`). A single trace misleads (a fixture gap masquerading as an executor bug; a second blocker hiding behind the first). Only treat as confirmed when independent RCAs converge.
5. **Testing = the real consumer path** (`feedback_consumer_test_path`). A direct `KiteConnect.place_order()` from a dev box is not a live test — its IP-reject was a wrong-path artifact. Drive user→backend→executor→relay→broker; direct broker REST is read-only verification only.
6. **Presence assertions mask broken cards** (`feedback_data_testid_on_components`, `feedback_cross_validate_displayed_values`). "0 screeners · 1 signals" survived weeks because tests matched `document.body.textContent` keywords the LLM always emits. Every data component needs `data-testid`; every metric must cross-validate against the source DB (the 4125% IV-Rank scale bug).
7. **Frontend needs a runtime-interaction pass** (`feedback_frontend_runtime_lens`). A logic read called the order ticket "healthy," then 4 runtime bugs surfaced (inline `ref={el=>el.focus()}` stealing focus every render; a reset `useEffect` wiping in-progress orders on a 3s feed reconnect). Review against the parent's re-render cadence.
8. **Silent-drop is worse than a loud failure** (`feedback_discipline_over_speed`). The `is_percent_of` desugar silently dropped a 3% threshold because only the Pydantic symptom was traced, not the full LLM→compiler→evaluator flow — the fix was worse than the original error.
9. **LLM-invented numbers are a compliance breach** (`project_portfolio_agent_institutional_audit`). Portfolio stress/rebalance numbers were read from LLM JSON (`recovery_days_estimate` existed only in the prompt template) — the exact de-hallucination breach PR #1592 closed. Money-facing numbers must be deterministically computed in TS.
10. **White-box SIR = SEBI RA-exemption** (`reference_aagman_entity_credentials`). Deterministic, disclosable SIR keeps Aagman exempt from Research-Analyst registration; black-box providers must register + maintain per-algo research reports. Aagman holds RIA `INA000021951` (adviser, not RA) — frame as compliant distribution, not buy/sell calls.

## Sparse / caveats
- **Formal `CHANGES_REQUESTED` reviews are near-absent** (n=1). Loop counts are a best-effort parse of Amit's verdict lines in COMMENTED bodies; a 🟡 "optional polish" was intentionally NOT counted as a change round (only REQUEST CHANGES / FIX-THEN-SHIP / BLOCK / CONDITIONAL). Numbers are honest but verdict-line-heuristic-based.
- **pandeyanshuman has only 1 review in the fetched 500-PR window** (his adversarial objections — PR #269 empty-stubs, #291 unused-franc, #392 75-file/skip-flag/kill-switch — predate it and were recovered from the `feedback_*.md` record, which cites them explicitly; encoded in `adversarial_vocab.json` as distilled patterns).
- **PR #270 (wrong-layer negative) is outside the fetched window;** the gateway-business-logic wrong-layer example in `layer_ground_truth.json` is sourced from `feedback_gateway_no_business_logic.md` (the gateway response-transformer mutating backtest dates) and labelled as such.
- No secrets were written — a secret-bearing snippet redactor ran over issue/PR bodies; the only sweep hit is the false-positive substring "ri**sk-c**alculations".
