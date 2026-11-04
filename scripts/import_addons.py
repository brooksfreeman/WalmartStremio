#!/usr/bin/env python3
"""Copy only existing local Stremio addon descriptors into a one-use TV import.

Reads the Flatpak's profile read-only. Never copies its auth or account settings.
No network requests are made and URLs are never printed.
"""
import argparse
import json
from pathlib import Path
import sqlite3

import tvctl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only-torrentio', action='store_true', help='Transfer only the existing configured Torrentio descriptor')
    args = parser.parse_args()
    root = Path.home() / '.var/app/com.stremio.Stremio/data/stremio/storage'
    matches = []
    for path in root.rglob('localstorage.sqlite3'):
        with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as con:
            row = con.execute("SELECT value FROM ItemTable WHERE key='profile'").fetchone()
        if not row:
            continue
        try:
            profile = json.loads(row[0])
        except (ValueError, UnicodeDecodeError):
            profile = json.loads(row[0].decode('utf-16-le'))
        addons = [{key: addon[key] for key in ('manifest', 'transportUrl', 'flags') if key in addon}
                  for addon in profile.get('addons', [])]
        if any(addon.get('manifest', {}).get('id') == 'com.stremio.torrentio.addon' for addon in addons):
            matches.append(addons)
    if len(matches) != 1:
        raise RuntimeError('Expected exactly one local profile containing Torrentio; nothing copied')
    addons = matches[0]
    if args.only_torrentio:
        addons = [addon for addon in addons if addon.get('manifest', {}).get('id') == 'com.stremio.torrentio.addon']
        if len(addons) != 1:
            raise RuntimeError('Expected exactly one configured Torrentio descriptor; nothing copied')
    tvctl.save_private('addon-import.pending.json', {'addons': addons})
    print(f'Prepared {len(addons)} locally cached addon descriptors, including Torrentio. No auth/account data copied; URLs withheld.')


if __name__ == '__main__':
    main()
