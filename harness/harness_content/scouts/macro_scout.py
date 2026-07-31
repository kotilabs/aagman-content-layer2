"""Macro signal scout — weekly deep editorial candidates."""
from datetime import date
from pathlib import Path

from harness_content.scouts.base import SignalScout


class MacroSignalScout(SignalScout):
    prompt_file = "signal_identifier_macro.md"
    lens_name = "macro"

    def digest_path(self, dt=None) -> Path:
        dt = dt or date.today().isoformat()
        return self.signals_dir / f"{dt}-macro-digest.md"
