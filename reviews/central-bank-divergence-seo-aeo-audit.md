# SEO/AEO Audit: Three Central Banks, Three Verdicts

## Score summary

| Dimension | Score | Status | Key takeaway |
|---|---|---|---|
| SEO | 7/10 | On Track | Strong entities and data tables; title and meta were missing and have now been added; internal links still need to be wired up. |
| GEO | 8/10 | Strong | Factual density and source traceability are excellent; the first 100 words now explicitly define the phenomenon and the actors. |
| AEO | 7/10 | On Track | Question-form H2s and definition pattern added; FAQ schema suggested; body could still use a short inline FAQ block. |
| Layer 2 fit | 9/10 | Strong | Voice, epistemic posture, and no-advice discipline are intact. Only minor tension between AEO direct-answer pressure and Substack analogy structure. |

## Executive summary

The draft is structurally sound, well-sourced, and already Layer-2-voice compliant. Its main SEO/AEO weakness was that the H1, meta description and first-paragraph answer target did not surface the central topic — "central bank divergence" — for search engines or answer engines. Those gaps have been fixed in the draft. The remaining work is mechanical: wire up internal links, validate schema markup, and decide whether to add an inline FAQ block.

## SEO findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| Title / H1 | Original H1 "Three Central Banks, Three Verdicts" was evocative but did not contain "divergence" or the bank abbreviations readers search. | Fixed | H1 now reads: **"Three Central Banks, Three Verdicts: Why the Fed, ECB and RBA Are Diverging in June 2026"**. Keeps voice while surfacing topic, entities and date. |
| Meta description | Missing. | Fixed | Added YAML frontmatter description: *"Central banks split in June 2026: the Fed held with a hawkish dot plot, the ECB hiked into slower growth, and the RBA paused. What it means for FX, rates and oil."* (159 characters). |
| URL slug | Not set. | Fixed | Suggested slug added to frontmatter: `central-bank-divergence-fed-ecb-rba-june-2026`. |
| Heading hierarchy | Logical H1 → H2 → H3 flow with no skipped levels. | Good | No change needed. |
| Subheadings as search queries | Several H2s were descriptive rather than query-shaped. | Fixed | H2s now include question forms: "What changed?", "How does central bank divergence transmit to markets?", "What makes this divergence unusual?", "What are the four plausible readings?", "What do 1975 and 2015 tell us?" |
| First 100 words / keyword coverage | Original opening was entirely analogy; central topic not stated until ~word 110. | Fixed | Added two-sentence direct answer before the analogy: "Central bank divergence happens when..." and "In mid-June 2026, the Federal Reserve, European Central Bank and Reserve Bank of Australia delivered exactly that." |
| Internal links | No internal links to other Aagman Layer 1 or Layer 2 pieces. | Needs Attention | Added an HTML-comment block with five high-relevance internal link opportunities. Writer should replace `LINK` with actual URLs. Minimum 3 links recommended. |
| External links / source credibility | Footnotes trace nearly every claim to central bank releases, market data or reputable research. | Strong | No change. |
| Image / table opportunities | Two markdown tables already present (policy actions, market reactions). | Strong | Consider converting the market-reaction table into an image/chart for Substack shareability, but keep the table for accessibility and snippet capture. |
| Keyword cannibalization | Low risk. | Good | The updated H1 owns "central bank divergence" + "Fed ECB RBA" + "June 2026". No Layer 1 piece is likely to target this exact intersection. |
| Cannibalization vs Layer 1 | The piece stays at Layer 2 altitude. | Good | It does not overlap with a hypothetical Layer 1 "what is monetary policy" or "how do central banks work" article. |

## GEO findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| Direct answer upfront | Original first 100 words did not plainly state what was happening. | Fixed | New opening sentences define divergence and name the three central banks before the analogy begins. |
| Factual density | Excellent: specific dates, rate levels, dot-plot shifts, market moves, source URLs. | Strong | No change. |
| Source credibility | Claims map to footnoted central bank releases and market data. | Strong | No change. Consider adding inline source labels directly under each table for GEO citation. |
| Entity clarity | Fed, ECB, RBA, Lagarde, Warsh, Brent, DXY, EUR/USD, AUD/USD, 2s30s are named consistently. | Strong | No change. |
| Comprehensiveness | Covers policy actions, transmission channels, four readings, historical analogs, implications, and open questions. | Strong | No change. |
| Original angle | The "tension" framing — hawkish Fed vs collapsing oil — is the second-order signal. | Strong | No change. |

## AEO findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| Definition pattern | Original opening lacked a plain "X is..." sentence. | Fixed | Opening now states: "Central bank divergence happens when the same macro shock pushes major central banks toward opposite policy decisions." |
| List / table snippets | Tables are already present and snippet-friendly. | Strong | No change. |
| Question-phrased headings | Most H2s were statements. | Fixed | See SEO table for question-form H2s. |
| Quotable paragraphs | Key explanations are concise (40–60 words). | Strong | The channel paragraphs under "How does central bank divergence transmit to markets?" are especially quotable. |
| FAQ schema | Not present. | Fixed | YAML frontmatter now includes a recommended `FAQPage` schema with five high-value questions. If the CMS does not support YAML, paste the same questions as a visible FAQ block before the Sources section. |

## Layer 2-specific findings

| Signal | Finding | Status | Recommendation |
|---|---|---|---|
| No advice framing | No buy/sell recommendations, price targets or return promises. | Strong | No change. |
| Uncertainty labeled | Four readings each with evidence and a hole; "What this does not affect" section. | Strong | No change. |
| Bias declared | Aagman's structural biases are not explicitly flagged in this piece, but none are used as conclusions. | Medium | Optional: add one sentence in the interpretation section noting that Aagman's long-cycle biases (e.g., US reserve-system strength, structurally higher rates) inform what is watched, not what is concluded. This is not strictly necessary because the piece does not lean on those biases. |
| Open ending | Ends with unresolved tension and a question. | Strong | No change. |
| Source table | Sources are footnoted; the two data tables include source columns. | Strong | No change. |

## Recommended changes

The following changes have already been applied to the draft unless marked *[audit only]*.

1. **Location:** YAML frontmatter / H1  
   **Issue:** Missing title, description, slug and schema.  
   **Fix:** Added full frontmatter block with title, 159-character description, slug, Article schema and FAQPage schema.  
   **Priority:** Critical — applied.

2. **Location:** Opening paragraph  
   **Issue:** First 100 words did not answer "what is happening" for GEO/AEO.  
   **Fix:** Inserted two direct-answer sentences before the thermostat analogy: "Central bank divergence happens when the same macro shock pushes major central banks toward opposite policy decisions. In mid-June 2026, the Federal Reserve, European Central Bank and Reserve Bank of Australia delivered exactly that."  
   **Priority:** Critical — applied.

3. **Location:** H2 subheadings  
   **Issue:** Descriptive H2s did not match search/answer-engine query patterns.  
   **Fix:** Rewrote H2s to question form while preserving Substack voice: "What changed? The ECB, RBA and Fed in one week", "How does central bank divergence transmit to markets?", "What makes this divergence unusual?", "What are the four plausible readings?", "What do 1975 and 2015 tell us?", "Implications: what this affects, and what it does not".  
   **Priority:** High — applied.

4. **Location:** After opening paragraph (HTML comment)  
   **Issue:** No internal links to other Aagman content.  
   **Fix:** Added a commented list of five suggested internal links with descriptive anchor text. Writer must replace `LINK` with real URLs.  
   **Priority:** High — partially applied (suggestions in place; URLs pending).

5. **Location:** After "Open question" section or before Sources  
   **Issue:** FAQ schema exists in frontmatter, but a visible FAQ block would further improve snippet capture.  
   **Fix:** *[audit only]* Add a short "Questions this raises" H2 with the five FAQ questions answered in 1–2 sentences each, using the existing body content.  
   **Priority:** Medium.

6. **Location:** Sources section  
   **Issue:** All footnotes use `https://` inline; fine for Substack but consider canonical citation format.  
   **Fix:** *[audit only]* No change required for SEO/AEO. Optional clean-up for readability.

## What to leave alone

- **The analogy.** The thermostat opening remains intact and matches the Substack overlay's 100–150 word analogy guidance.
- **The four-readings structure.** It is the signature Layer 2 move and should not be collapsed into a single narrative.
- **The data tables.** They already serve SEO snippet capture and Layer 2 sourcing discipline.
- **The no-advice discipline and open ending.** Both are correctly executed.

## Verdict

**Optimize and proceed.** The critical SEO/AEO gaps have been closed in the draft. The only remaining tasks are to wire up the internal-link placeholders and, optionally, add a visible FAQ block before publication.
