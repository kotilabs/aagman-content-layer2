// Raw-CDP post screenshotter: navigates a tab to a LinkedIn post URL and screenshots it.
// Usage: node cdp-shot.js <url> <outfile.png>
const WS = require('ws');

async function cdp(wsUrl, method, params = {}, id = 1) {
  return new Promise((resolve, reject) => {
    const ws = new WS(wsUrl, { perMessageDeflate: false });
    const timer = setTimeout(() => { ws.terminate(); reject(new Error('timeout ' + method)); }, 30000);
    ws.on('open', () => ws.send(JSON.stringify({ id, method, params })));
    ws.on('message', (data) => {
      const msg = JSON.parse(data);
      if (msg.id === id) {
        clearTimeout(timer);
        ws.close();
        msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
      }
    });
    ws.on('error', (e) => { clearTimeout(timer); reject(e); });
  });
}

(async () => {
  const [url, outfile] = process.argv.slice(2);
  // create a fresh tab
  const newTab = await (await fetch('http://localhost:9222/json/new?' + encodeURIComponent(url), { method: 'PUT' })).json();
  const wsUrl = newTab.webSocketDebuggerUrl;
  await new Promise(r => setTimeout(r, 9000)); // let it render
  // screenshot the viewport
  const shot = await cdp(wsUrl, 'Page.captureScreenshot', { format: 'png' });
  require('fs').writeFileSync(outfile, Buffer.from(shot.data, 'base64'));
  // close the tab
  await fetch('http://localhost:9222/json/close/' + newTab.id);
  console.log('saved', outfile);
})().catch(e => { console.error('Failed:', e.message); process.exit(1); });
