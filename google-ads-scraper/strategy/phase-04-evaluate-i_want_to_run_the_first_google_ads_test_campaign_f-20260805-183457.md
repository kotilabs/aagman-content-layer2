# Angle Scoring

**Scoring caveat first:** the ICP is unconfirmed. I've scored audience fit against the *implied* ICP — active Indian F&O / equity retail traders (the competitor set implies this). If the primary audience turns out to be long-term investors, angles 12 and 9 move up materially and this ranking should be redone. Channel is also undecided; executability assumes Search-first with Display possible, since that's the default for a first Google Ads test with a waitlist CTA.

## Scoring Table

| # | Angle (short) | Diff. | Audience Fit | Claim Safety | Executability | **Total** |
|---|---|---|---|---|---|---|
| 1 | Backtest before you bet | 4 | 5 | 5 | 4 | **18** |
| 2 | Plain words → backtest, no code | 4 | 5 | 5 | 5 | **19** |
| 3 | TWAP / VWAP live today | 5 | 4 | 5 | 4 | **18** |
| 4 | MIT / LIT / MTL — 9 order types | 5 | 4 | 5 | 4 | **18** |
| 5 | Multi-leg options, 4 legs in sync | 5 | 5 | 5 | 4 | **19** |
| 6 | You brief, they work, you approve | 4 | 5 | 5 | 5 | **19** |
| 7 | Kill switch + circuit breakers | 4 | 4 | 5 | 3 | **16** |
| 8 | SEBI IA + NSE-empanelled Whitebox | 5 | 4 | 5 | 4 | **18** |
| 9 | Trade in your language | 5 | 4 | 5 | 3 | **17** |
| 10 | Whitebox algos, disclosed logic | 5 | 3 | 5 | 3 | **16** |
| 11 | 500+ stock screener | 2 | 4 | 5 | 5 | **16** |
| 12 | Investor angle (compounders, MF) | 3 | 2 | 4 | 4 | **13** |
| 13 | Free in beta / legacy rates | 2 | 5 | 5 | 5 | **17** |
| 14 | Works with your existing broker | 3 | 5 | 5 | 4 | **17** |
| 15 | Second opinion that becomes a strategy | 2 | 5 | 5 | 3 | **15** |

### Notes on notable scores

- **Angle 11 (screener):** executability is high but differentiation is the problem — Tradomate is already saturating screener-intent keywords ("AI Stock Screener India," "Low PE Stock Screener"). We'd pay an auction premium to be the second-best version of their message.
- **Angle 13 (free/legacy rates):** low standalone differentiation ("free" is category-wide — Draconic uses it in ~70% of ads), but it's the best *conversion layer* in the set. Recommend deploying it as the universal offer/CTA suffix on the selected angles, not as a lead angle.
- **Angle 15:** deliberately enters Draconic's "ask before you trade" home turf. For a first test with an unknown budget, contested auctions are a bad place to learn. Defer.
- **Angle 9:** strong differentiation but executability is capped at 3 — we don't know if the landing page supports multi-language onboarding, which would break message match.

## Top 5 Selected Angles

**1. Angle 2 — Type your trading idea in plain words, get a backtest report. No Python, no Excel, no code.**
The broadest-appeal wedge: it describes the *category-creating* mechanic (natural language → tested strategy), not a feature. Both competitors sell analysis tools; neither claims idea-to-backtest in plain words. Trivially executable as Search copy against "backtest trading strategy India" intent.
*Safe-claim reference: §1 natural-language workspace; §6.1 prompt grammar; §16 Backtesting row (Yes).*

**2. Angle 6 — You brief, they work, you approve. Capital never leaves your broker.**
Draconic spends ~60% of its copy on the defensive negative ("Not a trading bot, no signals"). This angle owns the *positive* version of the same trust barrier — approval-gated, capital-stays-at-broker — which is both a differentiation play and a compliance-safe frame. Also a natural headline for any surface.
*Safe-claim reference: §1 core promise and "what it is not"; §7.3 / §9 capital-stays-at-broker; Content pillar #8.*

**3. Angle 5 — Multi-leg options: straddles, strangles, iron condors, up to 4 legs in sync, from one sentence.**
Speaks directly to the implied F&O core audience in their vocabulary — the same jargon-dense register Draconic uses — but with a capability nobody else claims. Concreteness ("4 legs in sync") is what makes it credible in a 30-character headline.
*Safe-claim reference: §7.1 options execution (multi-leg up to 4 legs in sync); §5 F&O coverage.*

**4. Angle 3 — TWAP and VWAP execution algos, live today.**
Verified competitor-empty territory: the institutional-democratization hook Draconic gestures at emotionally ("think like an FII desk") but Āagman can claim *functionally*. Angle 4 (MIT/LIT/MTL) scored identically and should run as a sibling ad group under the same "institutional execution for retail" theme rather than a separate bet.
*Safe-claim reference: §7.1 execution algorithms (TWAP/VWAP live); §7.2 retail broker comparison; §16 TWAP/VWAP row (Yes).*

**5. Angle 8 — SEBI-registered Investment Adviser (INA000021951) + NSE-empanelled Whitebox algo provider.**
The trust anchor for a first campaign with zero brand awareness: verifiable registration numbers beat "trust us" framing, and neither competitor runs credential-led creative. Hard to copy — a competitor would need the registrations, not just the words. Likely the strongest CTR driver on trust-sensitive finance queries, and the best defense against the category's "is this a scam?" objection.
*Safe-claim reference: §9.2 regulatory & compliance claims (INA000021951; NSE Circular Ref. 40/2026); §16 (no conflicting row); Content pillar #5.*

## Recommendation Structure (preview for the brief)

- **Lead angles (Search):** 2, 5, 3/4 (combined execution-depth cluster)
- **Trust layer (all ad groups):** 8 as sitelink/description line
- **Conversion layer (universal CTA):** Angle 13's offer — "Free while in beta, no credit card; early users lock legacy rates forever" — appended to every angle rather than tested alone

**Open items that still gate execution:** ICP confirmation (investor vs. trader — affects angle 12), budget/duration, landing-page message match for each angle, and a baseline waitlist number so "spike" is measurable.