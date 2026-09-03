# SEO/AEO Audit: India's Ozempic Moment, Six Months In

Signal ID: `india-glp1-ozempic-moment` | Audit date: 2026-09-03 | Surface: blog only. Run after markets-review corrections were applied.

## Score summary

| Dimension | Score | Status | Key takeaway |
|---|---|---|---|
| SEO | 8/10 | Strong | Precise H1, entities dense and early; missing frontmatter (slug/meta/schema) and internal links are the only real gaps. |
| GEO | 9/10 | Strong | Direct answer in the first 100 words, high factual density, every number sourced; AI engines can cite this cleanly. |
| AEO | 8/10 | Strong | Definition sentence and a snippet-ready table present; canonical skeleton headings don't map to search queries, but the table and Reading paragraphs compensate. |
| Layer 2 fit | 10/10 | Strong | Disclosure, bias declaration, known/unknown/unknowable, open-question ending — all present and correct. |

## Executive summary

The blog is factually dense, well-sourced, and structurally complete against the Layer 2 skeleton. The single most important optimization is mechanical, not editorial: the draft ships without the frontmatter block (title, meta description, slug, Article + FAQPage schema) that finalized Layer 2 pieces carry, and without internal links to the archive. Neither requires touching a sentence of the argument.

## SEO findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| Title / H1 | "India's Ozempic Moment, Six Months In" — precise, honest, contains brand entity (Ozempic) and geography (India). No clickbait. | Good | Leave. |
| Heading hierarchy | H1 → mandatory H2 subheadline → H3 canonical sections. No skipped levels. | Good | Leave. |
| Subheadings as search queries | Section names are the canonical skeleton (Context / Mechanism / Signal / Interpretation spectrum...), which the blog writer prompt mandates. They are not query-shaped, but the H2 subheadline and the open-question close carry the query-like phrasing. | Good (constrained by skeleton) | Leave — do not fight the mandated structure. |
| URL slug | None present. | Missing | `india-semaglutide-patent-cliff-generics-six-months` (applied in frontmatter below). |
| Meta description | None present. | Missing | Applied in frontmatter (157 chars, states the tension, no urgency). |
| Internal links | None present. | Missing | Add 3–5 archive links before publish (operator action — see Recommended changes; not auto-applied because link targets can't be verified from this repo). |
| Image / table opportunities | Table 1 (17 rows, sourced) is snippet-ready. The price ladder and the Hangzhou supply-route visual from the carousel design notes would both add clarity. | Good | Optional: port the price-ladder graphic into the Context section. |
| Keyword coverage | Semaglutide, Ozempic, Wegovy, GLP-1, India, generic, patent expiry all land in the first 150 words. Related entities (CDSCO, DCGI, Section 232, CDMO, API) appear naturally. | Good | Leave. |

## GEO findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| Direct answer upfront | The analogy opens the piece (mandated), but the second paragraph ("That is roughly where India's semaglutide market stands…") plus the Context section state plainly what happened and why it matters within ~150 words. | Good | Leave. |
| Factual density | 17-row data table plus dated, sourced claims throughout: 13 companies/26 brands, ₹1,290 vs ₹8,800–11,175, +56% to 414,000 units, $900/g → $90–160/g, one DCGI-registered supplier, 57%/38% share splits. | Good | Leave. |
| Source credibility | Every claim traces to the research artifact; sources named inline (Pharmarack via Bloomberg, Jefferies via ET, Zerodha Chatter). Derived figures labelled. | Good | Leave. |
| Entity clarity | Consistent naming: Novo Nordisk/Novo, Eli Lilly/Lilly, Dr Reddy's, Sinopep-Allsino, DCGI/CDSCO used with first-use context. | Good | Leave. |
| Comprehensiveness | Obvious follow-ups (export dimension, tariff overlay, oral pivot, quality risk) are all answered in-body or flagged as known unknowns. | Good | Leave. |
| Original angle | "Where the margin migrates" + single-supplier dependency + the four-reading interpretation spectrum go well beyond the dominant "cheap Ozempic in India" coverage. | Good | Leave. |

## AEO findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| Definition pattern | "Semaglutide — the molecule sold as Ozempic for diabetes and Wegovy for weight loss — is the defining drug class of this decade." Plain, early, quotable. | Good | Leave. |
| List / table snippets | Table 1 is directly extractable; the "What this affects" bullet list is snippet-shaped. | Good | Leave. |
| Question-phrased headings | None — the skeleton forbids them at section level. The closing section poses the core question in prose. | Needs Attention (minor) | Compensate with FAQPage schema (applied in frontmatter) so answer engines get question-form entries without breaking the skeleton. |
| Quotable paragraphs | The April-data paragraph (market +56%, Novo +40%) and the single-supplier paragraph are both 40–60-word direct answers. | Good | Leave. |

## Layer 2-specific findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| No advice framing | No buy/sell calls, targets, or return promises; "Nothing here is a recommendation to buy or sell any security" stated outright. | Good | Leave. |
| Uncertainty labeled | Known/unknown/unknowable section present; estimates and derived figures labelled inline. | Good | Leave. |
| Bias declared | "Aagman's structural bias, declared" paragraph present, correctly frames Reading A as bias-influenced and names the data that challenges it. | Good | Leave. |
| Open ending | Ends on an unresolved question (which layer stays scarce when the second API supplier arrives). No CTA. | Good | Leave. |
| Source table | Inline per-row sourcing in Table 1 plus a closing source paragraph. | Good | Leave. |
| Disclosure | Koti Labs / INA000021951 disclosure intact at the top. | Good | Leave. |

## Recommended changes

- **Location:** Top of file (before the disclosure line)
- **Issue:** No frontmatter — finalized Layer 2 blogs (e.g. `final/signal-fed-divergence-curve-steepening-blog.md`) carry title/description/date/slug and Article + FAQPage schema.
- **Fix:** Add the frontmatter block (applied in this pass):
  - title: "India's Ozempic Moment, Six Months In: What the Semaglutide Patent Cliff Revealed"
  - description: "Semaglutide's Indian patent expired on 20 March 2026; generics opened 85% below branded. Six months on, margin has migrated from molecule to infrastructure." (155 chars)
  - slug: `india-semaglutide-patent-cliff-generics-six-months`
  - Article schema + FAQPage schema with five questions (what happened when the patent expired; how much prices fell; who supplies the API; where the profits sit; what the Section 232 tariffs change).
- **Priority:** High

- **Location:** After the Context section (or before the source paragraph at the end)
- **Issue:** No internal links — the audit standard is 3–5 archive links.
- **Fix:** Operator action before publish: add a "Related reading from the archive" list pointing at 3–5 existing Layer 1/Layer 2 pieces (e.g. a Layer 1 explainer on how patent cliffs work, a Layer 2 piece on Indian pharma CDMOs or on Section 232 tariffs if one exists). Not auto-applied: link targets cannot be verified from this repo, and inventing URLs would violate the no-fabrication rule.
- **Priority:** High (operator task)

- **Location:** Context section
- **Issue:** A price-ladder visual (branded ₹8,800–16,400 down to ₹1,290) would strengthen snippet and image-search potential.
- **Fix:** Optional — port the carousel's price-ladder design note into the published post. Do not add if it delays publish; Table 1 already carries the data.
- **Priority:** Quick Win (optional)

## What to leave alone

- The H1 and the H2 subheadline — precise, honest, no clickbait.
- The mandated skeleton section headings — do not rename them into questions.
- Table 1 and its per-row sourcing — already snippet-ready.
- The interpretation spectrum, bias declaration, and known/unknown/unknowable sections — these are the piece's GEO differentiators.
- The closing open question — correct Layer 2 ending, no CTA.
- The disclosure line — mandatory, untouched.

## Verdict

Minor tweaks only — content is search-ready. Mechanical frontmatter applied in this pass; internal links queued as an operator action pre-publish.
