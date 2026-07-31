# Phase 2B — Content Distillation Report

**Date:** 2026-07-03
**Scope:** Extract real brand-voice / channel / compliance content for the AAGMAN harness from real sources. No invention.

## Sources actually read

1. **`kotilabs/aagman-content-layer2`** (public, Aryan's repo — cloned `--depth 1`). **Verdict: RICH, not thin.** It is a fully operational content system, not a stub:
   - `README.md` + `system_brief.md` — full "one signal, many surfaces" architecture, 13-agent pipeline, hard rules, file conventions.
   - `voice/` — 4 real voice docs: `layer2_voice_base.md`, `substack_overlay.md`, `carousel_overlay.md`, `thread_overlay.md`.
   - `prompts/` — 10 agent prompts (signal identifiers, research agent, blog/carousel/thread writers, infographic ideator, markets reviewer, SEO/AEO audit).
   - `final/` — 15 **approved** output files (real blog, LinkedIn + Instagram carousels, thread, infographic concepts) across signals: central-bank-divergence-RBI, india-vix-compression, dii-wall-fii-exodus, china-slower-growth, us-iran-oil-gold.
   - `research/`, `reviews/`, `signals/`, `state/` — canonical research artifacts, markets reviews, digests, operational config.
   - Single commit `927e658` ("Layer 2 run: central-bank divergence + RBI toolbox, China slowdown, US-Iran oil/gold, India VIX").

2. **Local session memories** (mined per instruction):
   - `project_portfolio_agent_institutional_audit.md` — **content-compliance gold.** SEBI disclaimer dropping, LLM-invented numbers, missing-price→0 fail-open, staleness-fail-open — all mapped into `rejected_patterns.json` + `sebi_extras.md`.
   - `project_research_product_quality_bar.md` — 5-tier customer-facing bar (liability/multi-language, prompt-injection, data fabrication, boundary/jurisdiction, edge). Fed the disclosure + no-fabrication + jurisdiction rules.
   - `project_mood_institutional.md` — reinforced "silent data loss is a bug / label staleness / never fail open" as a content-data principle.
   - `~/.claude/CLAUDE.md` — fail-fast / no-sentinel-fallback / typed-error discipline echoed into the fail-fast content rule.

## Deliverables (all under `harness_content/`, all non-empty)

| File | Status | Notes |
|---|---|---|
| `BRAND_VOICE.md` | ✅ | Full voice: identity, audience, epistemic posture, do/don't, formatting, hashtag+disclosure conventions, endings. Sourced from `voice/` + `final/`. |
| `distilled/examples.json` | ✅ **15 exemplars** | thread (3), linkedin_carousel (3), instagram_carousel (2), substack_blog (5), infographic (2). All verbatim from approved `final/` output with provenance in each `note`. |
| `distilled/rejected_patterns.json` | ✅ **13 patterns** | Hype, buy/sell (multi-language), urgency, engagement bait, emoji/snark, single-narrative certainty, LLM-invented numbers, silent defaulting, no-disclosure, anthropomorphism, filler, unlabelled bias. Derived from voice do/don'ts + portfolio-audit memory. |
| `distilled/channel_rules.json` | ✅ | substack_blog, x_thread, linkedin_carousel, instagram_carousel, infographic_concepts — lengths, per-slide/post structure, hashtag + disclosure + sourcing rules. |
| `distilled/sebi_extras.md` | ✅ | 7 content-specific compliance sections, stricter than base SEBI rules. |

(`inventory.md` not needed — repo structure was clear; this report covers it.)

## Key judgment calls / honest flags

- **content-layer2 was RICH.** Brand voice, channel formats, and content rules are almost entirely repo-sourced; the local memories supplied only the *compliance hardening* layer (disclosure, de-hallucination, fail-fast), which I've labelled as memory-sourced in `sebi_extras.md`.
- **Disclosure gap is a real finding, not an invention.** `grep` confirmed the published Layer 2 content carries **no standalone RIA/SEBI disclosure footer** — compliance is encoded *structurally* (no buy/sell, "what this does NOT affect", open-question endings). Because Aagman is a SEBI RIA (INA000021951) and the product side mandates an explicit `not_investment_advice` disclaimer, the harness **adds** an explicit-disclosure requirement on top of the repo's structural approach. This addition is called out as harness policy in both `BRAND_VOICE.md` and `sebi_extras.md` — it is not claimed to be existing repo practice.
- **Hashtags:** confirmed from source — threads `0-1 max or none`; carousels carry none (a design note literally says "no CTA, no external link, no hashtag"). Not fabricated.
- No secrets encountered or written. Only `harness_content/` was touched; `harness_core/` and `harness_engineering/` untouched.

## 5 brand-voice do/don'ts (extracted)

1. **DO** lead with the concrete, sourced number; **DON'T** use a hype adjective where a number will do (no massive/huge/explosive/game-changing).
2. **DO** hold competing interpretations in tension and separate facts/mechanism/interpretation/opinion; **DON'T** collapse an ambiguous signal into one confident narrative or perform certainty.
3. **DO** end on open cognitive tension (an unresolved variable, a non-actionable question); **DON'T** end with a CTA, trivia, or engagement bait.
4. **DON'T** give tips, price targets, buy/sell, or return promises (multi-language) — if it reads like advice, stop and reframe; **DO** draw the boundary explicitly ("what this does NOT affect").
5. **DO** trace every number to a real source and label bias/staleness inline; **DON'T** fabricate figures/sources or silently default a missing value (the product-side de-hallucination + fail-fast blocker).
