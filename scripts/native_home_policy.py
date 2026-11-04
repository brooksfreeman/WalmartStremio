#!/usr/bin/env python3
"""Bounded Home-provider experiment. Preflight is read-only.

The test command changes only the observed home_provider from vizios-home to
the existing netflix app, then restores it. Owner approval is still required
before invoking test. No firmware, app map, startup setting or files are changed.
"""
import argparse
import datetime
import ipaddress
import secrets
import subprocess
import sys
import time
import urllib.parse

import tvctl


def run_probe(bind, operation):
    nonce=secrets.token_hex(16)
    tvctl.save_private('native-home-policy-permit.json',{
        'operation':operation,'nonce':nonce,'expires':time.time()+25,
    })
    # Dedicated SmartCast activation, then explicit browser launch, independent
    # of the home_provider value being tested. This exact path is preflighted.
    tvctl.request('PUT','/key_command/',{'KEYLIST':[{'CODESET':4,'CODE':3,'ACTION':'KEYPRESS'}]})
    params=urllib.parse.urlencode({'homePolicy':operation,'nonce':nonce})
    tvctl.launch(f'http://{bind}:8099/local-runtime.html?{params}')
    for _ in range(30):
        path=tvctl.PRIVATE/f'native-home-policy-{operation}.json'
        if path.exists():
            result=tvctl.read_private(path.name)
            if result.get('nonce')==nonce and result.get('phase') in ('complete','error'):
                if result['phase']=='error':raise RuntimeError(result.get('error','Probe failed'))
                return result
        time.sleep(0.5)
    raise RuntimeError('Fresh completed Home-provider report missing')


def restore(bind):
    subprocess.run(['systemctl','--user','start','vizio-stremio-lab.service'],check=True)
    result=run_probe(bind,'restore')
    if result.get('current')!='vizios-home':raise RuntimeError('Original Home not verified')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind',required=True)
    parser.add_argument('operation',choices=['preflight','restore','test'])
    parser.add_argument('--owner-approved-native-home-test',action='store_true')
    args=parser.parse_args()
    bind=str(ipaddress.IPv4Address(args.bind))
    if args.operation=='restore':
        restore(bind);print('Original Home provider verified.');return
    if subprocess.run(['systemctl','--user','is-active','--quiet','vizio-stremio-watch.service']).returncode==0:
        raise RuntimeError('Pause Home watcher and arm its separate recovery first')
    if args.operation=='preflight':
        result=run_probe(bind,'preflight')
        tvctl.save_private('native-home-policy-backup.json',{
            'key':'/app/platformorchestrator/appsdatabase/home_provider',
            'original':result['current'],'saved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
        # Exercise the independent rollback transport while baseline is already
        # correct: this branch performs get only, never set.
        restore(bind)
        print('Read-only baseline backed up; independent restore transport verified without writing.');return
    if not args.owner_approved_native_home_test:
        raise RuntimeError('Specific owner approval required; no write sent')
    backup=tvctl.read_private('native-home-policy-backup.json')
    if backup.get('original')!='vizios-home':raise RuntimeError('No matching baseline backup')
    unit='vizio-home-provider-rollback-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')
    subprocess.run(['systemd-run','--user','--quiet','--collect','--unit='+unit,
        '--on-active=75s','--timer-property=AccuracySec=1s',sys.executable,
        str(tvctl.ROOT/'scripts/native_home_policy.py'),'--bind',bind,'restore'],check=True)
    record={'scope':'temporary existing Netflix Home provider; no startup change',
            'rollback_unit':unit,'states':[],'restored':False}
    try:
        record['apply']=run_probe(bind,'apply')
        tvctl.request('PUT','/key_command/',{'KEYLIST':[{'CODESET':4,'CODE':3,'ACTION':'KEYPRESS'}]})
        for _ in range(5):
            time.sleep(2)
            state=tvctl.request('GET','/state_extended')
            record['states'].append({'input':state.get('CURRENT_INPUT',{}).get('NAME'),
                                     'app':state.get('APP_CURRENT')})
    finally:
        try:
            record['restore']=restore(bind);record['restored']=True
            subprocess.run(['systemctl','--user','stop',unit+'.timer'],check=True)
        finally:
            tvctl.save_private('native-home-policy-test.json',record)
    print('Temporary test completed; original provider read back. Visual outcome requires owner feedback.')


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as error:
        print('Stopped:',type(error).__name__,str(error));raise SystemExit(1)
