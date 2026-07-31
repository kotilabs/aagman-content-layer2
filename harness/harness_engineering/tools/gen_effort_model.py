"""Regenerate harness_engineering/distilled/effort_model.json from merged-PR diff sizes.

est_tokens (the per-cycle CREATE budget math) is anchored on the REAL merged-PR
change-size distribution (median / p75 lines). The size distribution + severity ratio
are real; the lines->tokens factor below is a documented ESTIMATE.

BETTER later: once CREATE logs real fix cost (task_type=code_execution rows appear in
logs/cost_log.jsonl — see HANDOFF), recalibrate the anchor from measured tokens and set
create_samples. Until then this PR-size proxy is the honest best available.

Run:  ./venv312/bin/python harness_engineering/tools/gen_effort_model.py [owner/repo]
"""
import json
import statistics
import subprocess
import sys
from pathlib import Path

REPO = sys.argv[1] if len(sys.argv) > 1 else "kotilabs/aagman-v2"
OUT = Path(__file__).resolve().parents[1] / "distilled" / "effort_model.json"

READ_TOKENS = 30_000     # context the fixer reads: entry file + co-change siblings + tests
PER_LINE = 40            # generate + reason per changed line
RETRY = 1.5              # avg CREATE revise cycles (loop_limit 3, not always exercised)


def main():
    prs = json.loads(subprocess.run(
        ["gh", "pr", "list", "--repo", REPO, "--state", "merged", "--limit", "500",
         "--json", "additions,deletions"], capture_output=True, text=True).stdout)
    sizes = sorted((p["additions"] or 0) + (p["deletions"] or 0)
                   for p in prs if (p["additions"] or 0) + (p["deletions"] or 0) <= 8000)
    median = statistics.median(sizes)
    p75 = sizes[int(len(sizes) * 0.75)]

    def est(lines):
        return int(round((READ_TOKENS + lines * PER_LINE * RETRY) / 1000.0)) * 1000

    model = {
        "base": est(median),
        "p0": est(p75),
        "feature": est(median * 1.3),
        "create_samples": 0,
        "_provenance": (
            f"Anchored on {len(sizes)} merged PRs: median {int(median)} / p75 {p75} changed "
            f"lines (real). tokens = {READ_TOKENS} read + lines*{PER_LINE}*{RETRY} retry. "
            f"Size distribution + severity ratio (p0=p75) are REAL; the lines->tokens factor "
            f"is an ESTIMATE — recalibrate when CREATE logs code_execution tokens to cost_log."
        ),
    }
    OUT.write_text(json.dumps(model, indent=2) + "\n")
    print(f"median={int(median)} p75={p75} n={len(sizes)}")
    print(json.dumps(model, indent=2))


if __name__ == "__main__":
    main()
