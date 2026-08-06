# Click Estimation Model — 2-Week Sprint (₹20,000)

Date: 2026-08-06
Campaign: Aagman Waitlist — Search Sprint
Budget: ₹20,000 / 14 days (~₹1,430/day), 25/18.75/18.75/18.75/18.75 split
Source data: Keyword Planner export (July 2025–June 2026, India, 1,801 rows)

## Assumptions

- CTR: 3–5% (exact/phrase match, high message match, new account = no QS history)
- Impression share: 15–50% depending on competition level
- Cluster volumes: Planner monthly searches × (14/30), close-variant aggregation
  discounted where the export clusters terms

## Per-group model

| Group | Budget | Cluster vol (2wks) | Avg CPC | IS | Impressions | Clicks (low–high) | Binding constraint |
|---|---|---|---|---|---|---|---|
| Stock Screener | ₹5,000 | ~37,000 | ₹1–3 | 30–50% | 11,000–18,500 | 330–700 | Impression share — will under-spend |
| Options Strategy | ₹3,750 | ~11,600 | ₹35–50 | 20–35% | 2,300–4,000 | 75–120 | Budget (CPC-heavy) |
| Backtest | ₹3,750 | ~11,600 | ₹8–12 | 30–50% | 3,500–5,800 | 150–290 | Volume ceiling |
| Algo Trading | ₹3,750 | ~9,200 | ₹50–65 | 20–30% | 1,800–2,800 | 55–80 | Budget (CPC-heavy) |
| AI Trading | ₹3,750 | ~4,600–7,000 | ₹40–60 | 15–25% | 700–1,750 | 40–80 | Budget + competition |
| **Total** | **₹20,000** | | | | | **650–1,270** | |

**Most likely landing zone: 800–1,000 clicks over 14 days (pre-reallocation).**

## Signup projection

| Waitlist conversion rate | Signups |
|---|---|
| 8% (pessimistic) | ~65–100 |
| 12% (realistic) | ~95–120 |
| 15% (optimistic) | ~120–190 |

## Structural notes

1. **Screener under-spends by design.** At ₹1–3 CPC it yields 330–700 clicks for
   ₹500–1,500, leaving ₹3,500–4,500 unspent. That surplus is the day-7 reallocation
   fuel for the budget-capped groups (options/AI/algo), lifting their clicks ~30–50%.
2. **Blended CPC should land ₹20–25.** If actual blended CPC exceeds ₹30, the
   screener group is not winning impression share — nudge its bids.
3. **Post-reallocation total: ~1,100–1,400 clicks.** The table is the
   pre-reallocation state; day-7 shift pushes toward the upper band.

## Validation checkpoints

- Day 4: compare actual impressions per group vs. this model's IS assumptions.
  If screener IS <20%, raise bids toward the ₹1.4 top-of-page mark.
- Day 7: compare actual CPCs vs. modeled ranges; reforecast before reallocating.
- Day 14: final actuals vs. model — feeds the credit-phase (₹20K) allocation model.
