"""Probe 2: XHR from within browser session + pagination markup."""
import json, time
from playwright.sync_api import sync_playwright

URL = "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

xhr_log = []

def on_request(req):
    if req.resource_type in ("xhr", "fetch"):
        xhr_log.append({"url": req.url, "method": req.method, "post": req.post_data})

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(user_agent=UA)
    page = ctx.new_page()
    page.on("request", on_request)
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#ajax_cat .card-table", timeout=30000)
    time.sleep(1)

    print("=== XHR on initial load:", json.dumps(xhr_log, indent=1))

    # click letter A
    xhr_log.clear()
    page.click("a#A")
    page.wait_for_function("document.body.innerText.match(/of \\d+ records/)", timeout=30000)
    time.sleep(1.5)
    print("=== XHR after clicking A:", json.dumps(xhr_log, indent=1))
    print("=== counter:", page.evaluate(
        "document.body.innerText.match(/\\d+ to \\d+ of \\d+ records/)[0]"))

    # pagination markup
    pag = page.evaluate("""() => {
        const el = document.querySelector('#ajax_cat .pagination');
        return el ? el.outerHTML.slice(0, 1500) : null;
    }""")
    print("=== pagination:", pag)

    # hidden fields in ajax_cat
    hidden = page.evaluate("""() => {
        const out = {};
        document.querySelectorAll('#ajax_cat input[type=hidden]').forEach(i => out[i.name] = i.value);
        return out;
    }""")
    print("=== hidden fields:", hidden)

    # in-page fetch: letter A, page 2
    body = ("nextValue=2&next=n&intmId=13&contPer=&name=&regNo=&email=&location="
            "&exchange=&affiliate=&alp=A&doDirect=-1&intmIds=")
    resp = page.evaluate("""async (body) => {
        const r = await fetch('/sebiweb/ajax/other/getintmfpiinfo.jsp', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: body
        });
        const t = await r.text();
        return {status: r.status, len: t.length,
                counter: (t.match(/\\d+ to \\d+ of \\d+ records/) || [null])[0],
                head: t.slice(0, 300)};
    }""", body)
    print("=== in-page fetch page2 A:", json.dumps(resp, indent=1)[:800])
    browser.close()
