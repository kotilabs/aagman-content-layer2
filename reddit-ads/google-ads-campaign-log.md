# āagman Google Ads — Campaign Log

## 2026-08-07 — Search campaign built and verified, PAUSED

**Status:** Fully built and verified in Google Ads · Campaign **PAUSED** (spending nothing)

### Campaign setup

| Field | Value |
|---|---|
| Account | 9442115425 |
| Campaign name | Aagman Waitlist — Search |
| Network | Search-only (Display Network OFF, Search partners OFF) |
| Geo / Language | India presence-only / English |
| Bid strategy | Manual CPC |
| Daily budget | ₹1,430/day |
| Status | PAUSED |

### Ad groups

| Ad group | Default CPC | Theme |
|---|---|---|
| Screener | ₹1.5 | Stock/fund screening |
| Options | ₹50 | Options trading |
| Backtest | ₹7.5 | Strategy backtesting |
| Algo | ₹30 | Algorithmic trading |
| AI | ₹40 | AI investing assistant |

- **Keywords:** 34 exact + phrase match
- **Campaign negatives:** 22
- **Ads:** 5 RSAs
- **Assets:** 3 callouts

### Tracking & attribution

- **GCLID capture:** Live on `aagman.ai` — cookie set on `.aagman.ai`, 90-day expiry.
- **GA4 event:** `get_started_click` with `gclid_present` parameter (via GTM, published).
- **GA4 ↔ Google Ads:** Linked.
- **Cookie chain tested end-to-end:** `?gclid=test123` survives landing → redirect → Get Started → readable on `app.aagman.ai`.

### Conversion actions (offline click-import, 90-day window, one-per-click)

| Conversion | ID | Role |
|---|---|---|
| Verified Signup | 7711551329 | Primary |
| Form Submit | 7711551332 | Secondary |

### Open items

- [ ] End-to-end Ad Preview test: click → gclid in URL → submit test lead → confirm gclid in lead store → upload test conversion → confirm it appears in Google Ads (~24h)
- [ ] Enable campaign after test passes

### Notes

- Campaign is ready to launch once the offline conversion upload workflow is verified.
