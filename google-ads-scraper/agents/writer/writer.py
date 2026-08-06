"""Ad Copy Writer agent — smaller-single-format-calls approach."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from ..shared.context_loader import build_writer_context, load_competitive_intel_summary
from ..shared.llm import AdsLLM
from .prompt_builder import PromptBuilder
from .validators import validate_copy_pack, ValidationError


FORMATS_SPEC = {
    "google_rsa": {
        "description": "Google Responsive Search Ad",
        "headlines": {"count": 10, "max_chars": 30},
        "descriptions": {"count": 4, "max_chars": 90},
    },
    "linkedin": {
        "description": "LinkedIn sponsored content",
        "intro": "Introductory paragraph",
        "headline": {"max_chars": 70},
        "description": "Supporting description",
    },
}


class Writer:
    """Generates format-ready ad copy from a creative brief."""

    def __init__(self, root: Path | str | None = None, llm: AdsLLM | None = None):
        self.root = Path(root) if root else Path(__file__).resolve().parents[2]
        self.llm = llm or AdsLLM()
        self.prompt_builder = PromptBuilder(root=self.root)
        # Smaller calls should return quickly; cap per-call wall time so a full
        # 15-variant brief can finish in a reasonable window.
        self.llm.client.REQUEST_TIMEOUT = 60

    def load_brief(self, brief_path: Path | str) -> dict:
        """Load a YAML creative brief."""
        path = Path(brief_path)
        if not path.exists():
            raise FileNotFoundError(f"Brief not found: {path}")
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)

    def _competitive_intel(self, brief: dict) -> str | None:
        """Return competitor intel only when the brief does not already supply it."""
        if brief.get("competitive_intel"):
            return None
        return load_competitive_intel_summary(self.root)

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make a single LLM call and return cleaned text."""
        raw = self.llm.chat(system_prompt, user_prompt)
        # Strip common accidental wrappers.
        raw = re.sub(r"^```(?:json|text)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
        return raw

    def _parse_numbered_list(self, raw: str, expected_count: int | None = None) -> list[str]:
        """Extract items from a numbered list such as '1. Foo'."""
        # Lines that start with a number and a delimiter.
        pattern = re.compile(r"^\s*(?:\d+[.):\-]|\*)\s*(.+)$", re.MULTILINE)
        items = [m.group(1).strip() for m in pattern.finditer(raw)]

        if not items:
            # Fallback: split on newlines and strip bullets/dashes.
            items = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]

        # Clean up any lingering markdown bold/italic.
        items = [re.sub(r"\*\*?", "", item).strip() for item in items]

        if expected_count is not None:
            # If we got more, truncate; if fewer, leave as-is and let validation report it.
            items = items[:expected_count]

        return [item for item in items if item]

    def _generate_headlines(self, brief: dict, variant: dict, max_retries: int = 2) -> list[str]:
        """Generate exactly 15 Google RSA headlines in one small LLM call."""
        max_chars = FORMATS_SPEC["google_rsa"]["headlines"]["max_chars"]
        count = FORMATS_SPEC["google_rsa"]["headlines"]["count"]
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(
            brief,
            variant,
            "rsa_headlines",
            competitive_intel=self._competitive_intel(brief),
            count=count,
            max_chars=max_chars,
        )
        for attempt in range(max_retries + 1):
            raw = self._call_llm(system_prompt, user_prompt)
            items = self._parse_numbered_list(raw, expected_count=count)
            if len(items) == count and all(len(item) <= max_chars for item in items):
                return items
            if attempt < max_retries:
                print(f"      Headline length/count mismatch (attempt {attempt + 1}); retrying...")
        # Last resort: truncate any over-length headlines and pad if short.
        items = [item[:max_chars].rstrip() for item in items[:count]]
        while len(items) < count:
            items.append(variant.get("cta", "Join Free"))
        return items

    def _generate_descriptions(self, brief: dict, variant: dict, max_retries: int = 2) -> list[str]:
        """Generate exactly 4 Google RSA descriptions in one small LLM call."""
        max_chars = FORMATS_SPEC["google_rsa"]["descriptions"]["max_chars"]
        count = FORMATS_SPEC["google_rsa"]["descriptions"]["count"]
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(
            brief,
            variant,
            "rsa_descriptions",
            competitive_intel=self._competitive_intel(brief),
            count=count,
            max_chars=max_chars,
        )
        for attempt in range(max_retries + 1):
            raw = self._call_llm(system_prompt, user_prompt)
            items = self._parse_numbered_list(raw, expected_count=count)
            if len(items) == count and all(len(item) <= max_chars for item in items):
                return items
            if attempt < max_retries:
                print(f"      Description length/count mismatch (attempt {attempt + 1}); retrying...")
        # Last resort: truncate any over-length descriptions and pad if short.
        items = [item[:max_chars].rstrip() for item in items[:count]]
        while len(items) < count:
            items.append(variant.get("cta", "Join Free"))
        return items

    def _generate_linkedin(self, brief: dict, variant: dict, max_retries: int = 2) -> dict[str, str]:
        """Generate LinkedIn sponsored content in one small LLM call."""
        max_chars = FORMATS_SPEC["linkedin"]["headline"]["max_chars"]
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(
            brief,
            variant,
            "linkedin",
            competitive_intel=self._competitive_intel(brief),
            max_chars=max_chars,
        )
        for attempt in range(max_retries + 1):
            raw = self._call_llm(system_prompt, user_prompt)
            items = self._parse_numbered_list(raw, expected_count=3)

            # If parsing failed, try to extract explicit labels.
            if len(items) < 3:
                labels = {"intro": "", "headline": "", "description": ""}
                for line in raw.splitlines():
                    lower = line.lower()
                    if lower.startswith("intro:") or lower.startswith("1. intro:"):
                        labels["intro"] = line.split(":", 1)[1].strip()
                    elif lower.startswith("headline:") or lower.startswith("2. headline:"):
                        labels["headline"] = line.split(":", 1)[1].strip()
                    elif lower.startswith("description:") or lower.startswith("3. description:"):
                        labels["description"] = line.split(":", 1)[1].strip()
                items = [labels["intro"], labels["headline"], labels["description"]]

            def _strip_label(text: str, labels: tuple[str, ...]) -> str:
                t = text.strip()
                lower = t.lower()
                for label in labels:
                    if lower.startswith(label):
                        t = t[len(label):].strip()
                        break
                return t

            result = {
                "intro": _strip_label(items[0] if len(items) > 0 else "", ("intro:", "1.")),
                "headline": _strip_label(items[1] if len(items) > 1 else "", ("headline:", "2.")),
                "description": _strip_label(items[2] if len(items) > 2 else "", ("description:", "3.")),
            }
            if (
                result["intro"].strip()
                and result["headline"].strip()
                and result["description"].strip()
                and len(result["headline"]) <= max_chars
            ):
                return result
            if attempt < max_retries:
                print(f"      LinkedIn parse/missing field (attempt {attempt + 1}); retrying...")

        # Last resort: truncate headline if needed.
        result["headline"] = result["headline"][:max_chars].rstrip()
        if not result["intro"]:
            result["intro"] = variant.get("hook_direction", "")
        if not result["description"]:
            result["description"] = variant.get("cta", "")
        return result

    def _generate_formats(self, brief: dict, variant: dict) -> dict[str, object]:
        """Generate all requested formats for a variant using small LLM calls."""
        formats = variant.get("formats", ["google_rsa", "linkedin"])
        result: dict[str, object] = {}

        if "google_rsa" in formats:
            print("    -> generating RSA headlines...")
            headlines = self._generate_headlines(brief, variant)
            print("    -> generating RSA descriptions...")
            descriptions = self._generate_descriptions(brief, variant)
            result["google_rsa"] = {"headlines": headlines, "descriptions": descriptions}

        if "linkedin" in formats:
            print("    -> generating LinkedIn copy...")
            result["linkedin"] = self._generate_linkedin(brief, variant)

        return result

    def generate_variant(self, brief: dict, variant: dict, max_retries: int = 3) -> dict:
        """Generate copy for one variant and validate it, with retries on parse/refusal."""
        last_error: Exception | None = None

        for attempt in range(max_retries):
            try:
                formats_data = self._generate_formats(brief, variant)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                print(f"  Generation failed on attempt {attempt + 1}; retrying...")
                continue

            copy = {
                "variant_id": variant.get("id", "unknown"),
                "angle": variant.get("angle", ""),
                "formats": formats_data,
            }

            # Wrap for validator.
            pack = {"variants": {copy["variant_id"]: copy}}
            errors = validate_copy_pack(pack)
            if errors:
                err_text = "\n".join(f"{e.variant}/{e.field}: {e.message}" for e in errors)
                last_error = ValueError(f"Generated copy failed validation:\n{err_text}")
                print(f"  Validation failed on attempt {attempt + 1}; retrying...")
                continue

            return copy

        raise last_error or RuntimeError("Failed to generate valid copy after retries.")

    def run(self, brief_path: Path | str, out_stem: str | None = None) -> tuple[Path, Path]:
        """Generate a full copy pack from a brief."""
        brief = self.load_brief(brief_path)
        variants = brief.get("variants", [])
        if not variants:
            raise ValueError("Brief contains no variants.")

        copy_pack = {
            "campaign": brief.get("campaign", "untitled"),
            "objective": brief.get("objective", ""),
            "audience": brief.get("audience", ""),
            "success_metric": brief.get("success_metric", ""),
            "variants": {},
        }

        for variant in variants:
            vid = variant.get("id", f"variant_{len(copy_pack['variants']) + 1}")
            print(f"Generating copy for {vid} ({variant.get('angle', '')})...")
            try:
                generated = self.generate_variant(brief, variant)
                copy_pack["variants"][vid] = generated
            except Exception as exc:
                print(f"ERROR generating {vid}: {exc}")
                raise

        copy_dir = self.root / "copy"
        copy_dir.mkdir(exist_ok=True)
        if out_stem:
            safe_name = re.sub(r"[^a-z0-9_-]", "", out_stem.lower().replace(" ", "_"))
        else:
            safe_name = re.sub(r"[^a-z0-9_-]", "", copy_pack["campaign"].lower().replace(" ", "_"))
        if not safe_name:
            safe_name = "campaign"

        json_path = copy_dir / f"copy-pack-{safe_name}.json"
        md_path = copy_dir / f"copy-pack-{safe_name}.md"

        json_path.write_text(json.dumps(copy_pack, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._render_markdown(copy_pack), encoding="utf-8")

        print(f"\nCopy pack saved to:\n  {json_path}\n  {md_path}")
        return md_path, json_path

    def _render_markdown(self, copy_pack: dict) -> str:
        lines = [
            f"# Copy Pack: {copy_pack['campaign']}",
            "",
            f"**Objective:** {copy_pack['objective']}",
            f"**Audience:** {copy_pack['audience']}",
            f"**Success Metric:** {copy_pack['success_metric']}",
            "",
            "---",
            "",
        ]
        for vid, variant in copy_pack["variants"].items():
            lines.append(f"## Variant: {vid} — {variant.get('angle', '')}")
            lines.append("")
            for fmt_name, fmt_data in variant.get("formats", {}).items():
                lines.append(f"### {fmt_name}")
                if fmt_name == "google_rsa":
                    lines.append("**Headlines:**")
                    for h in fmt_data.get("headlines", []):
                        lines.append(f"- {h} ({len(h)} chars)")
                    lines.append("")
                    lines.append("**Descriptions:**")
                    for d in fmt_data.get("descriptions", []):
                        lines.append(f"- {d} ({len(d)} chars)")
                elif fmt_name == "linkedin":
                    lines.append(f"**Intro:** {fmt_data.get('intro', '')}")
                    lines.append(f"**Headline:** {fmt_data.get('headline', '')} ({len(fmt_data.get('headline', ''))} chars)")
                    lines.append(f"**Description:** {fmt_data.get('description', '')}")
                lines.append("")
        return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Ad Copy Writer")
    parser.add_argument("brief", help="Path to creative brief YAML")
    args = parser.parse_args()

    writer = Writer()
    writer.run(args.brief)


if __name__ == "__main__":
    main()
