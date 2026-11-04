#!/usr/bin/env python3
"""Read/change only two observed normal privacy menu toggles; never store keys."""
import argparse
import datetime
import json

import tvctl

SETTINGS = {
    'viewing_data': ('/menu_native/dynamic/tv_settings/privacy_and_legal/vizio_viewing_data', 'vizio_viewing_data', 'Off'),
    'limited_ad_tracking': ('/menu_native/dynamic/tv_settings/privacy_and_legal/advertising/limit_ad_tracking', 'limit_ad_tracking', 'On'),
}


def read(name):
    path, cname, _ = SETTINGS[name]
    result = tvctl.request('GET', path)
    matches = [x for x in result.get('ITEMS', []) if x.get('CNAME') == cname]
    if len(matches) != 1:
        raise RuntimeError('Unexpected privacy menu; no change')
    item = matches[0]
    if item.get('TYPE') != 'T_LIST_V1' or item.get('VALUE') not in ('On', 'Off') or type(item.get('HASHVAL')) is not int:
        raise RuntimeError('Unexpected privacy value/type; no change')
    return item


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'apply', 'restore'])
    args = parser.parse_args()
    before = {name: read(name) for name in SETTINGS}
    if args.action == 'status':
        print(json.dumps({name: x['VALUE'] for name, x in before.items()}, indent=2))
        return
    backup = tvctl.PRIVATE / 'privacy-settings-backup.json'
    if args.action == 'apply':
        if not backup.exists():
            tvctl.save_private(backup.name, {name: x['VALUE'] for name, x in before.items()})
        desired = {name: spec[2] for name, spec in SETTINGS.items()}
    else:
        desired = tvctl.read_private(backup.name)
        if set(desired) != set(SETTINGS) or any(v not in ('On', 'Off') for v in desired.values()):
            raise RuntimeError('Invalid saved toggle backup; no change')
    for name, value in desired.items():
        item = read(name)
        if item['VALUE'] != value:
            tvctl.request('PUT', SETTINGS[name][0], {'REQUEST': 'MODIFY', 'HASHVAL': item['HASHVAL'], 'VALUE': value})
        if read(name)['VALUE'] != value:
            raise RuntimeError(f'{name}: read-back did not match; inspect before proceeding')
        print(f'{name}: {value} (read-back verified)')
    record = {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'action': args.action,
        'before': {name: x['VALUE'] for name, x in before.items()},
        'after': desired,
        'verification': 'normal menu API read-back; no traffic capture or zero-telemetry claim',
    }
    (tvctl.ROOT / 'research/reviews/privacy-settings-result.json').write_text(json.dumps(record, indent=2) + '\n')


if __name__ == '__main__':
    main()
