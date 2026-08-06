"""Load source-of-truth and competitor reports for the ads agents."""
from __future__ import annotations

import re
from pathlib import Path


def load_source_of_truth(root: Path | str | None = None) -> str:
    """Load the Āagman capability source-of-truth document."""
    if root is None:
        root = Path(__file__).resolve().parents[2]  # google-ads-scraper/
    path = Path(root) / "source-of-truth" / "aagman-capability-source-of-truth.md"
    if not path.exists():
        raise FileNotFoundError(f"Source of truth not found at {path}")
    return path.read_text(encoding="utf-8")


def _truncate_ad_copy(content: str, max_ads: int = 15) -> str:
    """Keep the header and first N ad blocks from a detailed ad-copy file."""
    lines = content.splitlines()
    # Find ad block starts like "## Ad 1 — ..."
    ad_starts = [i for i, line in enumerate(lines) if line.strip().startswith("## Ad ")]
    if not ad_starts:
        return content[:6000]
    if len(ad_starts) <= max_ads:
        return content
    cutoff = ad_starts[max_ads]
    truncated = lines[:cutoff] + ["", f"_... {len(ad_starts) - max_ads} more ads omitted for brevity._"]
    return "\n".join(truncated)


def load_competitor_reports(root: Path | str | None = None) -> dict[str, dict[str, str]]:
    """Load compact competitor intelligence.

    Prefers the concise analysis.md. Falls back to the detailed ad-copy file,
    truncated to the first 15 ads to keep prompts small.
    """
    if root is None:
        root = Path(__file__).resolve().parents[2]  # google-ads-scraper/
    reports_dir = Path(root) / "reports"
    competitors: dict[str, dict[str, str]] = {}
    if not reports_dir.exists():
        return competitors

    for competitor_dir in sorted(reports_dir.iterdir()):
        if not competitor_dir.is_dir():
            continue
        name = competitor_dir.name
        for date_dir in sorted(competitor_dir.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            analysis_file = date_dir / "analysis.md"
            copy_file = date_dir / "ad_copy_with_image_descriptions.md"
            if analysis_file.exists():
                competitors[name] = {f"{date_dir.name}/analysis.md": analysis_file.read_text(encoding="utf-8")}
                break
            if copy_file.exists():
                competitors[name] = {
                    f"{date_dir.name}/ad_copy_with_image_descriptions.md": _truncate_ad_copy(
                        copy_file.read_text(encoding="utf-8"), max_ads=15
                    )
                }
                break
    return competitors


def _extract_section(sot: str, title_start: str) -> str:
    """Extract a section from the source of truth by its markdown heading."""
    if title_start not in sot:
        return ""
    start = sot.index(title_start)
    section = sot[start:]
    # Stop at the next top-level or second-level heading.
    next_heading = re.search(r"\n##+ ", section[len(title_start):])
    if next_heading:
        section = section[: len(title_start) + next_heading.start()]
    return section.strip()


def load_product_synopsis(root: Path | str | None = None) -> str:
    """Return a short product synopsis for the writer."""
    sot = load_source_of_truth(root)
    identity = _extract_section(sot, "## 1. Product Identity & Promise")
    who_for = _extract_section(sot, "## 2. Who It Is For")
    return f"{identity}\n\n{who_for}"


def load_safe_claims_for_variant(claim_refs: list[str], root: Path | str | None = None) -> str:
    """Return only the safe-to-claim rows relevant to a variant's claim_refs."""
    sot = load_source_of_truth(root)
    section_16 = _extract_section(sot, "## 16. What Is Safe to Claim")
    if not section_16:
        return "_Safe-to-claim table not found._"

    # Extract the table rows.
    lines = section_16.splitlines()
    header_idx = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("| Area"):
            header_idx = idx
            break
    if header_idx is None:
        return section_16

    # Keep header + separator + rows that match any claim_ref keyword.
    relevant = lines[header_idx : header_idx + 2]
    for line in lines[header_idx + 2 :]:
        if not line.strip().startswith("|"):
            continue
        # Check if any claim_ref keyword appears in this row.
        lowered = line.lower()
        if any(ref.lower() in lowered for ref in claim_refs):
            relevant.append(line)

    if len(relevant) <= 2:
        # Fallback: return the whole table if no rows matched.
        return "\n".join(lines[header_idx:])

    return "\n".join(relevant)


def load_ppc_playbook(root: Path | str | None = None) -> str:
    """Load the strategist's PPC practitioner playbook."""
    if root is None:
        root = Path(__file__).resolve().parents[2]  # google-ads-scraper/
    path = Path(root) / "agents" / "strategist" / "knowledge" / "ppc-playbook.md"
    if not path.exists():
        return "_PPC playbook not found._"
    return path.read_text(encoding="utf-8")


def find_keyword_data(root: Path | str | None = None) -> Path | None:
    """Find the newest Keyword Planner analysis/stats file under strategy/, if any."""
    if root is None:
        root = Path(__file__).resolve().parents[2]
    strategy_dir = Path(root) / "strategy"
    if not strategy_dir.exists():
        return None
    candidates = sorted(
        [
            p
            for p in strategy_dir.iterdir()
            if p.is_file()
            and any(
                marker in p.name.lower()
                for marker in ("keyword-planner-analysis", "keyword-stats", "keyword_planner")
            )
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def load_keyword_data(root: Path | str | None = None, explicit_path: Path | str | None = None) -> str | None:
    """Load keyword demand data (Keyword Planner export/analysis). None if unavailable."""
    path = Path(explicit_path) if explicit_path else find_keyword_data(root)
    if not path or not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def load_competitive_intel_summary(root: Path | str | None = None) -> str:
    """Read the latest competitor analysis.md files under reports/ and return a short markdown summary.

    Only analysis.md files are used (not the raw ad-copy dumps). For each competitor,
    the most recent dated folder is chosen.
    """
    if root is None:
        root = Path(__file__).resolve().parents[2]  # google-ads-scraper/
    reports_dir = Path(root) / "reports"
    if not reports_dir.exists():
        return "_No competitor reports found._"

    summaries: list[str] = []
    for competitor_dir in sorted(reports_dir.iterdir()):
        if not competitor_dir.is_dir():
            continue
        name = competitor_dir.name
        latest_analysis: str | None = None
        for date_dir in sorted(competitor_dir.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            analysis_file = date_dir / "analysis.md"
            if analysis_file.exists():
                latest_analysis = analysis_file.read_text(encoding="utf-8")
                break
        if not latest_analysis:
            continue

        snapshot_match = re.search(r"\*\*Snapshot:\*\*\s*(.+?)(?:\n\n|\n---|$)", latest_analysis, re.DOTALL)
        bottom_match = re.search(r"\*\*Bottom line:\*\*\s*(.+)", latest_analysis)
        snapshot = snapshot_match.group(1).strip() if snapshot_match else ""
        bottom = bottom_match.group(1).strip() if bottom_match else ""

        parts = [f"## Competitor: {name}", ""]
        if snapshot:
            parts.append(f"**Snapshot:** {snapshot}")
            parts.append("")
        if bottom:
            parts.append(f"**Bottom line:** {bottom}")
        if not snapshot and not bottom:
            snippet = latest_analysis[:800].strip()
            parts.append(snippet)

        summaries.append("\n".join(parts))

    if not summaries:
        return "_No competitor analysis files found._"
    return "\n\n".join(summaries)


def build_writer_context(variant: dict, root: Path | str | None = None) -> str:
    """Build a minimal context block for the writer from one variant's claim_refs."""
    synopsis = load_product_synopsis(root)
    claims = load_safe_claims_for_variant(variant.get("claim_refs", []), root)

    return (
        "=== PRODUCT SYNOPSIS ===\n"
        f"{synopsis}\n\n"
        "=== SAFE CLAIMS FOR THIS VARIANT ===\n"
        f"{claims}\n\n"
        "Use ONLY the capabilities listed above as 'Yes' or 'Partially' in your copy. "
        "Do not invent features. 'No' rows are forbidden."
    )


def build_context_block(root: Path | str | None = None, compact: bool = False) -> str:
    """Build a single text block containing source of truth + compact competitor reports."""
    if compact:
        return build_compact_context(root)

    sot = load_source_of_truth(root)
    competitors = load_competitor_reports(root)
    playbook = load_ppc_playbook(root)

    lines = [
        "# Āagman Capability Source of Truth\n",
        sot,
        "\n---\n",
        "# PPC Playbook (practitioner knowledge — follow it)\n",
        playbook,
        "\n---\n",
        "# Competitive Ad Intelligence\n",
    ]

    if not competitors:
        lines.append("_No competitor reports found. Run the Google Ads scraper first._\n")
        return "\n".join(lines)

    for name, files in sorted(competitors.items()):
        lines.append(f"\n## Competitor: {name}\n")
        for filename, content in sorted(files.items()):
            lines.append(f"\n### {filename}\n")
            lines.append(content)
            lines.append("")

    return "\n".join(lines)
