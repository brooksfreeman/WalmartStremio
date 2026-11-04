#!/usr/bin/env python3
"""Reversible automatic-sleep settings and a persistent server sleep inhibitor."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

import tvctl

SCHEMA = 'org.gnome.settings-daemon.plugins.power'
GNOME = {'sleep-inactive-ac-type': "'nothing'", 'sleep-inactive-battery-type': "'nothing'",
         'sleep-inactive-ac-timeout': '0', 'sleep-inactive-battery-timeout': '0'}
XFCE = ['/xfce4-power-manager/inactivity-on-ac', '/xfce4-power-manager/inactivity-on-battery']
UNIT = 'vizio-stremio-awake.service'


def run(*args, check=True):
    return subprocess.run(args, capture_output=True, text=True, check=check, timeout=20)


def settings():
    values = {'gnome': {}, 'xfce': {}}
    for key in GNOME:
        values['gnome'][key] = run('gsettings', 'get', SCHEMA, key).stdout.strip()
    for key in XFCE:
        result = run('xfconf-query', '-c', 'xfce4-power-manager', '-p', key, check=False)
        values['xfce'][key] = result.stdout.strip() if result.returncode == 0 else None
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['apply', 'status', 'restore'])
    args = parser.parse_args()
    backup = tvctl.PRIVATE / 'server-power-before.json'
    if args.action == 'apply':
        original = settings()
        if not backup.exists():
            tvctl.save_private(backup.name, original)
        for key, value in GNOME.items():
            run('gsettings', 'set', SCHEMA, key, value)
        for key in XFCE:
            extra = ['-n', '-t', 'uint'] if original['xfce'][key] is None else []
            # Installed Xfce4.18 uses14 to remove its inactivity sleep alarm.
            run('xfconf-query', '-c', 'xfce4-power-manager', '-p', key, *extra, '-s', '14')
        destination = Path.home() / '.config/systemd/user' / UNIT
        source = tvctl.ROOT / 'config/systemd' / UNIT
        if destination.exists() and destination.read_bytes() != source.read_bytes():
            old_unit = tvctl.PRIVATE / 'server-awake-unit-before.service'
            if not old_unit.exists():
                old_unit.write_bytes(destination.read_bytes()); old_unit.chmod(0o600)
        shutil.copyfile(source, destination)
        run('systemctl', '--user', 'daemon-reload')
        run('systemctl', '--user', 'enable', '--now', UNIT)
    elif args.action == 'restore':
        original = tvctl.read_private(backup.name)
        run('systemctl', '--user', 'disable', '--now', UNIT)
        for key, value in original['gnome'].items():
            run('gsettings', 'set', SCHEMA, key, value)
        for key, value in original['xfce'].items():
            if value is None:
                run('xfconf-query', '-c', 'xfce4-power-manager', '-p', key, '-r', check=False)
            else:
                run('xfconf-query', '-c', 'xfce4-power-manager', '-p', key, '-s', value)
    value = settings()
    value['sleep_inhibitor_active'] = run('systemctl', '--user', 'is-active', '--quiet', UNIT, check=False).returncode == 0
    value['automatic_sleep_disabled'] = all(value['gnome'][k] == v for k, v in GNOME.items()) and all(value['xfce'][k] == '14' for k in XFCE)
    print(json.dumps(value, indent=2))


if __name__ == '__main__':
    main()
