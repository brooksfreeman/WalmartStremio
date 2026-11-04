#!/usr/bin/env python3
"""Save source/docs plus a private evidence manifest, without exporting secrets.

Private evidence stays in place; its hashes let a later session verify identity.
This is not a full machine backup or a TV firmware/recovery image.
"""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    result=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            result.update(chunk)
    return result.hexdigest()


def main():
    dest=ROOT/'.private/checkpoints'
    dest.mkdir(mode=0o700,exist_ok=True)
    dest.chmod(0o700)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    files=[]
    for name in ['.gitignore','README.md','client','config','docs','scripts','tests','web','research/reviews']:
        path=ROOT/name
        for item in [path] if path.is_file() else path.rglob('*'):
            if item.is_file() and not item.is_symlink() and '__pycache__' not in item.parts and 'node_modules' not in item.parts:
                files.append(item)
    credentials=ROOT/'.private/credentials.json'
    secret=json.loads(credentials.read_text())['auth_token'].encode() if credentials.exists() else None
    if secret and any(secret in path.read_bytes() for path in files):
        raise RuntimeError('Paired credential found in source selection; checkpoint stopped')
    archive=dest/('source-checkpoint-'+stamp+'.tar.gz')
    with tarfile.open(archive,'w:gz') as output:
        for path in files:
            output.add(path,arcname=str(path.relative_to(ROOT)),recursive=False)
    archive.chmod(0o600)
    selected=[ROOT/'.private/vendor-localassets.enc',ROOT/'.private/rea-native-checkpoint-evidence.json',
              ROOT/'.private/server-power-before.json', ROOT/'.private/watchfree-shortcut.json',
              ROOT/'.private/home-navigation.json', ROOT/'.private/startup.json',
              ROOT/'.private/addon-manager-state.json', ROOT/'.private/addon-manager-result.json',
              ROOT/'mg1352-86.910.19.2-1F.utv',ROOT/'.private/rea-utv-inspection-evidence.json']
    for name in ['owner-tv-static','owner-actual-home','owner-native-launcher','owner-runtime-bindings','hardware-identification','utv-mg1352','unixtract']:
        selected.extend(path for path in (ROOT/'.private'/name).rglob('*') if path.is_file())
    selected.extend((ROOT/'.private').glob('loopback-*.json'))
    selected.extend((ROOT/'.private').glob('native-home-policy-*.json'))
    selected.extend((ROOT/'.private/addon-manager-backups').glob('*.json'))
    oss=ROOT/'.private/vendor-oss-5586l-fur92'
    for name in ['nested-identities.json','selected-source-identities.json','inventory-result.json','members.jsonl','vizios-inventory/result.json','vizios-inventory/members.jsonl','firmware-inventory/result.json','firmware-inventory/members.jsonl']:
        selected.append(oss/name)
    selected.append(ROOT/'.private/rea-sdk-interface-evidence.json')
    sdk=oss/'sdk-archives'
    selected.append(sdk/'identities.json')
    selected.append(sdk/'selected-libraries/identities.json')
    for component in ['acr-relink','sdk250','sdk-fancy','sdk132l']:
        selected.extend([sdk/(component+'-inventory/result.json'),sdk/(component+'-inventory/members.jsonl')])
    state=subprocess.run(['systemctl','--user','is-active','vizio-stremio-lab.service','vizio-stremio-engine.service','vizio-stremio-watch.service'],capture_output=True,text=True)
    manifest={
        'checkpoint_utc':stamp,'source_archive':archive.name,
        'source_archive_sha256':digest(archive),'source_files':len(files),
        'secrets_scan':'Paired AUTH token absent; credentials and raw private configuration excluded from archive.',
        'private_artifacts_remain_in_project':[{'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':digest(path)} for path in selected if path.exists()],
        'service_state_lab_engine_watch':state.stdout.splitlines(),
        'resume':'docs/RESUME-HERE.md',
        'note':'Local source snapshot and private evidence hashes. No upload, git commit, full machine backup or TV firmware backup.',
    }
    path=dest/('checkpoint-'+stamp+'.json')
    path.write_text(json.dumps(manifest,indent=2)+'\n');path.chmod(0o600)
    latest=dest/'latest.json'
    latest.write_text(json.dumps({'manifest':path.name,'source_archive':archive.name},indent=2)+'\n');latest.chmod(0o600)
    print('Saved',archive.name,'with',len(files),'source/doc files; private evidence retained separately.')


if __name__=='__main__':
    main()
