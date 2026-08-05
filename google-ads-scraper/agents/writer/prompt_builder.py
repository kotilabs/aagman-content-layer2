"""Assemble writer prompts from external markdown templates."""
from __future__ import annotations

import re
from pathlib import Path

from ..shared.context_loader import build_writer_context


class PromptBuilder:
    """Loads markdown templates and renders system + user prompts."""

    def __init__(self, root: Path | str | None = None, prompts_dir: Path | str | None = None):
        self.root = Path(root) if root else Path(__file__).resolve().parents[2]
        self.prompts_dir = Path(prompts_dir) if prompts_dir else Path(__file__).resolve().parent / "prompts"
        self._templates: dict[str, str] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Recursively load every *.md file under prompts_dir."""
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompt directory not found: {self.prompts_dir}")

        for path in sorted(self.prompts_dir.rglob("*.md")):
            key = path.relative_to(self.prompts_dir).as_posix()
            self._templates[key] = path.read_text(encoding="utf-8")

    def build_system_prompt(self) -> str:
        """Concatenate system/base.md and system/psychology.md."""
        base = self._templates.get("system/base.md", "")
        psychology = self._templates.get("system/psychology.md", "")
        return f"{base}\n\n{psychology}".strip()

    def build_user_prompt(
        self,
        brief: dict,
        variant: dict,
        task_name: str,
        competitive_intel: str | None = None,
        **task_vars: object,
    ) -> str:
        """Render the variant context plus the requested task template."""
        context_template = self._templates.get("context/variant_context.md", "")
        task_template = self._templates.get(f"tasks/{task_name}.md", "")
        if not task_template:
            raise ValueError(f"Task template not found: tasks/{task_name}.md")

        # Brief-level intel takes precedence over a passed fallback.
        intel = brief.get("competitive_intel") or competitive_intel or ""

        context = self._render(
            context_template,
            campaign=brief.get("campaign", ""),
            objective=brief.get("objective", ""),
            success_metric=brief.get("success_metric", ""),
            variant_id=variant.get("id", ""),
            angle=variant.get("angle", ""),
            persona=variant.get("persona", ""),
            hook_direction=variant.get("hook_direction", ""),
            cta=variant.get("cta", ""),
            product_synopsis=self._product_synopsis(variant),
            safe_claims=self._safe_claims(variant),
            competitive_intel=intel,
            cross_variant_proof_lines=brief.get("cross_variant_proof_lines", []),
        )

        task = self._render(task_template, **task_vars)
        return f"{context}\n\n{task}".strip()

    def _product_synopsis(self, variant: dict) -> str:
        """Return the product synopsis portion of the writer context."""
        full_context = build_writer_context(variant, self.root)
        marker = "=== PRODUCT SYNOPSIS ==="
        end_marker = "=== SAFE CLAIMS FOR THIS VARIANT ==="
        if marker not in full_context:
            return ""
        start = full_context.index(marker) + len(marker)
        end = full_context.index(end_marker) if end_marker in full_context else len(full_context)
        return full_context[start:end].strip()

    def _safe_claims(self, variant: dict) -> str:
        """Return the safe-claims portion of the writer context."""
        full_context = build_writer_context(variant, self.root)
        marker = "=== SAFE CLAIMS FOR THIS VARIANT ==="
        if marker not in full_context:
            return ""
        start = full_context.index(marker) + len(marker)
        end_marker = "Use ONLY the capabilities listed above"
        end = full_context.find(end_marker, start)
        if end == -1:
            end = len(full_context)
        return full_context[start:end].strip()

    @staticmethod
    def _render(template: str, **kwargs: object) -> str:
        """Simple {{ variable }} renderer with {% if variable %}...{% endif %} support."""

        def _conditional(match: re.Match[str]) -> str:
            var_name = match.group(1)
            block = match.group(2)
            return block if kwargs.get(var_name) else ""

        rendered = re.sub(
            r"{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}",
            _conditional,
            template,
            flags=re.DOTALL,
        )

        for key, value in kwargs.items():
            rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))

        return rendered
