#!/usr/bin/env python3
"""Serve only the TV lab assets, never the project or credentials directory."""
import argparse
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import time
import urllib.parse

import tvctl
from launcher_apps import NATIVE_APPS
import home_navigation
import addon_manager

WEB = tvctl.ROOT / "web"
HOME_RESOURCE_READS = {
    '/app/osu/ui-logging/enabled':'get',
    '/app/osu/dlm/updates':'get',
    '/app/osu/activeFolder':'get',
    '/app/osu/manifest':'enumerate',
    '/app/osu/dlm':'enumerate',
    '/app/osu':'enumerate',
    '/app/osu/manifestHash':'get',
    '/app/osu/manifestVersion':'get',
    '/app/loki/home/apps/all':'get',
    '/app/loki/home/apps/default':'get',
    '/loki/home/catalog-services/catalog-url-type':'get',
    '/app/loki/deployer/active':'get',
    '/app/loki/home/apps':'enumerate',
    '/loki/home/catalog-services':'enumerate',
    '/loki/home/live-hero':'enumerate',
}

FILES = {"/loopback-home-policy.js", "/loopback-wamp-meta.js", "/tv-local-launcher-rest.html", "/tv-local-launcher.html", "/loopback-home-install.js", "/loopback-registry-probe.js", "/loopback-binding-probe.js", "/loopback-control-probe.js", "/loopback-file-probe.js", "/loopback-inventory.js", "/local-runtime.html", "/local-runtime.js", "/launcher.html", "/launcher.js", "/launcher.css", "/hello.html", "/hello.js", "/style.css", "/player.html", "/player.js", "/test-captions.vtt", "/vendor/hls.min.js",
         "/addon/manifest.json", "/addon/catalog/movie/tv-lab.json", "/addon/meta/movie/tvlab-bbb.json", "/addon/stream/movie/tvlab-bbb.json"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", required=True)
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument("--diagnostics", action="store_true", help="Opt in to local page/media event logs for troubleshooting")
    args = parser.parse_args()
    tv_ip = tvctl.read_private("tv.json")["ip"]
    allowed = {tv_ip, args.bind, "127.0.0.1"}
    origin = f"http://{args.bind}:{args.port}"
    events = tvctl.PRIVATE / "web-events.jsonl"

    def log_event(value):
        if not args.diagnostics:
            return
        fd = os.open(events, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a") as f:
            f.write(json.dumps(value, separators=(",", ":")) + "\n")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def respond(self, code, content=b"", content_type="application/json", stremio=False, launcher=False, runtime_probe=False):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            if urllib.parse.urlsplit(self.path).path in ('/tv-local-launcher.html','/tv-local-launcher-rest.html','/native-home-policy-permit') and self.client_address[0] == tv_ip and self.headers.get('Origin') == 'http://127.0.0.1:12345':
                self.send_header('Access-Control-Allow-Origin','http://127.0.0.1:12345')
                self.send_header('Vary','Origin')
            self.send_header("X-Content-Type-Options", "nosniff")
            policy = "default-src 'self'; connect-src 'self' https://test-streams.mux.dev; media-src 'self' blob: https://media.w3.org https://test-streams.mux.dev; worker-src 'self' blob:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'"
            if stremio:
                policy = "default-src 'self'; connect-src 'self' http: https: blob:; img-src 'self' http: https: data: blob:; media-src 'self' http: https: blob:; worker-src 'self' blob:; font-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'wasm-unsafe-eval'; frame-ancestors 'none'; base-uri 'self'"
            if launcher:
                policy = "default-src 'none'; connect-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
            if runtime_probe:
                policy = "default-src 'none'; connect-src 'self' http://127.0.0.1:12345; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
            self.send_header("Content-Security-Policy", policy)
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            if self.client_address[0] not in allowed:
                return self.respond(403)
            path = urllib.parse.urlsplit(self.path).path
            # Temporary source-acquisition diagnostics only. Record neither
            # query strings nor ordinary launcher/media activity.
            probe_assets = {'/local-runtime.html': 'page', '/local-runtime.js': 'script', '/loopback-home-install.js':'home-installer', '/tv-local-launcher.html':'home-package'}
            if self.client_address[0] == tv_ip and path in probe_assets and (tvctl.PRIVATE / 'native-capture.pending').exists():
                tvctl.save_private('native-probe-' + probe_assets[path] + '-access.json', {
                    'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'asset': path,
                })
            if path == '/native-home-policy-permit':
                if self.client_address[0] != tv_ip or self.headers.get('Origin') != 'http://127.0.0.1:12345':
                    return self.respond(403)
                try:
                    permit=tvctl.read_private('native-home-policy-permit.json')
                    query=urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
                    if permit['expires'] < time.time() or query != {'operation':[permit['operation']],'nonce':[permit['nonce']]}:
                        return self.respond(403)
                except (OSError,ValueError,KeyError):
                    return self.respond(403)
                return self.respond(200,json.dumps({'operation':permit['operation'],'nonce':permit['nonce']}).encode())
            if path.startswith('/stremio/'):
                build = (tvctl.PRIVATE / 'stremio-tv-src/build').resolve()
                relative = urllib.parse.unquote(path[len('/stremio/'):]) or 'index.html'
                asset = (build / relative).resolve()
                if not asset.is_relative_to(build) or not asset.is_file():
                    return self.respond(404)
                content_type = 'application/wasm' if asset.suffix == '.wasm' else mimetypes.guess_type(asset)[0] or 'application/octet-stream'
                return self.respond(200, asset.read_bytes(), content_type, stremio=True)
            if path == "/health":
                return self.respond(200, b'{"ok":true}')
            if path == '/launcher-wallpaper.jpg':
                asset = tvctl.PRIVATE / 'launcher-wallpaper.jpg'
                if not asset.is_file():
                    return self.respond(404)
                return self.respond(200, asset.read_bytes(), 'image/jpeg', launcher=True)
            if path in ("/media/bbb-trailer.mp4", "/media/bbb-compatible.mp4"):
                media = tvctl.PRIVATE / "media" / Path(path).name
                if not media.is_file():
                    return self.respond(404)
                size = media.stat().st_size
                start, end = 0, size - 1
                byte_range = self.headers.get("Range")
                if byte_range:
                    match = re.fullmatch(r"bytes=(\d+)-(\d*)", byte_range)
                    if not match:
                        return self.respond(416)
                    start = int(match[1])
                    end = min(int(match[2]), end) if match[2] else end
                    if start > end:
                        return self.respond(416)
                self.send_response(206 if byte_range else 200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(end - start + 1))
                if byte_range:
                    self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.end_headers()
                log_event({"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           "peer": self.client_address[0], "kind": "media-range", "start": start, "end": end})
                try:
                    with media.open("rb") as f:
                        f.seek(start)
                        remaining = end - start + 1
                        while remaining:
                            chunk = f.read(min(65536, remaining))
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            remaining -= len(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            if path not in FILES:
                return self.respond(404)
            asset = WEB / path.lstrip("/")
            if not path.startswith('/launcher.'):
                log_event({"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           "peer": self.client_address[0], "kind": "asset", "path": path})
            content = asset.read_bytes()
            if path.startswith('/addon/'):
                content = content.replace(b'__LAB_ORIGIN__', origin.encode())
            return self.respond(200, content, mimetypes.guess_type(asset)[0] or "application/octet-stream", launcher=path.startswith('/launcher.'), runtime_probe=path.startswith('/local-runtime.'))

        def do_POST(self):
            path = urllib.parse.urlsplit(self.path).path
            expected_origin = 'http://127.0.0.1:12345' if path in ('/native-home-policy-report','/loopback-origin-report','/loopback-file-report','/loopback-control-report','/loopback-binding-report','/loopback-registry-report','/loopback-home-report','/loopback-wamp-meta-report') else origin
            if self.client_address[0] not in allowed or self.headers.get("Origin") != expected_origin:
                return self.respond(403)
            if path not in ("/native-home-policy-report", "/loopback-wamp-meta-report", "/loopback-home-report", "/loopback-registry-report", "/loopback-binding-report", "/loopback-control-report", "/loopback-file-report", "/loopback-origin-report", "/native-bridge-report", "/home-script-report", "/home-source-report", "/local-runtime-report", "/launcher/launch", "/event", "/home", "/addon-import", "/addon-backup", "/addon-import-complete", "/addon-manager/request", "/addon-manager/backup", "/addon-manager/report"):
                return self.respond(404)
            if path.startswith('/addon-') and self.client_address[0] != tv_ip:
                return self.respond(403)
            if path in ('/native-home-policy-report', '/local-runtime-report', '/home-source-report', '/home-script-report', '/native-bridge-report', '/loopback-origin-report', '/loopback-file-report', '/loopback-control-report', '/loopback-binding-report', '/loopback-registry-report', '/loopback-home-report', '/loopback-wamp-meta-report') and self.client_address[0] != tv_ip:
                return self.respond(403)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                limit = 262144 if path in ('/loopback-binding-report','/loopback-registry-report','/loopback-home-report','/loopback-wamp-meta-report') else 20000000 if path == '/home-script-report' else 3500000 if path in ('/local-runtime-report', '/home-source-report') else 262144 if path in ('/addon-backup','/addon-manager/backup','/addon-manager/report') else 16384
                if length < 0 or length > limit:
                    return self.respond(413)
                data = json.loads(self.rfile.read(length) or b"{}")
                if not isinstance(data, dict):
                    return self.respond(400)
                if path == '/addon-manager/request':
                    try:
                        pending = addon_manager.pending_request(data.get('nonce'))
                    except (OSError, ValueError):
                        return self.respond(403)
                    public = {key:pending[key] for key in ('operation','addon') if key in pending}
                    return self.respond(200, json.dumps(public).encode())
                elif path == '/addon-manager/backup':
                    pending = addon_manager.pending_request(data.get('nonce'))
                    addons = data.get('addons')
                    if not isinstance(addons,list) or len(addons)>100:
                        return self.respond(400)
                    (tvctl.PRIVATE/'addon-manager-backups').mkdir(mode=0o700,exist_ok=True)
                    name = 'addon-manager-backups/'+pending['nonce']+'.json'
                    if not (tvctl.PRIVATE/name).exists():
                        tvctl.save_private(name, {'tv_identity':pending['tv_identity'],'addons':addons})
                    return self.respond(200,b'{"ok":true}')
                elif path == '/addon-manager/report':
                    addon_manager.receive_report(data)
                    return self.respond(200,b'{"ok":true}')
                elif path == '/native-home-policy-report':
                    if set(data) != {'nonce','operation','phase','previous','current','error'} or data.get('operation') not in ('preflight','apply','restore') or data.get('phase') not in ('before','complete','error'):
                        return self.respond(400)
                    try:
                        permit=tvctl.read_private('native-home-policy-permit.json')
                        if permit['expires'] < time.time() or data['nonce'] != permit['nonce'] or data['operation'] != permit['operation']:
                            return self.respond(403)
                    except (OSError,ValueError,KeyError):
                        return self.respond(403)
                    tvctl.save_private('native-home-policy-'+data['operation']+'.json',data)
                    return self.respond(200,b'{"ok":true}')
                elif path == '/loopback-wamp-meta-report':
                    if set(data) != {'origin','realm','router_roles','feature_names','registration_count','uris','error','detail_limit'} or data.get('origin') != expected_origin or data.get('realm')!='systemregistry':
                        return self.respond(400)
                    tvctl.save_private('loopback-wamp-meta.json',data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/loopback-home-report':
                    if set(data) != {'origin','mode','steps','html_sha256','bridge_available','native_launch_at','error'} or data.get('origin') != expected_origin or data.get('mode') not in ('install','open','test','cleanup','install-rest','open-rest','test-rest','cleanup-rest'):
                        return self.respond(400)
                    tvctl.save_private('loopback-home-' + data['mode'] + '.json',data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/loopback-registry-report':
                    if set(data) != {'origin','operation','key','result','error'} or data.get('origin') != expected_origin or data.get('operation') not in ('enumerate','get') or data.get('key') not in (*HOME_RESOURCE_READS,'','/','/home','/app','/apps','/loki','/bootsc','/systemregistry','/loki/home','/app/home','/app/loki','/app/deployer','/app/platformorchestrator','/systemregistry/defaults','/app/platformorchestrator/appmanager','/app/platformorchestrator/appsdatabase','/app/loki/config','/app/loki/home','/app/loki/deployer','/loki/home/dev-tools','/app/platformorchestrator/appsdatabase/home_provider','/app/platformorchestrator/appsdatabase/apps','/app/platformorchestrator/appsdatabase/app_symbols','/app/platformorchestrator/appsdatabase/app_aliases','/app/platformorchestrator/appmanager/apps_status','/app/deployer/appVersionMap','/app/loki/bundle_version','/app/platformorchestrator/cache','/app/platformorchestrator/multiplexer','/loki/home/devtool','/loki/debug','/debug','/debug/platformorchestrator','/debug/conjure','/app/systemregistry','/app/scpl','/app/routines','/debug/platformorchestrator/appmanager','/app/routines/list','/app/systemregistry/sysreg.json','/debug/platformorchestrator/appmanager/state_machine'):
                        return self.respond(400)
                    if data['key'] in HOME_RESOURCE_READS and data['operation'] != HOME_RESOURCE_READS[data['key']]:
                        return self.respond(400)
                    if data['operation']=='get' and data['key'] not in (*HOME_RESOURCE_READS,'/app/platformorchestrator/appsdatabase/home_provider','/app/platformorchestrator/appsdatabase/apps','/app/platformorchestrator/appsdatabase/app_symbols','/app/platformorchestrator/appsdatabase/app_aliases','/app/platformorchestrator/appmanager/apps_status','/app/deployer/appVersionMap','/app/loki/bundle_version','/app/platformorchestrator/cache','/app/platformorchestrator/multiplexer','/loki/home/devtool','/loki/debug','/debug','/debug/platformorchestrator','/debug/conjure','/app/systemregistry','/app/scpl','/app/routines','/debug/platformorchestrator/appmanager','/app/routines/list','/app/systemregistry/sysreg.json','/debug/platformorchestrator/appmanager/state_machine'):
                        return self.respond(400)
                    tvctl.save_private('loopback-registry-' + ('root' if not data['key'] else 'slash' if data['key']=='/' else data['key'][1:].replace('/','_')) + '.json',data)
                    tvctl.save_private('loopback-registry-' + ('root' if not data['key'] else 'slash' if data['key']=='/' else data['key'][1:].replace('/','_')) + '-' + data['operation'] + '.json',data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/loopback-binding-report':
                    if set(data) != {'origin','functions','connections','appman','errors'} or data.get('origin') != expected_origin:
                        return self.respond(400)
                    tvctl.save_private('loopback-binding-metadata.json',data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/loopback-control-report':
                    if set(data) != {'origin','bootstrap_status','token_available','capabilities_status','capability_keys','bindings','error'} or data.get('origin') != expected_origin:
                        return self.respond(400)
                    tvctl.save_private('loopback-control-read.json',data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/loopback-file-report':
                    if set(data) != {'phase','origin','protocol','steps','error','url'} or data.get('origin') != expected_origin or data.get('phase') not in ('write','open','cleanup','executed'):
                        return self.respond(400)
                    tvctl.save_private('loopback-file-' + data['phase'] + '.json',data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/loopback-origin-report':
                    keys = {'origin','secure_context','connection_type','own_names','prototype_names','cache_storage','service_worker','indexed_db','registrations','cache_count','idb_count','errors','file_system_request','storage_persisted','storage_estimate','debuggers'}
                    if set(data) != keys or data.get('origin') != expected_origin:
                        return self.respond(400)
                    tvctl.save_private('loopback-origin-inventory.json',data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/native-bridge-report':
                    if set(data) != {'connection_type','own_names','prototype_names','send_type','receive_type'}:
                        return self.respond(400)
                    for key in ('connection_type','send_type','receive_type'):
                        if not isinstance(data[key],str) or len(data[key]) > 80:
                            return self.respond(400)
                    for key in ('own_names','prototype_names'):
                        if not isinstance(data[key],list) or len(data[key]) > 40 or any(not isinstance(x,str) or len(x)>80 for x in data[key]):
                            return self.respond(400)
                    tvctl.save_private('native-bridge-inventory.json',data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/home-script-report':
                    targets = {'sctv-app': '/scfs/sctv/app.js', 'system-ui-main': '/scfs/system-ui-app/static/js/main.61012d2e.chunk.js', 'sctv-worker': '/scfs/sctv/service-worker.js', 'sctv-source-map': '/scfs/sctv/app.js.map', 'conjure-main': '/scfs/conjure/main.html', 'conjure-index': '/scfs/conjure/index.html', 'conjure-package': '/scfs/conjure/package.json', 'scu-package': '/scfs/scu/package.json', 'conjure-script': '/scfs/conjure/js/scripts.js'}
                    if not isinstance(data.get('name'), str) or data['name'] not in targets or data.get('path') != targets[data['name']] or not set(data) <= {'name', 'path', 'status', 'bytes', 'oversized', 'text', 'error'}:
                        return self.respond(400)
                    if not isinstance(data.get('text', ''), str) or len(data.get('text', '').encode()) > 8*1024*1024:
                        return self.respond(413)
                    tvctl.save_private(data['name']+'-report.json', data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/home-source-report':
                    if set(data) != {'resources'} or not isinstance(data['resources'], dict) or set(data['resources']) not in ({'scu', 'system-ui-app'}, {'scu-loader'}, {'sctv', 'system-ui-index'}):
                        return self.respond(400)
                    report_name = 'actual-home-report.json' if 'sctv' in data['resources'] else 'home-loader-report.json' if 'scu-loader' in data['resources'] else 'home-source-report.json'
                    tvctl.save_private(report_name, data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/local-runtime-report':
                    if set(data) != {'features', 'resources'} or not isinstance(data['features'], dict) or not isinstance(data['resources'], dict) or set(data['resources']) != {'manifest', 'companion'}:
                        return self.respond(400)
                    tvctl.save_private('local-runtime-report.json', data)
                    return self.respond(200, b'{"ok":true}')
                elif path == '/launcher/launch':
                    # A closed list of reviewed launch descriptors. Never accept
                    # app IDs, URLs, namespace values, or settings from a page.
                    if set(data) != {'app'} or not isinstance(data['app'], str) or data['app'] not in (*NATIVE_APPS, 'tv'):
                        return self.respond(400)
                    if data['app'] == 'tv':
                        home_navigation.return_to_hdmi()
                    else:
                        tvctl.request('PUT', '/app/launch', {'VALUE': NATIVE_APPS[data['app']]})
                    return self.respond(200, b'{"ok":true}')
                elif path == '/addon-import':
                    pending = tvctl.PRIVATE / 'addon-import.pending.json'
                    if not pending.is_file():
                        return self.respond(404)
                    return self.respond(200, pending.read_bytes())
                elif path == '/addon-backup':
                    addons = data.get('addons')
                    if not isinstance(addons, list) or len(addons) > 100:
                        return self.respond(400)
                    if not (tvctl.PRIVATE / 'tv-addons-before-import.json').exists():
                        tvctl.save_private('tv-addons-before-import.json', {'addons': addons})
                    data = {'kind': 'addon-backup-saved', 'message': f'{len(addons)} addon descriptors; URLs withheld'}
                elif path == '/addon-import-complete':
                    pending = tvctl.PRIVATE / 'addon-import.pending.json'
                    if not pending.exists() or data.get('count') != len(tvctl.read_private(pending.name)['addons']):
                        return self.respond(400)
                    pending.replace(tvctl.PRIVATE / 'addon-import.completed.json')
                    data = {'kind': 'addon-import-verified', 'message': f"{data['count']} addon descriptors present in TV app; URLs withheld"}
                elif path == "/home":
                    tvctl.home()
                    data = {"kind": "home-api-success"}
                else:
                    keys = {"kind", "key", "code", "focused", "button", "ua", "width", "height", "video", "message"}
                    data = {k: v for k, v in data.items() if k in keys}
                data.update(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), peer=self.client_address[0])
                log_event(data)
                return self.respond(200, b'{"ok":true}')
            except (OSError, ValueError, RuntimeError, KeyError):
                return self.respond(500, b'{"ok":false}')

    server = ThreadingHTTPServer((args.bind, args.port), Handler)
    print(f"Lab listening at {origin}/hello.html; only TV and this PC admitted.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
