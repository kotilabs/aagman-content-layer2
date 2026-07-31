"""Offline routing eval — measure coding-agent routing against merged-PR ground truth.

Why: you cannot *optimise* a prompt you cannot *score*. The 339 merged PRs are a
free labelled dataset — for a PR that closed an issue, the files it changed reveal
the true area (2-segment path key). We hold (issue_text -> true_area) pairs and
measure how well a router predicts the area. Deterministic, no LLM budget.

This is the measurement backbone for the optimisation ladder: retrieval upgrades,
outcome-scored self-evolution, and DSPy-style prompt search all get judged here.

Two baseline routers ship so there's a comparison from day one:
  - keyword_router: the REAL production RCAAgent._route_layer (4 risk keywords).
  - score_nn_loo: leave-one-out nearest-neighbour over the issue texts — "does an
    incoming issue's closest past issue predict the right area?" (the retrieval
    hypothesis, scored without an LLM).

Build a real gold set (needs `gh`, no LLM budget):
    python3 -m harness_engineering.evals.routing_eval build   # writes routing_gold.json
    python3 -m harness_engineering.evals.routing_eval report  # scores the routers
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from harness_engineering.agents import RCAAgent, _area_of
from harness_engineering.route_index import RouteIndex, VectorRouteIndex, _tokens, jaccard

REPO = "kotilabs/aagman-v2"
_DIST = Path(__file__).resolve().parents[1] / "distilled"
_INDEX = _DIST / "route_index.json"          # committed: title+snippet, redaction-safe
_LAYER_GT = _DIST / "layer_ground_truth.json"


# --------------------------------------------------------------------------- #
# ground truth
# --------------------------------------------------------------------------- #
_TEST_RE = re.compile(
    r"(^|/)__tests__(/|$)|(^|/)tests?(/|$)|(^|/)testing(/|$)|(^|/)__mocks__(/|$)"
    r"|\.(test|spec)\.|(^|/)test_[^/]*\.py$|(^|/)conftest\.py$", re.I)


def _is_test_path(path: str) -> bool:
    """True for real test files. A substring check (`"test" in path`) is WRONG — it
    matches 'backTESTer' and mislabels every backtester PR (adversarial-verify find)."""
    return bool(_TEST_RE.search(path or ""))


def area_of_files(files, ignore_tests: bool = True, min_frac: float = 0.0) -> str:
    """The area (2-seg path key) most non-test files sit under. With min_frac>0 the
    winning area must be a strict majority of that fraction, else '' (drop ties and
    cross-cutting PRs whose 'majority' area is an artifact of file-listing order)."""
    cand = [f for f in (files or []) if f and (not ignore_tests or not _is_test_path(f))]
    cand = cand or [f for f in (files or []) if f]
    if not cand:
        return ""
    area, n = Counter(_area_of(f) for f in cand).most_common(1)[0]
    if n / len(cand) <= min_frac:
        return ""
    return area


def build_gold(pr_records, max_files: int = 18) -> list:
    """Turn merged-PR records into labelled routing examples. Keep only PRs that
    closed an issue and touched a focused set of files (a clean single-area label)."""
    gold = []
    for pr in pr_records or []:
        iss = pr.get("issue") or {}
        files = pr.get("files") or []
        if not iss.get("number") or not files or len(files) > max_files:
            continue
        area = area_of_files(files, min_frac=0.5)   # strict majority -> clean label
        if not area:
            continue
        gold.append({
            "pr": pr.get("number"),
            "issue_number": iss["number"],
            "issue_text": f"{iss.get('title', '')} {iss.get('body', '')}".strip(),
            "true_area": area,
            "files": files,
        })
    return gold


# --------------------------------------------------------------------------- #
# scoring
# --------------------------------------------------------------------------- #
def _true_area(rec) -> str:
    return rec.get("true_area", rec.get("area", ""))


def score(gold, router_fn, name: str = "router") -> dict:
    """Run router_fn(issue_text) -> area over records; report accuracy. Records may
    key the label as 'true_area' (gold) or 'area' (index)."""
    correct, misses = 0, []
    for g in gold:
        pred = router_fn(g["issue_text"])
        if pred == _true_area(g):
            correct += 1
        else:
            misses.append({"pr": g.get("pr"), "issue": g.get("issue_number"),
                           "pred": pred, "true": _true_area(g)})
    n = len(gold)
    return {"router": name, "n": n, "correct": correct,
            "accuracy": (correct / n) if n else 0.0, "misses": misses}


def score_nn_loo(gold, k: int = 1) -> dict:
    """Leave-one-out nearest-neighbour: predict an item's area from its closest
    OTHER item by token Jaccard. Measures the retrieval hypothesis without an LLM."""
    items = [(_tokens(g["issue_text"]), _true_area(g)) for g in gold]
    correct, misses = 0, []
    for i, g in enumerate(gold):
        q = items[i][0]
        ranked = []
        for j, (tj, aj) in enumerate(items):
            if j == i:
                continue
            union = q | tj
            ranked.append((len(q & tj) / len(union) if union else 0.0, aj))
        ranked.sort(key=lambda x: -x[0])
        top = [a for _, a in ranked[:k]]
        pred = Counter(top).most_common(1)[0][0] if top else ""
        if pred == _true_area(g):
            correct += 1
        else:
            misses.append({"issue": g.get("issue_number"), "pred": pred,
                           "true": _true_area(g)})
    n = len(gold)
    return {"router": f"nn-loo-k{k}", "n": n, "correct": correct,
            "accuracy": (correct / n) if n else 0.0, "misses": misses}


# --------------------------------------------------------------------------- #
# index build (issue -> area, entry_file) + honest train/test evaluation
# --------------------------------------------------------------------------- #
_SRC_EXT = (".ts", ".tsx", ".py", ".js", ".jsx", ".mjs", ".cjs", ".sql")


def _entry_of(files, area) -> str:
    """A representative entry file for the area: prefer a real source file over a
    config/docs/lock file, and a non-test file over a test file."""
    in_area = [f for f in files if _area_of(f) == area]
    nontest = [f for f in in_area if not _is_test_path(f)] or in_area or list(files)
    src = [f for f in nontest if f.lower().endswith(_SRC_EXT)]
    pool = src or nontest
    return pool[0] if pool else ""


def _dedup(records) -> list:
    """One record per issue_number (the fix touching the most files — most
    representative). WHY: the same issue is often closed by several merged PRs, and
    duplicate issue_text rows straddling a split are pure train/test leakage."""
    best = {}
    for r in records:
        n = r.get("issue_number")
        if n is None:
            continue
        if n not in best or len(r.get("files", [])) > len(best[n].get("files", [])):
            best[n] = r
    return list(best.values())


def to_index(gold, snippet: int = 220) -> list:
    """Gold -> committable index records (title+snippet only; redaction-safe). Deduped
    by issue so no issue appears twice (leakage guard baked into the artifact)."""
    return [{"pr": g.get("pr"), "issue_number": g.get("issue_number"),
             "issue_text": g["issue_text"][:snippet], "area": g["true_area"],
             "entry_file": _entry_of(g.get("files", []), g["true_area"])}
            for g in _dedup(gold)]


def _folds(records, test_every: int = 4):
    """All `test_every` deterministic folds (every Nth by issue number, each offset) —
    a full cross-validation over the data, not one cherry-picked split."""
    recs = sorted(records, key=lambda r: r.get("issue_number") or 0)
    for off in range(test_every):
        test = [r for i, r in enumerate(recs) if i % test_every == off]
        train = [r for i, r in enumerate(recs) if i % test_every != off]
        yield train, test


def evaluate(records=None, k: int = 3, test_every: int = 4, clean_thresh: float = 0.9) -> dict:
    """Honest cross-validated eval. Dedups by issue (no same-issue leakage), pools
    predictions over ALL folds (no fold cherry-picking), and separately reports the
    leakage-free 'generalization' accuracy on test items whose nearest TRAIN neighbour
    is < clean_thresh similar — the number that says whether retrieval beats memorising
    a near-duplicate. Majority-class baseline included as the bar to beat."""
    records = _dedup(records if records is not None else json.loads(_INDEX.read_text()))
    kw = keyword_router()
    maj_area = Counter(_true_area(r) for r in records).most_common(1)[0][0] if records else ""
    a = dict(ret=0, kw1=0, kwk=0, maj=0, n=0, cret=0, cmaj=0, cn=0)
    fold_ret = []
    for train, test in _folds(records, test_every):
        ri, train_tok = RouteIndex(train), [_tokens(r["issue_text"]) for r in train]
        fc = 0
        for r in test:
            true, q = _true_area(r), _tokens(r["issue_text"])
            p1, pk = ri.predict(r["issue_text"], k=1)[0], ri.predict(r["issue_text"], k=k)[0]
            a["kw1"] += p1 == true; a["ret"] += pk == true
            a["kwk"] += kw(r["issue_text"]) == true; a["maj"] += maj_area == true; a["n"] += 1
            fc += pk == true
            if max((jaccard(q, t) for t in train_tok), default=0.0) < clean_thresh:
                a["cret"] += pk == true; a["cmaj"] += maj_area == true; a["cn"] += 1
        fold_ret.append(fc / len(test) if test else 0.0)
    n, cn = a["n"] or 1, a["cn"] or 1
    return {"n": a["n"], "k": k, "maj_area": maj_area,
            "keyword_cv": a["kwk"] / n, "majority_cv": a["maj"] / n,
            "retrieval_k1_cv": a["kw1"] / n, "retrieval_cv": a["ret"] / n,
            "fold_range": [min(fold_ret), max(fold_ret)],
            "clean_n": a["cn"], "clean_retrieval": a["cret"] / cn, "clean_majority": a["cmaj"] / cn}


def evaluate_embed(records=None, embed_fn=None, k: int = 3, test_every: int = 4,
                   clean_thresh: float = 0.9) -> dict:
    """Same honest CV as evaluate(), but compares EMBEDDING cosine k-NN against the
    token-Jaccard baseline on identical folds. embed_fn(texts)->vectors (cached)."""
    if embed_fn is None:
        from harness_engineering.embeddings import embed as embed_fn
    records = sorted(_dedup(records if records is not None else json.loads(_INDEX.read_text())),
                     key=lambda r: r.get("issue_number") or 0)
    texts = [r["issue_text"] for r in records]
    vecs, tok = embed_fn(texts), [_tokens(t) for t in texts]
    maj = Counter(_true_area(r) for r in records).most_common(1)[0][0] if records else ""
    a = dict(emb=0, jac=0, maj=0, n=0, cemb=0, cjac=0, cmaj=0, cn=0)
    for off in range(test_every):
        te = [i for i in range(len(records)) if i % test_every == off]
        tr = [i for i in range(len(records)) if i % test_every != off]
        vidx = VectorRouteIndex([records[i] for i in tr], [vecs[i] for i in tr])
        jidx = RouteIndex([records[i] for i in tr])
        for i in te:
            true = _true_area(records[i])
            pe = vidx.predict_vec(vecs[i], k=k)[0]
            pj = jidx.predict(records[i]["issue_text"], k=k)[0]
            a["emb"] += pe == true; a["jac"] += pj == true
            a["maj"] += maj == true; a["n"] += 1
            if max((jaccard(tok[i], tok[j]) for j in tr), default=0.0) < clean_thresh:
                a["cemb"] += pe == true; a["cjac"] += pj == true
                a["cmaj"] += maj == true; a["cn"] += 1
    n, cn = a["n"] or 1, a["cn"] or 1
    return {"n": a["n"], "k": k, "maj_area": maj,
            "majority_cv": a["maj"] / n, "jaccard_cv": a["jac"] / n, "embed_cv": a["emb"] / n,
            "clean_n": a["cn"], "clean_majority": a["cmaj"] / cn,
            "clean_jaccard": a["cjac"] / cn, "clean_embed": a["cemb"] / cn}


# --------------------------------------------------------------------------- #
# routers under test
# --------------------------------------------------------------------------- #
def keyword_router(layer_gt_path=None):
    """Wrap the ACTUAL production router (RCAAgent._route_layer) so the eval scores
    real behaviour, not a reimplementation. panel=object() skips panel construction."""
    rca = RCAAgent(None, None, str(layer_gt_path or _LAYER_GT), None, None, panel=object())

    def fn(issue_text: str) -> str:
        layer, entry = rca._route_layer(issue_text)
        return _area_of(entry, layer)
    return fn


# --------------------------------------------------------------------------- #
# gh fetch (I/O; injectable) + CLI
# --------------------------------------------------------------------------- #
def _issue_ref(title: str, body: str = "") -> int | None:
    """This repo links the closing issue as a trailing '(#N)' in the PR title (the
    GitHub closingIssuesReferences graph is unused). Fall back to a 'fixes #N' verb
    in title/body, then any '#N' in the title."""
    m = re.search(r"\(#(\d+)\)\s*$", (title or "").strip())
    if m:
        return int(m.group(1))
    m = re.search(r"(?:fix(?:e[sd])?|close[sd]?|resolve[sd]?)\s+#(\d+)",
                  f"{title}\n{body}", re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"#(\d+)", title or "")
    return int(m.group(1)) if m else None


def _gh_fetch_prs(repo: str, limit: int) -> list:
    """Fetch merged PRs + all issues, then join PR -> issue via the title ref.
    Joining against the ISSUE list (not PRs) self-filters refs that point at PRs,
    since GitHub shares the number space but `gh issue list` returns only issues."""
    prs = json.loads(subprocess.run(
        ["gh", "pr", "list", "--repo", repo, "--state", "merged", "--limit", str(limit),
         "--json", "number,title,body,files"],
        capture_output=True, text=True, check=True).stdout or "[]")
    issues = json.loads(subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--state", "all", "--limit", "2000",
         "--json", "number,title,body"],
        capture_output=True, text=True, check=True).stdout or "[]")
    imap = {i["number"]: i for i in issues}
    recs = []
    for pr in prs:
        ref = _issue_ref(pr.get("title", ""), pr.get("body", ""))
        iss = imap.get(ref)
        if not iss:
            continue
        recs.append({
            "number": pr.get("number"),
            "issue": {"number": iss["number"],
                      "title": iss.get("title", ""), "body": iss.get("body", "")},
            "files": [f.get("path") for f in (pr.get("files") or []) if f.get("path")],
        })
    return recs


def fetch_gold(repo: str = REPO, limit: int = 500, fetch_fn=None) -> list:
    return build_gold((fetch_fn or _gh_fetch_prs)(repo, limit))


def report(records=None) -> str:
    ev = evaluate(records)
    lo, hi = ev["fold_range"]
    return "\n".join([
        f"Routing eval — {ev['n']} unique-issue examples, "
        f"{4}-fold CV (deduped, no same-issue leakage)", "",
        f"  majority-class baseline   {ev['majority_cv']*100:5.1f}%   (always '{ev['maj_area']}')",
        f"  keyword (_route_layer)    {ev['keyword_cv']*100:5.1f}%",
        f"  retrieval nn k=1          {ev['retrieval_k1_cv']*100:5.1f}%",
        f"  retrieval nn k={ev['k']}          {ev['retrieval_cv']*100:5.1f}%   "
        f"(per-fold {lo*100:.0f}-{hi*100:.0f}%)", "",
        f"  GENERALIZATION (leakage-free, {ev['clean_n']} test items whose nearest",
        f"  train neighbour is <0.9 similar):",
        f"    retrieval               {ev['clean_retrieval']*100:5.1f}%",
        f"    majority-class          {ev['clean_majority']*100:5.1f}%   <- the bar retrieval must clear",
    ])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "build":
        gold = fetch_gold(limit=int(sys.argv[2]) if len(sys.argv) > 2 else 500)
        idx = to_index(gold)
        _INDEX.write_text(json.dumps(idx, indent=1))
        print(f"wrote {len(idx)} routing-index records -> {_INDEX}")
    elif cmd == "report":
        print(report())
    elif cmd == "embed":
        from harness_engineering.embeddings import embed as _emb
        from harness_core.run import load_env
        os.environ.setdefault("OPENAI_API_KEY", load_env().get("OPENAI_API_KEY", ""))
        kk = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        ev = evaluate_embed(embed_fn=_emb, k=kk)
        print(f"Embedding cosine vs token-Jaccard — {ev['n']} unique-issue examples, "
              f"4-fold CV (leakage-free), k={ev['k']}\n")
        print(f"  majority-class baseline   {ev['majority_cv']*100:5.1f}%")
        print(f"  token-Jaccard k-NN        {ev['jaccard_cv']*100:5.1f}%")
        print(f"  embedding cosine k-NN     {ev['embed_cv']*100:5.1f}%")
        print(f"\n  leakage-free ({ev['clean_n']}): jaccard {ev['clean_jaccard']*100:.1f}%  "
              f"embed {ev['clean_embed']*100:.1f}%  majority {ev['clean_majority']*100:.1f}%")
    else:
        sys.exit(f"usage: {sys.argv[0]} [build [limit] | report | embed [k]]")
