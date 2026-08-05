# Āagman — Source of Truth: Product Capabilities (User POV)

> Last updated: 2026-08-04
> Purpose: A single reference document for content, marketing, and product messaging. It describes what Āagman can do from the user’s point of view, not the engineering implementation.
> Scope: Public website (`aagman.ai`) + `kotilabs/aagman-v2` repo docs/codebase. Bugs and internal issues are intentionally excluded.

---

## 1. Product Identity & Promise

**One-line positioning:** “An AI trading team built for Indian markets.”
**Investor-facing framing:** “Research. Plan. Invest. Go to work.”

**What it is:** A natural-language trading and investing workspace. The user describes a strategy, screen, or order in the language they think in, and a team of specialized AI agents turns it into a screen, a backtest, a paper trade, or a live deployment — with the user approving every step that involves real capital.

**What it is not:**
- Not a broker (capital stays in the user’s existing broker account).
- Not a tip/signal service.
- Not an autonomous trading bot that can deploy without approval.

**Core promise:** “You brief, they work, you approve.” The enforced workflow is **Backtest → Paper → Live**.

**Operator:** Koti Labs Private Limited.

---

## 2. Who It Is For

**Primary users:**
- **Active traders:** Indian retail traders in equities, indices, F&O, and commodities who want systematic, rule-based execution.
- **Investors:** Long-term investors and mutual-fund buyers who want to screen quality compounders, track portfolio health, and plan taxes before selling.
- **No-code systematic users:** People who want to build and test strategies/screens without Excel or Python.
- **Multi-lingual users:** Anyone who wants to trade or invest in the language they think in.

**Persona angles for content:**
- The F&O trader who wants a “second opinion” before entering a trade.
- The equity investor looking for quality compounders (high ROE/ROCE, low debt, steady growth).
- The mutual-fund buyer who wants to compare funds by return, expense ratio, sector, or holdings.
- The investor who wants portfolio health checks and tax-impact alerts before selling.
- The trader frustrated that broker apps hide advanced order types and algos.
- The person who wants to invest in Hindi, English, Hinglish, Tamil, Bengali, Telugu, or any other language they use.

---

## 3. The Agent Team

Āagman is organized as a team of specialized agents. The user interacts with them through a single chat.

| Agent | User-Facing Role |
|---|---|
| **Strategy Builder** | Turns a one-line idea into a structured, executable strategy. |
| **Screener** | Scans 500+ stocks, options, commodities in real time. |
| **Charting** | Reads patterns, IV, Greeks, OI — and explains them in plain English. |
| **Research** | Digests earnings, calls, news, filings. |
| **Portfolio** | Watches every position with real-time P&L and exposure. |
| **Risk** | Enforces kill-switches, position limits, and daily loss caps. |
| **Execution** | Places orders, monitors fills, and manages live deployments. |
| **Analytics** | Ranks results, compares strategies, and surfaces winners. |
| **Pulse** | Reads morning sentiment daily before the user wakes up. |

**Additional agents visible in the codebase:** Options Strategy Agent, Allocation Strategy Agent, Backtest Agent, Performance Agent, Market Scanner Agent, Conversation Agent, Chart Clarification Agent, Research Agent, Portfolio Agent.

---

## 4. Core User Workflows

### 4.1 Idea → Strategy → Backtest → Paper → Live
1. The user describes an idea in natural language.
2. The Strategy Builder drafts a strategy.
3. The Backtester proves it on historical data.
4. The user can promote it to paper trading (real-time prices, zero capital).
5. Only after paper results and explicit approval does it go live.

### 4.2 Research Workflow
- **Screen:** returns a filterable table (e.g., “NIFTY 50 stocks with RSI below 30”).
- **Analyze:** returns a score card + written reasoning (e.g., “Research on RELIANCE”).
- Output shapes: score card, bull/bear/base scenarios, comparison, ranking, valuation focus.

### 4.3 Live Deployment Management
- Start, pause, resume, or stop a deployment at any time.
- View open positions, working orders, P&L, and risk status.
- Trigger a kill switch manually or let the system trigger circuit breakers.

### 4.4 Investor Workflow
1. **Screen:** ask for quality compounders, mutual funds, or any fundamental criteria.
2. **Backtest:** see how the screen would have performed historically.
3. **Paper:** track the idea with live prices before committing capital.
4. **Place order:** execute through your broker in plain language (e.g., “Buy 10 Reliance shares if the price drops to ₹2,900”).
5. **Monitor:** get portfolio health checks, tax-impact alerts, and curated news on your holdings.

---

## 5. Markets & Asset Classes

| Asset Class | Coverage | Notes |
|---|---|---|
| **Equities & indices** | NSE / BSE | Cash/equity delivery and intraday. Supports quality-compounder screens (ROE, ROCE, debt, growth). |
| **Futures & Options** | NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX, BANKEX, stock options/futures | Multi-leg strategies supported. |
| **Commodities** | MCX futures | Public site mentions MCX; repo docs show a draft commodity onboarding PRD with continuous contracts. Treat as planned/enhanced unless confirmed shipped. |
| **Mutual Funds** | AMFI scheme codes | Screen by return, expense ratio, category, sector, holdings, ELSS tax-saver track record, etc. |
| **Not supported** | International stocks, crypto, forex, bonds | Explicitly out of scope. |

**Supported timeframes:** `1m`, `5m`, `15m`, `1h`, `1d`. Currently one timeframe per prompt/backtest.

---

## 6. Strategy Building Blocks

### 6.1 Natural-Language Prompt Grammar
A complete prompt should include:
1. Symbol / universe
2. Direction & size
3. Entry rule
4. Exit & risk rule
5. Mode: `backtest`, `paper`, `live`, or `screen`

**Example prompts — traders:**
- “Backtest a long-only EMA crossover on RELIANCE, daily, Jan to Dec 2025.”
- “Find NIFTY 50 stocks where RSI(14) is above 70.”
- “Buy 50 shares of RELIANCE at market, live. Stop-loss 1% below, target 2% above.”
- Hinglish: *“Live deploy karo — NIFTY ka RSI 30 ke neeche jaaye toh BankNifty mein bull call spread daal do.”*

**Example prompts — investors / mutual funds:**
- “Screen for quality compounders — companies above ₹1,000 Cr market cap with consistently high ROE and ROCE, low leverage, and steady revenue and profit growth over 3–5 years.”
- “Best large cap mutual funds by 1-year return.”
- “Low expense ratio flexi cap funds.”
- “ELSS funds with 5+ year track record sorted by returns.”
- “Which mutual funds hold RELIANCE?”
- “Stocks with ROE above 15% and debt-to-equity below 0.5.”
- Hindi/Hinglish: *“Ache fundamentals wale stocks — ROE 15% se zyada, low debt.”*

### 6.2 Indicators & Screeners

**Technical indicators:**
- Trend: SMA, EMA, WMA, DEMA, TEMA, KAMA, MAMA, T3, SAR, TRIMA
- Momentum: RSI, MACD, STOCH, CCI, WILLR, MOM, ROC, AROON, ADX
- Volatility: ATR, BBANDS, NATR
- Volume: OBV, AD, ADOSC
- Patterns: 61 TA-Lib candlestick patterns
- Stats: BETA, CORREL, STDDEV, LINEARREG, TSF, VAR
- Rolling: MAX, MIN, z-score, percentile rank, slope

**Screener metrics:**
- Technical: RSI, MACD, EMA, SMA, ATR, ADX, Bollinger Bands, Stochastic, OBV, candlestick patterns
- Fundamental: P/E, ROE, ROCE, debt-to-equity, Piotroski score, market cap, dividend yield, earnings quality
- Options: IV rank, open interest, PCR
- Mutual funds: 1-year / 3-year / 5-year returns, expense ratio, AUM, category (large cap, flexi cap, ELSS, etc.), sector exposure, top holdings

### 6.3 Position Sizing Models
- Fixed quantity (shares)
- Percent of equity
- Fixed lots (options / commodities)

### 6.4 Exit Types
- Fixed stop loss / take profit (% / points / INR absolute)
- Trailing stop
- Time stop (“exit after N bars”)
- Indicator exit
- Premium-based exits for options (e.g., 100% of premium collected)
- Combined exits (whichever triggers first)

### 6.5 Advanced Rules
- z-scores
- Arithmetic on indicators (e.g., “EMA(20) × 0.97”)
- Time-based entries (day of week, day of month)
- Indicator chaining (e.g., “EMA(10) of RSI(14)”)
- AND / OR condition combining

---

## 7. Order Types & Execution

### 7.1 What Āagman Exposes

**Simple / execution-native order types:**
- Market, Limit, Stop-Loss Limit, Stop-Loss Market
- MIT (Market If Touched)
- LIT (Limit If Touched)
- Market-to-Limit (MTL)
- Trailing stop
- Bracket / Cover / OCO-style structures
- AMO (After Market Order) and IOC

**Options execution:**
- Single-leg equity/F&O
- Multi-leg options: straddles, strangles, iron condors, spreads, butterflies — up to 4 legs placed in sync

**Execution algorithms:**
- TWAP — live
- VWAP — live
- Iceberg — coming next
- POV (Percent of Volume) — coming next

### 7.2 Why This Matters: Retail Broker Comparison

| Order Type / Algo | Typical Indian Retail Brokers | Āagman | Institutional EMS/OMS Desks |
|---|---|---|---|
| Market / Limit / SL / SL-M | ✓ Native | ✓ (relays through broker) | ✓ Native |
| Bracket / Cover / AMO / IOC | ✓ Native | ✓ (relays / composes) | ✓ Native |
| Trailing stop | Mostly via GTT; Dhan has native | ✓ Execution-native | ✓ Native |
| MIT / LIT / Market-to-Limit | ✗ Not exposed in standard retail UI | ✓ Included in 9 native types | ✓ Native on EMS |
| Iceberg / sliced orders | Zerodha, Dhan only | “Coming next” | ✓ Native |
| TWAP / VWAP | ✗ Not in standard retail UI | ✓ Live | ✓ Native |
| POV / IS / Adaptive / Sniper | ✗ Not available to retail | “Coming next” | ✓ Native |

**Content angle:** Āagman surfaces order types and algos that retail broker apps hide, without replacing the broker. It sits between the convenience of a Kite/Upstox app and the power of an institutional EMS.

### 7.3 Broker Integrations

- Public messaging: “Works with all major Indian brokers.”
- Currently documented end-to-end setup: **Zerodha** (via Kite Connect + Chrome Relay extension).
- Repo code shows adapters for: Zerodha, MOFSL, Dhan, Groww, Angel One, plus mock/paper brokers.
- **Relay agent:** a lightweight user-run agent on the user’s machine forwards write API calls from their IP. This satisfies SEBI static-IP whitelisting requirements while keeping strategy logic on Āagman’s servers.

---

## 8. Backtesting & Analytics

### 8.1 Backtest Mechanics
- Evaluates conditions at the **close of a bar**; fills at the **open of the next bar** to avoid look-ahead bias.
- Default assumptions used in examples: 5 bps fees, 3 bps slippage for equity; options costs should be overridden.
- Same Strategy Intermediate Representation (SIR) is intended to drive both backtests and live runs for parity.

### 8.2 Backtest Report Outputs
- Total return, max drawdown, win rate, number of trades
- Sharpe, Sortino, Calmar, profit factor, expectancy
- Equity curve and trade table

### 8.3 Screener Outputs
- Filterable table
- Score card with reasoning
- Ranking / comparison views

---

## 9. Risk, Compliance & Trust

### 9.1 In-Platform Risk Gates
- Four-layer kill switch: deployment, account, workspace, global.
- Pre-trade risk checks before any order goes out.
- Circuit breakers for daily loss, rapid order rate, consecutive rejection, relay offline.
- Two-tier risk engine: per-deployment limits + account-level aggregation across all deployments on the same demat.

### 9.2 Regulatory & Compliance Claims
- **SEBI-registered Investment Adviser:** INA000021951
- **NSE-empanelled algo provider (Whitebox):** under NSE Circular Ref. 40/2026 (3 Jun 2026)
- **Whitebox algorithms:** logic is disclosed and replicable, not black-box.
- All algo orders tagged with an exchange-assigned unique algo ID for audit.
- Data hosted on servers in India; aligned with DPDP Act, 2023.
- **Not a broker, DP, or Research Analyst.**

### 9.3 Security
- Broker credentials are envelope-encrypted; per-credential AES-256 DEK.
- Daily token refresh for brokers with short-lived tokens.
- Audit logging of signals, orders, fills, risk checks, kill switches, and reconciliation events.

---

## 10. Pricing & Access

- **Current status:** Free while in beta; no credit card required.
- Early users are promised “legacy rates — forever” once paid tiers launch.
- No published paid tiers or feature segmentation yet.

---

## 11. Languages & UX

- **Supported languages:** Designed to accept prompts in virtually any language the user thinks in. Public examples include English, Hindi, Hinglish, Tamil, Bengali, and Telugu.
- **Interface:** Chat-first with streaming responses; response types include clarification, setup progress, confirmation, backtest report, final summary, and plain text.

---

## 12. Roadmap / Coming-Soon Capabilities

The following appear in repo docs or public pages but should be treated as planned/coming-soon in content unless explicitly confirmed as shipped:

| Capability | Source | Status Hint |
|---|---|---|
| MCX commodities as first-class asset class | Repo PRD | Planned / draft |
| Continuous / back-adjusted commodity contracts | Repo PRD | Planned |
| Live Portfolio Dashboard | Repo PRD | Planned |
| Portfolio health score & tax insights | Public `/invest` page | Coming soon |
| Curated holdings-based news feed | Public `/invest` page | Coming soon |
| Iceberg orders | Public site + repo | Coming next |
| POV algo | Public site + repo | Coming next |

**Investor-specific coming-soon detail:**
- **Portfolio health score** across: diversification, concentration, cost efficiency, overlap, risk profile, tax efficiency, options exposure.
- **Tax insights:** days to LTCG, STCG vs LTCG impact before selling, ₹1L LTCG exemption tracking.
- **News feed:** macro and stock-specific news filtered to what the user actually holds, with sentiment tagging (likely positive / negative / neutral / affects your portfolio).

---

## 13. Public Limitations to Mention Carefully

These are user-facing constraints, not bugs. Use them to set expectations:

- Only one timeframe per prompt/backtest.
- Equity MIS/NRML is coerced to CNC in backtests.
- Futures lack rollover / continuous contract logic.
- No Supertrend, Heikin-Ashi, or Chandelier Exit.
- No partial exits or pyramiding.
- No covered calls (mixed equity + options legs).
- No dynamic position sizing based on volatility.
- Fundamental metrics are static snapshots, not point-in-time.

---

## 14. Content Pillars / Messaging Angles

Use these as the building blocks for blogs, LinkedIn posts, ads, and landing-page copy:

1. **“Ask before you trade.”** AI as a second opinion for F&O and equity decisions.
2. **Proof-first trading / investing.** Backtest → Paper → Live; no capital without evidence.
3. **Invest like you have a team.** Screen quality compounders, compare mutual funds, and track portfolio health without spreadsheets.
4. **Retail access to institutional order types.** MIT, LIT, MTL, TWAP, VWAP — inside a chat.
5. **Compliance by design.** SEBI IA + NSE Whitebox algo provider; not a retrofitted afterthought.
6. **Built for Indian markets.** NSE/BSE, F&O, MCX, mutual funds, multi-language support.
7. **No-code systematic investing.** Describe a rule or screen in any language; deploy without writing code.
8. **Capital stays at your broker.** Āagman routes orders through your existing broker; you hold the approval key.

---

## 15. Glossary

| Term | Meaning |
|---|---|
| **SIR** | Strategy Intermediate Representation — the structured, versioned contract that defines a strategy. |
| **IR** | Intermediate Representation (general). |
| **Relay** | User-run agent that forwards broker API calls from the user’s static IP. |
| **Deployment** | A running instance of a strategy in paper or live mode. |
| **Kill switch** | Manual or automatic halt of trading activity. |
| **Whitebox** | Algorithm logic is disclosed and auditable. |
| **MIT** | Market If Touched — buy/sell when price touches a trigger. |
| **LIT** | Limit If Touched. |
| **MTL** | Market-to-Limit. |
| **TWAP** | Time-Weighted Average Price execution algo. |
| **VWAP** | Volume-Weighted Average Price execution algo. |
| **POV** | Percent of Volume execution algo. |
| **EMS/OMS** | Execution Management System / Order Management System used by institutional desks. |

---

## 16. What Is Safe to Claim

Use this table as a final gut-check before publishing content. If a row says “Not safe to claim,” do not present it as shipped or currently available.

| Area | Public Site Status | Repo Status | Safe to Claim? | Content Guidance |
|---|---|---|---|---|
| Natural-language strategy creation | Live | Implemented | **Yes** | Safe to claim as available today. |
| Backtesting | Live | Implemented | **Yes** | Safe to claim as available today. |
| Screener | Live | Implemented | **Yes** | Safe to claim as available today. |
| Paper trading | Live | Planned / gating | **Partially** | Safe to describe as workflow intent, but verify live status before strong claims. |
| Live trading | Live | Described as planned in architecture docs | **Partially** | Public site claims live; repo architecture doc treats it as planned — align with product before claiming broadly. |
| Multi-broker execution | Live (major brokers) | Adapters exist for several brokers | **Partially** | Mention supported brokers generally; detailed setup only for Zerodha. |
| Kill switch / risk | Live | Architecture present | **Yes** | Safe to claim as available today. |
| TWAP / VWAP | Live | Live | **Yes** | Safe to claim as available today. |
| MCX commodities | Mentioned | Draft PRD | **No** | Not safe to claim as shipped; public site mentions it and repo is still draft. |
| Live Portfolio Dashboard | Not public | Draft PRD | **No** | Not safe to claim publicly; repo PRD only. |
| Portfolio health score & tax insights | Coming soon | Not public | **No** | Not safe to claim as shipped; public `/invest` page says coming soon. |
| Curated holdings-based news feed | Coming soon | Not public | **No** | Not safe to claim as shipped; public `/invest` page says coming soon. |
| Iceberg / POV | Coming next | Coming next | **No** | Not safe to claim as live; public site says coming next. |

---

*This document is a living source of truth. Update it whenever a major capability ships, a new asset class is added, or broker/order-type coverage changes.*
