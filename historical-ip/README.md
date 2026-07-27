# Aagman Historical Storytelling IP

> Deep historical essays on markets, assets, and economic manias — one story per week.

---

## What this IP is

A separate content layer under Aagman that produces long-form historical storytelling: deep essays on a single period, asset, or event, with an educational spine. It shares Layer 2's voice but is not news-driven. The stories are chosen for their structural lessons and their narrative power.

**Target reader:** The same self-taught intermediate to semi-pro Indian trader as Layer 2, but here the frame is "what the past teaches about how markets break and recover."

**Surfaces:**
- Long-form Substack essay (primary)
- X thread
- LinkedIn carousel (promotional)
- Instagram carousel (promotional)
- Infographic concepts

**Voice:** Financial Times leader column meets Matt Levine — dry, confident, structurally argued, lightly literary. Accessible without being simplistic. Educational without being a lecture.

**Cadence:** One deep essay per week.

---

## The core idea: one story, many surfaces

A historical story idea is proposed, researched once into a canonical artifact, then fanned out into multiple format-specific pieces. A single **historical reviewer** checks every output from a story before anything reaches the operator.

```
SIGNAL GENERATOR
         │
         ↓
  3 story ideas surfaced to operator
         │
         ↓
OPERATOR PICKS ONE
         │
         ↓
RESEARCH AGENT
  produces one canonical research artifact
         │
         ↓
BLOG WRITER
  produces first draft
         │
         ↓
FACT-CHECKER
  verifies claims, suggests fixes
         │
         ↓
BLOG WRITER (revision mode)
  applies fixes
         │
         ↓
   ┌─────┴─────┬─────────┬──────────────┐
   ↓           ↓         ↓              ↓
HISTORICAL  CAROUSEL  THREAD WRITER  INFOGRAPHIC
REVIEWER    WRITER                    IDEATOR
   │           │         │              │
   └─────┬─────┴─────────┴──────────────┘
         ↓
WRITERS CORRECT IN PARALLEL
         ↓
OPERATOR FINAL APPROVAL
         ↓
PUBLISH / SCHEDULE
```

---

## Directory structure

```
historical-ip/
├── README.md                  # this file
├── system_brief.md            # full system architecture handoff
├── prompts/                   # agent prompts
│   ├── signal_generator.md
│   ├── research_agent.md
│   ├── blog_writer.md
│   ├── fact_checker.md
│   ├── historical_reviewer.md
│   ├── thread_writer.md
│   ├── carousel_writer_promo.md
│   ├── infographic_ideator.md
│   └── social_distribution.md
├── voice/                     # single voice guide for all writing
│   └── historical_voice_base.md
├── signals/                   # story idea digests
├── research/                  # canonical research artifacts
├── drafts/                    # work-in-progress outputs
├── final/                     # operator-approved outputs
├── reviews/                   # reviewer reports
├── social/                    # social distribution copy (LinkedIn teasers)
└── state/
    ├── covered_topics.json    # memory of stories already published
    ├── signal_log.md          # every signal, status, surfaces produced
    ├── publish_calendar.md    # scheduled publishes
    └── tickets/               # operator format-decision tickets
```

---

## File naming conventions

| Artifact | Path |
|---|---|
| Story digest | `signals/{YYYY-MM-DD}-digest.md` |
| Operator ticket | `state/tickets/{YYYY-MM-DD}-{story-id}.md` |
| Research artifact | `research/story-{story-id}.md` |
| Blog draft | `drafts/story-{story-id}-blog.md` |
| Blog fact-check | `reviews/story-{story-id}-fact-check.md` |
| Thread draft | `drafts/story-{story-id}-thread.md` |
| LinkedIn carousel | `drafts/story-{story-id}-carousel-linkedin.md` |
| Instagram carousel | `drafts/story-{story-id}-carousel-instagram.md` |
| Infographic concepts | `drafts/story-{story-id}-infographic-concepts.md` |
| Historical review | `reviews/story-{story-id}-historical-review.md` |
| Social teaser | `social/story-{story-id}-linkedin.md` |

---

## Operational model

### Automation depth: full gates

The operator approves at every checkpoint:

1. Signal generator output (story ideas)
2. Research artifact completion
3. Blog first draft
4. Fact-check report
5. Revised blog draft
6. Each writer output (thread, carousel, infographic)
7. Historical reviewer output
8. Social teaser
9. Final approval of all surfaces together

### Cadence: weekly

One deep essay per week. Story selection happens at the start of the week; research and drafting mid-week; review and approval before the weekend.

### Trigger style: explicit chat trigger

The agent does not auto-advance. The operator says "proceed" or equivalent after each approval.

### Approval surface: this chat

Outputs are shown here; the operator approves, requests changes, or rejects inline.

---

## Research standard

Before citing any source, the research agent reads the full source. Every claim needs a URL. Disputed facts are presented as disputes.

The artifact has nine mandatory sections:

1. Story in one line
2. Why it matters now
3. Primer / definitions
4. Timeline
5. Key numbers table
6. Cast of characters
7. Educational spine
8. Proposed structure
9. Source list

---

## Content rules

- No price targets or buy/sell recommendations.
- No investment advice.
- No urgency words, emojis, or engagement bait.
- Every surface must end with an open cognitive tension, not a conclusion.
- Historical claims must be sourced; legends and folklore must be labeled as such.
- Explain terms and context that a modern reader may not know.

---

## Covered-topic memory

`state/covered_topics.json` stores every story that has been published or approved. The signal generator reads this file before proposing new ideas so we do not repeat topics.

---

## Status

| Story | Surfaces | Status |
|---|---|---|
| assignat-revolutionary-france | Blog, thread, carousel, infographic | Tested, approved conceptually |
| japanese-asset-bubble-1985-1990 | Blog, thread, carousel, infographic | Tested, approved conceptually |

---

## Repository

This lives inside `kotilabs/aagman-content-layer2` as `historical-ip/`.
