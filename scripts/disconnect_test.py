#!/usr/bin/env python3
"""Coordinated, bounded pause of the three PC TV helpers with timed recovery.

Run only after the owner is ready for the TV to cover HDMI and for app/Home
tests. The recovery timer belongs to systemd, so it survives this script ending.
No TV firmware, network access, credentials, or browser security is changed.
"""
import argparse
import datetime
import ipaddress
import socket
import subprocess
import time
import urllib.request

import tvctl

UNITS = ['vizio-stremio-lab.service', 'vizio-stremio-engine.service', 'vizio-stremio-watch.service']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', required=True)
    parser.add_argument('--seconds', type=int, default=60)
    args = parser.parse_args()
    if not 30 <= args.seconds <= 180:
        parser.error('Test interval must be 30..180 seconds')
    bind = str(ipaddress.IPv4Address(args.bind))
    origin = f'http://{bind}:8099'
    for unit in UNITS:
        state = subprocess.run(['systemctl', '--user', 'is-active', unit], capture_output=True, text=True)
        if state.stdout.strip() != 'active':
            raise RuntimeError('All three helpers must initially be active; no changes made')
    with urllib.request.urlopen(origin + '/launcher.html', timeout=3) as response:
        if response.status != 200:
            raise RuntimeError('Launcher unavailable; no changes made')
    tvctl.launch(origin + '/launcher.html?dependencyTest=1')
    print('Launcher requested. Allowing five seconds to load before pausing helpers.', flush=True)
    time.sleep(5)
    now = datetime.datetime.now(datetime.timezone.utc)
    unit = 'vizio-disconnect-recovery-' + now.strftime('%Y%m%dT%H%M%S')
    subprocess.run([
        'systemd-run', '--user', '--quiet', '--collect', '--unit=' + unit,
        '--on-active=' + str(args.seconds) + 's', '--timer-property=AccuracySec=1s',
        '/usr/bin/systemctl', '--user', 'start', *UNITS,
    ], check=True, capture_output=True)
    # Do not pause anything unless the independent recovery timer was armed.
    if (tvctl.PRIVATE / 'pc-disconnect-test.json').exists():
        tvctl.save_private('pc-disconnect-test.previous.json', tvctl.read_private('pc-disconnect-test.json'))
    tvctl.save_private('pc-disconnect-test.json', {
        'started_utc': now.isoformat(), 'duration_seconds': args.seconds,
        'recovery_unit': unit, 'initially_active': UNITS,
        'scope': 'Only PC helper services paused; PC OS and TV internet remain connected',
        'phase': 'recovery timer armed',
    })
    subprocess.run(['systemctl', '--user', 'stop', UNITS[2]], check=True)
    subprocess.run(['systemctl', '--user', 'stop', *UNITS[:2]], check=True)
    state = subprocess.run(['systemctl', '--user', 'is-active', *UNITS], capture_output=True, text=True)
    record = tvctl.read_private('pc-disconnect-test.json')
    record.update(phase='helpers paused', observed_unit_states=state.stdout.strip().splitlines())
    ports_closed = {}
    for port in (8099, 11470):
        try:
            with socket.create_connection((bind, port), timeout=1):
                ports_closed[str(port)] = False
        except OSError:
            ports_closed[str(port)] = True
    record['ports_closed_while_paused'] = ports_closed
    tvctl.save_private('pc-disconnect-test.json', record)
    if state.stdout.strip().splitlines() != ['inactive'] * 3 or not all(ports_closed.values()):
        subprocess.run(['systemctl', '--user', 'start', *UNITS], check=True)
        raise RuntimeError('Helpers did not isolate cleanly; restored services. Test inconclusive.')
    print('Helpers paused. Independent recovery timer will restart them in about', args.seconds, 'seconds.', flush=True)
    print('Test arrows, Netflix, then Home. Physical Input -> HDMI-2 returns to this PC.', flush=True)


if __name__ == '__main__':
    main()
