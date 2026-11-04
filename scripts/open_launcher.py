#!/usr/bin/env python3
"""Open the local clean launcher; Home/Input remains the TV escape path."""
import argparse
import ipaddress
import urllib.request

import tvctl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', required=True)
    parser.add_argument('--port', type=int, default=8099)
    args = parser.parse_args()
    origin = f'http://{ipaddress.IPv4Address(args.bind)}:{args.port}'
    with urllib.request.urlopen(origin + '/launcher.html', timeout=3) as response:
        if response.status != 200:
            raise RuntimeError('Local launcher unavailable')
    result = tvctl.launch(origin + '/launcher.html')
    print('Clean launcher:', result['STATUS']['RESULT'])


if __name__ == '__main__':
    main()
