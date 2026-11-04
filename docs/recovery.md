# Recovery and rollback

**Current replacement-TV setup:** WatchFree → Stremio, Home normal. Use the
**Stremio TV** desktop panel to turn the shortcut off or stop hosting. Original
1031 HDMI-2 details below are historical; replacement PC input is unconfirmed.
See [current controls and power rollback](DESKTOP-CONTROL.md).
Automatic sleep prevention is independent of hosting; restore it using
`python3 scripts/server_awake.py restore`.

## Leave a test page

With the optional Home redirect enabled, physical Home is intended to return
to the configured PC screen after a short delay (Stremio selected November 2). To get directly to this PC, use
physical **Input → HDMI-2**. The clean launcher's **TV / HDMI** button displays
physical Input → HDMI-2 instructions; the ordinary API input setter was rejected. To stop the redirect
immediately, stop the watcher as shown below. The following Home results were
verified before Home redirection was added.

1. Press **Home** on the TV remote. This worked in the first custom-page test.
2. The lab page's **Return Home** button calls only the reviewed Home launcher.
3. From this project directory, run:

   ```bash
   python3 scripts/tvctl.py home
   ```

That sends the repository's Home descriptor to NS 4 / app 1. The resulting
interface reports NS 0 / app 2. That identifier alone does not prove whether
the TV shows its own Home or the current HDMI input. The owner has confirmed
that this leaves the test page. Use **Input** to select the PC's HDMI input if
needed. No factory reset is needed for these page tests.

The TV is also the owner's Linux monitor. Coordinate before a power-cycle
test or relaunch that covers the desktop. An ordinary unplug/reconnect cycle restored valid control state in the native
diagnostic. Local sandbox files were written afterward, so their survival across
a full power loss has not been tested. Remote standby/wake was tested earlier.
Do not factory-reset or flash firmware as a page-recovery step.

## Clean launcher and privacy toggles

The wallpaper is currently disabled after the owner confirmed arrow
responsiveness returned without it. Both the original Pictures image and the
private project copy remain intact. Do not re-enable it while diagnosing lag.

`disconnect_test.py` is a coordinated test, not a normal launch command. It
covers HDMI, pauses the three PC helpers after loading the page, verifies
listener closure, and arms a separate user timer for recovery. Run it only
when the owner is ready. The red OFFLINE indicator is test-only; after testing,
normal Home opens the ordinary launcher. Physical Input → HDMI-2 remains the
fallback while the helpers are paused. Manual recovery is:

```bash
systemctl --user start vizio-stremio-lab.service vizio-stremio-engine.service vizio-stremio-watch.service
```

The clean page can be opened deliberately with:

```bash
python3 scripts/open_launcher.py --bind 192.0.2.24
```

It covers HDMI, so coordinate first when using the TV as this PC's monitor.
Physical Input → HDMI-2 remains the escape. The optional PC watcher now matches
only the observed SMARTCAST + Home-app state and opens our page. This changes
the visible Home behavior through external automation, not a firmware remap.
TV / HDMI now displays the physical input steps. The read-only flag guard prevents
a misleading setter attempt while current_input is disabled.

Read or change only the PC-side behavior:

```bash
python3 scripts/configure_home.py status
python3 scripts/configure_home.py disable-redirect
python3 scripts/configure_home.py restore-stremio
python3 scripts/configure_home.py enable
python3 scripts/configure_home.py enable-stremio
```

`disable-redirect` preserves the clean power-on screen. `restore-stremio`
disables the Home redirect and restores the previously tested Stremio startup.
`enable` selects the clean startup and enables Home redirection. No TV writes
or launches occur in this helper. `enable-stremio` selects Stremio for both
Home redirection and wake. The watcher reads configuration each loop.

Automatic startup reads optional `.private/startup.json` at each observed
off/on transition. `{"screen":"launcher"}` selects the clean page;
`{"screen":"stremio"}` restores the original Stremio start screen. Missing
file also defaults to Stremio. Changing this PC file does not write TV firmware.

Viewing Data was changed from On to Off; Limited Ad Tracking from Off to On.
Read their current values or restore the saved original toggle values with:

```bash
python3 scripts/privacy_settings.py status
python3 scripts/privacy_settings.py restore
```

Restore re-enables the original viewing-data preference. It cannot undo any
server-side deletion of historical logs associated with opting out. The helper
modifies only these two observed normal menu items; no arbitrary store keys.

Routine page/media event logging now defaults off. Existing historical private
test logs were retained. Deliberate troubleshooting can opt in with
`serve_lab.py --diagnostics` after stopping the page-host service; do not run
two listeners on port 8099. Logs stay local and private.

## Stop or disable PC services

The former foreground processes have been replaced by per-user systemd units.
To pause automatic TV launches while using it as a monitor:

```bash
systemctl --user stop vizio-stremio-watch.service
```

To stop everything and prevent it returning at the next Linux login:

```bash
systemctl --user disable --now vizio-stremio-watch.service vizio-stremio-engine.service vizio-stremio-lab.service
```

To enable it again:

```bash
systemctl --user enable --now vizio-stremio-lab.service vizio-stremio-engine.service vizio-stremio-watch.service
```

These commands do not undo TV pairing or change firmware/settings. Stopping
the engine stops torrent downloading/seeding; stopping the page host makes the
local app unavailable. No root/system service, user lingering, firewall rule,
DNS filter, or router change was installed. The official engine package was
extracted privately, not installed with the system package manager.

Units are in `/home/your-user/.config/systemd/user/vizio-stremio-*.service`.
Private logs live in `.private/service-logs/`; avoid sharing them because
future media/add-on URLs may contain credentials. After disabling the units,
removing only those three unit files and running `systemctl --user daemon-reload`
removes this integration. Same-name preexisting unit backups, if any, are under
`.private/service-backups/`.

For a foreground engine diagnosis, stop its user unit first to avoid a second
listener, then use these two separate commands:

```bash
python3 scripts/stremio_service.py prepare --bind <LINUX_LAN_IP>
python3 scripts/stremio_service.py run
```

The preparation verifies the pinned official package hash, applies only the
reviewed IP and frontend-origin restrictions, and records hashes privately.
Its HTTP port is 11470; only this PC and the TV are admitted. HTTPS/casting
are disabled for this local test. It does not enable router port forwarding.

## Pairing and certificate changes

Long-lived auth lives only in `.private/credentials.json` (0600); the project
directory's `.private` child is 0700 and gitignored. Deleting the local file
does not necessarily revoke the TV's saved pairing. Use the TV's normal paired
device management if revocation is needed; that interface has not been tested.

`tvctl.py` pins the certificate observed in the first unauthenticated read.
It stops if the fingerprint changes. Confirm the TV address/device and inspect
the new certificate before changing `.private/tv.json`; do not silently disable
this check. The initial trust is local trust-on-first-use, not public CA identity.

If a pairing dialog times out before completion, no auth token is saved. A
subsequent deliberate pairing attempt may start a fresh normal PIN flow.

## Add-on import rollback

The original seven TV-app add-on descriptors are in
`.private/tv-addons-before-import.json`. The imported eleven are in
`.private/addon-import.completed.json`. These can contain sensitive configured
URLs; do not publish them. The original PC profile was opened read-only and
was not modified. No account token or password was imported into the TV.

For a simple rollback, uninstall the added add-ons through Stremio's normal
Addons page. The saved original descriptor list permits a deliberate restore
if needed. Do not delete TV browser storage indiscriminately: it also contains
the tested Linux streaming-server selection and other player preferences.

## Undo REA integration

Original configuration backup:

`/home/your-user/.codex/backups/before-rea-20261101T195527Z/config.toml`

An additional byte copy immediately after setup is stored beside it as
`config.toml.after-rea-setup`; REA's own backup also remains alongside the live
config. Backups may contain private configuration and must not be shared.

Prefer the installed tool's reviewed `rea uninstall` workflow for removing
REA-owned registration/skill files while keeping unrelated integrations.
Preview its current help/plan first. Alternatively, remove only
`[mcp_servers.rea]` and its bundled skill after backing up the current files.
Do not blindly overwrite the whole config with an old backup if settings have
changed since this setup. Reconnect/restart Codex after removal.

Node and REA were installed under `/home/your-user/.local`; no system Node package
was replaced. Removing these user-local components should be a separate
deliberate action after checking whether another project has begun using them.

## Boundaries for later stages

Before firmware flashing, factory resets, bootloader changes, or potentially
unrecoverable writes, document the exact target/change and a demonstrated
recovery method, then obtain the owner's approval. No such action is authorized
by the routine page/playback tests. Do not invent store keys to seek startup.

### Current HDMI escape

Use the physical remote's Input button, then HDMI-2. The TV rejects the ordinary
current_input setter in the current firmware state. TV / HDMI on our page now
shows these steps rather than attempting an automatic switch. Do not rely on
legacy remote API input-code cycling or an arbitrary app descriptor for recovery.

Read-only tests may run without readiness prompts per the owner's November 1
instruction; ask when owner feedback or physical interaction is required.

## Native browser-file test and checkpoint

Only our disposable Chromium PERSISTENT directory
`owner-tv-lab-disposable-v1` has been created. No native root filesystem file,
Home provider, registry value, firmware, or boot setting has been changed.
Its contents can be removed using `open_native_probe.py --bind 192.0.2.24
file-cleanup` while the watcher is paused and a recovery timer is armed. Verify
the fresh private cleanup report. Never clear all browser storage or registry keys.

The native diagnostic may pause the watcher using an independent ten-minute
`vizio-native-registry-recovery.timer` (earlier file/bridge timers may be inactive).
Check live state. Restore the watcher, then stop only these diagnostic timers.
`docs/RESUME-HERE.md` and `.private/checkpoints/latest.json` locate saved progress.
