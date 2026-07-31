"""Regenerate harness_engineering/distilled/usage_weights.json from LIVE product usage.

Reads real user interactions (READ-ONLY) from the aagman-v2 Postgres
(mastra.mastra_messages + mastra.aagman_sessions), derives per-domain usage weights
(busiest domain = 1.0), and writes the committed snapshot the PRIORITIZE step consumes.
Run periodically so the weights track how users actually use the product.

Setup (one-time; secret stays in YOUR shell — never commit it):
    export HARNESS_PG_DSN="host=<prod-ro-pg> port=5432 dbname=aagman user=<ro-user> password=<ro-pass>"
    # (the prod read-only creds — see your reference_prod_db notes)

Run:
    PYTHONPATH=. ./venv312/bin/python harness_engineering/tools/gen_usage_weights.py
"""
import json
import os
import sys
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness_engineering.enrichment import Enrichment          # noqa: E402
from harness_engineering.enrichment_pg import load_interactions  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "distilled" / "usage_weights.json"


def main():
    dsn = os.environ.get("HARNESS_PG_DSN")
    if not dsn:
        sys.exit("set HARNESS_PG_DSN to the prod read-only PG DSN (host/port/dbname/user/password)")
    conn = psycopg2.connect(dsn)
    conn.set_session(readonly=True)
    interactions = load_interactions(conn, since_days=60)
    conn.close()

    weights = Enrichment.from_interactions(interactions).usage_weights()
    weights = {k: round(v, 4) for k, v in sorted(weights.items(), key=lambda kv: -kv[1])}
    OUT.write_text(json.dumps(weights, indent=2) + "\n")
    print(f"wrote {OUT} from {len(interactions)} interactions:")
    print(json.dumps(weights, indent=2))


if __name__ == "__main__":
    main()
