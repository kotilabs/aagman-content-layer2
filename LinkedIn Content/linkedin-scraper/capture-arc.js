// Capture LinkedIn session from the user's real Arc browser (already logged in).
// Requires Arc running with --remote-debugging-port=9222.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const context = browser.contexts()[0];
  const page = await context.newPage();
  await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);

  const url = page.url();
  if (url.includes('/login') || url.includes('/checkpoint')) {
    console.log('LinkedIn is NOT logged in in Arc (landed on', url, '). Log in there first.');
  } else {
    await context.storageState({ path: 'auth.json' });
    console.log('Captured session from Arc → auth.json. URL was:', url);
  }
  await page.close();
  await browser.close();
})().catch((e) => { console.error('Failed:', e.message); process.exit(1); });
