"""Narrow, reversible Home redirect configuration and HDMI recovery."""
import json
import re
import time

import tvctl


def config():
    path = tvctl.PRIVATE / 'home-navigation.json'
    if not path.exists():
        return {'redirect_home': False, 'return_input': 'HDMI-2'}
    value = tvctl.read_private(path.name)
    if set(value) != {'redirect_home', 'return_input'} or type(value['redirect_home']) is not bool:
        raise RuntimeError('Invalid Home navigation configuration')
    if not isinstance(value['return_input'], str) or not re.fullmatch(r'HDMI-[1-4]', value['return_input']):
        raise RuntimeError('Home recovery input must be an explicit HDMI input')
    return value


def is_stock_home(snapshot):
    app = snapshot.get('app', {})
    return snapshot.get('input') == 'SMARTCAST' and app.get('NAME_SPACE') == 4 and app.get('APP_ID') == '1'


def watchfree_enabled():
    path = tvctl.PRIVATE / 'watchfree-shortcut.json'
    if not path.exists():
        return False
    value = tvctl.read_private(path.name)
    if set(value) != {'enabled'} or type(value['enabled']) is not bool:
        raise RuntimeError('Invalid WatchFree shortcut configuration')
    return value['enabled']


def is_watchfree(snapshot):
    # Replacement W4K65M-1030: owner pressed WatchFree and confirmed its UI.
    # Match the stable observed app, not its transient namespace1/app51 launch.
    app = snapshot.get('app', {})
    return snapshot.get('input') == 'SMARTCAST' and app.get('NAME_SPACE') == 4 and app.get('APP_ID') == '3014'


def suspended():
    path = tvctl.PRIVATE / 'home-redirect-pause.json'
    if not path.exists():
        return False
    until = tvctl.read_private(path.name).get('until', 0)
    if not isinstance(until, (int, float)):
        raise RuntimeError('Invalid Home redirect pause')
    return time.time() < until


def return_to_hdmi():
    target = config()['return_input']
    available = tvctl.request('GET', '/menu_native/dynamic/tv_settings/devices/name_input')
    if target not in [x.get('NAME') for x in available.get('ITEMS', [])]:
        raise RuntimeError('Recovery HDMI input is not in the TV input list')
    initial = tvctl.request('GET', '/menu_native/dynamic/tv_settings/devices/current_input')
    if any(x.get('CNAME') == 'current_input' and str(x.get('ENABLED')).lower() == 'false'
           for x in initial.get('ITEMS', [])):
        raise RuntimeError('TV marks input setting read-only; use physical Input → ' + target)
    # Prevent a redirect during the short Home -> input-switch transition.
    tvctl.save_private('home-redirect-pause.json', {'until': time.time() + 12})
    tvctl.home()
    current = tvctl.request('GET', '/menu_native/dynamic/tv_settings/devices/current_input')
    matches = [x for x in current.get('ITEMS', []) if x.get('CNAME') == 'current_input']
    if len(matches) != 1 or type(matches[0].get('HASHVAL')) is not int:
        raise RuntimeError('Unexpected current input; use physical Input to recover')
    if matches[0].get('VALUE') != target:
        if str(matches[0].get('ENABLED')).lower() == 'false':
            raise RuntimeError('TV marks input setting read-only; use physical Input → ' + target)
        tvctl.request('PUT', '/menu_native/dynamic/tv_settings/devices/current_input', {
            'REQUEST': 'MODIFY', 'VALUE': target, 'HASHVAL': matches[0]['HASHVAL'],
        })
    verify = tvctl.request('GET', '/menu_native/dynamic/tv_settings/devices/current_input')
    if not any(x.get('CNAME') == 'current_input' and x.get('VALUE') == target for x in verify.get('ITEMS', [])):
        raise RuntimeError('HDMI read-back did not match; use physical Input')
