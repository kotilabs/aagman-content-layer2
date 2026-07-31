"""TDD: offline routing eval — score coding-agent routing against the ground
truth of what real merged PRs actually changed. Deterministic, no LLM budget:
the files a merging PR touched reveal the true area; we measure how well a router
predicts that area from the issue text. This is the measurement backbone — it turns
every future prompt/retrieval change into a measured one, not a guess.
"""
from pathlib import Path

from harness_engineering.evals.routing_eval import (
    area_of_files, build_gold, score, keyword_router, score_nn_loo, _issue_ref,
    evaluate, evaluate_embed, to_index, _dedup, _is_test_path,
)

_REPO = Path(__file__).resolve().parents[2]
LAYER_GT = str(_REPO / "harness_engineering" / "distilled" / "layer_ground_truth.json")


def test_area_of_files_takes_majority_ignoring_tests():
    files = ["backend/src/mastra/utils/risk-calculations.ts",
             "backend/src/mastra/agents/aagman-risk-agent.ts",
             "backend/src/mastra/utils/__tests__/risk.test.ts",  # test file ignored
             "backtester/packages/engine/x.py"]
    assert area_of_files(files) == "backend/src"


def test_is_test_path_does_not_match_backtester_substring():
    assert _is_test_path("backtester/packages/engine/mom.py") is False   # 'backTESTer' != test
    assert _is_test_path("backend/src/screener.ts") is False
    assert _is_test_path("backend/src/__tests__/a.test.ts") is True
    assert _is_test_path("backtester/packages/storage/tests/test_x.py") is True
    assert _is_test_path("conftest.py") is True
    assert _is_test_path("services/x/a.spec.ts") is True


def test_area_of_files_keeps_backtester_source_in_mixed_pr():
    # the test-substring bug dropped ALL backtester files -> mislabeled mixed PRs
    files = ["backtester/packages/engine/a.py", "backtester/packages/engine/b.py",
             "backtester/packages/storage/c.py", "market-data/apps/d.py"]
    assert area_of_files(files) == "backtester/packages"


def test_area_of_files_drops_tie_when_strict_majority_required():
    tie = ["aa/bb/x.ts", "aa/bb/y.ts", "cc/dd/z.ts", "cc/dd/w.ts"]     # 2-2, no majority
    assert area_of_files(tie, min_frac=0.5) == ""
    win = ["aa/bb/x.ts", "aa/bb/y.ts", "aa/bb/z.ts", "cc/dd/w.ts"]     # 3-1
    assert area_of_files(win, min_frac=0.5) == "aa/bb"


def test_build_gold_labels_and_filters():
    recs = [
        {"number": 2303, "issue": {"number": 2300, "title": "momentum offset wrong",
                                   "body": "nested momentum"},
         "files": ["backtester/packages/engine/a.py", "backtester/packages/engine/b.py"]},
        {"number": 9, "issue": {}, "files": ["x/y.ts"]},               # no linked issue -> drop
        {"number": 10, "issue": {"number": 11, "title": "t"},
         "files": ["a/b.ts"] * 40},                                    # too many files -> drop
    ]
    gold = build_gold(recs, max_files=18)
    assert len(gold) == 1
    g = gold[0]
    assert g["true_area"] == "backtester/packages" and g["issue_number"] == 2300
    assert "momentum" in g["issue_text"]


def test_score_computes_accuracy_and_misses():
    gold = [{"pr": 1, "issue_number": 1, "issue_text": "a", "true_area": "backend/src"},
            {"pr": 2, "issue_number": 2, "issue_text": "b", "true_area": "backtester/packages"}]
    r = score(gold, lambda t: "backend/src")
    assert r["n"] == 2 and r["correct"] == 1 and r["accuracy"] == 0.5
    assert r["misses"][0]["true"] == "backtester/packages"


def test_keyword_router_routes_risk_to_backend_src():
    fn = keyword_router(LAYER_GT)   # scores the REAL production _route_layer, not a copy
    assert fn("risk_blocked on RELIANCE rule 6.1.1") == "backend/src"


def test_issue_ref_links_pr_to_issue_number():
    # this repo links the closing issue as a trailing (#N) in the PR title
    assert _issue_ref("feat(market-data): resolver (#1749)", "") == 1749
    assert _issue_ref("fix: thing", "Fixes #2300 in the engine") == 2300
    assert _issue_ref("chore: bump deps", "no refs here") is None


def test_nn_loo_predicts_area_from_nearest_past_issue():
    gold = [
        {"pr": 1, "issue_number": 1, "true_area": "backend/src",
         "issue_text": "screener sector crash toFixed is not a function"},
        {"pr": 2, "issue_number": 2, "true_area": "backend/src",
         "issue_text": "screener sector crash toFixed error again"},
        {"pr": 3, "issue_number": 3, "true_area": "backtester/packages",
         "issue_text": "backtest momentum offset nested wrong dates"},
    ]
    r = score_nn_loo(gold, k=1)
    assert r["accuracy"] >= 2 / 3        # the two screener issues match each other


def test_to_index_truncates_and_picks_entry_file():
    gold = [{"pr": 1, "issue_number": 5, "issue_text": "x" * 500, "true_area": "backend/src",
             "files": ["backend/src/__tests__/a.test.ts", "backend/src/a.ts"]}]
    rec = to_index(gold, snippet=220)[0]
    assert len(rec["issue_text"]) == 220
    assert rec["area"] == "backend/src"
    assert rec["entry_file"] == "backend/src/a.ts"      # non-test file preferred


def test_entry_of_prefers_source_file_over_config():
    from harness_engineering.evals.routing_eval import _entry_of
    files = ["backend/src/config.json", "backend/src/pkg.toml", "backend/src/screener.ts"]
    # a .ts source file is a better routing target than a config/lock file
    assert _entry_of(files, "backend/src") == "backend/src/screener.ts"


def test_to_index_dedupes_by_issue_number():
    gold = [
        {"pr": 10, "issue_number": 1672, "issue_text": "same issue text",
         "true_area": "backend/src", "files": ["backend/src/a.ts"]},
        {"pr": 20, "issue_number": 1672, "issue_text": "same issue text",     # dup issue
         "true_area": "backend/src", "files": ["backend/src/a.ts", "backend/src/b.ts", "backend/src/c.ts"]},
        {"pr": 30, "issue_number": 99, "issue_text": "other",
         "true_area": "backtester/packages", "files": ["backtester/packages/x.py"]},
    ]
    idx = to_index(gold)
    assert sorted(r["issue_number"] for r in idx) == [99, 1672]     # 1672 collapsed to one
    assert next(r for r in idx if r["issue_number"] == 1672)["pr"] == 20  # kept the larger fix


def test_dedup_keeps_one_record_per_issue():
    recs = [{"issue_number": 1, "files": ["a"]}, {"issue_number": 1, "files": ["a", "b"]},
            {"issue_number": 2, "files": ["c"]}]
    out = _dedup(recs)
    assert sorted(r["issue_number"] for r in out) == [1, 2]
    assert next(r for r in out if r["issue_number"] == 1)["files"] == ["a", "b"]  # most-files kept


def test_evaluate_cv_dedupes_and_reports_generalization():
    # duplicate-issue rows must NOT let the same issue straddle train/test
    pairs = [("screener crash toFixed", "backend/src", 1),
             ("screener crash toFixed", "backend/src", 1),          # dup of issue 1
             ("backtest momentum offset", "backtester/packages", 2),
             ("backtest momentum offset", "backtester/packages", 2),  # dup of issue 2
             ("chart axis scaling wrong", "frontend/src", 3),
             ("orchestrator token loop", "orchestrator/src", 4)]
    recs = [{"issue_number": n, "issue_text": t, "area": a,
             "entry_file": f"{a}/x.ts"} for (t, a, n) in pairs]
    out = evaluate(recs, k=1, test_every=2)
    assert out["n"] == 4                       # 6 rows -> 4 unique issues after dedup
    for key in ("retrieval_cv", "keyword_cv", "majority_cv", "clean_retrieval"):
        assert key in out


def test_evaluate_cv_retrieval_beats_keyword():
    pairs = [("screener sector crash toFixed not a function", "backend/src"),
             ("screener sector crash toFixed error again", "backend/src"),
             ("screener crashes toFixed once more", "backend/src"),
             ("screener sector toFixed still crashing", "backend/src"),
             ("backtest momentum offset nested wrong dates", "backtester/packages"),
             ("backtest momentum offset scan wrong again", "backtester/packages"),
             ("backtest momentum nested offset broken", "backtester/packages"),
             ("backtest momentum offset dates off", "backtester/packages")]
    recs = [{"issue_number": i, "issue_text": t, "area": a, "entry_file": f"{a}/x.ts"}
            for i, (t, a) in enumerate(pairs)]      # distinct issue per row -> no leakage
    out = evaluate(recs, k=1, test_every=4)
    assert out["retrieval_cv"] > out["keyword_cv"]   # keyword=0; retrieval routes by neighbour


def test_evaluate_embed_beats_jaccard_on_non_lexical_areas():
    # issues that share NO tokens across the set -> Jaccard is blind; a semantic
    # embedder that clusters by area should win. Proves the harness distinguishes them.
    onehot = {"backend/src": [1, 0, 0], "backtester/packages": [0, 1, 0], "frontend/src": [0, 0, 1]}
    pairs = [("alpha uno", "backend/src"), ("beta dos", "backend/src"),
             ("gamma tres", "backend/src"), ("delta cuatro", "backend/src"),
             ("epsilon cinco", "backtester/packages"), ("zeta seis", "backtester/packages"),
             ("eta siete", "backtester/packages"), ("theta ocho", "backtester/packages"),
             ("iota nueve", "frontend/src"), ("kappa diez", "frontend/src"),
             ("mu once", "frontend/src"), ("nu doce", "frontend/src")]
    recs = [{"issue_number": i, "issue_text": t, "area": ar, "entry_file": f"{ar}/x.ts"}
            for i, (t, ar) in enumerate(pairs)]
    t2a = {r["issue_text"]: r["area"] for r in recs}
    out = evaluate_embed(recs, embed_fn=lambda ts: [onehot[t2a[t]] for t in ts], k=1, test_every=4)
    assert out["embed_cv"] >= 0.9                     # perfect semantic clustering
    assert out["embed_cv"] > out["jaccard_cv"]        # Jaccard is blind here
