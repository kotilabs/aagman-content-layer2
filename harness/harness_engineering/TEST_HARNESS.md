# TEST_HARNESS.md — aagman-v2's EXISTING test harness (discovered, not invented)

> The engineering domain's TestGates run THESE commands against
> `~/Documents/aagman-v2`. Every command below was copied verbatim from a real
> file in that repo (package.json / pyproject.toml / run_all.sh / README.md) by a
> read-only inventory pass. Do not substitute a guessed command.

Target repo: `/Users/ajitkumar/Documents/aagman-v2`
Package managers: **pnpm** (TypeScript/Node), **uv** (Python). Env via `dotenvx run -f ../.env`.

## Full regression suite (the outer safety net — judge gate)
```bash
bash /Users/ajitkumar/Documents/aagman-v2/regression-testing/run_all.sh
```
- `--fast` skips integration-marked tests (the inner loop, create gate).
- `run_all.sh <area>` runs a single area (see areas below).
- Underlying invocation (run_all.sh:34–45):
  `uv run --project backtester pytest "$TEST_PATH" -v -m "not integration" --tb=short --junit-xml=...`

## Single issue's regression test (the fail-before/pass-after proof, law d)
```bash
uv run --project backtester pytest /Users/ajitkumar/Documents/aagman-v2/regression-testing/<area>/test_<what>.py -v
```
Convention: one `test_<what>.py` per area; the area README table maps issue → test.

## regression-testing/ areas (8)
`agents/` · `backtesting/` · `data/` · `india/` · `sandbox/` · `screener/` · `strategy/` · `worker/`
(README.md table maps each area to what it tests + the issue that motivated it.)

## Per-layer test commands (from each service's package.json)
| Layer / service | Command | Runner |
|---|---|---|
| gateway (TS)   | `pnpm --filter gateway run test`   | vitest |
| backend (TS)   | `pnpm --filter backend run test`   | vitest (dotenvx `-f ../.env`) |
| market-data(TS)| `pnpm --filter @market-data/api run test` | vitest |
| frontend (TS)  | `pnpm --filter frontend run test`  | vitest |
| backtester (PY)| `dotenvx run -f ../.env -- uv run pytest packages/ apps/worker/` | pytest |
| orchestrator(PY)| `dotenvx run -f ../.env -- uv run pytest tests/ -v` | pytest |
| executor (PY)  | `uv run pytest apps/ packages/`    | pytest |

Pytest config (`pyproject.toml [tool.pytest.ini_options]`): `addopts="-q --tb=short --no-header"`,
`asyncio_mode="auto"`, markers `integration`, `parity`.

## Layer law entrypoint
`risk_blocked` / `rule 6.x` bugs → TypeScript at
`/Users/ajitkumar/Documents/aagman-v2/backend/src/mastra/utils/risk-calculations.ts` (confirmed present).

## The "22-check verify" suite — NOT FOUND
The spec's `dev_lab/scripts/verify.sh` (a 22-check suite) does **not exist** in the
current aagman-v2 tree (`dev_lab/` is absent; a search for "22-check"/verify runners
found only `testing/regression/verify-cleanup-migration.sh`, a DB-cleanup check —
not a 22-point suite). Therefore the judge (pre-PR) TestGate uses the **full
`run_all.sh` regression suite** as the outer safety net, not a fabricated 22-check.
If a verify suite is added later, wire it as a second judge TestGate here.
