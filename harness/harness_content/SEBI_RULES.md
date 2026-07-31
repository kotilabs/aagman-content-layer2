# SEBI_RULES.md — Compliance rules for public CONTENT

> Enforced by `ComplianceGate(rules_file="harness_content/SEBI_RULES.md", ...)`
> on every content artifact before PUBLISH. Aagman operates as a SEBI-registered
> Investment Adviser (**Koti Labs**, RIA reg **INA000021951**); all public content
> sits under RIA scrutiny. The panel votes against the RULES below; the
> `REQUIRED_STRINGS` section is enforced deterministically in code.

---

## THE SIX BASE RULES (SEBI RIA — educational content)

1. **Educational only — no buy/sell calls.** Content informs and explains. It
   never issues a buy, sell, hold, entry, or exit instruction on any specific
   security, in any language (English *buy/sell/should/recommend*, and Hindi /
   Hi-en `kharidiye`, `kharido`, `बेच`, `खरीद`). If a piece reads like advice,
   stop and reframe.
2. **No return claims / no performance promises.** Never state, imply, or
   backfit guaranteed, expected, or "typical" returns. No "this stock will
   give X%", no "our strategy returns Y%". Past data may be described as
   history, never projected as a promise.
3. **3-month price lag.** Do not quote a specific tradeable price/level for a
   named security more recent than three months old. Older, clearly-dated
   context is educational; fresh price levels edge into a live call.
4. **Mandatory RIA identification at the start of every post.** Every published
   unit opens by identifying the adviser — the RIA name (**Koti Labs**) and the
   registration number (**INA000021951**) — so the reader always knows the
   source and its regulatory standing. See `REQUIRED_STRINGS`.
5. **No specific security recommendations.** No "top 5 stocks to buy", no single-
   name conviction pitch, no model-portfolio tickers presented as a to-do list.
   Illustrative mentions are allowed only as neutral, dated, educational examples.
6. **Clear labeling.** Label what a thing is: *educational*, *illustrative*,
   *estimate*, *house view / bias*, *promotion of own product*. Nothing is
   smuggled as neutral fact. Every customer-facing unit carries an explicit
   **not-investment-advice** disclosure appropriate to the channel.

---

## STRICTER CONTENT-LAYER RULES (merged from content-layer2 + product compliance)

7. **No-advice boundary is absolute and multi-language.** No stock tips, price
   targets, entry/exit levels, or return promises — in any language. "Personal
   allocation" prompts ("where should I put ₹50L") get context, never a
   recommendation.
8. **Explicit disclosure is required and must NOT be droppable.** Structural
   framing (no buy/sell, open-question endings) is necessary but not sufficient
   for a SEBI RIA distributing publicly. The not-investment-advice disclosure
   must be present on every unit and must survive fallback/edge paths — the
   product-side failure was a disclaimer present on the happy path and dropped
   on the fallback path. Do not repeat it in content.
9. **No fabrication — every number traces to a source.** Every number, claim,
   quote, or fund/AMFI code traces to a research artifact or a live verifiable
   source; read the full source before citing. No invented statistic, source
   URL, or verdict. Fictional instrument or empty corpus → abstain, do not invent.
10. **Fail-fast on missing/stale data — never silently default.** Never present
    a derived, stale, or assumed figure as a hard current fact. Label
    stale/estimated/derived data (`as of <date>`, `estimate — sources differ`,
    `used for perspective, not prediction`) or drop it. Never fail *open* to
    "fresh/fine".
11. **Bias must be labelled, not smuggled.** House views (India long-cycle, gold
    hedge, rate-cycle) are undercurrents, never forecasts; flag inline where a
    view colours a reading. If data contradicts the bias, data wins. Promotion
    of Aagman's own product is openly labelled, never dressed as neutral analysis.
12. **No urgency, no anthropomorphism, no certainty theatre.** No "act now" /
    "don't miss" urgency bait (for an RIA this edges into inducement). Never
    anthropomorphize markets or imply a certainty markets don't offer. Present
    competing interpretations in tension; end on open cognitive tension, not a CTA.
13. **Jurisdiction / product boundary.** Out-of-scope topics (US equities,
    crypto, tax-filing, insurance) get a NOT_SUPPORTED / jurisdiction framing,
    not an improvised take. Stay within competence: Indian markets, macro,
    cross-asset commentary.

---

## REQUIRED_STRINGS

Every published content artifact MUST contain these verbatim (enforced in code by
ComplianceGate — a deterministic block, independent of the panel vote):

- Koti Labs
- INA000021951

---

## ONE-LINE PRE-PUBLISH GATE

No tips/targets/returns · every number sourced (no fabrication) · stale/estimated
data labelled · bias labelled · explicit not-advice disclosure present and
non-droppable · RIA name + reg number present · ends on open tension, not a CTA.
