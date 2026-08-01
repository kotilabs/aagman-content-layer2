"""Conversational analytics interface for the Layer 2 analytics agent.

Usage:
    ./harness/venv/bin/python harness/chat_analytics.py
    ./harness/venv/bin/python harness/chat_analytics.py --metrics-path layer2_full_run/analytics/2026-08-01-buffer-metrics.json

The script loads the latest normalized metrics file and starts a REPL where you
can ask questions about the data in natural language. Examples:

    > which post got the highest impressions?
    > compare linkedin vs instagram performance
    > what topics performed best in the last 30 days?
    > summarize the substack numbers
    > why do you think the rupee post outperformed?

Type `exit` or `quit` to leave.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any


def _load_env(repo: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    env_path = repo / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env.setdefault(k.strip(), v.strip())
    env.update(os.environ)
    return env


def _latest_metrics(workdir: Path) -> Path:
    candidates = sorted(workdir.glob("analytics/*-buffer-metrics.json"))
    if not candidates:
        raise FileNotFoundError(f"No metrics files found in {workdir / 'analytics'}")
    return candidates[-1]


def _build_system_prompt(data: dict[str, Any]) -> str:
    lookback = data.get("lookback_days", 30)
    posts = data.get("posts", [])
    aggregates = data.get("aggregates", {})
    channels = data.get("channels", [])
    surfaces = sorted({p.get("surface_label", p.get("surface", "unknown")) for p in posts})
    topic_buckets = sorted({p.get("topic_bucket", "other") for p in posts})

    return f"""You are an analytics assistant for a financial content brand.
You have access to the following content performance dataset.
Answer questions truthfully based only on the data provided.
Do not invent metrics. If data is missing, say it is missing.
Use medians for small samples. Separate reach (impressions/deliveries/views) from engagement quality.

Dataset summary:
- Date range: {lookback} days ending {date.today().isoformat()}
- Total posts: {len(posts)}
- Surfaces: {', '.join(surfaces) if surfaces else 'none'}
- Topic buckets: {', '.join(topic_buckets) if topic_buckets else 'none'}
- Buffer channels: {', '.join(c.get('display_name', c.get('name', c.get('service'))) for c in channels) if channels else 'none'}
- Aggregates: {json.dumps(aggregates, indent=2, default=str)}

For each post, the available fields are: id, title, surface, surface_label, publish_date, topic_bucket, creative_description, link_in_post, link_location, metrics, asset_descriptions.

Rules:
1. Cite specific post titles and numbers when making claims.
2. Flag small samples (n < 5 per cluster) as low confidence.
3. Do not give buy/sell advice.
4. Keep answers concise unless asked for detail.
5. If the user asks about a metric that is not present, say so.
"""


def _summarize_posts(posts: list[dict[str, Any]], max_posts: int | None = None) -> str:
    if max_posts is not None and len(posts) > max_posts:
        posts = posts[:max_posts]
        note = f"\n[Showing first {max_posts} posts; full dataset is larger.]"
    else:
        note = ""
    return json.dumps(posts, indent=2, default=str) + note


def _build_messages(system: str, data_json: str, history: list[dict[str, str]], question: str) -> list[dict[str, str]]:
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Here is the full normalized dataset:\n\n```json\n{data_json}\n```\n\nI will ask you questions about this data."},
        {"role": "assistant", "content": "Got it. I have the dataset and will answer based only on the metrics and posts provided. Ask away."},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": question})
    return messages


def _format_history_for_prompt(history: list[dict[str, str]]) -> str:
    lines = []
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)


def _direct_completion(prompt: str, model: str, api_key: str) -> str:
    """Call a model directly via litellm, bypassing the file-based bridge."""
    try:
        import litellm
    except ImportError as e:
        raise RuntimeError("litellm is required for --direct-llm. Install: ./harness/venv/bin/pip install litellm") from e

    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        api_key=api_key,
        temperature=0.7,
        max_tokens=2000,
    )
    return response["choices"][0]["message"]["content"]


def main() -> None:
    ap = argparse.ArgumentParser("chat_analytics.py")
    ap.add_argument("--metrics-path", default=None,
                    help="Path to a normalized metrics JSON file (defaults to the latest file).")
    ap.add_argument("--non-interactive", action="store_true",
                    help="Skip interactive prompts and use defaults.")
    ap.add_argument("--direct-llm", action="store_true",
                    help="Use OpenAI directly for answers instead of the file-based bridge (requires OPENAI_API_KEY).")
    ap.add_argument("--openai-api-key", default=None,
                    help="OpenAI API key for --direct-llm (or set OPENAI_API_KEY in .env).")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent
    env = _load_env(repo)
    workdir = repo / "layer2_full_run"

    if args.metrics_path:
        metrics_path = Path(args.metrics_path).expanduser().resolve()
        if not metrics_path.exists():
            raise SystemExit(f"Metrics file not found: {metrics_path}")
    else:
        metrics_path = _latest_metrics(workdir)
    print(f"Loaded metrics: {metrics_path}")

    data = json.loads(metrics_path.read_text(encoding="utf-8"))
    posts = data.get("posts", [])
    if not posts:
        print("No posts found in metrics file.")
        raise SystemExit(1)

    system_prompt = _build_system_prompt(data)
    # Keep the full dataset in context. If it gets too large, the bridge/LLM
    # will truncate; the summary at the top gives the assistant a fallback.
    data_json = json.dumps(data, indent=2, default=str)

    direct_model = "gpt-4o" if args.direct_llm else None
    openai_api_key = args.openai_api_key or env.get("OPENAI_API_KEY")

    router = None
    if not direct_model:
        from run_layer2_full import build_services
        services = build_services(workdir, env)
        router = services.router
        print("Using file-based LLM bridge. Each answer will wait for a response file.")
    else:
        print("Using direct LLM (gpt-4o). Answers will return immediately.")

    print("\nAnalytics chat ready. Ask questions about the data.")
    print("Type 'exit' or 'quit' to leave.\n")

    history: list[dict[str, str]] = []

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        messages = _build_messages(system_prompt, data_json, history, question)
        # Flatten messages into a single prompt for the router, which expects a prompt string.
        prompt = (
            "You are having a conversation about a content analytics dataset.\n\n"
            + system_prompt
            + "\n\n--- DATASET ---\n\n```json\n" + data_json + "\n```\n"
            + "\n\n--- CONVERSATION HISTORY ---\n" + _format_history_for_prompt(history)
            + "\n\nUser: " + question
            + "\n\nAssistant:"
        )

        try:
            if direct_model:
                if not openai_api_key:
                    raise RuntimeError("OPENAI_API_KEY not set. Add it to harness/.env or pass --openai-api-key.")
                answer = _direct_completion(prompt, direct_model, openai_api_key).strip()
            else:
                assert router is not None
                res = router.complete("complex_planning", prompt, domain="content", step="analytics_chat")
                answer = res.get("text", "").strip()
        except Exception as e:
            answer = f"Error calling router: {e}"

        print(answer)
        print()

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

        # Prevent unbounded context growth.
        if len(history) > 20:
            history = history[-20:]


if __name__ == "__main__":
    main()
