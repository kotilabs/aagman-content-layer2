#!/usr/bin/env python3
"""CLI entry point for the Performance Marketing Strategist agent."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure google-ads-scraper is on the path.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.strategist.strategist import Strategist  # noqa: E402


def main() -> None:
    strategist = Strategist(root=ROOT)
    strategist.run()


if __name__ == "__main__":
    main()
