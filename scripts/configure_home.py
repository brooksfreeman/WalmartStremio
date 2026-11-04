#!/usr/bin/env python3
"""Configure reversible PC-side Home behavior; no TV writes or launches."""
import argparse
import json

import home_navigation
import tvctl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'enable', 'enable-stremio', 'enable-watchfree', 'disable-watchfree', 'disable-redirect', 'restore-stremio'])
    args = parser.parse_args()
    navigation = home_navigation.config()
    startup_path = tvctl.PRIVATE / 'startup.json'
    startup = tvctl.read_private(startup_path.name) if startup_path.exists() else {'screen': 'stremio'}
    watchfree = home_navigation.watchfree_enabled()
    if args.action != 'status':
        backup = tvctl.PRIVATE / 'home-behavior-before-configure.json'
        if not backup.exists():
            tvctl.save_private(backup.name, {'navigation': navigation.copy(), 'startup': startup.copy()})
        if args.action != 'disable-watchfree':
            navigation['redirect_home'] = args.action in ('enable', 'enable-stremio')
        watchfree = args.action == 'enable-watchfree'
        if args.action == 'enable':
            startup = {'screen': 'launcher'}
        elif args.action in ('enable-stremio', 'enable-watchfree', 'restore-stremio'):
            startup = {'screen': 'stremio'}
        tvctl.save_private('home-navigation.json', navigation)
        tvctl.save_private('startup.json', startup)
        tvctl.save_private('watchfree-shortcut.json', {'enabled': watchfree})
    print(json.dumps({'navigation': navigation, 'startup': startup, 'watchfree_shortcut': watchfree}, indent=2))


if __name__ == '__main__':
    main()
