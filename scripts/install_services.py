#!/usr/bin/env python3
"""Prepare/install the three reversible per-user TV services. Does not enable them."""
import argparse
import datetime
import ipaddress
import shutil
from pathlib import Path

import tvctl


def quoted(value):
    value = str(value)
    if '\n' in value or '\r' in value:
        raise ValueError('Newline in systemd argument')
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%') + '"'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', required=True)
    parser.add_argument('--install', action='store_true', help='Copy reviewed units into ~/.config/systemd/user; back up existing same-name units')
    args = parser.parse_args()
    bind = str(ipaddress.IPv4Address(args.bind))
    prepared = tvctl.ROOT / 'config/systemd'
    prepared.mkdir(parents=True, exist_ok=True)
    installed = Path.home() / '.config/systemd/user'
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    for component in ('lab', 'engine', 'watch'):
        name = f'vizio-stremio-{component}.service'
        dependencies = ''
        if component == 'watch':
            dependencies = 'Requires=vizio-stremio-lab.service vizio-stremio-engine.service\nAfter=vizio-stremio-lab.service vizio-stremio-engine.service\n'
        text = (f'[Unit]\nDescription=Owner TV Stremio {component}\nStartLimitIntervalSec=0\n{dependencies}\n'
                '[Service]\nType=simple\n'
                f'ExecStart=/usr/bin/python3 {quoted(tvctl.ROOT / "scripts/service_entry.py")} {component} --bind {bind}\n'
                'Restart=on-failure\nRestartSec=5\nUMask=0077\nStandardOutput=null\nStandardError=null\n\n'
                '[Install]\nWantedBy=default.target\n')
        source = prepared / name
        source.write_text(text)
        if args.install:
            installed.mkdir(parents=True, exist_ok=True)
            dest = installed / name
            if dest.exists() and dest.read_text() != text:
                backup = tvctl.PRIVATE / 'service-backups' / timestamp
                backup.mkdir(parents=True, mode=0o700, exist_ok=True)
                shutil.copy2(dest, backup / name)
            shutil.copyfile(source, dest)
        print(('Installed: ' if args.install else 'Prepared: ') + name)


if __name__ == '__main__':
    main()
