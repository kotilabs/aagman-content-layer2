// Signal scout scraper: pulse.zerodha.com, zerohedge.com, armstrongeconomics.com
// Usage: node scrape.js  (run with cwd where playwright resolves)
// Output: JSON array to stdout — [{title, url, published, source}]. Errors → stderr.
const { chromium } = require('playwright');

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';

const SOURCES = [
  { name: 'pulse', url: 'https://pulse.zerodha.com/' },
  { name: 'zerohedge', url: 'https://www.zerohedge.com/' },
  { name: 'armstrong', url: 'https://www.armstrongeconomics.com/' },
];

// `node scrape.js <url> [name]` scrapes just that one source (used by add-source).
const CLI = process.argv[2]
  ? [{ name: process.argv[3] || 'custom', url: process.argv[2] }]
  : null;

// Runs inside the page. Extracts candidate news items generically.
function extract(sourceName) {
  const relToIso = (text) => {
    const m = text.match(/(\d+)\s*(minute|hour|day|week|month)s?\s*ago/i);
    if (!m) return null;
    const n = parseInt(m[1], 10);
    const unit = m[2].toLowerCase();
    const ms = { minute: 6e4, hour: 36e5, day: 864e5, week: 6048e5, month: 2592e6 }[unit];
    return new Date(Date.now() - n * ms).toISOString();
  };

  const absToIso = (text) => {
    // try native Date parse on things like "Oct 14, 2025" or "10/14/2025"
    const t = text.trim();
    if (t.length < 6 || t.length > 40) return null;
    const d = new Date(t);
    return isNaN(d.getTime()) ? null : d.toISOString();
  };

  const items = [];
  const seen = new Set();
  const anchors = Array.from(document.querySelectorAll('a[href]'));
  for (const a of anchors) {
    const title = (a.textContent || '').replace(/\s+/g, ' ').trim();
    if (title.length < 25 || title.length > 300) continue;
    const href = a.href;
    if (!/^https?:/.test(href) || seen.has(href)) continue;
    // skip obvious nav/chrome links
    if (/(login|signup|subscribe|about|contact|privacy|terms|#)/i.test(href) && title.length < 40) continue;

    // look for a date/relative-time near the anchor: itself, its container, siblings
    let published = null;
    let node = a;
    for (let depth = 0; depth < 4 && node && !published; depth++) {
      const scope = depth === 0 ? a : node;
      const t = scope.querySelector ? scope.querySelector('time[datetime]') : null;
      if (t) { published = absToIso(t.getAttribute('datetime')); }
      if (!published) {
        const txt = (scope.textContent || '').replace(/\s+/g, ' ');
        const rel = txt.match(/\d+\s*(?:minute|hour|day|week|month)s?\s*ago/i);
        if (rel) published = relToIso(rel[0]);
        if (!published) {
          const abs = txt.match(/(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}/i);
          if (abs) published = absToIso(abs[0]);
        }
      }
      node = node.parentElement;
    }
    seen.add(href);
    items.push({ title, url: href, published, source: sourceName });
  }
  return items;
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const out = [];
  for (const src of (CLI || SOURCES)) {
    try {
      const page = await browser.newPage({ userAgent: UA });
      await page.goto(src.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await page.waitForTimeout(3000); // let client-side content settle
      const items = await page.evaluate(extract, src.name);
      out.push(...items);
      console.error(`${src.name}: ${items.length} items`);
      await page.close();
    } catch (e) {
      console.error(`${src.name}: FAILED — ${e.message}`);
    }
  }
  await browser.close();
  process.stdout.write(JSON.stringify(out));
})().catch((e) => { console.error(e); process.exit(1); });
