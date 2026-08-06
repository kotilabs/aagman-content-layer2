"""Validators for ad copy formats."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValidationError:
    variant: str
    field: str
    message: str


def validate_google_rsa(headlines: list[str], descriptions: list[str]) -> list[ValidationError]:
    """Validate Google Responsive Search Ad copy."""
    errors: list[ValidationError] = []
    if len(headlines) != 10:
        errors.append(
            ValidationError("google_rsa", "headline_count", f"Expected 10 headlines, got {len(headlines)}")
        )
    for idx, h in enumerate(headlines, 1):
        if len(h) > 30:
            errors.append(
                ValidationError("google_rsa", f"headline_{idx}", f"Too long ({len(h)} chars): {h[:35]}...")
            )
    if len(descriptions) != 4:
        errors.append(
            ValidationError("google_rsa", "description_count", f"Expected 4 descriptions, got {len(descriptions)}")
        )
    for idx, d in enumerate(descriptions, 1):
        if len(d) > 90:
            errors.append(
                ValidationError("google_rsa", f"description_{idx}", f"Too long ({len(d)} chars): {d[:95]}...")
            )
    return errors


def validate_linkedin(intro: str, headline: str, description: str) -> list[ValidationError]:
    """Validate LinkedIn sponsored content."""
    errors: list[ValidationError] = []
    if len(headline) > 70:
        errors.append(
            ValidationError("linkedin", "headline", f"Headline too long ({len(headline)} chars): {headline[:75]}...")
        )
    if not description.strip():
        errors.append(ValidationError("linkedin", "description", "Description is empty"))
    if not intro.strip():
        errors.append(ValidationError("linkedin", "intro", "Intro text is empty"))
    return errors


def validate_copy_pack(copy_pack: dict) -> list[ValidationError]:
    """Validate an entire copy pack dict."""
    all_errors: list[ValidationError] = []
    for variant_id, variant in copy_pack.get("variants", {}).items():
        for fmt_name, fmt_data in variant.get("formats", {}).items():
            if fmt_name == "google_rsa":
                all_errors.extend(
                    validate_google_rsa(fmt_data.get("headlines", []), fmt_data.get("descriptions", []))
                )
            elif fmt_name == "linkedin":
                all_errors.extend(
                    validate_linkedin(
                        fmt_data.get("intro", ""),
                        fmt_data.get("headline", ""),
                        fmt_data.get("description", ""),
                    )
                )
    return all_errors
