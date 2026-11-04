#!/usr/bin/env python3
"""Read-only input/app observer for distinguishing Vizio Home from HDMI."""
import argparse
import datetime
import json
import time

import tvctl


def snapshot():
    result = tvctl.request('GET', '/menu_native/dynamic/tv_settings/devices/current_input')
    inputs = [x['VALUE'] for x in result.get('ITEMS', []) if x.get('CNAME') == 'current_input']
    if len(inputs) != 1 or not isinstance(inputs[0], str):
        raise RuntimeError('Unexpected input response')
    app = tvctl.request('GET', '/app/current').get('ITEM', {}).get('VALUE', {})
    return {'input': inputs[0], 'app': {'NAME_SPACE': app.get('NAME_SPACE'), 'APP_ID': app.get('APP_ID')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=int, default=180)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 600:
        parser.error('seconds must be 1..600')
    start = time.monotonic()
    changes = []
    previous = None
    print('Read-only Home observer started. No launches or setting changes.', flush=True)
    while time.monotonic() - start < args.seconds:
        try:
            current = snapshot()
            if current != previous:
                item = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), **current}
                changes.append(item)
                print(json.dumps(item), flush=True)
                tvctl.save_private('home-input-observation.json', {'changes': changes, 'effect': 'GET only'})
                previous = current
        except (OSError, ValueError, RuntimeError, KeyError) as exc:
            print('Read failed:', type(exc).__name__, flush=True)
        time.sleep(2)


if __name__ == '__main__':
    main()
