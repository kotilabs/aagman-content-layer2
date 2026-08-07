# IA Outbound — WhatsApp First-Touch Variants (A/B experiment)

**Audience:** SEBI-registered Investment Advisers (from `output/sebi_ia_register_2026-08-07.csv`)
**Channel:** WhatsApp, cold first touch, founder-sent
**Experiment:** two competing first messages, 50/50 random split across the pilot batch.
Track `variant`, reply, positive reply, access granted per contact.

Shared rules: lowercase founder voice, one ask, opt-out line visible, no pricing talk,
no return claims. Brand is written `āagman` (lowercase, macron); URL stays `aagman.ai`.

---

## Variant A — Credibility-led ("trust the person")

hi {first name}, ajit here. ex cxo at etmoney, early team at cred, prop trader since 2003.

i'm building āagman: describe a strategy in plain words (english, hindi, any indian
language) and it screens, backtests, and executes through your own broker,
approval-gated at every money step.

we're letting a few folks in the industry test it before launch. read about us
here: aagman.ai

if not relevant, just say "no" and i won't write again.

---

## Variant B — Workflow-led ("see the product")

hi {first name}, ajit here. ex cxo at etmoney, early team at cred, prop trader since 2003.

the shortest way to explain what i'm building (āagman): you type things like

"screen stocks with roe >15% and debt-to-equity <0.5"
"backtest ema 9/21 on banknifty, last 2 years, with fees and slippage"

and it does them. screen, backtest, deploy, one chat, any indian language.

we're letting a few folks in the industry test it before launch. read about us
here: aagman.ai

---

## Experiment notes

- Primary metric: positive-reply rate per variant. Secondary: reply rate, access-granted rate.
- Replies split into "tried the site first" (warmer) vs "replied blind" — log which.
- Pilot batch only (50–100 contacts), spaced sends, WhatsApp Business number.
  Register phones are ~1/4 missing + some landlines; expect ~60–70% WhatsApp reachability.
- Personalization tokens: {first name} from `contact_person` (fallback: firm name).
- Winner becomes the template for the full register (1,013 with emails / phone-reachable set).
