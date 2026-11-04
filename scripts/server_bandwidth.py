"""Unprivileged TCP throughput estimates for only our server service processes.

No capture files, peer addresses, media names or browsing history are retained.
UDP traffic and TCP/IP headers are outside these socket payload counters.
"""
import ipaddress
from pathlib import Path
import re
import subprocess
import time

UNITS = ('vizio-stremio-lab.service', 'vizio-stremio-engine.service')


def server_pids():
    result = subprocess.run(['systemctl', '--user', 'show', *UNITS, '-p', 'ControlGroup', '--value'],
                            capture_output=True, text=True, check=True, timeout=3)
    pids = set()
    root = Path('/sys/fs/cgroup')
    for group in result.stdout.splitlines():
        # Inactive units return an empty group. Never scan the host cgroup root.
        if not group.startswith('/') or group == '/' or '..' in Path(group).parts:
            continue
        base = root / group.lstrip('/')
        if base.name not in UNITS or not base.is_dir():
            continue
        for path in base.rglob('cgroup.procs'):
            pids.update(int(value) for value in path.read_text().split())
    return pids


def address(endpoint):
    value = endpoint.rsplit(':', 1)[0].strip('[]').split('%')[0]
    parsed = ipaddress.ip_address(value)
    return parsed.ipv4_mapped if getattr(parsed, 'ipv4_mapped', None) else parsed


def parse_counters(text, pids):
    counters = {}
    for line in text.splitlines():
        owners = set(map(int, re.findall(r'pid=(\d+)', line)))
        if not owners.intersection(pids):
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        try:
            local, peer = address(parts[3]), address(parts[4])
            if peer.is_loopback or local == peer:
                continue  # Exclude this panel's local health polling.
        except ValueError:
            continue
        inode = re.search(r'\bino:(\d+)', line)
        if not inode:
            continue
        values = dict((key, int(value)) for key, value in re.findall(r'\b(bytes_received|bytes_sent|bytes_acked):(\d+)', line))
        if values:
            counters[inode.group(1)] = (values.get('bytes_received', 0), values.get('bytes_sent', values.get('bytes_acked', 0)))
    return counters


def collect():
    pids = server_pids()
    if not pids:
        return {}
    result = subprocess.run(['ss', '-t', '-i', '-n', '-p', '-H', '-O', '-e'],
                            capture_output=True, text=True, check=True, timeout=3)
    return parse_counters(result.stdout, pids)


class Sampler:
    def __init__(self, collector=collect, clock=time.monotonic):
        self.collector = collector
        self.clock = clock
        self.previous = None
        self.last_time = None

    def sample(self):
        now = self.clock()
        try:
            current = self.collector()
        except (OSError, ValueError, subprocess.SubprocessError):
            self.previous = None
            self.last_time = None
            return {'time': now, 'available': False, 'receive_bps': None, 'send_bps': None}
        rates = [0.0, 0.0]
        if self.previous is not None and self.last_time is not None:
            elapsed = now - self.last_time
            if 0 < elapsed <= 15:
                for key, values in current.items():
                    before = self.previous.get(key, (0, 0))
                    for i in range(2):
                        rates[i] += max(0, values[i] - before[i]) / elapsed
        self.previous, self.last_time = current, now
        return {'time': now, 'available': True, 'receive_bps': rates[0], 'send_bps': rates[1]}
