# IA Outbound — WhatsApp First-Touch Variants (A/B experiment)

**Status:** FINAL copy (2026-08-07, approved by founder)
**Audience:** SEBI-registered Investment Advisers (from `output/sebi_ia_register_2026-08-07.csv`;
WhatsApp-reachable subset in the sheet's "Mobile Numbers" tab, 572 contacts)
**Channel:** WhatsApp, cold first touch, founder-sent
**Experiment:** two competing first messages, 50/50 random split across the pilot batch.
Track `variant`, reply, positive reply, access granted per contact.

---

## Variant A — Credibility-led ("trust the person")

hi {first name}, ajit here. ex prop trader, then fintech (cxo at etmoney, cred). been in and around markets since 2003.

now i'm putting all of that into āagman, a quant platform for indian markets. you describe a strategy in plain words (english, hindi, any indian language) and it screens, backtests, and executes through your own broker.

we're letting a few folks in the industry test it before launch. curious? just reply and i'll have you set up.

check us out at aagman.ai

---

## Variant B — Workflow-led ("see the product")

hi {first name}, ajit here. i've been in markets for the last 25 years, and i'm building āagman (sebi ria).

the shortest way to explain what it does: you type things like

"screen stocks with roe >15% and debt-to-equity <0.5"
"backtest ema 9/21 on banknifty, last 2 years, with fees and slippage"
"every tuesday at 9:20 am, if vix is above 14, sell 1 lot nifty weekly 23400 straddle. exit at 25% profit, 40% stop loss, or 3:15 pm"

and it does them. screen, backtest, deploy, one chat, any indian language.

we're letting a few folks in the industry test it before launch. curious? just reply and i'll have you set up.

check us out at aagman.ai

---

## Experiment notes

- Primary metric: positive-reply rate per variant. Secondary: reply rate, access-granted rate.
- Replies split into "tried the site first" (warmer) vs "replied blind" — log which.
- Pilot batch only (50–100 contacts), spaced sends, WhatsApp Business number.
- Personalization token: {first name} from `contact_person` (fallback: firm name).
- Winner becomes the template for the full register.

## Change log

- 2026-08-07: final founder-approved copy. A: compressed credibility line, "curious? just reply" ask,
  "check us out" close. B: added the weekly-straddle automation example (3rd prompt), "sebi ria" proof
  retained in B only, same ask/close as A. Opt-out line removed from both per founder decision —
  watch spam-report rate on the pilot batch; reinstate if blocks appear.
