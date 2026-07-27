# Aagman Historical Storytelling IP — System Architecture

> This file is a handoff brief. The operator gives this to a setup agent. The setup agent reads the full document, confirms understanding, then drafts or wires in the prompts below.

---

## What this IP is

A separate content layer under Aagman that produces deep historical essays on markets, assets, manias, crashes, and structural economic events. It is not news-driven. Each piece is a long-form essay with an educational spine, fanned out into X threads, LinkedIn/Instagram carousels, and infographic concepts.

The target reader is the self-taught intermediate to semi-pro Indian trader: someone who follows macros, respects drawdowns, and wants context that is rigorous but not academic.

---

## Architectural principle

One story is researched once into a canonical artifact, then expressed across many surfaces. One reviewer — the historical reviewer — sees every output from a story before the operator does. This prevents compression-distortion: a nuanced historical claim becoming a wrong carousel slide.

---

## End-to-end flow per story

```
SIGNAL GENERATOR
         │
         ↓
  3 story ideas surfaced to operator
         │
         ↓
OPERATOR PICKS ONE + DECIDES SURFACES
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
  verifies claims, flags errors and fixes
         │
         ↓
BLOG WRITER (revision mode)
  applies fixes
         │
         ↓
   ┌─────┴─────┬─────────┬──────────────┐
   ↓           ↓         ↓              ↓
HISTORICAL  CAROUSEL   THREAD       INFOGRAPHIC
REVIEWER    WRITER     WRITER       IDEATOR
   │           │         │              │
   └─────┬─────┴─────────┴──────────────┘
         ↓
WRITERS CORRECT IN PARALLEL
         ↓
SOCIAL DISTRIBUTION AGENT
  writes LinkedIn/Substack teaser from approved blog
         ↓
OPERATOR FINAL APPROVAL
         ↓
PUBLISH / SCHEDULE
```

---

## The agents

### 1. Signal generator

**Role.** Proposes 3 historical story ideas per week. Each idea includes period, asset, one-line hook, why it matters now, educational angle, and suggested surfaces.

**Inputs.** `state/covered_topics.json` (must not repeat), web access.

**Outputs.** `signals/{YYYY-MM-DD}-digest.md`.

**Prompt source.** `prompts/signal_generator.md`.

### 2. Operator pick

**Role.** Human gate. Operator selects one idea and decides surfaces.

**Output.** `state/tickets/{YYYY-MM-DD}-{story-id}.md`.

### 3. Research agent

**Role.** Deep dive into the selected story. Produces one canonical research artifact every downstream writer consumes. Goes to primary sources where possible.

**Inputs.** Ticket + raw sources.

**Outputs.** `research/story-{story-id}.md`.

**Prompt source.** `prompts/research_agent.md`.

### 4. Blog writer

**Role.** Writes the long-form essay from the research artifact.

**Inputs.** Research artifact + voice guides.

**Outputs.** `drafts/story-{story-id}-blog.md`.

**Prompt source.** `prompts/blog_writer.md`.

### 5. Fact-checker

**Role.** Verifies every dated claim, number, quote, and attribution in the blog draft. Suggests fixes and flags unverified claims.

**Inputs.** Blog draft + research artifact.

**Outputs.** `reviews/story-{story-id}-fact-check.md`.

**Prompt source.** `prompts/fact_checker.md`.

### 6. Blog writer — revision mode

**Role.** Applies fact-check fixes and produces revised blog draft.

**Outputs.** Updated `drafts/story-{story-id}-blog.md`.

### 7. Historical reviewer

**Role.** The universal gate. Reviews all surfaces from one story together: factual integrity, reasoning quality, educational clarity, cross-surface consistency, and format-specific standards.

**Outputs.** `reviews/story-{story-id}-historical-review.md`.

**Prompt source.** `prompts/historical_reviewer.md`.

### 8. Thread writer

**Role.** Writes the X thread from the research artifact.

**Outputs.** `drafts/story-{story-id}-thread.md`.

**Prompt source.** `prompts/thread_writer.md`.

### 9. Carousel writer

**Role.** Writes promotional carousel copy for LinkedIn and Instagram from the approved blog draft.

**Outputs.** `drafts/story-{story-id}-carousel-linkedin.md`, `drafts/story-{story-id}-carousel-instagram.md`.

**Prompt source.** `prompts/carousel_writer_promo.md`.

### 10. Infographic ideator

**Role.** Surfaces data-driven infographic concepts from the research artifact.

**Outputs.** `drafts/story-{story-id}-infographic-concepts.md`.

**Prompt source.** `prompts/infographic_ideator.md`.

### 11. Social distribution agent

**Role.** Writes a 100–120 word LinkedIn/Substack teaser from the approved blog.

**Outputs.** `social/story-{story-id}-linkedin.md`.

**Prompt source.** `prompts/social_distribution.md`.

### 12. Writers correct in parallel

**Role.** Each writer applies reviewer feedback to its own surface.

### 13. Operator approval

**Role.** Human gate. Operator sees all surfaces together and approves, rejects, or requests changes.

### 14. Publish

**Role.** Approved pieces move to `final/` and are published or scheduled per `state/publish_calendar.md`.

---

## Voice guide

- `voice/historical_voice_base.md` — the single voice guide for all writing. Contains core identity, tone discipline, and per-surface rules for Substack, X threads, carousels, and social teasers.

---

## Hard rules

- **One story, one research artifact, many surfaces.** Never re-research per surface.
- **Cross-surface consistency is mandatory.** The reviewer enforces this.
- **No fabrication.** Every number, quote, or claim traces to the research artifact or a verifiable source.
- **The operator sees all surfaces from one story together at approval.**
- **No investment advice.** No price targets, no buy/sell recommendations.
- **Historical claims must be sourced.** Legends must be labeled as legends.

---

## Setup agent checklist

1. Read this brief and confirm understanding to the operator.
2. Create directory structure.
3. Draft or wire in all prompts and voice guides.
4. Seed `state/covered_topics.json` with already-covered stories.
5. Create empty `state/signal_log.md`, `state/publish_calendar.md`, `state/operational_config.md`.
6. Run one end-to-end test story with the operator watching.
7. Only after the test passes is the system live.

---

## What the setup agent should NOT do

- Do not invent prompts the operator says they already have.
- Do not start processing stories before all prompts are gathered and the test story passes.
- Do not skip operator iteration on any drafted prompt.
- Do not commit to GitHub without explicit operator permission.
