"""state.py — crash-safe work-item store (SQLite).

Every sensed signal becomes a work item. This is what makes the harness resumable
and both domains gate-compatible. Dedup is by fingerprint against OPEN items only;
resume replays anything not in a terminal state from its current_step; every gate
decision appends an audit row carrying the rules_version in force at decision time.
"""
from __future__ import annotations

import datetime as _dt
import json
import sqlite3
import time as _time
from dataclasses import dataclass
from pathlib import Path

TERMINAL = {"published", "failed", "rejected"}

_COLUMNS = ["id", "domain", "status", "signal_json", "fingerprint", "current_step",
            "loop_counts_json", "rules_version", "relied_lessons_json", "cost_usd",
            "created_at", "updated_at"]


@dataclass
class WorkItem:
    id: str
    domain: str
    status: str = "sensed"
    signal_json: str = "{}"
    fingerprint: str = ""
    current_step: str = ""
    loop_counts_json: str = "{}"
    rules_version: str = ""
    relied_lessons_json: str = "[]"
    cost_usd: float = 0.0
    created_at: str = ""
    updated_at: str = ""


class WorkItemStore:
    def __init__(self, db_path, now=None):
        self.now = now or _time.time
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS work_items(
                id TEXT PRIMARY KEY, domain TEXT, status TEXT, signal_json TEXT,
                fingerprint TEXT, current_step TEXT, loop_counts_json TEXT,
                rules_version TEXT, relied_lessons_json TEXT, cost_usd REAL,
                created_at TEXT, updated_at TEXT);
            CREATE INDEX IF NOT EXISTS ix_wi_fingerprint ON work_items(fingerprint);
            CREATE TABLE IF NOT EXISTS audit(
                id INTEGER PRIMARY KEY AUTOINCREMENT, work_item_id TEXT,
                gate_name TEXT, verdict TEXT, rules_version TEXT, issues_json TEXT,
                at TEXT);
            """
        )
        self.conn.commit()

    # -- helpers ---------------------------------------------------------- #
    def _ts(self) -> str:
        return _dt.datetime.fromtimestamp(self.now()).isoformat(timespec="seconds")

    def _row_to_wi(self, row) -> WorkItem:
        return WorkItem(**{c: row[c] for c in _COLUMNS})

    # -- work items ------------------------------------------------------- #
    def get(self, id) -> WorkItem | None:
        row = self.conn.execute("SELECT * FROM work_items WHERE id=?", (id,)).fetchone()
        return self._row_to_wi(row) if row else None

    def create(self, signal) -> WorkItem:
        """Create from a Signal. Idempotent by id: re-sensing an existing id
        returns the current item (progress preserved), never resets it."""
        existing = self.get(signal.id)
        if existing:
            return existing
        ts = self._ts()
        wi = WorkItem(
            id=signal.id, domain=signal.domain, status="sensed",
            signal_json=json.dumps(getattr(signal, "payload", {})),
            fingerprint=getattr(signal, "fingerprint", ""),
            created_at=ts, updated_at=ts,
        )
        self.conn.execute(
            f"INSERT INTO work_items ({','.join(_COLUMNS)}) "
            f"VALUES ({','.join('?' * len(_COLUMNS))})",
            tuple(getattr(wi, c) for c in _COLUMNS),
        )
        self.conn.commit()
        return wi

    def update(self, id, **updates) -> WorkItem | None:
        allowed = {k: v for k, v in updates.items()
                   if k in _COLUMNS and k not in ("id", "created_at")}
        allowed["updated_at"] = self._ts()
        assignments = ",".join(f"{k}=?" for k in allowed)
        self.conn.execute(
            f"UPDATE work_items SET {assignments} WHERE id=?",
            (*allowed.values(), id),
        )
        self.conn.commit()
        return self.get(id)

    def is_duplicate(self, fingerprint) -> bool:
        rows = self.conn.execute(
            "SELECT status FROM work_items WHERE fingerprint=?", (fingerprint,)
        ).fetchall()
        return any(r["status"] not in TERMINAL for r in rows)

    def open_items(self) -> list:
        ph = ",".join("?" * len(TERMINAL))
        rows = self.conn.execute(
            f"SELECT * FROM work_items WHERE status NOT IN ({ph}) ORDER BY created_at",
            tuple(TERMINAL),
        ).fetchall()
        return [self._row_to_wi(r) for r in rows]

    # -- audit ------------------------------------------------------------ #
    def audit(self, work_item_id, gate_name, verdict, rules_version="", issues=None):
        self.conn.execute(
            "INSERT INTO audit (work_item_id,gate_name,verdict,rules_version,"
            "issues_json,at) VALUES (?,?,?,?,?,?)",
            (work_item_id, gate_name, verdict, rules_version,
             json.dumps(issues or []), self._ts()),
        )
        self.conn.commit()

    def audits(self, work_item_id) -> list:
        rows = self.conn.execute(
            "SELECT * FROM audit WHERE work_item_id=? ORDER BY id", (work_item_id,)
        ).fetchall()
        return [dict(r) for r in rows]
