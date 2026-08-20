// One-shot probe: dump candidate selectors from the live activity page. Run once, gently.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    storageState: 'auth.json',
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();
  await page.goto('https://www.linkedin.com/in/nikhilkamathcio/recent-activity/all/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(6000);
  // one gentle scroll so first batch fully renders
  await page.mouse.wheel(0, 1500);
  await page.waitForTimeout(4000);

  const info = await page.evaluate(() => {
    const first = document.querySelector('div.feed-shared-update-v2, article, div[data-urn]');
    const dump = {};
    dump.containerCount = document.querySelectorAll('div.feed-shared-update-v2, article, div[data-urn]').length;
    dump.bodyHeight = document.body.scrollHeight;
    if (first) {
      dump.containerTag = first.tagName + ' data-urn=' + (first.getAttribute('data-urn') || 'none');
      const sels = [
        '.update-components-actor__sub-description',
        'p.update-components-actor__sub-description span[aria-hidden="true"]',
        '.social-details-social-counts__reactions-count',
        'button[aria-label*="reaction" i]',
        'li.social-details-social-counts__reactions',
        'li.social-details-social-counts__comments button',
        'li.social-details-social-counts__item--with-social-proof',
        'button.social-details-social-counts__count-value',
        '.social-details-social-counts__item',
      ];
      dump.samples = {};
      for (const s of sels) {
        const el = first.querySelector(s);
        dump.samples[s] = el ? (el.getAttribute('aria-label') || el.innerText || '').trim().slice(0, 100) : null;
      }
      // social counts section raw text
      const social = first.querySelector('.social-details-social-counts');
      dump.socialText = social ? social.innerText.replace(/\n/g, ' | ').slice(0, 200) : null;
    }
    return dump;
  });
  console.log(JSON.stringify(info, null, 2));
  await browser.close();
})().catch((e) => { console.error('Failed:', e.message); process.exit(1); });
