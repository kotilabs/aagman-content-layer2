# Campaign Strategy — Āagman Waitlist Launch

## 1. Objective & Success Metric

**Objective:** 500 verified waitlist signups in 6 weeks.
**Budget:** ₹50,000/month × 6 weeks ≈ **₹75,000 total**.
**Target economics:** Blended CPA ≤ **₹150 per verified signup**. Since this is our first campaign, the real goal is dual: hit 500 signups *and* learn which segment + angle converts cheapest, so we can scale with confidence in quarter two.

**Measurement plan:**
- UTM-tagged landing page per angle/segment; "verified" = email confirmed (double opt-in), not raw form fills.
- Weekly review: pause any ad group with CPA > ₹250 after ~₹3,000 spend; reallocate to winners.
- Track signup → product activation as a secondary quality signal (which segment actually tries a backtest).

---

## 2. Audience Segments

Given the experimental mandate, we test **three segments** drawn directly from the source-of-truth personas (§2):

| Segment | Who | Hook | Est. share of test budget |
|---|---|---|---|
| **S1 — Active F&O trader** | NIFTY/BANKNIFTY options traders on Zerodha/Dhan, frustrated by limited order types | Institutional execution (TWAP/VWAP, MIT/LIT) + kill-switch risk control | 45% |
| **S2 — No-code systematic retail** | Traders with rule-based ideas but no Python/Excel skills | "Describe it in plain language, backtest it in minutes" | 35% |
| **S3 — Quality-stock investor** | Long-term equity/MF buyers, screener users | Quality-compounder screening + backtesting without spreadsheets | 20% |

**Deliberately excluded for now:** mutual-fund-only buyers and multi-language-first users — both are strong angles (§11) but we'll isolate them in Phase 2 once we have a baseline. Crypto/forex/international audiences are out of scope entirely (§5 — not supported).

---

## 3. Positioning & Differentiation (mapped to competitor gaps)

| Competitor gap (from ad intelligence) | Āagman counter-position |
|---|---|
| **Draconic has a messaging contradiction** — some ads say "AI trades for you," others say "not a bot." This is a trust and compliance liability. | **Resolve the contradiction they can't:** "You brief, they work, you approve." Every real-capital step requires explicit user approval — one coherent story, no wobble (§1, §14 pillar 2). |
| **Draconic owns "second opinion / ask before you trade"** and stops at analysis. No execution story. | **Go one step further than validation:** analysis → backtest → approved live deployment. We don't just say "ask first" — we say *"prove it first."* |
| **Tradomate is screener-and-insights only** — breakouts, PE/ROE screens, news alerts. No execution, no backtesting, no risk controls visible in any ad. | **Screener is step one, not the product.** Screen → backtest → deploy with a four-layer kill switch (§9.1). Full loop vs. half loop. |
| **Neither competitor claims regulatory standing in their ads.** Draconic even leans on defensive "not a bot" disclaimers as a compliance shield. | **Lead with compliance as a feature:** SEBI-registered Investment Adviser (INA000021951) + NSE-empanelled Whitebox algo provider (§9.2). Positive trust signal vs. their defensive one. |
| **Tradomate monetizes at ₹249/month; Draconic gates at "3 free analyses daily."** | **Free in beta, no card, legacy rates forever for early users** (§10) — a concrete, time-boxed reason to join the waitlist *now*. |
| **Both competitors are English-only in their creatives.** | Multi-language prompting (Hindi, Hinglish, Tamil, Bengali, Telugu — §11) as a Phase 2 wedge. |

**One-line positioning for the campaign:** *"An AI trading team built for Indian markets — you brief, they work, you approve."* (§1)

---

## 4. Messaging Angles

Each angle maps to a **safe-to-claim** capability. No angle touches a "No" row.

### Angle A — "Proof before money." (Primary, all segments)
> "Describe your strategy in plain language. Backtest it on real historical data — with fees and slippage baked in. Only deploy what survives."
- **Source of truth:** Backtesting — *Yes* (§16); backtest methodology with look-ahead-bias protection and cost assumptions (§8.1); full backtest report suite — Sharpe, drawdown, win rate, expectancy (§8.2).
- **Cautious wording:** When referencing the full Backtest → Paper → Live workflow, frame it as the product's enforced discipline ("built to make you prove a strategy before real capital"), per the *Partially* guidance on paper trading (§16) — do not promise a specific paper-trading feature experience until verified live.
- **Why it wins:** Neither competitor tells an evidence story. Draconic validates opinions; we validate *strategies with numbers*.

### Angle B — "The order types your broker app hides." (S1 — F&O traders)
> "TWAP and VWAP execution algos. MIT, LIT, Market-to-Limit. Multi-leg options in sync, up to 4 legs. From a chat window."
- **Source of truth:** TWAP/VWAP — *Yes* (§16); 9 native order types incl. MIT/LIT/MTL, trailing stops, brackets (§7.1); multi-leg options (§7.1); retail-vs-institutional comparison table (§7.2).
- **Guardrail:** Never mention Iceberg or POV — they are "coming next" and *not safe to claim* (§16).

### Angle C — "Regulated. Whitebox. Yours." (Trust layer — all segments, esp. S1)
> "SEBI-registered Investment Adviser. NSE-empanelled Whitebox algo provider. Every algo order tagged and auditable. Your capital never leaves your broker."
- **Source of truth:** §9.2 (SEBI IA INA000021951, NSE Whitebox empanelment, unique algo IDs, DPDP-aligned India hosting); §9.1 (four-layer kill switch, pre-trade risk checks, circuit breakers); §14 pillar 8 (capital stays at broker).
- **Why it wins:** Turns Draconic's defensive "not a bot" disclaimer into our affirmative trust claim.

### Angle D — "Screen like an analyst, without the spreadsheet." (S3 — investors)
> "Find quality compounders — ROE above 15%, low debt, steady growth — and backtest the screen before you invest a rupee."
- **Source of truth:** Screener — *Yes* (§16); fundamental metrics incl. ROE, ROCE, debt-to-equity, Piotroski (§6.2); investor workflow steps 1–2 (§4.4); example prompts (§6.1).
- **Guardrail:** Do **not** mention portfolio health scores, tax insights, or curated news — all "coming soon" and *not safe to claim* (§16).

### Angle E — "Free in beta. Locked in forever." (Offer layer — all segments)
> "Early waitlist users get legacy rates — forever. Free while in beta, no card required."
- **Source of truth:** §10 pricing & access.
- **Role:** Not a standalone campaign — layer this onto every CTA as the urgency mechanic.

---

## 5. Channel & Format Plan

### Google Search (~65% of budget)
High-intent harvesting with three campaign clusters:

1. **Category intent (S1/S2):** "backtest trading strategy India," "TWAP VWAP orders retail," "algo trading without coding," "options strategy builder NSE." Landing page: Angle A/B hybrid.
2. **Screener/investor intent (S3):** "stock screener ROE debt India," "quality stocks screener NSE." Landing page: Angle D. (These keywords are proven by Tradomate's sustained spend on identical intent — they've run screener ads since Jul 2025, which validates the demand.)
3. **Competitor conquesting (small test):** brand terms for draconic/tradomate-type alternatives ("AI trading second opinion," "tradingview alternative India"). Use comparison framing, never their copy (Rule 4). Cap at 10% of Search budget — conquesting CPAs are volatile.

### YouTube (~35% of budget)
Draconic's own intel shows statics underperform on YouTube, so we go **video-first**:

- **Asset 1 (30s, demo-led):** Screen recording — type a Hinglish prompt → backtest report appears → approve step. Ends on Angle A + E. This is our hero asset; a real product demo is something neither competitor's ad library shows.
- **Asset 2 (15s, cutdown):** "Your broker app has 4 order types. We have 9 — plus TWAP and VWAP." Angle B.
- **Asset 3 (15s, trust):** SEBI IA + NSE Whitebox + "capital stays at your broker." Angle C.
- **Targeting:** Custom segments on F&O/trading search terms + placements on Indian trading education channels; remarketing pool from Search clickers in weeks 3–6.

---

## 6. Variant Test Plan

Six weeks, structured like Draconic's sprint cadence — but we **retain winners** instead of full refreshes (their intel shows no evergreen retention; that's our edge).

| Week | Test | Variants | Decision rule |
|---|---|---|---|
| 1–2 | **Angle A/B test** (Search + YT) | Angle A (proof-first) vs. Angle B (order types) vs. Angle C (compliance) | Winner = lowest verified-signup CPA at ≥20 signups |
| 2–3 | **Segment test** (Search) | S1 vs. S2 vs. S3 landing pages, same winning angle | Reallocate budget split per §2 based on results |
| 3–4 | **Offer framing** | "Free in beta, no card" vs. "Legacy rates forever" | CTR + signup rate on landing page |
| 4–5 | **Language test** (YT only) | English voiceover vs. Hinglish voiceover, same creative | Watch-to-signup rate; feeds Phase 2 decision on multi-language push |
| 5–6 | **Scale winners** | 80% budget into top angle × top segment; 20% continues exploration | — |

**Test hygiene:** one variable per test; minimum ₹5,000 spend per cell before judging; keep a shared negative-keyword list from week 1 (exclude "tips," "calls," "sure profit," "free intraday calls" — they attract tip-seekers who will churn and pollute the waitlist).

---

## 7. Budget Split Recommendation

**₹75,000 total over 6 weeks (~₹12,500/week).**

| Allocation | Amount | Rationale |
|---|---|---|
| Search — category intent (S1/S2) | ₹27,000 (36%) | Highest intent, fastest learning loop |
| Search — screener/investor intent (S3) | ₹9,750 (13%) | Proven keyword demand (Tradomate's longevity), cheaper CPCs |
| Search — conquesting test | ₹4,875 (6.5%) | Strictly capped experiment |
| YouTube — video assets 1–3 | ₹22,500 (30%) | Demo-led video is our biggest differentiator; YT CPVs are cheap in India |
| YouTube/Search remarketing (wks 3–6) | ₹6,000 (8%) | Convert warm traffic; F&O buyers rarely convert first-touch |
| Creative reserve / contingency | ₹4,875 (6.5%) | Cutdown edits, winning-variant iterations |

**CPA math:** at ₹75,000 / 500 signups = ₹150 blended target. Expect Search to land near ₹120–180 and YouTube-assist to pull blended CPA down via remarketing. If any cluster exceeds ₹250 CPA after its test cell budget, pause and reallocate.

---

## 8. What Not to Say (Compliance Guardrails)

**Hard "No" claims — never present as shipped (§16):**
- ❌ MCX commodities trading ("draft PRD — not shipped")
- ❌ Live Portfolio Dashboard
- ❌ Portfolio health score, tax-impact alerts, LTCG tracking ("coming soon")
- ❌ Curated holdings-based news feed
- ❌ Iceberg or POV execution algos ("coming next" — may be teased only as "coming next," never as live)

**"Partially" claim — cautious wording only (§16):**
- ⚠️ Paper trading: describe only as the product's intended workflow discipline ("built to make you prove it before real capital"), never as a verified live feature experience.

**Category-level guardrails (§1, §9.2):**
- ❌ Never say or imply "AI trades for you" / autonomous trading — every real-capital step requires user approval. (This is also Draconic's exposed weakness; we must never repeat it.)
- ❌ Never position Āagman as a broker, DP, or Research Analyst.
- ❌ No tips, signals, stock picks, or "what to buy" framing — we are explicitly not a tip service.
- ❌ No return promises, profit screenshots, or performance guarantees in any creative.
- ❌ No "91% of traders lose money" fear-stat copy (Draconic uses it) — it invites regulatory scrutiny and off-brand fear appeal.
- ❌ No crypto, forex, or international-stock references — out of scope (§5).
- ❌ Never copy competitor phrasing ("second opinion," "think like an FII desk," etc.) — gap analysis only, original wording always.
- ✅ Always include in footer/landing page: "SEBI-registered Investment Adviser: INA000021951. Āagman is not a broker. Capital stays in your existing broker account."

**Bottom line:** We win by being the only player with a coherent, regulation-first story that spans the full loop — describe, prove, approve, execute — in the user's own language, free in beta. Six weeks, three segments, one variable at a time, kill fast, scale what survives.