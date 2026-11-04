#!/usr/bin/env python3
"""Build a self-contained browser-sandbox launcher with direct TV app control."""
import argparse
import hashlib
import ipaddress
import json
from pathlib import Path

import tvctl
from launcher_apps import NATIVE_APPS


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind',required=True,help='Existing PC Stremio host; native app tiles do not use it')
    parser.add_argument('--transport',choices=['wamp','rest'],default='wamp')
    args=parser.parse_args()
    bind=str(ipaddress.IPv4Address(args.bind))
    web=tvctl.ROOT/'web'
    script=(web/'launcher.js').read_text()
    start=script.index('const dependencyTest =')
    end=script.index('function clock()',start)
    script=script[:start]+script[end:]
    start=script.index('async function openApp(button)')
    end=script.index('[...tiles, tv].forEach',start)
    function='''async function openApp(button) {
  if(busy)return;
  if(button===tv){status.textContent='Press Input, then HDMI-2 to return to the PC.';return;}
  if(button.dataset.app==='stremio'){
    status.textContent='Stremio currently needs the Linux PC.';
    location.assign(__STREMIO_URL__);return;
  }
  const descriptor=nativeApps[button.dataset.app];
  if(!descriptor)return;
  busy=true;status.textContent='Opening '+button.querySelector('span:last-child').textContent+'…';
  try {
    if(typeof navigator.vizio?.createAppLaunchConnection!=='function')throw new Error('Native bridge unavailable');
    nativeClient=nativeClient||navigator.vizio.createAppLaunchConnection();
    const client=await nativeClient;
    await client.appLaunch(descriptor.APP_ID,descriptor.NAME_SPACE,descriptor.MESSAGE);
    status.textContent='Launch requested directly from the TV.';
  } catch(_){nativeClient=null;status.textContent='App launch failed. Input → HDMI-2 returns to the PC.';}
  finally{busy=false;}
}
'''.replace('__STREMIO_URL__',json.dumps(f'http://{bind}:8099/stremio/#/'))
    script=script[:start]+function+script[end:]
    if args.transport=='rest':
        old='''    if(typeof navigator.vizio?.createAppLaunchConnection!=='function')throw new Error('Native bridge unavailable');
    nativeClient=nativeClient||navigator.vizio.createAppLaunchConnection();
    const client=await nativeClient;
    await client.appLaunch(descriptor.APP_ID,descriptor.NAME_SPACE,descriptor.MESSAGE);'''
        new='''    const bootstrap=await fetch('http://127.0.0.1:7346/app/get_auth_token',{signal:AbortSignal.timeout(5000)});
    const auth=await bootstrap.json();
    const token=auth?.ITEM?.VALUE;
    if(typeof token!=='string'||!token)throw new Error('Local session unavailable');
    const response=await fetch('http://127.0.0.1:7346/app/launch',{
      method:'PUT',headers:{AUTH:token,'Content-Type':'application/json'},
      body:JSON.stringify({VALUE:descriptor}),signal:AbortSignal.timeout(8000),
    });
    if(!response.ok)throw new Error('Local app launch rejected');'''
        assert old in script
        script=script.replace(old,new)
    script=script.replace('// Local assets only. No analytics, storage, telemetry, or third-party requests.', '// Self-contained saved TV page. Native app tiles use only the local WAMP bridge.\nconst nativeApps='+json.dumps(NATIVE_APPS,separators=(',',':'))+';\nlet nativeClient=null;')
    script+="\nstatus.textContent='Saved on TV · Home shortcut pending · Stremio needs Linux';\n"
    script+='''
if(Number.isFinite(window.__ownerNativeLaunchAt)){
  const at=window.__ownerNativeLaunchAt;delete window.__ownerNativeLaunchAt;
  status.textContent='Testing direct TV launch of Netflix in 15 seconds…';
  setTimeout(()=>openApp(tiles.find(button=>button.dataset.app==='netflix')),Math.max(0,at-Date.now()));
}
'''
    html=(web/'launcher.html').read_text()
    connection='http://127.0.0.1:7346' if args.transport=='rest' else 'ws://127.0.0.1:55555'
    policy="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src "+connection+"; base-uri 'none'; form-action 'none'"
    html=html.replace('<link rel="stylesheet" href="/launcher.css">','<meta http-equiv="Content-Security-Policy" content="'+policy+'"><style>'+(web/'launcher.css').read_text()+'</style>')
    html=html.replace('<script src="/launcher.js" defer></script>','')
    html=html.replace('</body>','<script>'+script+'</script></body>')
    suffix='-rest' if args.transport=='rest' else ''
    (web/('tv-local-launcher'+suffix+'.html')).write_text(html)
    result={'date':'2026-11-01','model':'W4K65M-1031','html_sha256':hashlib.sha256(html.encode()).hexdigest(),'bytes':len(html.encode()),'transport':args.transport,'native_app_tiles':'TV-local '+args.transport+'; no PC helper; REST credential stays only in TV memory','stremio':'Existing Linux-hosted app and engine remain required','storage_target':'Chromium PERSISTENT/owner-tv-home'+suffix+'-v1/index.html','home_replaced':False,'cold_start_verified':False,'owner_test':'pending'}
    (tvctl.ROOT/('research/reviews/tv-local-launcher'+suffix+'-build.json')).write_text(json.dumps(result,indent=2)+'\n')
    print('Built self-contained TV launcher:',result['bytes'],'bytes; SHA256',result['html_sha256'])


if __name__=='__main__':
    main()
