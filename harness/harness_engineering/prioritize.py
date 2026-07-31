"""Budget-constrained PRIORITIZE selector.

Highest-impact-first: candidates are considered in descending impact (a priority
backlog leads with the most important work, not the best impact-per-token), cheaper
then lower id breaking ties, and filled greedily until the budget is exhausted. Safety
work (security / data-loss) is filled within a reserved fraction of the budget; safety
that exceeds the reserve is ESCALATED to a human rather than blindly force-included (a
large safety backlog would otherwise blow the budget many-fold) or silently deferred.
Nothing is silently truncated — every item is returned chosen, deferred, or escalated.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

_log = logging.getLogger("harness.prioritize")

# est_tokens anchored on the real merged-PR diff-size distribution (committed snapshot,
# regenerated from prod history). Falls back to the baked defaults if absent/malformed.
_EFFORT_PATH = Path(__file__).resolve().parent / "distilled" / "effort_model.json"
_DEFAULT_EFFORT = {"base": 48_000, "p0": 73_000, "feature": 53_000}


def _load_effort():
    try:
        d = json.loads(_EFFORT_PATH.read_text())
        return {k: int(d[k]) for k in ("base", "p0", "feature")}
    except Exception:
        return dict(_DEFAULT_EFFORT)


_EFFORT = _load_effort()


@dataclass
class WorkItem:
    id: int
    title: str
    kind: str            # "bug" | "feature"
    safety: bool         # security / data-loss / kill-switch → mandatory
    score: float         # impact (usage-weighted)
    est_tokens: int      # estimated CREATE cost
    domain: str = ""


def select_within_budget(items: list[WorkItem], budget: int, safety_reserve: float = 0.5):
    """Return (chosen, deferred, escalated). Safety items (ranked impact-first) are filled
    within `safety_reserve` × budget; safety that doesn't fit is escalated to a human, not
    force-included (which would blow the budget) nor silently deferred. The remaining budget
    fills discretionary work impact-first. Nothing is silently dropped."""
    key = lambda i: (-i.score, i.est_tokens, str(i.id))
    safety = sorted((i for i in items if i.safety), key=key)
    rest = sorted((i for i in items if not i.safety), key=key)
    chosen, deferred, escalated = [], [], []
    spent = 0
    safety_budget = budget * safety_reserve
    for i in safety:
        if spent + i.est_tokens <= safety_budget:
            chosen.append(i)
            spent += i.est_tokens
        else:
            escalated.append(i)
    for i in rest:
        if spent + i.est_tokens <= budget:
            chosen.append(i)
            spent += i.est_tokens
        else:
            deferred.append(i)
    return chosen, deferred, escalated


# --------------------------------------------------------------------------- #
# Engineering issue scoring — turn store work items into scored WorkItems.
# Domains are the real aagman_sessions.state->>'domain' values (verified on prod).
# --------------------------------------------------------------------------- #
CORE_DOMAINS = {"STRATEGY", "SCREENER", "OPTIONS_STRATEGY", "RESEARCH",
                "ANALYTICS", "MARKET_DATA", "PORTFOLIO"}

_DOMAIN_KW = {
    "SCREENER": ["screener", "screen"],
    "OPTIONS_STRATEGY": ["option", "greek", "iv ", "straddle", "strangle"],
    "STRATEGY": ["backtest", "strategy", "signal", "momentum"],
    "EXECUTION": ["execution", "executor", "order", "broker", "live", "deploy",
                  "fill", "mofsl", "zerodha"],
    "RESEARCH": ["research"],
    "ANALYTICS": ["analytic", "performance", "metric"],
    "PORTFOLIO": ["portfolio"],
    "MARKET_DATA": ["market data", "chart", "candle", "quote", "feed"],
}
_SEV = {"p0": 5, "critical": 5, "p1": 4, "regression": 4, "bug": 3, "p2": 2, "p3": 1}
_BUG_RX = re.compile(r"\b(fix|crash|error|broken|fail|wrong|not work)")


def infer_domain(title: str, labels: list[str]) -> str:
    t = title.lower() + " " + " ".join(labels).lower()
    best, hits = "", 0
    for dom, kws in _DOMAIN_KW.items():
        h = sum(1 for k in kws if k in t)
        if h > hits:
            best, hits = dom, h
    return best


def classify_issue(title: str, labels: list[str]):
    """Return (kind, safety, base_severity). safety = security / data-loss / live."""
    ls = set(labels)
    if "feature" in ls:
        kind = "feature"
    elif ls & {"bug", "regression", "p0", "critical"}:
        kind = "bug"
    else:
        kind = "bug" if _BUG_RX.search(title.lower()) else "feature"
    safety = bool(ls & {"security", "live-trading"})
    base = max([_SEV[l] for l in labels if l in _SEV] + [2])
    return kind, safety, base


def est_tokens_for(kind: str, base: int, model=None) -> int:
    m = model or _EFFORT
    if base >= 5:                       # p0 / critical → real p75 diff size
        return m["p0"]
    return m["feature"] if kind == "feature" else m["base"]


def prioritize_work_items(items, usage_weights, budget, core_only=True, safety_reserve=0.5):
    """Score store work items (issues) by severity × real usage weight, then return the
    budget-fitted subset highest-impact-first. Out-of-scope items (live-trading, or a
    non-core domain when core_only) are dropped this cycle; deferred items stay open.
    Safety work over the reserve is escalated (logged, never silently dropped)."""
    by_id = {}
    wrapped = []
    for wi in items:
        payload = json.loads(getattr(wi, "signal_json", "") or "{}")
        title = payload.get("title", "") or ""
        labels = payload.get("labels", []) or []
        dom = infer_domain(title, labels)
        if core_only and ("live-trading" in labels or dom not in CORE_DOMAINS):
            continue
        kind, safety, base = classify_issue(title, labels)
        score = round(base * (0.25 + 0.75 * usage_weights.get(dom, 0.0)), 3)
        num = payload.get("number", wi.id)
        wrapped.append(WorkItem(id=num, title=title[:70], kind=kind, safety=safety,
                                score=score, est_tokens=est_tokens_for(kind, base), domain=dom))
        by_id[num] = wi
    chosen, _deferred, escalated = select_within_budget(wrapped, budget, safety_reserve=safety_reserve)
    if escalated:
        _log.warning("PRIORITIZE: %d safety items exceed the %.0f%% safety-reserve of "
                     "%d tok/cycle — escalated for human triage (ids: %s)",
                     len(escalated), safety_reserve * 100, budget, [e.id for e in escalated[:10]])
    chosen.sort(key=lambda c: (not c.safety, -c.score, c.est_tokens, str(c.id)))
    return [by_id[c.id] for c in chosen]


def make_prioritizer(usage_weights, budget, core_only=True, safety_reserve=0.5):
    """Bind usage weights + a per-cycle token budget into the callable(list)->list hook
    GenericHarness.run_once applies before the pipeline."""
    return lambda items: prioritize_work_items(items, usage_weights, budget,
                                               core_only, safety_reserve)
