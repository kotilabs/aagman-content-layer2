"""x_scout_agent.py — X (Twitter) Home-Feed Scout agent for the content harness.

Scrolls the logged-in user's X home feed via browser automation, skims tweets for
relevance to Indian finance/markets, expands the selected ones, and clusters
topics using an LLM.

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

from harness_configs.x_scout_agent_config import XScoutConfig
from harness_core.run import load_env


class BrowserUseError(Exception):
    pass


class XScoutAgent:
    """Scout the X home feed for Indian finance/investing topics and cluster them."""

    def __init__(self, config: XScoutConfig | None = None):
        self.config = config or XScoutConfig.default()
        self.workdir = Path(self.config.workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.env = load_env(str(REPO / ".env")) if (REPO / ".env").exists() else dict(os.environ)
        self._session_started = False

    # -- public API -------------------------------------------------------- #

    def run(self, dt: str | None = None) -> Path:
        """Run a full home-feed scout + cluster pass. Return path to cluster markdown."""
        dt = dt or date.today().isoformat()

        tweets = self.fetch_feed(dt)
        self._save_raw_tweets(dt, tweets)

        relevant = self._screen_relevance(tweets)
        expanded = self._expand_tweets(relevant)

        response = self._cluster_tweets(expanded)
        self._save_cluster_response(dt, response)

        return self._write_cluster_markdown(dt, tweets, expanded, response)

    def fetch_feed(self, dt: str) -> list[dict]:
        """Scroll the X home feed incrementally and extract tweets."""
        self._open_session()
        try:
            print(f"\nOpening X home feed: {self.config.home_url}")
            self._navigate(self.config.home_url)

            all_tweets: list[dict] = []
            seen = set()
            stagnant = 0

            while len(all_tweets) < self.config.target_tweets and stagnant < 3:
                before = len(all_tweets)

                # Extract whatever is currently in the DOM.
                tweets = self._extract_tweets_from_feed()
                for t in tweets:
                    key = t.get("permalink") or t.get("tweetId")
                    if key and key not in seen:
                        seen.add(key)
                        all_tweets.append(t)

                print(f"  Scroll pass: {len(all_tweets)} unique tweets collected")

                if len(all_tweets) == before:
                    stagnant += 1
                else:
                    stagnant = 0

                if len(all_tweets) < self.config.target_tweets:
                    self._scroll_feed_once()

            print(f"\nFound {len(all_tweets)} unique tweets on feed")
            return all_tweets[: self.config.target_tweets]
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

        if "blocked by network security" in out.lower() or "unusual traffic" in out.lower():
            raise BrowserUseError(f"X blocked navigation to {url}")
        time.sleep(3.0)

    def _scroll_feed_once(self) -> None:
        try:
            self._run_bu(["scroll", "down", "--amount", str(self.config.scroll_amount)], timeout=30)
            time.sleep(self.config.pause_between_scrolls)
        except BrowserUseError:
            pass

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

    def _extract_tweets_from_feed(self) -> list[dict]:
        js = """
        Array.from(document.querySelectorAll('article[data-testid="tweet"]')).map(article => {
          const textEl = article.querySelector('[data-testid="tweetText"]');
          const text = textEl ? (textEl.innerText || '').trim() : '';

          const nameEl = article.querySelector('[data-testid="User-Name"]');
          let authorName = '';
          let authorHandle = '';
          if (nameEl) {
            const links = Array.from(nameEl.querySelectorAll('a'));
            const handleLink = links.find(a => a.getAttribute('href') && a.getAttribute('href').startsWith('/'));
            authorHandle = handleLink ? handleLink.getAttribute('href').replace(/^\//, '') : '';
            authorName = (nameEl.innerText || '').replace(new RegExp('\\s*@' + authorHandle + '\\s*$', 'i'), '').trim();
          }

          const timeEl = article.querySelector('time');
          const createdAt = timeEl ? timeEl.getAttribute('datetime') : '';
          let permalink = '';
          if (timeEl) {
            const link = timeEl.closest('a');
            if (link) permalink = link.getAttribute('href') || '';
          }
          if (!permalink) {
            const statusLink = article.querySelector('a[href*="/status/"]');
            permalink = statusLink ? statusLink.getAttribute('href') : '';
          }
          permalink = permalink.startsWith('http') ? permalink : (permalink ? 'https://x.com' + permalink : '');

          const tweetId = (permalink.match(/\/status\/(\\d+)/) || [])[1] || '';

          const metrics = {};
          ['reply', 'retweet', 'like'].forEach(kind => {
            const el = article.querySelector(`[data-testid="${kind}"]`);
            if (el) {
              const val = (el.innerText || '').replace(/[^0-9.KM]/gi, '').trim();
              metrics[kind] = val;
            }
          });

          const truncated = text.includes('…') || !!article.querySelector('a[href="#"]');

          return { tweetId, authorName, authorHandle, text, createdAt, permalink, metrics, truncated };
        })
        """
        tweets = self._eval_js(js)
        if not isinstance(tweets, list):
            return []
        return tweets

    def _expand_tweets(self, tweets: list[dict]) -> list[dict]:
        """Open each selected tweet permalink and read full text/thread."""
        if not tweets:
            return []

        expanded = []
        limit = self.config.expand_limit
        for i, tweet in enumerate(tweets[:limit], 1):
            permalink = tweet.get("permalink")
            if not permalink:
                expanded.append(tweet)
                continue

            print(f"  Expanding {i}/{min(len(tweets), limit)}: @{tweet.get('authorHandle', '')} — {tweet.get('text', '')[:60]}...")
            try:
                self._navigate(permalink, timeout=60)
                time.sleep(2)
                full = self._extract_tweet_detail()
                tweet["full_text"] = full.get("text", tweet.get("text", ""))
                tweet["thread"] = full.get("thread", [])
                tweet["expanded"] = True
            except BrowserUseError as e:
                tweet["expanded"] = False
                tweet["expand_error"] = str(e)

            expanded.append(tweet)
            if i < min(len(tweets), limit):
                time.sleep(self.config.pause_between_expansions)

        return expanded

    def _extract_tweet_detail(self) -> dict:
        js = """
        (function(){
          const main = document.querySelector('article[data-testid="tweet"]');
          const text = main ? (main.querySelector('[data-testid="tweetText"]') || {}).innerText || '' : '';

          const thread = Array.from(document.querySelectorAll('article[data-testid="tweet"]')).slice(1, 6).map(a => {
            const t = a.querySelector('[data-testid="tweetText"]');
            const author = a.querySelector('[data-testid="User-Name"]');
            return {
              author: author ? (author.querySelector('a') || {}).getAttribute('href') : '',
              text: t ? t.innerText : ''
            };
          }).filter(x => x.text);

          return { text, thread };
        })()
        """
        try:
            result = self._eval_js(js)
            return result if isinstance(result, dict) else {"text": "", "thread": []}
        except Exception:
            return {"text": "", "thread": []}

    # -- persistence ------------------------------------------------------- #

    def _save_raw_tweets(self, dt: str, tweets: list[dict]) -> None:
        raw_dir = self.workdir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / f"{dt}_raw_tweets.json"
        raw_path.write_text(json.dumps(tweets, indent=2), encoding="utf-8")
        print(f"\nWrote raw tweets: {raw_path}")

    def _save_cluster_response(self, dt: str, response: str) -> None:
        resp_dir = self.workdir / "responses"
        resp_dir.mkdir(parents=True, exist_ok=True)
        resp_path = resp_dir / f"{dt}_x_clusters.md"
        resp_path.write_text(response, encoding="utf-8")
        print(f"Wrote cluster response: {resp_path}")

    def _write_cluster_markdown(
        self, dt: str, feed_tweets: list[dict], expanded: list[dict], response: str
    ) -> Path:
        cluster_file = self.workdir / f"{dt}_x_clusters.md"
        lines = [
            f"# X Home-Feed Clusters — {dt}",
            "",
            f"- Tweets skimmed from feed: {len(feed_tweets)}",
            f"- Expanded for clustering: {len(expanded)}",
            "",
            "## Clusters",
            "",
            response,
            "",
        ]
        cluster_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote clusters: {cluster_file}")
        return cluster_file

    # -- LLM helpers ------------------------------------------------------- #

    def _screen_relevance(self, tweets: list[dict]) -> list[dict]:
        if not tweets:
            return []

        prompt = self._build_relevance_prompt(tweets)
        result = self._direct_llm_call(prompt)

        if not result:
            print("No direct LLM available; skipping relevance screen, expanding all.")
            return tweets

        try:
            # Extract JSON array from the response.
            match = re.search(r"\[.*?\]", result, re.DOTALL)
            if match:
                selected_links = json.loads(match.group(0))
            else:
                selected_links = []
        except Exception as e:
            print(f"Failed to parse relevance screen response: {e}")
            selected_links = []

        selected_set = set(selected_links)
        relevant = [t for t in tweets if t.get("permalink") in selected_set]
        print(f"\nRelevance screen: {len(relevant)}/{len(tweets)} tweets selected for expansion")
        return relevant

    def _build_relevance_prompt(self, tweets: list[dict]) -> str:
        blocks = []
        for i, t in enumerate(tweets, 1):
            blocks.append(
                f"### Tweet {i}\n"
                f"Author: {t.get('authorName', '')} (@{t.get('authorHandle', '')})\n"
                f"Text: {t.get('text', '')[:500]}\n"
                f"Likes: {t.get('metrics', {}).get('like', '')} | Retweets: {t.get('metrics', {}).get('retweet', '')} | Replies: {t.get('metrics', {}).get('reply', '')}\n"
                f"Permalink: {t.get('permalink', '')}"
            )
        return self.config.relevance_prompt_template.format(tweets="\n\n".join(blocks))

    def _cluster_tweets(self, tweets: list[dict]) -> str:
        prompt = self._build_clustering_prompt(tweets)
        direct = self._direct_llm_call(prompt)
        if direct:
            return direct

        req_id = f"x-cluster-{uuid.uuid4().hex[:8]}"
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

    def _build_clustering_prompt(self, tweets: list[dict]) -> str:
        blocks = []
        for i, t in enumerate(tweets, 1):
            text = t.get("full_text") or t.get("text", "")
            thread = t.get("thread", [])
            thread_text = "\n".join([f"  → {x.get('author', '')}: {x.get('text', '')}" for x in thread])
            blocks.append(
                f"### Tweet {i}\n"
                f"Author: {t.get('authorName', '')} (@{t.get('authorHandle', '')})\n"
                f"Text:\n{text[:1500]}\n"
                f"{thread_text}\n"
                f"Likes: {t.get('metrics', {}).get('like', '')} | Retweets: {t.get('metrics', {}).get('retweet', '')} | Replies: {t.get('metrics', {}).get('reply', '')}\n"
                f"Permalink: {t.get('permalink', '')}"
            )
        return self.config.clustering_prompt_template.format(tweets="\n\n".join(blocks))

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
