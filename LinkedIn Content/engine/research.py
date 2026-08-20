"""Research pass: answer the think note's research questions with verified facts."""
from . import ledger, llm, think

SYSTEM = (
    "You are the research pass of a LinkedIn writing engine. You answer "
    "factual questions for a writer. You only state facts you are confident "
    "are accurate; you never guess."
)


def research(ticket: dict, think_note: str):
    """Answer research questions when the think note asks for them.

    Returns the research text, or None when RESEARCH: no.
    """
    if not think.wants_research(think_note):
        return None
    questions = think.research_questions(think_note)
    user = f"""Answer each question below with verified facts. Use your
knowledge; where you are not certain a fact is accurate, mark it
UNVERIFIED. Be terse — bullet facts only, with dates and numbers. Only
state facts you are confident about; mark everything else UNVERIFIED
rather than guess.

=== CONTEXT ===
Topic: {ticket['topic']}
Founder's take: {ticket['take']}

=== RESEARCH QUESTIONS ===
{questions}
"""
    text = llm.complete(SYSTEM, user)
    path = think.research_path(ticket["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    ledger.log({"event": "researched", "ticket": ticket["id"],
                "questions": len([q for q in questions.splitlines() if q.strip()])})
    return text
