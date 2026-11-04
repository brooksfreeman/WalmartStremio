# Resume here

Updated November 1, 2026, local evening. Project:
`/path/to/WalmartStremio`.

## End-of-session handoff

Owner is going to sleep and requested all progress saved after current tasks.
Read-only native Home investigation and rollback preflight are complete. No
additional physical interaction or unattended native write should start tonight.
The next substantive experiment is prepared in docs/NATIVE-HOME-EXPERIMENT.md,
but has NOT run and awaits specific approval. All normal helpers were restored;
HTTP health200 verified. Temporary permit/capture markers and diagnostic timer
removed. Owner's last-HDMI startup setting remains unchanged.

Latest owner confirmation: after a cold power cycle, read-only storage reopening,
and direct-file retry, **launcher and Netflix both work**. Exact stored file bytes
survived power loss; reliable first launch and TV-only Home/autostart are still
unresolved. Do not repeat installation or claim full Home replacement.

## Objective and user preferences

Install the launcher and playback on the owner TV; replace Vizio/Walmart Home,
ads and startup without this PC. PC-assisted prototypes do not meet that goal.
Owner expressly requested saving all progress **and continuing**. Do not ask
readiness for routine tests. Ask for physical cooperation, feedback or missing
information when needed. The TV is the PC monitor: **Input → HDMI-2** returns here.
Switching to HDMI closes the diagnostic/modal and can interrupt a timed test.

TV W4K65M-1031, firmware 86.920.9.3-2, software 86.920.9.3-2.12.
TV 192.0.2.30:7345; Linux PC 192.0.2.24. Actual ViziOS/Conjure/Chromium Linux
stack observed. Android/APK/ADB is not established. No root or bootloader unlock.

Original boundary: concrete change and recovery method, plus approval, before
flashing, reset, bootloader changes or potentially unrecoverable writes. No
arbitrary configuration keys. Owner later said there is no risk in breaking the
TV and requested continued experimentation; no specific firmware write reviewed.

## Most recent verified progress

1. Local-origin custom execution works. LAN diagnostic navigates to the TV's
   installed Conjure spinner with an `offlineAppUrl` JavaScript bootstrap.
   `retryDelay=0` avoids the spinner's default three-second delay. Direct SCPL
   launch URL embedding this JavaScript was rejected HTTP400; browser navigation
   works. An accepted launch while HDMI is active is not proof of execution.
2. `http://127.0.0.1:12345` is a secure context with native Vizio bindings,
   service workers, Cache Storage, IndexedDB, legacy filesystem API and
   `storage.persisted()=true`. The original LAN-HTTP origin lacked these bridge/
   secure-storage features. No worker was registered or native filesystem opened.
3. A disposable persistent browser file was written, read back exactly, executed
   by rendering its contents, and reopened after closing the test app. Direct
   renderer-initiated filesystem URL navigation did not unload the document.
4. A real self-contained eleven-app launcher is saved in the TV's browser sandbox.
   The **working candidate uses local REST**:
   `PERSISTENT/owner-tv-home-rest-v1/index.html`.
   SHA256 `8cb842adeb0a46efa693db9ea94392142c772def7f0db63069ad0920a6f32293`.
   It has inline CSS/JS and no external asset dependencies. Native app tiles
   use the TV's own loopback7346 control service. A temporary local credential
   stays only in a TV JS closure; it is not stored or sent to this PC.
5. **Owner verified Netflix visibly opened** from the stored REST launcher in an
   uninterrupted helper-off trial. Controller verified all three PC helpers
   inactive and ports8099/11470 closed BEFORE launch; Netflix API descriptor N3:A1
   observed, helpers held off for another30 seconds then restored. PC OS and TV
   internet stayed on. See `research/reviews/tv-local-rest-native-launch-test.json`.
   Other native app tiles have not been individually verified through this new
   REST path. Stremio still requires the Linux host/engine.
6. The earlier **WAMP variant is not visually verified**: it changed API state to
   Netflix but owner saw black. Original paired HTTPS launch visibly opened
   Netflix. REST alternative subsequently succeeded. Do not turn API state alone
   into a passed UI result.

No physical Home, startup, native registry value, firmware, OEM file or bootloader
has been changed in this native pass. Browser sandbox file creation is not root,
a replacement OS, or native package registration. Cold-cycle readback now proves these files retained their exact bytes. Initial
direct opening after cold boot failed; after read-only initialization the direct
retry and Netflix both worked. Cold-start launch reliability remains unresolved.

## Direct-file test completed

Owner confirms **launcher appears and Netflix opens** after normal paired API
launch of the exact stored REST filesystem URI. This establishes browser-initiated
local-file launch; it differs from blocked renderer navigation. No LAN page fetch
is needed for the launcher itself. Physical Home/startup hook remains unresolved.
See research/reviews/tv-local-direct-launch-result.json.

## Actual native bridge and registry evidence

Function.prototype.toString recovered real JS classes from the running TV,
not merely the old SDK mocks. Sources: `.private/owner-runtime-bindings/`.
Factories connect to WAMP `ws://127.0.0.1:55555`:

- SystemRegistry: exists/get/enumerate read; create/set/update/remove are separate
  writes and have NOT been invoked. enumerate('') returned[]; enumerate('/')
  returned32 branches. Follow only discovered children.
- AppLaunch.appLaunch(appid,namespace,message_str) builds T_APP_V1 and calls
  com.vizio.conjure.appLaunch. Its visual trial failed/uncertain as above.
- Loki exposes message/session/query methods; no client methods invoked.
- VizioTest exposes only terminate; NOT invoked.
- window.appman exposes showTransparent/hideTransparent (system UI overlay),
  not a demonstrated Home routing API. Neither invoked by our probes.

Registry discovery reached `/app/platformorchestrator/appsdatabase`:
`home_provider` get returns `vizios-home`. `apps`, `app_symbols`, `app_aliases`
are JSON strings. Decoded full73-app map: `.private/owner-app-database.json`.
The Home entry is controller=loki, app=home, bundle=bundles/home, legacy N4:A1.
Existing sctv is controller=browser with local HTTP entry. All templates have
ctxId=0/empty request metadata; this may be a diagnostic snapshot. No captured
source proves that writing this registry mirror changes the app manager. DO NOT
blindly replace apps map or home_provider. This registry is distinct from both
SCPL arbitrary KV and vendor-root configuration reads.

Completed metadata reads: appmanager status and debug state machine confirm
native Loki Home and dynamically created browser app IDs; Home package is
v26.08.28.9. Registry cache exposes oobe_currentstate only; multiplexer exposes
spam thresholds. WAMP registration meta listing returns no_such_procedure in
systemregistry realm. Debug branch enumeration and routines list completed;
routines/list is empty. No native Home consumer/registration source recovered.
Cached vendor configurations added no authoritative Home path.

Prepared, NOT RUN native Home experiment: temporarily set the one observed
`/app/platformorchestrator/appsdatabase/home_provider` from `vizios-home` to the
existing `netflix` ID; send SmartCast key; restore original. This tests whether
registry is a real input or a diagnostic mirror. **Awaiting specific owner approval**
because native Home behavior and recoverability after a change are not proven.
See docs/NATIVE-HOME-EXPERIMENT.md. No native registry writes have occurred.

`native_home_policy.py preflight` completed twice through independent launches:
first read baseline and save private backup, then execute restore path with
original value already present, so no set call. Both reported vizios-home. Six
isolated mock scenarios verified read-only modes, refusal on baseline drift or
missing permit, and guarded apply/rollback. Native setter permissions remain
unknown. The first preflight attempt hit our own JS routing error and sent no
policy report; corrected routing then passed. No TV write in either attempt.

## Scripts and repeatable operations

- `scripts/open_native_probe.py --bind 192.0.2.24 MODE` activates SmartCast,
  verifies input and launches selected diagnostic. Requires watcher paused.
  Modes include inventory/bindings/control-read/registry-*; file-* for disposable
  file; home-install/open/test/cleanup for WAMP; corresponding home-*-rest for REST;
  home-direct for exact stored REST filesystem URL.
- `scripts/prepare_tv_local_launcher.py --bind 192.0.2.24 --transport rest`
  builds `web/tv-local-launcher-rest.html`. Do not rebuild casually: installed hash
  must match before timed tests. Installer uses exclusive create; cleanup only
  our exact own directory if deliberately reinstalling.
- `scripts/test_tv_local_launch.py --bind 192.0.2.24 --transport rest` loads
  stored page with15-second one-use native Netflix countdown, stops helpers,
  verifies isolation, reads app state, holds off another30sec if descriptor seen,
  restores helpers in finally. Independent90sec systemd recovery timer is armed
  before stopping anything. Requires lab/engine active and watcher paused.
- `tvctl.launch_stored_launcher()` permits one exact sandbox URI; ordinary
  tvctl.launch still permits explicit HTTP(S) only. No general file URL support.
- `scripts/save_checkpoint.py` archives code/docs/public reports and writes a
  private evidence hash manifest. `.private/checkpoints/latest.json` points at
  latest archive. Raw private evidence stays in place; this is not a whole-machine
  backup or TV firmware dump. No git identity/commit/upload configured.

## Services, control and recovery

Last known: all three normal helper services restored active; direct-file test
and initialized cold-cycle retry visually confirmed. Diagnostic recovery timer
canceled after restoration. Temporary capture and policy permit markers removed.
Inspect live state; timers expire. Starting watcher does not launch on an
already-existing state. Current physical Home redirect still opens the OLD
PC-hosted page. Do not claim it now launches the stored candidate.

Dedicated SmartCast key verified: PUT/key_command/ KEYLIST CODESET4,CODE3,
ACTION KEYPRESS; readback SMARTCAST. Generic Home and accepted app launch can
leave HDMI active. Helper handles input activation. Do not guess input codes.
Ordinary input setter currently read-only/rejected. Physical Input→HDMI-2 escape.

Restore normal PC prototype:

```bash
systemctl --user start vizio-stremio-lab.service vizio-stremio-engine.service vizio-stremio-watch.service
```

Then stop only our outstanding diagnostic recovery timers, verify three active
and HTTP8099/health200. Temporary GET markers exist only while
`.private/native-capture.pending` exists; remove it when diagnostic work ends.
Exact own browser cleanup modes exist; never clear all browser storage.
No factory reset required. Ordinary unplug/reconnect restored malformed API state
before the local files were written. Their power-loss retention is now verified,
while reliable first navigation after cold boot is unresolved.

## Earlier prototype / remaining limits

Owner verified adapted Stremio Web playback, licensed raw torrent sample,
video/audio, pause, seek, fullscreen, captions, Back, remote keyboard/search and
Torrentio result. Eleven configured add-ons imported privately. Full current
Stremio frontend and torrent/transcode engine need PC. No TV-native engine install.
PC-assisted eleven-app launcher and Home/wake redirect work; OEM visible2–3sec
before redirect. Earlier red-OFFLINE test proved that original prototype could
neither open apps nor return Home without helpers; new saved REST candidate is a
separate implementation with Netflix test above. Wallpaper caused arrow lag and
remains disabled. Viewing Data Off/Limited Ad Tracking On read back; not proof of
all telemetry stopped, OEM deletion, or account-free initial setup.

Vendor config says debug false, SSH false; no services enabled. External debugger
ports9555/9222 refused; loopback fetch TypeError ambiguous. /install GET500 does
not prove POST absence; no injection submitted. Vendor localassets file opaque,
not decrypted firmware. Native plaintext service binaries/filesystem not acquired.
Do not install Ghidra just to analyze an opaque file. SDK byte identity with
1030 research is component evidence, not whole-model/bootloader compatibility.

## REA and evidence

REA6.8.0 user-wide installed and actual tools callable; MCP integrations preserved,
no restart needed. Node:
`/home/your-user/.local/lib/nodejs/node-v24.22.2-linux-x64/bin/node`.
Skill `/home/your-user/.agents/skills/reverse-engineer-anything/SKILL.md`.
Last full export `.private/rea-native-checkpoint-evidence.json`,13records,
223885384bytes, mode0600. Bridge analysis parent
`ev_b1fd97073600b8e97e3968bb60e5ab66685d89d9b1d3491a379fc374554ce80e`;
3classes parsed, graph partial,384semantic unknowns. Other hashes/Evidence IDs
in review JSON. Do not repeat identical large analyses or mistake static source
for runtime execution. No native binary session opened.

Credentials, configured add-on URLs, raw configs and registry values stay ignored
under `.private` (0700 directory,0600 files). Never dump raw config or profile URLs.
Original Codex backup:
`/home/your-user/.codex/backups/before-rea-20261101T195527Z/config.toml`.

## Latest cold-cycle follow-up

Owner completed full off/unplug30s/reconnect. Preexisting TV startup setting
returns to last HDMI (owner configured it previously); we did not change it.
Initial direct-file attempt did not visibly open launcher. BEFORE any reinstall,
`home-open-rest` read the existing file and reported exact original SHA256, no
error. This verifies file retention across cold boot. It does not prove cold
startup navigation works. No files reinstalled. Owner confirmed the second `home-direct` after read-only
browser/storage initialization displayed the launcher and Netflix opened. Possible
initialization or startup timing issue; exact cause unknown.

WAMP Meta check completed: registration list returns no_such_procedure; dealer
and broker roles exist, advertised call_timeout/testament/progressive features.
Registry version reads identify home v26.08.28.9. Cached vendor configs added no
authoritative Home source. Metadata-only modes registry-debug-names, registry-home-routing and
registry-manager-state completed. No native registry value changed.
