#!/usr/bin/env python3
"""Test an explicit local UKF Qterics collection against an owned UTV offline.

Format reference: theubusu/unixtract at aadba866ea47ed9506ffe130a8558bb9147ee968,
src/formats/utv_qterics/mod.rs (GPL-3.0). This Python implementation uses the
existing cryptography library, not the upstream executable. No private key bytes,
unwrapped secrets or decrypted content are included in the report. No TV access.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import struct

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def collection_entries(text):
    # UKF strings have literal backslash-n sequences; its lexer does not implement
    # escaped quotation marks. Limit parsing to this one named collection.
    start = re.search(r'collection\s+"UTV_QTERICS"\s*:\s*\{', text)
    if not start:
        raise ValueError('Missing UTV_QTERICS collection')
    depth = 1
    end = None
    for match in re.finditer(r'"[^"]*"|[{}]', text[start.end():]):
        if match.group() == '{':
            depth += 1
        elif match.group() == '}':
            depth -= 1
            if depth == 0:
                end = start.end() + match.start()
                break
    if end is None:
        raise ValueError('Unterminated collection')
    body = re.sub(r'(?m)^\s*#.*$', '', text[start.end():end])
    pattern = r'"([^"]*)"\s*:\s*\{\s*"([^"]*)"\s*\}\s*,?'
    entries = re.findall(pattern, body)
    if re.sub(pattern, '', body).strip() or not entries:
        raise ValueError('Unsupported collection syntax; refusing partial parsing')
    if len(entries) > 128:
        raise ValueError('Collection exceeds this bounded trial')
    return entries


def inspect(path, keyfile):
    if keyfile.stat().st_size > 1024 * 1024:
        raise ValueError('Keyfile exceeds 1MiB bound')
    raw_keys = keyfile.read_bytes()
    entries = collection_entries(raw_keys.decode('utf-8'))
    artifact_digest = hashlib.sha256()
    with path.open('rb') as stream:
        prefix = stream.read(4)
        if len(prefix) != 4:
            raise ValueError('Missing UTV length')
        size = struct.unpack('>I', prefix)[0]
        if not 1 <= size <= min(1024 * 1024, path.stat().st_size - 4):
            raise ValueError('UTV header length out of bounds')
        token = stream.read(size)
        parts = token.split(b'.')
        if len(parts) != 3:
            raise ValueError('Invalid JWT structure')
        segment = parts[1]
        claims = json.loads(base64.b64decode(segment + b'=' * (-len(segment) % 4),
                                           altchars=b'-_', validate=True))
        block = claims['blk']
        declared_size = claims['siz']
        if not isinstance(block, int) or not 1 <= block <= 8 * 1024 * 1024:
            raise ValueError('Block size out of bounds')
        if not isinstance(declared_size, int) or declared_size <= 0:
            raise ValueError('Invalid declared size')
        block_count = (declared_size + block - 1) // block
        if path.stat().st_size != 4 + size + declared_size + 16 * block_count:
            raise ValueError('File does not match the reference tag layout')
        first = stream.read(min(block, declared_size) + 16)
        artifact_digest.update(prefix + token + first)
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            artifact_digest.update(part)
    wrapped = base64.b64decode(claims['key'], validate=True)
    rows = []
    for name, pem in entries:
        key = serialization.load_pem_private_key(pem.replace('\\n', '\n').encode(), None)
        if not isinstance(key, rsa.RSAPrivateKey):
            raise ValueError('Collection contains non-RSA private key')
        public = key.public_key().public_bytes(serialization.Encoding.DER,
                                              serialization.PublicFormat.SubjectPublicKeyInfo)
        row = {'name': name, 'public_key_sha256': hashlib.sha256(public).hexdigest()}
        try:
            secret = key.decrypt(wrapped, padding.OAEP(
                mgf=padding.MGF1(hashes.SHA1()), algorithm=hashes.SHA1(), label=None))
        except ValueError:
            row['unwrap'] = 'no-match'
            rows.append(row)
            continue
        row.update({'unwrap': 'success', 'unwrapped_bytes': len(secret)})
        if len(secret) == 44:
            nonce = bytes(4) + secret[36:44]
            try:
                plain = AESGCM(secret[:16]).decrypt(nonce, first, secret[16:32])
                row.update({'first_block_gcm': 'valid', 'plaintext_bytes': len(plain),
                            'plaintext_sha256': hashlib.sha256(plain).hexdigest()})
            except InvalidTag:
                row['first_block_gcm'] = 'invalid-tag'
        rows.append(row)
    return {
        'source': 'https://github.com/theubusu/unixtract',
        'reference_commit': 'aadba866ea47ed9506ffe130a8558bb9147ee968',
        'artifact_sha256': artifact_digest.hexdigest(),
        'keyfile_sha256': hashlib.sha256(raw_keys).hexdigest(),
        'tested_entries': len(rows),
        'unique_public_keys': len({r['public_key_sha256'] for r in rows}),
        'algorithm': 'RSA-OAEP(SHA1,MGF1-SHA1),44-byte secret,AES128-GCM,16-byte tag per chunk',
        'scope': 'Explicit published collection only; no brute force, TV access or extracted output',
        'results': rows,
        'limitations': [
            'Caller must verify signed metadata independently; this trial does not authenticate provenance.',
            'No match is limited to this exact key collection and reference algorithm.',
            'A first-block GCM success would not establish all blocks or whole plaintext digest.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('firmware', type=Path)
    parser.add_argument('--keyfile', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.firmware.resolve(strict=True), args.keyfile.resolve(strict=True))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'tested': result['tested_entries'],
                      'unique_public_keys': result['unique_public_keys'],
                      'unwrap_matches': sum(r['unwrap'] == 'success' for r in result['results']),
                      'report': str(args.output)}))


if __name__ == '__main__':
    main()
