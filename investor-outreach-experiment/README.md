# Investor Outreach Experiment

Cold email experiment targeting the top 5,000 ETM investors by estimated rupee balance, promoting [Aagman](https://aagman.ai) as an AI investing desk for Indian markets.

## Quick links

- Parent issues: [aagman-v2#2262](https://github.com/kotilabs/aagman-v2/issues/2262) (persona/messaging), [aagman-v2#2313](https://github.com/kotilabs/aagman-v2/issues/2313) (12 email variations + warm-up)
- Source sheet (top 5,000 by `RUPEE_BAL`): `15zQATsN-sYzHRBbu_z-EzHhx4PeIFeZEfoXJR8t_THM`
- Dub tracking links:
  - Variant 1a: `https://dub.sh/aagman-invest-1a`
  - Variant 2b: `https://dub.sh/aagman-invest-2b`
  - Variant 5b: `https://dub.sh/aagman-invest-5b`

## Files in this folder

| File | Purpose |
|------|---------|
| `experiment-plan.md` | Why, who, how many, schedule, randomization, and current infra |
| `email-copies.md` | Final copies of the 3 live variants with subjects, mailboxes, and links |
| `analytics-infra.md` | Click/open/bounce tracking today and the proper infra we need next |
| `send-script.py` | Working Python script used for today's 150-email batch |

## Status

- 2026-08-08: First 150 emails sent (50 per variant) via Zapmail API using 3 mailboxes on a pre-warmed `replyport.co` domain.
- Tracking columns added to the source sheet: `Sent_1a` (AQ), `Sent_2b` (AR), `Sent_5b` (AS).

## Owner

Aryan / Aagman Growth.
