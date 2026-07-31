"""review_blogs.py — run the markets reviewer on the three regenerated blogs."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import litellm

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from harness_content.layer2_full_agents import Layer2MarketsReviewerFull
from harness_core.llm_router import LLMRouter

WORKDIR = REPO / "layer2_full_run"

SIGNALS = {
    "economic-fragmentation-and-persistent-trade-frictions": [
        "blog", "thread", "carousel_linkedin", "carousel_instagram", "infographic"
    ],
    "the-rupee-equity-divergence-in-india": [
        "blog", "thread", "carousel_linkedin", "carousel_instagram", "infographic"
    ],
}


def load_env(path: Path) -> dict:
    env = dict(os.environ)
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def kimi_completion_fn(model: str, prompt: str, **kw):
    resp = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        **kw,
    )
    text = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage") or {}
    tokens = usage.get("total_tokens", 0)
    return {"text": text, "tokens": tokens}


def main():
    env = load_env(Path("/Users/aryansinha/aagman-qa-harness/.env"))
    env["OPENAI_API_KEY"] = env["VISION_API_KEY"]
    env["OPENAI_API_BASE"] = env["VISION_BASE_URL"]
    os.environ.update(env)

    cost_log = str(WORKDIR / "logs" / "cost_log.jsonl")
    router = LLMRouter(
        models_yaml_path=str(REPO / "demo_models.yaml"),
        completion_fn=kimi_completion_fn,
        cost_log_path=cost_log,
    )

    reviewer = Layer2MarketsReviewerFull(router, WORKDIR)

    for signal_id, surfaces in SIGNALS.items():
        print(f"\n=== Reviewing: {signal_id} ===")
        verdict = reviewer.run(signal_id, surfaces)
        print(f"Verdict: {verdict.verdict}")
        print(f"Issues: {verdict.issues}")
        review_path = reviewer.review_path(signal_id)
        print(f"Review file: {review_path}")


if __name__ == "__main__":
    main()
