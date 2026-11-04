const React = require('react');
const { useCore } = require('stremio/core');
const { useProfile } = require('stremio/common');

function TVAddonImport() {
    const core = useCore();
    const profile = useProfile();
    const requested = React.useRef(new URLSearchParams(location.hash.split('?')[1] || '').get('importLocalAddons') === '1');
    const started = React.useRef(false);
    const expected = React.useRef(null);
    const acknowledged = React.useRef(false);
    const [finished, setFinished] = React.useState(false);
    const [status, setStatus] = React.useState('Importing your local Stremio add-ons…');
    React.useEffect(() => {
        if (!requested.current || started.current) return;
        started.current = true;
        const post = (path, body) => fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
        (async () => {
            const response = await post('/addon-import', {});
            if (!response.ok) throw new Error('No pending local import');
            const data = await response.json();
            if (!Array.isArray(data.addons)) throw new Error('Invalid local import');
            const backup = await post('/addon-backup', {addons: profile.addons});
            if (!backup.ok) throw new Error('Could not back up TV add-ons');
            expected.current = data.addons;
            for (const addon of data.addons) {
                await core.transport.dispatch({action: 'Ctx', args: {action: 'InstallAddon', args: addon}});
            }
            setFinished(true);
            setStatus('Checking imported add-ons…');
        })().catch(() => setStatus('Add-on import did not finish. Your original setup is backed up locally.'));
    }, [core, profile.addons]);
    React.useEffect(() => {
        if (!finished || !expected.current || acknowledged.current) return;
        const installed = expected.current.every(addon => profile.addons.some(item => item.transportUrl === addon.transportUrl));
        if (!installed) return;
        acknowledged.current = true;
        fetch('/addon-import-complete', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({count:expected.current.length})})
            .then(r => {
                if (!r.ok) throw new Error('Acknowledgement failed');
                setStatus(`Imported ${expected.current.length} add-ons, including Torrentio. Your Stremio account was not copied.`);
            }).catch(() => setStatus('Add-ons installed; local completion record needs checking.'));
    }, [finished, profile.addons]);
    if (!requested.current) return null;
    return <div role="status" style={{position:'fixed',zIndex:100000,top:'1vh',left:'8vw',right:'8vw',padding:'1.2vw',fontSize:'1.5vw',background:'#211637',color:'white',border:'2px solid #a68bff'}}>{status}</div>;
}

module.exports = TVAddonImport;
