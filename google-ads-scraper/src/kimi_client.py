"""Kimi API client for image description and inventory summarization."""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import requests

from .config import Config

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3


class KimiClient:
    """Thin client around the Kimi chat completions endpoint."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.kimi_base_url.rstrip("/")
        self.model = config.kimi_model
        self.token = self._load_bearer_token(config.kimi_credentials_path)

    @staticmethod
    def _load_bearer_token(credentials_path: Path) -> str:
        """Load and return a formatted Bearer token from the credentials file."""
        if not credentials_path.exists():
            raise FileNotFoundError(f"Kimi credentials not found at {credentials_path}")
        with credentials_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

        token_type = data.get("token_type", "Bearer")
        access_token = data.get("access_token") or data.get("token")
        if not access_token:
            raise ValueError(f"No access_token or token field found in {credentials_path}")
        return f"{token_type} {access_token}"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
        }

    def _chat(self, messages: list[dict[str, object]], temperature: float = 1.0) -> str | None:
        """Send a chat completion request with simple exponential backoff."""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        for attempt in range(DEFAULT_MAX_RETRIES):
            try:
                response = requests.post(url, headers=self._headers(), json=payload, timeout=60)
                if response.status_code == 429:
                    sleep_seconds = 2 ** attempt
                    logger.warning("Kimi rate limit hit; backing off %s seconds.", sleep_seconds)
                    time.sleep(sleep_seconds)
                    continue
                if response.status_code == 400:
                    logger.warning(
                        "Kimi returned 400; skipping retries. Response: %s",
                        response.text[:200],
                    )
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
            except requests.exceptions.RequestException as exc:
                logger.warning("Kimi request failed (attempt %s): %s", attempt + 1, exc)
                time.sleep(2 ** attempt)

        logger.error("Kimi request failed after %s retries.", DEFAULT_MAX_RETRIES)
        return None

    def describe_image(self, image_url: str) -> str | None:
        """Ask Kimi to describe the ad creative and extract visible text/copy."""
        messages = [
            {
                "role": "system",
                "content": "You are an expert at describing online ad creatives.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Describe this advertisement creative in detail. "
                            "Extract any visible text, headlines, body copy, call-to-action buttons, "
                            "display URLs, brand names, and visual style. Keep the response concise."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ]
        return self._chat(messages)

    def summarize_inventory(self, inventory_text: str) -> str | None:
        """Ask Kimi for a marketing analysis of the raw ad inventory."""
        messages = [
            {
                "role": "system",
                "content": "You are a senior performance marketing analyst.",
            },
            {
                "role": "user",
                "content": (
                    "Analyze the following Google Ads inventory for the advertiser. "
                    "Report on: overarching themes, copy patterns (headlines, body, CTAs), "
                    "visual style, surface/channel strategy, and any notable trends. "
                    "Be concise and actionable.\n\n"
                    f"{inventory_text}"
                ),
            },
        ]
        return self._chat(messages, temperature=1.0)
