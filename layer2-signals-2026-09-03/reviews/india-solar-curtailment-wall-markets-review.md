# Markets Review: India's Solar Curtailment Wall — 8,133 GWh Held Back in a Single Quarter

Signal ID: `india-solar-curtailment-wall`
Review date: 2026-09-03
Surfaces reviewed: blog, LinkedIn carousel, Instagram carousel, infographic concepts. No X thread was produced for this signal — noted and skipped.

## Cross-surface consistency

| Issue | Surfaces affected | Severity | Fix |
|---|---|---|---|
| Southern region's zero transmission-driven curtailment is attributed only to "a buildout better synchronised with its grid." The research artifact (Interpretation B) notes the clean record *partly reflects slower RE growth* in the South. Without that caveat the regional split overstates the planning lesson. | Blog (Context), LinkedIn slide 3 | should-fix | Add the slower-buildout caveat in both places. |
| LinkedIn slide 4 calls the ISTS charge waiver expiry a "subsidy expiry." It is a transmission-charge waiver, not a subsidy; loose terminology on the signal's core mechanism. Instagram slide 3 gets this right ("transmission-charge waiver"). | LinkedIn carousel | should-fix | Change "subsidy expiry" to "transmission-charge waiver expiry." |
| All hard numbers (8,133 GWh split, 270.82 GW peak, 470/300 GWh Q1, 50.9/28.7 GW, TRAS 15.76/80.5 GWh, ₹3.8/₹4.4, 14.7/40.2/47 GW, 45 GW stalled, -65.8%/$3.37 bn, ₹7.1 trn discom debt, 3–4 GW BESS, <2 GWh operational, ₹7–8 vs ₹9–10) match the research artifact on every surface. | — | — | No action. |
| Session-level RTM price shape (near-zero solar hours, ₹10 cap post-sunset) is correctly labelled as "several summer sessions" on all surfaces, not presented as an average. Compliant with the artifact's caution. | all | — | No action. |
| IEEFA -65.8% investment decline carries the high-base caveat on blog and LinkedIn ("off a high base"). Instagram omits the figure entirely. Consistent. | — | — | No action. |

## Blog feedback

| Location | Issue | Severity | Fix |
|---|---|---|---|
| Interpretation spectrum, Reading two | "grid-enhancing technologies like dynamic line rating (which can lift corridor capacity 25–50% within one to three years)" — the 25–50% / 1–3-year quantification is NOT in the research artifact and traces to no listed source. SEBI rule 9 (every number traces to a source) violation risk. | blocker | Remove the parenthetical quantification; keep "grid-enhancing technologies like dynamic line rating." |
| Context section, Ember regional split | Southern zero attributed solely to synchronisation; artifact's Interpretation B caveat (slower southern buildout) missing. | should-fix | Add "partly because its buildout ran slower" or equivalent. |
| Disclosure line | "Educational content from Koti Labs (SEBI RIA INA000021951). Not investment advice — no buy/sell recommendation." Present at top, verbatim strings intact. | — | Compliant. Do not touch. |
| Signal/deviation section | "First, openness… Second, the paradox of simultaneity… Third, the inversion of the constraint" — substantive, correctly labelled as interpretation. Fine. | — | No action. |
| "What this does not affect" | Correctly covers the cause-breakdown unknown (transmission vs local oversupply), no-advice boundary, and the 500 GW target. Strong. | — | Leave alone. |
| Bias note | Aagman structural-bias note is present, labelled, and explicitly subordinated to the data. Compliant with SEBI rule 11. | — | Leave alone. |
| Implications section | Mentions ReNew as a named, dated, attributed example with a CEO quote — neutral educational use, no buy/sell framing. Compliant. | — | No action. |
| Length | Operator flag says ~100 words over the 1,800w target; raw file is 3,185 words total (~2,624 prose words excluding sources/data tables). Published Layer 2 finals in `final/` run 2,600–3,000 prose words by the same measure, so the 1,800w target presumably uses a narrower body-only count. De-AI + tightening pass will cut 150–250 words; it cannot reach 1,800 raw prose without deleting content beats. Operator should confirm which measure governs. | should-fix (process) | Trim in de-AI pass; flag measurement discrepancy to operator. |

## Carousel feedback (LinkedIn)

| Location | Issue | Severity | Fix |
|---|---|---|---|
| Slide 3 | Southern zero without slower-buildout caveat (see cross-surface table). | should-fix | Append caveat to body. |
| Slide 4 | "subsidy expiry" — wrong term for the ISTS charge waiver. | should-fix | Reword to "transmission-charge waiver." |
| Slide 5 | Headline "This isn't an energy shortage. It's a delivery shortage." is a "not X but Y" scaffold; also the slide's speaker note openly describes it as such. Factually fine; flagged for the de-AI pass, not a factual issue. | optional | Restate positively in de-AI pass. |
| Slide 10 | Single Substack CTA on final slide — permitted for a promo carousel. Open-question framing preserved. | — | Compliant. |
| All slides | Every number matches the research artifact; hero stats carry source attributions; session-level RTM label intact. | — | No action. |

## Carousel feedback (Instagram)

| Location | Issue | Severity | Fix |
|---|---|---|---|
| Slide 4 | Same "This isn't an energy shortage. It's a delivery shortage." construction as LinkedIn slide 5. | optional | Restate positively in de-AI pass. |
| All slides | Numbers match the artifact; attributions present; no unsupported claims. Slide 3 correctly says "transmission-charge waiver." | — | Clean. |

## Thread feedback

No thread was produced for this signal. Skipped.

## Infographic feedback

| Location | Issue | Severity | Fix |
|---|---|---|---|
| Whole file | Data-verdict table is rigorous: correctly flags the Bloomberg 12 GW / 7%-of-fleet figure as do-not-visualise, rejects the EcoNiti "one full week" equivalence, insists on the IEEFA high-base caveat and the session-level RTM label, and requires the South-slower-buildout footnote in Concept 3. Consistent with the artifact and the other surfaces. | — | Leave alone per operator directive. |

## Independent gaps

- **Gap:** The gas-import displacement angle (Ember: curtailed clean generation could have cut costly gas imports while spot gas ran ~2x pre-war levels) is unused on every surface.
  - Why it matters: It is the cleanest link from curtailment to the macro/FX layer and gives the "what it costs the country" frame a second number.
  - Suggested addition or correction: Optional one clause in the blog's implications section. Not added — the blog is already over its word target.
  - Severity: optional.
- **Gap:** Coal repositioning (PLF ~65–66% in FY26; draft NEP 2026 reframes coal as flexibility/reserves; 6 GW thermal expected in FY27) is unused.
  - Why it matters: It complicates the "solar vs wires" frame with the grid's actual balancing plan.
  - Suggested addition or correction: Optional. The blog's NEP paragraph could carry one clause. Left out for length.
  - Severity: optional.
- **Gap:** The partially verified Bloomberg figures (~12 GW / ~7% of fleet unable to run at full output; ~21 GW on T-GNA) are omitted everywhere.
  - Why it matters: This is the correct call — the research artifact flags them as reported-but-unverified at primary level, and the infographic file explicitly bars visualising them.
  - Suggested addition or correction: None. Omission confirmed as right.
  - Severity: none.

## Verdict

Corrections required — 1 blocker (unsourced dynamic-line-rating quantification in blog Reading two) and 2 should-fix items (Southern-zero caveat on blog + LinkedIn; "subsidy" misnomer on LinkedIn slide 4). All mandatory SEBI elements verified intact: Koti Labs / INA000021951 disclosure present, no buy/sell calls, no price targets, no return promises, bias labelled, open-question endings, promo CTAs correctly scoped to the last slide.
