"""One-off probe: understand the SEBI IA register page mechanism."""
import json
import time
from playwright.sync_api import sync_playwright

URL = "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

xhr_log = []

def on_response(resp):
    rt = resp.request.resource_type
    if rt in ("xhr", "fetch"):
        try:
            body = resp.text()
        except Exception:
            body = "<unreadable>"
        xhr_log.append({
            "url": resp.url,
            "method": resp.request.method,
            "post_data": resp.request.post_data,
            "status": resp.status,
            "body_preview": body[:2000],
        })

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(user_agent=UA)
    page = ctx.new_page()
    page.on("response", on_response)
    page.goto(URL, wait_until="networkidle", timeout=60000)
    time.sleep(2)

    print("=== TITLE:", page.title())
    # find the letter filter elements
    links = page.evaluate("""() => {
        const out = [];
        document.querySelectorAll('a, button, span, li').forEach(el => {
            const t = (el.innerText || '').trim();
            if (t === '0-9' || /^[A-Z]$/.test(t)) {
                out.push({tag: el.tagName, text: t, cls: el.className,
                          href: el.getAttribute('href'), onclick: el.getAttribute('onclick'),
                          id: el.id, outer: el.outerHTML.slice(0, 300)});
            }
        });
        return out;
    }""")
    print("=== LETTER FILTER ELEMENTS (first 8):")
    for l in links[:8]:
        print(json.dumps(l, indent=1))

    # click 0-9
    print("=== CLICKING 0-9 ...")
    xhr_log.clear()
    page.click("text='0-9'", timeout=10000)
    time.sleep(3)
    print("=== XHR/FETCH after click:")
    for x in xhr_log:
        print(json.dumps(x, indent=1)[:2500])

    # page text: counter
    counter = page.evaluate("""() => {
        const m = document.body.innerText.match(/\\d+\\s*to\\s*\\d+\\s*of\\s*\\d+\\s*records?/i);
        return m ? m[0] : null;
    }""")
    print("=== COUNTER:", counter)

    # dump html
    html = page.content()
    with open("/tmp/sebi_09.html", "w") as f:
        f.write(html)
    print("=== html saved to /tmp/sebi_09.html, len:", len(html))
    browser.close()
