#!/usr/bin/env python3
"""CLI entry point for the Ad Copy Writer agent."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.writer.writer import Writer  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ad Copy Writer")
    parser.add_argument("brief", help="Path to creative brief YAML")
    parser.add_argument("--name", default=None, help="Optional output filename stem (defaults to campaign name)")
    args = parser.parse_args()

    writer = Writer(root=ROOT)
    writer.run(args.brief, out_stem=args.name)


if __name__ == "__main__":
    main()
