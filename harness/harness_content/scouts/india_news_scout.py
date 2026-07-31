"""India news scout — daily / near-daily Indian market editorial candidates."""
from datetime import date
from pathlib import Path

from harness_content.scouts.base import SignalScout


class IndiaNewsScout(SignalScout):
    prompt_file = "signal_identifier_india_news.md"
    lens_name = "india_news"

    def digest_path(self, dt=None) -> Path:
        dt = dt or date.today().isoformat()
        return self.signals_dir / f"{dt}-india-news-digest.md"
