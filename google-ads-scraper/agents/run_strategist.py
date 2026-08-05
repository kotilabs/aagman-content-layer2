#!/usr/bin/env python3
"""CLI entry point for the Performance Marketing Strategist agent."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure google-ads-scraper is on the path.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.strategist.strategist import Strategist  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Performance Marketing Strategist")
    parser.add_argument(
        "--input",
        dest="input_text",
        help="Freeform campaign brief. Runs non-interactively.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Force interactive mode (requires a real TTY).",
    )
    args = parser.parse_args()

    strategist = Strategist(root=ROOT)

    # If no input provided and stdin is not a TTY, refuse to crash with EOFError.
    if args.input_text is None and not args.interactive:
        if not sys.stdin.isatty():
            parser.print_help()
            print(
                "\nError: stdin is not a TTY, so interactive mode is not available here.\n"
                "Either run this in a real terminal, or pass a brief with --input.",
                file=sys.stderr,
            )
            sys.exit(1)
        # stdin is a TTY; safe to go interactive.
        args.interactive = True

    strategist.run(args.input_text, force_interactive=args.interactive)


if __name__ == "__main__":
    main()
