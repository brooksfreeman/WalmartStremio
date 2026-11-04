#!/usr/bin/env python3
"""PC-dependent startup and opt-in Home or WatchFree app-state redirect.

Not installed or enabled automatically. A missing network response is never
treated as power-off, and starting the watcher does not launch an app.
"""
import argparse
import datetime
import ipaddress
import time
import urllib.request

import tvctl
import home_navigation
from observe_home import snapshot


def power_value():
    result = tvctl.request('GET', '/state/device/power_mode')
    items = result.get('ITEMS', [])
    for item in items:
        if item.get('CNAME') == 'power_mode' and type(item.get('VALUE')) is int:
            return item['VALUE']
    raise RuntimeError('Unexpected power response; no launch')


def log(message):
    print(datetime.datetime.now().astimezone().isoformat(timespec='seconds'), message, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', required=True, help='Linux LAN IPv4 used by serve_lab.py')
    parser.add_argument('--port', type=int, default=8099)
    parser.add_argument('--dry-run', action='store_true', help='Observe transitions without launching')
    parser.add_argument('--once', action='store_true', help='One read-only power query, then exit')
    args = parser.parse_args()
    bind = str(ipaddress.IPv4Address(args.bind))
    origin = f'http://{bind}:{args.port}'
    previous = None
    previous_home = None
    pending_home = False
    last_launch = -float('inf')
    log('Observer started; initial state never launches. Shortcuts require explicit local opt-in.')
    while True:
        redirect_enabled = False
        try:
            current = power_value()
            if current != previous:
                log(f'Power value {previous} -> {current}')
            transitioned = previous == 0 and current == 1
            previous = current
            home_enabled = home_navigation.config()['redirect_home']
            watchfree_enabled = home_navigation.watchfree_enabled()
            redirect_enabled = home_enabled or watchfree_enabled
            state = snapshot() if current == 1 and redirect_enabled else {}
            watchfree = watchfree_enabled and home_navigation.is_watchfree(state)
            home = watchfree or (home_enabled and home_navigation.is_stock_home(state))
            trigger = 'WatchFree' if watchfree else 'Home'
            if home and previous_home is False:
                pending_home = True
            if not home:
                pending_home = False
            previous_home = home
            redirect = pending_home and not home_navigation.suspended() and time.monotonic() - last_launch >= 5
            if transitioned or redirect:
                if args.dry_run:
                    log(f'Dry run: would launch Stremio from {trigger}.' if redirect and watchfree else 'Dry run: would launch the configured start screen.')
                else:
                    with urllib.request.urlopen(origin + '/health', timeout=3) as response:
                        if response.status != 200:
                            raise RuntimeError('Local frontend unavailable; no launch')
                    startup = tvctl.PRIVATE / 'startup.json'
                    screen = tvctl.read_private(startup.name).get('screen', 'stremio') if startup.exists() else 'stremio'
                    if screen not in ('stremio', 'launcher'):
                        raise RuntimeError('Unknown startup screen; no launch')
                    tvctl.launch(origin + ('/launcher.html' if screen == 'launcher' and not (redirect and watchfree) else '/stremio/#/'))
                    log(f'{trigger} redirect launch accepted; visual behavior needs owner verification.' if redirect else 'Startup launch accepted; visual behavior needs owner verification.')
                pending_home = False
                last_launch = time.monotonic()
        except (OSError, ValueError, KeyError, RuntimeError) as exc:
            log(f'Query/action failed ({type(exc).__name__}); no inferred power transition.')
        if args.once:
            return
        time.sleep(1 if redirect_enabled else 5)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
