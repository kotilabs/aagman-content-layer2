# Keyword & Ad-Group Plan — Āagman Waitlist Campaign

**Status: FINAL — grounded in Keyword Planner export (July 2025–June 2026, India, 1,801 rows).**
Budget: ₹75,000 / 6 weeks (~₹1,785/day). Search only.

---

## 1. Ad groups — angles mapped to demand clusters

| Ad Group | Intent theme | Angle(s) | Copy variant | Budget share |
|---|---|---|---|---|
| AG1 — Stock Screener | "find stocks" tool intent | **Angle 4** (Screener that doesn't stop at screening) | v6 | **35%** |
| AG2 — Options Strategy Builder | F&O strategy-building intent | **Angle 13** (no-code: describe the rule, deploy it) + Angle 15 offer in descriptions | v3 | **20%** |
| AG3 — Backtest | "test a strategy" intent | **Angle 3** (backtest in one sentence) + **Angle 1** (prove it before you trade it) | v1 + v2 | **15%** |
| AG4 — Algo Trading (broker-anchored) | "algo trading + broker name" intent | **Angle 6** copy ("Algos your broker app hides") — *keywords are the broker cluster, not TWAP/VWAP*; Angle 7 (capital stays at broker) in descriptions | v4 | **15%** |
| AG5 — AI Trading | "AI + trading" intent | **Angle 5** — contested zone (draconic), included per stakeholder request | v5 | **15%** |

**Cannibalization guard (Angles 1 & 3):** both live in AG3 but on separate intents — Angle 3's copy serves "backtest" queries; Angle 1's serves "prove/test before trading" phrasing within the same ad group via RSA asset pinning, not separate ad groups (the data shows one backtest cluster, not two).

---

## 2. Keywords with match types, volume, and bid ranges

Only terms present in the demand data. Exact + phrase per playbook.

### AG1 — Stock Screener (35%)
| Keyword | Match | Volume/mo | Top-of-page bid |
|---|---|---|---|
| stock screener | [exact] + "phrase" | 50,000 | ₹0.3–1.4 |
| stock screener free | [exact] + "phrase" | 5,000 | ~₹0.3–1.4 (cheap cluster) |
| best stock screener india | [exact] + "phrase" | 5,000 | ~₹0.3–1.4 |
| screener for indian stocks | [exact] + "phrase" | 5,000 | ~₹0.3–1.4 |

Excluded: bare "screener" (5,000,000/mo — navigational for screener.in; flag as future conquesting test, not week 1); "us stock screener" (wrong market).

### AG2 — Options Strategy Builder (20%)
| Keyword | Match | Volume/mo | Top-of-page bid |
|---|---|---|---|
| option trading | "phrase" only (not exact — broad head term, watch SQR) | 50,000 | (cluster ₹17–150) |
| options strategy builder | [exact] + "phrase" | 5,000 | ₹39–150 |
| straddle strategy | [exact] + "phrase" | 5,000 | (cluster range) |
| iron condor strategy | [exact] + "phrase" | 5,000 | (cluster range) |
| strangle | "phrase" only, with negatives (ambiguous bare term) | 5,000 | (cluster range) |
| free option strategy builder | [exact] + "phrase" | 500 | (cluster range) — pairs with free-beta offer |

Excluded: "straddle chart" (50,000/mo but informational — chart lookups, not tool intent).

### AG3 — Backtest (15%)
| Keyword | Match | Volume/mo | Top-of-page bid |
|---|---|---|---|
| backtest trading strategy | [exact] + "phrase" | 5,000 | ₹4–20 |
| free backtest software | [exact] + "phrase" | 5,000 | (₹4–20 cluster) |
| how do i backtest a trading strategy | [exact] only — informational phrasing, cheapest watch item | 5,000 | (₹4–20 cluster) |

### AG4 — Algo Trading, broker-anchored (15%)
| Keyword | Match | Volume/mo | Top-of-page bid |
|---|---|---|---|
| algo trading zerodha | [exact] + "phrase" | 5,000 | ₹17–79 |
| algorithmic trading in zerodha | [exact] + "phrase" | 5,000 | (₹17–120 cluster) |

Note: broker *names* are the query language here — this is the search home for the "institutional order types via your broker" message. Do NOT add "TWAP"/"VWAP" as keywords (zero volume, confirmed).

### AG5 — AI Trading (15%, capped)
| Keyword | Match | Volume/mo | Top-of-page bid |
|---|---|---|---|
| ai trading (variants) | [exact] + "phrase" | 5,000 across variants | ₹28–163, Medium competition |

⚠️ **Data caveat:** the export summary names the cluster ("AI trading variants," 5,000/mo aggregate, ₹28–163) but not the individual term-level rows. Before launch, pull the exact variant terms from the export and add them individually; do not enter the auction on a broad interpretation of "AI trading." Judge this group on **verified-signup CPA only**, kill it if week-2 CPA runs >2× the backtest group.

**Kill rule applied:** nothing in this plan sits under 50/mo except "free option strategy builder" (500/mo — kept deliberately as the offer-pairing term) and no other sub-threshold terms are included.

---

## 3. Budget share reasoning (one line each)

- **AG1 Screener — 35% (~₹26K):** 65K/mo combined volume at ₹0.3–1.4 CPC = the cheapest clicks in the account by 10–50×; volume × CPC economics make this the signup-volume engine.
- **AG2 Options — 20% (~₹15K):** highest-intent F&O cluster but ₹39–150 bids; 20% buys meaningful volume without letting CPCs eat the test budget.
- **AG3 Backtest — 15% (~₹11K):** 15K/mo at ₹4–20 — cheap clicks, moderate volume; this is where the two winning angles (1 & 3) prove out.
- **AG4 Algo — 15% (~₹11K):** 10K/mo broker-anchored at ₹17–120; moderate CPCs against high-intent queries — sized to learn whether the execution-depth message converts.
- **AG5 AI — 15% (~₹11K, hard cap):** highest CPCs in the set (₹28–163, draconic's contested zone); capped at 15% and first in line for reallocation if CPA underperforms.

Shares follow the demand-data allocation (35/20/15/15/15), which is volume × CPC-derived, not an even split. Daily pacing: ~₹625 / ₹357 / ₹268 / ₹268 / ₹268.

---

## 4. Zero-demand angles → education plays (not Search)

| Angle | Data verdict | Route |
|---|---|---|
| **Angle 2 — Paper trade with live prices** | 0 terms ≥50/mo. Dead. | Drop from Search entirely. Also still "Partially" per §16 — LP workflow mention only. |
| **Angle 6 as keywords (TWAP/VWAP/institutional execution)** | Zero search volume for order-type terms. | **Education play** — the *copy* survives on AG4's broker-anchored keywords; the *vocabulary* goes to video/LP content. Do not invent TWAP/VWAP keywords. |
| **Angle 13's "no code" framing as keywords** | "no code algo trading" = 50/mo — marketing-speak, not query language. | The angle survives as *copy* in AG2; the phrase never becomes a keyword. |
| **Angle 8 — SEBI-registered/NSE-empanelled** | Regulatory terms: zero volume. | Trust asset → descriptions, sitelinks, LP. Never a headline keyword. |
| **Angles 7, 9, 14 — broker-custody / whitebox / kill switches** | No demand cluster (insider vocabulary). | Descriptions/sitelinks/LP trust blocks. |
| **Conquesting (sensibull/opstra alternative)** | 50/mo — too thin to learn from in 6 weeks. | Revisit post-launch with remarketing, not cold Search. |
| **Angle 10 — Invest in your language** | Not testable on English Search; out of channel scope. | YouTube/vernacular surfaces in a later campaign. |

---

## 5. Campaign-level negative themes (week one)

- **Navigational/incumbent:** "screener.in" and bare-navigational drift (the 5M/mo term stays excluded by keyword selection, not negatives — add "screener in" as negative phrase if SQR shows leakage).
- **Wrong market:** us stock, us market, nyse, nasdaq, forex, crypto — unless confirmed in scope (SoT: Indian equities/F&O).
- **Informational-only:** chart, charts (kills "straddle chart"), meaning, what is, pdf, book, course, tutorial free-course variants — *but keep "free" itself* (it's a qualified modifier in AG1/AG2/AG3); negate only informational free-compounds as they appear.
- **Jobs/careers:** job, jobs, salary, career, internship, interview.
- **DIY-code intent (mismatched persona):** python, github, code, api documentation — searchers wanting to build, not use. (Watch: some algo-python searchers may convert to no-code; judge from week-1 SQR before hardening.)
- **Unshipped capability drift:** mcx, commodity, commodities (MCX marked coming-next — do not pay for clicks we can't serve).
- **Tips/tips-provider spam:** tips, telegram, sure shot, jackpot — low-quality, compliance-adjacent queries.
- **Movie/ambiguous-term bleed** for "strangle": review- and film-related terms as they surface.

---

## 6. Campaign settings

- **Network:** Google Search only. Display Network OFF. Search partners OFF for week 1 (revisit after clean baseline).
- **Location:** India, "Presence" targeting (not "Presence or interest"). No language/geo exclusions assumed — pan-India per brief; confirm metro-only split only if budget pressure demands it.
- **Language:** English (Angle 10/vernacular explicitly out of scope for this campaign).
- **Bidding:** Manual CPC, new account per playbook. Initial bids at the **low-to-mid bid range per cluster**: ₹1–2 screener, ₹40–60 options, ₹5–10 backtest, ₹20–40 algo, ₹30–50 AI. No automated strategies until 30+ verified conversions exist (and no PMax regardless — out of scope).
- **Match-type hygiene:** exact + phrase only, no broad.
- **Ad scheduling:** launch 24/7 for the investor-facing groups (AG1, AG3); for AG2/AG4 (F&O intent) consider weighting to market hours (9:00–11:30, 13:30–15:30 IST) after week-1 hour-of-day data — don't pre-restrict a 6-week test.
- **Conversion setup (prerequisite, flagged from brief):** "verified signup" must be the primary conversion action — requires GCLID capture on the waitlist form + offline conversion upload (email/WhatsApp-verified event), otherwise Smart-manual bidding optimizes toward raw form fills and the per-angle CPA comparison is meaningless. **Confirm verification definition before launch.**
- **Week-1 ritual:** pull search terms report → move converting queries to exact, add drift negatives, compare actual vs. Planner volumes. Planner is the forecast; SQR is the truth.

---

## Open confirmations before launch (unchanged from brief)

1. "Verified signup" definition + offline conversion tracking live?
2. Offer claims approved: "Free in beta, no card" / "legacy rates forever" (needed in AG2 copy)?
3. Waitlist LP live, mobile-fast on 4G?
4. Pull term-level AI-trading rows from the export to populate AG5 keywords.