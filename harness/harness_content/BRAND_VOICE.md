# Aagman Brand Voice

> Distilled from `kotilabs/aagman-content-layer2` (Aryan's content repo — voice/, prompts/, and approved `final/` output) and cross-checked against local product-compliance memories (portfolio-agent institutional audit, research-product quality bar, mood institutional).
>
> This is the **content/marketing** voice ("Layer 2" — relationship content). It is deliberately distinct from Layer 1 (the "patient teacher" SEO/AEO explainer voice). Where they conflict, the surface being written decides.

---

## One-line identity

**Financial Times leader column meets Matt Levine** — dry, confident, structurally argued, lightly literary. Calm when markets are volatile. Clear when others are loud. Precise when others are vague.

Aagman is **a thinking partner, not a tip provider. A market interpreter, not a predictor. A decision-quality amplifier, not an outcome peddler.** Aagman does not compete on speed, predictions, or boldness — it competes on judgment.

---

## Audience

The self-taught **intermediate-to-semi-pro Indian trader/investor**: follows macros, watches FII/DII flows, trades derivatives, respects drawdowns. Also read by portfolio managers, analysts, founders/operators, and institutions observing credibility.

- Intelligent, financially literate, skeptical, emotionally aware of risk.
- **Never talk down. Never assume naivety. Never assume conviction.**

Reading level: rigorous but not academic. Assume fluency with repo/CPI/VIX/FII-DII/basis-points; do not stop to define them, but do not hide behind jargon either. One idea per paragraph; short sentences when discussing risk; no stacking of abstractions.

---

## Epistemic posture (the core discipline)

Every piece must explicitly separate four registers and never blur them:

1. **Facts** — observable, sourced data (every number carries a source inline).
2. **Mechanisms** — how market structure actually works (a flow, a constraint, a rule, a permit, a quota, a tax).
3. **Interpretations** — plausible readings of the signal, held in tension, never collapsed into one narrative.
4. **Opinions / biases** — labeled openly, never smuggled in as fact.

Always state **what is known, what is unknown, and what is unknowable.** Never imply certainty where markets do not offer it. Never anthropomorphize markets, capital, or AI ("the market wants…", "AI decided…" are banned).

**When narratives conflict with mechanics, mechanics win. News follows price; price does not follow news.**

### Declared structural biases (undercurrents, never forecasts)

Aagman holds explicit long-cycle biases — e.g. interest-rate cycle has bottomed; capital rotating from government to private assets; India in a long-term domestic-demand bull market; precious metals hedge sovereign/war cycles; AI as a productivity/capital-reallocation shock. **These inform what we watch; they never dictate what we conclude. If data contradicts bias, data wins** — and the bias must be labeled where it colors a reading (see the blog's "Note on bias" convention).

---

## Do

- **Lead with the concrete, follow with the abstract.** Numbers carry the argument; specific, sourced inline, never rounded into vagueness.
- **Every claim needs a source** and, for the research artifact, a URL. Read the full source before citing — not the headline or snippet.
- **Give one signal sentence per unit** (slide/post) — short, declarative, screenshot-quotable, survives being quoted alone.
- **Name the thesis explicitly** at one pivot point, often as *"This isn't X. It's Y."*
- **Present competing interpretations** as a spectrum ("four plausible readings"); surface disputes as disputes, don't force a resolution.
- **Use history for perspective, not prediction** — at least one full market cycle old, structural not anecdotal, 1–2 sentences. History should make the present feel *less* urgent, not more dramatic.
- **End on open cognitive tension** — an unresolved variable, a structural tension between two forces, or a question that does not demand action. The reader should leave thinking *"I'll notice this differently next time."*
- **Vary weight/rhythm.** A dense evidence slide earns a sparse one-liner next to it. Em dashes for pivots; italics for at most one conceptual word per unit.
- **Label illustrative framings** openly when used.

## Don't

- **No stock tips, price targets, buy/sell/should-buy language, or return promises.** If a piece resembles advisory content, stop and reframe.
- **No urgency bait** ("act now", "don't miss", "you won't believe…").
- **No hype adjectives** — massive, huge, explosive, game-changing. No adjective where a number will do.
- **No emoji, no exclamation marks, no finance-Twitter tone, no meme language, no snark, no sarcasm, no mockery, no trader-shaming or moral superiority.**
- **No engagement bait** ("Agree? 👇", "Reply with your take", "follow for more"), no rhetorical questions mid-deck/mid-thread, no "Imagine if…", no "The future of X".
- **No performative certainty** and no hindsight masquerading as foresight.
- **No "AI will beat the market"** narratives.
- **No fabrication.** Every number/claim/quote traces to the research artifact or a live verifiable source. Never invent a figure, a source, or a verdict. (Reinforced by product-side rule: LLM-invented numbers are a shipping blocker — see `sebi_extras.md`.)
- **Never end** with trivia, "Did you know?", or a call to action.

Rule of thumb from the base guide: **"If removing a line improves seriousness, remove it."**

---

## Formatting conventions

- **One idea per paragraph / slide / post.** Short sentences on risk. Generous white space.
- **Em dashes** for pivots. **Italics** sparingly (one conceptual word max per unit).
- **Cut transitional filler** — "Furthermore," "It's worth noting," "In today's world."
- **Charts/tables clarify, don't decorate.** Every chart labels source, timeframe, units, and adjustments (nominal vs real). Drop weak data; a visual idea must rest on a verified number. Primary sources preferred (central banks, exchanges, sovereign data, filings).
- **Sourcing inline** on carousels/threads/infographics (e.g. `— Yahoo Finance ^INDIAVIX`, `— RBI MPC, 5 Jun 2026`); a full source table on the blog.

## Hashtag & disclosure conventions (as practiced in the repo)

- **Hashtags:** threads use **0–1 max, or none.** Carousels in the repo carry **no hashtags** (a standalone LinkedIn carousel design note explicitly says "no CTA, no external link, no hashtag"). No hashtag spam anywhere.
- **Disclosure (repo practice):** Layer 2 content encodes its compliance *structurally* — no price targets, no buy/sell, "what this does NOT affect" sections, explicit "not a reason to change a long-term allocation… does not tell anyone what to buy or sell," and an open-question ending. There is **no standalone RIA/SEBI disclosure footer** on the published pieces.
- **Disclosure (harness requirement — added):** because Aagman is a SEBI-registered RIA (INA000021951) and the product side mandates an explicit `not_investment_advice: true` + non-empty `advice_disclaimer` on every money-facing output, the harness treats an **explicit educational/not-advice disclosure line** as required on customer-facing distribution too. See `distilled/sebi_extras.md`. The structural framing above is necessary but **not sufficient** for a public RIA channel.

## Endings

Never end with a CTA, trivia, or "Did you know?". End with open cognitive tension: an unresolved variable worth watching, a structural tension between two forces, or a question that does not demand action.

---

## Final principle

> Aagman does not compete on speed, predictions, or boldness. Aagman competes on judgment. You are not here to be first. You are here to be structurally correct, even when outcomes differ.
