#!/usr/bin/env python3
"""Small, staged SmartCast controller. Secrets stay in .private; no store writes."""
import argparse
import datetime
import hashlib
import http.client
import ipaddress
import json
import os
from pathlib import Path
import ssl
import subprocess
import sys
import urllib.parse
import uuid

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / ".private"


def save_private(name, value):
    PRIVATE.mkdir(mode=0o700, exist_ok=True)
    os.chmod(PRIVATE, 0o700)
    path = PRIVATE / name
    temp = path.with_suffix(path.suffix + ".tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(value, f, indent=2)
        f.write("\n")
    os.replace(temp, path)
    os.chmod(path, 0o600)


def read_private(name):
    return json.loads((PRIVATE / name).read_text())


def request(method, path, body=None, authenticated=True):
    state = read_private("tv.json")
    ipaddress.ip_address(state["ip"])
    conn = http.client.HTTPSConnection(
        state["ip"], 7345, timeout=10, context=ssl._create_unverified_context()
    )
    try:
        conn.connect()
        fingerprint = hashlib.sha256(conn.sock.getpeercert(binary_form=True)).hexdigest()
        if fingerprint != state["certificate_sha256"]:
            raise RuntimeError("TV TLS certificate changed; inspect before updating the pin")
        headers = {"Accept": "application/json", "Connection": "close"}
        if authenticated:
            headers["AUTH"] = read_private("credentials.json")["auth_token"]
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()
        conn.request(method, path, body=data, headers=headers)
        response = conn.getresponse()
        raw = response.read(2 * 1024 * 1024)
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            save_private('last-control-error.json', {
                'method': method, 'path': path, 'http_status': response.status,
                'body_text': raw.decode('utf-8', errors='replace'),
            })
            raise RuntimeError(f"TV returned non-JSON (HTTP {response.status})") from None
        if response.status >= 400:
            result = value.get("STATUS", {}).get("RESULT", "unknown")
            raise RuntimeError(f"TV returned HTTP {response.status}: {result}")
        result = value.get("STATUS", {}).get("RESULT")
        if result and result != "SUCCESS":
            raise RuntimeError(f"TV response: {result}")
        return value
    finally:
        conn.close()


def pair():
    if (PRIVATE / "credentials.json").exists():
        raise RuntimeError("Pairing credential already exists; try capabilities first")
    identity = {"DEVICE_NAME": "Owner Linux TV Lab", "DEVICE_ID": "owner-tv-" + uuid.uuid4().hex[:12]}
    result = request("PUT", "/pairing/start", identity, authenticated=False)
    item = result["ITEM"]
    pending = dict(identity, PAIRING_REQ_TOKEN=item["PAIRING_REQ_TOKEN"])
    save_private("pairing-pending.json", pending)
    print("Normal pairing started. Enter the TV's PIN in the local desktop dialog.", flush=True)
    prompt = subprocess.run(
        ["zenity", "--entry", "--hide-text", "--title=Vizio TV pairing",
         "--text=Enter the PIN currently shown on your TV. It stays on this PC.",
         "--timeout=300"], capture_output=True, text=True
    )
    if prompt.returncode:
        raise RuntimeError("PIN dialog cancelled or timed out; no auth token saved")
    pin = prompt.stdout.strip()
    if not pin.isdigit() or len(pin) != 4:
        raise RuntimeError("Expected a four-digit TV PIN; not sent")
    pending.update(CHALLENGE_TYPE=1, RESPONSE_VALUE=pin)
    result = request("PUT", "/pairing/pair", pending, authenticated=False)
    save_private("credentials.json", {
        "auth_token": result["ITEM"]["AUTH_TOKEN"],
        "device_name": identity["DEVICE_NAME"], "device_id": identity["DEVICE_ID"],
        "paired_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    (PRIVATE / "pairing-pending.json").unlink(missing_ok=True)
    print("Paired. Credential saved locally with mode 0600; token withheld.")


def launch(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise RuntimeError("Only explicit HTTP(S) page URLs without credentials are allowed")
    return request("PUT", "/app/launch", {
        "VALUE": {"MESSAGE": url, "NAME_SPACE": 4, "APP_ID": "3001"}
    })


def launch_stored_launcher():
    """Browser-initiated navigation to our one exact sandbox file, not arbitrary file URLs."""
    return request('PUT','/app/launch',{'VALUE':{
        'MESSAGE':'filesystem:http://127.0.0.1:12345/persistent/owner-tv-home-rest-v1/index.html',
        'NAME_SPACE':4,'APP_ID':'3001',
    }})


def home():
    return request("PUT", "/app/launch", {"VALUE": {
        "MESSAGE": json.dumps({"app": "home", "bundle": "bundles/home"}, separators=(",", ":")),
        "NAME_SPACE": 4, "APP_ID": "1"
    }})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("pair", "capabilities", "current", "home"):
        sub.add_parser(name)
    sub.add_parser("launch").add_argument("url")
    args = parser.parse_args()
    if args.command == "pair":
        pair()
        return
    if args.command in ("capabilities", "current"):
        path = {"capabilities": "/system/capabilities", "current": "/app/current"}[args.command]
        result = request("GET", path)
        save_private(args.command + ".json", result)
        print(args.command + ": " + result.get("STATUS", {}).get("RESULT", "received"))
        print("Full response saved privately; top-level keys:", ", ".join(result))
    else:
        result = home() if args.command == "home" else launch(args.url)
        print(args.command + ": " + result.get("STATUS", {}).get("RESULT", "received"))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print("Stopped:", str(exc), file=sys.stderr)
        sys.exit(1)
