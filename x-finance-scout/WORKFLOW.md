# X Finance Scout — Workflow

Loop: scroll your X home feed → curate finance/econ/markets candidates → **user picks + steers the angle** → research → write → quote-tweet on go-ahead.

Feed access is the same as `aagman-harness-run/harness_agents/x_scout_agent.py`: the **browser-use CLI** with the logged-in `kotilabs.com` profile, headed mode. No X API keys needed. (kimi-webbridge was tried first — its `navigate` hangs on this machine; don't use it for this.)

## Layout

- `scripts/extract_feed.py [target]` — scrolls x.com/home via browser-use, saves tweets to `state/feed-<timestamp>.json` (author, handle, text, metrics, permalink, time)
- `state/` — feed dumps + `posted.jsonl` (never quote the same tweet twice — check this file)
- `drafts/` — writeups before posting
- `research/` — research notes per topic

Posting is driven interactively via browser-use. Proven flow (X composer, learned 2026-08-17):

1. `browser-use --profile kotilabs.com --headed open "https://x.com/compose/post"`
2. `state` → find the `Post text` textbox index (it changes every load, never reuse an old index)
3. Insert text via `eval` with `document.execCommand('insertText', ...)` — `browser-use input` mangles newlines into one block. Clear first with select-all + `execCommand('delete')`.
4. **Verify before touching anything else**: eval the composer and check `chars` and that `innerText.slice(0, N)` matches the draft's exact first words. The clear-and-retype path leaves one stray character behind (posted "aairtel" live because of this). If head ≠ draft head, delete everything and redo — do not proceed with images until text is exact.
5. Images: `browser-use upload <file-input-index> <path>` — ONE file per call. X caps at 4 images/post. The "Add media" button goes `disabled=true` when full; use that as the count check.
6. `eval` a click on `[data-testid="tweetButton"]`.
7. Verify on the profile page (`open https://x.com/<handle>`) — newest post's text head, photo count, timestamp. Check `posted.jsonl` gets the new URL.

Two gotchas: Buffer can't post X long-form (reports the channel as "X Free Profile" and caps at 280 even on Premium accounts) — long posts must go through the browser. And the browser profile's logged-in account may not be the target account — check the composer account switcher, because a mismatch means you can't delete the post later either.

## The loop (human-in-the-loop — the user is the editor)

The agent curates, the user decides. Never auto-pick, never auto-write, never auto-post.

1. **Extract**: `python3 scripts/extract_feed.py 60` — scrolls x.com/home via browser-use (profile `kotilabs.com`, headed), saves ~60 tweets to `state/feed-<timestamp>.json`.
2. **Curate, don't pick**: from the dump, shortlist the 3-5 tweets most worth engaging with — finance, economics, markets, stocks, consumer spending, inflation, rates, jobs, retail, housing, credit. Skip: crypto shills, engagement bait, politics-only, old tweets (>48h), already-posted URLs (check `state/posted.jsonl`).
3. **Verify before presenting (web search, not memory)**: for each shortlisted tweet, run real web searches on its central claim *before* forming any angle. Confirm the claim is true, get the date/numbers right, and find what coverage already exists. Never present an angle built on training-data memory alone — every suggested angle must trace to something found in search. Save one-line sourcing notes per candidate.
4. **Present options to the user** and stop. For each candidate show: author + link, a one-line summary, engagement, why it's worth engaging (grounded in the verification pass — what the coverage says, what's missing from it), and 1-2 possible angles with the facts that back them. Then wait.
5. **User picks + steers**: the user says which tweet(s) to take and any angle/input they want. That input wins over the agent's suggested angles.
6. **Deep research** the chosen topic: go past the verification pass — primary sources (exchange circulars, company reports, official data), 3-4 hard facts, what's missing/wrong/underappreciated in the original post. Save notes with links to `research/`.
7. **Write** the draft in `drafts/`: punchy, plain English, no AI slop (no "delve", no "game-changer", no "It's not X, it's Y"). Length per the user's call — short (≤280 chars) or long-form (~150-200 words) if they want an expanded take. Show the draft in chat.
8. **Post only on explicit go-ahead**: quote-tweet via browser-use (open the tweet permalink in the same profile, Repost → Quote, fill composer, Post). Log to `state/posted.jsonl` (URL, draft file, timestamp).

## Voice rules

- Write for the scroller: the first line must make someone stop mid-feed. A surprising fact or a "sounds boring, isn't" reframe. No throat-clearing.
- Talk to the reader ("you", "your neighbour"), not at them. Concrete over abstract.
- Every draft must answer "what does this mean for a normal person" in plain terms — emis, petrol, savings, salary, grocery bill. The goal is reach: a macro take only travels if a non-finance scroller sees their own life in it.
- All lowercase. No em dashes. Short lines, lots of air.
- No academia/finance jargon ("fiscal dominance", "equilibrium", "repricing" as a noun) — say the plain thing instead.
- Sound like a person with a point of view, not a newsletter.
- One idea per post. Lead with the angle, not a summary of the original tweet.
- Numbers beat adjectives.
- **De-AI every draft before showing it**: run the stop-slop checks (`~/.kimi-code/skills/stop-slop`). Kill filler openers ("here's the thing", "here's why"), rhetorical setups ("sounds X. it isn't."), imperative crutches ("read that again"), "not X, it's Y" contrasts, dramatic one-line fragments used as crutches, pull-quote lines, adverbs, passive voice. Vary rhythm; don't end every section on a punchy one-liner. The story must flow — each line earns the next, no whiplash pivots.
- Never make up a stat — every number comes from the research step.

## Failure modes

- **X layout change**: scripts key off `data-testid` attributes (`tweet`, `retweet`, `tweetTextarea_0`, `tweetButton`). If extraction returns 0 tweets or posting fails at a step, snapshot the page and find the new hooks.
- **Not logged in**: extract returns 0 tweets or a login wall — tell the user to log into X in the browser.
- **Rate limits / spam flags**: don't run this more than a few times a day; don't post more than 2-3 quote tweets per run.
