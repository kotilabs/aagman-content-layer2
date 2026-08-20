// Phase 1+2: categorize all posts, extract writing features, join with normalized engagement.
const fs = require('fs');
const path = require('path');
const OUT = path.join(__dirname, 'output', 'all-posts.json');
const d = JSON.parse(fs.readFileSync(OUT, 'utf8'));

const eng = (p) => p.reactions + p.comments + p.reposts;
const median = (a) => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)] || 1; };

// normalized score (same as before: vs creator median)
const byCreator = {};
for (const p of d.posts) (byCreator[p.profile] ||= []).push(eng(p));
const base = {};
for (const [c, arr] of Object.entries(byCreator)) base[c] = Math.max(median(arr), 1);
for (const p of d.posts) p._score = Math.round(eng(p) / base[p.profile] * 100);

// ---- categorization ----
function categorize(p) {
  const t = p.text.toLowerCase();
  if (p.type === 'repost') return 'curation-repost';
  if (/\b(we('re| are) hiring|join (us|our team)|open role|job opening|founding engineer)\b/.test(t)) return 'announcement-hiring';
  if (/\b(launching|introducing|announcing|we (just )?(launched|shipped|built)|new feature|now live|we got into|yc w\d+|raised|funding)\b/.test(t)) return 'announcement-product';
  if (/\b(behind the scenes|bts|our office|team offsite|work culture|day in (my|the) life)\b/.test(t) || /office (in the making|tour|vibes)/.test(t)) return 'behind-the-scenes';
  if (/\b(unpopular opinion|hot take|contrarian|i (find it )?odd|controversial|change my mind|nobody talks about)\b/.test(t)) return 'opinion-contrarian';
  if (/\d+\s*(years?|yrs?)\s*(back|ago)|throwback|when (i|we) started|i (failed|lost|quit|dropped out)|my (first|journey|story)|i was \d+|i still remember|childhood/.test(t)) return 'personal-milestone';
  if (/\b(how (to|does|do)|explained|myth|what is|guide|framework|steps? to|here's (how|why)|breakdown|learn)\b/.test(t)) return 'educational';
  if (/\b(market|sensex|nifty|stocks?|ipo|valuation|inflation|gdp|rupee|dollar|interest rate|sebi|economy|investors?|portfolio|trading|f&o|mutual funds?|crypto|gold)\b/.test(t)) return 'market-commentary';
  if (/\?$/.test(p.text.trim()) || /^.{0,80}\?\s*$/m.test(p.text)) return 'conversation-starter';
  return 'other';
}

// ---- feature extraction ----
function features(p) {
  const text = p.text;
  const lines = text.split('\n').filter((l) => l.trim());
  const firstLine = (lines[0] || '').trim();
  const words = text.split(/\s+/).filter(Boolean);
  return {
    chars: text.length,
    words: words.length,
    lines: lines.length,
    firstLineChars: firstLine.length,
    firstLine: firstLine.slice(0, 120),
    hookType: (() => {
      if (/^\d+/.test(firstLine) || /₹|\$|\d+%/.test(firstLine)) return 'number-led';
      if (/\?\s*$/.test(firstLine)) return 'question';
      if (/^(i|we|my)\b/i.test(firstLine)) return 'first-person';
      if (/^(never|always|stop|don't|nobody|everyone|most people)/i.test(firstLine)) return 'bold-claim';
      if (/^["'“]/.test(firstLine)) return 'quote/dialogue';
      return 'statement';
    })(),
    emojis: (text.match(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2190}-\u{21FF}\u{2B00}-\u{2BFF}]/gu) || []).length,
    hashtags: (text.match(/#\w+/g) || []).length,
    hasLink: /https?:\/\//.test(text),
    endsWithQuestion: /\?\s*$/.test(text.trim()),
    unicodeBold: /[\u{1D400}-\u{1D7FF}]/u.test(text),
  };
}

for (const p of d.posts) {
  p._category = categorize(p);
  p._f = features(p);
}

// ---- aggregate stats per category ----
const cats = {};
for (const p of d.posts) (cats[p._category] ||= []).push(p);
const catStats = Object.entries(cats).map(([cat, arr]) => {
  const scores = arr.map((p) => p._score);
  return {
    category: cat,
    n: arr.length,
    avgScore: Math.round(scores.reduce((a, b) => a + b, 0) / arr.length),
    medianScore: median(scores),
    pctAboveBaseline: Math.round(arr.filter((p) => p._score > 100).length / arr.length * 100),
    avgWords: Math.round(arr.reduce((a, p) => a + p._f.words, 0) / arr.length),
    avgFirstLineChars: Math.round(arr.reduce((a, p) => a + p._f.firstLineChars, 0) / arr.length),
    topType: Object.entries(arr.reduce((m, p) => ((m[p.type] = (m[p.type] || 0) + 1), m), {})).sort((a, b) => b[1] - a[1])[0][0],
  };
}).sort((a, b) => b.medianScore - a.medianScore);

console.log('=== CATEGORY STATS (sorted by median score) ===');
console.table(catStats);

// hook type performance
const hooks = {};
for (const p of d.posts) (hooks[p._f.hookType] ||= []).push(p._score);
console.log('=== HOOK TYPE PERFORMANCE ===');
console.table(Object.entries(hooks).map(([h, s]) => ({
  hook: h, n: s.length,
  avgScore: Math.round(s.reduce((a, b) => a + b, 0) / s.length),
  medianScore: median(s),
})).sort((a, b) => b.medianScore - a.medianScore));

// dump categorized data + top/bottom per category for teardown
fs.writeFileSync(path.join(__dirname, 'analysis-posts.json'), JSON.stringify(d, null, 2));
const digest = {};
for (const [cat, arr] of Object.entries(cats)) {
  const sorted = [...arr].sort((a, b) => b._score - a._score);
  digest[cat] = {
    top: sorted.slice(0, 10).map((p) => ({ profile: p.profile, score: p._score, url: p.url, f: p._f, text: p.text })),
    bottom: sorted.slice(-5).map((p) => ({ profile: p.profile, score: p._score, url: p.url, f: p._f, text: p.text })),
  };
}
fs.writeFileSync(path.join(__dirname, 'analysis-digest.json'), JSON.stringify(digest, null, 2));
console.log('\nwrote analysis-posts.json + analysis-digest.json');
