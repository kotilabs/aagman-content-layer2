# Infographic Concepts: Ola Electric's ₹7,240 Crore PLI Unlock and India's EV Battery Sector

**Signal:** signal-ola-electric-pli-ev-battery
**Source:** research/signal-ola-electric-pli-ev-battery.md
**Date:** 2026-08-12

---

## Verified interesting data

| Data point | What it shows | Source | Verdict |
|---|---|---|---|
| ₹7,240 crore ceiling, 5-yr quarterly window to CY2031, for a 20 GWh award | The first real unlock in the ACC PLI scheme | Moneycontrol / BSE filing, Aug 12, 2026 | Strong |
| ₹0 disbursed vs ₹5,180 crore invested (all beneficiaries, as of May 31, 2026) | Five years in, the scheme had paid nothing | Lok Sabha written reply via YoMobility, Jul 21–22, 2026 | Strong |
| 1.4 GWh commissioned vs 50 GWh target (2.8%) as of Oct 2025 — all of it Ola | The delivery gap; Ola is the entire commissioned base | IEEFA/JMK, Jan 22, 2026 | Strong |
| ~1.4 GWh commissioned vs ~178 GWh announced capacity nationwide (early 2026) | Announcements vs reality across the sector | IMARC, May 14, 2026 | Strong — needs "announced ≠ committed" context |
| Allocations: Ola 20 / Reliance 10+5 / ACC Energy Storage 5 (apparently Rajesh Exports' vehicle — implied by the bid record, not officially stated) / unallocated 10 | The entire 50 GWh scheme map in four bars | Lok Sabha reply via YoMobility, Jul 2026 | Strong — ACC Energy Storage identity needs hedging |
| ~100% cell import dependence; 75% of BEV batteries in India predominantly Chinese; import bill 8x from $384mn | The strategic problem the scheme addresses | IEEFA, May 29, 2026; IEEFA/JMK, Jan 2026 | Strong |
| ₹7,240 crore ≈ ₹0.72/Wh ≈ $8–9/kWh at full 20 GWh utilisation over 5 years (~15% of ~$55/kWh LFP price) | Translates the headline into unit economics | Derived from ceiling + allocation; benchmark per AGAIC Power, Jul 15, 2026 | Needs context — derived arithmetic, must be labelled |
| Scheme mechanics: 25% DVA in 2 yrs → 60% in 5 yrs; ₹225 crore/GWh min investment; 0.1%/day delay penalty; per-kWh subsidy declining over 5 years | Why payouts are gated and why everyone missed | Scheme rules via worldtradescanner summary; JMK/IEEFA | Strong for a mechanism panel |
| Timeline: May 2021 approval → Mar 2022 auction (full 50 GWh incl. Hyundai 20) → Hyundai exit → Sep 2024 re-auction (10 GWh) → Oct 2025: 1.4 GWh built → Jun 2026: Rajesh Exports SEBI cloud → Aug 12, 2026: Ola extension | Five years of slippage ending in the first unlock | Mercom 2022; IEEFA/JMK; evelectree Jun 2026; Moneycontrol Aug 2026 | Strong |
| Ola Q1 FY27: loss ₹336 cr, revenue -45% YoY to ₹455 cr; ceiling ≈ 21x quarterly loss | Why the PLI re-rates the cell subsidiary relative to a shrinking EV business | StartupTalky/CNBCTV18, Aug 7, 2026 | Strong |
| ₹57 crore liquidated-damages provision reversed pre-approval, auditor-flagged | The penalty overhang the extension erased | Outlook Business, Aug 10, 2026 | Good supporting detail |
| Scheme budget: ₹18,100 crore; Ola ceiling = 40% of it | Concentration of the scheme on one firm | JMK/IEEFA + derived | Strong |

---

## Recommended concepts

### Concept 1: "The Scheme That Paid Nothing" — timeline-to-zero infographic
- **Central insight:** Five years after approval, India's flagship battery scheme had disbursed ₹0 — and the Ola extension is the first event that could change the zero.
- **Data:** May 2021 approval (₹18,100 cr outlay) → Mar 2022 auction of full 50 GWh → Hyundai 20 GWh exit → Sep 2024 re-auction (only 10 GWh) → Oct 2025: 1.4 GWh commissioned (2.8%) → May 2026: ₹5,180 cr invested, 1,277 jobs, ₹0 claimed → Aug 12, 2026: Ola's ₹7,240 cr window opened, first disbursement due Q3 FY27.
- **Visualization type:** Horizontal timeline with a "claims paid" counter fixed at ₹0 running beneath it, flipping to a question mark at the Aug 2026 node.
- **Composition notes:** Reader enters at the outlay figure (₹18,100 cr) top-left; the eye walks the slippage milestones left to right; the ₹0 counter is the constant ribbon at the bottom; payoff is the final node in a contrasting colour — the only forward-looking event on the line.
- **Sources:** JMK/IEEFA (Jan 2026), Mercom (Mar 2022), YoMobility/Lok Sabha reply (Jul 2026), Moneycontrol (Aug 12, 2026).
- **Generation prompt (Aagman design language):** White-background institutional infographic. Bold near-black headline "The Scheme That Paid Nothing" with charcoal subhead "Five years after approval, India's flagship battery PLI had disbursed ₹0 — until the Ola extension." Layout: horizontal timeline across the full width, read left to right. Nodes: May 2021 approval (₹18,100 cr outlay, mint `#56E8B8`), Mar 2022 auction of 50 GWh (teal `#6FE6CD`), Hyundai 20 GWh exit (amber `#F59E0B`), Sep 2024 re-auction 10 GWh, Oct 2025 1.4 GWh commissioned (2.8%), May 2026 ₹5,180 cr invested / ₹0 claimed, Aug 12 2026 Ola's ₹7,240 cr window opened (sky `#67C7F1`, largest node). A constant ribbon beneath the timeline shows "Incentives paid: ₹0" until the final node, where it flips to a question mark. Floating annotation boxes in soft mint background (`#E7EEEA`) at the Oct 2025 and Aug 2026 nodes. Two-column footer: left "Five years, ₹5,180 cr invested, zero disbursements.", right "Ola's extension is the first event that could change the zero." Source line: "Sources: JMK/IEEFA, Mercom, YoMobility/Lok Sabha, Moneycontrol." No clutter, no stock-price noise.

### Concept 2: "Who Holds India's 50 GWh" — allocation bar map
- **Central insight:** India's entire planned cell capacity sits with three groups — 40% of it with a company that missed its first deadlines and just got rescued.
- **Data:** Ola 20 GWh (Tamil Nadu); Reliance 10 + 5 GWh (Gujarat; first-round 5 delayed); ACC Energy Storage 5 GWh (Karnataka; apparently Rajesh Exports' vehicle — implied by the bid record; under MHI review post-SEBI order); unallocated 10 GWh. Overlay: 2.5 GWh installed to date (company-stated, Aug 2026), of which 1.4 GWh independently verified as commissioned (IEEFA/JMK, Oct 2025) — all of it Ola.
- **Visualization type:** Single stacked 50 GWh bar segmented by beneficiary, with a thin "actually built" sliver bar beneath for contrast — the sliver itself split into installed (2.5 GWh, company-stated) and verified-commissioned (1.4 GWh) segments; status flags (delayed / under review / not tendered) as annotation chips.
- **Composition notes:** The 50 GWh bar dominates; the two-number sliver underneath — 2.5 GWh installed vs 1.4 GWh verified — is the visual gut-punch, and the split is honest: commissioning is the scheme's gating event, so the label must not inflate it. Colour-coding by status rather than by company keeps the reader on the risk structure, not the logos.
- **Sources:** YoMobility/Lok Sabha reply (Jul 2026), IEEFA/JMK (Jan 2026), Moneycontrol (Aug 12, 2026), evelectree (Jun 2026).
- **Generation prompt (Aagman design language):** White-background institutional infographic. Bold near-black headline "Who Holds India's 50 GWh" with charcoal subhead "The entire planned cell capacity sits with three groups — 40% of it with a company that missed its first deadlines." Layout: one large stacked horizontal bar totaling 50 GWh, segmented by beneficiary: Ola 20 GWh in mint (`#56E8B8`), Reliance 15 GWh in teal (`#6FE6CD`), ACC Energy Storage 5 GWh in sky (`#67C7F1`), unallocated 10 GWh in light grey (`#8A938E`). Status annotation chips in soft mint background (`#E7EEEA`): Ola "rescued clock", Reliance "delayed", ACC "under MHI review". Below the main bar, a thin contrasting sliver bar: 2.5 GWh installed (company-stated) vs 1.4 GWh verified commissioned, all Ola. Two-column footer: left "Ola holds 40% of the scheme; its extension resets the clock.", right "Commissioned: 1.4 GWh of 50 GWh target (2.8%)." Source line: "Sources: YoMobility/Lok Sabha, IEEFA/JMK, Moneycontrol, evelectree." No company logos, no inflated installed numbers.

### Concept 3: "What ₹7,240 Crore Buys Per kWh" — unit-economics bridge
- **Central insight:** The ceiling is not a cheque — at full utilisation it is roughly $8–9/kWh of support, about 15% of the Chinese LFP price it must compete with.
- **Data:** ₹7,240 cr ceiling ÷ (20 GWh/yr × 5 yrs ≈ 100 GWh) ≈ ₹0.72/Wh ≈ $8.6/kWh; LFP benchmark ~$55/kWh; implied support ~15% of sales value; scheme design: per-kWh subsidy × DVA %, declining over five years; DVA gates 25% → 60%.
- **Visualization type:** Bridge/waterfall from "₹7,240 crore ceiling" to "per-kWh support," side-by-side with a simple bar comparing Chinese LFP price vs supported Indian cost position; a footnote strip stating this is derived arithmetic at full utilisation — and that the ceiling assumes full utilisation from day one against a plant at 2.5 GWh installed today, so realized incentives will very likely land far below ₹7,240 crore as Ola ramps through the scheme's declining-rate years.
- **Composition notes:** Left panel converts the crore headline step by step (crore → per-GWh → per-kWh); right panel anchors it against the import price. The derivation footnote is mandatory, not optional — this is the one number in the set that is computed, not sourced.
- **Sources:** Moneycontrol (ceiling, Aug 12, 2026); AGAIC Power tender analysis (benchmark, Jul 15, 2026); scheme rules via JMK/IEEFA.
- **Generation prompt (Aagman design language):** White-background institutional infographic. Bold near-black headline "What ₹7,240 Crore Buys Per kWh" with charcoal subhead "At full utilisation, the ceiling is roughly $8–9/kWh — about 15% of the Chinese LFP price it must compete with." Layout: two-panel bridge. Left panel: step-down conversion from ₹7,240 cr → per-GWh → per-kWh (`₹0.72/Wh ≈ $8.6/kWh`) in mint (`#56E8B8`) and teal (`#6FE6CD`) blocks. Right panel: side-by-side bar comparing Chinese LFP benchmark ~$55/kWh (light grey `#8A938E`) vs supported Indian cost position ~$46–47/kWh (mint `#56E8B8`). A mandatory footnote strip below in grey (`#6F7873`) states the derivation and the caveat: "Assumes full utilisation from day one; realised incentives will likely land far below ₹7,240 cr as Ola ramps through declining-rate years." Two-column footer: left "Ceiling is not a cheque; it is a per-kWh support at full output.", right "DVA gates: 25% in 2 yrs → 60% in 5 yrs." Source line: "Sources: Moneycontrol, AGAIC Power, JMK/IEEFA." No gradients, no parity claims beyond the labelled support.

### Concept 4: "China Dependency vs Domestic Build" — divergence graphic
- **Central insight:** India's battery import bill grew eightfold while its commissioned domestic cell capacity reached 2.8% of target — the PLI is an attempt to bend that divergence.
- **Data:** Import bill 8x from $384mn (IEEFA); 75% of BEV batteries in India predominantly Chinese; ~100% cell import dependence; 1.4 GWh built vs ~178 GWh announced; 20 GWh Ola line vs India's EV cell demand trajectory. Annotation: localisation shifts the import bill upstream (cathode, separator, electrolyte stay imported) — and that upstream dependence directly threatens Milestone-2, the 60% DVA gate on later-year payouts.
- **Visualization type:** Two-line divergence (import dependence/bill rising vs commissioned domestic capacity near zero) with the announced-capacity cloud shown as a faded "promise zone" and a small gate marker on the timeline where the 60% DVA requirement bites.
- **Composition notes:** The reader should see one line climbing and one flatlining; the faded announced-capacity band above the flat line communicates the announcement-reality gap without a single adjective.
- **Sources:** IEEFA (May 29, 2026), IEEFA/JMK (Jan 22, 2026), IMARC (May 14, 2026).
- **Generation prompt (Aagman design language):** White-background institutional infographic. Bold near-black headline "China Dependency vs Domestic Build" with charcoal subhead "Battery imports grew eightfold while commissioned domestic cell capacity reached 2.8% of target." Layout: two-line divergence chart. One line (amber `#F59E0B`) climbing steeply: battery import bill 8× from $384mn, 75% of BEV batteries predominantly Chinese, ~100% cell import dependence. Second line (mint `#56E8B8`) flat near zero: 1.4 GWh commissioned vs 50 GWh target, ~178 GWh announced capacity shown as a faded "promise zone" band above the flat line. A small gate marker on the timeline where 60% DVA requirement bites, in sky (`#67C7F1`). Floating annotation in soft mint background (`#E7EEEA`): "Localisation may shift the import bill upstream to cathode, separator, electrolyte — threatening the 60% DVA gate." Two-column footer: left "Imports climbed; domestic build flatlined.", right "The PLI is an attempt to bend the divergence." Source line: "Sources: IEEFA, JMK/IEEFA, IMARC." No adjectives, the gap speaks for itself.

### Concept 5: "The Penalty That Became a Paycheck" — mechanism explainer panel
- **Central insight:** Ola was accruing delay penalties (0.1% of performance security per day) on a missed milestone; the revision converted that liability into a full five-year incentive window.
- **Data:** ₹57 cr liquidated-damages provision reversed (auditor-flagged); penalty rate 0.1%/day; original vs revised timeline (2-year extension); quarterly disbursement start Q3 FY27; ceiling ₹7,240 cr vs market cap ~₹18,236 cr (~40%).
- **Visualization type:** Before/after ledger-style panel — left column "before Aug 12" (penalties accruing, provision reversed under auditor protest, PLI excluded from projections), right column "after" (penalty overhang waived, 20 quarterly payments scheduled, ₹7,240 cr ceiling).
- **Composition notes:** Two-column accounting layout suits the FT-ledger voice; the ceiling-vs-market-cap ratio chip is the anchor stat at the bottom.
- **Sources:** Outlook Business (Aug 10, 2026), Fortune India (Aug 12, 2026 — quote and market cap), scheme rules via JMK/IEEFA.
- **Generation prompt (Aagman design language):** White-background institutional infographic in a ledger/accounting style. Bold near-black headline "The Penalty That Became a Paycheck" with charcoal subhead "Ola was accruing delay penalties; the revision converted that liability into a five-year incentive window." Layout: two-column before/after panel. Left column (muted grey): "Before Aug 12" — penalties accruing at 0.1%/day, ₹57 cr liquidated-damages provision reversed under auditor protest, PLI excluded from projections. Right column (mint `#56E8B8` and teal `#6FE6CD`): "After Aug 12" — penalty overhang waived, 20 quarterly payments scheduled, ₹7,240 cr ceiling. A horizontal divider separates the two. Bottom anchor chip in soft mint background (`#E7EEEA`): "Ceiling ₹7,240 cr vs market cap ~₹18,236 cr (~40%)." Two-column footer: left "The extension erased a penalty overhang and replaced it with a payment schedule.", right "First disbursement due Q3 FY27." Source line: "Sources: Outlook Business, Fortune India, JMK/IEEFA." No stock-price chart, no speculation beyond the ledger.

---

## What to avoid

- **"Ola stock pops 3%" as a hero visual.** A 2.92% intraday move is market noise, not structure; using it as a lead stat overstates the re-rating and contradicts the muted-reaction nuance. Dropped.
- **India-vs-China cell cost parity charts.** No verified Indian cell cost/kWh exists (Ola's costs are undisclosed); any parity line would be invented. Only the support-vs-benchmark framing of Concept 3 is defensible, and only with the derivation labelled.
- **Jobs-created visual.** 1,118–1,277 jobs vs a 1.03 million estimate is a real number but rests on a speculative jobs model in the JMK/IEEFA report; the ratio invites misreading. Noted for monitoring, not visualized.
- **₹15.15 lakh crore SEBI allegation figure for Rajesh Exports.** Extraordinary number from an interim order under dispute; including it in a graphic would dominate the layout and import an unresolved legal claim. Referenced only as "under MHI review" in Concept 2.

---

## Final recommendation

Proceed with **Concept 1 (timeline-to-zero)** as the primary graphic and **Concept 2 (allocation bar map)** as a companion panel — together they tell the full story: a scheme that paid nothing for five years, whose entire capacity sits with three groups, 40% of it now on a rescued clock. Concept 3 is a strong third if space allows, provided the derived per-kWh figure carries its methodology footnote. Concepts 4 and 5 are alternates; 4 risks redundancy with 1+2, 5 is better suited to a text-led carousel than a data graphic.

**Hero stats for layout:**
- ₹7,240 crore — five-year PLI ceiling, first disbursement due Oct–Dec 2026
- ₹0 — incentives paid under the scheme since May 2021 (vs ₹5,180 crore invested)
- 1.4 GWh of 50 GWh — commissioned capacity vs target as of Oct 2025, all of it Ola's
- ~$8–9/kWh — implied support at full utilisation, ≈15% of the ~$55/kWh Chinese LFP benchmark (derived)
