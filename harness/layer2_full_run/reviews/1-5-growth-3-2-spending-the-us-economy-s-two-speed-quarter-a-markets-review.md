**Markets Review: — "1.5% Growth, 3.2% Spending: The US Economy's Two-Speed Quarter and What It Does to Earnings Quality"**

Signal ID: `1-5-growth-3-2-spending-the-us-economy-s-two-speed-quarter-a` · Review date: 2026-08-18
Surfaces produced: infographic concepts only. Blog, carousels (LinkedIn/Instagram), and thread were not produced for this signal — noted and skipped.

## Cross-surface consistency

| Issue | Surfaces affected | Severity | Fix |
|---|---|---|---|
| Only one surface exists, so no cross-surface contradiction is possible; checked the concepts file against the research artifact claim-by-claim instead. Arithmetic verified: 2.12 + 1.20 − 0.67 − 1.01 − 0.14 = 1.50 (matches headline); 0.67 + 1.01 + 0.14 = 1.82 (matches "combined 1.82 pts"); 2.12 / 0.37 ≈ 5.7x (matches "5.7x swing"); June services/goods $58.2B / $7.0B ≈ 8.3:1 (matches "8:1 in June dollars"). No claim in the concepts file exceeds or contradicts the research artifact. | infographic | nit | None required. |
| The 3.2% real PCE figure is a signal-record number not directly re-read from NIPA Table 1.1.1 (research artifact flags this explicitly). The concepts file carries the qualifier in every instance and in the final recommendation. | infographic | nit | Keep the on-graphic qualifier exactly as drafted: "signal record; consistent with the published +2.12 pt contribution (BEA NIPA 1.1.2)." Do not let a designer shorten it to a bare "3.2%". |

## Blog Feedback

Not produced — skipped.

## Carousel Feedback (LinkedIn)

Not produced — skipped.

## Carousel Feedback (Instagram)

Not produced — skipped.

## Thread Feedback

Not produced — skipped.

## Infographic Feedback

Claim-vs-data alignment lens applied. Every visualized number in all five concepts traces to the research artifact's source list; no concept visualizes a number the artifact does not contain.

| Location | Issue | Severity | Fix |
|---|---|---|---|
| Concept 1 ("Where the 1.5% Hides"), data line and composition | The buildout (+1.28 pts) is presented as a sub-bar of fixed investment (+1.20 pts), but the component exceeds its parent — because nonresidential structures subtracted within fixed investment. A waterfall reader will see +1.28 inside +1.20 as an internal inconsistency. | should-fix | Add a footnote or sub-decomposition tick on the investment bar: "equipment + IPP +1.28; structures negative; net fixed investment +1.20." Without it the strongest concept looks arithmetically wrong. |
| Concept 1 and Concept 5, source attribution | All NIPA 1.1.2 contribution numbers (the spine of both concepts) are sourced to "BEA NIPA 1.1.2 via Phoebe Reads." Phoebe Reads is a secondary aggregator; BEA's interactive table is the primary source. On a published graphic, "via Phoebe Reads" reads as sourcing a blog for government statistics. | should-fix | Attribute on-graphic to "BEA, NIPA Table 1.1.2 (advance estimate, July 30, 2026)"; Phoebe Reads belongs in the production notes as the retrieval conduit. Before publication, pull the contribution lines directly from BEA's interactive data app to convert secondary into primary sourcing. |
| Concept 2 ("Two Speedometers"), composition | The concept uses both the 1.7% → 3.9% acceleration (a 2.2-pt move) and the "2.4-pt private-demand gap" (3.9% final sales vs 1.5% headline). Two different deltas near each other on one graphic invites misreading. | nit | Label each delta explicitly: needle move = 2.2 pts Q1→Q2; gap callout = 2.4 pts between the two gauges. Do not merge. |
| Concept 2, FOMC vote bar | The 9–3 vote and dissenters' names trace to PaySpace Magazine, a secondary outlet, not the FOMC statement. The reviewer's independent check found consistent reporting of a contested July hold, but the graphic states names and vote count as hard fact. | should-fix | Verify against the FOMC statement/press materials at federalreserve.gov before drawing the vote bar. If not verifiable at production time, drop the vote bar; the speedometer divergence stands alone without it. |
| Concept 4 ("1.5% GDP, 15% Revenue"), central insight | The phrase sector revenue lines "read directly off the GDP components that grew" is stronger than the evidence. FactSet reports the sector leaderboard; it does not attribute Energy's revenue lead to petroleum exports. The research artifact's own open question #5 asks how much of Energy's resilience is volume versus price/geopolitics. The wire from "petroleum exports" to "Energy revenue" is an interpretation, not a data line. | should-fix | Change the wiring language from "read directly off" to "map onto," and mark the petroleum-exports→Energy wire as interpretive (dashed line or labeled inference) while consumer→consumer-services and buildout→IT/Comm Services stay solid. This keeps the graphic inside the research artifact's epistemic lines. |
| Concept 4, "honesty ribbon" (50.4% → 32.0%) | Good instinct, correctly sourced to FactSet. One refinement: the ribbon should also note the 86% beat rate is measured against estimates, not against the economy — an expectations metric, not a macro metric. | nit | Add three words: "86% beat analyst estimates." Prevents a reader treating beat rate as economic strength. |
| Concept 3 ("The 3.2% Is Real. So Is the 2.7%."), title and payoff | The tension framing is right and avoids the "resilient consumer" trap the brief warns against. The June 2022 reference tick needs its own source note (lowest since June 2022 per Phoebe Reads reading the BEA full series to 1959). | nit | Cite the "lowest since June 2022" claim inline; it is the one comparative-superlative on the graphic and superlatives draw fact-checks. |
| All concepts, general | No concept states that Q2 is an advance estimate subject to revision on August 26 and an annual history rewrite on September 30. Concept 5 mentions watching the revision, but the caveat belongs on every graphic that draws the 1.5% decomposition. | should-fix | Add a standard corner strip to Concepts 1, 2, and 5: "Advance estimate; second estimate Aug 26, 2026; annual revision Sep 30, 2026." This is disclosure-ready framing, not decoration. |
| What-to-avoid section | Correctly rejects the 6.25% deflator lead, the index-record standalone, the celebratory consumer, and FOMC drama. This section is doing real gatekeeping work and matches the reviewer's own read. | nit | None. |

## Independent gaps

- **Gap:** The tariff front-running / unwind hypothesis (research interpretation D) is visually invisible. The concepts rate inventories and trade as "low-information, reverses" — but if the wholesale inventory drawdown and the capital-goods import surge are tariff timing rather than cycle noise, the half-life ratings in Concepts 1 and 5 are wrong in the direction of complacency.
  - Why it matters: the entire editorial value of the decomposition is the half-life ranking; a tariff-timing driver would invert it (inventory restock may not come if tariffs were the reason for the pre-build).
  - Suggested addition or correction: on Concept 5's matrix, add a third axis marker or asterisk on inventories and net exports: "persistence rating assumes non-tariff driver; tariff-timing unwind would extend the drag." One line, keeps the concept honest.
  - Severity: should-fix
- **Gap:** No concept engages the possibility that the August 26 revision moves the consumer contribution itself. Advance-estimate PCE is built partly on judgmental trends (the BEA notes this for IPP; retail survey data underpins goods). The 5.7x contribution swing is the most quoted number in the set and the most revision-exposed.
  - Why it matters: if the second estimate trims PCE, every concept's central insight survives (the divergence is large) but the specific bars move; a graphic without the revision strip ages badly in eight days.
  - Suggested addition or correction: covered by the revision-caveat strip above; additionally, keep bar labels in "pts" rather than redrawing percentages so a revision update is a re-label, not a redesign.
  - Severity: nit (subsumed by the should-fix revision strip)
- **Gap:** The upper-income / asset-funded spending channel (research interpretation B's counter-evidence — dividend and interest income both rose in June) appears nowhere in the concepts. Concept 3 frames the funding gap as drawdown-only.
  - Why it matters: the strongest counter to the exhaustion reading is that asset income, not just saving, funds upper-income spending; without it, Concept 3 leans slightly harder bearish than the research artifact.
  - Suggested addition or correction: one sidebar line in Concept 3: "June income growth was led by compensation *and* asset receipts (dividends, interest) — the funding mix is not drawdown alone." Keeps the tension honest in both directions.
  - Severity: nit
- **Gap checked and dismissed:** the "AMINA retrospective" and "veloxmacro weekly" references in the signal record could not be verified and appear in no concept — correct handling, no action.

## Verdict

Clean — ready for SEO audit / human approval. No blockers. Five should-fix items and five nits on the infographic surface, all compositional or attribution-level; none changes the data, the decomposition, or the editorial spine. The concepts file is factually consistent with the research artifact, the arithmetic checks out line by line, and the claim-vs-data alignment the infographic surface is judged on holds. The should-fix items (buildout-vs-parent footnote, BEA-primary attribution, FOMC vote verification, Energy-wire softening, revision-caveat strip) should be applied at design/production time rather than requiring a rewrite cycle.