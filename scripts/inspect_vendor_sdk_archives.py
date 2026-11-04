#!/usr/bin/env python3
"""Inventory previously uninspected vendor compiler/relink archives, inertly.

Scope: four explicit members of the already verified manufacturer archive.
No archive path extraction, link following, compilation, code execution, or TV I/O.
"""
import argparse
import collections
import hashlib
import json
from pathlib import PurePosixPath
import re
import tarfile
import time

from inspect_vendor_oss import ARCHIVE, OUT, ROOT, save_json

TARGETS = {
    '5586L_FUR9.2/tools/vizio_toolchain-2.50-50af9fb.tar.gz': 'sdk250',
    '5586L_FUR9.2/FANCYPLAYER/conan/packages/bin/vizio_toolchain.tar.gz': 'sdk-fancy',
    '5586L_FUR9.2/ES-PLAYER/toolchain/vizio_toolchain-1.32-L-f98fda7.tar.xz': 'sdk132l',
    '5586L_FUR9.2/ACR/libACR.tar.xz': 'acr-relink',
}
SOURCE = OUT / 'sdk-archives'
PATTERN = re.compile(r'loki|platformorchestrator|sysreg_wrap|vizio[-_]ipc|bundleroot|vizios-home|^libipc[.]', re.I)


def copy_archives():
    identity = json.loads((ROOT/'research/reviews/vendor-5586l-fur92-archive-identity.json').read_text())
    if not identity['published_checksums_match'] or ARCHIVE.stat().st_size != identity['bytes']:
        raise RuntimeError('Verified original archive required')
    SOURCE.mkdir(mode=0o700, exist_ok=False)
    results = []
    with tarfile.open(ARCHIVE, 'r|gz') as archive:
        for member in archive:
            if member.name not in TARGETS:
                continue
            if not member.isfile():
                raise RuntimeError('Expected regular archive member')
            suffix = '.tar.xz' if member.name.endswith('.xz') else '.tar.gz'
            dest = SOURCE/(TARGETS[member.name]+suffix)
            digest = hashlib.sha256()
            size = 0
            with archive.extractfile(member) as src, dest.open('xb') as output:
                dest.chmod(0o600)
                while block := src.read(16*1024*1024):
                    output.write(block)
                    digest.update(block)
                    size += len(block)
            if size != member.size:
                raise RuntimeError('Member size mismatch')
            results.append({'member':member.name, 'component':TARGETS[member.name],
                            'saved_as':dest.name, 'bytes':size, 'sha256':digest.hexdigest()})
            print(f'Copied inert {dest.name}: {size} bytes', flush=True)
            if len(results) == len(TARGETS):
                break
    if len(results) != len(TARGETS):
        raise RuntimeError('Missing explicit target member')
    save_json(SOURCE/'identities.json', results)
    return results


def inspect(identity):
    component = identity['component']
    path = SOURCE/identity['saved_as']
    dest = SOURCE/(component+'-inventory')
    if dest.exists():
        entries=list(dest.iterdir())
        if len(entries)!=1 or entries[0].name!='members.jsonl' or entries[0].stat().st_size:
            raise RuntimeError('Existing inventory output; refusing overwrite')
    else:
        dest.mkdir(mode=0o700, exist_ok=False)
    with path.open('rb') as stream:
        magic=stream.read(6)
    mode = 'r|xz' if magic==b'\xfd7zXZ\x00' else 'r|gz' if magic[:2]==b'\x1f\x8b' else 'r|'
    print(f'{component}: detected archive mode {mode}',flush=True)
    count = captured_bytes = 0
    prefixes = collections.Counter()
    candidates, captures = [], []
    last_report = time.monotonic()
    index_path = dest/'members.jsonl'
    with index_path.open('w') as index, tarfile.open(path, mode) as archive:
        index_path.chmod(0o600)
        for member in archive:
            count += 1
            record = {'name':member.name, 'bytes':member.size, 'type':member.type.decode('ascii','replace')}
            index.write(json.dumps(record)+'\n')
            if member.isfile():
                parts = PurePosixPath(member.name).parts
                prefixes['/'.join(parts[:2])] += 1
                relevant = bool(PATTERN.search(parts[-1])) or '/bundles/home/' in member.name.lower()
                relevant |= '/include/vizio/' in member.name.lower()
                if relevant:
                    candidates.append(record)
                doc = len(parts)<=3 and parts[-1].lower() in {'readme','readme.md','readme.txt','manifest.json'}
                if (relevant or doc) and member.size<=2*1024*1024 and captured_bytes+member.size<=16*1024*1024:
                    data = archive.extractfile(member).read()
                    target = dest/(hashlib.sha256(member.name.encode()).hexdigest()[:16]+'.inert')
                    target.write_bytes(data)
                    target.chmod(0o600)
                    captures.append({**record,'saved_as':target.name,'sha256':hashlib.sha256(data).hexdigest()})
                    captured_bytes += len(data)
            if count%4000 == 0:
                archive.members.clear()
            if time.monotonic()-last_report>20:
                print(f'{component}: {count} members inventoried', flush=True)
                last_report=time.monotonic()
    result = {'component':component,'identity':identity,'complete_tar_inventory':True,
              'compression_mode':mode,'members':count,'prefixes':dict(prefixes),'candidate_paths':candidates,
              'inert_captures':captures,'captured_bytes':captured_bytes,
              'limits':['Filename inventory and selected small files only; no generic binary symbol scan.',
                        'Other embedded archives not recursively expanded; header names do not prove runtime availability.',
                        'No file paths extracted or links followed; no scripts or code executed; no TV operations.']}
    save_json(dest/'result.json',result)
    save_json(ROOT/f'research/reviews/vendor-sdk-{component}-inventory.json',result)
    print(f'{component}: complete, {count} members, {len(candidates)} candidate paths.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scan',choices=list(TARGETS.values()))
    args=parser.parse_args()
    if args.scan:
        items=json.loads((SOURCE/'identities.json').read_text())
        items=[item for item in items if item['component']==args.scan]
    else:
        items=copy_archives()
    for item in items:
        inspect(item)
