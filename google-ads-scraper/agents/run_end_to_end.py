#!/usr/bin/env python3
"""CLI entry point to run Strategist then Writer back-to-back."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.strategist.strategist import Strategist  # noqa: E402
from agents.writer.writer import Writer  # noqa: E402


def main() -> None:
    strategist = Strategist(root=ROOT)
    strategy_path, brief_path = strategist.run()

    print("\n" + "=" * 60)
    print("Running writer against the generated brief...")
    print("=" * 60 + "\n")

    writer = Writer(root=ROOT)
    writer.run(brief_path)


if __name__ == "__main__":
    main()
