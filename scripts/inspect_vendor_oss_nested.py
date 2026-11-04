#!/usr/bin/env python3
"""Read inventories and selected inert text from the two referenced OSS archives."""
import argparse
import collections
import hashlib
import json
from pathlib import PurePosixPath
import re
import tarfile
import time

from inspect_vendor_oss import OUT, ROOT, save_json

FILES = {'vizios': 'vizios-gpl.tar.gz', 'firmware': 'firmware-oss.tar.gz'}
RELEVANT = re.compile(r'loki|spock|platformorchestrator|conjure|sysreg|bundleroot|home_provider|deployer|/bundles/', re.I)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('component', choices=FILES)
    component = parser.parse_args().component
    path = OUT / FILES[component]
    identities = json.loads((OUT / 'nested-identities.json').read_text())
    identity = next(item for item in identities if item['saved_as'] == path.name)
    if path.stat().st_size != identity['bytes']:
        raise RuntimeError('Nested archive size changed')
    dest = OUT / (component + '-inventory')
    dest.mkdir(mode=0o700, exist_ok=False)
    components = collections.Counter()
    candidates, captures, nested = [], [], []
    count = captured_bytes = total_bytes = 0
    last_report = time.monotonic()
    index_path = dest / 'members.jsonl'
    with index_path.open('w') as index, tarfile.open(path, 'r|gz') as archive:
        index_path.chmod(0o600)
        for member in archive:
            count += 1
            record = {'name': member.name, 'bytes': member.size, 'type': member.type.decode('ascii', 'replace')}
            index.write(json.dumps(record) + '\n')
            if member.isfile():
                parts = PurePosixPath(member.name).parts
                total_bytes += member.size
                components['/'.join(parts[:2])] += 1
                relevant = bool(RELEVANT.search(member.name))
                if relevant:
                    candidates.append(record)
                if member.name.endswith(('.tar.gz', '.tgz', '.tar.xz', '.tar.bz2', '.zip', '.tar.zst')):
                    nested.append(record)
                doc = len(parts) <= 3 and parts[-1].lower() in {'readme', 'readme.md', 'readme.txt', 'build_gpl_fw.sh', 'build.sh', 'manifest.json', 'manifest.xml'}
                if (relevant or doc) and member.size <= 4*1024*1024 and captured_bytes + member.size <= 64*1024*1024:
                    data = archive.extractfile(member).read()
                    target = dest / (hashlib.sha256(member.name.encode()).hexdigest()[:16] + '.inert')
                    target.write_bytes(data)
                    target.chmod(0o600)
                    captures.append({**record, 'sha256': hashlib.sha256(data).hexdigest(), 'saved_as': target.name})
                    captured_bytes += len(data)
            if count % 4000 == 0:
                archive.members.clear()  # No link resolution or random access used.
            if time.monotonic() - last_report > 20:
                print(f'{component}: {count} members, {total_bytes/1024**3:.1f} GiB declared file bytes', flush=True)
                last_report = time.monotonic()
    result = {'component': component, 'identity': identity,
              'complete_tar_inventory': True, 'members': count,
              'declared_regular_file_bytes': total_bytes, 'components': dict(components),
              'relevant_path_candidates': candidates, 'selected_inert_captures': captures,
              'captured_bytes': captured_bytes, 'nested_archives': nested,
              'limits': ['Filename inventory plus selected small files only; embedded archives not searched.',
                         'Only regular-file bytes copied to flat inert names; no code execution or TV changes.']}
    save_json(dest / 'result.json', result)
    save_json(ROOT / ('research/reviews/vendor-5586l-fur92-' + component + '-inventory.json'), result)
    print(f'{component}: inventory complete: {count} members, {len(candidates)} candidate paths, {len(captures)} captures, {len(nested)} embedded archives.', flush=True)


if __name__ == '__main__':
    main()
