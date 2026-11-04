const React = require('react');
const { createPortal } = require('react-dom');

function TVSearchKeyboard({ value, onChange, onSubmit, onClose }) {
    const ref = React.useRef(null);
    React.useEffect(() => {
        ref.current?.querySelector('button')?.focus();
        const back = e => {
            if (['Escape', 'Backspace', 'BrowserBack', 'GoBack'].includes(e.key) || [461, 10009].includes(e.keyCode)) {
                e.preventDefault(); e.stopImmediatePropagation(); onClose();
            }
        };
        window.addEventListener('keydown', back, true);
        return () => window.removeEventListener('keydown', back, true);
    }, [onClose]);
    const keys = ['qwertyuiop', "asdfghjkl'", 'zxcvbnm-./', '1234567890'].join('').split('');
    const button = (label, action, span = 1) => <button key={label} type="button"
        onClick={action} onFocus={e => e.currentTarget.setAttribute('data-tv-focus', 'true')}
        style={{gridColumn:`span ${span}`,padding:'.8vw',fontSize:'1.8vw',color:'white',background:'#39295e',border:'2px solid #a68bff',borderRadius:'.4vw'}}>{label}</button>;
    return createPortal(<div ref={ref} role="dialog" aria-modal="true" aria-label="TV search keyboard"
        style={{position:'fixed',zIndex:100001,left:'9vw',right:'9vw',bottom:'3vh',padding:'1.5vw',background:'#171122',color:'white',border:'2px solid #a68bff',borderRadius:'1vw'}}>
        <div style={{fontSize:'1.6vw',marginBottom:'1vw',minHeight:'2.2vw'}}>{value || 'Type a title with arrows and OK'}</div>
        <div style={{display:'grid',gridTemplateColumns:'repeat(10,1fr)',gap:'.6vw'}}>
            {keys.map(key => button(key.toUpperCase(), () => onChange((value + key).slice(0, 200))))}
            {button('Space', () => onChange(value + ' '), 3)}
            {button('⌫', () => onChange(value.slice(0, -1)), 2)}
            {button('Clear', () => onChange(''))}
            {button('Search', onSubmit, 2)}
            {button('Close', onClose, 2)}
        </div>
        <div style={{fontSize:'1.1vw',marginTop:'1vw'}}>Arrows move · OK types · Back closes the keyboard</div>
    </div>, document.body);
}

module.exports = TVSearchKeyboard;
