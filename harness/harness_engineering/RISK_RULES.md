# RISK_RULES.md — Engineering domain: invariants + laws

> Enforced by `ComplianceGate(rules_file="harness_engineering/RISK_RULES.md", ...)`
> on engineering artifacts (RCA, fix, PR), and injected verbatim into the RCA,
> JUDGE, and gate prompts. The SAME ComplianceGate class enforces this file for
> the engineering domain that enforces `SEBI_RULES.md` for content — only the
> rules file differs. Target repo: **aagman-v2**.

---

## 1. INDIAN MARKET INVARIANTS (product truths — never violate, never "fix away")

- **CNC equity short = BLOCK.** A CNC (delivery) short on cash equity is not a
  valid product state and must be blocked, never "made to work".
- **F&O naked short = ALLOW.** A naked short in F&O is legitimate; do not force a
  stop-loss or a hedge onto it as a precondition.
- **Stop-loss is OPTIONAL for F&O.** Never require an SL to place an F&O order.
- **Product type is auto-derived, never asked.** CNC vs MIS vs NRML is derived
  from instrument + intent; never prompt the user to choose it.
- **STT:** CNC = **0.1% on both sides**; MIS = **0.025% sell-side only**. Any
  cost/PnL math must use these.
- **`rr_ratio = take_profit / stop_loss`.** Reward-to-risk is take-profit over
  stop-loss — never inverted.

## 2. LAYER LAW (route the bug to the right language/file)

- Errors mentioning **`risk_blocked`** or **`rule 6.x`** are **TypeScript** logic,
  starting at **`risk-calculations.ts`**. Begin the investigation there.
- **Never write Python tests for a TypeScript bug** (or vice-versa). Fix the bug
  in the layer that owns it. Symptom language dictates the layer.

## 3. THE FOUR ENGINEERING LAWS (verbatim — enforce in RCA + JUDGE + gate)

**(a)** Infra or data errors — or absence of expected data — are **NEVER
skipped**. They are investigated to **root cause**.

**(b)** **NEVER defer a bug because it is "pre-existing".** Everything
encountered — pre-existing or newly identified — gets an RCA (root cause
analysis).

**(c)** Every conclusion must be **DATA-backed, CODE-backed, or
TEST-RESULT-backed**. No "probably" / "should be" conclusions.

**(d)** A bug fix is verified **ONLY** by code inspection **AND** an actual
executed test that **failed before** the fix and **passes after**.

## 4. BRANCH LAW

- **Never commit on `main`.** Always branch **`ajit/fix-{n}`** for each fix.
- **Amit merges all PRs.** The harness opens PRs; it does not self-merge.

## 5. REGRESSION LAW

- Every fix **adds a regression test** under **`regression-testing/{area}/`** and
  updates that area's README table (the row that names the bug and links the test).
- A fix without a regression test is incomplete and must not be marked done.

---

## ONE-LINE PRE-PR GATE

Root cause proven (data/code/test-backed, no "probably") · no pre-existing excuse ·
bug reproduced by a test that failed before and passes after · product invariants
intact (CNC short blocked, F&O short allowed, STT/`rr_ratio` correct) · bug fixed
in the owning layer · branch `ajit/fix-{n}` (never `main`) · regression test added
under `regression-testing/{area}/`.
