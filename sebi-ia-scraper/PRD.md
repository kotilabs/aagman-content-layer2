# PRD — SEBI Investment Adviser Register Scraper (Test Extraction Phase)

## Background
SEBI publishes the register of Investment Advisers (intmId=13) as a JS-driven page.
Plain HTTP GET returns only the search-form shell; records load via an XHR POST
behind a WAF that blocks non-browser requests. We need a reliable, polite,
resumable extraction pipeline, proven first on two letter filters.

## Goal (this phase)
Prove extraction works: pull all records for letter filters "0-9" (6 records)
and "A" (145 records, ~6 pages of 25), save CSV + raw JSONL, and document the
page mechanism (endpoint, params, pagination semantics).

## Source contract
- Page: https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13
- Letter filter calls `searchFormFpiAlp(letter)` → POST
  `/sebiweb/ajax/other/getintmfpiinfo.jsp` (form-urlencoded):
  `nextValue`, `next` (s=first, n=numbered), `intmId=13`, `alp=<letter>`,
  `doDirect` (page-1 for numbered pages, -1 for first), plus empty search fields
  (`name`, `regNo`, `contPer`, `email`, `location`, `exchange`, `affiliate`,
  `language=2`, `model`, `esgCategory`, `intmIds`).
- WAF (F5-shaped "Unauthorized Request Blocked") rejects bare curl; requests must
  run inside a browser session (Playwright, in-page fetch).
- Response = HTML fragment injected into `#ajax_cat`: hidden fields
  (`totalpage`, `nextValue`), counter "X to 25 of N records", pagination links,
  then one `div.fixed-table-body.card-table` per record.
- Record = label:value pairs in `div.card-view` (label `.title>span`, value
  `.value>span`). 9 possible labels: Name, Registration No., E-mail, Telephone,
  Fax No., Address, Contact Person, Correspondence Address, Validity.
  Some cards omit Telephone/Fax/E-mail — parse by label, never by position.

## Functional requirements
- FR1: CLI `python scrape.py <letter> [<letter>...]` (e.g. `0-9 A`).
- FR2: Walk pagination per letter by deriving page count from the on-page
  counter / totalpage hidden field; verify each fetched page's counter.
- FR3: Cache every fetched page's raw HTML under `cache/`; re-runs reuse cache.
- FR4: Extract per record: letter, name, registration_no, email (lowercased),
  telephone, fax, address, contact_person, correspondence_address, validity.
- FR5: Write `output/sebi_ia_register_TEST.csv`, `output/raw_TEST.jsonl`,
  `output/run.log` (per-letter scraped vs page-reported counts, mechanism notes).
- FR6: Politeness: headless Chromium, real-ish UA, 1–2s delays between fetches.

## Validation gate
- 0-9: exactly 6 records; ≥1 record lacking Telephone/Fax parses with no column shift.
- A: exactly 145 records; first record "A58 KNOWLEDGE SERVICES PRIVATE LIMITED"
  has email legal@a58.in; spot-check records missing phone/fax.
- Any mismatch vs page-reported totals must be logged in run.log and reported.

## Out of scope (this phase)
Letters other than 0-9 and A; full-register run; scheduling/automation.
