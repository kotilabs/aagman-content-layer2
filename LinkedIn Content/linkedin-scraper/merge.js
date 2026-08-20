// Merge all per-profile JSONs in output/ into all-posts.json + all-posts.csv
const fs = require('fs');
const path = require('path');
const OUT = path.join(__dirname, 'output');

const files = fs.readdirSync(OUT).filter((f) => f.endsWith('.json') && !['summary.json', 'all-posts.json'].includes(f));
const all = [];
for (const f of files) {
  const d = JSON.parse(fs.readFileSync(path.join(OUT, f), 'utf8'));
  const handle = f.replace('.json', '');
  for (const p of d.posts) all.push({ profile: handle, ...p });
}

fs.writeFileSync(
  path.join(OUT, 'all-posts.json'),
  JSON.stringify({ scrapedAt: new Date().toISOString(), profiles: files.length, totalPosts: all.length, posts: all }, null, 2)
);

const esc = (s) => '"' + String(s ?? '').replace(/"/g, '""').replace(/\n/g, ' ') + '"';
const header = 'profile,date,type,reactions,comments,reposts,url,text';
const rows = all.map((p) => [esc(p.profile), esc(p.date), esc(p.type), p.reactions, p.comments, p.reposts, esc(p.url), esc(p.text)].join(','));
fs.writeFileSync(path.join(OUT, 'all-posts.csv'), [header, ...rows].join('\n'));

console.log('profiles:', files.length, '| total posts:', all.length);
