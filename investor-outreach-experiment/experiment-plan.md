# Experiment Plan — Investor Outreach

## Goal

Validate messaging and drive sign-ups/interest from high-AUM Indian retail investors by sending cold emails to the top 5,000 ETM investors ranked by estimated rupee balance (`RUPEE_BAL`).

## Target persona

- Indian retail investors with meaningful portfolio balance
- Already research stocks/funds but do it across many tabs/tools
- Frustrated by: fragmented research, manual monitoring, delayed execution
- Wants: one AI investing desk for Indian markets in English/Hinglish/regional languages

## Audience source

- Sheet ID: `15zQATsN-sYzHRBbu_z-EzHhx4PeIFeZEfoXJR8t_THM`
- Sorted by `RUPEE_BAL` descending (top 5,000 rows)
- Columns: rank, name, email, `RUPEE_BAL`, and tracking flags

## Live variants

We selected 3 variants from the original 12-variant matrix in [aagman-v2#2313](https://github.com/kotilabs/aagman-v2/issues/2313):

| Variant | Mailbox | Angle | Dub link |
|---------|---------|-------|----------|
| 1a | sean@replyport.co | Research fragmentation pain | `https://dub.sh/aagman-invest-1a` |
| 2b | seth@replyport.co | Set-and-forget automation | `https://dub.sh/aagman-invest-2b` |
| 5b | dale@replyport.co | One desk for the whole loop | `https://dub.sh/aagman-invest-5b` |

## Send cadence

- 50 emails per mailbox per day = 150 total per day
- Sent via Zapmail API using pre-warmed `replyport.co` Google Workspace
- Throttle: 30–60 second random delay between consecutive sends
- Daily batches avoid mailbox reputation damage and keep us inside sane warm-up limits

## Randomization rules

- Each recipient receives exactly one variant.
- Assignment is randomized per batch so no variant hogs the top ranks.
- The script shuffles the full send list before dispatch to avoid mailbox/IP clustering.
- Result is recorded in the source sheet:
  - `Sent_1a` (column AQ) = "yes"
  - `Sent_2b` (column AR) = "yes"
  - `Sent_5b` (column AS) = "yes"

## Current infra

| Layer | Tool | Notes |
|-------|------|-------|
| Mailboxes + sending | Zapmail API (`api.zapmail.ai/api/v2/onebox/send-email`) | Pre-warmed `replyport.co` domain |
| Link tracking | Dub (`dub.sh`) | UTM + click analytics per variant |
| Recipient data | Google Sheets (gws CLI) | Source of truth for ranks and sent flags |
| Execution | `send-script.py` (this folder) | Randomized, throttled, retries 3x |

## Open questions / risks

- We do not yet have reliable open tracking; click-through is the only hard signal.
- Zapmail does not expose detailed send analytics (opens/clicks/bounces) in the API we are using.
- We need to graduate to a proper outbound tool (Instantly, Smartlead, or Reachinbox) for volume, deliverability, and analytics.

## Next steps

1. Complete today's 150 sends and mark sheet columns.
2. Watch Dub click data per variant for 48–72 hours.
3. Decide winning message based on click rate.
4. Build analytics infra documented in `analytics-infra.md`.
