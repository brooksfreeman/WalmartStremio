'use strict';
// Local assets only. No analytics, storage, telemetry, or third-party requests.
const tiles = Array.from(document.querySelectorAll('#apps button'));
const tv = document.getElementById('tv');
const status = document.getElementById('status');
let busy = false;
let lastTile = tiles[0];
const dependencyTest = new URLSearchParams(location.search).get('dependencyTest') === '1';
if (dependencyTest) {
  const badge = document.getElementById('dependency-test');
  badge.hidden = false;
  let sawOffline = false;
  async function checkHelpers() {
    let online = false;
    try {
      const response = await fetch('/health', {cache:'no-store', signal:AbortSignal.timeout(1000)});
      online = response.ok;
    } catch (_) {}
    badge.classList.toggle('offline', !online);
    if (!online) {
      sawOffline = true;
      badge.textContent = 'PC helpers OFFLINE — test arrows, Netflix, then Home now';
    } else {
      badge.textContent = sawOffline ? 'PC helpers restored — test interval ended' : 'PC helpers online — wait for OFFLINE before testing';
    }
    setTimeout(checkHelpers, 1000);
  }
  checkHelpers();
}
function clock() {
  const now = new Date();
  document.getElementById('clock').textContent = now.toLocaleTimeString([], {hour: 'numeric', minute: '2-digit'});
}
clock();
setInterval(clock, 30000);
async function openApp(button) {
  if (busy) return;
  if (button === tv) {
    status.textContent = 'Press Input on your TV remote, then choose the HDMI port connected to this PC.';
    return;
  }
  if (button.dataset.app === 'stremio') {
    location.assign('/stremio/#/');
    return;
  }
  busy = true;
  status.textContent = button === tv ? 'Returning to TV…' : 'Opening ' + button.querySelector('span:last-child').textContent + '…';
  try {
    const response = await fetch('/launcher/launch', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({app:button.dataset.app}), signal:AbortSignal.timeout(4000)});
    if (!response.ok) throw new Error('Launch failed');
    status.textContent = 'Launch requested. If the app stays closed, press Home to return.';
  } catch (_) {
    status.textContent = 'Could not open the app. Home or Input returns to TV.';
  } finally {
    busy = false;
  }
}
[...tiles, tv].forEach(button => button.addEventListener('click', () => openApp(button)));
tiles.forEach(button => button.addEventListener('focus', () => {lastTile = button;}));
window.addEventListener('keydown', e => {
  const key = e.key || ({13:'Enter',37:'ArrowLeft',38:'ArrowUp',39:'ArrowRight',40:'ArrowDown'})[e.keyCode];
  const back = ['Escape','Backspace','BrowserBack','GoBack'].includes(key) || [461,10009].includes(e.keyCode);
  if (!back && !['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Enter'].includes(key)) return;
  e.preventDefault();
  e.stopImmediatePropagation();
  if (back) {tv.focus(); return;}
  if (key === 'Enter') {if (!e.repeat) document.activeElement?.click(); return;}
  const current = document.activeElement;
  if (current === tv) {if (key === 'ArrowUp') lastTile.focus(); return;}
  const index = tiles.indexOf(current);
  if (index < 0) {tiles[0].focus(); return;}
  const columns = getComputedStyle(document.getElementById('apps')).gridTemplateColumns.split(' ').length;
  if (key === 'ArrowDown') {
    if (index + columns < tiles.length) tiles[index + columns].focus();
    else tv.focus();
  } else if (key === 'ArrowUp') {
    if (index >= columns) tiles[index - columns].focus();
  } else {
    const next = index + (key === 'ArrowLeft' ? -1 : 1);
    if (next >= 0 && next < tiles.length) tiles[next].focus();
  }
}, true);
tiles[0].focus();
