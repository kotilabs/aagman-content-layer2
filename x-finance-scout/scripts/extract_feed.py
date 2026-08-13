#!/usr/bin/env python3
"""extract_feed.py — scroll the logged-in X home feed via browser-use CLI and dump tweets to JSON.

Same access pattern as aagman-harness-run/harness_agents/x_scout_agent.py:
browser-use --profile kotilabs.com --headed open https://x.com/home, then
scroll + eval JS extraction loop.

Usage: python3 extract_feed.py [target_tweets]   (default 60)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROFILE = "kotilabs.com"
HOME_URL = "https://x.com/home"
SCROLL_AMOUNT = 900
PAUSE_BETWEEN_SCROLLS = 1.5
OUT_DIR = Path(__file__).resolve().parent.parent / "state"

EXTRACT_JS = """
Array.from(document.querySelectorAll('article[data-testid="tweet"]')).map(article => {
  const textEl = article.querySelector('[data-testid="tweetText"]');
  const text = textEl ? (textEl.innerText || '').trim() : '';

  const nameEl = article.querySelector('[data-testid="User-Name"]');
  let authorName = '';
  let authorHandle = '';
  if (nameEl) {
    const links = Array.from(nameEl.querySelectorAll('a'));
    const handleLink = links.find(a => a.getAttribute('href') && a.getAttribute('href').startsWith('/'));
    authorHandle = handleLink ? handleLink.getAttribute('href').replace(/^\\//, '') : '';
    authorName = (nameEl.innerText || '').replace(new RegExp('\\\\s*@' + authorHandle + '\\\\s*$', 'i'), '').trim();
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

  const tweetId = (permalink.match(/\\/status\\/(\\d+)/) || [])[1] || '';

  const metrics = {};
  ['reply', 'retweet', 'like'].forEach(kind => {
    const el = article.querySelector(`[data-testid="${kind}"]`);
    if (el) metrics[kind] = (el.innerText || '').replace(/[^0-9.KM]/gi, '').trim();
  });

  return { tweetId, authorName, authorHandle, text, createdAt, permalink, metrics };
})
"""


def run_bu(args: list[str], timeout: float = 60.0) -> str:
    result = subprocess.run(
        ["browser-use"] + args, capture_output=True, text=True, timeout=timeout, check=False
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"browser-use failed ({result.returncode}): {err[:500]}")
    return result.stdout or ""


def eval_js(js: str) -> object:
    wrapped = f"JSON.stringify((function(){{ return ({js}); }})())"
    out = run_bu(["eval", wrapped])
    m = re.search(r"^result:\s*(.+)$", out, re.MULTILINE)
    if not m:
        raise RuntimeError(f"Could not parse eval output: {out[:500]}")
    return json.loads(m.group(1).strip())


def main() -> None:
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        run_bu(["close", "--all"], timeout=30)
    except Exception:
        pass

    print(f"Opening {HOME_URL} (profile={PROFILE}) ...", flush=True)
    out = run_bu(["--profile", PROFILE, "--headed", "open", HOME_URL], timeout=90)
    if "blocked by network security" in out.lower() or "unusual traffic" in out.lower():
        raise SystemExit("X blocked navigation — open the browser and check login manually.")
    time.sleep(4)

    all_tweets: list[dict] = []
    seen: set[str] = set()
    stagnant = 0

    while len(all_tweets) < target and stagnant < 3:
        before = len(all_tweets)
        tweets = eval_js(EXTRACT_JS)
        if isinstance(tweets, list):
            for t in tweets:
                key = t.get("permalink") or t.get("tweetId")
                if key and key not in seen:
                    seen.add(key)
                    all_tweets.append(t)
        print(f"  pass: {len(all_tweets)} unique tweets", flush=True)
        stagnant = stagnant + 1 if len(all_tweets) == before else 0
        if len(all_tweets) < target:
            try:
                run_bu(["scroll", "down", "--amount", str(SCROLL_AMOUNT)], timeout=30)
            except Exception:
                pass
            time.sleep(PAUSE_BETWEEN_SCROLLS)

    out_path = OUT_DIR / f"feed-{datetime.now():%Y%m%d-%H%M%S}.json"
    out_path.write_text(json.dumps({"collected": len(all_tweets), "tweets": all_tweets}, indent=1))
    print(f"Saved {len(all_tweets)} tweets -> {out_path}")


if __name__ == "__main__":
    main()
