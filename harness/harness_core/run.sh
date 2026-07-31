#!/usr/bin/env bash
# Thin wrapper: run the harness from the repo root with venv + .env loaded.
#   ./harness_core/run.sh --domain content --once --dry-run
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f .env ]; then set -a; . ./.env; set +a; fi
export PYTHONPATH=.
exec ./venv312/bin/python3 harness_core/run.py "$@"
