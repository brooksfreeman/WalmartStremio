#!/usr/bin/env python3
"""Reproduce two fixed, inert library copies for static inspection only."""
import hashlib
import json
import tarfile

from inspect_vendor_sdk_archives import SOURCE


def main():
    dest=SOURCE/'selected-libraries'
    dest.mkdir(mode=0o700,exist_ok=False)
    selection={
        'libACR/relink_instructions/_vsl_libs/lib/libvsl.so':'libvsl-sdk.so',
        'libACR/relink_instructions/build_libs/vsl/libvsl.so':'libvsl-build.so',
    }
    records=[]
    with tarfile.open(SOURCE/'acr-relink.tar.xz','r|xz') as archive:
        for member in archive:
            if member.name not in selection:
                continue
            if not member.isfile() or member.size>4*1024*1024:
                raise RuntimeError('Unexpected native member')
            data=archive.extractfile(member).read()
            path=dest/selection[member.name]
            path.write_bytes(data)
            path.chmod(0o600)
            records.append({'member':member.name,'saved_as':str(path.relative_to(SOURCE)),
                            'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            if len(records)==len(selection):
                break
    path=dest/'identities.json'
    path.write_text(json.dumps(records,indent=2)+'\n')
    path.chmod(0o600)


if __name__=='__main__':
    main()
