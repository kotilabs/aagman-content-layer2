"""reddit_scout_agent.py — Reddit Scout agent for the content harness.

Fetches posts from configured Indian finance/investing subreddits via browser
automation, reads full bodies + top comments, and clusters topics using an LLM.

Can be used standalone or wired into the harness runner.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from harness_configs.reddit_scout_agent_config import RedditScoutConfig
from harness_core.run import load_env


class BrowserUseError(Exception):
    pass


class RedditScoutAgent:
    """Scout Reddit for finance/investing topics and cluster them."""

    def __init__(self, config: RedditScoutConfig | None = None):
        self.config = config or RedditScoutConfig.default()
        self.workdir = Path(self.config.workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.env = load_env(str(REPO / ".env")) if (REPO / ".env").exists() else dict(os.environ)
        self._session_started = False

    # -- public API -------------------------------------------------------- #

    def run(self, dt: str | None = None, subreddits: list[str] | None = None) -> Path:
        """Run a full scout + cluster pass. Return path to cluster markdown."""
        dt = dt or date.today().isoformat()
        subs = subreddits or self.config.subreddits

        posts = self.fetch_all(dt, subs)
        self._save_raw_posts(dt, posts)

        for sort in self.config.sorts:
            if not posts[sort]:
                print(f"No posts for {sort}, skipping clustering.")
                continue
            response = self._cluster_posts(posts[sort], sort)
            self._save_cluster_response(dt, sort, response)

        return self._write_cluster_markdown(dt, posts)

    def fetch_all(self, dt: str, subreddits: list[str] | None = None) -> dict[str, list[dict]]:
        """Fetch posts for the given subreddits and sorts."""
        subs = subreddits or self.config.subreddits
        self._open_session()
        try:
            results: dict[str, list[dict]] = {sort: [] for sort in self.config.sorts}
            for idx, subreddit in enumerate(subs):
                for sort in self.config.sorts:
                    try:
                        fetched = self._fetch_subreddit_sort(subreddit, sort)
                        results[sort].extend(fetched)
                    except Exception as e:
                        print(f"  Failed r/{subreddit}/{sort}: {e}")

                if idx < len(subs) - 1:
                    print(f"\n  Pausing {self.config.pause_between_subreddits}s before next subreddit...")
                    time.sleep(self.config.pause_between_subreddits)
            return results
        finally:
            self._close_session()

    # -- browser automation helpers ---------------------------------------- #

    def _run_bu(self, args: list[str], timeout: float = 60.0) -> str:
        cmd = ["browser-use"]
        session = os.environ.get("BROWSER_USE_SESSION")
        if session:
            cmd.extend(["--session", session])
        cmd.extend(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            raise BrowserUseError(f"browser-use timed out: {' '.join(cmd)}") from exc

        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()
            raise BrowserUseError(f"browser-use failed ({result.returncode}): {err[:500]}")
        return result.stdout or ""

    def _open_session(self) -> None:
        try:
            self._run_bu(["close", "--all"], timeout=30)
        except BrowserUseError:
            pass

    def _close_session(self) -> None:
        try:
            self._run_bu(["close", "--all"], timeout=30)
        except BrowserUseError:
            pass
        self._session_started = False

    def _navigate(self, url: str, timeout: float = 60.0) -> None:
        if self._session_started:
            out = self._run_bu(["open", url], timeout=timeout)
        else:
            args: list[str] = []
            if self.config.headed:
                args.append("--headed")
            if os.environ.get("BROWSER_USE_CDP_URL"):
                args.extend(["--cdp-url", os.environ["BROWSER_USE_CDP_URL"]])
            else:
                args.extend(["--profile", self.config.browser_profile])
            args.extend(["open", url])
            out = self._run_bu(args, timeout=timeout)
            self._session_started = True

        if "blocked by network security" in out.lower():
            raise BrowserUseError(f"Reddit blocked navigation to {url}")
        time.sleep(2.5)

    def _scroll_feed(self) -> None:
        for _ in range(self.config.feed_scrolls):
            try:
                self._run_bu(["scroll", "down", "--amount", "800"], timeout=30)
                time.sleep(1.5)
            except BrowserUseError:
                break

    def _eval_js(self, js: str, timeout: float = 60.0) -> Any:
        wrapped = f"JSON.stringify((function(){{ return ({js}); }})())"
        out = self._run_bu(["eval", wrapped], timeout=timeout)
        m = re.search(r"^result:\s*(.+)$", out, re.MULTILINE)
        if not m:
            raise BrowserUseError(f"Could not parse eval output: {out[:500]}")
        raw = m.group(1).strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BrowserUseError(f"Invalid JSON from eval: {raw[:500]}") from exc

    def _fetch_subreddit_sort(self, subreddit: str, sort: str) -> list[dict]:
        url = f"https://www.reddit.com/r/{subreddit}/{sort}/"
        print(f"\nFetching r/{subreddit}/{sort} ...")
        self._navigate(url)
        self._scroll_feed()

        posts = self._extract_posts_from_feed(subreddit, sort)
        print(f"  Found {len(posts)} posts on feed")

        detailed = []
        for i, post in enumerate(posts, 1):
            print(f"  Reading post {i}/{len(posts)}: {post.get('title', '')[:60]}...")
            detailed.append(self._extract_post_detail(post))
            time.sleep(self.config.pause_between_posts)

        return detailed

    def _extract_posts_from_feed(self, subreddit: str, sort: str) -> list[dict]:
        limit = self.config.limit
        js = f"""
        Array.from(document.querySelectorAll('shreddit-post')).slice(0,{limit}).map(p => {{
          const postId = p.getAttribute('id') || p.getAttribute('data-post-id') || '';
          const title = p.getAttribute('post-title') || '';
          const permalink = p.getAttribute('permalink') || '';
          const score = parseInt(p.getAttribute('score') || '0', 10);
          const numComments = parseInt(p.getAttribute('comment-count') || '0', 10);
          const author = p.getAttribute('author') || '';
          const postType = p.getAttribute('post-type') || '';
          const subredditName = p.getAttribute('subreddit-name') || '{subreddit}';
          const created = p.getAttribute('created-timestamp') || '';
          const contentHref = p.getAttribute('content-href') || '';
          const bodyPreview = (p.innerText || '').split('\\n').filter(l => l.trim()).slice(0,8).join('\\n');
          return {{postId, title, permalink, score, numComments, author, postType,
                   subreddit: subredditName, created, contentHref, bodyPreview}};
        }})
        """
        posts = self._eval_js(js)
        if not isinstance(posts, list):
            return []
        seen = set()
        unique = []
        for p in posts:
            key = p.get("postId") or p.get("permalink")
            if key and key not in seen:
                seen.add(key)
                unique.append(p)
        return unique

    def _extract_post_detail(self, post: dict) -> dict:
        permalink = post.get("permalink")
        if not permalink:
            return post

        url = f"https://www.reddit.com{permalink}" if permalink.startswith("/") else permalink
        try:
            self._navigate(url, timeout=60)
            time.sleep(2)
        except BrowserUseError as e:
            post["body"] = ""
            post["top_comments"] = []
            post["fetch_error"] = str(e)
            return post

        body = self._extract_post_body()
        comments = self._extract_post_comments()

        post["body"] = body
        post["top_comments"] = comments
        return post

    def _extract_post_body(self) -> str:
        js = """
        (function(){
          const post = document.querySelector('shreddit-post');
          if (!post) return '';
          const text = post.innerText || '';
          const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
          const start = Math.max(0, lines.findIndex(l => l.length > 80 || l.includes('.') || l.includes('?')));
          return lines.slice(start).join('\\n').slice(0,3000);
        })()
        """
        try:
            body = self._eval_js(js)
            return body if isinstance(body, str) else ""
        except Exception:
            return ""

    def _extract_post_comments(self) -> list[dict]:
        limit = self.config.comments_per_post
        js = f"""
        Array.from(document.querySelectorAll('shreddit-comment')).slice(0,{limit + 1}).map(c => {{
          const author = c.getAttribute('author') || '';
          const text = (c.innerText || '').replace(/\\n+/g, ' ').trim();
          return {{author, text: text.slice(0,800)}};
        }}).filter(c => c.author !== 'AutoModerator' && c.text.length > 10)
        """
        try:
            comments = self._eval_js(js)
            return comments if isinstance(comments, list) else []
        except Exception:
            return []

    # -- persistence ------------------------------------------------------- #

    def _save_raw_posts(self, dt: str, posts: dict[str, list[dict]]) -> None:
        raw_dir = self.workdir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / f"{dt}_raw_posts.json"
        raw_path.write_text(json.dumps(posts, indent=2), encoding="utf-8")
        print(f"\nWrote raw posts: {raw_path}")

    def _save_cluster_response(self, dt: str, sort: str, response: str) -> None:
        resp_dir = self.workdir / "responses"
        resp_dir.mkdir(parents=True, exist_ok=True)
        resp_path = resp_dir / f"{dt}_reddit_clusters_{sort}.md"
        resp_path.write_text(response, encoding="utf-8")
        print(f"Wrote {sort} cluster response: {resp_path}")

    def _write_cluster_markdown(self, dt: str, posts: dict[str, list[dict]]) -> Path:
        cluster_file = self.workdir / f"{dt}_reddit_clusters.md"
        lines = [f"# Reddit Clusters — {dt}", ""]

        for sort in self.config.sorts:
            resp_path = self.workdir / "responses" / f"{dt}_reddit_clusters_{sort}.md"
            if not resp_path.exists():
                lines.append(f"## {sort.upper()} Posts Clusters")
                lines.append("")
                lines.append(f"*No cluster response yet for {sort}.*")
                lines.append("")
                continue

            response_text = resp_path.read_text(encoding="utf-8").strip()
            lines.append(f"## {sort.upper()} Posts Clusters")
            lines.append("")
            lines.append(response_text)
            lines.append("")
            lines.append(f"*Raw posts: {len(posts[sort])}*")
            lines.append("")

        cluster_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote clusters: {cluster_file}")
        return cluster_file

    # -- LLM clustering ---------------------------------------------------- #

    def _cluster_posts(self, posts: list[dict], sort: str) -> str:
        prompt = self._build_clustering_prompt(posts, sort)

        direct = self._direct_llm_call(prompt)
        if direct:
            return direct

        # Fallback: write request file and raise so caller can provide response.
        req_id = f"reddit-cluster-{sort}-{uuid.uuid4().hex[:8]}"
        req_dir = self.workdir / "gates" / "llm_requests"
        resp_dir = self.workdir / "gates" / "llm_responses"
        req_dir.mkdir(parents=True, exist_ok=True)
        resp_dir.mkdir(parents=True, exist_ok=True)
        req_file = req_dir / f"{req_id}.md"
        resp_file = resp_dir / f"{req_id}.md"

        header = (
            f"# LLM Request\n\n"
            f"- model: `{self.config.llm_model}`\n"
            f"- request id: `{req_id}`\n"
            f"- response path: `{resp_file}`\n\n"
            f"---\n\n"
        )
        req_file.write_text(header + prompt, encoding="utf-8")
        print(f"\nNo direct LLM key configured. Request written: {req_file}")
        print(f"Provide response at: {resp_file}")
        return f"*Awaiting LLM response at {resp_file}*"

    def _build_clustering_prompt(self, posts: list[dict], sort: str) -> str:
        post_blocks = []
        for i, post in enumerate(posts, 1):
            block = [
                f"### Post {i}",
                f"Subreddit: r/{post.get('subreddit', '')}",
                f"Title: {post.get('title', '')}",
                f"Score: {post.get('score', 0)} | Comments: {post.get('numComments', 0)}",
                f"Permalink: https://www.reddit.com{post.get('permalink', '')}",
                f"Author: u/{post.get('author', '')}",
            ]
            body = post.get("body", "") or post.get("bodyPreview", "")
            block.append(f"Body:\n{body[:2000]}")
            comments = post.get("top_comments", [])
            if comments:
                block.append("Top comments:")
                for c in comments:
                    author = c.get("author", "")
                    text = c.get("text", "")
                    block.append(f"- u/{author}: {text[:500]}")
            post_blocks.append("\n".join(block))

        return self.config.clustering_prompt_template.format(
            sort_upper=sort.upper(),
            comments_per_post=self.config.comments_per_post,
            posts="\n\n".join(post_blocks),
        )

    def _direct_llm_call(self, prompt: str) -> str | None:
        if OpenAI is None:
            return None

        api_key: str | None = None
        base_url: str | None = None
        model: str | None = None

        if self.env.get("OPENAI_API_KEY"):
            api_key = self.env["OPENAI_API_KEY"]
            base_url = self.env.get("OPENAI_BASE_URL")
            model = self.env.get("LLM_MODEL", self.config.llm_model)
        elif self.env.get("OPENAI_COMPATIBLE_API_KEY") and self.env.get("OPENAI_COMPATIBLE_BASE_URL"):
            api_key = self.env["OPENAI_COMPATIBLE_API_KEY"]
            base_url = self.env["OPENAI_COMPATIBLE_BASE_URL"]
            model = self.env.get("LLM_MODEL", self.config.llm_model)

        if not api_key or not model:
            return None

        client = OpenAI(api_key=api_key, base_url=base_url)
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.llm_temperature,
                max_tokens=self.config.llm_max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"Direct LLM call failed: {e}")
            return None
