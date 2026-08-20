"""Model-agnostic LLM call. Backends selected via env vars."""
import json
import os
import shutil
import subprocess
import urllib.request
import urllib.error


def _post(url: str, headers: dict, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM API error {e.code}: {body}") from e


def complete(system: str, user: str) -> str:
    """Send a system+user prompt to whichever LLM backend is configured."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        data = _post(
            "https://api.anthropic.com/v1/messages",
            {
                "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
            },
            {
                "model": "claude-sonnet-4-5",
                "max_tokens": 4096,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
        )
        return "".join(b.get("text", "") for b in data.get("content", []))

    if os.environ.get("OPENAI_API_KEY"):
        data = _post(
            "https://api.openai.com/v1/chat/completions",
            {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
            {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        return data["choices"][0]["message"]["content"]

    if shutil.which("kimi"):
        prompt = (
            "[IMPORTANT: You are being called as a pure text-completion backend. "
            "Do NOT use any tools, web search, or file access. Answer with plain text only, "
            "from your own knowledge. If you are unsure of a fact, say so in the answer.]\n\n"
            f"[SYSTEM]\n{system}\n\n[USER]\n{user}"
        )
        last_err = None
        for attempt in range(2):  # kimi -p occasionally hangs; kill and retry once
            try:
                out = subprocess.run(
                    ["kimi", "--output-format", "stream-json", "-p", prompt],
                    capture_output=True, text=True, timeout=300,
                    stdin=subprocess.DEVNULL,
                    env={**os.environ, "TERM": "dumb", "NO_COLOR": "1"},
                )
                if out.returncode != 0:
                    raise RuntimeError(f"kimi CLI failed: {out.stderr.strip()[:500]}")
                parts = []
                for ln in out.stdout.splitlines():
                    ln = ln.strip()
                    if not ln.startswith("{"):
                        continue
                    try:
                        evt = json.loads(ln)
                    except json.JSONDecodeError:
                        continue
                    if evt.get("role") == "assistant" and evt.get("content"):
                        parts.append(evt["content"])
                if not parts:
                    raise RuntimeError(f"kimi CLI returned no assistant content: {out.stdout[:300]}")
                return "\n".join(parts).strip()
            except subprocess.TimeoutExpired as e:
                last_err = e
        raise RuntimeError("kimi CLI hung twice; giving up") from last_err

    raise RuntimeError(
        "No LLM backend configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY "
        "(in your environment or in a .env file at the project root — see "
        ".env.example), or install the kimi CLI."
    )
