#!/usr/bin/env python3
"""Bounded, certificate-pinned GETs of documented native installation surfaces.

Reads only. Never submits a package, starts an update, obtains an internal
credential, enables debugging, or changes configuration.
"""
import hashlib
import http.client
import json
import os
import ssl
from pathlib import Path

import tvctl

PATHS = ('/install', '/scpl/install', '/static/install.html',
         '/dlm/available_update_info', '/uli/available_update_info')


def main():
    state = tvctl.read_private('tv.json')
    directory = tvctl.PRIVATE / 'native-installation-reads'
    directory.mkdir(mode=0o700, exist_ok=True)
    results = []
    for index, path in enumerate(PATHS):
        connection = http.client.HTTPSConnection(state['ip'], 7345, timeout=8,
                                                 context=ssl._create_unverified_context())
        try:
            connection.connect()
            fingerprint = hashlib.sha256(connection.sock.getpeercert(binary_form=True)).hexdigest()
            if fingerprint != state['certificate_sha256']:
                raise RuntimeError('TV certificate pin changed')
            connection.request('GET', path, headers={
                'AUTH': tvctl.read_private('credentials.json')['auth_token'],
                'Accept': '*/*', 'Connection': 'close',
            })
            response = connection.getresponse()
            body = response.read(1024*1024+1)
            if len(body) > 1024*1024:
                raise RuntimeError('Response exceeded bounded read')
            destination = directory / f'{index}.response'
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(body)
            item = {'method': 'GET', 'path': path, 'status': response.status,
                    'content_type': response.getheader('Content-Type'),
                    'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
            try:
                value = json.loads(body)
                item['result'] = value.get('STATUS', {}).get('RESULT')
                content = value.get('ITEM', {}).get('VALUE')
                if isinstance(content, dict):
                    item['value_keys'] = list(content)
                    if type(content.get('IS_AVAILABLE')) is bool:
                        item['update_available'] = content['IS_AVAILABLE']
            except (ValueError, AttributeError):
                pass
            results.append(item)
        except (OSError, RuntimeError) as error:
            results.append({'method': 'GET', 'path': path, 'error': str(error)})
        finally:
            connection.close()
    tvctl.save_private('native-installation-read-summary.json', results)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
