"""Show what the harness would prioritize RIGHT NOW — the usage-driven do-list.

Ranks open core-product tickets by (severity x real usage weight), highest-impact-first,
and dedups against open PRs (so already-in-flight work is flagged, not recommended).
Needs only `gh` + the committed usage_weights.json snapshot — no DB.

Examples:
    PYTHONPATH=. ./venv312/bin/python harness_engineering/tools/show_recommendations.py
    ... show_recommendations.py --since 2026-06-26 --top 10      # recent tickets only
    ... show_recommendations.py --all-scope                       # include execution/live-trading
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness_engineering.prioritize import (  # noqa: E402
    infer_domain, classify_issue, CORE_DOMAINS)

DIST = Path(__file__).resolve().parents[1] / "distilled"
_SEV = {5: "P0", 4: "P1", 3: "bug", 2: "nfr", 1: "low"}


def _gh(args):
    return json.loads(subprocess.run(args, capture_output=True, text=True).stdout)


def _inflight(repo):
    """issue# -> [open PR#] via the repo's `(#N)` title convention + `closes #N` bodies."""
    prs = _gh(["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "400",
               "--json", "number,title,body"])
    m = {}
    for pr in prs:
        refs = {int(x) for x in re.findall(r"#(\d+)", pr.get("title") or "")}
        for mt in re.finditer(r"(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)"
                              r"\s+#(\d+)", pr.get("body") or "", re.I):
            refs.add(int(mt.group(1)))
        for n in refs:
            m.setdefault(n, []).append(pr["number"])
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="kotilabs/aagman-v2")
    ap.add_argument("--since", help="only issues created on/after YYYY-MM-DD")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--all-scope", action="store_true",
                    help="include execution/live-trading (default: core product only)")
    a = ap.parse_args()

    weights = json.loads((DIST / "usage_weights.json").read_text())
    args = ["gh", "issue", "list", "--repo", a.repo, "--state", "open", "--limit", "400",
            "--json", "number,title,labels,createdAt"]
    if a.since:
        args += ["--search", f"created:>={a.since}"]
    issues = _gh(args)
    inflight = _inflight(a.repo)

    clean, flagged = [], []
    for it in issues:
        labels = [l["name"] for l in it["labels"]]
        dom = infer_domain(it["title"], labels)
        if not a.all_scope and ("live-trading" in labels or dom not in CORE_DOMAINS):
            continue
        _, _, base = classify_issue(it["title"], labels)
        score = round(base * (0.25 + 0.75 * weights.get(dom, 0.0)), 3)
        row = (score, base, it["number"], dom, it["createdAt"][:10], it["title"])
        (flagged if it["number"] in inflight else clean).append(row)
    clean.sort(key=lambda r: (-r[0], -r[1], r[2]))

    print(f"in scope: {len(clean) + len(flagged)}  |  clean (no PR): {len(clean)}  |  "
          f"in-flight: {len(flagged)}\n")
    print(f"{'#':>2} {'issue':>6} {'score':>5} {'sev':>4} {'domain':<16} {'opened':>10}  title")
    for i, (s, b, n, d, day, t) in enumerate(clean[:a.top], 1):
        print(f"{i:>2} #{n:<5} {s:>5} {_SEV[b]:>4} {d:<16} {day:>10}  {t[:58]}")


if __name__ == "__main__":
    main()
