# Infographic Concepts: Why Did the US Join the Yen Intervention?

**Source research artifact:** `research/signal-us-japan-yen-intervention.md`
**Date:** 2026-08-12

---

## Verified interesting data

| Data point | What it shows | Source | Verdict |
|---|---|---|---|
| ¥163.99 low → ¥155.23 bounce → ~¥158 retrace (all within one week) | The operation moved the yen ~6 yen, then gave back a third — intervention effect vs. trend | thesun.my (3 Aug); OMFIF (8 Aug) | Strong — clean three-point narrative |
| Japan's solo Thursday operation: up to $58.97bn | Largest single-day currency defense ever; Japan was already at unprecedented scale *before* the US joined | BoJ data via SunCrypto (5 Aug); Cape Capital | Strong — anchor stat |
| US leg: $5–10bn vs Japanese leg: ~$75bn | The asymmetry is the story — a token US amount did outsized signalling work | Reuters notepad photo via Express Tribune (2 Aug); OMFIF estimate (8 Aug) | Strong, but label both as estimates pending MOF disclosure |
| US funded in euros, not dollars (NY Fed via Goldman Sachs & Morgan Stanley) | Deliberate posture: support the yen without selling dollars | FT via Brussels Signal (7 Aug); Reuters | Strong — single most revealing design detail |
| Rate gap: BoJ 1.0% (highest since 1995) vs Fed 3.50–3.75% = ~250–275bp | The mechanical cause intervention doesn't touch | OMFIF (8 Aug); SunCrypto (5 Aug) | Strong — required context for every visual |
| 10-year UST 4.1% → 4.6% YTD; 30-year >5.1% (21 Jul) | Why Washington cares: the pressure point predates the intervention | OMFIF (8 Aug); CRFB (21 Jul) | Strong — the "tolerance" axis |
| FIMA repo: $60bn/day per-institution cap, priced above private repo | The new intervention-financing architecture and its limits | Bloomingbit (5 Aug) | Needs context — most readers have never heard of FIMA; one-sentence explainer required |
| Historical spacing: 1998 (joint yen buy, US leg $833mn) → 2011 (joint yen *sell*) → 2026 (joint yen buy) | 28-year gap; direction flipped in 2011; US legs have always been small | NY Fed (1998); SunCrypto; MUFG | Strong — timeline is the natural visual |
| FX volumes on 31 Jul: EBS $102bn (10-yr high), CME record $158bn, yen futures record $52bn | Positioning was crowded — the operation caught a one-sided market | The Full FX (2 Aug) | Strong supporting stat |
| BoJ held 1.0% (8–1, Takata dissent for 1.25%) the same week; next meeting 17–18 Sep | The fundamental lever stayed untouched — policy divergence continues | SunCrypto (5 Aug); Jiji Press (11 Aug) | Strong for the "what's not fixed" panel |
| Japan intervened joint 5× vs solo 8× since 1985; joint ops more often coincided with trend turns | Coordinated intervention has a better hit rate than solo | Brent Donnelly (Spectra Markets) via Reuters/EnterpriseAM (3 Aug) | Needs context — small sample, correlation not causation |

---

## Recommended concepts

### Concept 1: "The Neighbour's Alarm" — the intervention-financing loop (FLOW)

- **Central insight:** Defending the yen is paid for in US Treasuries — so Japan's currency problem was mechanically becoming America's bond-market problem, and the US leg was designed to break that loop.
- **Data:** reserves-funded intervention chain (sell Treasuries → dollars → yen); Japan's ~$59bn solo day; 10Y yield 4.1% → 4.6%; FIMA $60bn/day cap as the bypass.
- **Visualization type:** Flow diagram — a circular loop (Yen weakens → Japan intervenes → sells Treasuries → US yields rise → Washington's problem) with the US operation shown as two inserted "valves": (1) joint buying reduces total spend, (2) FIMA repo reroutes financing away from bond sales.
- **Rough composition notes:** Reader sees the loop first, in red, with the yield arrow climbing at the bottom. The two US interventions appear as blue valves breaking the cycle, each tagged with its number ($5–10bn; $60bn/day cap). Payoff line at the bottom, tagged as the essay's argument rather than settled fact: "The essay's reading: the US didn't buy the yen. It bought control of how Japan pays for the yen."
- **Source attribution:** OMFIF (yield path, mechanism); SunCrypto (solo operation size); Bloomingbit (FIMA cap); FT/Reuters (euro funding).
- **Generation prompt (Aagman design language):** Clean institutional infographic on a white background. Bold near-black headline "The Neighbour's Alarm" at top, with a one-line charcoal subhead: "Defending the yen is paid for in US Treasuries — the US leg was designed to break that loop." Primary mint (`#56E8B8`) and teal (`#6FE6CD`) as accent colors; amber (`#F59E0B`) only for the yield-pressure arrow. Layout: circular flow diagram, read clockwise. Start at top: "Yen weakens" → right: "Japan intervenes" → bottom: "Sells Treasuries / dollars rise" → left: "US yields climb" → back to top. The bottom yield arrow is amber and thick, annotated "10Y 4.1% → 4.6%". Two mint-colored valves break the loop: a joint-buy valve tagged "US+Japan: $5–10bn" and a FIMA-repo valve tagged "$60bn/day cap". Floating annotation boxes with soft mint background (`#E7EEEA`) at the two valves. Two-column footer: left "The US didn't buy the yen; it bought control of how Japan pays for it.", right "Japan's solo day: ~$59bn; US leg: $5–10bn in euros." Source line at bottom: "Sources: OMFIF, BoJ via SunCrypto, Bloomingbit, FT/Reuters." No gradients, no shadows, no decorative icons.

### Concept 2: "28 Years in One Timeline" — the rarity of US participation (TIMELINE)

- **Central insight:** The US has acted on the yen only three times in three decades — and the direction, partners, and funding of each operation tell you what Washington actually feared each time.
- **Data:** 1998 — joint yen buy, US leg $833mn, yen 146 → 136 (NY Fed); 2011 — G7 yen *sell* after Tōhoku, opposite direction; 2026 — joint yen buy, US leg $5–10bn in euros, Fed absent. Secondary track: USD/JPY level at each event (146 / 76.25 / 163.99) — the 2011 figure is the record yen spike of ¥76.25 per dollar on 17 March 2011 that triggered the G7 sale (FinanceFeeds, citing Reuters' intervention history).
- **Visualization type:** Horizontal timeline with three event cards above/below a USD/JPY sparkline; each card tagged with direction (buy/sell), coalition (US+Japan / G7 / US+Japan), and funding (dollars / dollars / euros).
- **Rough composition notes:** The eye lands on 2026 first (largest card, right edge), then scans left across the 28-year gap. The 2011 card flipped below the axis makes the direction reversal instant. The euro-funding tag on 2026 is the payoff detail.
- **Source attribution:** NY Fed (1998); MUFG (1998 context); SunCrypto (2011, 2026); Brussels Signal/FT (euros).
- **Generation prompt (Aagman design language):** White-background institutional infographic. Bold near-black headline "28 Years in One Timeline" with charcoal subhead "The US has acted on the yen only three times in three decades — direction, partners, and funding tell the real story." Layout: horizontal timeline spanning the full width, with a thin USD/JPY sparkline running beneath. Three event cards: 1998 above the axis (mint `#56E8B8`), 2011 below the axis (amber `#F59E0B` to signal opposite direction), 2026 above the axis and largest (teal `#6FE6CD`). Each card shows: year, direction (buy/sell), coalition, funding currency, and US leg size. Annotation boxes in soft mint background (`#E7EEEA`) tag "1998: $833mn, dollars, yen 146 → 136", "2011: G7 yen sell after Tōhoku, ¥76.25 spike", "2026: $5–10bn in euros, Fed absent". Two-column footer: left "Direction flipped in 2011; funding switched to euros in 2026.", right "28-year gap between US legs on the yen." Source line: "Sources: NY Fed, MUFG, SunCrypto, FT/Reuters." No clutter, no portraits, no flags.

### Concept 3: "The Gap Intervention Can't Close" — rate differential vs. currency defense (DIVERGENCE)

- **Central insight:** Everything that happened in the first week of August sits on top of an untouched 250–275bp rate gap — intervention moved the price, not the incentive.
- **Data:** BoJ 1.0% (highest since 1995) vs Fed 3.50–3.75%; yen path ¥163.99 → ¥155.23 → ~¥158; BoJ hold 8–1 with dissent for 1.25%; next meeting 17–18 Sep; market pricing leans to a Fed *hike*.
- **Visualization type:** Two-panel divergence. Left panel: bar comparison of policy rates with the 250–275bp gap bracketed. Right panel: the one-week USD/JPY path annotated with "intervention" at the drop and "drift back" on the retrace.
- **Rough composition notes:** The gap bracket dominates the left panel — visually un-closeable. The right panel's partial retrace answers it. Footer stat: "The BoJ held rates the same week Washington bought yen." Payoff: the UBS line, "supported more by intervention risk than by domestic monetary fundamentals."
- **Source attribution:** OMFIF (rates, retrace); SunCrypto (BoJ vote, UBS quote); Jiji Press (September meeting).
- **Generation prompt (Aagman design language):** Clean white-background infographic. Bold near-black headline "The Gap Intervention Can't Close" with charcoal subhead "Intervention moved the yen's price, not the rate incentive behind it." Two-panel layout. Left panel: bar comparison of policy rates — BoJ 1.0% in mint (`#56E8B8`), Fed 3.50–3.75% in teal (`#6FE6CD`), with a bracketed gap in near-black showing "250–275bp". Right panel: one-week USD/JPY path as a line chart, mint stroke, annotated with three floating boxes: "¥163.99 low", "intervention bounce to ¥155.23", "retrace to ~¥158". Small annotation below line: "BoJ held 1.0% the same week (8–1 vote, next meeting 17–18 Sep)." Two-column footer: left "The rate gap is untouched; the retrace proves it.", right "Policy divergence is the force; intervention is the punctuation." Source line: "Sources: OMFIF, SunCrypto, Jiji Press." No gradients, no 3D, minimal grid.

### Concept 4: "A Signal, Not a Wall" — the size asymmetry (COMPARISON)

- **Central insight:** The US spent maybe a tenth of what Japan spent — proof the American leg was priced as a signal, not as firepower.
- **Data:** Japan ~$59bn solo Thursday / ~$75bn estimated total; US $5–10bn; combined effect ~6 yen in two sessions; EBS record $102bn volume.
- **Visualization type:** Scaled bar/trench comparison — Japanese bar dwarfs the US bar; an arrow from the thin US bar to the six-yen move carries the label "the signal, most likely, did the work" (the essay's reading, not settled fact).
- **Rough composition notes:** Extreme scale contrast is the whole visual; resist adding other elements. Footnote required: all sizes are estimates pending MOF month-end disclosure.
- **Source attribution:** SunCrypto/Cape Capital (Japanese leg); Reuters notepad photo + OMFIF (US leg); The Full FX (volumes).
- **Generation prompt (Aagman design language):** White-background institutional infographic. Bold near-black headline "A Signal, Not a Wall" with charcoal subhead "The US spent maybe a tenth of what Japan spent — the signal, not the firepower, did the work." Layout: two horizontal bars in extreme scale contrast. Large mint (`#56E8B8`) bar labeled "Japan total ~$75bn"; tiny teal (`#6FE6CD`) bar below labeled "US leg $5–10bn". A curved arrow from the small US bar to a large callout: "~6 yen move in two sessions". Floating annotation box in soft mint background (`#E7EEEA`): "EBS record $102bn volume — positioning was crowded." Two-column footer: left "Asymmetry is the story: a token US amount carried outsized signalling weight.", right "Sizes are estimates pending MOF month-end disclosure." Source line: "Sources: SunCrypto/Cape Capital, Reuters/OMFIF, The Full FX." No map, no flags, no decorative elements.

---

## What to avoid

- **"South Korea joined the intervention" map/graphic** — single low-credibility wire (Guavy), uncorroborated. Dropped.
- **"Japan drew $59.7bn from FIMA" flow** — single low-credibility source (worldatlarge.news), contradicted by Reuters/FT accounts that FIMA is a *future* plan. Dropped; monitor MOF/Fed disclosures.
- **A single point-estimate total for the intervention** — sources disagree by 3× (¥9tn / ¥13.8tn / ~$75bn / $32–36.6bn). Any graphic must show the range or wait for MOF month-end disclosure.
- **Carry-trade unwind domino map** (yen → tech stocks → EM → crypto) — real mechanism but unquantified for this episode (position estimates are "several hundred billion," unsourced at that precision). Better suited to a future unwind event than to this intervention story.
- **Trump/Bessent quote collage** — the quotes are atmosphere, not data; they risk turning an analytical graphic into politics coverage.

---

## Final recommendation

**Proceed with Concepts 1 and 3.**

Concept 1 ("The Neighbour's Alarm") is the lead infographic: it visualizes the piece's actual thesis — the Treasury-protection mechanism — which no other outlet has rendered as a flow, and every number in it is multi-sourced. Concept 3 is the natural companion or standalone alternative if a simpler execution is needed. Concept 2 is strong but better saved for a follow-up piece if the joint framework holds; Concept 4 folds cleanly into Concept 1 as its left-hand panel rather than standing alone.
