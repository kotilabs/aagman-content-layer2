"""OpenRouter client for cheap vision-based image descriptions."""
from __future__ import annotations

import logging
import time

import requests

from .config import Config

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3


class OpenRouterClient:
    """Thin client around OpenRouter's chat completions endpoint for vision."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.openrouter_base_url.rstrip("/")
        self.model = config.openrouter_model
        self.api_key = config.openrouter_api_key
        self.http_referer = config.openrouter_http_referer
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not configured. Set OPENROUTER_API_KEY."
            )

    def _headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.http_referer:
            headers["HTTP-Referer"] = self.http_referer
        return headers

    def describe_image(
        self,
        image_url: str,
        prompt: str | None = None,
        max_tokens: int = 500,
    ) -> str | None:
        """Ask a cheap vision model to describe an image URL and extract copy."""
        user_prompt = prompt or (
            "Describe this advertisement creative in detail. "
            "Extract any visible text, headlines, body copy, call-to-action buttons, "
            "display URLs, brand names, and visual style. Keep the response concise."
        )
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert at describing online ad creatives. "
                        "Return visible text, headline, body, CTA, and visual style."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
            "max_tokens": max_tokens,
        }

        for attempt in range(DEFAULT_MAX_RETRIES):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                    timeout=60,
                )
                if response.status_code == 429:
                    sleep_seconds = 2 ** attempt
                    logger.warning(
                        "OpenRouter rate limit hit; backing off %s seconds.",
                        sleep_seconds,
                    )
                    time.sleep(sleep_seconds)
                    continue
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content")
                    return content.strip() if content else None
                return None
            except requests.exceptions.Timeout:
                logger.warning("OpenRouter request timed out (attempt %s).", attempt + 1)
                time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as exc:
                logger.warning(
                    "OpenRouter request failed (attempt %s): %s", attempt + 1, exc
                )
                time.sleep(2 ** attempt)

        logger.error("OpenRouter request failed after %s retries.", DEFAULT_MAX_RETRIES)
        return None
