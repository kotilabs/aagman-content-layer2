"""Performance Marketing Strategist agent."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from ..shared.context_loader import build_context_block
from ..shared.llm import AdsLLM


INTERVIEW_QUESTIONS = [
    {
        "key": "objective",
        "question": "What is the campaign objective?",
        "options": "signups / waitlist / broker connects / app installs / brand awareness / other",
    },
    {
        "key": "icp",
        "question": "Who is the primary ICP?",
        "options": "active trader / equity investor / mutual-fund buyer / no-code systematic user / multi-lingual user",
    },
    {
        "key": "budget",
        "question": "What is the monthly budget range and campaign duration?",
        "options": "e.g. ₹50k/month for 6 weeks",
    },
    {
        "key": "channels",
        "question": "Which channels are in scope for this campaign?",
        "options": "Google Search only / Google + YouTube / LinkedIn / others",
    },
    {
        "key": "offer",
        "question": "What is the offer or main CTA?",
        "options": "e.g. free backtest, waitlist for beta, connect broker",
    },
    {
        "key": "push",
        "question": "What message or angle do you want to push hard?",
        "options": "e.g. proof-first trading, institutional order types, SEBI compliance",
    },
    {
        "key": "avoid",
        "question": "What must we avoid saying or implying?",
        "options": "e.g. guaranteed returns, autonomous trading, unverified features",
    },
    {
        "key": "success",
        "question": "What number makes this campaign a win?",
        "options": "e.g. CPA < ₹500, 500 signups, 100 broker connects",
    },
]


class Strategist:
    """Interviews the user, reads context, and produces a strategy + creative brief."""

    def __init__(self, root: Path | str | None = None, llm: AdsLLM | None = None):
        self.root = Path(root) if root else Path(__file__).resolve().parents[2]
        self.llm = llm or AdsLLM()
        self.context = build_context_block(self.root)

    def interview(self) -> dict[str, str]:
        """Ask the user the strategy questions in the terminal."""
        print("\n=== Performance Marketing Strategist ===\n")
        print("Answer the following questions. Defaults are shown in [brackets].\n")
        answers: dict[str, str] = {}
        for item in INTERVIEW_QUESTIONS:
            print(f"{item['question']}")
            print(f"Options: {item['options']}")
            default = ""
            raw = input("> ").strip()
            answers[item["key"]] = raw if raw else default
            print()
        return answers

    def _strategy_system_prompt(self) -> str:
        return (
            "You are a senior performance marketing strategist for an Indian fintech "
            "startup called Āagman. You have full access to the company's capability "
            "source of truth and to competitor ad intelligence.\n\n"
            "RULES:\n"
            "1. Use ONLY 'Yes' rows from the 'What Is Safe to Claim' table as live claims.\n"
            "2. Use 'Partially' rows only with the cautious wording provided.\n"
            "3. NEVER claim 'No' rows as shipped or currently available.\n"
            "4. Reference competitor ads only for gap analysis, never copy their exact wording.\n"
            "5. Every messaging angle must map to a safe-to-claim capability from the source of truth.\n"
            "6. Be specific, concise, and actionable."
        )

    def _strategy_user_prompt(self, answers: dict[str, str]) -> str:
        q_lines = "\n".join(
            f"{item['key']}: {answers.get(item['key'], '')}"
            for item in INTERVIEW_QUESTIONS
        )
        return (
            "Use the context below to write a campaign strategy.\n\n"
            "=== CONTEXT ===\n"
            f"{self.context}\n\n"
            "=== INTERVIEW ANSWERS ===\n"
            f"{q_lines}\n\n"
            "=== REQUIRED OUTPUT ===\n"
            "Write a markdown campaign strategy with these sections:\n"
            "# Campaign Strategy\n"
            "## 1. Objective & Success Metric\n"
            "## 2. Audience Segments\n"
            "## 3. Positioning & Differentiation (map to competitor gaps)\n"
            "## 4. Messaging Angles (3–5; each with its safe-to-claim source-of-truth reference)\n"
            "## 5. Channel & Format Plan\n"
            "## 6. Variant Test Plan\n"
            "## 7. Budget Split Recommendation\n"
            "## 8. What Not to Say (compliance guardrails)\n"
        )

    def generate_strategy(self, answers: dict[str, str]) -> str:
        """Generate the strategy markdown."""
        return self.llm.chat(
            self._strategy_system_prompt(),
            self._strategy_user_prompt(answers),
        )

    def _brief_system_prompt(self) -> str:
        return (
            "You are a senior performance marketing strategist. Convert the campaign "
            "strategy into a machine-readable creative brief in JSON.\n\n"
            "RULES:\n"
            "1. Output ONLY valid JSON. No markdown code fences. No commentary.\n"
            "2. Every variant must include claim_refs citing source-of-truth rows.\n"
            "3. Formats are limited to: google_rsa, linkedin.\n"
            "4. For google_rsa, request 15 headlines (≤30 chars) and 4 descriptions (≤90 chars).\n"
            "5. For linkedin, request intro text + headline (≤70 chars) + description.\n"
            "6. Include 3–5 variants per messaging angle."
        )

    def _brief_user_prompt(self, answers: dict[str, str], strategy: str) -> str:
        return (
            "Convert the following campaign strategy and interview answers into a "
            "machine-readable JSON creative brief.\n\n"
            "=== INTERVIEW ANSWERS ===\n"
            f"{yaml.safe_dump(answers)}\n"
            "=== STRATEGY ===\n"
            f"{strategy}\n\n"
            "=== REQUIRED JSON SCHEMA ===\n"
            "{\n"
            '  "campaign": "<short name>",\n'
            '  "objective": "<...>",\n'
            '  "audience": "<...>",\n'
            '  "success_metric": "<...>",\n'
            '  "variants": [\n'
            '    {\n'
            '      "id": "v1",\n'
            '      "angle": "<messaging angle name>",\n'
            '      "persona": "<ICP>",\n'
            '      "hook_direction": "<one-line direction for the writer>",\n'
            '      "cta": "<call to action>",\n'
            '      "claim_refs": ["Section X.Y", "Safe-to-Claim row"],\n'
            '      "formats": ["google_rsa", "linkedin"]\n'
            '    }\n'
            '  ]\n'
            "}\n"
        )

    def generate_brief(self, answers: dict[str, str], strategy: str) -> dict:
        """Generate and parse the JSON creative brief."""
        import json

        raw = self.llm.chat(
            self._brief_system_prompt(),
            self._brief_user_prompt(answers, strategy),
        )
        # Strip any accidental markdown fences.
        raw = re.sub(r"^```json\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)

    def run(self) -> tuple[Path, Path]:
        """Run the full strategist workflow and save outputs."""
        answers = self.interview()
        print("Generating strategy...")
        strategy = self.generate_strategy(answers)

        strategy_dir = self.root / "strategy"
        strategy_dir.mkdir(exist_ok=True)
        safe_name = re.sub(r"[^a-z0-9_-]", "", answers.get("objective", "campaign").lower().replace(" ", "_"))
        if not safe_name:
            safe_name = "campaign"
        strategy_path = strategy_dir / f"campaign-strategy-{safe_name}.md"
        strategy_path.write_text(strategy, encoding="utf-8")
        print(f"\nStrategy saved to: {strategy_path}")

        print("\nGenerating creative brief...")
        brief = self.generate_brief(answers, strategy)
        brief_path = strategy_dir / f"creative-brief-{safe_name}.yaml"
        brief_path.write_text(yaml.safe_dump(brief, sort_keys=False), encoding="utf-8")
        print(f"Creative brief saved to: {brief_path}")

        return strategy_path, brief_path


def main() -> None:
    strategist = Strategist()
    strategist.run()


if __name__ == "__main__":
    main()
