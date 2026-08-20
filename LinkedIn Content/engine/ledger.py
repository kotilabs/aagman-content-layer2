"""JSONL event ledger at memory/ledger.jsonl."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "memory" / "ledger.jsonl"


def log(event: dict) -> None:
    event = dict(event)
    event.setdefault("ts", datetime.now(timezone.utc).isoformat())
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def all() -> list[dict]:
    if not LEDGER.exists():
        return []
    events = []
    with LEDGER.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events
