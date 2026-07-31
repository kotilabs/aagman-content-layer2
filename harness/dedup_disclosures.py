"""dedup_disclosures.py — remove duplicate SEBI disclosure blocks from blog tops."""
from pathlib import Path

WORKDIR = Path("/Users/aryansinha/aagman-harness-run/layer2_full_run/drafts")
DISCLOSURE = "Educational content from Koti Labs (SEBI RIA INA000021951). Not investment advice"

for path in WORKDIR.glob("signal-*-blog.md"):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # Drop leading disclosure-like paragraphs that repeat the same idea.
    kept = []
    seen_disclosure = False
    for line in lines:
        stripped = line.strip()
        is_disclosure = DISCLOSURE in stripped and "RIA" in stripped
        if is_disclosure:
            if seen_disclosure:
                continue
            seen_disclosure = True
        kept.append(line)
    # If the very next non-empty line after first disclosure is a bold duplicate, remove it too.
    cleaned = "\n".join(kept)
    path.write_text(cleaned, encoding="utf-8")
    print(f"Cleaned {path.name}")
