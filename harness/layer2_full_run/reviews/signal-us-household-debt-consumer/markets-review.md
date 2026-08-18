# Markets Review — us-household-debt-consumer

**Reviewer:** Aagman Layer 2 Markets Reviewer
**Review date:** 2026-08-12
**Surfaces reviewed:** Infographic concept only (`drafts/signal-us-household-debt-consumer-infographic.md`)
**Surfaces not produced:** blog, thread, carousel — those sections are skipped; the pipeline produced a single surface for this signal.

**Canonical research:** `harness/layer2_full_run/research/signal-us-household-debt-consumer.md`

---

## Pass 1 — Factual integrity

Every headline number in the infographic was checked against the research artifact. Result: all primary figures trace cleanly.

| Claim in infographic | Research artifact | Verdict |
|---|---|---|
| Total debt −$13B (−0.1%) to $18.771T, first decline since Q2 2020 | §2, line 18 — identical | Verified |
| Annual change +$383B | §2, line 28 — identical | Verified |
| Mortgages −$74B to $13.117T | §2, line 20 — identical | Verified |
| Cards +$21B to $1.263T (record; +$54B y/y) | §2, line 22 — identical | Verified |
| Auto +$28B to $1.713T (record; +$58B y/y) | §2, line 22 — identical | Verified |
| Student −$7B to $1.651T; 3.6M new defaults since Q4 2025 | §2, lines 20, 38 — 1.0M (Q4 2025) + 2.6M (Q1 2026) = 3.6M | Verified |
| HELOC +$13B to $459B; +$142B above Q1 2022 low | §2, line 24 — identical | Verified |
| 30-yr fixed 6.69% (week ending 6 Aug 2026), highest in over a year | §2, line 46 — identical | Verified |
| Card APR 20.94% all accounts / ~22.15% assessed-interest (May 2026, G.19) | §2, line 42 — identical | Verified |
| Auto 48-mo new-car rate 7.36% (Feb 2026, G.19) | §2, line 44 — identical | Verified |
| Aggregate delinquency 4.7%, improved slightly | §2, line 30 — identical | Verified |
| Card 90+ stock delinquency 12.8% (Q1 2026), flow stable since early 2024 | §2, line 34 — identical | Verified |
| Charged-off debt still reported after 1 yr: 80% (2024) vs ~40% | §2, line 34 — research says "2004–2012 about 40%"; infographic says "~40% pre-2012" | **Minor drift** — see I-5 below |
| 23M Americans carry charged-off card balances | §2, line 36 — identical | Verified |
| Q2 2020: −$34B total driven by cards −$76B | §2, line 50 — identical | Verified |
| Fed held 3.50%–3.75% (28–29 July 2026), 3 hawkish dissents | §2, line 48 — identical | Verified |
| Flows into serious delinquency: cards 6.97%, auto 3.00%, mortgages 1.52% (from 1.29%) | §2, line 32 — identical | Verified |
| Hero stat "+$49B new card-and-auto debt" | §4, line 93 — research itself derives +$49B from +$21B + $28B | Verified (derived, arithmetic correct) |

Specific items called out for scrutiny:

- **NY Fed Q2 2026 data ($18.771T, composition):** all figures match the artifact exactly. No drift.
- **Card APR figures (20.94% / 22.15%):** correctly attributed to G.19 May 2026 with the all-accounts vs assessed-interest distinction preserved. The infographic resists the temptation to mix in Bankrate (19.57%) or LendingTree (23.80%) figures, which measure different things. Correct choice.
- **12.8% delinquency artifact claim:** handled correctly — it appears only as a footer caveat with the NY Fed's own reconciliation attached, never as a scare stat. This matches the artifact's warning in §4 and the infographic's own "what to avoid" list.
- **3–4.5% legacy mortgage rate range:** the infographic flags it explicitly as "qualitative range for legacy rates, 6.69% verified" (line 38). This is honest handling of an unverified qualitative claim inherited from research §4. Acceptable, with a design-level caveat noted in I-4 below.
- **Kobeissi Letter tweet:** not cited or relied on anywhere in the infographic. The login-gated provenance problem does not propagate. No action needed.
- **"Other +$6B" waterfall bar (line 41):** this figure does not appear in the research artifact. It is a residual derived by subtraction (−74 −7 +13 +21 +28 +6 = −13 ✓). The arithmetic is correct and the NY Fed report does carry an "other" category, but the number is not independently sourced in the artifact. See I-2 below.

## Pass 2 — Reasoning quality

The core analytical move — same headline, inverted composition — is sound and is the artifact's own thesis (§1, §4, §7 Analogue 1). The infographic resists two failure modes the artifact explicitly warns against: it does not claim households "can't afford" the card debt (flow delinquency stable ~7%), and it does not make a Fed prediction. The "repricing, not deleveraging" framing is an interpretive label, but it is the artifact's label ("composition effect," §4) and is defensible.

One reasoning wrinkle: the color logic keys debt to "cost of credit," but applies that key inconsistently across categories — mortgage is colored by the *stock's legacy rate* (3–4.5%, cool) while HELOC and card are colored by the *current marginal rate* (hot). A new mortgage at 6.69% is more expensive than a legacy HELOC draw, yet mortgage is "cool" and HELOC is "hot." The reader is asked to hold both rate frames at once. The artifact's mechanism section supports both frames separately but the graphic merges them without flagging the switch. See I-4.

The substitution thesis itself ("households trading cheap debt for expensive debt") is supported by levels (+$49B expensive vs −$81B cheap) but is only one of four competing interpretations in the artifact (§5, Interpretation B). The infographic appropriately hedges via the footer caveats; it does not overcommit. Good.

## Pass 3 — Independent gap analysis

Gaps the infographic (and in some cases the research artifact) misses:

1. **Seasonality of the Q/Q card move (gap in both outputs, optional).** Card balances have a well-known seasonal pattern (Q1 paydown, Q4 spend-up). A +$21B Q2 rise is partly seasonal; neither the artifact nor the infographic adjusts for or acknowledges this. It does not break the record-level claim (levels, not changes, set the record), but the "absorbing the consumption gap" mechanism leans on the quarterly change.
2. **The student-loan default wave is invisible in the visual design.** The data table flags it ("shrinking balance masks a default wave"), and the "what to avoid" list warns against presenting student loans as clean paydown — yet the waterfall layout (layout step 3) annotates cards and auto but gives the student −$7B bar no annotation. Rendered bare, a cool-toned down-bar visually reads as benign deleveraging, which is precisely the inversion the avoid-list prohibits. The concept polices itself in prose but not in layout. See I-3.
3. **Lender-behavior counterargument is underweighted (optional).** The strongest counter to the distress-substitution thesis is in the artifact (§5-B): card limits rose $85B — lenders are still extending. The footer caveats carry +$383B y/y, delinquency 4.7%, and the 12.8% artifact note, but not the limit expansion. One line would strengthen the honest-broker posture the footer is clearly aiming for.
4. **HELOC purpose is unknown (optional).** The data table states "rate-locked owners are tapping equity through the side door instead of refinancing" as fact. The artifact (§8, Unknown) explicitly says whether HELOC draws fund consumption, renovation, or consolidation is unknown. The substitution framing is the artifact's own mechanism claim, so this is inherited, not invented — but the infographic states it one notch more confidently than the research does.
5. **Debt-service burden is absent (acknowledged, optional).** No debt-to-income or debt-service ratio exists in the release; the artifact notes this. Neither output can show it. Noted only so the absence is on record.

## Pass 4 — Cross-surface consistency

Only one surface exists. Consistency of the infographic against the research artifact:

| Dimension | Consistent? | Notes |
|---|---|---|
| Headline framing ("deleveraging illusion") | Yes | Matches artifact §1 and title |
| Composition data | Yes | All bars trace (see Pass 1) |
| 2020 mirror-image comparison | Yes | Matches artifact §7 Analogue 1, including the "opposite household" language |
| Delinquency treatment | Yes | 12.8% only with artifact caveat; flows presented as stable |
| Fed policy framing | Yes | Shows the debate (hold, 3 dissents), no prediction — matches artifact §6 and avoid-list |
| Student loans | **Partial** | Data table honest; waterfall layout lacks the mask annotation (I-3) |
| Kobeissi sourcing | Yes | Not cited; login-gated source does not propagate |

## Pass 5 — Format-specific feedback (infographic)

| ID | Severity | Issue | Recommendation |
|---|---|---|---|
| I-1 | **should-fix** | **Internal contradiction in the rate-ladder spec.** Line 46 says ladder "markers sized by balance"; line 52 labels card the "(largest marker, $1.263T)". Auto is $1.713T (larger) and mortgage is $13.1T (10× larger). As written the spec cannot be executed: either markers are sized by balance — in which case card is the *smallest* of the three and mortgage swamps the axis — or they are not. | Decide explicitly. Best fix: size markers by balance but exclude the mortgage stock from sizing (annotate "mortgage marker not to scale — stock $13.1T"), or use a log/sqrt scale and say so in the legend. Remove "(largest marker)" from the card annotation unless it survives the chosen rule. |
| I-2 | **should-fix** | **"Other +$6B" bar is a derived residual with no source in the artifact.** Arithmetic checks (−13 net ✓) and the NY Fed report does carry an "other" category, but the artifact never states the figure. | Either verify the "other" line against the Q2 2026 report and add it to the artifact's data table, or label the bar on-graphic as "other (residual)". Do not present it as a sourced value. |
| I-3 | **should-fix** | **Student-loan bar violates the concept's own avoid-list when rendered.** Layout step 3 annotates card and auto records but leaves the student −$7B bar bare; as a cool down-bar it will read as benign paydown, inverting reality per line 68. | Add a one-line annotation to the student bar ("balance down, defaults up — 3.6M new defaults since Q4 2025") or a shared footnote keyed to the bar. |
| I-4 | **should-fix** | **Hot/cool color key mixes two rate frames.** Mortgage is colored by legacy stock rate (3–4.5% qualitative, unverified); HELOC/card/auto by current marginal rate. A new mortgage (6.69%) out-costs a HELOC draw yet renders "cool" while HELOC renders "hot". | Make the legend frame-explicit: "color = cost of the *existing* debt being repaid vs the *new* debt being added", or key every category to current rates and annotate the mortgage bar with the qualitative 3–4.5% legacy note the draft already flags. Do not leave the switch implicit. |
| I-5 | **optional** | Minor drift: "~40% pre-2012" vs the artifact's "2004–2012 about 40%". The research window starts in 2004; "pre-2012" overextends it. | Use "~40% (2004–2012)" on the footnote. |
| I-6 | **optional** | Footer omits the strongest bull fact: card limits +$85B (lenders still extending). | Add as a fourth footer caveat if space allows; it is the cleanest counterweight to the hot-tone story. |
| I-7 | **optional** | Rate ladder omits HELOC rate while HELOC appears in the waterfall as "hot". No HELOC rate is sourced anywhere in the artifact. | Either source a HELOC rate (Prime-based, ~7.5–8.5% territory) through research and add it, or grey the HELOC bar with "rate not shown". |

**Is the visual concept the right way to show the data?** Yes. Paired waterfalls of flows (not a levels pie) with a cost-of-credit color key is the correct encoding for this story — the argument is about flows and prices, not shares. The explicit rejection of a levels treemap (line 65) is correct: mortgages are 70% of the total and would bury the story. The "make the bars sum visibly to the net" instruction (line 55) is good chart hygiene.

## Pass 6 — Explanatory depth

Strong. The header/subhead pair ("US household debt just fell for the first time in six years." / "Look at what fell.") earns the subversion without clickbait. The 2020 mirror-image does the argumentative work visually that prose would otherwise have to do — a reader can extract "same headline, opposite household" without reading a paragraph. The footer caveats preserve both the bull and bear readings, which is the artifact's actual finding. The concept explains rather than merely displays. No changes required at the concept level.

## Independent gaps summary

- Seasonality of Q/Q card balance move unacknowledged (both outputs) — optional.
- Student-loan default wave visible in prose, invisible in layout — carried as I-3.
- Lender limit expansion (+$85B) underweighted — carried as I-6.
- HELOC draw purpose stated more confidently than research allows — optional.
- Debt-service ratio absent from the release itself — on record, no action.

## Verdict

**APPROVE WITH CHANGES — no blockers.**

Every primary number on the graphic traces to the NY Fed Q2 2026 report, G.19, Freddie Mac PMMS, or the FOMC record via the research artifact; the two numbers that don't (the qualitative 3–4.5% legacy mortgage range and the derived "Other +$6B" residual) are flagged or fixable. The Kobeissi tweet's login-gated provenance does not propagate into the surface. Reasoning is sound and appropriately hedged against the artifact's competing interpretations.

Four should-fix items, all at design-spec level, none requiring new research beyond one optional source check:

1. **I-1** — resolve the rate-ladder marker-size contradiction ("sized by balance" vs "card = largest marker" is unexecutable as written).
2. **I-2** — source or label the "Other +$6B" residual.
3. **I-3** — annotate the student-loan bar so the rendered chart obeys its own avoid-list.
4. **I-4** — make the hot/cool color key frame-explicit (legacy stock rate vs current marginal rate).

Fix those, and the concept is cleared to render.
