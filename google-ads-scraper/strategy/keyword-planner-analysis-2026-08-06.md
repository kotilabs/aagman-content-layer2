# Keyword Planner Analysis — 2026-08-06

Source: Keyword Planner export (Google Sheets, July 2025 – June 2026 data, India).
Seed list: 55 terms (`keyword-research-seed-list.md`) + URL discovery on competitor pages.
1,801 rows analyzed, deduped.

## Headline findings

1. **Screener is the goldmine, not backtest.** "stock screener" = 50,000/mo at ₹0.3–1.4
   top-of-page bid. "stock screener free" (5,000/mo), "best stock screener india" (5,000/mo),
   "screener for indian stocks" (5,000/mo) all similarly cheap. Tradomate validated the
   demand; nobody is bidding it up. → Screener ad group gets largest budget share (~40%).

2. **Options strategy = high-intent F&O cluster.** "option trading" (50,000/mo),
   "options strategy builder" (5,000/mo, ₹39–150), "straddle strategy" (5,000/mo),
   "iron condor strategy" (5,000/mo), "strangle" (5,000/mo). Pricier but action-ready.
   "free option strategy builder" (500/mo) pairs v3 with the free-beta offer. → ~25% budget.

3. **Backtest is real but smaller.** "backtest trading strategy" (5,000/mo, ₹4–20),
   "free backtest software" (5,000/mo), "how do i backtest a trading strategy" (5,000/mo).
   Cheap clicks. → ~20% budget.

4. **Algo searches are broker-anchored.** "algo trading zerodha" (5,000/mo, ₹17–79),
   "algorithmic trading in zerodha" (5,000/mo). People search algos BY BROKER NAME.
   This is the search home for v4's "algos through your broker" message. → ~15% budget.

5. **TWAP/VWAP/institutional-execution terms have ZERO search volume.**
   v4 angle is education, not intent-harvesting. The v4 copy still runs — against the
   algo-trading keywords, where "Algos Your Broker App Hides" fits the intent.

6. **Paper trading: dead** (0 terms ≥50/mo). Removed.

7. **AI trading is contested** — 5,000/mo across variants but Medium competition,
   ₹28–163 bids (Draconic's zone). Skipped for week 1 to avoid auction premiums.

8. **"screener" bare term = 5,000,000/mo** but ~all navigational for screener.in.
   Excluded from core list; flagged as future conquesting candidate.

9. **"us stock screener" (5,000/mo)** — wrong market, excluded.

10. **Intraday strategy terms all ≤50/mo each** — too thin to learn from in 6 weeks.

## Surprises vs. the seed list

- Seed-list hits: screener cluster, options strategy cluster, backtest cluster (roughly
  as predicted, though screener volume was underestimated 10x).
- Seed-list misses: TWAP/VWAP (zero), paper trading (zero), regulatory terms (zero),
  "no code algo trading" (50/mo — the "no code" framing is marketing-speak, not query language),
  "sensibull alternative" / "opstra alternative" (50/mo — conquesting volume too thin for week 1).
- Discovered via URL expansion: "free backtest software" (5,000/mo), broker-anchored algo
  searches, "straddle chart" (50,000/mo but informational — chart lookups, not tool intent).

## Budget allocation — 2-week sprint (₹20K + ₹20K Google credit follow-on)

**Structure decided 2026-08-06:** ₹20,000 over 14 days (~₹1,430/day), then a
₹20,000 Google credit (spend-₹20K-get-₹20K offer) funds weeks 3–4 based on results.

Flattened split for cross-surface learning (first campaign = buy data across all
angles, not maximum cheap signups):

| Ad Group | Copy variant | Share | ₹ (2 wks) | Est. clicks | Why |
|---|---|---|---|---|---|
| Stock Screener | v6 | 25% | ₹5,000 | ~400–500 | Cheapest CPCs; capped naturally by impression share at ₹0.3–1.4 bids |
| Options Strategy | v3 | 18.75% | ₹3,750 | ~75 | High-intent F&O; directional verdict possible |
| Backtest | v1 + v2 | 18.75% | ₹3,750 | ~200 | Volume-capped (~15K/mo cluster); cannot spend more regardless |
| Algo Trading | v4 | 18.75% | ₹3,750 | ~60 | Broker-anchored; directional verdict |
| AI Trading | v5 | 18.75% | ₹3,750 | ~60 | Contested zone; kept for long-term category ownership data |

**Rejected:** equal 20/20/20/20/20 split — strands ₹2–3K in screener/backtest
(impression-share and volume capped) while expensive groups starve.

**Day-7 reallocation rule (non-negotiable):** over-allocate daily budgets slightly;
on day 7 move whatever screener/backtest didn't spend into whichever of
options/algo/AI shows best CTR. The split is a starting hypothesis, not a
14-day commitment.

**Sprint decision rules:**
- Days 1–3: launch all 5 groups, verify ads approved + tracking fires. No changes.
- Day 4: first search-terms review; add junk negatives (tips, jobs, courses).
- Day 7: swap weakest headlines in any group with CTR <2% after 100+ impressions;
  pause any keyword with ₹1,000+ spend and zero signups; reallocate per rule above.
- Days 8–14: shift ~20% of daily budget toward best cost-per-signup groups.
- Day 14: credit-phase decision — 70–80% of the ₹20K credit goes into the 1–2
  angles with the cheapest verified signups, remainder continues exploration.
  If nothing converted, credit funds the LP/offer fix before more media spend.

**Signup projection:** ~650–950 clicks over the sprint; at 8–15% waitlist
conversion = ~50–140 verified signups.

## Next data step

After week 1: pull the search terms report, compare actual queries vs. this list,
move winners to exact match, add negatives for drift. Keyword Planner volume is a
forecast; the search terms report is the truth.
