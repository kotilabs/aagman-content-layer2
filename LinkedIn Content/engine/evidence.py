"""Performance evidence store: performance/evidence.md, split on '## ' headers."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "performance" / "evidence.md"
CATEGORIES = ROOT / "categories"


def _sections() -> dict:
    """Return {header: body} for each '## Header' section; {} if file missing."""
    if not EVIDENCE.exists():
        return {}
    text = EVIDENCE.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^## (.+?)\s*$\n(.*?)(?=^## |\Z)", text,
                         re.MULTILINE | re.DOTALL):
        out[m.group(1).strip()] = m.group(2).strip()
    return out


def _matched_slug(think_note: str):
    """First category slug (with or without its numeric prefix) named in the SHAPE TAG."""
    m = re.search(r"SHAPE TAG:\s*(.+)", think_note)
    tag = m.group(1).lower() if m else ""
    for p in sorted(CATEGORIES.glob("*.md")):
        slug = p.stem
        bare = re.sub(r"^\d+-", "", slug)
        if slug in tag or bare in tag:
            return slug
    return None


def evidence_for(think_note: str) -> str:
    """Universal section + the section for the shape tag's primary card (if any).
    Empty string when nothing is available — callers omit silently."""
    sections = _sections()
    if not sections:
        return ""
    parts = []
    if "Universal" in sections:
        parts.append(f"## Universal\n{sections['Universal']}")
    slug = _matched_slug(think_note)
    if slug and slug in sections:
        parts.append(f"## {slug}\n{sections[slug]}")
    return "\n\n".join(parts)
