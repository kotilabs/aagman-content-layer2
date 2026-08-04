"""Configuration loader for the scraper."""
import os
from pathlib import Path


def default_credentials_path() -> Path:
    return Path.home() / ".kimi-code" / "credentials" / "kimi-code.json"


class Config:
    def __init__(self):
        self.max_ads = int(os.getenv("MAX_ADS", "0")) or None
        self.headless = os.getenv("HEADLESS", "true").lower() != "false"
        self.kimi_credentials_path = Path(
            os.getenv("KIMI_CODE_CREDENTIALS", default_credentials_path())
        )
        self.kimi_base_url = os.getenv("KIMI_BASE_URL", "https://api.kimi.com/coding/v1")
        self.kimi_model = os.getenv("KIMI_MODEL", "k3")
        self.delay_seconds = float(os.getenv("DELAY_SECONDS", "2"))
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "output"))

        # OpenRouter vision settings
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv(
            "OPENROUTER_MODEL", "google/gemini-2.5-flash-lite"
        )
        self.openrouter_base_url = os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self.openrouter_http_referer = os.getenv("OPENROUTER_HTTP_REFERER", "")

    def validate(self):
        if not self.kimi_credentials_path.exists():
            raise FileNotFoundError(
                f"Kimi credentials not found at {self.kimi_credentials_path}. "
                "Set KIMI_CODE_CREDENTIALS or run `kimi-code login`."
            )
