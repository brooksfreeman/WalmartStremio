#!/usr/bin/env python3
"""User-service entry point: component output stays in private local logs."""
import argparse
import datetime
import ipaddress
import os
import sys

import tvctl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('component', choices=['lab', 'engine', 'watch'])
    parser.add_argument('--bind', required=True)
    args = parser.parse_args()
    bind = str(ipaddress.IPv4Address(args.bind))
    os.umask(0o077)
    logs = tvctl.PRIVATE / 'service-logs'
    logs.mkdir(mode=0o700, exist_ok=True)
    fd = os.open(logs / (args.component + '.log'), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    os.dup2(fd, 1)
    os.dup2(fd, 2)
    os.close(fd)
    print(datetime.datetime.now().astimezone().isoformat(), 'Starting', args.component, flush=True)
    commands = {
        'lab': ['serve_lab.py', '--bind', bind],
        'engine': ['stremio_service.py', 'run'],
        'watch': ['watch_power.py', '--bind', bind],
    }
    command = commands[args.component]
    argv = [sys.executable, '-u', str(tvctl.ROOT / 'scripts' / command[0]), *command[1:]]
    os.chdir(tvctl.ROOT)
    os.execv(sys.executable, argv)


if __name__ == '__main__':
    main()
