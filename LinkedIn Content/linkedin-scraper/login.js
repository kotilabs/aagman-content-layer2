// One-time LinkedIn login: opens a browser, you log in manually, saves session to auth.json
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();
  await page.goto('https://www.linkedin.com/login');

  console.log('Log in to LinkedIn in the browser window.');
  console.log('Waiting until you reach the feed (up to 5 minutes)...');

  try {
    await page.waitForURL('**/feed/**', { timeout: 300000 }).catch(async () => {
      // some logins land on /in/<handle>/ or checkpoint; accept any non-login page
      await page.waitForFunction(
        () => !location.pathname.startsWith('/login') && !location.pathname.startsWith('/checkpoint'),
        { timeout: 300000 }
      );
    });
    await context.storageState({ path: 'auth.json' });
    console.log('Session saved to auth.json — run: node scraper.js profiles.txt');
  } catch (e) {
    console.log('Browser closed before login completed — no session saved. Re-run login.js.');
  }
  await browser.close().catch(() => {});
})();
