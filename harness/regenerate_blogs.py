"""regenerate_blogs.py — regenerate the three Layer 2 blog drafts with the
updated depth-first prompts and full research artifacts.

Uses the Kimi API directly (not the file bridge) so it completes in one shot.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import litellm

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from harness_content.layer2_full_agents import Layer2Writer
from harness_core.llm_router import LLMRouter

WORKDIR = REPO / "layer2_full_run"

SIGNALS = [
    "the-endgame-of-the-global-rate-cut-cycle",
    "economic-fragmentation-and-persistent-trade-frictions",
    "the-rupee-equity-divergence-in-india",
]


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

    writer = Layer2Writer(router, WORKDIR)

    for signal_id in SIGNALS:
        print(f"\n=== Regenerating blog: {signal_id} ===")
        path = writer.create(signal_id, "blog", mode="promo")
        text = path.read_text(encoding="utf-8")
        words = len(text.split())
        print(f"Wrote: {path}")
        print(f"Word count: {words}")


if __name__ == "__main__":
    main()
