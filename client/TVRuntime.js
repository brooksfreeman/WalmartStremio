// Local diagnostics for the owner TV build. Never record route parameters,
// addon URLs, stream URLs, account data, or browser storage.
function safeMessage(value) {
    return String(value || '').replace(/https?:\/\/\S+/g, '[URL omitted]').slice(0, 700);
}

function report(kind, message) {
    fetch('/event', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kind, message: safeMessage(message) }),
        keepalive: true,
    }).catch(() => {});
}

window.addEventListener('error', e => {
    let file = '';
    try { file = new URL(e.filename).pathname.split('/').pop(); } catch (_) {}
    report('stremio-js-error', `${e.message}; file=${file}; line=${e.lineno}; column=${e.colno}`);
});
window.addEventListener('unhandledrejection', e => report('stremio-rejection', e.reason?.message || e.reason));
function routeReport() {
    const route = location.hash.split('/')[1]?.split('?')[0];
    const name = ['player', 'discover', 'library', 'addons', 'settings', 'search', 'intro'].includes(route) ? route : 'board-or-other';
    report('stremio-route', name);
    setTimeout(() => report('stremio-route-ready', `${name}; app children=${document.getElementById('app')?.childElementCount || 0}; video=${!!document.querySelector('video')}`), 3000);
}
window.addEventListener('hashchange', routeReport);
routeReport();

// No floating Home link: React Router can navigate with pushState without a
// hashchange event, leaving a route-hidden link visible over video. The player
// control bar provides a Home action when shown; physical TV Home stays normal.
const isPlayerRoute = () => /^#\/player(?:[/?]|$)/.test(location.hash);

// The desktop app's custom div buttons do not acquire focus on this TV.
// Keep native player/menu handling; supply spatial focus for pages and dialogs.
const style = document.createElement('style');
style.textContent = '[data-tv-focus="true"]:focus{outline:4px solid #fff!important;outline-offset:3px!important;box-shadow:0 0 0 7px #7352be!important}';
document.head.appendChild(style);
const visible = el => {
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1 && getComputedStyle(el).visibility !== 'hidden' && !el.closest('[aria-hidden="true"]');
};
window.addEventListener('keydown', e => {
    const dialogs = Array.from(document.querySelectorAll('[role="dialog"], [class*="modal-dialog-container"]')).filter(visible);
    const scope = dialogs.at(-1) || document;
    if (!dialogs.length && isPlayerRoute()) return;
    const edit = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName);
    if (edit && !document.activeElement?.matches('[data-tv-search="true"]')) return;
    const back = ['Backspace', 'BrowserBack', 'GoBack'].includes(e.key) || [461, 10009].includes(e.keyCode);
    if (back && dialogs.length) {
        e.preventDefault(); e.stopImmediatePropagation();
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', bubbles: true }));
        return;
    }
    if (back && ['#/', '#', ''].includes(location.hash)) {
        e.preventDefault(); e.stopImmediatePropagation();
        location.assign('/launcher.html');
        return;
    }
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Enter'].includes(e.key)) return;
    const controls = Array.from(scope.querySelectorAll('button,a[href],input:not([type="file"]),textarea,select,[tabindex]:not([tabindex="-1"])'))
        .filter(el => visible(el) && !el.disabled && !el.classList.contains('disabled') && el.getAttribute('aria-disabled') !== 'true' && el.getAttribute('type') !== 'file');
    if (!controls.length) return;
    e.preventDefault(); e.stopImmediatePropagation();
    const active = document.activeElement;
    let target = controls[0];
    if (controls.includes(active)) {
        if (e.key === 'Enter') {
            if (!e.repeat) active.click();
            return;
        }
        const a = active.getBoundingClientRect();
        const x = a.left + a.width / 2, y = a.top + a.height / 2;
        const horizontal = ['ArrowLeft', 'ArrowRight'].includes(e.key);
        const sign = ['ArrowLeft', 'ArrowUp'].includes(e.key) ? -1 : 1;
        let best = Infinity;
        target = active;
        controls.forEach(el => {
            if (el === active) return;
            const b = el.getBoundingClientRect();
            const dx = b.left + b.width / 2 - x, dy = b.top + b.height / 2 - y;
            const primary = (horizontal ? dx : dy) * sign;
            const secondary = Math.abs(horizontal ? dy : dx);
            if (primary < 2) return;
            const score = primary + secondary * 3;
            if (score < best) { best = score; target = el; }
        });
    }
    target.setAttribute('data-tv-focus', 'true');
    target.focus();
    target.scrollIntoView({block: 'nearest', inline: 'nearest'});
}, true);

module.exports = { report };
