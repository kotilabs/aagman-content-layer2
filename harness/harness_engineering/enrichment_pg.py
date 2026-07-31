"""Postgres adapter: read real user interactions from mastra.mastra_messages +
mastra.aagman_sessions (read-only) into QueryInteraction rows the enrichment core
consumes. Pure helpers (extract_text / outcome_from_state) are unit-tested; the SQL
is IO, verified by running against prod.

Outcome is reconstructed coarsely from session state (pendingQuestions / stage /
confirmed) until #2390's aagman_query_outcomes table gives a per-query outcome.
"""
from __future__ import annotations

import json

from harness_engineering.enrichment import QueryInteraction


def extract_text(content) -> str:
    """Pull user text out of the mastra content shape
    {"format":2,"parts":[{"type":"text","text":"..."}]}. Non-JSON strings pass through."""
    if content is None:
        return ""
    obj = content
    if isinstance(content, str):
        s = content.strip()
        if not (s.startswith("{") or s.startswith("[")):
            return content
        try:
            obj = json.loads(s)
        except Exception:
            return content
    if isinstance(obj, dict):
        parts = obj.get("parts") or []
        texts = [p.get("text", "") for p in parts
                 if isinstance(p, dict) and p.get("type") == "text"]
        return " ".join(t for t in texts if t).strip()
    return ""


def outcome_from_state(state) -> str:
    """Coarse outcome reconstruction from aagman_sessions.state (session-level).
    Full error taxonomy (timeout/no_market_data/crash) needs #2390."""
    if not isinstance(state, dict):
        return ""
    pq = state.get("pendingQuestions")
    if isinstance(pq, list) and pq:
        return "NEEDS_CLARIFICATION"
    if state.get("stage") == "complete" and state.get("confirmed") in (True, "true"):
        return "READY"
    return ""


def load_interactions(conn, schema: str = "mastra", since_days: int = 60,
                      limit: int | None = None) -> list[QueryInteraction]:
    cur = conn.cursor()
    cur.execute("SET statement_timeout = '30s'")
    sql = (
        f'SELECT m.thread_id, m."resourceId", m.content, s.state '
        f'FROM {schema}.mastra_messages m '
        f'JOIN {schema}.aagman_sessions s ON m.thread_id = s.thread_id '
        f"WHERE m.role = 'user' "
        f'AND m."createdAt" > now() - (%s || \' days\')::interval '
        f'ORDER BY m."createdAt" DESC'
    )
    if limit:
        sql += f" LIMIT {int(limit)}"
    cur.execute(sql, (str(since_days),))
    out = []
    for thread_id, user_id, content, state in cur.fetchall():
        st = state if isinstance(state, dict) else {}
        out.append(QueryInteraction(
            workspace_id=(thread_id or "").replace("ws-", "", 1),
            user_id=user_id or "",
            domain=st.get("domain") or "UNKNOWN",
            text=extract_text(content),
            outcome=outcome_from_state(st),
        ))
    cur.close()
    return out
