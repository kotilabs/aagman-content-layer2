// LinkedIn profile post scraper.
// Usage: node scraper.js profiles.txt [--max 50] [--headed]
// profiles.txt: one profile URL or handle per line.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const profilesFile = args[0];
const maxPosts = (() => { const i = args.indexOf('--max'); return i >= 0 ? parseInt(args[i + 1], 10) : 50; })();
const headed = args.includes('--headed');
const OUT_DIR = path.join(__dirname, 'output');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const rand = (min, max) => Math.floor(min + Math.random() * (max - min));

function parseCount(text) {
  if (!text) return 0;
  const t = text.replace(/,/g, '').trim().toLowerCase();
  const m = t.match(/([\d.]+)\s*([km]?)/);
  if (!m) return 0;
  let n = parseFloat(m[1]);
  if (m[2] === 'k') n *= 1000;
  if (m[2] === 'm') n *= 1000000;
  return Math.round(n);
}

function normalizeProfileUrl(raw) {
  let s = raw.trim();
  if (!s) return null;
  s = s.split('?')[0]; // drop tracking params like ?skipRedirect=true
  if (!s.startsWith('http')) s = `https://www.linkedin.com/in/${s.replace(/^\/+|\/+$/g, '')}/`;
  if (!s.endsWith('/')) s += '/';
  return s;
}

async function scrapeProfile(page, profileUrl) {
  const activityUrl = profileUrl + 'recent-activity/all/';
  console.log(`\n== ${profileUrl}`);
  await page.goto(activityUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(rand(3000, 5000));

  if (page.url().includes('/login') || page.url().includes('/checkpoint')) {
    throw new Error('Session expired or checkpoint hit — re-run login.js');
  }

  const posts = new Map(); // key: post urn/url
  let staleRounds = 0;

  while (posts.size < maxPosts && staleRounds < 5) {
    // expand all "see more" buttons currently on page
    await page.evaluate(() => {
      document.querySelectorAll('button.feed-shared-inline-show-more-text__see-more-less-toggle-btn, button.see-more, [class*="see-more"]').forEach((b) => {
        try { b.click(); } catch (e) {}
      });
    });
    await sleep(800);

    const batch = await page.evaluate(() => {
      const out = [];
      const articles = document.querySelectorAll('div.feed-shared-update-v2, article, div[data-urn]');
      articles.forEach((el) => {
        try {
          const urn = el.getAttribute('data-urn') || '';
          const textEl = el.querySelector('.feed-shared-inline-show-more-text, .update-components-text, [class*="commentary"]');
          const text = textEl ? textEl.innerText.trim() : '';
          // timestamp: the sub-description row holds "2w • Edited" style text; find the span that looks like a relative time
          let timeText = '';
          el.querySelectorAll('.update-components-actor__sub-description span, [class*="sub-description"] span').forEach((sp) => {
            if (timeText) return;
            const t = (sp.innerText || '').trim();
            if (/^\d+\s*(s|m|h|d|w|mo|yr)\b/i.test(t)) timeText = t.split('•')[0].trim();
          });
          const linkEl = el.querySelector('a[href*="/feed/update/"], a[href*="/posts/"]');
          const url = linkEl ? linkEl.href.split('?')[0] : '';
          // social counts
          let reactions = 0, comments = 0, reposts = 0;
          const num = (s) => ((s || '').replace(/,/g, '').match(/\d+/) || [''])[0];
          const reactEl = el.querySelector('li.social-details-social-counts__reactions button, button[data-reaction-details], [class*="social-counts__reactions"] button, .social-details-social-counts__reactions-count');
          if (reactEl) reactions = num(reactEl.getAttribute('aria-label') || reactEl.innerText);
          const cmEl = el.querySelector('li.social-details-social-counts__comments button, button[aria-label*="comment" i], [class*="social-counts-comments"]');
          if (cmEl) comments = num(cmEl.getAttribute('aria-label') || cmEl.innerText);
          const rpEl = el.querySelector('button[aria-label*="repost" i], [class*="social-counts-reposts"]');
          if (rpEl) reposts = num(rpEl.getAttribute('aria-label') || rpEl.innerText);
          const hasVideo = !!el.querySelector('video, [class*="video"]');
          const hasImage = !!el.querySelector('.update-components-image img, [class*="feed-shared-image"] img');
          const isRepost = /reposted this/i.test(el.querySelector('.update-components-header')?.innerText || '');
          const key = urn || url || text.slice(0, 80);
          if (!key || (!text && !url)) return;
          out.push({ key, urn, url, text, timeText, reactions: String(reactions), comments: String(comments), reposts: String(reposts), hasVideo, hasImage, isRepost });
        } catch (e) {}
      });
      return out;
    });

    let added = 0;
    for (const p of batch) {
      if (!posts.has(p.key)) {
        let type = 'text';
        if (p.isRepost) type = 'repost';
        else if (p.hasVideo) type = 'video';
        else if (p.hasImage) type = 'image';
        posts.set(p.key, {
          text: p.text,
          url: p.url || p.urn,
          date: p.timeText,
          type,
          reactions: parseCount(p.reactions),
          comments: parseCount(p.comments),
          reposts: parseCount(p.reposts),
        });
        added++;
      } else if (p.text && p.text.length > (posts.get(p.key).text || '').length) {
        // a later scroll round has this post with "see more" expanded — upgrade the stored text
        posts.get(p.key).text = p.text;
      }
    }

    staleRounds = added === 0 ? staleRounds + 1 : 0;
    process.stdout.write(`\r  posts collected: ${posts.size}   `);

    // scroll to the very bottom to trigger LinkedIn's infinite loader
    await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }));
    await sleep(rand(3000, 6000));

    // click "Show more results" style pagination button if present
    const moreBtn = await page.$('button:has-text("Show more results"), button.scaffold-finite-scroll__load-button');
    if (moreBtn) { await moreBtn.click().catch(() => {}); await sleep(rand(2000, 4000)); }
  }

  console.log(`\n  done: ${posts.size} posts`);
  return [...posts.values()].slice(0, maxPosts);
}

function toCsv(posts) {
  const esc = (s) => `"${String(s ?? '').replace(/"/g, '""').replace(/\n/g, ' ')}"`;
  const header = 'date,type,reactions,comments,reposts,url,text';
  const rows = posts.map((p) => [esc(p.date), esc(p.type), p.reactions, p.comments, p.reposts, esc(p.url), esc(p.text)].join(','));
  return [header, ...rows].join('\n');
}

(async () => {
  if (!profilesFile) { console.error('Usage: node scraper.js profiles.txt [--max 50] [--headed] [--cdp]'); process.exit(1); }
  const profiles = fs.readFileSync(profilesFile, 'utf8').split('\n').map(normalizeProfileUrl).filter(Boolean);
  if (!profiles.length) { console.error('No profiles found in file'); process.exit(1); }
  let browser, context, page;
  if (args.includes('--cdp')) {
    // drive the real Arc browser (already logged in, genuine fingerprint)
    browser = await chromium.connectOverCDP('http://localhost:9222');
    context = browser.contexts()[0];
    page = await context.newPage();
  } else {
    if (!fs.existsSync('auth.json')) { console.error('No auth.json — run: node login.js first'); process.exit(1); }
    browser = await chromium.launch({ headless: !headed });
    context = await browser.newContext({
      storageState: 'auth.json',
      viewport: { width: 1280, height: 900 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    });
    page = await context.newPage();
  }

  const summary = [];
  for (const profile of profiles) {
    const handle = profile.split('/in/')[1]?.replace(/\/+$/, '') || 'unknown';
    try {
      const posts = await scrapeProfile(page, profile);
      fs.writeFileSync(path.join(OUT_DIR, `${handle}.json`), JSON.stringify({ profile, scrapedAt: new Date().toISOString(), count: posts.length, posts }, null, 2));
      fs.writeFileSync(path.join(OUT_DIR, `${handle}.csv`), toCsv(posts));
      const eng = posts.length ? Math.round(posts.reduce((s, p) => s + p.reactions + p.comments, 0) / posts.length) : 0;
      summary.push({ profile, posts: posts.length, avgEngagement: eng });
      console.log(`  saved output/${handle}.json + .csv`);
    } catch (e) {
      console.error(`  FAILED ${profile}: ${e.message}`);
      summary.push({ profile, posts: 0, error: e.message });
      if (e.message.includes('login.js')) break;
    }
    await sleep(rand(10000, 20000));
  }

  fs.writeFileSync(path.join(OUT_DIR, 'summary.json'), JSON.stringify(summary, null, 2));
  console.log('\nAll done. Summary in output/summary.json');
  await browser.close();
})();
