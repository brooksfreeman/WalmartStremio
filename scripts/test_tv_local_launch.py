#!/usr/bin/env python3
"""Test stored launcher -> Netflix while all three PC helpers are stopped.

TV internet and this PC remain on. Uses an independent systemd recovery timer;
no native registry writes, firmware changes, or Home reassignment.
"""
import argparse
import datetime
import ipaddress
from pathlib import Path
import socket
import subprocess
import sys
import time

import tvctl

UNITS=['vizio-stremio-lab.service','vizio-stremio-engine.service','vizio-stremio-watch.service']


def states():
    return subprocess.run(['systemctl','--user','is-active',*UNITS],capture_output=True,text=True).stdout.splitlines()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind',required=True)
    parser.add_argument('--transport',choices=['wamp','rest'],default='wamp')
    args=parser.parse_args()
    bind=str(ipaddress.IPv4Address(args.bind))
    before=states()
    if before!=['active','active','inactive']:
        raise RuntimeError('Lab/engine must be active and watcher paused before test')
    suffix='-rest' if args.transport=='rest' else ''
    build=__import__('json').loads((tvctl.ROOT/('research/reviews/tv-local-launcher'+suffix+'-build.json')).read_text())
    installed=tvctl.read_private('loopback-home-install'+suffix+'.json')
    if installed.get('error') or installed.get('html_sha256')!=build['html_sha256']:
        raise RuntimeError('No verified matching stored launcher; no test sent')
    started=time.time()
    subprocess.run([sys.executable,str(tvctl.ROOT/'scripts/open_native_probe.py'),'--bind',bind,'home-test'+suffix],check=True)
    report_path=tvctl.PRIVATE/('loopback-home-test'+suffix+'.json')
    for _ in range(12):
        if report_path.exists() and report_path.stat().st_mtime>=started:break
        time.sleep(0.5)
    else:raise RuntimeError('Fresh test-loader report missing; helpers left running')
    report=tvctl.read_private(report_path.name)
    if report.get('error') or report.get('html_sha256')!=build['html_sha256'] or not report.get('native_launch_at'):
        raise RuntimeError('Invalid test-loader result; helpers left running')
    launch_at=report['native_launch_at']/1000
    if not 8 < launch_at-time.time() < 20:
        raise RuntimeError('TV/PC clock timing unsuitable; helpers left running')
    unit='vizio-local-native-test-recovery-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')
    subprocess.run(['systemd-run','--user','--quiet','--collect','--unit='+unit,'--on-active=90s','--timer-property=AccuracySec=1s','/usr/bin/systemctl','--user','start',*UNITS],check=True,capture_output=True)
    record={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'PC helpers stopped; PC OS and TV internet remain on','recovery_unit':unit,'launcher_sha256':report['html_sha256'],'native_launch_at':report['native_launch_at'],'phase':'recovery armed','initial_states':before}
    record_name='native-local-launch'+suffix+'-test.json'
    if (tvctl.PRIVATE/record_name).exists():tvctl.save_private(record_name.replace('.json','.previous.json'),tvctl.read_private(record_name))
    tvctl.save_private(record_name,record)
    try:
        subprocess.run(['systemctl','--user','stop',*UNITS],check=True,timeout=12)
        record['paused_states']=states()
        closed={}
        for port in (8099,11470):
            try:
                with socket.create_connection((bind,port),timeout=1):closed[str(port)]=False
            except OSError:closed[str(port)]=True
        record['ports_closed']=closed
        record['isolated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        if record['paused_states']!=['inactive']*3 or not all(closed.values()):raise RuntimeError('Helper isolation failed')
        if time.time()>=launch_at-2:raise RuntimeError('Helpers stopped too late for a valid test')
        record['phase']='helpers isolated before scheduled TV-native launch'
        tvctl.save_private(record_name,record)
        print('All three helpers inactive and both ports closed before TV-native launch.',flush=True)
        while time.time()<launch_at+4:time.sleep(0.5)
        state=tvctl.request('GET','/state_extended')
        app=state.get('APP_CURRENT',{})
        record['observed_after_launch']={k:app.get(k) for k in ('NAME_SPACE','APP_ID')} if isinstance(app,dict) else {'schema_error':True}
        record['observed_input']=state.get('CURRENT_INPUT',{}).get('NAME')
        record['netflix_descriptor_observed']=isinstance(app,dict) and str(app.get('NAME_SPACE'))=='3' and str(app.get('APP_ID'))=='1'
        record['phase']='API Netflix descriptor observed; visual confirmation required' if record['netflix_descriptor_observed'] else 'native launch not verified'
        tvctl.save_private(record_name,record)
        print(record['phase']+': '+str(record['observed_after_launch']),flush=True)
        if record['netflix_descriptor_observed']:
            print('Keeping helpers stopped for another 30 seconds of visual loading time.',flush=True)
            while time.time()<launch_at+34:time.sleep(0.5)
    finally:
        subprocess.run(['systemctl','--user','start',*UNITS],check=True)
        record['restored_states']=states()
        tvctl.save_private(record_name,record)
        if record['restored_states']==['active']*3:
            subprocess.run(['systemctl','--user','stop',unit+'.timer'],check=True)
        print('Restored helpers: '+str(record['restored_states']),flush=True)


if __name__=='__main__':
    try:main()
    except (OSError,RuntimeError,subprocess.SubprocessError) as error:
        print('Stopped:',type(error).__name__,str(error));raise SystemExit(1)
