"""Signal scout: run the Playwright scraper, filter, dedupe, rank, write digest."""
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRAPE_JS = ROOT / "scouts" / "scrape.js"
SIGNALS = ROOT / "signals"
SEEN = SIGNALS / "seen.json"
SOURCES_JSON = SIGNALS / "sources.json"

DEFAULT_SOURCES = [
    {"name": "pulse", "url": "https://pulse.zerodha.com/", "cutoff_days": 3, "enabled": True},
    {"name": "zerohedge", "url": "https://www.zerohedge.com/", "cutoff_days": 14, "enabled": True},
    {"name": "armstrong", "url": "https://www.armstrongeconomics.com/", "cutoff_days": 14, "enabled": True},
]


def load_sources() -> list:
    if SOURCES_JSON.exists():
        return json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    return DEFAULT_SOURCES


def scrape_source(url: str, name: str) -> list:
    """Run the Playwright scraper for one source; returns raw item list."""
    node_modules = ROOT / "node_modules"
    if not (node_modules / "playwright").exists():
        raise RuntimeError(
            "playwright not found in the project's node_modules — "
            "run `npm install` at the project root first."
        )
    env = dict(os.environ, NODE_PATH=str(node_modules))
    proc = subprocess.run(
        ["node", str(SCRAPE_JS), url, name],
        cwd=str(ROOT),
        env=env, capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"scraper failed for {name}: {proc.stderr.strip()}")
    if proc.stderr.strip():
        print(proc.stderr.strip())
    return json.loads(proc.stdout or "[]")

BEAT = ["SEBI", "RBI", "F&O", "options", "futures", "MCX", "NSE", "BSE",
        "broker", "FPI", "SIP", "commodity", "commodities", "gold", "silver",
        "rates", "bond", "Nifty", "Sensex", "derivatives", "trading", "markets"]


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


JUNK_URL_PATTERNS = [
    r"/help/",
    r"armstrongeconomics\.com/(?:category|tag|about|media|library-research|press-interviews)",
    r"/(?:category|tag|author|topics)/[^/]*$",  # navigation/index pages on any source
    r"ticketspice\.com",
    r"polymarket\.com",
    r"(?:^|//)(?:www\.)?(?:x|twitter)\.com",
    r"zerohedge\.com/sponsored-post/",
]
JUNK_URL_RE = re.compile("|".join(JUNK_URL_PATTERNS), re.IGNORECASE)

JUNK_TITLE_RE = re.compile(
    r"^(view all|models|library|library & research|about\b|home|menu|"
    r"subscribe|sign in|log in|read more|more\b|contact|donate|shop)\b",
    re.IGNORECASE,
)

URL_DATE_RE = re.compile(r"/((?:19|20)\d{2}-\d{2}-\d{2})/")


def _is_junk(item: dict) -> bool:
    return bool(JUNK_URL_RE.search(item["url"]) or JUNK_TITLE_RE.match(item["title"].strip()))


def _url_date(item: dict):
    """ISO timestamp from a /YYYY-MM-DD/ path segment (e.g. ZeroHedge), else None."""
    m = URL_DATE_RE.search(item["url"])
    if m:
        return f"{m.group(1)}T00:00:00+00:00"
    return None


def _load_seen() -> dict:
    if SEEN.exists():
        return json.loads(SEEN.read_text(encoding="utf-8"))
    return {}


def _score(title: str) -> int:
    t = title.lower()
    return sum(1 for kw in BEAT if kw.lower() in t)


def _age_label(item: dict, now: datetime) -> str:
    if not item["published"]:
        return "date unknown"
    dt = datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
    hours = (now - dt).total_seconds() / 3600
    if hours < 24:
        return f"{max(1, int(hours))}h ago"
    return f"{int(hours // 24)}d ago"


def run_scout() -> str:
    sources = [s for s in load_sources() if s.get("enabled", True)]
    items = []
    for src in sources:
        try:
            items.extend(scrape_source(src["url"], src["name"]))
        except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            print(f"{src['name']}: FAILED — {e}")  # continue with the others

    cutoffs = {s["name"]: int(s.get("cutoff_days", 14)) for s in load_sources()}
    now = datetime.now(timezone.utc)
    seen = _load_seen()

    fresh = []
    for item in items:
        if _is_junk(item):
            continue
        item["published"] = item.get("published") or _url_date(item)
        dt = None
        if item["published"]:
            dt = datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
        cutoff = timedelta(days=cutoffs.get(item["source"], 14))
        if dt and now - dt > cutoff:
            continue  # too old
        if not dt and item["source"] == "pulse":
            continue  # pulse items without a parseable date are dropped
        fresh.append((item, dt))

    # dedupe against the seen store and within this run (normalized title)
    new_items = []
    for item, dt in fresh:
        key = _norm_title(item["title"])
        if key in seen:
            continue
        seen[key] = now.isoformat()
        new_items.append((item, dt))

    # rank: beat-keyword count desc, then recency (undated last)
    far_past = datetime(1970, 1, 1, tzinfo=timezone.utc)
    new_items.sort(key=lambda it: (-_score(it[0]["title"]), -(it[1] or far_past).timestamp()))

    lines = [f"# Signal Digest — {now.date().isoformat()}", ""]
    for i, (item, dt) in enumerate(new_items, 1):
        lines.append(f"{i}. [{_age_label(item, now)} · {item['source']}] {item['title']}")
        lines.append(f"   {item['url']}")
    if not new_items:
        lines.append("(no new signals)")

    SIGNALS.mkdir(parents=True, exist_ok=True)
    SEEN.write_text(json.dumps(seen, indent=1), encoding="utf-8")
    digest = SIGNALS / f"{now.date().isoformat()}-digest.md"
    digest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return str(digest)
