"""Usage-enrichment provider for the engineering harness.

Turns normalized user-interaction rows into an `Enrichment` the harness steps
consume. The row shape mirrors the #2390 `aagman_query_outcomes` contract, so the
same logic is fed today by retro-classification over `mastra_messages` and later by
the real table — the Postgres/outcome adapter is a separate layer; this core is pure.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QueryInteraction:
    """One user NL turn, normalized to the #2390 outcome-row shape.

    `outcome` / `error_category` stay blank until a source supplies them
    (retro-classifier or the aagman_query_outcomes table).
    """
    workspace_id: str
    user_id: str
    domain: str
    intent: str = ""
    text: str = ""
    outcome: str = ""
    error_category: str = ""
    created_at: str = ""


@dataclass
class NLCluster:
    domain: str
    count: int
    users: int          # distinct users who asked
    sample: str         # a representative query


@dataclass
class Persona:
    name: str
    primary_domain: str
    workspaces: int     # workspaces whose most-used domain is this one
    share: float        # fraction of active workspaces


@dataclass
class ProblemSignal:
    domain: str
    error_category: str
    kind: str           # "bug" | "feature"
    frequency: int      # occurrences
    users: int          # distinct affected users
    severity: int       # 1..3
    score: float        # impact = frequency * users * severity
    sample: str


@dataclass
class Enrichment:
    nl_clusters: list[NLCluster] = field(default_factory=list)
    personas: list[Persona] = field(default_factory=list)
    problem_signals: list[ProblemSignal] = field(default_factory=list)

    @classmethod
    def from_interactions(cls, interactions: list[QueryInteraction]) -> "Enrichment":
        return cls(
            nl_clusters=_cluster_by_domain(interactions),
            personas=_derive_personas(interactions),
            problem_signals=_problem_signals(interactions),
        )

    def usage_weights(self) -> dict[str, float]:
        """domain -> [0,1] usage weight, normalized by the busiest domain. Feeds the
        PRIORITIZE scorer so tickets are weighted by where users actually are."""
        if not self.nl_clusters:
            return {}
        busiest = max(c.count for c in self.nl_clusters)
        return {c.domain: c.count / busiest for c in self.nl_clusters}


# Domain → persona name. Keys are the real aagman_sessions.state->>'domain' values
# (verified on prod); unknown domains fall back to "general".
_PERSONA_NAME = {
    "OPTIONS_STRATEGY": "options-trader",
    "OPTIONS": "options-trader",
    "SCREENER": "screener-explorer",
    "STRATEGY": "backtesting-quant",
    "BACKTEST": "backtesting-quant",
    "EXECUTION": "execution-live",
    "ANALYTICS": "analytics-user",
    "MARKET_DATA": "market-data-user",
    "PORTFOLIO": "portfolio-manager",
    "RESEARCH": "research-reader",
    "CHART": "chart-analyst",
}

# error_category → severity (3 = worst). Non-success outcomes with a blank category
# derive one from the outcome so nothing is silently dropped.
_SEVERITY = {
    "no_market_data": 3, "crash": 3, "blocked": 3,
    "timeout": 2, "wrong_answer": 2, "misroute": 2, "failed": 2,
    "needs_clarification": 1, "unsupported_intent": 1, "not_supported": 1,
}
_FEATURE_CATEGORIES = {"unsupported_intent", "not_supported"}


def _cluster_by_domain(interactions: list[QueryInteraction]) -> list[NLCluster]:
    buckets: dict[str, list[QueryInteraction]] = {}
    for ix in interactions:
        buckets.setdefault(ix.domain, []).append(ix)
    clusters = [
        NLCluster(
            domain=domain,
            count=len(rows),
            users=len({r.user_id for r in rows}),
            sample=next((r.text for r in rows if r.text), ""),
        )
        for domain, rows in buckets.items()
    ]
    clusters.sort(key=lambda c: (-c.count, c.domain))
    return clusters


def _derive_personas(interactions: list[QueryInteraction]) -> list[Persona]:
    # per workspace: its most-used domain (deterministic tiebreak by domain name)
    ws_domain_counts: dict[str, dict[str, int]] = {}
    for ix in interactions:
        ws_domain_counts.setdefault(ix.workspace_id, {})
        ws_domain_counts[ix.workspace_id][ix.domain] = (
            ws_domain_counts[ix.workspace_id].get(ix.domain, 0) + 1
        )
    total_ws = len(ws_domain_counts)
    if not total_ws:
        return []

    primary_by_ws = {
        ws: max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
        for ws, counts in ws_domain_counts.items()
    }
    per_domain: dict[str, int] = {}
    for domain in primary_by_ws.values():
        per_domain[domain] = per_domain.get(domain, 0) + 1

    personas = [
        Persona(
            name=_PERSONA_NAME.get(domain, "general"),
            primary_domain=domain,
            workspaces=n,
            share=n / total_ws,
        )
        for domain, n in per_domain.items()
    ]
    personas.sort(key=lambda p: (-p.share, p.primary_domain))
    return personas


def _problem_signals(interactions: list[QueryInteraction]) -> list[ProblemSignal]:
    buckets: dict[tuple[str, str], list[QueryInteraction]] = {}
    for ix in interactions:
        if not _is_problem(ix):
            continue
        category = ix.error_category or _outcome_to_category(ix.outcome)
        buckets.setdefault((ix.domain, category), []).append(ix)

    signals = []
    for (domain, category), rows in buckets.items():
        freq = len(rows)
        users = len({r.user_id for r in rows})
        severity = _SEVERITY.get(category, 2)
        signals.append(ProblemSignal(
            domain=domain,
            error_category=category,
            kind="feature" if category in _FEATURE_CATEGORIES else "bug",
            frequency=freq,
            users=users,
            severity=severity,
            score=freq * users * severity,
            sample=next((r.text for r in rows if r.text), ""),
        ))
    signals.sort(key=lambda s: (-s.score, s.domain, s.error_category))
    return signals


def _is_problem(ix: QueryInteraction) -> bool:
    # A non-success outcome. Blank outcome = unlabeled → skip until a source labels it.
    return bool(ix.outcome) and ix.outcome != "READY"


def _outcome_to_category(outcome: str) -> str:
    return outcome.strip().lower() or "unknown"
