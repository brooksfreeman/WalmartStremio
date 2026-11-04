#!/usr/bin/env python3
"""Launch one read-only native source probe after a physical Home transition.

Run with the PC watcher paused and its independent recovery timer armed.
No input changes, remote-key guessing, configuration writes or firmware actions.
"""
import argparse
import ipaddress
import subprocess
import time

import tvctl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', required=True)
    args = parser.parse_args()
    bind = str(ipaddress.IPv4Address(args.bind))
    state = subprocess.run(['systemctl','--user','is-active','vizio-stremio-watch.service'],
                           capture_output=True,text=True).stdout.strip()
    if state != 'inactive':
        raise RuntimeError('Pause the watcher before starting this diagnostic')
    deadline = time.monotonic() + 180
    print('Waiting for physical Home; only read-only state queries until then.',flush=True)
    while time.monotonic() < deadline:
        try:
            value = tvctl.request('GET','/state_extended')
            current = value.get('CURRENT_INPUT')
            app = value.get('APP_CURRENT')
            if (isinstance(current,dict) and current.get('NAME') == 'SMARTCAST'
                    and isinstance(app,dict) and app.get('NAME_SPACE') == 4
                    and app.get('APP_ID') == '1'):
                observed = {'input':'SMARTCAST','app':{'NAME_SPACE':4,'APP_ID':'1'}}
                tvctl.save_private('native-physical-home-trigger.json',observed)
                result = tvctl.launch(f'http://{bind}:8099/local-runtime.html?nativeEntries=1')
                print('Physical Home observed; probe launch '+result['STATUS']['RESULT'],flush=True)
                return
        except (OSError,RuntimeError,ValueError) as error:
            print('State unavailable: '+type(error).__name__,flush=True)
        time.sleep(3)
    print('No valid physical Home state observed; no probe launched.',flush=True)


if __name__ == '__main__':
    main()
