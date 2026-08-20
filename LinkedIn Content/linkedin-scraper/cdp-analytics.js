// Navigate to a LinkedIn post, click "View analytics", screenshot the panel.
// Usage: node cdp-analytics.js <post-url> <outfile.png>
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

(async () => {
  const [url, outfile] = process.argv.slice(2);
  const tab = await (await fetch('http://localhost:9222/json/new?' + encodeURIComponent(url), { method: 'PUT' })).json();
  const ws = await connect(tab.webSocketDebuggerUrl);
  await sleep(9000);

  // find and click "View analytics"
  const click = await cmd(ws, 'Runtime.evaluate', {
    expression: `(() => {
      const els = [...document.querySelectorAll('a, button, span')];
      const el = els.find(e => (e.innerText || '').trim().toLowerCase() === 'view analytics');
      if (!el) return 'NOT_FOUND';
      el.click();
      return 'CLICKED';
    })()`,
    returnByValue: true,
  });
  console.log('click:', click.result.value);
  await sleep(5000);

  const shot = await cmd(ws, 'Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(outfile, Buffer.from(shot.data, 'base64'));
  console.log('saved', outfile);
  await fetch('http://localhost:9222/json/close/' + tab.id);
  process.exit(0);
})().catch(e => { console.error('Failed:', e.message); process.exit(1); });
