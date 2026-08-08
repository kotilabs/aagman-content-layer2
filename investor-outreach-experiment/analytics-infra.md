# Analytics Infrastructure — Investor Outreach

## What we can measure today

### 1. Clicks (via Dub)

- Each variant has a unique Dub short link.
- Dub gives us: total clicks, unique clicks, countries/devices, referrer, timestamp.
- **Signal:** relative click rate per variant.
- **Limitation:** clicks only. No opens, no bounces, no reply attribution.

### 2. Send status (via Zapmail API response)

- `send_email` returns `success` + `messageId`.
- We log it to `/tmp/send_today_150_results.json` and mark the sheet.
- **Signal:** delivery acceptance by Gmail.
- **Limitation:** acceptance ≠ inbox placement. No bounce/complaint feedback in this endpoint.

### 3. Google Sheet tracking

- Columns: `Sent_1a` (AQ), `Sent_2b` (AR), `Sent_5b` (AS)
- Manual/update script marks "yes" per recipient.
- Future columns to add:
  - `Clicked` (timestamp or Dub event id)
  - `Opened` (if pixel enabled)
  - `Replied`
  - `Converted` (signed up / onboarded)

## What we cannot measure yet

- **Opens:** no tracking pixel in the current text emails.
- **Bounces:** Zapmail `send_email` does not return bounce status synchronously.
- **Replies:** not surfaced via the API endpoint we use.
- **Spam placement:** no seed-list or inbox-placement tool.
- **Downstream conversion:** Dub → GA4 → sign-up event is not yet wired.

## Proper infra we need next

### Option A — Mail suite on the existing Zapmail mailboxes

- Add a 1x1 transparent tracking pixel hosted on a domain we control.
- Append `?r=<recipient_id>&v=<variant>` to the pixel URL.
- Parse replies via Gmail API or Zapmail's fetch-emails endpoint.
- Pros: minimal cost, keeps current domain.
- Cons: manual, does not scale to high volume, weak deliverability monitoring.

### Option B — Dedicated outbound platform (recommended)

Tools: **Instantly**, **Smartlead**, or **Reachinbox**.

| Capability | Why it matters |
|------------|----------------|
| Multiple rotating senders + warming | Scale past 50/day/mailbox safely |
| Unified inbox / reply handling | See replies without polling Gmail |
| Open/click/reply/bounce analytics | Full funnel visibility |
| Lead list + campaign management | Upload CSV, assign variants, schedule sequences |
| A/B testing + winner auto-rotate | Pick best subject/body automatically |
| Unsubscribe & bounce handling | Stay compliant, protect domain rep |

### Option C — Build a lightweight orchestrator

- Keep Zapmail for sending.
- Add a small service that:
  - reads the Google Sheet,
  - assigns variants randomly,
  - schedules sends via cron,
  - stores events in a database or Notion,
  - exposes a tiny dashboard.
- Pros: fully controlled.
- Cons: engineering time; still lacks deliverability depth of a dedicated tool.

## Recommended next actions

1. **Short term (this week):**
   - Use Dub clicks as the primary win metric for the first 150 sends.
   - Add `Clicked` and `Replied` columns to the source sheet.
   - Manually check reply mailboxes (`sean@`, `seth@`, `dale@replyport.co`) daily.

2. **Medium term (next 2 weeks):**
   - Evaluate Instantly vs Smartlead vs Reachinbox on price and India deliverability.
   - Migrate the remaining 4,850 recipients into the chosen tool.
   - Wire Dub/UTM → GA4 → sign-up event for downstream attribution.

3. **Guardrail metrics:**
   - Bounce rate < 5%
   - Complaint rate < 0.1%
   - Daily send cap per mailbox until tool warming is complete
   - Stop a variant if click rate is materially lower than the others

## UTM / attribution notes

- Dub links currently redirect to `https://aagman.ai` (or the target landing page).
- To see campaign data in Google Analytics, append UTM params to the destination URL in Dub:
  - `utm_source=zapmail`
  - `utm_medium=email`
  - `utm_campaign=investor-outreach-aug2026`
  - `utm_content=<variant>` (e.g., `1a`, `2b`, `5b`)
- This lets GA4 report sessions and conversions by variant.
