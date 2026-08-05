"""Shared LLM helper for the ads agents."""
from __future__ import annotations

import sys
from pathlib import Path

# Allow importing the scraper's src package.
_SCRAPER_ROOT = Path(__file__).resolve().parents[2]
if str(_SCRAPER_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRAPER_ROOT))

from src.config import Config  # noqa: E402
from src.kimi_client import KimiClient  # noqa: E402


class _AdsKimiClient(KimiClient):
    """Kimi client with a longer timeout for large strategist prompts."""

    REQUEST_TIMEOUT = 180

    def _chat(self, messages: list[dict[str, object]], temperature: float = 1.0) -> str | None:
        import logging
        import time

        import requests

        logger = logging.getLogger(__name__)
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        for attempt in range(3):
            try:
                response = requests.post(
                    url, headers=self._headers(), json=payload, timeout=self.REQUEST_TIMEOUT
                )
                if response.status_code == 429:
                    sleep_seconds = 2 ** attempt
                    logger.warning("Kimi rate limit hit; backing off %s seconds.", sleep_seconds)
                    time.sleep(sleep_seconds)
                    continue
                if response.status_code == 400:
                    logger.warning("Kimi returned 400; skipping retries. Response: %s", response.text[:200])
                    return None
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content")
                    return content.strip() if content else None
                return None
            except requests.exceptions.Timeout:
                logger.warning("Kimi request timed out (attempt %s).", attempt + 1)
                time.sleep(2 ** attempt)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Kimi request failed (attempt %s): %s", attempt + 1, exc)
                time.sleep(2 ** attempt)

        logger.error("Kimi request failed after retries.")
        return None


class AdsLLM:
    """Thin wrapper around KimiClient for the ads agents."""

    # The configured Kimi model only supports temperature=1.
    TEMPERATURE = 1.0

    def __init__(self):
        self.config = Config()
        self.config.validate()
        self.client = _AdsKimiClient(self.config)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Return the LLM response text; raise on failure."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.client._chat(messages, temperature=self.TEMPERATURE)
        if response is None:
            raise RuntimeError("LLM call returned no response (rate limited or error).")
        return response
