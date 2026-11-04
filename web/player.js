'use strict';
const video = document.getElementById('video');
const status = document.getElementById('status');
const stage = document.getElementById('stage');
const buttons = Array.from(document.querySelectorAll('button'));
const requestedSource = new URLSearchParams(location.search).get('source');
const source = ['lan', 'compatible', 'hls'].includes(requestedSource) ? requestedSource : 'w3c';
if (source === 'lan' || source === 'compatible') {
  video.src = source === 'compatible' ? '/media/bbb-compatible.mp4' : '/media/bbb-trailer.mp4';
  document.querySelector('h1').textContent += ' · LAN delivery diagnostic';
  document.querySelector('.hint').textContent = 'Same licensed file, served by this Linux PC for diagnosis. This test requires the PC to stay on. No transcoding.';
} else if (source === 'w3c') {
  video.src = 'https://media.w3.org/2010/05/bunny/trailer.mp4';
}
function state() {
  const quality = video.getVideoPlaybackQuality ? video.getVideoPlaybackQuality() : {};
  return {source, time: video.currentTime, duration: Number.isFinite(video.duration) ? video.duration : null,
    readyState: video.readyState, networkState: video.networkState, paused: video.paused,
    muted: video.muted, volume: video.volume, width: video.videoWidth, height: video.videoHeight,
    frames: quality.totalVideoFrames, dropped: quality.droppedVideoFrames,
    audioDecodedBytes: video.webkitAudioDecodedByteCount,
    fullscreen: Boolean(document.fullscreenElement),
    fillScreen: stage.classList.contains('fill-screen'),
    captions: video.textTracks.length ? video.textTracks[0].mode : 'none',
    error: video.error ? {code: video.error.code, message: video.error.message} : null};
}
function event(kind, message) {
  fetch('/event', {method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({kind, message, video: state()})}).catch(() => {});
}
async function togglePlay() {
  if (video.paused) {
    if (video.ended) video.currentTime = 0;
    try { await video.play(); } catch (e) { status.textContent = e.message; event('play-rejected', e.message); }
  } else video.pause();
}
function seek(delta) {
  if (Number.isFinite(video.duration)) video.currentTime = Math.max(0, Math.min(video.duration - .1, video.currentTime + delta));
  event('seek-request', String(delta));
}
async function home() {
  video.pause();
  status.textContent = 'Returning Home…';
  try {
    const response = await fetch('/home', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'});
    if (!response.ok) throw new Error('Home request failed');
  } catch (_) { status.textContent = 'Press Home on the physical remote to exit.'; }
}
document.getElementById('play').onclick = togglePlay;
document.getElementById('back').onclick = () => seek(-10);
document.getElementById('forward').onclick = () => seek(10);
document.getElementById('home').onclick = home;
document.getElementById('fullscreen').onclick = () => {
  stage.classList.toggle('fill-screen');
  document.getElementById('fullscreen').textContent = stage.classList.contains('fill-screen') ? 'Exit full screen' : 'Fullscreen';
  status.textContent = stage.classList.contains('fill-screen') ? 'Full TV viewport · CSS layout' : 'Player in page';
  event('fill-screen-change', 'Uses the full webview viewport; native Fullscreen API did not complete on this TV.');
};
document.getElementById('subtitles').onclick = () => {
  const track = video.textTracks[0];
  if (!track) return;
  track.mode = track.mode === 'showing' ? 'disabled' : 'showing';
  status.textContent = 'Captions ' + track.mode;
  event('captions-toggle');
};
for (const name of ['loadedmetadata', 'canplay', 'playing', 'pause', 'seeking', 'seeked', 'ended', 'error', 'waiting', 'stalled']) {
  video.addEventListener(name, () => {
    status.textContent = name + ' · ' + video.currentTime.toFixed(1) + ' s' + (video.error ? ' · ' + video.error.message : '');
    event('video-' + name);
  });
}
document.addEventListener('fullscreenchange', () => event('fullscreen-change'));
document.getElementById('captions').addEventListener('load', () => event('captions-loaded'));
setInterval(() => { if (!video.paused) event('playback-progress'); }, 5000);
window.addEventListener('keydown', e => {
  fetch('/event', {method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({kind: 'player-key', key: e.key, code: e.keyCode})}).catch(() => {});
  const direction = {ArrowLeft: -1, ArrowUp: -1, ArrowRight: 1, ArrowDown: 1}[e.key];
  if (direction) {
    e.preventDefault();
    const index = buttons.indexOf(document.activeElement);
    buttons[(index + direction + buttons.length) % buttons.length].focus();
  } else if (['Escape', 'Backspace', 'BrowserBack', 'GoBack'].includes(e.key) || [461, 10009].includes(e.keyCode)) {
    e.preventDefault(); home();
  } else if (e.key === 'MediaPlayPause') { e.preventDefault(); togglePlay(); }
  else if (e.key === 'MediaFastForward') { e.preventDefault(); seek(10); }
  else if (e.key === 'MediaRewind') { e.preventDefault(); seek(-10); }
});
buttons[0].focus();
event('player-ready', JSON.stringify({ua: navigator.userAgent,
  h264: video.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"'),
  vp9: video.canPlayType('video/webm; codecs="vp9,opus"'),
  nativeHls: video.canPlayType('application/vnd.apple.mpegurl'),
  hlsJsVersion: typeof Hls !== 'undefined' ? Hls.version : null,
  mse: typeof Hls !== 'undefined' ? Hls.isSupported() : false}));
if (source === 'hls') {
  (async () => {
    status.textContent = 'Reading the Stremio test add-on…';
    const manifest = await (await fetch('/addon/manifest.json')).json();
    event('addon-manifest', manifest.id);
    const catalog = await (await fetch('/addon/catalog/movie/tv-lab.json')).json();
    const meta = catalog.metas[0];
    const response = await (await fetch('/addon/stream/movie/' + encodeURIComponent(meta.id) + '.json')).json();
    const stream = response.streams[0];
    document.querySelector('h1').textContent = meta.name + ' · Stremio-compatible HLS client';
    document.querySelector('.hint').textContent = 'CC BY 3.0 · Blender Foundation. HLS media comes directly from Mux’s public test host. The page and demo add-on still come from this PC. No local transcoding.';
    event('addon-stream-ready', 'Public HLS stream resolved via Stremio manifest/catalog/stream protocol');
    if (typeof Hls === 'undefined' || !Hls.isSupported()) throw new Error('HLS.js / MediaSource unsupported on this TV');
    const hls = new Hls({enableWorker: false, startLevel: 0, capLevelToPlayerSize: true});
    hls.on(Hls.Events.ERROR, (_event, data) => {
      event('hls-error', JSON.stringify({type: data.type, details: data.details, fatal: data.fatal}));
      if (data.fatal) status.textContent = 'HLS error: ' + data.details;
    });
    hls.on(Hls.Events.MANIFEST_PARSED, () => {status.textContent = 'Stream ready. Press Play / Pause with OK.'; event('hls-manifest-parsed');});
    hls.loadSource(stream.url);
    hls.attachMedia(video);
  })().catch(e => {status.textContent = e.message; event('hls-setup-error', e.message);});
}
