# Infographic Concept: US Household Debt — The Deleveraging Illusion

**Signal ID:** us-household-debt-consumer  
**Date:** 2026-08-12  
**Research source:** `harness/layer2_full_run/research/signal-us-household-debt-consumer.md`

## Verified interesting data

| Data point | What it shows | Source | Verdict |
|---|---|---|---|
| Total household debt fell $13B (−0.1%) to $18.771T in Q2 2026 | First quarterly decline since Q2 2020 — the headline everyone will quote. | NY Fed, Q2 2026 Quarterly Report, 11 Aug 2026 | Strong |
| Annual change is +$383B (Q2 2025 → Q2 2026) | The "decline" is a quarterly dent inside an ongoing annual expansion. | NY Fed, 11 Aug 2026 | Strong |
| Mortgages fell $74B to $13.117T | The entire decline — and then some — comes from the cheapest debt on the balance sheet. | NY Fed, 11 Aug 2026 | Strong |
| Credit cards rose $21B to $1.263T (series record; +$54B y/y) | The most expensive mainstream credit is at an all-time high. | NY Fed, 11 Aug 2026 | Strong |
| Auto loans rose $28B to $1.713T (series record; +$58B y/y) | Second record, second-most-expensive category. | NY Fed, 11 Aug 2026 | Strong |
| Student loans fell $7B to $1.651T | Shrinking balance masks a default wave — 3.6M new defaults since Q4 2025. | NY Fed, 11 Aug 2026; NY Fed May 2026 report | Strong |
| HELOC balances +$13B to $459B; +$142B above the Q1 2022 low | Rate-locked owners are tapping equity instead of refinancing; whether draws fund consumption, renovation, or consolidation is unknown. | NY Fed, 11 Aug 2026 | Strong |
| 30-yr fixed mortgage at 6.69% (week ending 6 Aug 2026), highest in over a year | Why no one refinances: lock-in is rational. | Freddie Mac PMMS | Strong |
| Credit card APR 20.94% all accounts / ~22.15% assessed-interest accounts (May 2026, G.19) | The price of the debt that is *growing*. | Fed G.19 / FRED | Strong |
| Auto 48-month new-car rate 7.36% (Feb 2026, G.19) | The price of the second-growing category. | Fed G.19 | Strong |
| Aggregate delinquency 4.7%, improved slightly | The benign headline the bulls will cite. | NY Fed, 11 Aug 2026 | Strong |
| Card 90+ stock delinquency 12.8% (Q1 2026) vs flow stable since 2024 | The alarmist number is a reporting artifact — charged-off debt now lingers on bureau files (80% still reported after 1 year vs ~40% in 2004–2012). | Liberty Street Economics, 11 Aug 2026 | Strong |
| 23M Americans carry charged-off card balances on their credit reports | A slow, quiet tightening of credit access at the bottom of the distribution. | Liberty Street Economics, 11 Aug 2026 | Strong |
| Q2 2020's decline (−$34B) was driven by cards falling $76B | The mirror image: then, expensive debt fell; now, expensive debt leads. | NY Fed, 6 Aug 2020 | Strong |
| Fed held 3.50%–3.75% in July with 3 hawkish dissents | The policy debate this print lands in. | FOMC, 28–29 July 2026 | Strong |
| Serious-delinquency flows: cards 6.97%, auto 3.00%, mortgages 1.52% (up from 1.29%) | New stress is elevated but flat — except mortgages, creeping up. | NY Fed, 11 Aug 2026 | Strong (mortgage move needs one more quarter) |

## Recommended concept

### Concept (selected): "Same Headline, Opposite Household"

- **Central insight:** Two quarterly declines, six years apart, with identical headlines and inverted contents. Q2 2020 fell because households paid off their *most expensive* debt (cards −$76B). Q2 2026 fell because their *cheapest* debt ran off (mortgages −$74B) while expensive debt hit records. The 2020 decline was deleveraging; the 2026 decline is repricing — debt migrating up the rate curve, not off the balance sheet.

- **Hero stats (large type):**
  - **−$13B** — first quarterly decline since 2020 *(the headline)*
  - **+$49B** — new credit-card and auto debt added in the same quarter *(the story)*
  - **20.94%** — average APR on the debt that is growing
  - **~3–4.5% vs 6.69%** — the rate households hold vs the rate the market offers *(mortgage lock-in; qualitative range for legacy rates, 6.69% verified)*

- **Data to include:**
  - Q2 2026 component bars: Mortgages −$74B, Student −$7B, HELOC +$13B, Cards +$21B (record $1.263T), Auto +$28B (record $1.713T), Other +$6B *(labelled on-graphic as "other (residual)" — derived by subtraction from the sourced components to reconcile to the −$13B net; the NY Fed report carries an "other" category but this exact figure is not separately sourced in the research artifact)*. Net: −$13B.
  - Q2 2020 comparison: Cards −$76B drove a −$34B total decline.
  - Rate ladder: mortgage 6.69% (PMMS, 6 Aug 2026) → auto 7.36% (G.19, Feb 2026) → card 20.94% (G.19, May 2026). HELOC is omitted from the ladder ("rate not shown") — no HELOC rate is sourced in the research artifact; in the waterfalls it is colored hot as prime-based revolving credit.
  - Footnote panel: annual change +$383B; aggregate delinquency 4.7% (improved); stock card delinquency 12.8% flagged as reporting artifact per NY Fed; the +$21B Q/Q card move is partly seasonal (Q1 paydown, Q4/Q2 spend-up) — the record claim rests on the level, not the quarterly change.

- **Visualization type:** Paired waterfall charts — one for Q2 2020, one for Q2 2026 — with a shared color code keyed to *borrowing cost*, not category. Cheap debt (mortgage, student) in cool tones; expensive debt (card, auto, HELOC) in hot tones. The 2020 waterfall's hot bar points down; the 2026 waterfall's hot bars point up. Below, a horizontal "rate ladder" strip placing each category's current borrowing cost on a 0–24% axis. Markers are sized by balance, **with the mortgage stock excluded from the sizing scale** (a $13.1T marker would swamp the axis); the mortgage marker is annotated "not to scale — stock $13.1T". **Color-key legend is frame-explicit:** "color = cost of the *existing* debt being repaid vs the *new* debt being added — mortgage/student are colored by the legacy rate on the outstanding stock (mortgage 3–4.5%, qualitative); card/auto/HELOC are colored by the current marginal rate on new borrowing." The two rate frames are never merged silently: a new mortgage at 6.69% costs more than the "cool" mortgage color implies, and the legend says so.

- **Layout (single-column, 3:4 or 4:5 portrait):**
  1. **Header band:** "US household debt just fell for the first time in six years." Subhead: "Look at what fell."
  2. **Left half — Q2 2020 waterfall** (small, muted, labelled "The last decline: −$34B. Credit cards −$76B. Households paid off their most expensive debt.")
  3. **Right half — Q2 2026 waterfall** (dominant, full color, labelled "This decline: −$13B. Mortgages −$74B. Credit cards +$21B (record). Auto +$28B (record).") — the student-loan −$7B bar carries a one-line annotation, "balance down, defaults up: 3.6M new defaults since Q4 2025 (1.0M Q4 2025 + 2.6M Q1 2026 re-reporting)," so it does not render as benign paydown.
  4. **Rate ladder strip** across the lower third: card 20.94% ($1.263T), auto 7.36% ($1.713T), new mortgage 6.69% ($13.1T stock, mostly locked far below; marker not to scale — see sizing rule above). Markers sized by balance among card/auto; auto is the largest marker on the strip. Caption: "The debt that's shrinking is cheap. The debt that's growing costs 21%."
  5. **Footer strip — four caveats in small type:** +$383B year over year; delinquency 4.7% and steady; card limits rose $85B in the quarter — lenders are still extending (the strongest counter to a distress reading); 12.8% card delinquency headline is a reporting artifact (NY Fed).

- **Composition notes:** The asymmetry is the design: 2020 rendered small and grey so 2026 dominates. The waterfall bars must sum visibly to the net — the reader should be able to check the arithmetic (the "other" bar is labelled "other (residual)" to make clear it is the balancing figure, not a sourced value). Hot/cool color logic is explained once in the frame-explicit legend (existing-stock rate for mortgage/student vs current marginal rate for card/auto/HELOC) and then trusted. No pie charts; the argument is about flows and rates, not shares.

- **Source annotations (on-graphic, small type):**
  - "Balance data: Federal Reserve Bank of New York, Quarterly Report on Household Debt and Credit, Q2 2026 (released 11 Aug 2026); Q2 2020 report (6 Aug 2020)."
  - "Rates: Fed G.19 (May 2026 card APR; Feb 2026 auto rate); Freddie Mac PMMS (week ending 6 Aug 2026)."
  - "Delinquency reconciliation: NY Fed Liberty Street Economics, 'How Distressed Are Consumers?', 11 Aug 2026."
- **Generation prompt (Aagman design language):** White-background institutional infographic in a 4:5 portrait ratio. Bold near-black headline at top: "Same Headline, Opposite Household." Charcoal subhead: "Two quarterly declines, six years apart. 2020 paid off expensive debt; 2026 lost cheap debt while expensive debt hit records." Layout: header band, then two side-by-side waterfall charts. Left chart (smaller, muted grey tones): Q2 2020, net −$34B, driven by credit cards −$76B (amber `#F59E0B` bar pointing down). Right chart (dominant, full color): Q2 2026, net −$13B, mortgages −$74B in cool mint (`#56E8B8`) pointing down, credit cards +$21B and auto +$28B in amber (`#F59E0B`) pointing up. Floating annotation on student loans: "−$7B balance, but 3.6M new defaults since Q4 2025". Below the waterfalls, a horizontal rate ladder strip: card 20.94% (largest marker), auto 7.36%, new mortgage 6.69%; mortgage marker annotated "stock $13.1T, not to scale". Two-column footer: left "The debt that's shrinking is cheap; the debt that's growing costs 21%.", right "+$383B year over year; aggregate delinquency 4.7% and steady." Source line at bottom: "Sources: NY Fed, Fed G.19, Freddie Mac PMMS, Liberty Street Economics." No pie charts, no per-household averages, no crisis framing.

## What to avoid

- **"First decline since 2020" as an unqualified hero line.** True and useless — the scout's own framing shows why. If used, it must be immediately subverted by the composition data, as in the layout above.
- **A debt-by-category pie or treemap of levels.** Mortgages are 70% of the total; a levels chart buries the entire story. Flows (q/q changes) are the information.
- **The 12.8% card delinquency number as a standalone scare stat.** The NY Fed published a companion analysis the same day explaining it is driven by stale charged-off reporting, not new distress. Using it raw would be both sloppy and wrong in implication. It belongs only as a footnote with the caveat attached.
- **Claiming households "can't afford" the card debt.** Flow delinquency is stable at ~7%; nothing verified supports a crisis framing. The defensible claim is substitution toward expensive credit, not imminent default.
- **Student loans as a clean "paydown" data point.** The −$7B decline coincides with 3.6M new defaults and delayed collections; presenting it as deleveraging would invert reality.
- **Any per-household average debt figure** (~$141K derived from $18.77T / household count). Household counts are not in the primary source; a derived stat on the hero graphic invites a fact-check the artifact can't win.
- **"The Fed will hike/cut" framing.** The July meeting had three dissents; the data feeds a debate. Show the debate (3.50%–3.75% hold, 3 dissents), not a prediction.

## Final recommendation

Proceed with the single concept above, "Same Headline, Opposite Household." It is fully supported by primary sources (every number traces to the NY Fed report, G.19, or Freddie Mac PMMS), it has a genuine structural insight rather than a chart of the news, and the 2020 mirror-image comparison does the argumentative work that prose would otherwise have to do. The footer caveats keep the graphic honest against both the bullish (delinquency improving) and bearish (record revolving debt) readings — which is the actual finding: the aggregate says deleveraging, the composition says repricing, and both are true.
