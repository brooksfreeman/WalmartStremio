# Stremio TV desktop controls

Double-click **Stremio TV** on `/home/your-user/Desktop/`, or find it in Applications.
It opens a local GTK3 panel; no terminal or web account required. Closing the
window leaves background services running.

## Controls

- **Server status** checks both the frontend host and streaming engine.
- **WatchFree opens Stremio** toggles PC observation and persists the preference.
  Off stops/disables the observer; hosting remains online. On starts hosting if
  needed and restores the observer. Home remains normal.
- **Start server when this PC turns on** controls the server units' boot enablement.
  User lingering starts them before login; Wi-Fi is configured for system-wide
  autoconnect. This toggle does not immediately stop running services.
- **Start / repair** restarts hosting and the observer if its shortcut is enabled.
- **Stop server** stops all three processes now. The boot toggle determines
  whether they return at the next boot. Existing streaming playback will stop.
- **Open Stremio on TV** starts hosting if needed and sends its reviewed app launch.

The current WatchFree button route was physically verified on replacement1030.
PC detects stable WatchFree app4/3014 and opens Stremio. A brief WatchFree flash
can appear; opening WatchFree via another route also redirects. This is not a
remote firmware rewrite. Home redirect is disabled.

## Add-ons tab

1. Paste the provider's Install link (`stremio://…`) or its HTTP(S) manifest.json
   URL. A configured link can contain personal tokens, so it is masked by default.
2. Click **Install add-on**. The TV opens Stremio's add-ons screen and confirms the
   new descriptor is installed. The input clears after confirmed success.
3. **Refresh from TV** reads the installed list. **Remove selected** confirms and
   removes one add-on; protected built-ins stay protected.

These operations open the TV screen and therefore leave current playback. They
require the paired TV to be on. No editing source or copying a Stremio account is
needed. An initial list is a cached snapshot; refresh for current state. Exact
pre-change descriptors, manifests and configured URLs are retained only under
.private. Pairing/certificate identity binds snapshots to the correct TV. Requests
use one-use nonces, timeouts, allowed operations and TV-only Origin/source checks.
Provider manifest text is treated as data. URLs are never included in public logs
or desktop error messages. HTTP(S) redirects are validated before following them.

## Bandwidth graph

Overview shows current server receive/send in **Mb/s**, with a two-minute history.
It reads Linux TCP socket counters for the frontend and engine service cgroups,
including child processes. Other PC applications and local health checks are
excluded. UDP and protocol headers are excluded, and sockets that close between
samples may be missed; this is an estimate of server TCP throughput. It is not
whole-PC traffic or a percentage of an assumed internet speed. It also captures
HTTP streams sent to the TV, not only torrent-engine statistics. No packet capture,
peer address log, stream name log or persistent bandwidth history is created.
Requires Linux cgroup-v2 process membership and iproute2's ss; unavailable counters
are labeled unavailable rather than substituted with whole-PC traffic.

## Startup, network and power

All three service units are enabled and retry on failure while the network starts.
User lingering is enabled. Host/engine health checks passed during validation. The owner explicitly left
hosting stopped after November3 control testing; Start / repair restarts it. Wi-Fi
autoconnect/system availability checked. A full PC reboot was not performed.
Addresses remain192.0.2.24 (PC),192.0.2.57 (TV); DHCP reassignment may require
updating prepared units, allowlists and the TV's saved server preference.

Automatic sleep is disabled in the installed Xfce power manager and GNOME settings.
A separate enabled user service, vizio-stremio-awake.service, holds an actual
sleep/idle block inhibitor. Its state was verified with systemd-inhibit. The
[Xfce4.18 source](https://github.com/xfce-mirror/xfce4-power-manager/blob/xfce-4.18/src/xfpm-manager.c#L494)
confirms inactivity value14 removes the sleep alarms. No display blanking or lid
policy change was necessary for this desktop chassis.

To restore the exact saved automatic-sleep preferences and remove our inhibitor:

```bash
python3 scripts/server_awake.py restore
```

Original settings stay private in `.private/server-power-before.json`. The awake
service is independent of the panel's hosting switch because owner requested the
computer never sleep. Turning the PC off necessarily stops hosting until boot.

## Installation and validation

Source: scripts/tv_control_panel.py; installer: scripts/install_desktop_control.py;
icon: config/icons/stremio-tv.svg. Launchers installed at:

- `/home/your-user/Desktop/stremio-tv.desktop`
- `/home/your-user/.local/share/applications/stremio-tv.desktop`

Live controls passed shortcut off/on and boot preference off/on, then restored
all services online, WatchFree on and boot enabled. Desktop entries validated,
trusted and launched. GUI screenshot visually reviewed; service units verified.
See research/reviews/desktop-control-validation.json. No packages installed. November3 adds 6 standard-library regression tests and
real TV URL installation/removal verification. Both tabs were visually reviewed.

Torrentio was installed separately from the owner's cached PC descriptor, using
an origin-checked TV-only one-use import. The replacement browser client verified
its presence; URLs/account details were not exposed. Old-TV import records were
preserved and the new TV's previous add-ons backed up privately.
