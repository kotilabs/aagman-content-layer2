# SEO/AEO Audit: India's Solar Wall — The Grid Can't Carry What the Panels Can Make

Signal ID: `india-solar-curtailment-wall`
Audit date: 2026-09-03
Draft audited: `drafts/signal-india-solar-curtailment-wall-blog.md` (post markets-review corrections, post de-AI pass)

## Score summary

| Dimension | Score | Status | Key takeaway |
|---|---|---|---|
| SEO | 7/10 | On Track | Strong headings and keyword density; H1 omits the word "curtailment," no frontmatter, no internal links. |
| GEO | 9/10 | Strong | Direct answer upfront, dense dated numbers, every claim traceable to the artifact. |
| AEO | 8/10 | Strong | Definition sentence and question H3s present; one tighter quotable answer block would help. |
| Layer 2 fit | 10/10 | Strong | Bias labelled, no advice, open ending, source table, disclosure intact. |

## Executive summary

The draft is factually dense, well-sourced, and structurally close to publishable. The single most important optimization is search-surface labelling: the H1 never uses the word "curtailment" (the actual search term), and the file lacks the slug/meta-description frontmatter that published Layer 2 pieces carry. Both are cheap fixes that do not touch the prose.

## SEO findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| Title / H1 | "India's Solar Wall: The Grid Can't Carry What the Panels Can Make" — honest, tension-bearing, but the core search term "solar curtailment" appears nowhere in the H1. | Needs Attention | Change H1 to "India's Solar Curtailment Wall: The Grid Can't Carry What the Panels Can Make." |
| Heading hierarchy | H1 → H2 subtitle → H2 sections, with question-form H3s under Context, Mechanism and Signal/deviation. No skipped levels. | Good | Leave as is. |
| Subheadings as search queries | H3s ("What changed in April–June 2026?", "How does a grid end up refusing free electricity?", "Why is this quarter different from a normal summer of grid stress?") map to real queries. | Good | Leave as is. |
| URL slug | None present (no frontmatter). | Missing | `india-solar-curtailment-grid-transmission-2026` |
| Meta description | None present. | Missing | "India curtailed 8,133 GWh of solar power in April–June 2026, even as demand hit a record 270.82 GW. The transition's constraint is now the grid, not the panels." (159 chars) |
| Frontmatter | Published finals (e.g. `signal-fed-divergence-curve-steepening-blog.md`) carry YAML frontmatter with title, description, date, slug and Article/FAQPage schema. This draft has none. | Missing | Add frontmatter block; keep the SEBI disclosure line immediately after it, before the H1. |
| Internal links | Zero internal links. The audit standard is 3–5 links to other Aagman Layer 1/Layer 2 pieces. Published finals use either a "Related reading from the archive:" block or inline `/p/...` links. | Missing | Candidates by theme: the DII-flows/FII-exodus piece (India market flows), the F&O microstructure reset (India market structure), the copper–gold divergence piece (energy-transition commodities). Operator must insert final slugs/URLs at publish time — they are not knowable from the draft stage. Do not invent slugs. |
| Image / table opportunities | The buildout-vs-grid data table is present and snippet-friendly. Infographic concepts file offers four commissionable visuals. | Good | Leave as is. |
| Keyword coverage | "Solar," "curtailment," "Grid Controller of India," "ISTS," "discom," "IEX," "BESS," "transmission" all appear naturally and early (subtitle + In short paragraph). | Good | Leave as is. |

## GEO findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| Direct answer upfront | The H2 subtitle states the fact (8,133 GWh, one quarter) and the "In short" paragraph states what happened and why it matters within the first ~200 words. | Good | Leave as is. |
| Factual density | Exceptional: monthly curtailment split, 270.82 GW peak dated 21 May, TRAS daily averages, IEX price series, auction series, discom debt — all citable by an AI engine. | Good | Leave as is. |
| Source credibility | Every number traces to the research artifact; 14-row source table with URLs. | Good | Leave as is. |
| Entity clarity | MNRE, Grid Controller of India Ltd, National Load Dispatch Centre, IEX, ICRA, Ember, CSEP, IEEFA, SECI, ReNew — named consistently with full forms at first use where needed. | Good | Leave as is. |
| Comprehensiveness | Mechanism, four readings, two historical analogues, implications, and the data-cause unknown are all covered. No obvious follow-up left unanswered. | Good | Leave as is. |
| Original angle | The uncompensated-curtailment risk-allocation framing and the contract-stack argument go beyond the dominant "grid lag" coverage. | Good | Leave as is. |

## AEO findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| Definition pattern | "Curtailment is deliberate: the grid operator orders plants to reduce output when the system cannot safely absorb it." — a clean "X is..." definition inside the In short paragraph. | Good | Leave as is. |
| List / table snippets | The buildout-vs-grid table is directly extractable. The three-layer mechanism is prose; converting it to a list would harm the voice — not recommended. | Good | Leave as is. |
| Question-phrased headings | Three question H3s plus question-form FAQ candidates. | Good | Mirror them in the FAQPage schema. |
| Quotable paragraphs | The In short paragraph runs ~85 words — slightly long for a featured-snippet pull, but the definition sentence inside it works standalone. | Good | No change; the sentence, not the paragraph, is the snippet. |

## Layer 2-specific findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| No advice framing | Explicit "What this does not affect" section; no buy/sell language, no targets, no return promises. ReNew mention is dated, attributed, neutral. | Good | Leave as is. |
| Uncertainty labeled | Cause-breakdown unknown (transmission vs local oversupply) explicitly flagged; interpretation spectrum holds four readings in tension. | Good | Leave as is. |
| Bias declared | Aagman India-bull bias note present and subordinated to the data. | Good | Leave as is. |
| Open ending | Ends on the absorption question — no CTA. | Good | Leave as is. |
| Source table | Present, 14 sources, dated. | Good | Leave as is. |
| Disclosure | "Educational content from Koti Labs (SEBI RIA INA000021951). Not investment advice — no buy/sell recommendation." intact at the top of the content body. | Good | Must stay immediately after the new frontmatter, before the H1. |
| Length | 1,800w target vs ~2,570 prose words (ex-sources/tables). Published finals run 2,598–3,011 by the same measure, and `prompts/blog_writer.md` permits going longer when the signal has more moving parts. The operator's "~100 words over" flag implies a narrower body-only count that could not be reproduced from the file. De-AI pass trimmed ~55 words; reaching 1,800 under any raw measure requires deleting a structural section (a reading or an analogue), which is an editorial call above this loop. | Needs Attention | Operator to confirm the counting convention or accept the "go longer" clause. |

## Recommended changes

- **Location:** Frontmatter (new, top of file)
  - **Issue:** No slug, meta description, or schema — published finals carry these.
  - **Fix:** Add YAML frontmatter: title, description (meta text above), date 2026-09-03, slug `india-solar-curtailment-grid-transmission-2026`, Article + FAQPage schema with questions drawn from the H3s. Disclosure line stays directly below, before the H1.
  - **Priority:** Critical
- **Location:** H1
  - **Issue:** "Curtailment" — the search term — absent from the title.
  - **Fix:** "India's Solar Curtailment Wall: The Grid Can't Carry What the Panels Can Make"
  - **Priority:** High
- **Location:** Body, after Context section (or per house convention)
  - **Issue:** No internal links.
  - **Fix:** Operator inserts 3–5 links at publish time once slugs are confirmed — candidates: the DII-flows/FII-exodus piece, the F&O microstructure reset, the copper–gold divergence piece. Do not fabricate slugs in the draft.
  - **Priority:** High (publish-time task)

## What to leave alone

- The "In short" paragraph, the definition sentence, and the question H3s — already AEO-optimal.
- The buildout-vs-grid table and the 14-row source table — snippet-ready, do not reformat.
- The interpretation spectrum and both historical analogues — depth is the GEO moat; do not compress.
- The disclosure line, bias note, and open-question ending — compliance load-bearing.
- All numbers and session-level labels (RTM price shape, IEEFA high-base caveat, Southern-buildout caveat) — verified in the markets review.

## Verdict

Optimize and proceed — frontmatter + H1 keyword fix applied to the draft; internal links deferred to publish time (slugs not knowable at draft stage); length flagged to the operator as a counting-convention question, not a defect the de-AI pass can solve.
