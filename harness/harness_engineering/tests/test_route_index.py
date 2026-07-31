"""TDD: production retrieval router (issue text -> area/entry_file, k-NN)."""
from harness_engineering.route_index import (
    RouteIndex, _tokens, jaccard, cosine, VectorRouteIndex,
)


def test_tokens_and_jaccard():
    assert _tokens("Screener CRASH toFixed a") == {"screener", "crash", "tofixed"}
    assert jaccard({"a", "b"}, {"b", "c"}) == 1 / 3
    assert jaccard(set(), set()) == 0.0


def test_predict_returns_majority_area_and_entry_of_nearest():
    ex = [
        {"issue_text": "screener sector crash toFixed not a function",
         "area": "backend/src", "entry_file": "backend/src/screener.ts"},
        {"issue_text": "screener sector crash toFixed again error",
         "area": "backend/src", "entry_file": "backend/src/screener.ts"},
        {"issue_text": "backtest momentum offset nested wrong",
         "area": "backtester/packages", "entry_file": "backtester/packages/engine/mom.py"},
    ]
    area, entry = RouteIndex(ex).predict("screener crashed with toFixed", k=3)
    assert area == "backend/src"
    assert entry == "backend/src/screener.ts"


def test_predict_empty_on_no_overlap_or_empty_index():
    assert RouteIndex([]).predict("anything") == ("", "")
    ri = RouteIndex([{"issue_text": "backtest momentum",
                      "area": "backtester/packages", "entry_file": "x.py"}])
    assert ri.predict("zzz qqq www") == ("", "")   # no shared tokens -> no guess


def test_load_missing_file_is_empty_not_error():
    assert RouteIndex.load("/nonexistent/route_index.json").predict("x") == ("", "")


def test_cosine():
    assert cosine([1, 0], [1, 0]) == 1.0
    assert cosine([1, 0], [0, 1]) == 0.0
    assert abs(cosine([1, 1], [1, 0]) - (1 / 2 ** 0.5)) < 1e-9
    assert cosine([0, 0], [1, 0]) == 0.0          # zero vector -> 0, no divide error


def test_vector_route_index_predicts_majority_area_of_nearest_by_cosine():
    ex = [{"area": "backend/src", "entry_file": "a.ts"},
          {"area": "backend/src", "entry_file": "a.ts"},
          {"area": "backtester/packages", "entry_file": "m.py"}]
    vecs = [[1, 0, 0], [0.9, 0.1, 0], [0, 0, 1]]
    area, entry = VectorRouteIndex(ex, vecs).predict_vec([1, 0, 0], k=2)
    assert area == "backend/src" and entry == "a.ts"


def test_vector_route_index_empty_is_safe():
    assert VectorRouteIndex([], []).predict_vec([1, 0]) == ("", "")
    assert VectorRouteIndex([{"area": "x"}], [[1, 0]]).predict_vec([]) == ("", "")
