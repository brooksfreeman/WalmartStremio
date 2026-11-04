'use strict';
const status = document.getElementById('status');
const buttons = Array.from(document.querySelectorAll('button'));
const event = data => fetch('/event', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)}).catch(() => {});
async function home() {
  status.textContent = 'Returning Home…';
  try {
    const response = await fetch('/home', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'});
    if (!response.ok) throw new Error('Home request failed');
  } catch (_) { status.textContent = 'Press Home on the physical remote to exit.'; }
}
buttons.forEach(button => button.addEventListener('click', () => {
  if (button.id === 'home') return home();
  document.documentElement.style.background = {blue: '#101c30', green: '#123326', orange: '#492c19'}[button.dataset.color];
  status.textContent = button.textContent + ' selected — OK button works';
  event({kind: 'select', button: button.textContent});
}));
window.addEventListener('keydown', e => {
  event({kind: 'key', key: e.key, code: e.keyCode, focused: document.activeElement.textContent.slice(0, 40)});
  const direction = {ArrowLeft: -1, ArrowUp: -1, ArrowRight: 1, ArrowDown: 1}[e.key];
  if (direction) {
    e.preventDefault();
    const index = buttons.indexOf(document.activeElement);
    buttons[(index + direction + buttons.length) % buttons.length].focus();
  } else if (['Escape', 'Backspace', 'BrowserBack', 'GoBack'].includes(e.key) || [461, 10009].includes(e.keyCode)) {
    e.preventDefault(); home();
  }
});
buttons[0].focus();
event({kind: 'ready', ua: navigator.userAgent, width: innerWidth, height: innerHeight});
