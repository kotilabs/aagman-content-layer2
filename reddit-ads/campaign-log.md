# āagman Reddit Ads — Campaign Log

## 2026-08-07 — First test submitted for approval

**Status:** Submitted for Reddit review · Campaign PAUSED pending approval + founder go

### Campaign setup

| Field | Value |
|---|---|
| Objective | Conversions |
| Optimization event | Lead |
| Bid strategy | Lowest Cost |
| CPC cap | $1.00 (mandatory field) |
| Geo | India only |
| Placements | Feed + Conversation |
| Expansion targeting | OFF |
| Total budget | $140 ($10/day × 7 days × 2 ad groups) |

### Ad groups

#### AG1 — Traders
- **Daily budget:** $10
- **Duration:** 7 days
- **Format:** Text-only promoted post
- **Copy:** AD 1 from `creative-v1.md` (founder voice, viral post verbatim)
- **Communities:** IndiaAlgoTrading, algotrading, IndianStreetBets, IndianStockMarket
- **Landing page:** `https://www.aagman.ai/?utm_source=reddit&utm_medium=paid&utm_campaign=aagman_test_1&utm_content=ad1_traders`
- **CTA:** Learn More
- **Comments:** ON

#### AG2 — Investors
- **Daily budget:** $10
- **Duration:** 7 days
- **Format:** Text-only promoted post
- **Copy:** AD 2 from `creative-v1.md`
- **Communities:** r/personalfinanceindia, r/FIRE_Ind, r/mutualfunds, r/IndianFIRE, r/investing
- **Landing page:** `https://www.aagman.ai/invest?utm_source=reddit&utm_medium=paid&utm_campaign=aagman_test_1&utm_content=ad2_investors`
- **CTA:** Learn More
- **Comments:** ON

### Tracking

- Reddit Pixel ID: `a2_hiwsqs0yjt0p`
- Pixel installed on:
  - `aagman-website/index.html`
  - `aagman-website/invest/index.html`
- Events configured:
  - `PageVisit` on every page load
  - `Lead` when user clicks any link containing `app.aagman.ai`

### Open items

- [ ] Reddit approval (~24–48h; finance may take longer)
- [ ] Founder go to enable spend
- [ ] SEBI/BASL pre-approval status (ads submitted; verify compliance posture before enabling)
- [ ] Set up comment-reply library for predictable objections
- [ ] Verify Pixel events fire correctly via Reddit Events Manager after deploy

### Notes

- AD 3 (founder's letter) deferred to a later test.
- Retargeting ad group deferred until Pixel has enough traffic.
- Campaign built using Advanced Create.
