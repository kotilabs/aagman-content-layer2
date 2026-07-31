"""harness_content/scouts/base.py — base class for signal scouts.

A scout reads a prompt from the Layer 2 prompts/ directory, recalls memory,
calls the router, caches the response, and writes a digest file.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Any


class SignalScout(ABC):
    """Base class for all signal scouts.

    Subclasses define:
        - prompt_file: which Layer 2 prompt to run
        - lens_name: "macro", "realtime", "news", "x", "reddit"
        - digest_name(date): filename for the digest
    """

    prompt_file: str = ""
    lens_name: str = ""

    def __init__(self, router: Any, workdir: str | Path,
                 memory_factory: Any | None = None):
        self.router = router
        self.workdir = Path(workdir)
        self.memory_factory = memory_factory
        self.signals_dir = self.workdir / "signals"
        self.signals_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def digest_path(self, dt: date | str | None = None) -> Path:
        ...

    def run(self, dt: date | str | None = None) -> Path:
        """Run the scout and write the digest."""
        dt = dt or date.today()
        if isinstance(dt, str):
            dt_str = dt
        else:
            dt_str = dt.isoformat()

        digest_path = self.digest_path(dt_str)
        cache = self._cache_path(dt_str)

        if cache.exists():
            text = cache.read_text(encoding="utf-8").strip()
        else:
            prompt = self._build_prompt(dt_str)
            res = self.router.complete(
                "complex_planning",
                prompt,
                domain="content",
                step=f"signal_{self.lens_name}",
                request_id=f"layer2-signal-{self.lens_name}-{dt_str}",
                timeout=0,
            )
            text = res["text"].strip()
            cache.write_text(text, encoding="utf-8")

        digest = self._assemble_digest(dt_str, text)
        digest_path.write_text(digest, encoding="utf-8")
        return digest_path

    def _build_prompt(self, dt: str) -> str:
        from harness_content.layer2_full_agents import _read_prompt
        lessons = self._recall_lessons()
        prompt = _read_prompt(self.prompt_file)
        prompt += (
            "\n\nRun the full workflow above and produce the complete output. "
            "Include every required section."
        )
        if lessons:
            prompt += f"\n\nLESSONS FROM PAST CYCLES:\n{lessons}\n"
        prompt += f"\nPUBLICATION DATE: {dt}\n"
        return prompt

    def _recall_lessons(self) -> str:
        if not self.memory_factory:
            return ""
        mem = self.memory_factory("content", "ideate")
        texts = []
        for lid in mem.top_k(f"signal scouting {self.lens_name}", k=5):
            les = mem.get(lid)
            if les and les.text:
                texts.append(f"- {les.text}")
        return "\n".join(texts)

    def _cache_path(self, dt: str) -> Path:
        return self.signals_dir / f".{dt}-{self.lens_name}-response.md"

    def _assemble_digest(self, dt: str, body: str) -> str:
        return (
            f"# Aagman Layer 2 Signal Digest — {self.lens_name.upper()} — {dt}\n\n"
            f"## {self.lens_name.title()} Lens\n\n{body}\n\n"
            f"---\n\n"
            f"## Operator notes\n\n"
            f"- Review candidates above.\n"
            f"- Pick one signal and the surfaces to produce.\n"
            f"- Write selection to `state/tickets/{dt}-<signal-id>.md`.\n"
        )
