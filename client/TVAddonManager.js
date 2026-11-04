const React = require('react');
const { useCore } = require('stremio/core');
const { useProfile } = require('stremio/common');
const { useLocation } = require('react-router');

function TVAddonSession({ requestNonce }) {
    const core = useCore();
    const profile = useProfile();
    const nonce = React.useRef(requestNonce);
    const started = React.useRef(false);
    const request = React.useRef(null);
    const reported = React.useRef(false);
    const [ready, setReady] = React.useState(false);
    const [message, setMessage] = React.useState('Updating add-ons from your PC…');
    const post = (path, data) => fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
    React.useEffect(() => {
        if (!nonce.current || started.current) return;
        started.current = true;
        (async () => {
            const response = await post('/addon-manager/request', {nonce:nonce.current});
            if (!response.ok) throw new Error();
            request.current = await response.json();
            // Save the exact current descriptors privately before any change.
            const backup = await post('/addon-manager/backup', {nonce:nonce.current, addons:profile.addons});
            if (!backup.ok) throw new Error();
            if (request.current.operation !== 'list') {
                await core.transport.dispatch({action:'Ctx', args:{
                    action:request.current.operation === 'install' ? 'InstallAddon' : 'UninstallAddon',
                    args:request.current.addon,
                }});
            }
            setReady(true);
        })().catch(() => setMessage('The add-on operation could not finish. Check the PC controls.'));
    }, [core, profile.addons]);
    React.useEffect(() => {
        if (!ready || reported.current || !request.current) return;
        const found = profile.addons.some(a => a.transportUrl === request.current.addon?.transportUrl);
        if (request.current.operation === 'install' && !found) return;
        if (request.current.operation === 'remove' && found) return;
        reported.current = true;
        post('/addon-manager/report', {nonce:nonce.current, addons:profile.addons, error:null})
            .then(r => {if (!r.ok) throw new Error(); setMessage('Add-ons updated. You can return to browsing.'); setTimeout(() => setMessage(''), 4000);})
            .catch(() => setMessage('Could not confirm the result to your PC.'));
    }, [ready, profile.addons]);
    if (!nonce.current || !message) return null;
    return <div role="status" style={{position:'fixed',zIndex:100000,top:'1vh',left:'8vw',right:'8vw',padding:'1.2vw',background:'#211637',color:'white',border:'2px solid #a68bff'}}>{message}</div>;
}

function TVAddonManager() {
    const route = useLocation();
    const nonce = new URLSearchParams(route.search).get('manageLocalAddons');
    return nonce ? <TVAddonSession key={nonce} requestNonce={nonce} /> : null;
}

module.exports = TVAddonManager;
