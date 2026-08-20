// Full per-post capture: post screenshot + View analytics panel (text + screenshot).
// Usage: node cdp-full.js <url> <basename>
const WS = require('ws');
const fs = require('fs');

function connect(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WS(wsUrl, { perMessageDeflate: false });
    ws.on('open', () => resolve(ws));
    ws.on('error', reject);
  });
}
let msgId = 0;
function cmd(ws, method, params = {}) {
  const id = ++msgId;
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('timeout ' + method)), 30000);
    const onMsg = (data) => {
      const msg = JSON.parse(data);
      if (msg.id === id) {
        clearTimeout(timer);
        ws.off('message', onMsg);
        msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
      }
    };
    ws.on('message', onMsg);
    ws.send(JSON.stringify({ id, method, params }));
  });
}
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const evalJs = async (ws, expression) =>
  (await cmd(ws, 'Runtime.evaluate', { expression, returnByValue: true })).result.value;

(async () => {
  const [url, base] = process.argv.slice(2);
  const tab = await (await fetch('http://localhost:9222/json/new?' + encodeURIComponent(url), { method: 'PUT' })).json();
  const ws = await connect(tab.webSocketDebuggerUrl);
  await sleep(9000);

  // post card text (for record)
  const cardText = await evalJs(ws, `(document.querySelector('div.feed-shared-update-v2, main')||document.body).innerText.slice(0,1500)`);
  fs.writeFileSync(`${base}-post.txt`, cardText || '');

  // click View analytics
  const clicked = await evalJs(ws, `(() => {
    const els = [...document.querySelectorAll('a, button, span')];
    const el = els.find(e => (e.innerText || '').trim().toLowerCase() === 'view analytics');
    if (!el) return 'NOT_FOUND';
    el.click(); return 'CLICKED';
  })()`);
  console.log('view analytics:', clicked);

  if (clicked === 'CLICKED') {
    await sleep(5000);
    // scroll the analytics page to load all sections
    await evalJs(ws, `window.scrollTo(0, document.body.scrollHeight)`);
    await sleep(3000);
    const panelText = await evalJs(ws, `document.body.innerText`);
    fs.writeFileSync(`${base}-analytics.txt`, panelText || '');
    const shot = await cmd(ws, 'Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${base}-analytics.png`, Buffer.from(shot.data, 'base64'));
    console.log('analytics captured');
  }
  await fetch('http://localhost:9222/json/close/' + tab.id);
  process.exit(0);
})().catch(e => { console.error('Failed:', e.message); process.exit(1); });
