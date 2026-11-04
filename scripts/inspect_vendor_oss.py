#!/usr/bin/env python3
"""Inventory the verified owner-provided OSS tarball without extracting paths.

Read selected small documentation and relevant candidate files into flat,
hash-named inert files. Never follow archive links, execute scripts or build code.
The compressed archive identity must already match the manufacturer's checksums.
"""
import collections
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / '5586L_FUR9.2.tar.gz'
OUT = ROOT / '.private/vendor-oss-5586l-fur92'
REVIEW = ROOT / 'research/reviews/vendor-5586l-fur92-inventory.json'
RELEVANT = re.compile(r'(^|/)(loki[^/]*|spock[^/]*|conjure[^/]*|platformorchestrator[^/]*|bundles|BundleRoot\.xml|home_provider)(/|$)', re.I)
DOC_NAMES = {'readme', 'readme.md', 'readme.txt', 'build.sh', 'manifest.json', 'manifest.xml'}


def save_json(path, value):
    with path.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
    path.chmod(0o600)


def main():
    identity = json.loads((ROOT / 'research/reviews/vendor-5586l-fur92-archive-identity.json').read_text())
    if not identity.get('published_checksums_match') or ARCHIVE.stat().st_size != identity['bytes']:
        raise RuntimeError('A matching, checksum-verified archive is required')
    OUT.mkdir(mode=0o700, exist_ok=False)
    os.chmod(OUT, 0o700)
    count = 0
    declared_bytes = 0
    captured_bytes = 0
    components = collections.Counter()
    candidates = []
    captured = []
    nested = []
    last_report = time.monotonic()
    inventory = OUT / 'members.jsonl'
    with inventory.open('w') as index, tarfile.open(ARCHIVE, mode='r|gz') as archive:
        inventory.chmod(0o600)
        for member in archive:
            count += 1
            parts = PurePosixPath(member.name).parts
            record = {'name': member.name, 'size': member.size, 'type': member.type.decode('ascii', 'replace')}
            index.write(json.dumps(record) + '\n')
            if member.isfile():
                declared_bytes += member.size
                component = '/'.join(parts[:2])
                components[component] += 1
                relevant = bool(RELEVANT.search(member.name))
                if relevant:
                    candidates.append(record)
                if member.name.endswith(('.tar.gz', '.tgz', '.tar.xz', '.tar.bz2', '.zip', '.tar.zst')):
                    nested.append(record)
                small_doc = len(parts) <= 3 and parts[-1].lower() in DOC_NAMES
                if (relevant or small_doc) and member.size <= 4*1024*1024 and captured_bytes + member.size <= 64*1024*1024:
                    data = archive.extractfile(member).read()
                    digest = hashlib.sha256(data).hexdigest()
                    target = OUT / (hashlib.sha256(member.name.encode()).hexdigest()[:16] + '.inert')
                    target.write_bytes(data)
                    target.chmod(0o600)
                    captured.append({**record, 'sha256': digest, 'saved_as': target.name})
                    captured_bytes += len(data)
            if time.monotonic() - last_report > 20:
                print(f'Inventoried {count} members; {declared_bytes/1024**3:.1f} GiB declared file bytes', flush=True)
                last_report = time.monotonic()
    result = {
        'archive': ARCHIVE.name, 'archive_sha256': identity['digests']['sha256'],
        'complete_tar_inventory': True, 'members': count, 'declared_regular_file_bytes': declared_bytes,
        'components': dict(components), 'relevant_path_candidates': candidates,
        'nested_archives': nested, 'selected_inert_captures': captured,
        'captured_bytes': captured_bytes,
        'limits': ['Filename inventory is not a source-content search or proof of completeness of vendor release.',
                   'Nested archives have not been inspected.',
                   'No archive paths extracted; no script execution, build, installation or TV operations.'],
    }
    save_json(OUT / 'inventory-result.json', result)
    save_json(REVIEW, result)
    print(f'Inventory complete: {count} members; {len(candidates)} relevant path candidates; {len(nested)} nested archives; {len(captured)} inert captures.', flush=True)


if __name__ == '__main__':
    main()
