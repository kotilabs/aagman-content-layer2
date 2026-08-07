# IA Outbound — Email First-Touch Variants (A/B experiment)

**Status:** FINAL copy (2026-08-07), email versions of the approved WhatsApp variants
**Audience:** SEBI-registered Investment Advisers — email-reachable set (1,013 contacts in the register with emails)
**Channel:** Cold email, founder-sent
**Experiment:** same A/B logic as the WhatsApp arm. 50/50 random split. Track variant, open,
reply, positive reply, access granted per contact.

---

## Variant A — Credibility-led ("trust the person")

**Subject options (pick one per test cell):**
1. `from one market person to another`
2. `early access — a few folks in the industry`
3. `what i'm building after etmoney and cred`

hi {first name},

ajit here. ex prop trader, then fintech (cxo at etmoney, cred). been in and around markets since 2003.

now i'm putting all of that into āagman, a quant platform for indian markets. you describe a strategy in plain words (english, hindi, any indian language) and it screens, backtests, and executes through your own broker.

we're letting a few folks in the industry test it before launch. curious? just reply to this mail and i'll have you set up.

check us out at aagman.ai

ajit
founder, āagman

---

## Variant B — Workflow-led ("see the product")

**Subject options (pick one per test cell):**
1. `type it, it trades`
2. `"sell 1 lot nifty straddle if vix is above 14" — like that`
3. `a screener, backtester and execution desk in one chat`

hi {first name},

ajit here. i've been in markets for the last 25 years, and i'm building āagman (sebi ria).

the shortest way to explain what it does: you type things like

"screen stocks with roe >15% and debt-to-equity <0.5"
"backtest ema 9/21 on banknifty, last 2 years, with fees and slippage"
"every tuesday at 9:20 am, if vix is above 14, sell 1 lot nifty weekly 23400 straddle. exit at 25% profit, 40% stop loss, or 3:15 pm"

and it does them. screen, backtest, deploy, one chat, any indian language.

we're letting a few folks in the industry test it before launch. curious? just reply and i'll have you set up.

check us out at aagman.ai

ajit
founder, āagman

---

## Email-specific notes

- Subject lines are part of the experiment — keep subject constant within a cell, or run subject as a
  second factor only after the message winner is clear. Don't A/B everything at once on 100 contacts.
- One link only (aagman.ai at the end). Cold email with multiple links eats deliverability.
- Plain text, no images, no buttons. It should read like ajit typed it, because that's the whole play.
- Send from a real founder mailbox (ajit@aagman.ai or similar) with proper SPF/DKIM/DMARC — not a
  marketing tool's shared IP. If volume scales beyond the pilot, move to a subdomain (e.g. mail.aagman.ai)
  to protect the main domain's reputation.
- Unsubscribe/opt-out: one line in the footer for the email arm ("not relevant? reply 'no' and you're off
  the list"). Email is more regulated-reader territory than WhatsApp; keep it.
- Personalization token: {first name} from `contact_person` (fallback: firm name).

## Change log

- 2026-08-07: email versions derived from the founder-approved WhatsApp finals. Content kept near-identical
  for cross-channel comparability; added subject lines, sign-off block, and email deliverability notes.
