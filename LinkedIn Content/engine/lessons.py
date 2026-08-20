"""Lesson store: a single parseable markdown file at memory/lessons.md."""
import re
import uuid
from datetime import date
from pathlib import Path

from . import ledger

ROOT = Path(__file__).resolve().parent.parent
LESSONS = ROOT / "memory" / "lessons.md"

LESSON_RE = re.compile(
    r"^## \[(?P<id>[^\]]+)\]\s*\n"
    r"- status: (?P<status>candidate|active|retired)\n"
    r"- source: (?P<source>pushback|metrics)\n"
    r"- category: (?P<category>\S+)\n"
    r"- stage: (?P<stage>hook|voice|structure|cta|general)\n"
    r"- created: (?P<created>\S+)\n"
    r"- text: (?P<text>.*)$",
    re.MULTILINE,
)

VALID_STAGES = ("hook", "voice", "structure", "cta", "general")


def _parse() -> list[dict]:
    if not LESSONS.exists():
        return []
    return [m.groupdict() for m in LESSON_RE.finditer(LESSONS.read_text(encoding="utf-8"))]


def _write(lessons: list[dict]) -> None:
    parts = ["# Lessons\n"]
    for l in lessons:
        parts.append(
            f"## [{l['id']}]\n"
            f"- status: {l['status']}\n"
            f"- source: {l['source']}\n"
            f"- category: {l['category']}\n"
            f"- stage: {l['stage']}\n"
            f"- created: {l['created']}\n"
            f"- text: {l['text']}\n"
        )
    LESSONS.parent.mkdir(parents=True, exist_ok=True)
    LESSONS.write_text("\n".join(parts), encoding="utf-8")


def add(text: str, source: str, category: str = "all", stage: str = "general") -> str:
    if stage not in VALID_STAGES:
        stage = "general"
    lesson = {
        "id": uuid.uuid4().hex[:8],
        "status": "candidate",
        "source": source,
        "category": category or "all",
        "stage": stage,
        "created": date.today().isoformat(),
        "text": " ".join(text.split()),  # one line
    }
    lessons = _parse()
    lessons.append(lesson)
    _write(lessons)
    ledger.log({"event": "lesson_added", "lesson_id": lesson["id"],
                "category": lesson["category"], "stage": lesson["stage"],
                "source": lesson["source"]})
    return lesson["id"]


def _set_status(lesson_id: str, status: str) -> bool:
    lessons = _parse()
    for l in lessons:
        if l["id"] == lesson_id:
            l["status"] = status
            _write(lessons)
            return True
    return False


def activate(lesson_id: str) -> bool:
    ok = _set_status(lesson_id, "active")
    if ok:
        ledger.log({"event": "lesson_activated", "lesson_id": lesson_id})
    return ok


def retire(lesson_id: str) -> bool:
    return _set_status(lesson_id, "retired")


def active(category: str = None) -> list[str]:
    out = []
    for l in _parse():
        if l["status"] != "active":
            continue
        if category and l["category"] not in (category, "all"):
            continue
        out.append(l["text"])
    return out


def candidates() -> list[dict]:
    return [l for l in _parse() if l["status"] == "candidate"]


def all_lessons() -> list[dict]:
    return _parse()
