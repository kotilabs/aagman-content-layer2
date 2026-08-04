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

    def validate(self):
        if not self.kimi_credentials_path.exists():
            raise FileNotFoundError(
                f"Kimi credentials not found at {self.kimi_credentials_path}. "
                "Set KIMI_CODE_CREDENTIALS or run `kimi-code login`."
            )
