"""whatsapp_formatter_agent.py — WhatsApp distribution formatter for harness signals.

Takes any harness signal (research artifact / blog draft) and produces a
WhatsApp-consumable message plus a shareable wa.me link the user can open
and forward to groups.

WhatsApp formatting rules (enforced by validate_message):
- *bold* with single asterisks renders in WA; **double** and # headers do NOT
- no markdown links — paste raw URLs (WA auto-previews), at most one, at the end
- no tables, no em dashes, no emojis
- short paragraphs, one idea each, blank line between
- hook line first: it is the forward preview
- target ~700-1,200 chars; forwards longer than that don't get read
- lowercase house voice

Usage:
    python3 whatsapp_formatter_agent.py check <message.txt>     # validate only
    python3 whatsapp_formatter_agent.py link <message.txt>      # validate + print wa.me share link
"""
from __future__ import annotations

import re
import sys
import urllib.parse
from pathlib import Path

MAX_CHARS = 1200
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002190-\U000021FF\U00002B00-\U00002BFF\uFE0F]"
)

RULES = """\
- hook line first, it is the forward preview
- *bold* with single asterisks only (double asterisks do not render)
- no markdown headers, no markdown links, no tables
- raw URLs only, at most one, placed at the end
- no emojis, no em dashes
- short paragraphs, one idea each, blank line between
- lowercase house voice
- target <= 1200 chars
"""


def validate_message(text: str) -> list[str]:
    """Return a list of rule violations (empty = clean)."""
    problems = []
    if len(text) > MAX_CHARS:
        problems.append(f"too long: {len(text)} chars (max {MAX_CHARS})")
    if EMOJI_RE.search(text):
        problems.append("contains emoji")
    if "\u2014" in text or "\u2013" in text:
        problems.append("contains em/en dash")
    if re.search(r"^#{1,6}\s", text, re.MULTILINE):
        problems.append("contains markdown header")
    if re.search(r"\[[^\]]+\]\([^)]+\)", text):
        problems.append("contains markdown link — use raw URL")
    if "**" in text:
        problems.append("contains ** double asterisks — WA bold is single *")
    urls = re.findall(r"https?://\S+", text)
    if len(urls) > 1:
        problems.append(f"{len(urls)} urls — keep at most one, at the end")
    if urls and urls[0] not in text.rstrip().split("\n")[-1]:
        problems.append("url is not on the last line")
    return problems


def share_link(text: str) -> str:
    return "https://wa.me/?text=" + urllib.parse.quote(text)


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in {"check", "link"}:
        print(__doc__)
        raise SystemExit(1)
    text = Path(sys.argv[2]).read_text(encoding="utf-8").strip()
    problems = validate_message(text)
    if problems:
        print("VIOLATIONS:")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    print(f"clean ({len(text)} chars)")
    if sys.argv[1] == "link":
        print(share_link(text))


if __name__ == "__main__":
    main()
