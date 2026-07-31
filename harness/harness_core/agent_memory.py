"""agent_memory.py — namespaced lessons with self-evolution hooks.

AgentMemory(domain, step) is one namespace. Lessons carry helped/misled/last_used
so retrieval can compound: top_k ranks by relevance x confidence, so proven lessons
surface and misleading ones sink. attribute() credits/blames after an outcome.

These columns ship in Phase 1 (cheap) even though scoring only activates in Phase 7
— you cannot score retroactively without them. count() feeds Phase-2 seed checks.
"""
from __future__ import annotations

import re
import sqlite3
import time as _time
from dataclasses import dataclass
from pathlib import Path

_WORD = re.compile(r"[a-z0-9]+")
# Terminal SUCCESS outcomes that credit (helped) a relied-on lesson; anything else
# blames (misled). "published" is the harness's generic success state — omitting it
# would blame every lesson behind a successful cycle.
_CREDIT = {"helped", True, "pass", "approved", "merged", "published", "unedited"}


def _tokens(s: str) -> set:
    return set(_WORD.findall((s or "").lower()))


@dataclass
class Lesson:
    id: str
    domain: str
    step: str
    text: str
    tags: str = ""
    helped: int = 0
    misled: int = 0
    last_used: float = 0.0
    created_at: float = 0.0
    retired: int = 0

    @property
    def confidence(self) -> float:
        n = self.helped + self.misled
        return self.helped / n if n else 0.5  # neutral prior for unproven seeds


_COLS = ["id", "domain", "step", "text", "tags", "helped", "misled",
         "last_used", "created_at", "retired"]


class AgentMemory:
    def __init__(self, domain, step, db_path=None, now=None):
        self.domain = domain
        self.step = step
        self.now = now or _time.time
        db_path = db_path or str(
            Path(__file__).resolve().parent.parent / "data" / "memory.db")
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS lessons(
                id TEXT PRIMARY KEY, domain TEXT, step TEXT, text TEXT, tags TEXT,
                helped INTEGER DEFAULT 0, misled INTEGER DEFAULT 0,
                last_used REAL DEFAULT 0, created_at REAL DEFAULT 0,
                retired INTEGER DEFAULT 0);
            CREATE INDEX IF NOT EXISTS ix_lessons_ns ON lessons(domain, step);
            """
        )
        self.conn.commit()

    def _row(self, r) -> Lesson:
        return Lesson(**{c: r[c] for c in _COLS})

    def add(self, text, id=None, tags=None) -> Lesson:
        n = self.conn.execute(
            "SELECT COUNT(*) c FROM lessons WHERE domain=? AND step=?",
            (self.domain, self.step)).fetchone()["c"]
        lid = id or f"{self.domain}.{self.step}.{n + 1}"
        les = Lesson(id=lid, domain=self.domain, step=self.step, text=text,
                     tags=tags or "", created_at=self.now(), last_used=self.now())
        self.conn.execute(
            f"INSERT OR REPLACE INTO lessons ({','.join(_COLS)}) "
            f"VALUES ({','.join('?' * len(_COLS))})",
            tuple(getattr(les, c) for c in _COLS))
        self.conn.commit()
        return les

    def get(self, id) -> Lesson | None:
        r = self.conn.execute("SELECT * FROM lessons WHERE id=?", (id,)).fetchone()
        return self._row(r) if r else None

    def count(self, include_retired=False) -> int:
        q = "SELECT COUNT(*) c FROM lessons WHERE domain=? AND step=?"
        if not include_retired:
            q += " AND retired=0"
        return self.conn.execute(q, (self.domain, self.step)).fetchone()["c"]

    def all(self, include_retired=False) -> list:
        q = "SELECT * FROM lessons WHERE domain=? AND step=?"
        if not include_retired:
            q += " AND retired=0"
        return [self._row(r) for r in self.conn.execute(
            q, (self.domain, self.step)).fetchall()]

    def top_k(self, query, k=10) -> list:
        """Return up to k lesson IDs ranked by relevance x confidence, recency tiebreak."""
        qt = _tokens(query)
        scored = []
        for les in self.all(include_retired=False):
            relevance = len(qt & _tokens(les.text + " " + les.tags))
            score = (1 + relevance) * les.confidence
            scored.append((score, les.last_used, les.id))
        scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
        return [lid for _, _, lid in scored[:k]]

    def attribute(self, lesson_ids, outcome):
        """Credit (helped) or blame (misled) the lessons a step relied on. Auto-retire
        a lesson whose confidence < 0.3 after >= 5 uses (archived, not deleted)."""
        credit = outcome in _CREDIT
        for lid in lesson_ids:
            les = self.get(lid)
            if not les:
                continue
            if credit:
                les.helped += 1
            else:
                les.misled += 1
            retired = les.retired
            if (les.helped + les.misled) >= 5 and les.confidence < 0.3:
                retired = 1
            self.conn.execute(
                "UPDATE lessons SET helped=?, misled=?, last_used=?, retired=? "
                "WHERE id=?",
                (les.helped, les.misled, self.now(), retired, lid))
        self.conn.commit()
