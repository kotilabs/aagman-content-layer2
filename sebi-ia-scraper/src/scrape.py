#!/usr/bin/env python3
"""SEBI Investment Adviser register scraper (test extraction phase).

Usage:
    python scrape.py 0-9 A

Mechanism (verified 2026-08-06):
    The register page loads records via POST /sebiweb/ajax/other/getintmfpiinfo.jsp
    (form-urlencoded). The endpoint sits behind a WAF that blocks non-browser
    clients, so all requests are issued as in-page fetch() calls inside a
    Playwright Chromium session (which carries the session cookies).
    Pagination: page 1 -> next=s, doDirect=-1, nextValue=1;
    page k>1   -> next=n, doDirect=k-1, nextValue=1.
    Each HTML fragment response carries a "X to Y of N records" counter and
    hidden fields (totalpage, nextValue); we verify the counter per page.

Raw HTML of every fetched page is cached under cache/ so re-runs don't refetch.
"""

import csv
import json
import os
import re
import sys
import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

PAGE_URL = ("https://www.sebi.gov.in/sebiweb/other/OtherAction.do"
            "?doRecognisedFpi=yes&intmId=13")
XHR_PATH = "/sebiweb/ajax/other/getintmfpiinfo.jsp"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

PAGE_SIZE = 25
FETCH_DELAY_S = 1.5

# CLI letter -> value of the `alp` request param (site uses id A1 for "0-9")
LETTER_TO_ALP = {"0-9": "A1"}

LABEL_MAP = {
    "name": "name",
    "registration no.": "registration_no",
    "e-mail": "email",
    "telephone": "telephone",
    "fax no.": "fax",
    "address": "address",
    "contact person": "contact_person",
    "correspondence address": "correspondence_address",
    "validity": "validity",
}
FIELDS = ["letter", "name", "registration_no", "email", "telephone", "fax",
          "address", "contact_person", "correspondence_address", "validity"]

LOG_LINES = []


def log(msg):
    line = "[{}] {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    LOG_LINES.append(line)


def cache_path(letter, page_no):
    safe = letter.replace("/", "_")
    return os.path.join(CACHE_DIR, "{}_p{}.html".format(safe, page_no))


def build_body(alp, page_no):
    """Replicates the site's own request body (see js/other.js searchFormFpi)."""
    if page_no == 1:
        next_, do_direct = "s", "-1"
    else:
        next_, do_direct = "n", str(page_no - 1)
    return ("nextValue=1&next={}&intmId=13&contPer=&name=&regNo=&email="
            "&location=&exchange=&affiliate=&alp={}&language=2&model="
            "&esgCategory=&doDirect={}&intmIds=").format(next_, alp, do_direct)


def fetch_page(page, alp, page_no, attempts=3):
    """In-page fetch of one result page; returns (html, status)."""
    body = build_body(alp, page_no)
    for attempt in range(1, attempts + 1):
        resp = page.evaluate(
            """async ([url, body]) => {
                const r = await fetch(url, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: body
                });
                return {status: r.status, text: await r.text()};
            }""", [XHR_PATH, body])
        text = resp["text"]
        if resp["status"] == 200 and ("card-table" in text
                                      or "No record(s) available" in text):
            return text, resp["status"]
        log("    fetch p{} attempt {} failed (status {}, len {})".format(
            page_no, attempt, resp["status"], len(text)))
        time.sleep(3 * attempt)
    raise RuntimeError("could not fetch page {} for alp={}".format(page_no, alp))


def parse_counter(html):
    m = re.search(r"(\d+)\s*to\s*(\d+)\s*of\s*(\d+)\s*records", html)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def parse_totalpage(html):
    m = re.search(r"name=['\"]totalpage['\"]\s*value=['\"]?(\d+)", html)
    return int(m.group(1)) if m else None


def get_page_html(pw_page, letter, page_no):
    """Return raw HTML for letter/page, from cache or by fetching."""
    path = cache_path(letter, page_no)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read(), "cache"
    alp = LETTER_TO_ALP.get(letter, letter)
    html, _ = fetch_page(pw_page, alp, page_no)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return html, "fetched"


def parse_records(html, letter):
    """Parse card blocks label-by-label (never by position)."""
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for card in soup.select("div.fixed-table-body.card-table"):
        rec = {f: "" for f in FIELDS}
        rec["letter"] = letter
        for view in card.select("div.card-view"):
            title_el = view.select_one(".title span")
            value_el = view.select_one(".value")
            if not title_el or not value_el:
                continue
            label = title_el.get_text(strip=True).lower()
            key = LABEL_MAP.get(label)
            if not key:
                continue
            value = value_el.get_text(" ", strip=True)
            rec[key] = value.lower() if key == "email" else value
        if rec["name"] or rec["registration_no"]:
            records.append(rec)
    return records


def scrape_letter(pw_page, letter):
    """Fetch (with cache) all pages for one letter. Returns (records, meta)."""
    meta = {"letter": letter, "reported_total": None, "totalpage": None,
            "pages_fetched": 0, "pages_cached": 0, "counter_errors": []}

    html1, src = get_page_html(pw_page, letter, 1)
    meta["pages_fetched" if src == "fetched" else "pages_cached"] += 1
    if "No record(s) available" in html1:
        log("  letter {}: no records (empty letter) [p1 from {}]".format(letter, src))
        meta["reported_total"] = 0
        return [], meta
    counter = parse_counter(html1)
    if not counter:
        raise RuntimeError("no record counter on page 1 of letter " + letter)
    _, _, total = counter
    meta["reported_total"] = total
    n_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    tp = parse_totalpage(html1)
    meta["totalpage"] = tp
    if tp and tp != n_pages:
        log("  WARNING: totalpage={} but counter implies {} pages".format(tp, n_pages))
    log("  letter {}: reported {} records across {} page(s) [p1 from {}]".format(
        letter, total, n_pages, src))

    pages_html = [html1]
    for p in range(2, n_pages + 1):
        time.sleep(FETCH_DELAY_S)
        html, src = get_page_html(pw_page, letter, p)
        meta["pages_fetched" if src == "fetched" else "pages_cached"] += 1
        c = parse_counter(html)
        exp_start = (p - 1) * PAGE_SIZE + 1
        if not c:
            meta["counter_errors"].append("p{}: no counter".format(p))
            log("  WARNING: p{} has no counter".format(p))
        elif c[0] != exp_start or c[2] != total:
            meta["counter_errors"].append(
                "p{}: counter {} (expected start {}, total {})".format(p, c, exp_start, total))
            log("  WARNING: p{} counter {} != expected start {}/total {}".format(
                p, c, exp_start, total))
        else:
            log("  p{} ok: {} to {} of {} [{}]".format(p, c[0], c[1], c[2], src))
        pages_html.append(html)

    records = []
    for html in pages_html:
        records.extend(parse_records(html, letter))
    return records, meta


def main():
    letters = sys.argv[1:]
    if not letters:
        sys.exit("usage: python scrape.py <letter> [<letter>...]  (e.g. 0-9 A)")
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    log("letters requested: {}".format(", ".join(letters)))
    log("mechanism: POST {} inside Playwright session; "
        "p1 next=s&doDirect=-1&nextValue=1; page k>1 next=n&doDirect=k-1&nextValue=1; "
        "alp param: 0-9 -> A1, letters map to themselves".format(XHR_PATH))

    all_records = []
    metas = []
    failed_letters = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=UA)
        page = ctx.new_page()
        page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("#ajax_cat .card-table", timeout=30000)
        log("page loaded, session established")
        for letter in letters:
            try:
                records, meta = scrape_letter(page, letter)
            except Exception as e:
                log("  letter {} FAILED hard ({}); retrying once after 10s".format(letter, e))
                time.sleep(10)
                try:
                    records, meta = scrape_letter(page, letter)
                except Exception as e2:
                    log("  letter {} FAILED on retry ({}); SKIPPING".format(letter, e2))
                    failed_letters.append(letter)
                    continue
            all_records.extend(records)
            metas.append(meta)
            time.sleep(FETCH_DELAY_S)
        browser.close()

    if failed_letters:
        log("FAILED letters (skipped): {}".format(", ".join(failed_letters)))

    # summary vs reported totals
    for meta in metas:
        n = sum(1 for r in all_records if r["letter"] == meta["letter"])
        status = "MATCH" if n == meta["reported_total"] else "MISMATCH"
        log("letter {}: scraped {} vs reported {} -> {}".format(
            meta["letter"], n, meta["reported_total"], status))
        for err in meta["counter_errors"]:
            log("  counter error: " + err)

    # data oddities: duplicate registration numbers
    seen = {}
    for r in all_records:
        if r["registration_no"]:
            seen.setdefault(r["registration_no"], []).append(r["name"])
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    if dups:
        log("duplicate registration numbers found: {}".format(json.dumps(dups)))
    else:
        log("no duplicate registration numbers in scraped set")
    missing_phone = sum(1 for r in all_records if not r["telephone"])
    missing_fax = sum(1 for r in all_records if not r["fax"])
    missing_email = sum(1 for r in all_records if not r["email"])
    log("records missing telephone={} fax={} email={} (of {})".format(
        missing_phone, missing_fax, missing_email, len(all_records)))

    suffix = "{}-{}".format(letters[0], letters[-1])
    csv_path = os.path.join(OUTPUT_DIR, "sebi_ia_register_{}.csv".format(suffix))
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(all_records)
    jsonl_path = os.path.join(OUTPUT_DIR, "raw_{}.jsonl".format(suffix))
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    log("wrote {} records to {} and {}".format(len(all_records), csv_path, jsonl_path))

    log_path = os.path.join(OUTPUT_DIR, "run_{}.log".format(suffix))
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(LOG_LINES) + "\n")
    print("run.log ->", log_path)


if __name__ == "__main__":
    main()
