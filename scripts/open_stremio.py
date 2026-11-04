#!/usr/bin/env python3
"""Open one reviewed Stremio screen. Covering HDMI ends when Home/Input exits it."""
import argparse
import ipaddress
import urllib.parse
import urllib.request

import tvctl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', required=True, help='Linux PC IPv4 hosting serve_lab.py')
    parser.add_argument('--port', type=int, default=8099)
    parser.add_argument('--screen', choices=['browse', 'sample', 'addon', 'server'], default='browse')
    args = parser.parse_args()
    bind = str(ipaddress.IPv4Address(args.bind))
    origin = f'http://{bind}:{args.port}'
    with urllib.request.urlopen(origin + '/health', timeout=3) as response:
        if response.status != 200:
            raise RuntimeError('Lab server is not healthy')
    route = {
        'browse': '/',
        'sample': '/metadetails/movie/tvlab-bbb',
        'addon': '/addons?' + urllib.parse.urlencode({'addon': origin + '/addon/manifest.json'}),
        'server': '/settings?' + urllib.parse.urlencode({'streamingServerUrl': f'http://{bind}:11470'}),
    }[args.screen]
    result = tvctl.launch(origin + '/stremio/#' + route)
    print(f"Stremio {args.screen}: {result['STATUS']['RESULT']}. Home/Input leaves the transient page.")


if __name__ == '__main__':
    main()
