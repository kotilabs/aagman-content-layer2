# PPC Playbook — Practitioner Knowledge for the Strategist

Distilled from Google Ads official mechanics and practitioner sources (PPC Mastery /
The PPC Edge, Lunio, Digital Dawn India, JumpFly, PPC audits). This is institutional
knowledge: read it before planning ANY campaign. Do not re-derive it.

---

## 1. Platform mechanics (how Google Ads actually works)

### Keywords vs. search terms vs. search themes
- **Keywords** are what you bid on in Search campaigns, with match types (exact, phrase, broad).
- **Search terms** are what people actually typed. The search terms report is the only
  ground truth — review it weekly (every 72 hours in the first weeks).
- **Search themes** exist ONLY in Performance Max. They are broad intent signals
  (3–5 word phrases), up to 50 per asset group, that guide Google's AI. Google can
  ignore them. They are NOT keywords and do not restrict matching.

### PMax internal matching hierarchy (cannibalization)
- Exact match keywords in Search campaigns beat everything.
- PMax search themes have the SAME auction priority as phrase/broad match keywords
  in Search campaigns — so PMax routinely cannibalizes Search traffic when both run.
  Ad Rank is the tie-breaker.
- PMax over-inflates itself with brand conversions. ALWAYS add Brand Exclusions to
  PMax, and catch brand traffic in a separate branded Search campaign.
- Audience signals in PMax are hints, not targeting. Google WILL go beyond them.
  Do not layer 15 signals hoping for control; 3–5 strong ones (customer list,
  site visitors, intent segments) is enough.
- PMax negatives: self-serve campaign-level negatives are rolling out; otherwise use
  the Performance Max Campaign Modification Request Form via Google support.
- Use a spend-allocation script (Mike Rhodes) to see PMax channel split — the UI hides it.

### Match types in 2025+
- Exact is no longer exact (close variants). Phrase is mostly redundant — use
  exact + broad with strong negatives, or exact + phrase on small budgets.
- Broad match without conversion data burns budget. On a new account: start
  exact + phrase, manual CPC, then move to Maximize Conversions after 15–30
  conversions, then Target CPA (set 10–20% above observed CPA).
- Smart bidding needs ~30–50 conversions/month to work. Below that, stay manual.

### Learning & pacing
- Learning phase: 7–14 days. Do not touch bids/budget/assets during it.
- Budget or bid changes: max once per 7–14 days, in 20–30% increments.
- Daily budget should be 2–3× target CPA, or the campaign stays "limited" forever.

### Tracking (the #1 skipped step)
- Never optimize for form submissions — Google learns to find form-fillers, not buyers.
- Capture GCLID in a hidden form field. Store with the lead.
- Two conversion actions: "Form Submit" (secondary) and "Qualified/Verified Lead"
  (primary, optimized for). Upload offline conversions weekly.
- Without offline conversion tracking, lead-gen campaigns optimize blind.

---

## 2. Campaign setup hygiene (the silent budget killers)

- New Search campaigns DEFAULT to Search + Display Network. Turn Display OFF.
- Also default: Search Partners on, "Presence or interest" geo-targeting. Set
  "Presence" only unless you want tourists.
- Negative keywords go in WEEK ONE, not after waste shows: tips/calls/telegram,
  jobs/careers/salary, course/training/certification, free download/apk/crack,
  how-to informational (unless deliberate).
- Granular ad groups (STAGs): one intent theme per ad group, 5–10 keywords max.
- Never put a competitor's trademark in ad TEXT. Bidding on their brand terms is
  allowed; writing their name in the headline invites disapproval.
- Use Ad Preview to check ads. Never click your own ads. Exclude internal IPs.
- Ad extensions are free CTR: sitelinks, callouts, structured snippets. Use them all.

---

## 3. Keyword & demand planning (where most strategies fail)

- Keywords are decided from DEMAND DATA, not product language. Process:
  seed list → Keyword Planner expansion → volume/CPC overlay → intent
  classification → cluster → launch → validate in search terms report.
- Kill anything under ~50 monthly searches for a short test — no learning value.
- Watch for vendor-speak: nobody searches your internal feature names
  ("4 leg options", "multi-leg execution"). Searchers use their own words
  (strategy names, tool names, broker names, "free X", "best X india").
- Localization: searchers rarely append their country. Geo-targeting handles
  location. Real localization signals are instrument/market terms
  (NSE, NIFTY, BANKNIFTY, F&O) — or broker names.
- Broker-anchored searches are a real pattern in India ("algo trading zerodha").
- An angle with zero search volume is NOT a search angle — it is an education
  play. Say so explicitly and route it to video/display/landing content instead
  of pretending keywords exist for it.
- "Free" as an intent modifier is high-volume in India ("free stock screener",
  "free backtest software"). Match it in copy ONLY when the keyword contains it —
  message match, not a pricing pitch.
- Bare generic terms with huge volume ("screener", 5M/mo) are usually navigational
  for an incumbent brand. Exclude or treat as a separate conquesting test.

---

## 4. Copy craft (learned from real campaign iterations)

- Message match: headlines must contain the query words. It drives Quality Score
  AND tells the searcher they're in the right place.
- Quality over quantity: 10 strong headlines beat 15 padded ones.
- NEVER negative-only framings ("Not a bot. Not a tip service.") — a searcher with
  no context can't tell what the product IS. State the positive. Counter-positioning
  belongs on the landing page, not in a 30-char headline.
- NEVER insider vocabulary the searcher doesn't think in ("formula syntax",
  "multi-leg", "4-leg", acronyms). Plain-language version always.
- Trust fragments are not headlines ("SEBI-Registered IA", "NSE-Empanelled").
  Trust belongs in descriptions and on the landing page.
- Don't hardcode CTAs or mandate specific phrases in briefs — give the writer
  negative constraints and let it find the language.
- Pre-qualify with copy where clicks are expensive: pricing, audience qualifiers.

---

## 5. India-specific realities

- 60%+ traffic is mobile. Landing page must load <3s on mid-range Android/4G.
- WhatsApp is the follow-up channel — double opt-in via WhatsApp beats email.
- F&O traders are most active 9:00–11:30 and 13:30–15:30 IST — consider ad scheduling.
- Financial/trading ads trigger extra policy review: no return promises, no
  "guaranteed profits", no fear stats ("91% of traders lose"), no urgency bait.
- EMI/free/no-card framing outperforms discount framing for tools in beta.

---

## 6. Small-budget sequencing (₹50K–₹1L total tests)

- Week 1–2: Search only, exact + phrase, manual CPC. Learn which keyword clusters
  and angles produce verified conversions.
- Week 3–4: switch Search to Maximize Conversions; start offline conversion uploads;
  add Display REMARKETING only (site visitors who didn't convert) — never cold
  Display on a small budget.
- Week 3+: PMax only after 30–50 conversions exist, with brand exclusions and
  5–10 search themes per asset group. Sequential with Search, not parallel, on
  small budgets — parallel muddies attribution and lets PMax cannibalize Search.
- One variable per test. Kill fast: any cell with >₹3,000–5,000 spend and zero
  verified conversions gets paused.

---

## Sources

- PPC Mastery / The PPC Edge #118, #92, #108 (PMax mechanics, cannibalization, brand inflation)
- Lunio: Performance Max Search Themes guide (prioritization, reporting limits)
- JumpFly: Keywords vs. Search Terms vs. Search Themes
- Digital Dawn: Performance Max Lead Generation Guide for India (offline conversions,
  GCLID, budget minimums, WhatsApp follow-up)
- Google Ads Help: About Performance Max, search themes, match types
- Beyondgoat / Sarah Stemen: "limited by budget" diagnosis, reverse-budget formula
- In-house iterations: Aagman v8/v9 copy reviews (vendor-speak, negative framings,
  insider vocabulary, keyword planner overlay)
