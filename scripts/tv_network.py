"""Local, reversible address changes for an already-paired TV."""
import hashlib
import http.client
import ipaddress
import json
import os
import ssl
import uuid

import tvctl


def address(value, pc_ip):
    try:
        ip = ipaddress.IPv4Address(value.strip())
    except (ValueError, AttributeError):
        raise RuntimeError('Enter a TV IPv4 address, such as 192.168.1.50, without a port.') from None
    if (ip.is_unspecified or ip.is_loopback or ip.is_multicast or ip.is_link_local
            or ip.is_reserved or str(ip) == pc_ip):
        raise RuntimeError('Enter the TV’s LAN address, different from this PC’s address.')
    return str(ip)


def verify_tv(ip, fingerprint):
    """Check the existing certificate before sending any pairing credential."""
    conn = http.client.HTTPSConnection(ip, 7345, timeout=5,
                                       context=ssl._create_unverified_context())
    try:
        conn.connect()
        actual = hashlib.sha256(conn.sock.getpeercert(binary_form=True)).hexdigest()
        if actual != fingerprint:
            raise RuntimeError('That address belongs to a different device. The saved TV address was not changed.')
    except OSError:
        raise RuntimeError('Could not reach the TV. Turn it on and check its IP address and Wi-Fi connection.') from None
    finally:
        conn.close()


def write_source(path, data):
    temp = path.with_suffix(path.suffix + '.network-tmp')
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'wb') as output:
        output.write(data)
    os.replace(temp, path)
    path.chmod(0o600)


class Change:
    def __init__(self, ip, pc_ip):
        self.tv = tvctl.read_private('tv.json')
        self.ip = address(ip, pc_ip)
        verify_tv(self.ip, self.tv['certificate_sha256'])
        self.path = tvctl.PRIVATE / 'stremio-server/server.js'
        self.source = self.path.read_bytes()
        self.record = tvctl.read_private('stremio-server-preparation.json')
        old_peers = ['127.0.0.1', '::1', pc_ip, self.tv['ip']]
        if (hashlib.sha256(self.source).hexdigest() != self.record['patched_sha256']
                or self.record['allowed_ips'] != old_peers
                or self.record['frontend_origin'] != f'http://{pc_ip}:8099'):
            raise RuntimeError('The streaming server configuration needs repair before changing the TV address.')
        # Match only our generated access guard; never replace arbitrary IP text.
        old = f'if ({json.dumps(old_peers)}.indexOf(peer) < 0)'
        peers = ['127.0.0.1', '::1', pc_ip, self.ip]
        new = f'if ({json.dumps(peers)}.indexOf(peer) < 0)'
        if self.source.count(old.encode()) != 1:
            raise RuntimeError('The streaming server access list needs repair before changing the TV address.')
        self.updated = self.source.replace(old.encode(), new.encode())
        self.new_record = dict(self.record, allowed_ips=peers,
                               patched_sha256=hashlib.sha256(self.updated).hexdigest())

    def backup(self):
        tvctl.save_private('tv-network-backup-' + uuid.uuid4().hex + '.json', {
            'tv': self.tv, 'preparation': self.record, 'server_source': self.source.decode(),
        })

    def apply(self):
        write_source(self.path, self.updated)
        tvctl.save_private('stremio-server-preparation.json', self.new_record)
        tvctl.save_private('tv.json', dict(self.tv, ip=self.ip))

    def restore(self):
        write_source(self.path, self.source)
        tvctl.save_private('stremio-server-preparation.json', self.record)
        tvctl.save_private('tv.json', self.tv)
