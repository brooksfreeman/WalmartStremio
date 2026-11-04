// Owner TV adaptation for Stremio Web. No TV credentials are present here.
const React = require('react');

function TVRemoteBar({ state, menusOpen, active, onPlayPause, onSeek, onCaptions, onAudio, onBrowse, onCloseMenus }) {
    const [shown, setShown] = React.useState(true);
    const bar = React.useRef(null);
    const timer = React.useRef(null);
    const actions = React.useRef({});
    actions.current = { onPlayPause, onSeek, onCaptions, onAudio, onBrowse, onCloseMenus };
    const emit = React.useCallback((kind, message) => {
        const el = document.querySelector('video');
        const data = { kind, message, video: {
            source: 'stremio-tv', time: el?.currentTime ?? null,
            duration: Number.isFinite(el?.duration) ? el.duration : null,
            paused: el?.paused, readyState: el?.readyState,
            width: el?.videoWidth, height: el?.videoHeight,
            frames: el?.getVideoPlaybackQuality?.().totalVideoFrames,
            audioDecodedBytes: el?.webkitAudioDecodedByteCount,
            error: el?.error ? { code: el.error.code } : null,
        } };
        fetch('/event', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).catch(() => {});
    }, []);
    const reveal = React.useCallback(() => {
        setShown(true);
        clearTimeout(timer.current);
        if (state.paused === false) timer.current = setTimeout(() => setShown(false), 7000);
    }, [state.paused]);
    React.useEffect(() => {
        if (active && shown && !menusOpen) requestAnimationFrame(() => bar.current?.querySelector('button')?.focus());
    }, [active, shown, menusOpen]);
    React.useEffect(() => {
        reveal();
        const interval = setInterval(() => emit('stremio-player-state'), 5000);
        return () => { clearInterval(interval); clearTimeout(timer.current); };
    }, [emit, reveal]);
    React.useEffect(() => {
        if (!active) return;
        const keydown = (e) => {
            const back = ['Escape', 'Backspace', 'BrowserBack', 'GoBack'].includes(e.key) || [461, 10009].includes(e.keyCode);
            if (back && (menusOpen || shown)) {
                e.preventDefault();
                e.stopImmediatePropagation();
                if (menusOpen) {actions.current.onCloseMenus(); reveal();}
                else setShown(false);
                return;
            }
            if (menusOpen) return;
            if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) return;
            if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Enter', 'MediaPlayPause'].includes(e.key)) return;
            e.preventDefault();
            e.stopImmediatePropagation();
            if (e.repeat && ['Enter', 'MediaPlayPause'].includes(e.key)) return;
            emit('stremio-remote-key', e.key);
            if (e.key === 'MediaPlayPause' || (!shown && e.key === 'Enter')) {
                actions.current.onPlayPause();
                reveal();
                return;
            }
            const buttons = Array.from(bar.current?.querySelectorAll('button') || []);
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || !shown) {
                reveal();
                requestAnimationFrame(() => bar.current?.querySelector('button')?.focus());
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                reveal();
                const index = buttons.indexOf(document.activeElement);
                buttons[(index + (e.key === 'ArrowLeft' ? -1 : 1) + buttons.length) % buttons.length]?.focus();
            } else if (e.key === 'Enter') {
                reveal();
                if (buttons.includes(document.activeElement)) document.activeElement.click();
                else actions.current.onPlayPause();
            }
        };
        window.addEventListener('keydown', keydown, true);
        return () => window.removeEventListener('keydown', keydown, true);
    }, [active, menusOpen, shown, reveal, emit]);
    if (!active || menusOpen || !shown) return null;
    const style = { position: 'absolute', zIndex: 100, bottom: '2vh', left: '3vw', right: '3vw',
        padding: '1vw', background: 'rgba(12,10,24,.96)', borderRadius: '1vw', display: 'flex', gap: '1vw' };
    const buttonStyle = { fontSize: '1.5vw', padding: '1vw 1.4vw', color: 'white', border: '2px solid #a68bff',
        borderRadius: '.5vw', background: '#35265a' };
    const button = (text, handler) => <button key={text} style={buttonStyle} onFocus={e => {e.target.style.outline = '4px solid white';}}
        onBlur={e => {e.target.style.outline = '';}} onClick={handler}>{text}</button>;
    return <div ref={bar} style={style} aria-label="TV remote controls">
        {button(state.paused ? 'Play' : 'Pause', onPlayPause)}
        {button('−10 s', () => onSeek(Math.max(0, (state.time || 0) - 10000)))}
        {button('+10 s', () => onSeek(Math.min(state.duration || Infinity, (state.time || 0) + 10000)))}
        {button('Captions', () => {setShown(false); onCaptions();})}
        {button('Audio', () => {setShown(false); onAudio();})}
        {button('Browse', onBrowse)}
        {button('Home', () => {location.assign('/launcher.html');})}
    </div>;
}

module.exports = TVRemoteBar;
