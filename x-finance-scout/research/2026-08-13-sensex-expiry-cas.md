# Research — Sensex expiry 13 Aug 2026 close-price jump

Source tweet: @_anujsinghal — https://x.com/_anujsinghal/status/2087852120691347751
Claim: Sensex 78000 CE went ₹2 → ₹80; 78000 PE ₹166 → 0; indicative equilibrium price 78,860 at 3:28pm became 79,080 at close (~220 pts).

## Verified context

- **3 Aug 2026: India replaced VWAP closing with a Closing Auction Session (CAS) for F&O stocks.**
  - Old system: closing price = VWAP of last 30 min of continuous trading.
  - New system: continuous trading in F&O stocks ends 3:15pm; CAS runs 3:15–3:35 (transition 3:15–3:20, market+limit orders 3:20–3:25, limit-only with random close 3:28–3:30, matching 3:30–3:35). Derivatives keep trading till 3:40pm.
  - Options settle against the official cash closing price — now set by the auction.
  - Source: Economic Times, 3 Aug 2026 — https://m.economictimes.com/markets/stocks/news/stock-market-closing-time-changes-from-today-what-happens-at-315-330-and-340-pm/articleshow/132817243.cms

- **The exact failure was predicted on day one.** On 3 Aug, Nifty spiked ~200 pts in the last 5 minutes; cash/futures diverged. Rajesh Palviya (Axis Securities): "if similar mismatches emerge during expiry, option settlement could surprise traders because contracts settle against the official cash closing price." A discount-brokerage official advised ignoring the closing print entirely.
  - Source: Moneycontrol, 3 Aug 2026 — https://www.moneycontrol.com/news/business/markets/closing-auction-confusion-here-s-what-traders-should-watch-out-during-tomorrow-s-expiry-13992675.html

- The "indicative equilibrium price" shown during CAS is only indicative — unmatched orders can enter/modify until the random close (3:28–3:30), so the final matched price can gap away from the 3:28 indication.

## Angle

The "who moved the close?" framing is wrong — no fat finger needed. The settlement mechanism changed 10 days ago: a 30-min VWAP (expensive to move) became a 20-min concentrated auction (cheap to tip at the margin) while options trade 5 minutes past the cash close and settle on that auction print. A 220-pt IEP→close gap on expiry day was a when, not an if. Retail weekly sellers are the ones learning the new rules with their own money.
