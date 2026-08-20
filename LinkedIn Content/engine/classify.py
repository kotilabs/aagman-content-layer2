"""Classify a ticket into exactly one category card via the LLM."""
import re
from pathlib import Path

from . import llm

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = ROOT / "categories"


def list_categories() -> list[tuple[str, str]]:
    """Return [(slug, first-line description)] for each category card."""
    out = []
    for p in sorted(CATEGORIES.glob("*.md")):
        first = next(
            (ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()),
            "",
        )
        out.append((p.stem, first))
    return out


def classify(topic: str, take: str) -> tuple[str, str]:
    """Return (category_slug, reasoning paragraph)."""
    cats = list_categories()
    catalog = "\n".join(f"- {slug}: {desc}" for slug, desc in cats)
    system = (
        "You are a strict content classifier for a LinkedIn writing engine. "
        "You choose exactly one category for a post and explain why."
    )
    user = f"""Choose exactly one category for this LinkedIn post.

RULE: The category is decided by the post's PURPOSE — what the reader walks
away with — never by surface ingredients. A post mentioning a product can
still be a personal story; a post mentioning a market can still be humor.

Categories:
{catalog}

Post topic: {topic}
Founder's take: {take}

Respond in EXACTLY this format (two lines):
CATEGORY: <slug from the list above>
REASONING: <one paragraph explaining the purpose-based choice>"""
    resp = llm.complete(system, user)
    slug_m = re.search(r"^CATEGORY:\s*(\S+)", resp, re.MULTILINE)
    reason_m = re.search(r"^REASONING:\s*(.+?)\s*$", resp, re.MULTILINE | re.DOTALL)
    slug = slug_m.group(1) if slug_m else ""
    valid = {s for s, _ in cats}
    if slug not in valid:
        # fall back: match a slug, or its name (numeric prefix stripped,
        # hyphens as spaces), anywhere in the response text
        low = resp.lower().replace("-", " ")
        slug = next(
            (s for s in valid
             if s in resp or s.split("-", 1)[1].replace("-", " ") in low),
            "",
        )
        if not slug:
            raise RuntimeError(f"Classifier returned no recognizable category. Raw response: {resp[:400]}")
    reasoning = reason_m.group(1).strip() if reason_m else resp.strip()
    return slug, reasoning
