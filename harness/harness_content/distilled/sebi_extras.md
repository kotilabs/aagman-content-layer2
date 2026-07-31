# SEBI / Compliance Extras — Content-Specific

> Content-layer rules that are **stricter than or additional to** the base SEBI rules (merged into `SEBI_RULES.md` in Phase 3). Sourced from `kotilabs/aagman-content-layer2` (voice guides, README content rules, approved output) and the product-side compliance memories (portfolio-agent institutional audit, research-product quality bar, mood institutional). Aagman entity context: SEBI RIA **INA000021951** (Koti Labs) — public content sits under RIA scrutiny.

---

## 1. No-advice boundary is absolute on public content

- **No stock tips, price targets, entry/exit levels, or return promises** — in any language. Product-side bar is zero-tolerance and multi-language: banned English *buy/sell/should/recommend* AND Hindi/Hi-en (`kharidiye`, `kharido`, `बेच`, `खरीद`). Content inherits the same bar.
- **"Personal allocation" is not an exception.** "Where should I put ₹50L" style prompts get context, never a recommendation (from the research-product quality bar, Tier 4 boundary).
- **If a piece resembles advisory content, stop and reframe.** This is a first-class editorial gate, not a footnote check.

## 2. Explicit disclosure required (harness policy — stricter than repo practice)

- **Finding:** the published Layer 2 content in the repo carries **no standalone RIA/SEBI disclosure footer**. It encodes compliance *structurally* — no buy/sell, a "what this does NOT affect" section, "does not tell anyone what to buy or sell", and an open-question (non-directive) ending.
- **Harness requirement:** structural framing is **necessary but not sufficient** for a SEBI-registered RIA distributing publicly. Every customer-facing content unit must additionally carry an **explicit educational / not-investment-advice disclosure** appropriate to the channel (deck back-slide, thread pinned/profile or final post, blog footer). This mirrors the product-side mandate that every money-facing output ship with `not_investment_advice: true` and a non-empty `advice_disclaimer` (portfolio-agent audit BLOCKERs 1–2: the disclaimer being *dropped* on the highest-risk output was a shipping blocker).
- The disclosure line must not be swallowed on fallback/edge paths — the product bug was precisely that the disclaimer was present on the happy path and dropped on the rebalance/stress fallback.

## 3. No fabrication — every number traces to a source

- **Content rule:** every number, claim, quote, or sourced point in any surface traces to the research artifact or a live verifiable source. Read the **full source** before citing (not headline/snippet). Illustrative framings allowed **only when openly labelled**.
- **Product reinforcement (de-hallucination):** LLM-invented numbers are a documented blocker — the portfolio agent shipped LLM-emitted stress/rebalance figures and fabricated qty/value as if deterministic. For content this means: no invented statistic, no invented source URL, no invented fund/verdict/AMFI code. **Fictional instrument or empty corpus → abstain, do not invent.**
- Where estimates legitimately differ (e.g. FII flow numbers across brokers), **include a source-definition line** and never launder one estimate as "the official figure" (infographic "What to avoid" convention).

## 4. Fail-fast on missing/stale data — never silently default

- No sentinel fallbacks: never present a **derived, stale, or assumed** figure as a hard current fact. The portfolio audit's headline BLOCKERs were missing-price→0, cost-basis-as-live-value, and unvalued holdings silently dropped. The content analogue: label stale/estimated/derived data (`used for perspective, not prediction`, `as of <date>`, `estimate — sources differ`), or drop it.
- **Flag staleness explicitly.** Stale-data corpus → surface `last_updated` (research-product bar, Tier 3). Never fail *open* to "fresh/fine".

## 5. Bias must be labelled, not smuggled

- Aagman's declared long-cycle biases (India bull market, gold hedge, rate-cycle bottom, etc.) are **undercurrents, never forecasts**. Where a house view colours a reading, flag it inline (the blog `*Note on bias: … it is not evidence. Data can still contradict it.*` convention). **If data contradicts bias, data wins.**
- Promotion of Aagman's own product/strategies must be **openly labelled**, never dressed as neutral market analysis.

## 6. No urgency, no anthropomorphism, no certainty theatre

- No urgency bait ("act now", "don't miss") — SEBI-adjacent concern: manufactured urgency pushes readers toward action, which for an RIA edges into inducement.
- Never anthropomorphize markets/capital/AI, and never imply certainty markets don't offer. Present competing interpretations in tension; consensus-single-narrative content is the flagged failure mode.

## 7. Jurisdiction / product boundary (from research-product bar, Tier 4)

- Out-of-scope topics get a **NOT_SUPPORTED / jurisdiction** framing rather than an improvised take: US equities, crypto, tax-filing advice, insurance. Content on Aagman channels stays within its competence (Indian markets, macro, cross-asset commentary) and does not drift into regulated adjacent advice.

---

### One-line gate for any content unit before publish
No tips/targets/returns · every number sourced (no fabrication) · stale/estimated data labelled · bias labelled · explicit not-advice disclosure present and not droppable · ends on open tension, not a CTA.
