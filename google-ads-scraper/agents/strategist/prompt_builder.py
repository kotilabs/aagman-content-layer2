"""Assemble strategist prompts from external markdown templates."""
from __future__ import annotations

import re
from pathlib import Path

from ..shared.context_loader import build_context_block, load_competitive_intel_summary


class PromptBuilder:
    """Loads markdown templates and renders system + phase prompts."""

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

    def render_system(self) -> str:
        """Render the strategist system prompt."""
        return self._templates.get("system/thinker.md", "").strip()

    def render_understand(self, input_text: str, context: str) -> str:
        """Render the understand-phase user prompt."""
        template = self._templates.get("phases/understand.md", "")
        return self._render(template, input_text=input_text, context=context)

    def render_competitive_gap(self, understand_output: str, context: str) -> str:
        """Render the competitive-gap user prompt."""
        template = self._templates.get("phases/competitive_gap.md", "")
        return self._render(template, understand_output=understand_output, context=context)

    def render_brainstorm(self, understand_output: str, competitive_gap_output: str, context: str) -> str:
        """Render the brainstorm-phase user prompt."""
        template = self._templates.get("phases/brainstorm.md", "")
        return self._render(
            template,
            understand_output=understand_output,
            competitive_gap_output=competitive_gap_output,
            context=context,
        )

    def render_evaluate(self, understand_output: str, brainstorm_output: str, context: str) -> str:
        """Render the evaluate-phase user prompt."""
        template = self._templates.get("phases/evaluate.md", "")
        return self._render(
            template,
            understand_output=understand_output,
            brainstorm_output=brainstorm_output,
            context=context,
        )

    def render_keyword_plan(self, understand_output: str, evaluate_output: str, keyword_data: str | None) -> str:
        """Render the keyword-plan user prompt.

        ``keyword_data`` is the demand-data text, or None when unavailable —
        the template handles both branches via {% if keyword_data %}.
        """
        template = self._templates.get("phases/keyword_plan.md", "")
        return self._render(
            template,
            understand_output=understand_output,
            evaluate_output=evaluate_output,
            keyword_data=keyword_data or "",
        )

    def render_brief(
        self,
        understand_output: str,
        competitive_gap_output: str,
        evaluate_output: str,
        keyword_plan_output: str,
        context: str,
        competitive_intel_summary: str,
    ) -> str:
        """Render the final-brief user prompt."""
        template = self._templates.get("phases/brief.md", "")
        return self._render(
            template,
            understand_output=understand_output,
            competitive_gap_output=competitive_gap_output,
            evaluate_output=evaluate_output,
            keyword_plan_output=keyword_plan_output,
            context=context,
            competitive_intel_summary=competitive_intel_summary,
        )

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

        return rendered.strip()
