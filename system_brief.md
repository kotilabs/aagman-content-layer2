# Aagman Content Layer 2 — System Architecture

> This file is a handoff brief. The operator gives this to a setup agent. The setup agent reads the full document, then works through the "What to ask the operator for" section step by step, collects each prompt or input the operator already has, drafts the ones the operator doesn't have, and wires the whole system together. Do not invent prompts the operator says they already have. Ask, receive, wire in.

---

## What this layer is

A second content layer alongside the existing SEO/AEO machine (Layer 1). Layer 2 is the relationship layer: long-form Substack essays, Instagram and LinkedIn carousels, X threads, and infographic concepts that engage Aagman's ICP — self-taught intermediate to semi-pro Indian traders — around live market signals, macro events, commodities moves, geopolitical developments, and cross-asset narratives.

The content is event-shaped, not query-shaped. It answers "what's happening and what does it mean," not "how do I trade X." Distribution surfaces: Substack newsletter, Substack posts, LinkedIn carousels, Instagram carousels, X threads, and infographics.

---

## The architectural principle

One signal expresses across many surfaces. A market or macro signal is identified, deeply researched once into a canonical artifact, then fanned out into multiple format-specific pieces that all draw from the same research. One reviewer agent — the markets reviewer — sees every output from a given signal before any of it reaches the operator. This is what keeps claims consistent across surfaces and prevents the compression-distortion problem where a nuanced blog claim becomes a wrong carousel claim.

---

## End-to-end flow per signal

```
SIGNAL IDENTIFIER (two modes, run daily)
         │
         ↓
  signal digest surfaced to operator
         │
         ↓
OPERATOR PICKS SIGNAL + DECIDES FORMATS
  (blog? carousel? thread? infographic? combinations?)
         │
         ↓
RESEARCH AGENT
  produces one canonical research artifact per chosen signal
         │
         ↓
   ┌─────┴─────┬─────────┬──────────────┐
   ↓           ↓         ↓              ↓
BLOG WRITER  CAROUSEL  THREAD WRITER  INFOGRAPHIC
             WRITER                    IDEATOR
             (2 modes:
              promo /
              standalone)
   │           │         │              │
   └─────┬─────┴─────────┴──────────────┘
         ↓
MARKETS REVIEWER
  reviews ALL outputs from this signal together,
  cross-surface consistency + per-surface depth checks
         │
         ↓
WRITERS CORRECT IN PARALLEL
         │
         ↓
SEO/AEO AUDIT (blog only)
         │
         ↓
BLOG WRITER FINAL CORRECTIONS
         │
         ↓
OPERATOR APPROVAL (sees all surfaces together)
         │
         ↓
PUBLISH TO RESPECTIVE SURFACES
```

---

## The agents

For each agent: role, inputs, outputs, prompt source. "Prompt source" tells the setup agent whether to ask the operator for an existing prompt, or to draft one and iterate with the operator.

### 1. Signal identifier — two distinct lenses

**Role.** Hunts for content-worthy signals across markets and macro. Two lenses, kept distinct because they operate on different time horizons.

- **Lens 1 — Macro/structural.** Broad, slower-moving editorial topics: central bank regimes, geopolitical shifts, commodity supercycles, AI × capital × labor, long-cycle structural changes. The "what is the world doing to the market" feed.
- **Lens 2 — Real-time signals.** Recent, live-market developments: options flow, OI buildup, FII/DII activity, sector rotation, vol regime shifts, technical setups, breaking regulatory or corporate news. The "what is the market telling us right now" feed.

**Inputs.** Live web/news access, market data sources where available.

**Outputs.** A structured digest of signals per lens. Each signal includes: one-line description, why it matters now, suggested content angle, raw sources for downstream research.

**Cadence.** Macro lens runs weekly; real-time lens runs daily. Both surface to the operator.

**Prompt source.** **Operator has both prompts.** Ask for them. Wire in as-is.

### 2. Operator format-decision step

**Role.** Human gate. Operator reviews the daily signal digest, picks signals to act on, decides which surfaces each signal expresses on.

**Output.** A per-signal ticket: `Signal {id} → produce: [blog | carousel-promo | carousel-standalone | thread | infographic]`. The ticket triggers downstream agents.

**Prompt source.** None. Human decision in the UI.

### 3. Research agent

**Role.** Deep dive into the selected signal. Produces one canonical research artifact every downstream writer consumes. Internet access. Goes to primary sources where possible (RBI minutes, SEBI circulars, company filings, central bank statements, exchange data, official commodity reports).

**Inputs.** The signal record + its raw sources from the identifier.

**Outputs.** Structured research artifact at `research/signal-{id}.md`. Contents: the full picture, sourced facts, key data points in tables, competing interpretations, historical analogues where relevant, cross-asset implications, sources list. Structured enough that downstream writers don't have to re-interpret it.

**Prompt source.** Ask operator if they have one. If not, setup agent drafts based on the role spec above; iterate with operator until approved.

### 4. Blog writer (long-form Substack)

**Role.** Writes the long-form essay from the research artifact.

**Inputs.** Research artifact + Layer 2 voice guide, Substack overlay.

**Outputs.** First draft at `drafts/signal-{id}-blog.md`.

**Prompt source.** **Operator has it.** Ask, receive, wire in.

### 5. Carousel writer (two modes)

**Role.** Writes carousel copy for LinkedIn and Instagram. One agent, switchable between two modes:

- **Mode 1 — promo carousel.** Takes research + blog draft, pulls 6–8 most arresting points or the strongest narrative arc, designs as a teaser. Last slide is always "read the full take on Substack" with the link.
- **Mode 2 — standalone carousel.** Takes the research artifact directly, produces a complete piece in 8–12 slides. The whole argument fits in the carousel.

**Inputs.** Research artifact, optionally the blog draft (for promo mode), Layer 2 voice guide carousel overlay, platform spec (LinkedIn vs Instagram tweaks).

**Outputs.** Slide-by-slide copy at `drafts/signal-{id}-carousel-{platform}.md`. Per slide: headline, body copy, any data callout, and a design note (what the visual should show — chart, quote, number, comparison). Design notes go to the designer downstream.

**Prompt source.** Ask operator if one exists. If not, setup agent drafts; iterate.

### 6. Thread writer (X)

**Role.** Writes the X thread from the research artifact. Usually 8–15 posts, each standalone-readable, with a strong opener and a payoff.

**Inputs.** Research artifact + Layer 2 voice guide thread overlay.

**Outputs.** Post-by-post thread copy at `drafts/signal-{id}-thread.md`.

**Prompt source.** Ask operator. If none, setup agent drafts; iterate.

### 7. Infographic ideator

**Role.** Surfaces concepts, not finished copy. Takes the research artifact and outputs the most interesting numbers/data points + 3–5 specific infographic concepts.

**Inputs.** Research artifact.

**Outputs.** Concepts file at `drafts/signal-{id}-infographic-concepts.md` listing: the most interesting numbers from the research with the story each tells; 3–5 infographic concepts (central insight, data to include, visualization type — timeline, comparison, ratio, geography, etc., rough composition notes); source attribution for every number.

**Prompt source.** Ask operator. If none, setup agent drafts; iterate.

### 8. Markets reviewer — the universal gate

**Role.** The single reviewer for every output across every surface for a given signal. Has the working breadth of a senior macro analyst or sell-side desk strategist: monetary policy, commodities, geopolitics, equity and derivatives markets, FX and rates, market microstructure, and the cross-asset linkages between them. Skeptical by default, especially on consensus-aligned claims. Internet access for independent verification and gap research.

**What it reviews, per signal.** All format outputs together in one pass (blog + every carousel + thread + infographic concepts). Five passes:

1. **Factual integrity.** Every checkable claim — verify against research artifact and against current external sources where the claim is time-sensitive.
2. **Reasoning quality across domains.** Monetary policy interpretation, commodity supply/demand framing, geopolitical transmission to markets, cross-asset linkage validity, market-structure claims.
3. **Independent gap analysis.** From its own research: counterarguments the piece doesn't engage, cross-asset signals contradicting the thesis, missing historical analogues, missing asymmetries. Discipline: only suggest what strengthens the piece for its surface and intent; never pad.
4. **Cross-surface consistency.** Do all outputs claim the same thing about the world? Stylistic difference is fine; argumentative difference is a flag. A claim true with context (blog) becoming false without context (carousel slide) is a flag. A thread post that fails the standalone-screenshot test is a flag.
5. **Format-specific severity weighting.** Blog: nuance and depth held to highest standard. Carousel: compression-distortion lens. Thread: standalone-post lens. Infographic: claim-vs-data alignment lens.

**Output.** Single structured review file at `reviews/signal-{id}/markets-review.md`. Sections: cross-surface consistency issues, then per-surface feedback (blog / carousel / thread / infographic). Each issue has location, issue, severity (blocker / should-fix / optional), and the specific fix. Verdict line at end: "Corrections required, X blockers across N surfaces" or "Clean — ready for SEO audit / human approval."

**Posture rule built into the prompt.** Be skeptical by default. The most valuable move is sometimes "this is the consensus take, here's what the consensus is missing." Lazy-consensus content is the most common failure mode in macro/markets writing.

**Prompt source.** **Setup agent drafts this prompt.** New role specific to Layer 2. Iterate with operator until approved. If the operator shares the Layer 1 reviewer prompt as a structural reference, use it for the output schema only — the substance is different.

### 9. Writers correct in parallel

**Role.** Each writer reads its own section of the markets review plus the cross-surface section, and applies corrections. Blockers must be fixed. Should-fix items addressed unless the writer has a defended reason not to. Optional suggestions used at writer's discretion, subject to surface word/slide/post limits.

**Outputs.** Corrected drafts overwriting the previous draft files, plus an updated `research/signal-{id}.md` if the reviewer surfaced new sources worth keeping.

**Prompt source.** No new prompt needed — this is the same writer agents from steps 4–7 running in "correction mode," which is a section the setup agent adds to each writer's base prompt. Ask operator to confirm the wording for the correction-mode instruction once drafted.

### 10. SEO/AEO audit (blog only)

**Role.** Runs the operator's existing SEO/AEO audit over the corrected blog draft. Carousels, threads, and infographics skip this step — they don't compete in search/answer engines, so the audit would produce noise.

**Inputs.** Corrected blog draft.

**Outputs.** Audit report attached to the blog file.

**Prompt source.** **Operator has it.** Ask, receive, wire in.

### 11. Blog writer final corrections

**Role.** Blog writer applies SEO/AEO fixes. Final blog saved to `final/signal-{id}-blog.md`.

**Prompt source.** Reuses the blog writer prompt with a final-pass instruction. Setup agent adds this instruction; operator approves wording.

### 12. Operator approval

**Role.** Operator sees all surfaces from this signal together at one gate, with the markets reviewer's cross-surface notes visible alongside. Approves, requests changes, or rejects per surface.

**Output.** Approved files moved to `final/` per surface; rejected ones routed back to the relevant writer with operator notes.

**Prompt source.** None. UI surface.

### 13. Publish

**Role.** Approved pieces publish to their respective surfaces. Substack, LinkedIn, Instagram (designer hands carousel copy + design notes to whoever builds the visual asset), X, and infographic concepts handed to the designer.

**Prompt source.** None. Operational step; may be automated per-surface where the platform allows, or manual.

---

## Voice guides for Layer 2

The Layer 1 voice guide (patient teacher) is not the right fit for Layer 2 (thoughtful market participant writing for peers). The setup agent needs to assemble:

- **Layer 2 base voice guide** — the underlying tone and principles for all Layer 2 content (skeptical, sharp, well-sourced, willing to take a view).
- **Substack overlay** — long-form essay rhythm, room for nuance, willing to argue a thesis.
- **Carousel overlay** — one doc covering both LinkedIn and Instagram with platform deltas. Tight, scannable, headline-driven.
- **Thread overlay** — short sentences, one idea per post, standalone-readable, strong opener and payoff.

**Prompt source for each.** Ask operator if any of these exist. If not, setup agent drafts; iterate with operator. The Layer 1 voice guide and the covered-call reference article can be shared by the operator as structural references for *what a voice guide looks like*, but the content is different.

---

## File and directory conventions

```
aagman-content-layer-2/
├── system_brief.md                   ← this file
├── voice/
│   ├── layer2_voice_base.md
│   ├── substack_overlay.md
│   ├── carousel_overlay.md
│   └── thread_overlay.md
├── prompts/
│   ├── signal_identifier_macro.md    ← operator
│   ├── signal_identifier_realtime.md ← operator
│   ├── research_agent.md             ← operator OR drafted
│   ├── blog_writer.md                ← operator
│   ├── carousel_writer.md            ← operator OR drafted
│   ├── thread_writer.md              ← operator OR drafted
│   ├── infographic_ideator.md        ← operator OR drafted
│   ├── markets_reviewer.md           ← drafted by setup agent
│   └── seo_aeo_audit.md              ← operator
├── signals/
│   └── {date}-digest.md              ← output of signal identifiers (macro + realtime lenses)
├── research/
│   └── signal-{id}.md
├── drafts/
│   ├── signal-{id}-blog.md
│   ├── signal-{id}-carousel-linkedin.md
│   ├── signal-{id}-carousel-instagram.md
│   ├── signal-{id}-thread.md
│   └── signal-{id}-infographic-concepts.md
├── reviews/
│   └── signal-{id}/markets-review.md
├── final/
│   └── (approved files per surface)
├── state/
│   ├── signal_log.md                 ← every signal, its status, which surfaces produced
│   ├── publish_calendar.md           ← scheduled publishes per surface
│   ├── operational_config.md         ← automation depth, cadence, file conventions
│   └── tickets/
│       └── {date}-{signal-id}.md     ← operator format-decision tickets

```

---

## What the setup agent does, step by step

1. **Read this entire brief.** Confirm understanding back to the operator in a short summary covering: the signal-as-unit principle, the fan-out architecture, the universal markets reviewer, the multi-format-from-one-research economy, the per-surface voice overlays. Flag anything unclear before proceeding.

2. **Ask the operator for the prompts they already have**, in this order. Receive each one, save it to the right path in `prompts/`, and confirm receipt before asking for the next.
   - Signal identifier — Macro/structural lens
   - Signal identifier — Real-time market lens
   - Blog writer prompt
   - SEO/AEO audit prompt
   - Carousel writer prompt (if exists)
   - Thread writer prompt (if exists)
   - Infographic ideator prompt (if exists)
   - Research agent prompt (if exists)
   - Layer 1 voice guide, covered-call reference, and Layer 1 reviewer prompt (as structural references only — do not copy their substance)

3. **For each prompt the operator does NOT have**, draft it from the role spec in this brief, share with operator, iterate until approved, then save to the right path.

4. **Draft the markets reviewer prompt** based on section 8 of this brief. Share with operator, iterate, save.

5. **Draft the Layer 2 voice guides** (base + Substack overlay + carousel overlay + thread overlay) if the operator doesn't already have them. Iterate, save.

6. **Set up the directory structure** per the conventions above. Create empty state files (`signal_log.md`, `publish_calendar.md`) with schema headers.

7. **Add the "correction mode" instruction to each writer prompt** so they know how to consume the markets reviewer's feedback file. Have the operator approve the wording once.

8. **Confirm the full loop** with the operator before any signal is processed end-to-end:
   - Where does the signal identifier output land?
   - How does the operator pick signals and write tickets?
   - How are research → writers → reviewer → corrections → audit → final wired (sequential agent calls, file-watching, manual triggers)?
   - Which steps are automated and which require operator action?
   - What's the approval surface (dashboard, CLI, file inspection)?

9. **Decide two operational questions with the operator:**
   - **Automation depth.** Full operator gates between every agent (slow, safe) or only at signal-pick and final-approval (fast, lighter supervision)? Recommendation: full gates for the first 2 weeks while calibrating; drop intermediate gates once consistent.
   - **Cadence.** Fixed publishing cadence per surface (e.g., 1 Substack/week, 3 carousels/week) with agents stretching to fill it, OR publish only when signals are strong enough? Recommendation: the latter, because Layer 2's value is signal quality, and forced filler dilutes the franchise.

10. **Run one end-to-end test signal** with the operator watching every step. Confirm each agent's input/output, the markets reviewer's cross-surface check, the operator's approval surface. Adjust prompts where needed. Only after this test passes is the system live.

---

## Hard rules across the layer

- **Skeptical by default.** Especially the markets reviewer. Consensus-aligned macro content is the most common failure mode; the reviewer's job is to be the friction against it.
- **One signal, one research artifact, many surfaces.** Never re-research the same signal per surface. The research agent is the single source; surface writers consume it.
- **Cross-surface consistency is mandatory.** The markets reviewer is the only place this gets enforced, so its cross-surface pass is non-optional.
- **No fabrication.** Every number, claim, quote, or sourced point in any surface traces to the research artifact or to a live verifiable source. Illustrative framings are allowed where openly labeled.
- **The operator sees all surfaces from one signal together at approval.** Not piece by piece. This is what makes the cross-surface check meaningful at the human gate too.
- **SEO/AEO audit is blog-only.** Don't run it on carousels, threads, or infographics — produces noise.

---

## What the setup agent should NOT do

- Do not invent or guess any prompt the operator says they already have.
- Do not start processing signals before all prompts are gathered and the test signal has passed end-to-end.
- Do not skip the operator iteration step on any drafted prompt. The operator approves every prompt before it goes live.
- Do not graft this onto Layer 1's pipeline. Layer 2 is its own system, with its own state files, its own dashboard (or dashboard view), its own cadence. The two layers may share underlying tools (web search, file I/O, the same agent runner) but are operationally separate.

---

End of brief. Ask the operator for the first item in step 2 to begin.
