"""run_layer2_full.py — full content-layer2 orchestrator.

Implements the complete Layer 2 workflow from signal identifier through final
approval, using the Kimi Code bridge for every LLM call and file-based human
gates. The runner is resumable: run it repeatedly and it advances to the next
pending gate or LLM request.

Subcommands:
    signal_identifier  Generate (or resume) the daily signal digest.
    select_signal      Present digest candidates and wait for operator pick.
    research           Run the research agent for the selected ticket.
    write              Fan out writers for the selected surfaces.
    review             Run the markets reviewer on all produced drafts.
    correct            Apply reviewer feedback (up to 2 correction loops).
    seo                Run SEO/AEO audit + final blog corrections.
    publish_approval   Wait for final approval, then move surfaces to final/.
    analytics          Collect social/Substack metrics and run the analytics report (interactive by default).
    run_all            Advance through the whole pipeline as far as possible.
    status             Show current state.

Human gates use files in layer2_full_run/gates/:
    PENDING.md   what the operator/assistant needs to decide
    RESPONSE.md  operator selection/notes (for select_signal)
    APPROVED     marker file for approvals
    REJECTED     marker file for rejections
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from harness_core.agent_memory import AgentMemory
from harness_core.agent_base import Verdict
from harness_core.budget import BudgetGuard
from harness_core.kill_switch import KillSwitch
from harness_core.llm_router import LLMRouter
from harness_core.run import Services, load_env
from harness_core.state import WorkItemStore
from harness_core.telegram import Telegram
from harness_configs.kimi_code_bridge import (
    AwaitingResponseError,
    make_kimi_code_bridge,
)
from harness_configs.layer2_full_config import build_config, SURFACES
from harness_configs.x_scout_agent_config import XScoutConfig
from harness_configs.reddit_scout_agent_config import RedditScoutConfig
from harness_agents.x_scout_agent import XScoutAgent
from harness_agents.reddit_scout_agent import RedditScoutAgent
from harness_content.layer2_full_agents import (
    Layer2Corrector,
    Layer2FinalCorrector,
    Layer2MarketsReviewerFull,
    Layer2PublisherFull,
    Layer2ResearchAgentFull,
    Layer2SEOAuditor,
    Layer2SignalIdentifier,
    Layer2Writer,
    parse_digest_candidates,
    write_all_surfaces,
)
from harness_content.analytics_agent import (
    AnalyticsAnalyzer,
    AnalyticsCollector,
    BufferMCPClient,
)
from harness_content.seed_layer2 import seed_all
from harness_content.judges import Layer2ContentJudge

WORKDIR_NAME = "layer2_full_run"
DEFAULT_SURFACES = SURFACES
MAX_CORRECTION_LOOPS = 2


# --------------------------------------------------------------------------- #
# Interactive prompt helpers
# --------------------------------------------------------------------------- #
def _is_interactive(args) -> bool:
    """True unless the operator explicitly requested non-interactive mode.

    We default to interactive because analytics is an operator-driven action.
    Use --non-interactive for CI/automation.
    """
    return not getattr(args, "non_interactive", False)


def _prompt_choice(question: str, choices: list[tuple[str, str]], default_idx: int = 0) -> int:
    """Ask the user to pick one option by number. Returns the chosen index.
    Uses the default if input is not available (e.g., piped/non-TTY execution)."""
    print(f"\n{question}")
    for i, (key, desc) in enumerate(choices, 1):
        print(f"  [{i}] {key}: {desc}")
    default_num = default_idx + 1
    while True:
        try:
            raw = input(f"Choose (1-{len(choices)}) [{default_num}]: ").strip()
        except EOFError:
            print(f"Using default [{default_num}].")
            return default_idx
        if not raw:
            return default_idx
        try:
            num = int(raw)
        except ValueError:
            print("Please enter a number.")
            continue
        if 1 <= num <= len(choices):
            return num - 1
        print(f"Please choose between 1 and {len(choices)}.")


def _prompt_input(question: str, default: str = "") -> str:
    """Ask for free text input with an optional default.
    Uses the default if input is not available."""
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            raw = input(f"{question}{suffix}: ").strip()
        except EOFError:
            if default:
                print(f"Using default '{default}'.")
                return default
            raise
        if raw:
            return raw
        if default:
            return default
        print("A value is required.")


def _prompt_yes_no(question: str, default: bool = False) -> bool:
    """Ask a yes/no question. Uses the default if input is not available."""
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        try:
            raw = input(f"{question}{suffix}: ").strip().lower()
        except EOFError:
            print("Using default '{}'.", format("yes" if default else "no"))
            return default
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please answer yes or no.")


# --------------------------------------------------------------------------- #
# Gate helpers
# --------------------------------------------------------------------------- #
class GatePending(Exception):
    """Raised when a human gate needs operator input."""


class GateRejected(Exception):
    """Raised when a human gate was rejected."""


def _gate_dir(workdir: Path, gate_name: str) -> Path:
    d = workdir / "gates" / gate_name
    d.mkdir(parents=True, exist_ok=True)
    return d


def _request_gate(workdir: Path, gate_name: str, body: str) -> None:
    gdir = _gate_dir(workdir, gate_name)
    (gdir / "PENDING.md").write_text(body, encoding="utf-8")
    (gdir / "REQUESTED").write_text(str(time.time()), encoding="utf-8")
    raise GatePending(f"Gate '{gate_name}' pending. See {gdir / 'PENDING.md'}")


def _check_approval_gate(workdir: Path, gate_name: str) -> bool:
    gdir = _gate_dir(workdir, gate_name)
    if (gdir / "APPROVED").exists():
        return True
    if (gdir / "REJECTED").exists():
        raise GateRejected(f"Gate '{gate_name}' was rejected.")
    return False


def _gate_body(workdir: Path, gate_name: str) -> str:
    gdir = _gate_dir(workdir, gate_name)
    path = gdir / "PENDING.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _clear_gate(workdir: Path, gate_name: str) -> None:
    gdir = _gate_dir(workdir, gate_name)
    for name in ("PENDING.md", "RESPONSE.md", "REQUESTED", "APPROVED", "REJECTED"):
        (gdir / name).unlink(missing_ok=True)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, TypeError):
        return ""


# --------------------------------------------------------------------------- #
# Scout → digest helpers
# --------------------------------------------------------------------------- #
def _digest_path_for_source(workdir: Path, date: str, source: str) -> Path:
    """Map a scout source name to its digest file path."""
    signals_dir = workdir / "signals"
    mapping = {
        "default": f"{date}-digest.md",
        "combined": f"{date}-digest.md",
        "macro": f"{date}-macro-digest.md",
        "india_news": f"{date}-india-news-digest.md",
        "x": f"{date}-x-digest.md",
        "reddit": f"{date}-reddit-digest.md",
    }
    return signals_dir / mapping.get(source, f"{date}-{source}-digest.md")


def _available_digest_sources(workdir: Path, date: str) -> dict[str, Path]:
    """Return all digest files that exist for a date, keyed by source name."""
    sources = ["combined", "macro", "india_news", "x", "reddit"]
    found = {}
    for src in sources:
        path = _digest_path_for_source(workdir, date, src)
        if path.exists():
            found[src] = path
    return found


def _clusters_to_digest(source: str, clusters_text: str, date: str) -> str:
    """Convert X/Reddit cluster markdown into a digest the parser can read."""
    lines = [
        f"# Aagman Layer 2 Signal Digest — {source.upper()} — {date}",
        "",
        f"> Clustered signals from the {source} scout.",
        "",
        "---",
        "",
        "## Real-time Market Lens",
        "",
    ]

    # Match headings that look like cluster titles.
    heading_re = re.compile(r"^(#{2,4})\s*(?:\d+\.?\s*|Cluster\s*\d+[:\-]?\s*)?(.*?)$", re.MULTILINE)
    summary_re = re.compile(r"[-*]\s*\*\*Summary:\*\*\s*(.+)", re.IGNORECASE)

    sections = []
    headings = list(heading_re.finditer(clusters_text))
    for i, m in enumerate(headings):
        level, title = m.group(1), m.group(2).strip()
        if not title or title.lower() in ("clusters", "new posts clusters", "hot posts clusters"):
            continue
        if "other / noise" in title.lower() or title.lower().startswith("other"):
            continue
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(clusters_text)
        block = clusters_text[start:end]
        summary = ""
        for sm in summary_re.finditer(block):
            summary = sm.group(1).strip()
            break
        sections.append((title, summary, block.strip()))

    if not sections:
        # Fallback: dump the whole thing as a single candidate.
        sections.append((f"{source.title()} feed summary", "Clustered feed activity.", clusters_text))

    for idx, (title, summary, block) in enumerate(sections, 1):
        lines.append(f"### Signal: {title}")
        lines.append("")
        lines.append(f"- **Source:** {source}")
        lines.append(f"- **Why this matters now:** {summary or '(see cluster below)'}")
        lines.append("")
        lines.append("**Raw cluster:**")
        lines.append("")
        lines.append(block)
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Operator notes",
        "",
        "- Review the clusters above.",
        "- Pick one signal and the surfaces to produce.",
        f"- Write selection to `state/tickets/{date}-<signal-id>.md`.",
    ])

    return "\n".join(lines)


def _record_outcome(workdir: Path, services: Services, outcome: str,
                    notes: str = "") -> None:
    """Store a feedback lesson from a terminal outcome in the content memory."""
    if not services or not getattr(services, "memory_factory", None):
        return
    state = load_state(workdir)
    signal_id = state.get("signal_id", "unknown")
    title = state.get("signal_title", signal_id)
    surfaces = state.get("surfaces", [])
    ticket_path = Path(state.get("ticket_path", "") or "")
    ticket_notes = ""
    if ticket_path.exists():
        # Capture any operator notes added under the Signal brief section.
        ticket_text = _read_text(ticket_path)
        if "## Signal brief" in ticket_text:
            parts = ticket_text.split("## Signal brief", 1)
            tail = parts[1]
            # Stop at next heading.
            next_heading = tail.find("\n## ")
            if next_heading != -1:
                tail = tail[:next_heading]
            ticket_notes = tail.strip().replace("(Copied from digest. Add operator notes here.)", "").strip()

    lesson = (
        f"outcome={outcome} | signal={signal_id} | title={title} | "
        f"surfaces={','.join(surfaces)}"
    )
    if notes:
        lesson += f" | notes={notes}"
    if ticket_notes:
        lesson += f" | ticket_notes={ticket_notes}"

    mem = services.memory_factory("content", "publish")
    mem.add(lesson, id=f"content.publish.{signal_id}.{outcome}", tags=outcome)
    print(f"Recorded lesson: content.publish.{signal_id}.{outcome}")


# --------------------------------------------------------------------------- #
# Services
# --------------------------------------------------------------------------- #
def build_services(workdir: Path, env: dict | None = None) -> Services:
    env = dict(env or {})
    cost_log = str(workdir / "logs" / "cost_log.jsonl")
    mem_db = str(workdir / "data" / "memory.db")
    telegram = Telegram(env.get("TELEGRAM_BOT_TOKEN"), env.get("TELEGRAM_CHAT_ID"))
    budget = BudgetGuard(float(env.get("DAILY_BUDGET_USD", "5.00")), cost_log,
                         notifier=telegram.notifier(),
                         paused_path=str(workdir / "PAUSED"))

    request_dir = workdir / "gates" / "llm_requests"
    response_dir = workdir / "gates" / "llm_responses"
    bridge = make_kimi_code_bridge(request_dir, response_dir, poll_interval=2.0)

    router = LLMRouter(
        models_yaml_path=str(REPO / "harness_configs" / "models_kimi.yaml"),
        completion_fn=bridge,
        cost_log_path=cost_log,
        budget=budget,
    )
    # Kimi Code is the runtime; override pricing to zero.
    router.pricing = {m: 0.0 for m in router.pricing}

    store = WorkItemStore(str(workdir / "data" / "state.db"))
    kill = KillSwitch(str(workdir / "KILL"), pid_path=str(workdir / "PID"))
    memory_factory = lambda domain, step: AgentMemory(domain, step, db_path=mem_db)

    return Services(
        router=router, store=store, budget=budget, kill=kill, telegram=telegram,
        memory_factory=memory_factory, env=env, workdir=str(workdir),
        dry_run=False,
    )


def ensure_workdir(workdir: Path) -> None:
    for sub in ("signals", "state/tickets", "research", "drafts", "reviews",
                "final", "logs", "data", "gates/llm_requests",
                "gates/llm_responses"):
        (workdir / sub).mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# State persistence
# --------------------------------------------------------------------------- #
def state_path(workdir: Path) -> Path:
    return workdir / "data" / "layer2_full_state.json"


def load_state(workdir: Path) -> dict:
    path = state_path(workdir)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_state(workdir: Path, state: dict) -> None:
    state_path(workdir).write_text(json.dumps(state, indent=2), encoding="utf-8")


def current_date(state: dict) -> str:
    from datetime import date
    return state.get("date") or date.today().isoformat()


# --------------------------------------------------------------------------- #
# Workflow steps
# --------------------------------------------------------------------------- #
def cmd_signal_identifier(services: Services, workdir: Path, args) -> None:
    """Generate the daily signal digest (macro + realtime)."""
    state = load_state(workdir)
    date = args.date or current_date(state)
    state["date"] = date
    save_state(workdir, state)

    digest_path = workdir / "signals" / f"{date}-digest.md"
    if args.force:
        digest_path.unlink(missing_ok=True)
        for cache in workdir.glob(f"signals/.{date}-*-response.md"):
            cache.unlink(missing_ok=True)
    elif digest_path.exists():
        print(f"Digest already exists: {digest_path}")
        return

    identifier = Layer2SignalIdentifier(services.router, workdir)
    try:
        digest_path = identifier.run(date=date)
        print(f"Wrote digest: {digest_path}")
        # Clear any stale selection gate for this date.
        _clear_gate(workdir, f"signal_selection_{date}")
    except AwaitingResponseError as e:
        print(f"\nAwaiting LLM response for {e.req_id}")
        print(f"Request file:  {e.req_file}")
        print(f"Response file: {e.resp_file}")
        print("\nRead the request, provide a response, and re-run this command.")
        raise SystemExit(0)


def cmd_macro_scout(services: Services, workdir: Path, args) -> None:
    """Generate the macro signal digest only."""
    from harness_content.scouts import MacroSignalScout
    state = load_state(workdir)
    date = args.date or current_date(state)
    state["date"] = date
    save_state(workdir, state)

    scout = MacroSignalScout(
        services.router, workdir,
        memory_factory=services.memory_factory if services else None,
    )
    digest_path = scout.digest_path(date)
    if args.force:
        digest_path.unlink(missing_ok=True)
        cache = workdir / "signals" / f".{date}-macro-response.md"
        cache.unlink(missing_ok=True)
    elif digest_path.exists():
        print(f"Macro digest already exists: {digest_path}")
        return

    try:
        digest_path = scout.run(date)
        print(f"Wrote macro digest: {digest_path}")
        _clear_gate(workdir, f"signal_selection_{date}")
    except AwaitingResponseError as e:
        print(f"\nAwaiting LLM response for {e.req_id}")
        print(f"Request file:  {e.req_file}")
        print(f"Response file: {e.resp_file}")
        print("\nRead the request, provide a response, and re-run this command.")
        raise SystemExit(0)


def cmd_india_news_scout(services: Services, workdir: Path, args) -> None:
    """Generate the India news signal digest only."""
    from harness_content.scouts import IndiaNewsScout
    state = load_state(workdir)
    date = args.date or current_date(state)
    state["date"] = date
    save_state(workdir, state)

    scout = IndiaNewsScout(
        services.router, workdir,
        memory_factory=services.memory_factory if services else None,
    )
    digest_path = scout.digest_path(date)
    if args.force:
        digest_path.unlink(missing_ok=True)
        cache = workdir / "signals" / f".{date}-india_news-response.md"
        cache.unlink(missing_ok=True)
    elif digest_path.exists():
        print(f"India news digest already exists: {digest_path}")
        return

    try:
        digest_path = scout.run(date)
        print(f"Wrote India news digest: {digest_path}")
        _clear_gate(workdir, f"signal_selection_{date}")
    except AwaitingResponseError as e:
        print(f"\nAwaiting LLM response for {e.req_id}")
        print(f"Request file:  {e.req_file}")
        print(f"Response file: {e.resp_file}")
        print("\nRead the request, provide a response, and re-run this command.")
        raise SystemExit(0)


def cmd_x_scout(services: Services, workdir: Path, args) -> None:
    """Run the X home-feed scout and write a digest of clustered candidates."""
    state = load_state(workdir)
    date = args.date or current_date(state)
    state["date"] = date
    save_state(workdir, state)

    digest_path = _digest_path_for_source(workdir, date, "x")
    if args.force:
        digest_path.unlink(missing_ok=True)

    if digest_path.exists():
        print(f"X digest already exists: {digest_path}")
        return

    config = XScoutConfig.default()
    agent = XScoutAgent(config)
    try:
        cluster_file = agent.run(dt=date)
    except Exception as exc:
        raise SystemExit(f"X scout failed: {exc}") from exc

    clusters_text = cluster_file.read_text(encoding="utf-8") if cluster_file.exists() else ""
    digest = _clusters_to_digest("x", clusters_text, date)
    digest_path.parent.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(digest, encoding="utf-8")
    print(f"Wrote X digest: {digest_path}")
    _clear_gate(workdir, f"signal_selection_{date}")


def cmd_reddit_scout(services: Services, workdir: Path, args) -> None:
    """Run the Reddit scout and write a digest of clustered candidates."""
    state = load_state(workdir)
    date = args.date or current_date(state)
    state["date"] = date
    save_state(workdir, state)

    digest_path = _digest_path_for_source(workdir, date, "reddit")
    if args.force:
        digest_path.unlink(missing_ok=True)

    if digest_path.exists():
        print(f"Reddit digest already exists: {digest_path}")
        return

    config = RedditScoutConfig.default()
    agent = RedditScoutAgent(config)
    try:
        cluster_file = agent.run(dt=date)
    except Exception as exc:
        raise SystemExit(f"Reddit scout failed: {exc}") from exc

    clusters_text = cluster_file.read_text(encoding="utf-8") if cluster_file.exists() else ""
    digest = _clusters_to_digest("reddit", clusters_text, date)
    digest_path.parent.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(digest, encoding="utf-8")
    print(f"Wrote Reddit digest: {digest_path}")
    _clear_gate(workdir, f"signal_selection_{date}")


def cmd_select_signal(services: Services, workdir: Path, args) -> dict:
    """Present digest candidates and wait for operator selection."""
    state = load_state(workdir)
    date = args.date or current_date(state)

    available = _available_digest_sources(workdir, date)
    if not available:
        raise SystemExit(
            f"No digest found for {date}. Run one of:\n"
            f"  python run_layer2_full.py signal_identifier\n"
            f"  python run_layer2_full.py macro_scout\n"
            f"  python run_layer2_full.py india_news_scout\n"
            f"  python run_layer2_full.py x_scout\n"
            f"  python run_layer2_full.py reddit_scout"
        )

    gate_name = f"signal_selection_{date}"
    gdir = _gate_dir(workdir, gate_name)

    # Already selected?
    response_file = gdir / "RESPONSE.md"
    if response_file.exists():
        selection = _parse_selection(response_file)
        source = selection.get("digest_source", "combined")
        digest_path = _digest_path_for_source(workdir, date, source)
        state["digest_source"] = source
        state["signal_id"] = selection["signal_id"]
        state["signal_title"] = selection.get("title", selection["signal_id"])
        state["surfaces"] = selection.get("surfaces", DEFAULT_SURFACES)
        state["operator_notes"] = selection.get("operator_notes", "")
        state["ticket_path"] = str(
            workdir / "state" / "tickets" / f"{date}-{selection['signal_id']}.md"
        )
        save_state(workdir, state)
        _write_ticket(state, workdir)
        print(f"Selection accepted: {selection['signal_id']} (from {source})")
        print(f"Digest: {digest_path}")
        print(f"Ticket: {state['ticket_path']}")
        _clear_gate(workdir, gate_name)
        return selection

    # Build pending file from all available digests.
    body = f"# Signal Selection — {date}\n\n"
    body += "## Available digests\n\n"
    for src, path in available.items():
        body += f"- `{src}` → `{path}`\n"
    body += "\nPick one digest_source in your response.\n\n"

    all_candidates: list[tuple[str, list]] = []
    for src, path in available.items():
        candidates = parse_digest_candidates(path)
        if not candidates:
            continue
        body += f"## Candidates from `{src}`\n\n"
        for i, c in enumerate(candidates, 1):
            body += (
                f"### {src}-{i}. {c.title}\n"
                f"- **id:** `{c.id}`\n"
                f"- **lens:** {c.lens}\n"
                f"- **why now:** {c.why_now or '(see digest)'}\n\n"
            )
        all_candidates.append((src, candidates))

    if not all_candidates:
        raise SystemExit(f"No candidates found in any digest for {date}.")

    body += (
        f"\n## How to respond\n\n"
        f"Write `{gdir / 'RESPONSE.md'}` with:\n"
        f"```yaml\n"
        f"---\n"
        f"digest_source: <one of: {', '.join(available.keys())}>\n"
        f"signal_id: <id from the chosen digest>\n"
        f"title: <signal title>\n"
        f"surfaces: [{', '.join(DEFAULT_SURFACES)}]\n"
        f"operator_notes: |\n"
        f"  <your angle, context, or questions for the research agent>\n"
        f"---\n"
        f"```\n\n"
        f"The `operator_notes` field is optional but strongly recommended for India news, X, and Reddit signals. "
        f"It tells the research agent what angle to pursue.\n"
    )
    _request_gate(workdir, gate_name, body)
    return {}  # never reached


def _parse_selection(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    # Try YAML frontmatter first.
    if text.strip().startswith("---"):
        import yaml
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1]) or {}
    # Fallback: simple key:value.
    out = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if k in ("surfaces",):
                out[k] = [s.strip() for s in v.strip("[]").split(",") if s.strip()]
            else:
                out[k] = v
    return out


_SCOUT_CHOICES = {
    "signal_identifier": (
        "Combined macro + realtime lens",
        "Runs the original Layer 2 digest: macro/structural candidates plus "
        "real-time market signals in one file."
    ),
    "macro_scout": (
        "Macro / structural lens only",
        "Weekly deep editorial candidates across macro, equities, commodities, "
        "rates, credit, derivatives, AI×capital, and political economy."
    ),
    "india_news_scout": (
        "India news lens",
        "Daily/near-daily Indian markets, companies, sectors, and policy."
    ),
    "x_scout": (
        "X home-feed lens",
        "Scrolls your logged-in X home feed, expands relevant tweets, and "
        "clusters them into story candidates."
    ),
    "reddit_scout": (
        "Reddit lens",
        "Clusters posts from r/IndianStockMarket, r/DalalStreetTalks, "
        "r/IndianStocks, r/IndianStreetBets, r/MutualfundsIndia."
    ),
}


def _parse_scout_selection(path: Path) -> str:
    """Read the scout choice from a response file."""
    text = path.read_text(encoding="utf-8").strip()
    # YAML frontmatter.
    if text.startswith("---"):
        import yaml
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            scout = fm.get("scout", "")
            if scout in _SCOUT_CHOICES:
                return scout
    # Simple key:value or bare command.
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            if k.strip().lower() in ("scout", "command"):
                scout = v.strip().strip('"\'')
                if scout in _SCOUT_CHOICES:
                    return scout
        if line in _SCOUT_CHOICES:
            return line
    return ""


def _write_ticket(state: dict, workdir: Path) -> Path:
    date = state["date"]
    signal_id = state["signal_id"]
    title = state.get("signal_title", signal_id)
    surfaces = state.get("surfaces", DEFAULT_SURFACES)
    digest_source = state.get("digest_source", "combined")
    operator_notes = state.get("operator_notes", "")
    ticket_path = workdir / "state" / "tickets" / f"{date}-{signal_id}.md"
    ticket_path.parent.mkdir(parents=True, exist_ok=True)

    notes_fm = f"operator_notes: |\n{_indent_block(operator_notes, 2)}\n" if operator_notes else "operator_notes: \"\"\n"
    notes_body = (
        f"## Operator notes\n\n{operator_notes}\n\n" if operator_notes
        else "## Operator notes\n\n(Add angle, context, or questions here.)\n\n"
    )

    body = (
        f"---\n"
        f"signal_id: {signal_id}\n"
        f"title: {title}\n"
        f"date: {date}\n"
        f"surfaces: [{', '.join(surfaces)}]\n"
        f"digest_source: {digest_source}\n"
        f"{notes_fm}"
        f"---\n\n"
        f"# Ticket: {title}\n\n"
        f"Selected surfaces: {', '.join(surfaces)}\n\n"
        f"Scout source: `{digest_source}`\n\n"
        f"## Signal brief\n\n"
        f"(Copied from digest. The research agent will also read the operator notes below.)\n\n"
        f"{notes_body}"
        f"## Sources\n\n"
        f"- (add source pointers)\n"
    )
    ticket_path.write_text(body, encoding="utf-8")
    return ticket_path


def _indent_block(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line for line in text.splitlines())


def cmd_research(services: Services, workdir: Path, args) -> Path:
    """Run the research agent for the selected ticket."""
    state = load_state(workdir)
    if "ticket_path" not in state:
        raise SystemExit("No ticket selected. Run select_signal first.")

    gate_name = "research_approval"
    if _check_approval_gate(workdir, gate_name):
        print("Research approved.")
        _clear_gate(workdir, gate_name)
        return Path(state["ticket_path"])

    signal_id = state["signal_id"]
    research_file = workdir / "research" / f"signal-{signal_id}.md"
    if research_file.exists() and not args.force:
        body = _gate_body(workdir, gate_name) or f"Research exists: {research_file}"
    else:
        researcher = Layer2ResearchAgentFull(
            services.router, workdir,
            memory_factory=services.memory_factory if services else None,
        )
        research_file = researcher.run(state["ticket_path"])
        body = (
            f"# Research Approval\n\n"
            f"Signal: {state.get('signal_title', signal_id)}\n"
            f"File: `{research_file}`\n\n"
            f"Review the research artifact. If it is ready, create:\n"
            f"`{workdir / 'gates' / gate_name / 'APPROVED'}`\n\n"
            f"To reject, create:\n"
            f"`{workdir / 'gates' / gate_name / 'REJECTED'}`\n"
        )

    _request_gate(workdir, gate_name, body)
    return research_file  # never reached


def cmd_write(services: Services, workdir: Path, args) -> list[Path]:
    """Fan out writers for selected surfaces."""
    state = load_state(workdir)
    signal_id = state["signal_id"]
    surfaces = state.get("surfaces", DEFAULT_SURFACES)

    writer = Layer2Writer(
        services.router, workdir,
        memory_factory=services.memory_factory if services else None,
    )
    mode = "standalone" if "blog" not in surfaces else "promo"

    # Skip if drafts already exist and --force is not set.
    existing_paths = [
        workdir / "drafts" / f"signal-{signal_id}-{_surface_file(s)}"
        for s in surfaces
    ]
    if all(p.exists() for p in existing_paths) and not args.force:
        print("Drafts already exist. Skipping write. Use --force to regenerate.")
        return existing_paths

    # Run in parallel for speed.
    paths = write_all_surfaces(writer, signal_id, surfaces, mode=mode)
    for p in paths:
        print(f"Wrote draft: {p}")
    return paths


def cmd_review(services: Services, workdir: Path, args) -> None:
    """Run the content judge on all produced drafts."""
    state = load_state(workdir)
    signal_id = state["signal_id"]
    surfaces = state.get("surfaces", DEFAULT_SURFACES)

    judge = Layer2ContentJudge(
        services.router, workdir,
        memory_factory=services.memory_factory if services else None,
    )
    review_file = judge.review_path(signal_id)
    if review_file.exists() and not args.force:
        print(f"Review file already exists: {review_file}")
        return
    verdict = judge.run(signal_id, surfaces)
    print(f"Content judge: {verdict.verdict}")
    print(f"Review file: {verdict.meta['review_file']}")
    if verdict.issues:
        print(f"Surfaces with blockers: {', '.join(verdict.issues)}")


def cmd_correct(services: Services, workdir: Path, args) -> None:
    """Apply judge feedback to surfaces with blockers."""
    state = load_state(workdir)
    signal_id = state["signal_id"]
    surfaces = state.get("surfaces", DEFAULT_SURFACES)

    judge = Layer2ContentJudge(
        services.router, workdir,
        memory_factory=services.memory_factory if services else None,
    )
    verdict = judge.run(signal_id, surfaces)
    if verdict.verdict == "pass":
        print("No blockers. Ready for SEO.")
        return

    corrector = Layer2Corrector(Layer2Writer(
        services.router, workdir,
        memory_factory=services.memory_factory if services else None,
    ))
    loop_key = f"correction_loops_{signal_id}"
    loops = state.get(loop_key, 0)
    if loops >= MAX_CORRECTION_LOOPS:
        print(f"Max correction loops ({MAX_CORRECTION_LOOPS}) reached. "
              f"Remaining blockers: {verdict.issues}")
        return

    review_path = judge.review_path(signal_id)
    for surface in verdict.issues:
        print(f"Correcting {surface}...")
        corrector.correct(signal_id, surface, review_path)

    state[loop_key] = loops + 1
    save_state(workdir, state)
    print(f"Correction loop {loops + 1} complete. Re-run review to check.")


def cmd_seo(services: Services, workdir: Path, args) -> None:
    """Run SEO/AEO audit on blog and apply fixes."""
    state = load_state(workdir)
    signal_id = state["signal_id"]

    if "blog" not in state.get("surfaces", DEFAULT_SURFACES):
        print("No blog surface. Skipping SEO.")
        return

    gate_name = "seo_approval"
    if _check_approval_gate(workdir, gate_name):
        print("SEO audit approved.")
        _clear_gate(workdir, gate_name)
        return

    auditor = Layer2SEOAuditor(services.router, workdir)
    audit_file = auditor.audit_path(signal_id)
    final_blog = workdir / "drafts" / f"signal-{signal_id}-blog.md"
    if audit_file.exists() and final_blog.exists() and not args.force:
        print(f"SEO audit and corrected blog already exist. Skipping SEO.")
    else:
        audit_file = auditor.run(signal_id)
        print(f"SEO audit: {audit_file}")

        final_corrector = Layer2FinalCorrector(services.router, workdir)
        final_corrector.run(signal_id)
        print(f"Applied SEO fixes to blog draft.")

    body = (
        f"# SEO/AEO Approval\n\n"
        f"Signal: {state.get('signal_title', signal_id)}\n"
        f"Audit: `{audit_file}`\n"
        f"Corrected blog: `{workdir / 'drafts' / f'signal-{signal_id}-blog.md'}`\n\n"
        f"Approve by creating:\n"
        f"`{workdir / 'gates' / gate_name / 'APPROVED'}`\n"
    )
    _request_gate(workdir, gate_name, body)


def _surface_file(surface: str) -> str:
    from harness_content.layer2_full_agents import _SURFACE_FILE
    return _SURFACE_FILE[surface]


def cmd_publish_approval(services: Services, workdir: Path, args) -> None:
    """Wait for final approval, then publish approved surfaces."""
    state = load_state(workdir)
    signal_id = state["signal_id"]
    surfaces = state.get("surfaces", DEFAULT_SURFACES)

    gate_name = "publish_approval"
    gate_dir = _gate_dir(workdir, gate_name)
    rejected_file = gate_dir / "REJECTED"
    approved_file = gate_dir / "APPROVED"

    if rejected_file.exists():
        notes = _read_text(rejected_file)
        _record_outcome(workdir, services, "rejected", notes=notes)
        raise GateRejected(f"Gate '{gate_name}' was rejected.")

    if approved_file.exists():
        notes = _read_text(approved_file)
        publisher = Layer2PublisherFull(workdir)
        copied = publisher.publish(signal_id, surfaces)
        print(f"Published {len(copied)} surfaces to final/:")
        for p in copied:
            print(f"  {p}")
        _record_outcome(workdir, services, "published", notes=notes)
        _clear_gate(workdir, gate_name)
        return

    # Build summary of all surfaces for the operator.
    body = f"# Final Publish Approval\n\nSignal: {state.get('signal_title', signal_id)}\n\n"
    body += "## Surfaces ready\n\n"
    for surface in surfaces:
        path = workdir / "drafts" / f"signal-{signal_id}-{_surface_file(surface)}"
        exists = path.exists()
        body += f"- {'[x]' if exists else '[ ]'} {surface}: `{path}`\n"
    body += (
        f"\nReview all surfaces and the markets review.\n"
        f"Approve by creating:\n"
        f"`{workdir / 'gates' / gate_name / 'APPROVED'}`\n\n"
        f"Reject by creating:\n"
        f"`{workdir / 'gates' / gate_name / 'REJECTED'}`\n"
    )
    _request_gate(workdir, gate_name, body)


# --------------------------------------------------------------------------- #
# analytics — Buffer collection + LLM analysis
# --------------------------------------------------------------------------- #
def _run_ga4_smoke_test(env: dict[str, str]) -> bool:
    """Run the GA4 MCP smoke test and return True if it connected."""
    import subprocess as sp
    repo = Path(__file__).resolve().parent
    python = sys.executable
    test_script = repo / "harness" / "test_ga_mcp.py"
    if not test_script.exists():
        print("GA4 test script not found; skipping smoke test.")
        return False
    env_override = {**os.environ, **env}
    print("\nRunning GA4 MCP smoke test...")
    result = sp.run([python, str(test_script)], env=env_override, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return False
    return True


def _configure_analytics_interactive(env: dict[str, str], args) -> dict:
    """Ask the operator which data sources to include and return a config dict."""
    print("\n=== Analytics Agent — data source selection ===")
    print("The agent will always pull Buffer social data if BUFFER_MCP_TOKEN is set.")

    choices = [
        ("Buffer only", "LinkedIn, X, Instagram, Facebook from Buffer"),
        ("Buffer + Substack CSV", "Merge a Substack posts-export CSV"),
        ("Buffer + GA4 (test)", "Also run the Google Analytics 4 connection smoke test"),
        ("All of the above", "Buffer + Substack CSV + GA4 test"),
    ]
    idx = _prompt_choice("What do you want to include in this analytics run?", choices, default_idx=0)
    include_substack = idx in (1, 3)
    include_ga4 = idx in (2, 3)

    substack_csv_path = None
    substack_csv_mapping = None
    if include_substack:
        default_csv = env.get("SUBSTACK_CSV_PATH", "")
        substack_csv_path = _prompt_input("Path to Substack posts export CSV", default=default_csv)
        default_map = env.get("SUBSTACK_CSV_MAPPING", "")
        raw_map = input(f"Path to JSON column-mapping file (optional){f' [{default_map}]' if default_map else ''}: ").strip()
        substack_csv_mapping = raw_map or default_map or None

    if include_ga4:
        print("\n--- GA4 credentials (required for the smoke test) ---")
        default_creds = env.get("GOOGLE_APPLICATION_CREDENTIALS", "")
        default_project = env.get("GOOGLE_CLOUD_PROJECT", "")
        default_property = env.get("GA_PROPERTY_ID", "")
        creds = _prompt_input("Path to service-account JSON key", default=default_creds)
        project = _prompt_input("GCP project ID", default=default_project)
        prop = _prompt_input("GA4 property ID (numeric)", default=default_property)
        env["GOOGLE_APPLICATION_CREDENTIALS"] = creds
        env["GOOGLE_CLOUD_PROJECT"] = project
        env["GA_PROPERTY_ID"] = prop

    default_lookback = str(getattr(args, "analytics_days", 30))
    lookback_days = int(_prompt_input("Lookback window in days", default=default_lookback))

    default_describe = getattr(args, "describe_assets", False)
    describe_assets = _prompt_yes_no("Describe post images with a vision model? Requires OPENAI_API_KEY.", default=default_describe)

    default_direct = getattr(args, "direct_llm", False)
    direct_llm = _prompt_yes_no("Use direct Kimi LLM for the analysis instead of the file bridge? Faster, but uses API credits.", default=default_direct)

    return {
        "lookback_days": lookback_days,
        "describe_assets": describe_assets,
        "substack_csv_path": substack_csv_path,
        "substack_csv_mapping": substack_csv_mapping,
        "include_ga4": include_ga4,
        "direct_llm": direct_llm,
    }


def cmd_analytics(services: Services, workdir: Path, args) -> None:
    """Collect Buffer metrics and run the analytics analysis prompt."""
    env = services.env if services else dict(os.environ)
    token = env.get("BUFFER_MCP_TOKEN", "")
    if not token:
        raise SystemExit(
            "BUFFER_MCP_TOKEN not set. Add it to .env to use the analytics agent."
        )

    interactive = _is_interactive(args)
    if interactive:
        config = _configure_analytics_interactive(env, args)
    else:
        config = {
            "lookback_days": getattr(args, "analytics_days", 30),
            "describe_assets": getattr(args, "describe_assets", False),
            "substack_csv_path": getattr(args, "substack_csv", None) or env.get("SUBSTACK_CSV_PATH"),
            "substack_csv_mapping": getattr(args, "substack_csv_mapping", None) or env.get("SUBSTACK_CSV_MAPPING"),
            "include_ga4": False,
            "direct_llm": getattr(args, "direct_llm", False),
        }

    lookback_days = config["lookback_days"]
    describe_assets = config["describe_assets"]
    substack_csv_path = config["substack_csv_path"]
    substack_csv_mapping = config["substack_csv_mapping"]
    organization_id = env.get("BUFFER_ORGANIZATION_ID") or None
    channel_ids = None
    if env.get("BUFFER_CHANNEL_IDS"):
        channel_ids = [c.strip() for c in env["BUFFER_CHANNEL_IDS"].split(",") if c.strip()]

    if config.get("include_ga4"):
        ga_ok = _run_ga4_smoke_test(env)
        if ga_ok:
            print("GA4 smoke test succeeded. Note: GA4 data is not yet merged into the normalized analytics report.")
        else:
            print("GA4 smoke test failed or was skipped. Continuing with Buffer/Substack data only.")

    with BufferMCPClient(token) as client:
        collector = AnalyticsCollector(
            client,
            workdir,
            download_assets=True,
            describe_assets=describe_assets,
            openai_api_key=env.get("OPENAI_API_KEY"),
            substack_csv_path=substack_csv_path,
            substack_csv_mapping=substack_csv_mapping,
        )
        raw_path, norm_path = collector.run(
            organization_id=organization_id,
            channel_ids=channel_ids,
            lookback_days=lookback_days,
        )
    print(f"Collected Buffer metrics: {norm_path}")
    print(f"Raw Buffer response:      {raw_path}")
    if substack_csv_path:
        print(f"Substack CSV merged:      {substack_csv_path}")
    if describe_assets:
        print("Asset descriptions generated (or attempted; see metrics file).")

    analyzer = AnalyticsAnalyzer(
        services.router,
        workdir,
        memory_factory=services.memory_factory if services else None,
        direct_model=("openai/kimi-for-coding" if config.get("direct_llm") else None),
        openai_api_key=env.get("VISION_API_KEY") or env.get("OPENAI_API_KEY"),
    )
    analysis_path = analyzer.run(norm_path)
    print(f"Analysis report:          {analysis_path}")


# --------------------------------------------------------------------------- #
# start — pick a scout and begin the run
# --------------------------------------------------------------------------- #
def cmd_start(services: Services, workdir: Path, args) -> None:
    """Show a startup menu so the operator picks which scout to run."""
    state = load_state(workdir)
    date = args.date or current_date(state)
    state["date"] = date
    save_state(workdir, state)

    gate_name = f"scout_selection_{date}"
    gdir = _gate_dir(workdir, gate_name)
    response_file = gdir / "RESPONSE.md"

    # If a scout is already chosen, run it.
    if response_file.exists():
        scout = _parse_scout_selection(response_file)
        if not scout:
            _clear_gate(workdir, gate_name)
            raise SystemExit(
                f"Could not parse scout selection from {response_file}. "
                f"Clear the gate and re-run start."
            )
        print(f"Scout selected: {scout}")

        handlers = {
            "signal_identifier": cmd_signal_identifier,
            "macro_scout": cmd_macro_scout,
            "india_news_scout": cmd_india_news_scout,
            "x_scout": cmd_x_scout,
            "reddit_scout": cmd_reddit_scout,
        }
        handlers[scout](services, workdir, args)

        # If the scout produced a digest, move on to signal selection.
        available = _available_digest_sources(workdir, date)
        if available:
            print("\nScout complete. Moving to signal selection.")
            cmd_select_signal(services, workdir, args)
        return

    # Build the menu gate.
    body = (
        f"# Scout Selection — {date}\n\n"
        f"Pick which lens to run today. The harness will run that scout, "
        f"then move to signal selection.\n\n"
        f"## Available scouts\n\n"
    )
    for key, (title, desc) in _SCOUT_CHOICES.items():
        body += f"### `{key}`\n- **{title}**\n- {desc}\n\n"
    body += (
        f"\n## How to respond\n\n"
        f"Write `{gdir / 'RESPONSE.md'}` with:\n"
        f"```yaml\n"
        f"scout: macro_scout\n"
        f"```\n\n"
        f"Or just the command name on one line:\n"
        f"```\n"
        f"macro_scout\n"
        f"```\n"
    )
    _request_gate(workdir, gate_name, body)


# --------------------------------------------------------------------------- #
# run_all — advance as far as possible
# --------------------------------------------------------------------------- #
def cmd_run_all(services: Services, workdir: Path, args) -> None:
    """Run the pipeline until a gate or LLM request blocks."""
    state = load_state(workdir)

    # 1. Digest — any available source satisfies this step.
    date = args.date or current_date(state)
    available = _available_digest_sources(workdir, date)
    if not available:
        print("No digest found. Run: python run_layer2_full.py start")
        raise SystemExit(1)

    # 2. Selection.
    if "signal_id" not in state:
        print("Step: select_signal")
        cmd_select_signal(services, workdir, args)
        state = load_state(workdir)

    # 3. Research.
    signal_id = state["signal_id"]
    surfaces = state.get("surfaces", DEFAULT_SURFACES)
    research_file = workdir / "research" / f"signal-{signal_id}.md"
    gate_name = "research_approval"
    try:
        research_approved = research_file.exists() and _check_approval_gate(workdir, gate_name)
    except GateRejected:
        raise
    if not research_approved:
        print("Step: research")
        cmd_research(services, workdir, args)

    # 4. Write.
    print("Step: write")
    cmd_write(services, workdir, args)

    # 5. Review + correction loop.
    judge = Layer2ContentJudge(
        services.router, workdir,
        memory_factory=services.memory_factory if services else None,
    )
    review_file = judge.review_path(signal_id)
    if review_file.exists() and not args.force:
        print("Step: review (existing review file found, skipping)")
        verdict = Verdict(verdict="pass", issues=[], score=1.0,
                          meta={"review_file": str(review_file),
                                "blocker_surfaces": [],
                                "review_text": review_file.read_text(encoding="utf-8")})
    else:
        print("Step: review")
        verdict = judge.run(signal_id, surfaces)
    while verdict.verdict != "pass":
        loop_key = f"correction_loops_{signal_id}"
        if state.get(loop_key, 0) >= MAX_CORRECTION_LOOPS:
            print("Step: correction limit reached")
            break
        print("Step: correct")
        cmd_correct(services, workdir, args)
        state = load_state(workdir)
        print("Step: review")
        verdict = judge.run(signal_id, surfaces)

    # 6. SEO (blog only).
    if "blog" in surfaces:
        print("Step: seo")
        try:
            cmd_seo(services, workdir, args)
        except GatePending:
            raise

    # 7. Publish approval.
    print("Step: publish_approval")
    cmd_publish_approval(services, workdir, args)

    print("\nPipeline complete for this signal.")


def cmd_status(services: Services, workdir: Path, args) -> None:
    """Print current state."""
    state = load_state(workdir)
    print("Layer 2 Full Run State")
    print("-" * 40)
    for k, v in sorted(state.items()):
        print(f"{k}: {v}")
    print("-" * 40)
    digest = workdir / "signals" / f"{current_date(state)}-digest.md"
    print(f"Digest exists: {digest.exists()}")
    if "signal_id" in state:
        sid = state["signal_id"]
        print(f"Research exists: {(workdir / 'research' / f'signal-{sid}.md').exists()}")
        for s in state.get("surfaces", DEFAULT_SURFACES):
            print(f"Draft {s} exists: "
                  f"{(workdir / 'drafts' / f'signal-{sid}-{_surface_file(s)}').exists()}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser("run_layer2_full.py")
    ap.add_argument("command", choices=[
        "start", "signal_identifier", "macro_scout", "india_news_scout", "x_scout", "reddit_scout",
        "select_signal", "research", "write", "review", "correct", "seo",
        "publish_approval", "analytics", "run_all", "status",
    ])
    ap.add_argument("--date", default=None,
                    help="Digest/ticket date override (YYYY-MM-DD).")
    ap.add_argument("--force", action="store_true",
                    help="Re-run even if output already exists.")
    ap.add_argument("--analytics-days", type=int, default=30,
                    help="Lookback window in days for the analytics agent (default: 30).")
    ap.add_argument("--describe-assets", action="store_true",
                    help="Download post images and describe them with a vision model (requires OPENAI_API_KEY).")
    ap.add_argument("--substack-csv", default=None,
                    help="Path to a Substack posts export CSV to merge into analytics (or set SUBSTACK_CSV_PATH in .env).")
    ap.add_argument("--substack-csv-mapping", default=None,
                    help="Path to a JSON file mapping canonical metadata fields to CSV column names (or set SUBSTACK_CSV_MAPPING in .env).")
    ap.add_argument("--non-interactive", action="store_true",
                    help="Skip interactive prompts for analytics; use CLI flags and .env values only. Default is interactive.")
    ap.add_argument("--direct-llm", action="store_true",
                    help="Use Kimi directly for the analytics analysis instead of the file-based bridge (requires VISION_API_KEY or OPENAI_API_KEY).")
    ap.add_argument("--openai-api-key", default=None,
                    help="API key for --direct-llm (or set VISION_API_KEY / OPENAI_API_KEY in .env).")
    args = ap.parse_args(argv)

    env = load_env(str(REPO / ".env")) if (REPO / ".env").exists() else dict(os.environ)
    workdir = REPO / WORKDIR_NAME
    ensure_workdir(workdir)

    # Seed memory once.
    mem_db = workdir / "data" / "memory.db"
    if not mem_db.exists() or args.force:
        seed_counts = seed_all(db_path=str(mem_db))
        print("Seeded Layer 2 memory:")
        for ns, n in seed_counts.items():
            print(f"  {ns}: {n} lessons")

    services = build_services(workdir, env)

    # Build config so Services wiring is exercised.
    _ = build_config(services)

    handlers = {
        "start": cmd_start,
        "signal_identifier": cmd_signal_identifier,
        "macro_scout": cmd_macro_scout,
        "india_news_scout": cmd_india_news_scout,
        "x_scout": cmd_x_scout,
        "reddit_scout": cmd_reddit_scout,
        "select_signal": cmd_select_signal,
        "research": cmd_research,
        "write": cmd_write,
        "review": cmd_review,
        "correct": cmd_correct,
        "seo": cmd_seo,
        "publish_approval": cmd_publish_approval,
        "analytics": cmd_analytics,
        "run_all": cmd_run_all,
        "status": cmd_status,
    }

    try:
        handlers[args.command](services, workdir, args)
    except GatePending as e:
        print(f"\n{e}")
        return 0
    except GateRejected as e:
        print(f"\nRejected: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
