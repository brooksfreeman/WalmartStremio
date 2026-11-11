"""Private, one-use desktop-to-TV Stremio add-on operations."""
import hashlib
import ipaddress
import json
import secrets
import time
import urllib.parse
import urllib.request

import tvctl

PENDING = 'addon-manager.pending.json'
STATE = 'addon-manager-state.json'
REPORT = 'addon-manager-result.json'


def identity():
    return tvctl.read_private('tv.json')['certificate_sha256']


def cached_addons():
    try:
        state = tvctl.read_private(STATE)
        return state['addons'] if state.get('tv_identity') == identity() else []
    except (OSError, ValueError, KeyError):
        return []


def summary():
    return [{'key': hashlib.sha256(a['transportUrl'].encode()).hexdigest(),
             'name': a.get('manifest', {}).get('name', 'Unnamed add-on'),
             'version': a.get('manifest', {}).get('version', ''),
             'protected': bool(a.get('flags', {}).get('protected', False))} for a in cached_addons()]


def manifest_url(value):
    value = value.strip()
    if value.startswith('stremio://'):
        value = 'https://' + value[len('stremio://'):]
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Paste an HTTP(S) manifest URL or a stremio:// install link.')
    if parsed.fragment:
        raise ValueError('Paste the add-on install link, not the Stremio website address.')
    return value


def fetch_addon(value):
    url = manifest_url(value)
    try:
        request = urllib.request.Request(url, headers={
            'Accept': 'application/json',
            'User-Agent': 'StremioTV-AddonManager/1.0',
        })
        class HTTPRedirects(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                manifest_url(newurl)
                return super().redirect_request(req, fp, code, msg, headers, newurl)
        opener = urllib.request.build_opener(HTTPRedirects())
        with opener.open(request, timeout=15) as response:
            if urllib.parse.urlsplit(response.url).scheme not in ('http', 'https'):
                raise ValueError()
            body = response.read(2 * 1024 * 1024 + 1)
        if len(body) > 2 * 1024 * 1024:
            raise ValueError()
        manifest = json.loads(body)
        if not isinstance(manifest, dict) or not all(isinstance(manifest.get(k), str) and manifest[k] for k in ('id', 'name', 'version')):
            raise ValueError()
        if not isinstance(manifest.get('resources'), list) or not isinstance(manifest.get('types'), list):
            raise ValueError()
    except (OSError, ValueError):
        # Provider URLs can contain personal keys. Never echo them in errors.
        raise RuntimeError('Could not read an add-on manifest. Paste its Install link or manifest.json URL.') from None
    return {'transportUrl': url, 'manifest': manifest, 'flags': {'official': False, 'protected': False}}


def pending_request(nonce):
    value = tvctl.read_private(PENDING)
    if value.get('nonce') != nonce or value.get('expires', 0) < time.time() or value.get('tv_identity') != identity():
        raise ValueError('Expired add-on request')
    return value


def receive_report(data):
    request = pending_request(data.get('nonce'))
    if set(data) != {'nonce', 'addons', 'error'} or not isinstance(data['addons'], list) or len(data['addons']) > 100:
        raise ValueError('Invalid add-on report')
    for addon in data['addons']:
        if not isinstance(addon, dict) or not isinstance(addon.get('transportUrl'), str) or not isinstance(addon.get('manifest'), dict):
            raise ValueError('Invalid add-on descriptor')
    urls = [a['transportUrl'] for a in data['addons']]
    target = request.get('addon', {}).get('transportUrl')
    error = data['error'] is not None
    if not error and request['operation'] == 'install' and target not in urls:
        raise ValueError('Install not verified')
    if not error and request['operation'] == 'remove' and target in urls:
        raise ValueError('Removal not verified')
    if not error:
        tvctl.save_private(STATE, {'tv_identity': identity(), 'addons': data['addons'], 'updated': time.time()})
    tvctl.save_private(REPORT, {'nonce': request['nonce'], 'operation': request['operation'],
                              'success': not error, 'count': len(urls)})


def operate(bind, operation, addon=None, timeout=40):
    bind = str(ipaddress.IPv4Address(bind))
    if operation not in ('list', 'install', 'remove'):
        raise ValueError('Unsupported add-on operation')
    nonce = secrets.token_urlsafe(24)
    value = {'nonce': nonce, 'operation': operation, 'tv_identity': identity(), 'expires': time.time() + timeout + 10}
    if addon is not None:
        value['addon'] = addon
    if (tvctl.PRIVATE / PENDING).exists():
        previous = tvctl.read_private(PENDING)
        if previous.get('expires', 0) > time.time():
            raise RuntimeError('Another add-on operation is still running. Try again shortly.')
    tvctl.save_private(PENDING, value)
    try:
        tvctl.launch(f'http://{bind}:8099/stremio/#/addons?manageLocalAddons={nonce}')
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                report = tvctl.read_private(REPORT)
                if report.get('nonce') == nonce:
                    if not report.get('success'):
                        raise RuntimeError('Stremio could not complete the change. Check the TV add-ons screen.')
                    return summary()
            except (OSError, ValueError):
                pass
            time.sleep(.4)
        raise RuntimeError('No confirmation from Stremio. Turn on the TV and try again.')
    finally:
        try:
            if tvctl.read_private(PENDING).get('nonce') == nonce:
                (tvctl.PRIVATE / PENDING).unlink()
        except (OSError, ValueError):
            pass


def selected_addon(key):
    for addon in cached_addons():
        if hashlib.sha256(addon['transportUrl'].encode()).hexdigest() == key:
            return addon
    raise RuntimeError('Refresh the TV add-on list and select an add-on again.')
