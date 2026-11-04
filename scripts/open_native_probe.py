#!/usr/bin/env python3
"""Activate SmartCast and open one explicitly selected, bounded lab probe.

Pause the PC Home watcher and arm its independent recovery timer first.
Inventory/bindings/control modes read only. File write/cleanup affect only our
explicit disposable browser-sandbox directory. No native setting is written.
"""
import argparse
import ipaddress
import subprocess
import time

import tvctl

MODES = {
    'inventory':'loopbackRedirect=1',
    'bindings':'loopbackBindings=1',
    'control-read':'loopbackControl=1',
    'registry-root':'loopbackRegistry=empty',
    'registry-slash':'loopbackRegistry=slash',
    'registry-branches':'loopbackRegistry=branches',
    'registry-policy':'loopbackRegistry=policy',
    'registry-manager':'loopbackRegistry=manager',
    'registry-providers':'loopbackRegistry=providers',
    'registry-database':'loopbackRegistry=database',
    'registry-status':'loopbackRegistry=status',
    'registry-loki':'loopbackRegistry=loki',
    'registry-debug-names':'loopbackRegistry=debug-names',
    'registry-home-routing':'loopbackRegistry=home-routing',
    'registry-manager-state':'loopbackRegistry=manager-state',
    'registry-home-resources':'loopbackRegistry=home-resources',
    'registry-home-catalog':'loopbackRegistry=home-catalog',
    'registry-osu-identity':'loopbackRegistry=osu-identity',
    'registry-osu-storage':'loopbackRegistry=osu-storage',
    'registry-osu-dlm':'loopbackRegistry=osu-dlm',
    'registry-osu-log-status':'loopbackRegistry=osu-log-status',
    'file-write':'loopbackFile=write',
    'file-open':'loopbackFile=open',
    'file-stored':'loopbackStored=1',
    'file-cleanup':'loopbackFile=cleanup',
    'home-install':'localHome=install',
    'home-open':'localHome=open',
    'home-test':'localHome=test',
    'home-cleanup':'localHome=cleanup',
    'home-direct':None,
    'home-install-rest':'localHome=install-rest',
    'home-open-rest':'localHome=open-rest',
    'home-test-rest':'localHome=test-rest',
    'home-cleanup-rest':'localHome=cleanup-rest',
    'wamp-meta':'wampMeta=1',
}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind',required=True)
    parser.add_argument('mode',choices=MODES)
    args=parser.parse_args()
    bind=str(ipaddress.IPv4Address(args.bind))
    if subprocess.run(['systemctl','--user','is-active','--quiet','vizio-stremio-watch.service']).returncode == 0:
        raise RuntimeError('Pause watcher and arm its independent recovery timer before a diagnostic')
    tvctl.request('PUT','/key_command/',{'KEYLIST':[{'CODESET':4,'CODE':3,'ACTION':'KEYPRESS'}]})
    state=tvctl.request('GET','/state_extended')
    for _ in range(8):
        if state.get('CURRENT_INPUT',{}).get('NAME')=='SMARTCAST':break
        time.sleep(0.2)
        state=tvctl.request('GET','/state_extended')
    if state.get('CURRENT_INPUT',{}).get('NAME')!='SMARTCAST':
        raise RuntimeError('SmartCast input not active; no launch sent')
    result=tvctl.launch_stored_launcher() if args.mode=='home-direct' else tvctl.launch(f'http://{bind}:8099/local-runtime.html?{MODES[args.mode]}')
    print(args.mode+': '+result['STATUS']['RESULT']+' (request accepted; verify fresh report)')


if __name__=='__main__':
    try:
        main()
    except (OSError,ValueError,RuntimeError) as error:
        print('Stopped:',type(error).__name__,str(error))
        raise SystemExit(1)
