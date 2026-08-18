# Markets Review — signal-ola-electric-pli-ev-battery

**Reviewer:** Aagman Layer 2 Markets Reviewer
**Date:** 2026-08-12
**Outputs reviewed:** standalone carousel (10 slides), infographic concepts (5 concepts + recommendation)
**Not produced for this signal (skipped):** blog, thread, promo carousel
**Reference:** research/signal-ola-electric-pli-ev-battery.md

---

## Cross-surface consistency table

| Claim | Research artifact | Carousel | Infographic | Verdict |
|---|---|---|---|---|
| ₹7,240 cr ceiling, 5-yr quarterly window to CY2031 | ✓ (BSE filing, Aug 12) | Slides 1, 5, 7, 10 ✓ | Verified table, Concepts 1/3/5 ✓ | Consistent |
| ₹0 disbursed vs ₹5,180 cr invested (May 31, 2026) | ✓ Lok Sabha reply | Slide 3 ✓ | Concept 1 ✓ | Consistent |
| 1.4 GWh of 50 GWh (2.8%) commissioned, Oct 2025 | ✓ IEEFA/JMK | Slide 2 ✓ | Concept 1, hero stats ✓ | Consistent |
| Ola capacity: 2.5 GWh installed / 3.5 under installation / 6 GWh by quarter-end | "installed" | Slide 6: "2.5 GWh built" | Concept 2: "commissioned capacity to date ~2.5 GWh" | **Drift** — research says *installed*; infographic upgrades to *commissioned*, which is the term the scheme gates on and was last verified at 1.4 GWh (Oct 2025). Use "installed" everywhere. |
| Ceiling ≈ 21x quarterly loss | Table says 21.5x; Interpretation C says ≈21x | Slide 5: "≈ 21x" | Verified table: "≈ 21x" | Consistent between outputs; trivially understates the table's own 21.5x. Optional: align to 21.5x. |
| $8–9/kWh implied support, ~15% of ~$55/kWh LFP | Derived, labelled | Slide 7 ✓ labelled derived | Concept 3 ✓ derivation footnote mandatory | Consistent; correctly caveated on both surfaces |
| 75% of BEV batteries in India predominantly Chinese | "predominantly from China," BEV | Slide 8 headline: "75% of the batteries in India's EVs come from China" | Concept 4: "predominantly Chinese" ✓ | **Carousel compresses**: drops "predominantly" and shifts BEV→EV. Infographic is faithful. |
| Allocations: Ola 20 / Reliance 10+5 / ACC Energy 5 / unallocated 10 | ✓ Lok Sabha reply | Slide 9 ✓ but hero stat says "10 GWh **never** allocated" | Concept 2 ✓ | **Carousel hero stat is wrong** — the 10 GWh was allocated to Hyundai in Mar 2022, freed on withdrawal, re-tendered in Sep 2024, and not re-awarded. "Never allocated" contradicts the research's own auction history. |
| ACC Energy Storage = Rajesh Exports' vehicle | Implied (Rajesh won 5 GWh, Mar 2022; ACC Energy Storage holds 5 GWh) but never stated explicitly | Slide 3: "Rajesh Exports' vehicle" | Concept 2: "ACC Energy Storage (Rajesh Exports)" | Both surfaces present an inference as fact. Almost certainly true, but the artifact doesn't establish it — attribute or hedge. |
| 40% of scheme budget rides on Ola | ✓ derived (₹7,240 of ₹18,100 cr) | Not used | Verified table ✓, no concept features it | Underused, not inconsistent |
| ₹57 cr provision reversal, auditor-flagged | ✓ Outlook Business | Slide 4 ✓ | Concept 5 ✓ | Consistent |
| Market cap ~₹18,236 cr, ceiling ≈ 40% of it | Sourced to Fortune India row | Not used | Concept 5 attributes to **Trade Brains** | Minor attribution mismatch with the artifact's sourcing |

---

## Carousel feedback table

| Slide | Issue | Severity | Recommendation |
|---|---|---|---|
| 1 | Headline "Zero conditions already met" is ambiguous and fails under its most natural reading. Milestone-1 has three gates: commissioning, ≥₹225 cr/GWh invested, ≥25% DVA. Ola has commissioned 2.5 GWh and (as the scheme's dominant investor) almost certainly met the investment gate — the unmet gate is DVA *verification*. A reader can also parse the headline as "zero conditions attached," which would be flatly wrong for a conditional, DVA-scaled stream. | **Blocker** | Rewrite. Something like "₹7,240 crore on the table. One unverified gate still stands in the way" — the tension the speaker note intends is approval vs payout, not zero vs everything. |
| 9 | Hero stat "40 GWh of 50 GWh awarded; 10 GWh never allocated" is factually wrong per the artifact's auction history (full 50 GWh awarded Mar 2022 incl. Hyundai 20; Hyundai withdrew; Sep 2024 re-auction awarded only 10). | **Blocker** | Change to "10 GWh still unawarded after Hyundai's exit" or "10 GWh unallocated today" — one word fixes it, but it sits in the hero stat. |
| 3 | "Rajesh Exports' vehicle" states the ACC Energy Storage identity as fact; the artifact never equates the two explicitly. | Should-fix | "ACC Energy Storage — the entity that won Rajesh Exports' 5 GWh bid" or cite the mapping. Same fix applies to infographic Concept 2. |
| 8 | Headline drops "predominantly" and widens BEV→EV. The artifact's claim is that 75% of Li-ion batteries in BEVs come *predominantly* from China. As written it asserts origin, not dominant sourcing. | Should-fix | Restore "predominantly" — the word is load-bearing; without it the claim overstates. |
| 6 | Uses "~178 GWh announced" without the "announced ≠ committed" caveat that the infographic itself flags as mandatory. Announced capacity is a soft number and the slide's contrast ("only meaningful cell production vs 178 GWh") leans on it. | Should-fix | Add three words: "announced — not committed — capacity." |
| 2 | "to anyone who would build gigafactories in India" — the artifact documents that the evaluation criteria in fact *excluded* the two experienced battery makers (Exide, Amara Raja) and favoured new entrants. The slide's phrasing papers over the scheme's most-criticised design choice. | Should-fix | This is a missed depth opportunity, not an error: one clause ("which picked first-time cell makers over Exide and Amara Raja") would carry Interpretation B into the deck. |
| 9 | Headline "The template now exists" asserts Interpretation D as settled. The artifact explicitly notes Ola "may be a special case (furthest along, largest award), not a template." Body hedges; headline doesn't. | Optional | Acceptable as a headline if the body keeps the hedge — it does. Note only. |
| 7 | "At full tilt" carries the full-utilisation caveat, but the derivation assumes a 20 GWh/yr run-rate for all five years against a plant that is at 2.5 GWh installed today. The realized-vs-ceiling gap is the single most likely way the ₹7,240 cr headline over-delivers expectations, and the deck never says so plainly. | Should-fix | One sentence: "That ceiling assumes full utilisation from day one; a realistic ramp pays out far less." The artifact's own Open Question 2 makes exactly this point. |
| 5 | Quote and "not in any analyst model" are verbatim-faithful. Hero stat 21x vs table's 21.5x. | Optional | Align to 21.5x or leave — immaterial. |
| Format | No-CTA rule for standalone: observed. No external links. Self-contained arc (scheme → zero payouts → pivot → economics → dependency → precedent → falsifiable close). | ✓ Pass | — |

## Infographic feedback table

| Concept / section | Issue | Severity | Recommendation |
|---|---|---|---|
| Concept 2 | "Overlay: commissioned capacity to date ~2.5 GWh, all Ola" conflates *installed* (2.5 GWh, Aug 2026, company-stated) with *commissioned* (1.4 GWh, Oct 2025, IEEFA-verified). Commissioning is the scheme's gating event; inflating it in a graphic titled around delivery gaps undercuts the graphic's own thesis. | **Blocker** | Label the sliver "2.5 GWh installed (company-stated), 1.4 GWh independently verified as of Oct 2025" — the two-number sliver is actually a *stronger* visual. |
| Concept 2 | "ACC Energy Storage/Rajesh Exports" identity asserted, matching the carousel's unestablished inference. | Should-fix | Same fix as carousel slide 3. |
| Concept 5 | Market-cap source listed as Trade Brains; the artifact sources the ₹18,236 cr figure in the Fortune India market-reaction row. | Optional | Correct the attribution or cite both. |
| Concept 3 | Derivation handling is exemplary — mandatory footnote, full-utilisation assumption stated, benchmark sourced. | ✓ Pass | Keep the footnote non-negotiable in layout. |
| Concept 1 | All timeline nodes trace to the artifact (May 2021 → Mar 2022 → Hyundai exit → Sep 2024 → Oct 2025 → May 2026 → Aug 2026). The ₹0 counter device is the strongest single idea across both outputs. | ✓ Pass | — |
| "What to avoid" | All four exclusions are correctly reasoned: the 2.92% pop as hero stat would contradict the muted-reaction nuance; no verified Indian cell cost exists for a parity chart; the jobs ratio rests on a speculative model; the ₹15.15 lakh cr SEBI figure is an unresolved allegation. This section shows better judgment than the average inclusion decision. | ✓ Pass | — |
| Verified data table | Every row traces to the artifact with correct dates and sources. The "Needs context" verdicts on the 178 GWh and per-kWh rows are appropriate. | ✓ Pass | — |

---

## Independent gap analysis

1. **Realized-vs-ceiling gap is underweighted on both surfaces.** The ₹7,240 cr ceiling requires ~100 GWh of DVA-verified output over five years. The plant is at 2.5 GWh installed with 6 GWh expected this quarter; the declining-rate design front-loads value into early years Ola will spend ramping. Neither output states the plain conclusion: realized incentives will very likely land far below the ceiling, and the market's +2.9% shrug partly prices exactly that. The carousel's slide 7 caveat ("at full tilt") is too soft. **Should-fix** (this is the strongest single strengthening move available).

2. **Captive demand math is gestured at, not done.** Slide 10 asks whether Ola's vehicle business can "absorb a 20 GWh line" but never sizes captive demand. The artifact supplies deliveries (39,192 vehicles in Q1 FY27) and revenue -45% YoY; even without pack-size arithmetic, stating "captive two-wheeler demand today runs at a small fraction of one GWh per quarter; the line is 20 GWh per year" would make the external-customer dependency concrete. The artifact's Open Question 4 is the deck's best unanswered punch. **Should-fix for carousel depth; optional for infographic.**

3. **The 60% DVA gate vs the import-composition point are never connected.** Slide 8 explains that localisation shifts the import bill upstream (cathode, separator, electrolyte stay imported) — but neither surface notes that Milestone-2 (60% DVA by year five) is precisely what that upstream import dependence threatens. The later-year payouts gate on a localisation level the material chain may not reach inside the window. This is the artifact's Mechanism + Cross-asset sections' sharpest combined insight, and it's missing. **Should-fix.**

4. **Budget-headroom zero-sum goes unmentioned.** Interpretation D notes each extension consumes headroom within the fixed ₹18,100 cr outlay — Ola's ceiling alone is 40% of it. If Reliance gets a parallel extension on 15 GWh (~₹5,430 cr at the same implied rate), the scheme is ~70% committed to two groups with 10 GWh unallocated and no second budget in sight. The infographic verified the 40% figure but no concept uses it. **Optional** — would strengthen Concept 2 or a budget-allocation chip.

5. **Exide/Amara Raja as the scheme's outsiders.** The artifact's cross-asset section flags that the two experienced battery makers are now building *outside* the scheme, competing against subsidised cells for the first time. Neither surface touches it. It's the cleanest second-order trade the story offers. **Optional.**

6. **Counterargument coverage is otherwise good.** The auditor-flagged ₹57 cr reversal (governance smell), the "approval is not disbursement" falsifier (slide 10), and the subsidy-expiry risk (slide 10's "before the window closes") all survive into the outputs. The Rajesh Exports SEBI allegation is handled at the right temperature on both surfaces.

---

## Verdict

**2 blockers, 7 should-fix, 4 optional. Rework required before publication.**

- **Blocker 1 — Carousel slide 1 headline.** "Zero conditions already met" is ambiguous to the point of meaning-inversion and dubious on its most natural reading (commissioning and investment gates appear met; DVA verification is the open gate).
- **Blocker 2 — Carousel slide 9 hero stat.** "10 GWh never allocated" contradicts the artifact's documented auction history (allocated to Hyundai, withdrawn, partially re-tendered).
- **Blocker 3 — Infographic Concept 2 sliver label.** "Commissioned ~2.5 GWh" upgrades a company-stated installed figure into the scheme's gating term; the verified commissioned figure remains 1.4 GWh (Oct 2025).

*(Counted as two blockers for the surfaces: the carousel headline and the hero stat; the infographic label is a third blocker-level fix on its own surface.)*

Everything else is tightening: restore "predominantly" (slide 8), hedge the ACC Energy Storage identity (slide 3 / Concept 2), add "announced ≠ committed" (slide 6), and put the realized-vs-ceiling gap in plain language (slide 7 / Concept 3 footnote already halfway there). The underlying research is strong and the outputs are unusually disciplined about derivation-labelling and exclusion choices — the failures are concentrated in headline compression, which is exactly where a skeptical reader looks first.

**Do not rewrite from scratch.** All corrections are line-level.
