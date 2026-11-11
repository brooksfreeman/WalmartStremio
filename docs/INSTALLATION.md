# Installation guide

[Back to README](../README.md) · [File guide](FILE-GUIDE.md)

This guide sets up the PC-hosted Stremio app and WatchFree shortcut. You do not
need the firmware archives, native Home experiments or hardware research.

**Before starting:** use a Linux x86-64 desktop PC you can leave running. Keep
the TV on and its remote nearby. These commands are for Bash on Mint/Ubuntu/Debian.
Run one code block at a time, in order. If a command fails, stop at that step;
continuing can hide the original problem. Only commands beginning with `sudo`
need administrator privileges. Do not run the project itself as root.

The steps are based on the working installation and checked against the source.
They have not been tested as a complete fresh installation on a second machine.

## Contents

- [Compatibility](#compatibility-and-tested-limits)
- [1. Prerequisites](#1-install-host-prerequisites)
- [2. Download and network addresses](#2-clone-this-project-and-choose-your-addresses)
- [3. Pair the TV](#3-record-this-tvs-certificate-and-pair-normally)
- [4. Build the TV frontend](#4-build-the-pinned-tv-frontend)
- [5. Start the services](#5-prepare-the-engine-and-install-user-services)
- [6. Open Stremio](#6-open-stremio-and-accept-your-server-address)
- [7. Enable WatchFree](#7-enable-the-physical-watchfree-shortcut)
- [8. Desktop controls and add-ons](#8-install-and-use-the-desktop-app)
- [9. Automatic startup](#9-startup-after-reboot-and-keeping-the-pc-awake)
- [Troubleshooting](#troubleshooting)
- [Updates and removal](#updates-and-removal)

## Compatibility and tested limits

| Item | Tested setup / requirement |
| --- | --- |
| TV | W4K65M-1030, firmware `86.920.9.3-2`, software `86.920.9.3-2.12` |
| PC | Linux Mint 22.3, x86-64, Xfce 4.18, systemd user services |
| Desktop UI | GTK 3, system Python with PyGObject and Cairo |
| Frontend | Stremio Web `5.0.0-beta.43`, pinned commit below |
| Node | Existing build verified with Node `24.22.2`; upstream declares Node >=22 |
| Package manager | pnpm `11.8.0`, explicitly pinned in commands |
| Engine | Official Stremio service `0.1.22`, engine `4.21.0`, Linux amd64 package |
| Network | TV and PC mutually reachable; no guest/client isolation; stable IPv4 addresses |
| WatchFree | Stable observed app: input `SMARTCAST`, namespace `4`, app ID `3014` |

Other models, firmware revisions, desktops and operating systems are unverified.
A matching marketing name alone does not prove the same API or browser behavior.
Windows, macOS, ARM hosts and container deployment have no tested installation
path here. The engine preparation script specifically downloads an amd64 Debian
package. Each user must pair their own TV and install their own add-ons.

Verified on the original installation: TV playback with sound; physical WatchFree
redirect; desktop switches; startup enablement; add-on list/install/remove with
existing add-ons preserved; and real server TCP traffic in the graph. A full PC
reboot and a fresh second-machine end-to-end installation have not been tested.
Build 12 removes the standalone floating Home button entirely. Its browser
regression checks passed; final owner visual confirmation on the TV is pending.

## 1. Install host prerequisites

Use a normal desktop user account. Run the following from a terminal in the
graphical session, so pairing dialogs, GTK and desktop settings are available.
Commands below target Mint/Ubuntu/Debian; do not run the Python services as root.

```bash
sudo apt update
sudo apt install git ca-certificates python3 python3-gi python3-gi-cairo \
  python3-cairo gir1.2-gtk-3.0 zenity iproute2 desktop-file-utils \
  xdg-user-dirs libglib2.0-bin
```

Install **Node.js 24 with npm** from the [official Node.js download page](https://nodejs.org/en/download).
Select version **24**, Linux and the installation method appropriate to your PC;
follow the instructions shown there, then reopen your terminal if requested.
The recorded build used `24.22.2`. The distro’s default Node package may be too
old. Node runs the build tools; pnpm downloads the frontend dependencies. The
commands below run the pinned pnpm version through npm’s `npx`, so you do not
need a separate global pnpm installation. Verify before continuing:

```bash
node --version
npm --version
npx --yes pnpm@11.8.0 --version
/usr/bin/python3 -c 'import gi, cairo; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk; print("GTK ready")'
systemctl --user --version
stat -fc %T /sys/fs/cgroup
```

The last command should report `cgroup2fs` for the bandwidth monitor. Node/pnpm
are build dependencies; Python/systemd and the downloaded engine are needed
during normal hosting. [pnpm installation documentation](https://pnpm.io/installation)
describes installation options; this project deliberately pins an older tested
version rather than requesting `latest`.

## 2. Clone this project and choose your addresses

Keep the clone in a permanent directory; installed services and the desktop
shortcut point to that location. These commands create a `WalmartStremio` folder
inside your current directory. If you already cloned it, enter that folder
instead of cloning again.

```bash
git clone https://github.com/brooksfreeman/WalmartStremio.git
cd WalmartStremio
read -r -p 'PC LAN IPv4 address: ' TVLAB_PC_IP
read -r -p 'TV LAN IPv4 address: ' TVLAB_TV_IP
export TVLAB_PC_IP TVLAB_TV_IP
```

Find the TV address in its Network/TV Information screen. Find the PC address
in your connection settings or `ip -4 address`. Use the LAN interface that
reaches the TV, not loopback or an unrelated VPN interface. Reserve both
addresses in the router's DHCP settings before setup. Continue in this same
terminal; the exported variables are used below. Enter addresses only (for example,
`192.168.1.50`), without `http://` or a port. Do not use `192.0.2.*` addresses
from older project examples; those are documentation placeholders.

If you open another terminal later, `cd` back to the project folder and repeat
the two `read` commands and `export` line to restore these variables.

Network connections used:

| Connection | Purpose |
| --- | --- |
| PC → TV TCP 7345 | Certificate-pinned HTTPS pairing and local control |
| TV → PC TCP 8099 | Stremio frontend and local control endpoints |
| TV → PC TCP 11470 | Streaming engine |
| PC/TV → internet | Build downloads, selected add-on services and media |

Allow the TV to reach the two PC ports in your existing firewall. Do not turn
the firewall off. Do not forward these ports through your router. Frontend and
engine HTTP are intended for a trusted LAN, not public internet hosting. The
service restricts which device addresses may connect, but this is not a public
hosting service with user logins.
GitHub stores source; GitHub Pages cannot run this Python server or media engine.

## 3. Record this TV's certificate and pair normally

First, record an identity check for your TV. Copy the complete block below,
including its final `PY` line, into your terminal. It saves the TV address and
a fingerprint of its HTTPS certificate so later requests can detect a different
certificate. Confirm the address belongs to your TV before typing `yes`. This
first connection trusts the device at that address; it does not independently
verify the manufacturer. The script refuses to overwrite an existing setup.

```bash
python3 - <<'PY'
import hashlib, ipaddress, os, socket, ssl, sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
import tvctl
ip = str(ipaddress.IPv4Address(os.environ['TVLAB_TV_IP']))
if (tvctl.PRIVATE / 'tv.json').exists() or (tvctl.PRIVATE / 'credentials.json').exists():
    raise SystemExit('Existing TV configuration found. Stop and inspect it; nothing overwritten.')
context = ssl._create_unverified_context()
with socket.create_connection((ip, 7345), timeout=10) as raw:
    with context.wrap_socket(raw, server_hostname=ip) as connection:
        pin = hashlib.sha256(connection.getpeercert(binary_form=True)).hexdigest()
print('TV address:', ip)
print('Certificate SHA-256:', pin)
print('Is this your TV? Type yes to save: ', end='', flush=True)
with open('/dev/tty') as terminal:
    confirmed = terminal.readline().strip()
if confirmed != 'yes':
    raise SystemExit('Nothing saved.')
tvctl.save_private('tv.json', {'ip': ip, 'certificate_sha256': pin})
print('Saved locally. Next run the normal PIN pairing command.')
PY
```

Only continue after it prints **Saved locally**. Now start normal PIN pairing:

```bash
python3 scripts/tvctl.py pair
```

After pairing succeeds, check that the TV accepts an authenticated request:

```bash
python3 scripts/tvctl.py capabilities
```

**Expected result:** the pairing command displays a PIN on the TV. Enter it in
the local Zenity dialog. A successful result saves the credential under `.private/` with restricted permissions and does not
print the token. Do not copy another person's `.private/` directory or share
pairing output, tokens or raw TV responses in a GitHub issue.

If no PIN appears, check the TV is on, setup is complete, the address is correct,
and TCP 7345 is reachable. Stop on an unexpected certificate change; confirm the
device and address rather than bypassing the comparison.

## 4. Build the pinned TV frontend

“Frontend” means the interface you see on the TV. The upstream source and its
lockfile are fetched into the ignored private build directory. Start this section
from the `WalmartStremio` folder. The parenthesized commands temporarily enter
the upstream directory and return automatically. The public preparation script
applies the local adaptations.

```bash
mkdir -p .private research/reviews
chmod 700 .private
git clone https://github.com/Stremio/stremio-web.git .private/stremio-tv-src
git -C .private/stremio-tv-src checkout --detach c34935cc36e28c00ec15f066c38bbc6f6f59f716
(
  cd .private/stremio-tv-src
  npx --yes pnpm@11.8.0 install --frozen-lockfile --ignore-scripts
)
python3 scripts/prepare_stremio_tv.py
(
  cd .private/stremio-tv-src
  npx --yes pnpm@11.8.0 run build
)
```

Do not switch to an arbitrary newer upstream commit: the preparation script
expects specific source locations and intentionally stops if they change. The
bundled HLS.js file and its license must stay in `web/vendor/`.

The built frontend is served at `/stremio/`. Its source, node_modules and the
rest of `.private/` are not exposed as static files. Existing asset-size warnings
are known; a nonzero build exit status is a failure. The standalone floating
Home button is absent in this source; the auto-hiding player bar still has a
Home action.

## 5. Prepare the engine and install user services

```bash
python3 scripts/stremio_service.py prepare --bind "$TVLAB_PC_IP"
python3 scripts/install_services.py --bind "$TVLAB_PC_IP" --install
systemctl --user daemon-reload
systemctl --user start vizio-stremio-lab.service vizio-stremio-engine.service
```

Engine preparation downloads the official pinned package, checks SHA-256,
extracts it locally and applies the reviewed LAN allowlist/CORS adaptations. It
does not install a system package or firewall rule. The services are installed
but are not enabled at boot by the installer. `install_services.py` regenerates
the lab, engine and watch files in `config/systemd/` with your actual clone path
and PC address. Do not copy the repository’s example versions directly into
systemd. Those generated files will show as modified in Git; do not publish your
machine-specific versions.

Check both endpoints from the PC:

```bash
python3 - <<'PY'
import os, urllib.request
ip = os.environ['TVLAB_PC_IP']
for port, path in [(8099, '/health'), (11470, '/settings')]:
    with urllib.request.urlopen(f'http://{ip}:{port}{path}', timeout=5) as response:
        print(port, response.status)
PY
```

**Expected result:** both should print HTTP status `200`. A working frontend alone does not prove the media
engine is ready.

## 6. Open Stremio and accept your server address

Configure and open the TV's streaming-server settings:

```bash
python3 scripts/open_stremio.py --bind "$TVLAB_PC_IP" --screen server
```

On the TV, accept/use `http://YOUR_PC_LAN_IP:11470`, replacing the placeholder
with the same PC address. Then open the catalog:

```bash
python3 scripts/open_stremio.py --bind "$TVLAB_PC_IP"
```

Keep route options after `#`, as the supplied launcher does. Mixing a
document-level query string with a route-level query can break upstream server
configuration parsing. A successful launch API response only means the request
was accepted: visually verify the TV actually shows Stremio, then test a lawful
stream with video and sound. Content, codecs and add-on availability vary.

## 7. Enable the physical WatchFree shortcut

First, with the watcher stopped, observe what your TV actually reports:

```bash
systemctl --user stop vizio-stremio-watch.service
python3 scripts/observe_home.py --seconds 30
```

While it runs, press the physical WatchFree button. The tested stable state is
`SMARTCAST` with namespace `4` and app ID `3014`; a transient namespace `1` /
app `51` was also seen. If your stable state differs, stop here: matching that
device requires an inspected change to `is_watchfree()` in
`scripts/home_navigation.py`. Do not broaden it to every native app or HDMI.

If it matches, leave WatchFree using physical Home or Input, then enable:

```bash
python3 scripts/configure_home.py enable-watchfree
systemctl --user start vizio-stremio-watch.service
```

Press WatchFree again after the observer has seen a different screen. Stremio
should open after a brief delay. Starting the watcher while WatchFree is already
open does not trigger an initial launch. The code detects app state, not the
physical key itself, so opening WatchFree through another route also redirects.
The observer also launches the configured screen after it actually observes a
TV power-off → power-on transition. Missing network replies do not count as off.

To undo immediately:

```bash
systemctl --user stop vizio-stremio-watch.service
python3 scripts/configure_home.py disable-watchfree
```

## 8. Install and use the desktop app

```bash
python3 scripts/install_desktop_control.py
```

Open **Stremio TV** from the desktop or Applications. If the desktop environment
requires it, mark the shortcut as allowed/trusted. A direct fallback is
`/usr/bin/python3 scripts/tv_control_panel.py` from the project directory.

| Control | Effect |
| --- | --- |
| Start / repair | Restarts frontend/engine; starts watcher if shortcut is enabled |
| Stop server | Stops hosting and observer now; does not turn off boot enablement |
| WatchFree opens Stremio | Persists shortcut choice; off stops/disables watcher, on starts hosting and watcher |
| Start server when this PC turns on | Enables/disables user units and enables lingering when turning on |
| Open Stremio on TV | Starts hosting if needed, then launches the TV page |
| Close window | Leaves the current service state unchanged |

The no-sleep service is independent of Stop server. A PC shutdown always stops
hosting until the PC boots again.

### Choose whether subtitles start on or off

In **Overview**, use **Subtitles on by default**. New installations start with
this option On. It applies when a video starts, including resumed videos and
next episodes. On chooses an available track using your saved/configured subtitle
language, with English as the fallback. Off prevents automatic caption selection.
You can still change captions manually during the current video.

Saving this setting does not start the server or contact the TV. After updating
from an older version, rebuild the frontend with `prepare_stremio_tv.py` and the
build command in step 4, then exit and reopen Stremio on the TV. Updating only
the desktop Python code will not update the TV player. Local tests passed;
live TV playback of this new subtitle-default behavior is not yet verified.

### Update the TV IP address

If the TV gets a new address, open **Network**, enter the IPv4 address shown in
the TV's network settings in the four number boxes, and choose **Save TV IP
address**. Each box accepts 0–255. Tab or a period moves to the next box. Keep
the TV on.
The app checks that it is your paired TV, then updates the saved address and
both server access lists. Running services briefly restart, interrupting playback;
a stopped server stays stopped. WatchFree and boot preferences are preserved.
An unreachable address or different TV certificate leaves the settings unchanged.

### Add-ons without editing code

In **Add-ons**, paste a provider's `stremio://…` install link or an HTTP(S)
manifest URL, then choose **Install add-on**. Use **Refresh from TV** to fetch
the current list. Click **Delete** beside an add-on to uninstall it, then confirm. Protected built-ins cannot be deleted.
Configured links are masked because they can contain personal tokens.

These operations open the TV's add-ons screen and leave current playback.
The TV must be on and paired. Installation/removal is reported successful only
after the TV core confirms the changed list. Existing descriptors are backed up
privately before changes. The first displayed list may be a cached snapshot.

This repository does not include anyone's Torrentio configuration, account,
provider token or paid service access. If you use Torrentio or another provider,
obtain your own configured manifest/install URL and paste it here. A provider
configuration webpage URL is not necessarily an add-on manifest URL. Only use
media and services you are entitled to access.

### Bandwidth monitoring

Overview shows current receive/send rates in **Mb/s** and the last two minutes
of traffic for the host and engine processes, including their child processes.
It uses Linux cgroup-v2 process membership and `ss` TCP payload counters. It
excludes other PC apps, local health checks, UDP and protocol headers; short
connections closed between samples may be missed. It is an estimate, not a
percentage of internet capacity. History stays in memory while the app runs.

## 9. Startup after reboot and keeping the PC awake

Turn on **Start server when this PC turns on** in the desktop panel. CLI
equivalent, after enabling the WatchFree configuration above:

```bash
loginctl enable-linger "$USER"
systemctl --user enable vizio-stremio-lab.service vizio-stremio-engine.service vizio-stremio-watch.service
```

Lingering allows the user services to start before desktop login. If your
distribution requires administrator authorization for lingering, complete its
normal authorization flow. Make sure the network itself autoconnects before
login. With NetworkManager, use the connection editor to enable automatic
connection and availability for all users; a user-session-only Wi-Fi secret may
prevent before-login connectivity. DHCP reservations must remain stable.

For a desktop-independent sleep/idle blocker:

```bash
mkdir -p "$HOME/.config/systemd/user"
cp config/systemd/vizio-stremio-awake.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now vizio-stremio-awake.service
systemd-inhibit --list
```

Also set your desktop power preferences to never suspend automatically on AC.
The supplied `server_awake.py apply` additionally backs up and changes the
tested GNOME power schema and Xfce 4.18 inactivity settings. Use that helper only
on a matching desktop with `xfconf-query` available; it is not a universal KDE,
GNOME-only or laptop power configurator. On the tested Mint/Xfce setup:

```bash
sudo apt install xfconf
python3 scripts/server_awake.py apply
python3 scripts/server_awake.py status
```

It applies battery settings too. Lid-close behavior, manual suspend, power loss
and another administrator's power policy require separate consideration. To
restore settings saved by this helper, use `python3 scripts/server_awake.py restore`.
If you installed only the inhibitor manually, disable that unit manually instead.

When ready, test a normal PC reboot yourself. After networking returns, check
service status, both health endpoints, WatchFree launch, then playback. Merely
showing units as enabled is not an end-to-end reboot test.

## Troubleshooting

| Symptom | Checks / fix |
| --- | --- |
| Server stopped | Use Start / repair; stopping now and disabling boot are separate controls |
| Blank TV or launch fails | TV on/setup complete; correct address/pairing; 7345 reachable; build exists; both endpoints healthy |
| TV loads UI but cannot stream | Reaccept this PC's `:11470` address; check engine and firewall; try a known lawful stream with a compatible format |
| WatchFree opens normally | Toggle enabled; watcher active; stable app ID matches; leave WatchFree once before trying again |
| Return to desktop | Use the physical TV Input button and choose the actual PC-connected HDMI port; there is no universal HDMI-2 assumption |
| Add-on request times out | TV on and reachable; frontend loaded; no other pending operation; retry after the previous request expires |
| Add-on URL rejected | Use an actual manifest/install URL, not a webpage; URL credentials/fragments and non-HTTP schemes are rejected |
| Bandwidth graph zero/unavailable | Services and real transfer active; cgroup-v2 available; `ss` installed and allowed to expose same-user socket ownership |
| Old floating Home still visible | Exit Stremio, then reopen it so the new JavaScript loads; rebuilding does not alter an already-running TV page |
| Certificate changed | Confirm TV/address and inspect identity; do not disable certificate comparison |
| Before-login startup fails | Check lingering, enabled units, network autoconnect and stable addresses |
| GTK import fails | Use `/usr/bin/python3` with distro PyGObject/Cairo, not an unrelated virtualenv |
| Preparation script stops | Verify exact upstream commit and pinned dependencies; inspect the mismatch instead of removing its checks |

Useful local checks:

```bash
systemctl --user is-active vizio-stremio-lab.service vizio-stremio-engine.service vizio-stremio-watch.service
systemctl --user is-enabled vizio-stremio-lab.service vizio-stremio-engine.service vizio-stremio-watch.service
loginctl show-user "$USER" -p Linger
python3 -m unittest discover -s tests -v
```

Component output is under `.private/service-logs/`; it is not primarily in the
systemd journal because the service entry point redirects output. Never attach
these files wholesale to public issues. If a downloaded engine cannot execute,
check architecture and missing shared libraries locally; do not replace the
pinned package with an unverified binary.

### If the TV stays on HDMI after a launch

The launch response alone does not confirm that the screen changed. Press the
physical Home/SmartCast button to leave HDMI, then retry **Open Stremio on TV**.
Use **Input** and the PC-connected HDMI port to return to the desktop if the TV
also serves as your PC monitor.

### If addresses change

For a TV address change, use **Network → Save TV IP address** in the desktop app.
A replacement TV requires its own deliberate certificate recording and PIN pairing;
this setting only accepts the already-paired TV.

For a PC address change, stop the three hosting services. Set `TVLAB_PC_IP` to the
new PC address, then rerun engine `prepare`, service installation and `daemon-reload`. Start the
services and accept the new streaming-server address on the TV. Both the engine
allowlist/CORS origin and generated service binding must match. Never silently
reuse another TV's credential or certificate.

## Updates and removal

Before updating, keep a local backup of `.private/` and your source version.
Check `git status` first: setup generates local service files and may regenerate
patch reports. Preserve those changes before pulling updates; do not discard
files blindly or force an update over your configuration.
That backup contains secrets: keep it out of GitHub. Stop hosting, review the
source changes, rerun frontend preparation/build, and restart. Reopen the TV app
to load changed JavaScript. Reprepare the engine only if its adaptation or
addresses changed. Moving the project requires regenerating service files and
the desktop shortcut.

To stop and disable automatic hosting:

```bash
systemctl --user disable --now vizio-stremio-watch.service vizio-stremio-lab.service vizio-stremio-engine.service
```

Restore power settings first if you used `server_awake.py apply`; otherwise
disable `vizio-stremio-awake.service` separately. Remove only this project's user
unit files and `stremio-tv.desktop` launchers if uninstalling, then run
`systemctl --user daemon-reload`. Leave lingering enabled if other user services
need it. Removing local credential files does not necessarily revoke the TV's
saved pairing; use its normal paired-device controls when available. Deleting
`.private/` loses local add-on backups and settings, so do that only deliberately.

## Sources, licenses and privacy

The frontend starts from [Stremio Web's pinned source](https://github.com/Stremio/stremio-web/tree/c34935cc36e28c00ec15f066c38bbc6f6f59f716).
Its `package.json` and `pnpm-lock.yaml` are obtained from that checkout unchanged.
The preparation script and `client/` files provide the local changes.
The engine is downloaded from the [official service release](https://github.com/Stremio/stremio-service/releases/tag/v0.1.22)
with SHA-256 `fcbab342fcd8990312b400698ae85f9c87aed0326a0da0168c1ddba18c39a415`.
See [third-party notices](../THIRD_PARTY_NOTICES.md) and [LICENSE](../LICENSE).
No affiliation with Vizio, Walmart or Stremio is claimed.

Keep `.private/`, `.env`, `.tv_auth`, account/add-on URLs, device captures and
generated machine-specific service files out of commits. The included ignore
rules help but do not protect files already tracked or manually forced into Git.
Report model/firmware, host OS, error category and redacted steps when requesting
help. Do not publish serial numbers, network details, PINs, tokens or provider URLs.
