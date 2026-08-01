"""analytics_agent.py — Buffer MCP collection + LLM analysis for Layer 2.

Architecture:
    1. BufferMCPClient      stdlib JSON-RPC caller to https://mcp.buffer.com/mcp
    2. AnalyticsCollector   fetch account/channels/posts/metrics, normalize, persist
    3. AnalyticsAnalyzer    read persisted metrics, run analytics_agent.md prompt

The collector uses only stdlib so it can run without the harness dependency tree.
The analyzer plugs into the harness LLMRouter via `services.router`.
"""
from __future__ import annotations

import csv
import json
import os
import re
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
_BUFFER_MCP_ENDPOINT = "https://mcp.buffer.com/mcp"
_BUFFER_MCP_PROTOCOL_VERSION = "2024-11-05"

_METRIC_ALIASES = {
    "reactions": "likes",
    "comments": "comments",
    "shares": "shares",
    "impressions": "impressions",
    "reach": "reach",
    "views": "views",
    "engagementRate": "engagement_rate",
    "saves": "saves",
    "follows": "follows",
    "postCount": "post_count",
}

# Flexible column-name aliases for Substack export CSVs. Keys are lower-cased;
# the first matching column in the CSV is used.
_SUBSTACK_COLUMN_ALIASES = {
    "id": ["post_id", "id", "post_uuid"],
    "title": ["title", "post_title"],
    "subtitle": ["subtitle", "post_subtitle"],
    "published_at": ["published_at", "post_date", "publish_date", "date", "sent_at"],
    "text": ["body", "content", "post_body", "text"],
    "word_count": ["word_count", "words"],
    "url": ["url", "post_url", "permalink", "link"],
    # Reach / delivery
    "email_deliveries": ["email_deliveries", "deliveries", "delivered", "recipients"],
    "email_opens": ["email_opens", "opens"],
    "email_open_rate": ["email_open_rate", "open_rate", "open_pct"],
    "email_clicks": ["email_clicks", "clicks"],
    "email_click_rate": ["email_click_rate", "click_rate", "click_pct"],
    "email_unsubscribes": ["email_unsubscribes", "unsubscribes"],
    # Surface engagement
    "likes": ["likes", "reactions", "applause", "hearts"],
    "comments": ["comments", "comment_count"],
    "shares": ["shares", "share_count"],
    # Audience
    "free_subscribers": ["free_subscribers", "free_subs"],
    "paid_subscribers": ["paid_subscribers", "paid_subs"],
    "new_free_subscribers": ["new_free_subscribers", "new_free_subs"],
    "new_paid_subscribers": ["new_paid_subscribers", "new_paid_subs"],
}

_TOPIC_KEYWORDS = {
    "india macro": ["india", "rupee", "inr", "sensex", "nifty", "rbi", "fii", "dii"],
    "global macro": ["fed", "us", "china", "global", "treasury", "dollar", "oil", "gold"],
    "policy": ["tariff", "trade war", "regulation", "budget", "government", "policy"],
    "earnings": ["earnings", "revenue", "profit", "ipo", "groww", "listing"],
    "crypto": ["bitcoin", "crypto", "btc", "eth"],
    "ai / tech": ["ai", "data center", "semiconductor", "chip", "switch 2"],
}

_SURFACE_LABELS = {
    "twitter": "X",
    "linkedin": "LinkedIn",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "substack": "Substack",
}


# --------------------------------------------------------------------------- #
# Buffer MCP client (stdlib only)
# --------------------------------------------------------------------------- #
class BufferMCPError(Exception):
    """Raised when the Buffer MCP returns an error."""


class BufferMCPClient:
    """Minimal MCP-over-HTTP client for Buffer.

    Usage:
        with BufferMCPClient(token) as client:
            channels = client.call_tool("list_channels", {"organizationId": org, "first": 50})
    """

    def __init__(self, token: str, endpoint: str | None = None):
        self.token = token
        self.endpoint = endpoint or _BUFFER_MCP_ENDPOINT
        self._initialized = False

    def __enter__(self) -> BufferMCPClient:
        self.initialize()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # Streamable HTTP transport is stateless; nothing to close.
        return None

    def _request(self, payload: dict) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, application/json-rpc, text/event-stream",
                "Authorization": f"Bearer {self.token}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def initialize(self) -> dict:
        res = self._request({
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": _BUFFER_MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "aagman-analytics-agent", "version": "0.1.0"},
            },
        })
        if "error" in res:
            raise BufferMCPError(f"initialize failed: {res['error']}")
        # Required handshake notification.
        self._notify("notifications/initialized", {})
        self._initialized = True
        return res.get("result", {})

    def _notify(self, method: str, params: dict) -> None:
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, application/json-rpc, text/event-stream",
                "Authorization": f"Bearer {self.token}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60):
            pass

    def call_tool(self, name: str, arguments: dict | None = None,
                  req_id: int | str = 1) -> Any:
        if not self._initialized:
            self.initialize()
        res = self._request({
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        })
        if "error" in res:
            raise BufferMCPError(f"tools/call {name} failed: {res['error']}")
        content = res.get("result", {}).get("content", [])
        if not content:
            return None
        text = content[0].get("text", "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Some tools may return plain text; wrap it.
            return text


# --------------------------------------------------------------------------- #
# Collection / normalization
# --------------------------------------------------------------------------- #
def _today() -> str:
    return date.today().isoformat()


def _safe_id(raw: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", raw.lower()).strip("-")


def _parse_iso(dt: str | None) -> datetime | None:
    if not dt:
        return None
    try:
        # Buffer returns ISO with Z; replace for fromisoformat compatibility.
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except ValueError:
        return None


def _topic_bucket(text: str) -> str:
    text_lower = text.lower()
    scores = {
        bucket: sum(1 for kw in kws if kw in text_lower)
        for bucket, kws in _TOPIC_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"


def _creative_description(post: dict) -> str:
    """Best-effort creative format label from Buffer post payload."""
    assets = post.get("assets", [])
    if not assets:
        return "text-only"
    types = [a.get("type") for a in assets]
    if "video" in types:
        return "video"
    if "carousel" in types or len([t for t in types if t == "image"]) > 1:
        return "carousel / multi-image"
    if "image" in types:
        return "single image"
    return "mixed media"


def _has_link(text: str) -> tuple[bool, str]:
    urls = re.findall(r"https?://\S+", text)
    if not urls:
        return False, ""
    # Buffer posts include the link in the body by default.
    return True, "body"


def _normalize_metrics(raw_metrics: list[dict]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for m in raw_metrics:
        key = _METRIC_ALIASES.get(m.get("type"), m.get("type"))
        out[key] = m.get("value")
    return out


@dataclass
class NormalizedPost:
    id: str
    title: str
    surface: str
    surface_label: str
    publish_date: str
    topic_bucket: str
    creative_description: str
    text: str
    link_in_post: bool
    link_location: str
    metrics: dict[str, Any]
    assets: list[dict] = field(default_factory=list)
    asset_descriptions: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Substack CSV ingestion
# --------------------------------------------------------------------------- #
def _resolve_csv_columns(header: list[str]) -> dict[str, str | None]:
    """Map canonical field names to the first matching CSV column name."""
    lower_header = [h.strip().lower() for h in header]
    mapping: dict[str, str | None] = {}
    for canonical, aliases in _SUBSTACK_COLUMN_ALIASES.items():
        matched: str | None = None
        for alias in aliases:
            if alias in lower_header:
                matched = header[lower_header.index(alias)]
                break
        mapping[canonical] = matched
    return mapping


def _substack_creative_description(word_count: int | None) -> str:
    if not word_count:
        return "newsletter"
    if word_count < 500:
        return "short newsletter (<500 words)"
    if word_count < 1200:
        return "medium newsletter (500–1,200 words)"
    return "long-form essay (1,200+ words)"


class SubstackCSVCollector:
    """Read a Substack posts export CSV and normalize rows to NormalizedPost.

    Substack export column names vary by plan and export type; this class uses
    `_SUBSTACK_COLUMN_ALIASES` to tolerate common variants. Any metric columns
    that match are copied into the normalized `metrics` dict under canonical
    names.
    """

    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)

    def read(self) -> list[NormalizedPost]:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Substack CSV not found: {self.csv_path}")

        rows = list(csv.DictReader(self.csv_path.read_text(encoding="utf-8").splitlines()))
        if not rows:
            return []

        cols = _resolve_csv_columns(list(rows[0].keys()))
        posts: list[NormalizedPost] = []
        for idx, row in enumerate(rows):
            title = (row.get(cols["title"]) or "").strip()
            subtitle = (row.get(cols["subtitle"]) or "").strip()
            body = (row.get(cols["text"]) or "").strip()
            text = body if body else (f"{title}\n{subtitle}".strip())
            published = (row.get(cols["published_at"]) or "").strip()

            # Build a stable id if the export does not provide one.
            raw_id = (row.get(cols["id"]) or "").strip()
            post_id = raw_id or _safe_id(f"{published}-{title}") or f"substack-{idx}"

            # Metrics: every canonical key whose column exists and is numeric.
            metrics: dict[str, Any] = {}
            for canonical, col_name in cols.items():
                if not col_name or canonical in ("id", "title", "subtitle", "published_at", "text", "url"):
                    continue
                raw_val = row.get(col_name, "").strip()
                if raw_val == "":
                    continue
                # Accept integers, floats, and percentages like "12.3%".
                clean = raw_val.replace(",", "").replace("%", "").strip()
                try:
                    if "." in clean:
                        metrics[canonical] = float(clean)
                    else:
                        metrics[canonical] = int(clean)
                except ValueError:
                    metrics[canonical] = raw_val

            word_count = metrics.get("word_count")
            link_in_post, link_location = _has_link(text)

            posts.append(NormalizedPost(
                id=post_id,
                title=title[:120],
                surface="substack",
                surface_label="Substack",
                publish_date=published[:10] if published else "",
                topic_bucket=_topic_bucket(text),
                creative_description=_substack_creative_description(
                    int(word_count) if isinstance(word_count, (int, float)) else None
                ),
                text=text,
                link_in_post=link_in_post,
                link_location=link_location,
                metrics=metrics,
                assets=[],
                asset_descriptions=[],
                raw=dict(row),
            ))
        return posts


# --------------------------------------------------------------------------- #
# Asset download / visual description
# --------------------------------------------------------------------------- #
class CreativeDescriber:
    """Download Buffer image/video assets and describe them.

    Vision descriptions are optional. If litellm + an API key are unavailable,
    the describer still downloads the assets and records a type-based label.
    """

    def __init__(self, assets_dir: str | Path, api_key: str | None = None,
                 model: str = "gpt-4o"):
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = api_key
        self.model = model

    def download_post_assets(self, post: dict) -> list[dict]:
        """Download all downloadable assets for a post. Returns asset records."""
        post_id = post.get("id", "unknown")
        post_dir = self.assets_dir / _safe_id(post_id)
        post_dir.mkdir(parents=True, exist_ok=True)

        saved: list[dict] = []
        for idx, asset in enumerate(post.get("assets", [])):
            url = asset.get("source") or asset.get("thumbnail")
            if not url:
                continue
            ext = self._guess_extension(url, asset.get("type", ""))
            filename = f"asset-{idx}.{ext}"
            local_path = post_dir / filename
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=60) as resp, \
                        local_path.open("wb") as f:
                    f.write(resp.read())
                saved.append({
                    "type": asset.get("type"),
                    "mime_type": asset.get("mimeType"),
                    "remote_url": url,
                    "local_path": str(local_path.relative_to(self.assets_dir.parent)),
                })
            except Exception as e:
                saved.append({
                    "type": asset.get("type"),
                    "remote_url": url,
                    "download_error": str(e),
                })
        return saved

    def describe_assets(self, assets: list[dict]) -> list[str]:
        """Return one description string per asset."""
        descriptions = []
        for asset in assets:
            if asset.get("download_error"):
                descriptions.append(f"{asset.get('type', 'asset')}: unavailable ({asset['download_error']})")
                continue
            url = asset.get("remote_url")
            asset_type = asset.get("type", "image")
            if asset_type == "video":
                descriptions.append("Video asset with thumbnail (duration/visual content not analyzed).")
                continue
            vision_desc = self._vision_describe(url)
            if vision_desc:
                descriptions.append(vision_desc)
            else:
                descriptions.append(f"{asset_type.capitalize()} asset: {url}")
        return descriptions

    def _vision_describe(self, image_url: str) -> str | None:
        """Try to get a one-line visual description from a vision model."""
        if not self.api_key:
            return None
        try:
            import litellm
            if self.api_key:
                litellm.api_key = self.api_key
            prompt = (
                "Describe this social-media creative in one concise sentence. "
                "Focus on format (chart, infographic, photo, carousel slide), "
                "dominant visuals, colors, and any headline or data shown. "
                "Do not speculate about performance."
            )
            resp = litellm.completion(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }],
                max_tokens=120,
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception:
            return None

    @staticmethod
    def _guess_extension(url: str, asset_type: str) -> str:
        ext = url.split("?")[0].split(".")[-1].lower()
        if ext in ("jpg", "jpeg", "png", "webp", "gif", "mp4", "mov"):
            return ext
        if asset_type == "video":
            return "mp4"
        return "jpg"


class AnalyticsCollector:
    """Fetch Buffer data and normalize it for the analytics prompt.

    Substack long-form analytics can be merged in via a CSV export; set
    `substack_csv_path` to the path of the Substack posts export.
    """

    def __init__(self, client: BufferMCPClient, workdir: str | Path,
                 download_assets: bool = True, describe_assets: bool = False,
                 openai_api_key: str | None = None,
                 substack_csv_path: str | Path | None = None):
        self.client = client
        self.workdir = Path(workdir)
        self.analytics_dir = self.workdir / "analytics"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self.download_assets = download_assets
        self.describe_assets = describe_assets
        self.substack_csv_path = substack_csv_path
        self._describer: CreativeDescriber | None = None
        if download_assets:
            assets_dir = self.analytics_dir / "assets" / _today()
            self._describer = CreativeDescriber(
                assets_dir, api_key=openai_api_key, model="gpt-4o"
            )

    def fetch_account(self) -> dict:
        return self.client.call_tool("get_account", {})

    def fetch_channels(self, organization_id: str) -> list[dict]:
        res = self.client.call_tool("list_channels", {
            "organizationId": organization_id,
            "first": 250,
        })
        return res if isinstance(res, list) else res.get("nodes", [])

    def fetch_posts(self, organization_id: str, channel_ids: list[str],
                    lookback_days: int = 30, first: int = 100) -> list[dict]:
        """Return raw Buffer post nodes with metrics, filtered to lookback_days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        res = self.client.call_tool("list_posts", {
            "organizationId": organization_id,
            "channelIds": channel_ids,
            "first": first,
            "includeMetrics": True,
        })
        if isinstance(res, str):
            raise BufferMCPError(f"list_posts returned non-JSON: {res[:500]}")
        edges = res.get("edges", [])
        posts = [e["node"] for e in edges]
        filtered = []
        for p in posts:
            ts = _parse_iso(p.get("sentAt") or p.get("dueAt"))
            if ts and ts >= cutoff:
                filtered.append(p)
        return filtered

    def fetch_aggregates(self, organization_id: str, channel_ids: list[str],
                         lookback_days: int = 30) -> dict[str, Any]:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=lookback_days)
        res = self.client.call_tool("get_aggregated_post_metrics", {
            "organizationId": organization_id,
            "startDateTime": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endDateTime": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "channelIds": channel_ids,
        })
        return {
            "period_days": lookback_days,
            "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "metrics": _normalize_metrics(res.get("metrics", [])),
        }

    def normalize(self, posts: list[dict], channels: list[dict]) -> list[NormalizedPost]:
        channel_map = {c["id"]: c for c in channels}
        normalized: list[NormalizedPost] = []
        for post in posts:
            text = post.get("text", "")
            first_line = text.split("\n")[0].strip() or text[:80].strip()
            title = first_line[:120]
            channel = channel_map.get(post.get("channelId"), {})
            service = channel.get("service", post.get("channelService", "unknown"))
            surface_label = _SURFACE_LABELS.get(service, service)
            link_in_post, link_location = _has_link(text)
            due = _parse_iso(post.get("dueAt") or post.get("sentAt"))

            assets: list[dict] = []
            descriptions: list[str] = []
            if self.download_assets and self._describer is not None:
                assets = self._describer.download_post_assets(post)
                if self.describe_assets:
                    descriptions = self._describer.describe_assets(assets)

            normalized.append(NormalizedPost(
                id=post.get("id", ""),
                title=title,
                surface=service,
                surface_label=surface_label,
                publish_date=(due.strftime("%Y-%m-%d") if due else ""),
                topic_bucket=_topic_bucket(text),
                creative_description=_creative_description(post),
                text=text,
                link_in_post=link_in_post,
                link_location=link_location,
                metrics=_normalize_metrics(post.get("metrics", [])),
                assets=assets,
                asset_descriptions=descriptions,
                raw=post,
            ))
        return normalized

    def run(self, organization_id: str | None = None,
            channel_ids: list[str] | None = None,
            lookback_days: int = 30) -> tuple[Path, Path]:
        """Fetch, normalize, and persist. Returns (raw_path, normalized_path)."""
        if organization_id is None:
            account = self.fetch_account()
            organizations = account.get("organizations", [])
            if not organizations:
                raise BufferMCPError("No Buffer organizations found.")
            organization_id = organizations[0]["id"]

        channels = self.fetch_channels(organization_id)
        if channel_ids is None:
            channel_ids = [c["id"] for c in channels if not c.get("isDisconnected")]

        posts = self.fetch_posts(organization_id, channel_ids, lookback_days)
        aggregates = self.fetch_aggregates(organization_id, channel_ids, lookback_days)
        normalized = self.normalize(posts, channels)

        # Merge Substack CSV export if provided.
        substack_posts: list[NormalizedPost] = []
        if self.substack_csv_path:
            substack_posts = SubstackCSVCollector(self.substack_csv_path).read()
            normalized.extend(substack_posts)

        today = _today()
        raw_path = self.analytics_dir / f"{today}-buffer-raw.json"
        norm_path = self.analytics_dir / f"{today}-buffer-metrics.json"

        raw_payload = {
            "organization_id": organization_id,
            "channel_ids": channel_ids,
            "lookback_days": lookback_days,
            "channels": channels,
            "posts": posts,
            "aggregates": aggregates,
        }
        if substack_posts:
            raw_payload["substack_csv_path"] = str(self.substack_csv_path)
            raw_payload["substack_posts"] = [p.raw for p in substack_posts]

        raw_path.write_text(json.dumps(raw_payload, indent=2, default=str), encoding="utf-8")

        norm_path.write_text(json.dumps({
            "date": today,
            "organization_id": organization_id,
            "lookback_days": lookback_days,
            "aggregates": aggregates,
            "channels": [
                {"id": c["id"], "service": c.get("service"), "name": c.get("name"),
                 "display_name": c.get("displayName")}
                for c in channels
            ],
            "posts": [
                {
                    "id": p.id,
                    "title": p.title,
                    "surface": p.surface,
                    "surface_label": p.surface_label,
                    "publish_date": p.publish_date,
                    "topic_bucket": p.topic_bucket,
                    "creative_description": p.creative_description,
                    "asset_descriptions": p.asset_descriptions,
                    "assets": [
                        {"type": a.get("type"), "remote_url": a.get("remote_url")}
                        for a in p.assets
                    ],
                    "link_in_post": p.link_in_post,
                    "link_location": p.link_location,
                    "metrics": p.metrics,
                }
                for p in normalized
            ],
        }, indent=2), encoding="utf-8")

        return raw_path, norm_path


# --------------------------------------------------------------------------- #
# Analysis
# --------------------------------------------------------------------------- #
class AnalyticsAnalyzer:
    """Run the analytics_agent.md prompt over collected Buffer metrics."""

    def __init__(self, router, workdir: str | Path,
                 prompt_path: str | Path | None = None,
                 memory_factory: Callable | None = None):
        self.router = router
        self.workdir = Path(workdir)
        self.prompt_path = (
            Path(prompt_path)
            if prompt_path
            else self.workdir.parent / "harness_content" / "prompts" / "analytics_agent.md"
        )
        self.memory_factory = memory_factory

    def _read_prompt(self) -> str:
        if self.prompt_path.exists():
            return self.prompt_path.read_text(encoding="utf-8")
        # Fallback: traverse from workdir.
        fallback = self.workdir.parent / "harness_content" / "prompts" / "analytics_agent.md"
        if fallback.exists():
            return fallback.read_text(encoding="utf-8")
        raise FileNotFoundError(f"analytics_agent.md not found at {self.prompt_path}")

    def _recall_lessons(self) -> str:
        if not self.memory_factory:
            return ""
        try:
            mem = self.memory_factory("content", "publish")
            lessons = mem.recall("analytics lessons content performance", top_k=10)
            if not lessons:
                return ""
            lines = ["## Past lessons already in memory", ""]
            for lesson in lessons:
                lines.append(f"- {lesson.get('text', '')}")
            return "\n".join(lines) + "\n"
        except Exception:
            return ""

    def _build_prompt(self, metrics_path: Path) -> str:
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
        posts = data.get("posts", [])
        aggregates = data.get("aggregates", {})
        channels = data.get("channels", [])
        lookback = data.get("lookback_days", 30)

        # Surface-level historical averages from this batch.
        surface_stats: dict[str, dict[str, list]] = {}
        for p in posts:
            svc = p.get("surface_label", p.get("surface", "unknown"))
            surface_stats.setdefault(svc, {"impressions": [], "engagement_rate": []})
            m = p.get("metrics", {})
            if "impressions" in m:
                surface_stats[svc]["impressions"].append(m["impressions"])
            if "reach" in m:
                surface_stats[svc]["impressions"].append(m["reach"])
            # Substack uses email deliveries as its reach unit.
            if "email_deliveries" in m:
                surface_stats[svc]["impressions"].append(m["email_deliveries"])
            if "engagement_rate" in m:
                surface_stats[svc]["engagement_rate"].append(m["engagement_rate"])
            # Substack open rate is the closest equivalent to engagement rate.
            if "email_open_rate" in m:
                surface_stats[svc]["engagement_rate"].append(m["email_open_rate"])

        hist = {}
        for svc, vals in surface_stats.items():
            hist[svc] = {
                "median_impressions": _median(vals["impressions"]),
                "median_engagement_rate": _median(vals["engagement_rate"]),
            }

        context = {
            "goal": "brand awareness + credibility for an Indian fintech/trading AI product",
            "primary_success_metric": "impressions first, then engagement rate",
            "audience_context": "Channels: " + ", ".join(
                f"{c.get('display_name', c.get('name'))} ({c.get('service')})"
                for c in channels
            ) + (" + Substack (CSV export)" if any(p.get("surface") == "substack" for p in posts) else ""),
            "lookback_days": lookback,
            "aggregates": aggregates,
            "historical_averages": hist,
            "posts": posts,
        }

        prompt = (
            f"{_read(self.prompt_path)}\n\n"
            f"{_recall_lessons(self.memory_factory)}\n"
            "## Input data\n\n"
            f"```json\n{json.dumps(context, indent=2, default=str)}\n```\n\n"
            "Run the full workflow above and produce the complete Analytics Report."
        )
        return prompt

    def run(self, metrics_path: str | Path | None = None,
            output_path: str | Path | None = None) -> Path:
        metrics_path = Path(metrics_path) if metrics_path else self._latest_metrics()
        if not metrics_path.exists():
            raise FileNotFoundError(f"Metrics file not found: {metrics_path}")

        today = _today()
        if output_path is None:
            output_path = self.workdir / "analytics" / f"{today}-analysis.md"
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        prompt = self._build_prompt(metrics_path)
        res = self.router.complete(
            "complex_planning",
            prompt,
            domain="content",
            step="analytics",
        )
        output_path.write_text(res.get("text", ""), encoding="utf-8")
        return output_path

    def _latest_metrics(self) -> Path:
        candidates = sorted(self.workdir.glob("analytics/*-buffer-metrics.json"))
        if not candidates:
            raise FileNotFoundError("No *-buffer-metrics.json files found.")
        return candidates[-1]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _read(path: str | Path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, TypeError):
        return ""


def _recall_lessons(memory_factory: Callable | None) -> str:
    if not memory_factory:
        return ""
    try:
        mem = memory_factory("content", "publish")
        lessons = mem.recall("analytics lessons content performance", top_k=10)
        if not lessons:
            return ""
        lines = ["## Past lessons already in memory", ""]
        for lesson in lessons:
            lines.append(f"- {lesson.get('text', '')}")
        return "\n".join(lines) + "\n"
    except Exception:
        return ""


def _median(values: list[float]) -> float | None:
    clean = sorted([v for v in values if v is not None])
    if not clean:
        return None
    n = len(clean)
    mid = n // 2
    if n % 2 == 1:
        return clean[mid]
    return (clean[mid - 1] + clean[mid]) / 2.0


# --------------------------------------------------------------------------- #
# CLI / direct run helper
# --------------------------------------------------------------------------- #
def run_analytics_pipeline(
    token: str,
    workdir: str | Path,
    router=None,
    lookback_days: int = 30,
    organization_id: str | None = None,
    channel_ids: list[str] | None = None,
    substack_csv_path: str | Path | None = None,
) -> tuple[Path, Path | None]:
    """One-shot collection; analysis only if a router is provided."""
    with BufferMCPClient(token) as client:
        collector = AnalyticsCollector(
            client, workdir, substack_csv_path=substack_csv_path
        )
        raw_path, norm_path = collector.run(
            organization_id=organization_id,
            channel_ids=channel_ids,
            lookback_days=lookback_days,
        )

    analysis_path: Path | None = None
    if router is not None:
        analyzer = AnalyticsAnalyzer(router, workdir)
        analysis_path = analyzer.run(norm_path)

    return norm_path, analysis_path


if __name__ == "__main__":
    # Standalone collection smoke test (no LLM).
    import sys

    env = {}
    repo = Path(__file__).resolve().parent.parent
    env_path = repo / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env.setdefault(k.strip(), v.strip())

    token = env.get("BUFFER_MCP_TOKEN", "")
    if not token:
        print("BUFFER_MCP_TOKEN not found in .env", file=sys.stderr)
        raise SystemExit(1)

    workdir = repo / "layer2_full_run"
    substack_csv = env.get("SUBSTACK_CSV_PATH")
    with BufferMCPClient(token) as client:
        collector = AnalyticsCollector(client, workdir, substack_csv_path=substack_csv)
        raw, norm = collector.run(lookback_days=30)
    print(f"Raw posts:      {raw}")
    print(f"Normalized:     {norm}")
