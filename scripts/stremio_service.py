#!/usr/bin/env python3
"""Prepare/run the pinned official Stremio engine with a local IP allowlist.

No system package, tray, startup entry, or firewall rule is installed.
"""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import urllib.request

import tvctl

VERSION = 'v0.1.22'
SHA256 = 'fcbab342fcd8990312b400698ae85f9c87aed0326a0da0168c1ddba18c39a415'
URL = f'https://github.com/Stremio/stremio-service/releases/download/{VERSION}/stremio-service_amd64.deb'
DEPS = tvctl.PRIVATE / 'deps'
PACKAGE = DEPS / 'stremio-service_amd64.deb'
BUNDLE = DEPS / 'stremio-service/usr/share/stremio-service'
WORK = tvctl.PRIVATE / 'stremio-server'


def prepare(bind, port):
    ipaddress.IPv4Address(bind)
    tv_ip = str(ipaddress.IPv4Address(tvctl.read_private('tv.json')['ip']))
    DEPS.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not PACKAGE.exists():
        temp = PACKAGE.with_suffix('.download')
        urllib.request.urlretrieve(URL, temp)
        if hashlib.sha256(temp.read_bytes()).hexdigest() != SHA256:
            raise RuntimeError('Official package SHA-256 mismatch')
        temp.replace(PACKAGE)
    if hashlib.sha256(PACKAGE.read_bytes()).hexdigest() != SHA256:
        raise RuntimeError('Official package SHA-256 mismatch')
    subprocess.run(['dpkg-deb', '-x', str(PACKAGE), str(DEPS / 'stremio-service')], check=True)
    original = (BUNDLE / 'server.js').read_text()
    source = original
    old = 'http.createServer(app)), port = 11470;'
    peers = json.dumps(['127.0.0.1', '::1', bind, tv_ip])
    new = ('http.createServer(function(req, res) { '
           'var peer = String(req.socket.remoteAddress || "").replace(/^::ffff:/, ""); '
           f'if ({peers}.indexOf(peer) < 0) {{ res.statusCode = 403; return res.end("Forbidden"); }} '
           'app(req, res); })), port = 11470;')
    if source.count(old) != 1:
        raise RuntimeError('Unexpected server HTTP listener; review required')
    source = source.replace(old, new)
    old = '"https://stremio.github.io" === req.headers.origin'
    if source.count(old) != 1:
        raise RuntimeError('Unexpected server CORS handler; review required')
    source = source.replace(old, f'({json.dumps(f"http://{bind}:{port}")} === req.headers.origin || {old})')
    WORK.mkdir(mode=0o700, exist_ok=True)
    (WORK / 'state').mkdir(mode=0o700, exist_ok=True)
    (WORK / 'server.js').write_text(source)
    tvctl.save_private('stremio-server-preparation.json', {
        'service': VERSION, 'package_url': URL, 'package_sha256': SHA256,
        'source_sha256': hashlib.sha256(original.encode()).hexdigest(),
        'patched_sha256': hashlib.sha256(source.encode()).hexdigest(),
        'allowed_ips': json.loads(peers), 'frontend_origin': f'http://{bind}:{port}',
    })
    print('Prepared verified official engine. HTTP clients limited to this PC and TV; HTTPS/casting disabled.')


def run():
    record = tvctl.read_private('stremio-server-preparation.json')
    if hashlib.sha256((WORK / 'server.js').read_bytes()).hexdigest() != record['patched_sha256']:
        raise RuntimeError('Prepared server changed; review or prepare again')
    env = dict(os.environ, APP_PATH=str(WORK / 'state'), SETTINGS_PATH=str(WORK / 'state'),
               FFMPEG_BIN=str(BUNDLE / 'ffmpeg'), FFPROBE_BIN=str(BUNDLE / 'ffprobe'),
               CASTING_DISABLED='1', NO_HTTPS_SERVER='1')
    os.execve(str(BUNDLE / 'stremio-runtime'), [str(BUNDLE / 'stremio-runtime'), str(WORK / 'server.js')], env)


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run'])
    parser.add_argument('--bind')
    parser.add_argument('--frontend-port', type=int, default=8099)
    args = parser.parse_args()
    if args.command == 'prepare':
        if not args.bind:
            parser.error('prepare requires --bind <PC IPv4>')
        prepare(args.bind, args.frontend_port)
    else:
        run()


if __name__ == '__main__':
    main()
