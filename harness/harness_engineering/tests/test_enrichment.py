"""TDD for the usage-enrichment provider.

The provider turns normalized user-interaction rows (the #2390 `aagman_query_outcomes`
shape — today reconstructed from mastra_messages, later read straight from the table)
into an Enrichment the harness steps consume: NL-frequency clusters, personas derived
from real usage, and scored bug/feature problem-signals.

Core logic is pure (operates on in-memory rows) so it is fixture-testable without a
DB; the Postgres adapter is a separate integration layer.
"""
from harness_engineering.enrichment import QueryInteraction, Enrichment


def _ix(**kw):
    base = dict(workspace_id="w1", user_id="u1", domain="SCREENER", text="")
    base.update(kw)
    return QueryInteraction(**base)


# --------------------------------------------------------------------------- #
# Cycle 1: NL frequency clustering by domain
# --------------------------------------------------------------------------- #
def test_nl_clusters_count_and_distinct_users_by_domain():
    ix = [
        _ix(workspace_id="w1", user_id="u1", domain="SCREENER", text="show top gainers"),
        _ix(workspace_id="w1", user_id="u1", domain="SCREENER", text="top gainers today"),
        _ix(workspace_id="w2", user_id="u2", domain="OPTIONS", text="nifty pcr"),
    ]
    e = Enrichment.from_interactions(ix)
    by = {c.domain: c for c in e.nl_clusters}

    assert by["SCREENER"].count == 2
    assert by["SCREENER"].users == 1
    assert by["OPTIONS"].count == 1
    assert by["SCREENER"].sample


def test_nl_clusters_sorted_most_frequent_first():
    ix = [_ix(domain="OPTIONS") for _ in range(3)] + [_ix(domain="CHART")]
    e = Enrichment.from_interactions(ix)
    assert [c.domain for c in e.nl_clusters] == ["OPTIONS", "CHART"]


def test_from_interactions_empty_is_safe():
    e = Enrichment.from_interactions([])
    assert e.nl_clusters == []
    assert e.personas == []
    assert e.problem_signals == []


def test_usage_weights_normalized_by_busiest_domain():
    ix = [_ix(domain="STRATEGY") for _ in range(4)] + [_ix(domain="SCREENER") for _ in range(2)]
    w = Enrichment.from_interactions(ix).usage_weights()
    assert w["STRATEGY"] == 1.0
    assert w["SCREENER"] == 0.5
    assert Enrichment.from_interactions([]).usage_weights() == {}


# --------------------------------------------------------------------------- #
# Cycle 2: personas derived from each workspace's primary (most-used) domain
# --------------------------------------------------------------------------- #
def test_personas_derived_from_workspace_primary_domain():
    ix = [
        _ix(workspace_id="w1", user_id="u1", domain="OPTIONS"),
        _ix(workspace_id="w1", user_id="u1", domain="OPTIONS"),
        _ix(workspace_id="w1", user_id="u1", domain="CHART"),      # w1 primary = OPTIONS
        _ix(workspace_id="w2", user_id="u2", domain="SCREENER"),   # w2 primary = SCREENER
    ]
    e = Enrichment.from_interactions(ix)
    by = {p.primary_domain: p for p in e.personas}

    assert by["OPTIONS"].name == "options-trader"
    assert by["OPTIONS"].workspaces == 1
    assert abs(by["OPTIONS"].share - 0.5) < 1e-9
    assert by["SCREENER"].name == "screener-explorer"


def test_personas_map_real_prod_domains():
    # real domains discovered on prod (not the synthetic OPTIONS/CHART guesses)
    ix = [
        _ix(workspace_id="w1", domain="OPTIONS_STRATEGY"),
        _ix(workspace_id="w2", domain="STRATEGY"),
        _ix(workspace_id="w3", domain="ANALYTICS"),
        _ix(workspace_id="w4", domain="MARKET_DATA"),
    ]
    e = Enrichment.from_interactions(ix)
    by = {p.primary_domain: p.name for p in e.personas}
    assert by["OPTIONS_STRATEGY"] == "options-trader"
    assert by["STRATEGY"] == "backtesting-quant"
    assert by["ANALYTICS"] == "analytics-user"
    assert by["MARKET_DATA"] == "market-data-user"


def test_personas_sorted_by_share_desc():
    ix = [
        _ix(workspace_id="w1", domain="OPTIONS"),
        _ix(workspace_id="w2", domain="OPTIONS"),
        _ix(workspace_id="w3", domain="SCREENER"),
    ]
    e = Enrichment.from_interactions(ix)
    assert e.personas[0].primary_domain == "OPTIONS"   # 2/3 of workspaces


# --------------------------------------------------------------------------- #
# Cycle 3: problem-signals — classify bug vs feature and score by impact
# --------------------------------------------------------------------------- #
def test_problem_signals_classify_bug_vs_feature_and_score():
    ix = [
        _ix(workspace_id="w1", user_id="u1", domain="OPTIONS",
            outcome="FAILED", error_category="no_market_data", text="nifty 500 backtest"),
        _ix(workspace_id="w2", user_id="u2", domain="OPTIONS",
            outcome="FAILED", error_category="no_market_data", text="banknifty backtest"),
        _ix(workspace_id="w3", user_id="u3", domain="EXECUTION",
            outcome="NOT_SUPPORTED", error_category="unsupported_intent", text="trailing sl on gtt"),
        _ix(workspace_id="w4", user_id="u4", domain="SCREENER", outcome="READY", text="ok"),
    ]
    e = Enrichment.from_interactions(ix)
    sig = {(s.domain, s.error_category): s for s in e.problem_signals}

    nmd = sig[("OPTIONS", "no_market_data")]
    assert nmd.kind == "bug"
    assert nmd.frequency == 2 and nmd.users == 2 and nmd.severity == 3
    assert nmd.score == 2 * 2 * 3

    assert sig[("EXECUTION", "unsupported_intent")].kind == "feature"
    # a successful (READY) turn yields no problem-signal
    assert all(s.error_category for s in e.problem_signals)
    # highest impact first
    assert e.problem_signals[0].domain == "OPTIONS"
