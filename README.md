# Aagman Content Layer 2

> Signal-driven macro, markets, commodities and cross-asset relationship content across Substack, X, LinkedIn, Instagram and infographics.

---

## What this layer is

Layer 2 is Aagman’s **relationship content layer**. It sits alongside Layer 1 (query-driven SEO/AEO blogs) and produces event-shaped commentary that explains *what is happening in markets and why it matters*.

The target reader is the self-taught intermediate to semi-pro Indian trader: someone who follows macros, watches FII/DII flows, trades derivatives, and wants context that is rigorous but not academic.

**Surfaces:**
- Long-form Substack essays
- X threads
- LinkedIn carousels (promotional and standalone)
- Instagram carousels (promotional and standalone)
- Infographic concepts

**Voice:** Financial Times leader column meets Matt Levine — dry, confident, structurally argued, lightly literary. No urgency, no advice, no performative certainty.

---

## The core idea: one signal, many surfaces

A market or macro signal is identified, deeply researched once into a canonical artifact, then fanned out into multiple format-specific pieces that all draw from the same research. A single **markets reviewer** checks every output from a signal before anything reaches the operator.

This prevents the compression-distortion problem: a nuanced blog claim becoming a wrong carousel claim.

```
SIGNAL IDENTIFIER (macro + realtime lenses)
         │
         ↓
  signal digest surfaced to operator
         │
         ↓
OPERATOR PICKS SIGNAL + FORMATS
         │
         ↓
RESEARCH AGENT
  produces one canonical research artifact
         │
         ↓
   ┌─────┴─────┬─────────┬──────────────┐
   ↓           ↓         ↓              ↓
BLOG WRITER  CAROUSEL  THREAD WRITER  INFOGRAPHIC
             WRITER                    IDEATOR
             (promo /
              standalone)
   │           │         │              │
   └─────┬─────┴─────────┴──────────────┘
         ↓
MARKETS REVIEWER
  reviews ALL outputs from this signal together
         ↓
CORRECTION AGENT
  applies review feedback
         ↓
SEO/AEO AUDIT (blog only)
         ↓
OPERATOR FINAL APPROVAL
         ↓
PUBLISH / SCHEDULE
```

---

## Directory structure

```
.
├── drafts/                    # work-in-progress outputs
├── final/                     # operator-approved outputs ready for publish
├── prompts/                   # agent prompts
│   ├── signal_identifier_macro.md
│   ├── signal_identifier_realtime.md
│   ├── research_agent.md
│   ├── blog_writer.md
│   ├── carousel_writer_promo.md
│   ├── carousel_writer_standalone.md
│   ├── thread_writer.md
│   ├── infographic_ideator.md
│   ├── markets_reviewer.md
│   └── seo_aeo_audit.md
├── research/                  # canonical research artifacts per signal
├── reviews/                   # markets reviewer reports + SEO/AEO audits
├── signals/                   # daily signal digests
├── state/                     # operational config, tickets, logs, calendar
│   ├── operational_config.md
│   ├── signal_log.md
│   ├── publish_calendar.md
│   └── tickets/
├── voice/                     # voice guides and per-surface overlays
│   ├── layer2_voice_base.md
│   ├── substack_overlay.md
│   ├── carousel_overlay.md
│   └── thread_overlay.md
├── system_brief.md            # full system architecture handoff doc
└── README.md                  # this file
```

---

## File naming conventions

| Artifact | Path |
|---|---|
| Signal digest | `signals/{YYYY-MM-DD}-digest.md` |
| Operator ticket | `state/tickets/{YYYY-MM-DD}-{signal-id}.md` |
| Research artifact | `research/signal-{signal-id}.md` |
| Blog draft | `drafts/signal-{signal-id}-blog.md` |
| Thread draft | `drafts/signal-{signal-id}-thread.md` |
| LinkedIn carousel | `drafts/signal-{signal-id}-carousel-linkedin.md` |
| Instagram carousel | `drafts/signal-{signal-id}-carousel-instagram.md` |
| Infographic concepts | `drafts/signal-{signal-id}-infographic-concepts.md` |
| Markets review | `reviews/{signal-id}-markets-review.md` |
| SEO/AEO audit | `reviews/{signal-id}-seo-aeo-audit.md` |

---

## Operational model

### Automation depth: full gates

The operator approves at every checkpoint:

1. Signal identifier output (macro + realtime digests)
2. Research artifact completion
3. Each writer output (blog, carousels, thread, infographic)
4. Markets reviewer output
5. SEO/AEO audit output (blog only)
6. Final approval of all surfaces together

### Cadence: signal-driven

No fixed weekly quota. Editorial quality and signal strength determine output, not schedule pressure.

### Trigger style: explicit chat trigger

The agent does not auto-advance. The operator says "run next" or equivalent after each approval.

### Approval surface: this chat

Outputs are shown here; the operator approves, requests changes, or rejects inline.

---

## How to run a signal end-to-end

### 1. Generate the signal digest

Run the macro and/or realtime signal identifiers. Both lenses are surfaced in one digest file:

```
signals/{YYYY-MM-DD}-digest.md
```

### 2. Pick a signal and create a ticket

The operator selects a signal and decides which surfaces to produce. A ticket is written to:

```
state/tickets/{YYYY-MM-DD}-{signal-id}.md
```

Example ticket fields:
- Signal ID
- Publication date
- Surfaces to produce (blog, thread, LinkedIn, Instagram, infographic)
- Source pointers
- Operator notes

### 3. Research the signal

The research agent reads the ticket and source pointers, researches deeply, and writes:

```
research/signal-{signal-id}.md
```

Hard rule: every claim needs a source; read the full source before citing it.

### 4. Produce surfaces in parallel

Writers consume the same research artifact and produce their respective drafts. For signals with a blog, carousels use the **promotional** prompt and tease the essay. For signals without a blog, carousels use the **standalone** prompt and tell the full story.

### 5. Markets review

The markets reviewer reads the research artifact and all produced surfaces, then writes a single review:

```
reviews/{signal-id}-markets-review.md
```

Issues are tagged `[BLOCKER]`, `[MAJOR]`, `[MINOR]`, or `[FYI]`.

### 6. Corrections

The correction agent applies the review feedback and updates the drafts in place.

### 7. SEO/AEO audit (blog only)

For Substack essays, an SEO/AEO audit checks title, meta description, H2 structure, snippet fit, internal-link opportunities and schema markup.

### 8. Operator final approval

The operator reviews all final outputs. Approved pieces are moved from `drafts/` to `final/`.

### 9. Publish / schedule

Final content is published or scheduled according to `state/publish_calendar.md`.

---

## Research standard

Layer 2’s editorial integrity rests on the research artifact. Before citing any source, the research agent reads the full source — not the headline or snippet. Every claim needs a URL. Disputed facts are presented as disputes, not forced resolutions.

The artifact has ten mandatory sections:

1. Signal restatement
2. Verified facts
3. Key data table
4. Mechanism
5. Competing interpretations
6. Cross-asset implications
7. Historical analogues
8. Known, unknown, and unknowable
9. Open questions
10. Source list

---

## Content rules

- No price targets or buy/sell recommendations.
- No investment advice.
- No urgency words, emojis, or engagement bait.
- Every surface must end with an open cognitive tension, not a conclusion.
- Carousels lead with concrete data, then abstract mechanism.
- Threads have a strong hook, body beats, pivot thesis, and open end.
- Infographics drop weak data; visual ideas must rest on verified numbers.

---

## Status of first batch

| Signal | Surfaces | Status |
|---|---|---|
| central-bank-divergence | Blog, thread, LinkedIn carousel, Instagram carousel, infographic concepts | Reviewed, corrected, in `drafts/` |
| dii-wall-fii-exodus | Infographic concepts | Reviewed, corrected, in `final/` |
| china-slower-growth | LinkedIn standalone carousel, Instagram standalone carousel | Reviewed, corrected, in `drafts/` |

---

## Contributing

This repo is operated by Aagman’s content agent loop. Direct edits are welcome, but agent-run prompts and file conventions should be updated in `prompts/` and `state/operational_config.md` so the loop stays consistent.

---

## Repository

`kotilabs/aagman-content-layer2`
