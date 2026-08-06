"""Performance Marketing Strategist agent."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import yaml

from ..shared.context_loader import (
    build_context_block,
    load_competitive_intel_summary,
    load_keyword_data,
)
from ..shared.llm import AdsLLM
from .prompt_builder import PromptBuilder


class Strategist:
    """Turns freeform campaign input into a strategy and machine-readable brief."""

    def __init__(
        self,
        root: Path | str | None = None,
        llm: AdsLLM | None = None,
        prompts_dir: Path | str | None = None,
        keyword_data_path: Path | str | None = None,
    ):
        self.root = Path(root) if root else Path(__file__).resolve().parents[2]
        self.llm = llm or AdsLLM()
        self.prompt_builder = PromptBuilder(root=self.root, prompts_dir=prompts_dir)
        self.context = build_context_block(self.root)
        self.competitive_intel_summary = load_competitive_intel_summary(self.root)
        self.keyword_data = load_keyword_data(self.root, explicit_path=keyword_data_path)

    # ------------------------------------------------------------------
    # Public run modes
    # ------------------------------------------------------------------
    def run(
        self, input_text: str | None = None, force_interactive: bool = False
    ) -> tuple[Path, Path]:
        """Run the strategist.

        If ``input_text`` is provided, use freeform mode. Otherwise enter
        interactive mode when ``force_interactive`` is True.
        """
        if input_text:
            return self.run_freeform(input_text)
        if force_interactive:
            return self.run_interactive()
        raise ValueError(
            "No input provided and interactive mode not enabled. "
            "Use --input or run in a real terminal."
        )

    def run_freeform(self, input_text: str) -> tuple[Path, Path]:
        """Run the full thinking pipeline from a raw brief string."""
        return self._run_pipeline(input_text)

    def run_interactive(self) -> tuple[Path, Path]:
        """Collect a freeform brief, ask clarifying questions, then run the pipeline."""
        print("\n=== Performance Marketing Strategist ===\n")
        print("Describe the campaign in your own words. Include goal, audience,")
        print("budget, channels, offer, guardrails, and success metric if you know them.\n")

        raw_input = input("Brief: ").strip()
        if not raw_input:
            raise ValueError("No brief provided.")

        # Use a quick understand pass to surface missing/ambiguous items.
        print("\nReading the brief...")
        raw_understand = self._call_phase("understand", input_text=raw_input, context=self.context)

        missing = self._parse_missing_items(raw_understand)
        clarifications: dict[str, str] = {}
        if missing:
            print("\nI have a few clarifying questions:\n")
            for item in missing[:3]:
                answer = input(f"{item}: ").strip()
                clarifications[item] = answer
            print()

        if clarifications:
            clarification_block = "\n".join(f"{k}: {v}" for k, v in clarifications.items())
            combined_input = (
                f"{raw_input}\n\n"
                f"=== Clarifications ===\n"
                f"{clarification_block}"
            )
        else:
            combined_input = raw_input

        # Demand-data gate: keyword plans are not finalized without search-volume data.
        if self.keyword_data is None:
            print("\nNo Keyword Planner / demand data was found in strategy/.")
            print("Keyword plans are provisional without it. If you have an export,")
            raw_path = input("paste the file path (or press Enter to skip): ").strip()
            if raw_path:
                self.keyword_data = load_keyword_data(self.root, explicit_path=raw_path)
                if self.keyword_data is None:
                    print(f"Could not load keyword data from: {raw_path} — proceeding provisional.")
        else:
            print("\nKeyword demand data found — keyword plan will be data-backed.")

        return self._run_pipeline(
            combined_input,
            pre_understand_output=raw_understand,
        )

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------
    def _run_pipeline(
        self,
        input_text: str,
        pre_understand_output: str | None = None,
    ) -> tuple[Path, Path]:
        """Execute the five-phase thinking pipeline and save artifacts."""
        safe_name = self._safe_name(input_text)
        strategy_dir = self.root / "strategy"
        strategy_dir.mkdir(exist_ok=True)

        # Optional raw understand artifact from interactive clarification step.
        if pre_understand_output:
            raw_path = strategy_dir / f"phase-00-understand-raw-{safe_name}.md"
            raw_path.write_text(pre_understand_output, encoding="utf-8")

        print("\nPhase 1/6: understanding the brief...")
        understand_output = self._call_phase(
            "understand",
            input_text=input_text,
            context=self.context,
        )
        self._save_artifact(strategy_dir, f"phase-01-understand-{safe_name}.md", understand_output)

        print("Phase 2/6: analyzing competitive gaps...")
        competitive_gap_output = self._call_phase(
            "competitive_gap",
            understand_output=understand_output,
            context=self.context,
        )
        self._save_artifact(
            strategy_dir,
            f"phase-02-competitive-gap-{safe_name}.md",
            competitive_gap_output,
        )

        print("Phase 3/6: brainstorming angles...")
        brainstorm_output = self._call_phase(
            "brainstorm",
            understand_output=understand_output,
            competitive_gap_output=competitive_gap_output,
            context=self.context,
        )
        self._save_artifact(
            strategy_dir,
            f"phase-03-brainstorm-{safe_name}.md",
            brainstorm_output,
        )

        print("Phase 4/6: evaluating angles...")
        evaluate_output = self._call_phase(
            "evaluate",
            understand_output=understand_output,
            brainstorm_output=brainstorm_output,
            context=self.context,
        )
        self._save_artifact(
            strategy_dir,
            f"phase-04-evaluate-{safe_name}.md",
            evaluate_output,
        )

        print("Phase 5/6: keyword & demand plan...")
        keyword_plan_output = self._call_phase(
            "keyword_plan",
            understand_output=understand_output,
            evaluate_output=evaluate_output,
            keyword_data=self.keyword_data,
        )
        self._save_artifact(
            strategy_dir,
            f"phase-05-keyword-plan-{safe_name}.md",
            keyword_plan_output,
        )

        print("Phase 6/6: writing the creative brief...")
        brief = self._generate_brief(
            understand_output=understand_output,
            competitive_gap_output=competitive_gap_output,
            evaluate_output=evaluate_output,
            keyword_plan_output=keyword_plan_output,
        )

        strategy_markdown = self._render_strategy_markdown(
            understand_output=understand_output,
            competitive_gap_output=competitive_gap_output,
            evaluate_output=evaluate_output,
            keyword_plan_output=keyword_plan_output,
            brief=brief,
        )

        strategy_path = strategy_dir / f"campaign-strategy-{safe_name}.md"
        strategy_path.write_text(strategy_markdown, encoding="utf-8")

        brief_path = strategy_dir / f"creative-brief-{safe_name}.yaml"
        brief_path.write_text(yaml.safe_dump(brief, sort_keys=False), encoding="utf-8")

        print(f"\nStrategy saved to:      {strategy_path}")
        print(f"Creative brief saved to: {brief_path}")

        return strategy_path, brief_path

    # ------------------------------------------------------------------
    # LLM calls
    # ------------------------------------------------------------------
    def _call_phase(self, phase_name: str, **kwargs: object) -> str:
        """Render and call one phase prompt."""
        system_prompt = self.prompt_builder.render_system()

        render_method = getattr(self.prompt_builder, f"render_{phase_name}")
        user_prompt = render_method(**kwargs)

        raw = self.llm.chat(system_prompt, user_prompt)
        return self._clean_llm_output(raw)

    def _generate_brief(
        self,
        understand_output: str,
        competitive_gap_output: str,
        evaluate_output: str,
        keyword_plan_output: str,
    ) -> dict:
        """Generate and parse the final JSON creative brief."""
        system_prompt = self.prompt_builder.render_system()
        user_prompt = self.prompt_builder.render_brief(
            understand_output=understand_output,
            competitive_gap_output=competitive_gap_output,
            evaluate_output=evaluate_output,
            keyword_plan_output=keyword_plan_output,
            context=self.context,
            competitive_intel_summary=self.competitive_intel_summary,
        )

        raw = self.llm.chat(system_prompt, user_prompt)
        raw = self._clean_llm_output(raw)
        # Strip any accidental markdown fences.
        raw = re.sub(r"^```json\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)

    @staticmethod
    def _clean_llm_output(raw: str) -> str:
        """Remove common accidental wrappers from LLM output."""
        return re.sub(r"^```(?:json|text|markdown)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _save_artifact(strategy_dir: Path, filename: str, content: str) -> None:
        """Write an intermediate thinking artifact."""
        (strategy_dir / filename).write_text(content, encoding="utf-8")

    @staticmethod
    def _parse_missing_items(understand_output: str) -> list[str]:
        """Extract missing/ambiguous bullets from an understand output."""
        marker = "## Missing or Ambiguous Items"
        if marker not in understand_output:
            return []

        section = understand_output.split(marker, 1)[1]
        # Stop at the next heading if present.
        next_heading = re.search(r"\n##+ ", section)
        if next_heading:
            section = section[: next_heading.start()]

        items: list[str] = []
        for line in section.splitlines():
            stripped = line.strip()
            if stripped.lower() in {"none", "", "-", "*"}:
                continue
            if stripped.startswith(("- ", "* ")):
                items.append(stripped[2:].strip())
            elif re.match(r"^\d+[.):]\s+", stripped):
                items.append(re.sub(r"^\d+[.):]\s+", "", stripped))

        return items

    def _safe_name(self, text: str) -> str:
        """Derive a filesystem-safe name from the input text."""
        # Take the first meaningful alphanumeric chunk.
        cleaned = re.sub(r"[^a-z0-9\s_-]+", "", text.lower())
        cleaned = re.sub(r"\s+", "_", cleaned).strip("_")
        cleaned = cleaned[:50]
        if not cleaned:
            cleaned = "campaign"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{cleaned}-{timestamp}"

    def _render_strategy_markdown(
        self,
        understand_output: str,
        competitive_gap_output: str,
        evaluate_output: str,
        keyword_plan_output: str,
        brief: dict,
    ) -> str:
        """Assemble a human-readable strategy summary from phase outputs."""
        campaign = brief.get("campaign", "Campaign")
        objective = brief.get("objective", "")
        audience = brief.get("audience", "")
        success_metric = brief.get("success_metric", "")

        lines = [
            f"# Campaign Strategy: {campaign}",
            "",
            f"**Objective:** {objective}",
            f"**Audience:** {audience}",
            f"**Success Metric:** {success_metric}",
            f"**Keyword data status:** {brief.get('keyword_data_status', 'provisional')}",
            "",
            "---",
            "",
            "## 1. Extracted Brief",
            "",
            understand_output,
            "",
            "## 2. Competitive Gap Analysis",
            "",
            competitive_gap_output,
            "",
            "## 3. Evaluated Messaging Angles",
            "",
            evaluate_output,
            "",
            "## 4. Keyword & Demand Plan",
            "",
            keyword_plan_output,
            "",
            "## 5. Final Variant Plan",
            "",
        ]

        for variant in brief.get("variants", []):
            vid = variant.get("id", "")
            angle = variant.get("angle", "")
            persona = variant.get("persona", "")
            hook = variant.get("hook_direction", "")
            cta = variant.get("cta", "")
            refs = variant.get("claim_refs", [])
            formats = variant.get("formats", [])

            lines.append(f"### {vid} — {angle}")
            lines.append("")
            lines.append(f"- **Persona:** {persona}")
            lines.append(f"- **Hook direction:** {hook}")
            lines.append(f"- **CTA:** {cta}")
            lines.append(f"- **Safe-claim refs:** {', '.join(refs) if refs else 'None'}")
            lines.append(f"- **Formats:** {', '.join(formats) if formats else 'None'}")
            lines.append("")

        return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Performance Marketing Strategist")
    parser.add_argument(
        "--input",
        dest="input_text",
        help="Freeform campaign brief. If omitted, interactive mode is used.",
    )
    parser.add_argument(
        "--keyword-data",
        dest="keyword_data_path",
        help="Path to Keyword Planner export/analysis. If omitted, strategy/ is scanned "
        "for keyword-planner-analysis files; interactive mode will ask.",
    )
    args = parser.parse_args()

    strategist = Strategist(keyword_data_path=args.keyword_data_path)
    strategist.run(args.input_text)


if __name__ == "__main__":
    main()
