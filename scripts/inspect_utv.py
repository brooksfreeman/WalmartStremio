#!/usr/bin/env python3
"""Inspect an explicitly supplied UTV file offline; never install or execute it.

Requires the already-installed cryptography package. Embedded certificates can
verify internal consistency; they do not supply an independently trusted root.
No commands, URLs, certificate revocation URLs or paths from claims are followed.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import struct

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def decode_url(part):
    return base64.b64decode(part + b'=' * (-len(part) % 4),
                            altchars=b'-_', validate=True)


def verify_signature(key, signature, message, algorithm):
    if not isinstance(key, rsa.RSAPublicKey):
        return 'unsupported-non-RSA-key'
    try:
        key.verify(signature, message, padding.PKCS1v15(), algorithm)
        return 'valid'
    except InvalidSignature:
        return 'invalid'


def cert_summary(cert):
    return {
        'subject': cert.subject.rfc4514_string(),
        'issuer': cert.issuer.rfc4514_string(),
        'sha256': cert.fingerprint(hashes.SHA256()).hex(),
        'public_key_bits': cert.public_key().key_size,
        'not_before_utc': cert.not_valid_before.isoformat() + 'Z',
        'not_after_utc': cert.not_valid_after.isoformat() + 'Z',
    }


def inspect(path, installed_version=None):
    path = path.resolve(strict=True)
    if not path.is_file():
        raise ValueError('Input must be a regular file')
    size = path.stat().st_size
    with path.open('rb') as stream:
        prefix = stream.read(4)
        if len(prefix) != 4:
            raise ValueError('Missing length prefix')
        jwt_size = struct.unpack('>I', prefix)[0]
        if not 1 <= jwt_size <= min(1024 * 1024, size - 4):
            raise ValueError('JWT length is out of bounds')
        token = stream.read(jwt_size)
        parts = token.split(b'.')
        if len(parts) != 3:
            raise ValueError('Expected three JWT segments')
        header = json.loads(decode_url(parts[0]))
        claims = json.loads(decode_url(parts[1]))
        if not isinstance(header, dict) or not isinstance(claims, dict):
            raise ValueError('JWT header and claims must be objects')
        total_digest = hashlib.sha256(prefix + token)
        payload_digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            total_digest.update(block)
            payload_digest.update(block)

    leaf = x509.load_pem_x509_certificate(
        claims['crt'].replace('\\n', '\n').encode('ascii'))
    intermediate = x509.load_pem_x509_certificate(
        claims['int'].replace('\\n', '\n').encode('ascii'))
    jwt_signature = 'not-checked-unsupported-algorithm'
    if header.get('alg') == 'RS512':
        jwt_signature = verify_signature(leaf.public_key(), decode_url(parts[2]),
                                        parts[0] + b'.' + parts[1], hashes.SHA512())
    leaf_signature = verify_signature(intermediate.public_key(), leaf.signature,
                                     leaf.tbs_certificate_bytes,
                                     leaf.signature_hash_algorithm)
    payload_bytes = size - 4 - jwt_size
    layout = {'payload_offset': 4 + jwt_size, 'payload_bytes': payload_bytes}
    declared = claims.get('siz')
    chunk = claims.get('blk')
    if isinstance(declared, int) and declared > 0 and isinstance(chunk, int) and chunk > 0:
        full, tail = divmod(declared, chunk)
        count = full + bool(tail)
        layout.update({
            'declared_size': declared, 'declared_block_size': chunk,
            'full_declared_blocks': full, 'declared_tail_bytes': tail,
            'declared_block_count_including_tail': count,
            'payload_minus_declared_size': payload_bytes - declared,
            'difference_per_declared_block_if_uniform':
                (payload_bytes - declared) / count,
            'interpretation': 'Arithmetic only; no chunk-header, AES mode or padding semantics verified.',
        })
    audience = claims.get('aud')
    selected = {name: claims.get(name) for name in
                ['sub', 'opd', 'siz', 'blk', 'upf', 'upi', 'aud', 'aas', 'upn', 'man', 'hsh']}
    return {
        'artifact': {'path': str(path), 'bytes': size,
                     'sha256': total_digest.hexdigest()},
        'jwt': {'length': jwt_size, 'algorithm': header.get('alg'),
                'claim_names': sorted(claims), 'selected_claims': selected,
                'url_present': bool(claims.get('url')),
                'key_field_decoded_bytes': len(base64.b64decode(claims['key'], validate=True)),
                'signature_with_embedded_leaf': jwt_signature},
        'certificates': {'leaf': cert_summary(leaf), 'intermediate': cert_summary(intermediate),
                         'leaf_signature_with_embedded_intermediate': leaf_signature,
                         'issuer_subject_match': leaf.issuer == intermediate.subject,
                         'independent_root_trust': 'not-established'},
        'layout': layout,
        'payload': {'sha256': payload_digest.hexdigest(),
                    'hash_matches_claim_hsh': payload_digest.hexdigest().lower() ==
                        str(claims.get('hsh', '')).lower(),
                    'plaintext_recovered': False,
                    'plaintext_digest_verified': False},
        'installed_version_comparison': {
            'installed_version': installed_version,
            'exact_audience_member': installed_version in audience
                if installed_version is not None and isinstance(audience, list) else None,
            'limitation': 'Audience comparison alone does not establish full device update policy or model compatibility.',
        },
        'effects': {'network_requests': False, 'tv_operations': False,
                    'target_execution': False, 'decryption': False, 'flashing': False},
        'limitations': [
            'Signed metadata is not proof that opaque payload bytes satisfy the plaintext digest.',
            'Embedded certificate consistency is not independently authenticated download provenance.',
            'RSA-wrapped-key/AES interpretation comes from external research, not recovered cipher implementation.',
            'Neither current-version status nor exact owner-model compatibility established by this file.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    parser.add_argument('--installed-version')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.path, args.installed_version)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'report': str(output), 'sha256': result['artifact']['sha256'],
                      'jwt_signature': result['jwt']['signature_with_embedded_leaf'],
                      'leaf_signature': result['certificates']['leaf_signature_with_embedded_intermediate'],
                      'plaintext_recovered': False}))


if __name__ == '__main__':
    main()
