"""kimi_code_bridge.py — Kimi Code CLI as the LLM provider.

This bridge lets the harness run with no external API keys. When the harness
needs an LLM completion, the bridge writes the prompt to a request file and
polls for a response file. A human operator or the Kimi Code session provides
the response by writing it to the expected response path.

The bridge is intentionally simple: it is the seam between the harness's
LLMRouter and the Kimi Code runtime. It does not generate text itself.
"""
from __future__ import annotations

import sys
import time
import uuid
from pathlib import Path


class AwaitingResponseError(TimeoutError):
    """Raised when timeout=0 and no response file exists yet.

    The request file has been written; the caller (or an assistant) must write
    the response file and retry.
    """

    def __init__(self, req_id: str, req_file: Path, resp_file: Path):
        self.req_id = req_id
        self.req_file = req_file
        self.resp_file = resp_file
        super().__init__(
            f"Awaiting response for {req_id}. Write response to: {resp_file}"
        )


def _strip_response_header(text: str) -> str:
    """Strip a leading '# Title' header block if the responder added one."""
    if not text.startswith("# "):
        return text
    lines = text.splitlines()
    in_header = False
    body_lines = []
    for line in lines:
        if line.startswith("# "):
            in_header = True
            continue
        if in_header and line.strip() == "":
            in_header = False
            continue
        if not in_header:
            body_lines.append(line)
    return "\n".join(body_lines).strip()


def make_kimi_code_bridge(request_dir: str | Path,
                          response_dir: str | Path,
                          poll_interval: float = 2.0,
                          timeout: float | None = None):
    """Return a completion_fn for LLMRouter.

    Args:
        request_dir: where prompt request files are written.
        response_dir: where response files are expected.
        poll_interval: seconds between polls.
        timeout: max seconds to wait; None = no timeout.

    The returned callable accepts two optional kwargs:
        request_id: stable id for resumable requests (default: random 12-char).
        timeout:    per-call timeout override. Use 0 to write the request file
                    and raise AwaitingResponseError immediately instead of polling.

    Returns:
        A callable with signature (model, prompt, **kw) -> {"text": str, "tokens": int}.
    """
    request_dir = Path(request_dir)
    response_dir = Path(response_dir)
    request_dir.mkdir(parents=True, exist_ok=True)
    response_dir.mkdir(parents=True, exist_ok=True)

    def completion_fn(model: str, prompt: str, **kw):
        req_id = kw.get("request_id") or uuid.uuid4().hex[:12]
        req_file = request_dir / f"{req_id}.md"
        resp_file = response_dir / f"{req_id}.md"

        # Resumable: if a response already exists, consume it and return.
        if resp_file.exists():
            text = resp_file.read_text(encoding="utf-8")
            resp_file.unlink(missing_ok=True)
            req_file.unlink(missing_ok=True)
            text = _strip_response_header(text)
            tokens = int(len(text.split()) * 1.3)
            return {"text": text, "tokens": tokens}

        # Write the request so Kimi Code can see it.
        header = (
            f"# LLM Request\n\n"
            f"- model: `{model}`\n"
            f"- request id: `{req_id}`\n"
            f"- response path: `{resp_file}`\n\n"
            f"---\n\n"
        )
        req_file.write_text(header + prompt, encoding="utf-8")

        print(f"\n[KIMI_CODE_BRIDGE] Request {req_id} waiting for response at: {resp_file}",
              flush=True)

        call_timeout = kw.get("timeout")
        if call_timeout is None:
            call_timeout = timeout

        # Non-blocking mode: let the assistant provide the response out-of-band.
        if call_timeout == 0:
            raise AwaitingResponseError(req_id, req_file, resp_file)

        # Poll for the response file.
        waited = 0.0
        while True:
            if resp_file.exists():
                text = resp_file.read_text(encoding="utf-8")
                resp_file.unlink(missing_ok=True)
                req_file.unlink(missing_ok=True)
                text = _strip_response_header(text)
                tokens = int(len(text.split()) * 1.3)
                return {"text": text, "tokens": tokens}

            time.sleep(poll_interval)
            if call_timeout is not None:
                waited += poll_interval
                if waited >= call_timeout:
                    req_file.unlink(missing_ok=True)
                    raise TimeoutError(
                        f"Kimi Code did not provide a response for {req_id} within {call_timeout}s"
                    )

    return completion_fn
