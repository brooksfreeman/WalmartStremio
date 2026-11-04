#!/usr/bin/env python3
"""Copy only reviewed OSS source prefixes as non-executable local files.

No archive link is followed and no member-provided permissions are applied.
Existing output is never overwritten. This does not extract or install firmware.
"""
import hashlib
import json
from pathlib import PurePosixPath
import tarfile

from inspect_vendor_oss import OUT


def main():
    dest = OUT / 'selected-source'
    dest.mkdir(mode=0o700, exist_ok=False)
    prefixes = ('rootfs/OSUpdater/', 'rootfs/eris/', 'rootfs/inspector/', 'rootfs/reader/')
    exact = {'README.md', 'rootfs/snap/snapcraft.yaml', 'sysroot/snap/snapcraft.yaml', 'storaged/snap/snapcraft.yaml'}
    records = []
    total = 0
    with tarfile.open(OUT / 'vizios-gpl.tar.gz', 'r|gz') as archive:
        for member in archive:
            parts = PurePosixPath(member.name).parts
            normalized = '/'.join(parts)
            if not member.isfile() or '.git' in parts or '..' in parts or PurePosixPath(member.name).is_absolute():
                continue
            if normalized not in exact and not normalized.startswith(prefixes):
                continue
            if member.size > 4*1024*1024 or total + member.size > 64*1024*1024:
                raise RuntimeError('Selected-source cap reached; stopped')
            path = dest.joinpath(*parts)
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            data = archive.extractfile(member).read()
            path.write_bytes(data)
            path.chmod(0o600)
            total += len(data)
            records.append({'member': member.name, 'saved_as': str(path.relative_to(OUT)),
                            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    target = OUT / 'selected-source-identities.json'
    target.write_text(json.dumps(records, indent=2) + '\n')
    target.chmod(0o600)
    print(f'Selected source: {len(records)} inert files, {total} bytes.')


if __name__ == '__main__':
    main()
