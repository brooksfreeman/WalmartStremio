# Resume here

Updated November 3, 2026 (America/New_York). Project:
`/path/to/WalmartStremio`.

## November 10 public update

Desktop Overview adds **Subtitles on by default**. The boolean preference stays
local and is read by the TV frontend when each stream starts. Rebuild the frontend
and reopen Stremio to use it. Manual choices remain valid for the current stream.
Live TV playback validation of this new behavior is still pending.

Desktop Network adds a four-part TV IPv4 editor. It verifies the existing paired
TV certificate, updates the controller and engine access configuration, and
preserves the prior running/stopped service state with backup/rollback handling.
This does not pair a new TV or change the PC address. Live IP migration was not
performed during this publication review.

Publication validation: 19 Python regression tests, subtitle-hook fixture tests
and isolated real GTK checks passed. No TV or hosting-service changes were made.
The add-on manifest client also identifies itself with an application User-Agent.
See INSTALLATION.md, DESKTOP-CONTROL.md and FILE-GUIDE.md for current instructions.

## Current objective and next action

**Publication preparation, November3:** created
`/home/your-user/Documents/Stremio TV - GitHub Publishing and Setup Guide.md`
and a separate `/home/your-user/Documents/stremio-tv-github-ready/` source snapshot.
Guide includes owner upload steps and full public setup README. Export uses35
explicit public app/source files, portable awake unit, notices and tests; no
private state, generated machine-specific service units or old research copied.
Clean pinned upstream plus preparation script reproduced current frontend source
twice using existing dependencies; six tests passed from export. No second-PC
end-to-end install or GitHub upload. Publisher still needs repository URL and
license decision for own contributions. Export is a snapshot, not live linked;
continue normal hosting from original project. Hosting left stopped.

**Current objective:** PC-hosted Stremio, triggered by the **physical WatchFree
button**, with desktop controls and automatic server startup. Home stays normal.
Owner explicitly corrected the earlier Home-button choice, then physically
verified WatchFree opens Stremio. Native Home/firmware/hardware work is parked.

Replacement W4K65M-1030 at192.0.2.57, firmware86.920.9.3-2/software86.920.9.3-2.12,
separately certificate-pinned and normally PIN-paired.
Old identity/credentials saved privately under hardware-identification/replacement/
before-switch-*. Never reuse its browser settings/files as replacement evidence.

**November3 overlay follow-up / tvbuild12:** owner still saw the standalone Home
box after build11. Reproduced its failure in actual isolated Chrome: React Router
pushState can change the hash route without hashchange, leaving the catalog link
mounted over video. Removed standalone floating Home creation entirely on all
routes. Auto-hiding player-bar Home remains. Rebuilt successfully; all five
Chrome catalog/pushState route checks have zero floating links and the compiled
main.js contains no tv-clean-home. Prior route-only fix is superseded.
Owner explicitly chose **Keep hosting stopped; I’ll reopen later** after the
build12 update. Reload and owner visual confirmation pending. Existing live
page cannot receive rebuilt JavaScript without reopening. See
research/reviews/home-overlay-removal-validation.json.

Desktop panel now has **Overview** with two-minute live receive/send bandwidth
chart and **Add-ons** with masked URL field, Install, Refresh from TV and Remove.
Supports HTTP(S) manifest URLs and stremio:// links. Backend validates manifest,
uses nonce/expiry/TV identity and origin/source guards; exact pre-change add-ons
backed up privately. TV core confirms install/removal before reporting success.
Live read/install/remove tested using own local sample add-on; all original7
add-ons (including Torrentio) preserved. Protected built-ins cannot be removed in
UI. URLs/state/backups remain private; public CLI summary contains names/version/
hashed selectors only. No provider-specific credentials baked into source.

Bandwidth uses ss TCP payload counters for the host/engine cgroup process IDs,
including children; explicitly excludes other apps, local health polls and UDP.
Never fall back to host-wide counters when units are inactive. History stays in
RAM. Actual server traffic detected during TV tests; rates are estimates because
short-lived sockets may close between samples. Units Mb/s, not percent link use.

Six local regression tests, isolated real HTTP origin/nonce tests, Chrome checks,
webpack and live TV add-on operations passed. See controls-v2-live-validation.json.
Source rollback build and original service state saved in private controls-update-
backup/. Services were initially stopped but enabled; started for live validation
then owner explicitly requested **Keep it stopped** after checking controls.
All three hosting services are now intentionally stopped; boot enablement remains
on. Clean control-triggered stops were confirmed, not crashes. Panel labels this
Server stopped and Start / repair brings it online. No pairing/privacy/power changes.
GitHub publishing was mentioned as a future plan, not authorized upload; nothing
was uploaded. Continue source/private boundary. Tests: python3 -m unittest discover
-s tests -v. User clarified “autofill” meant desktop URL-based add-on management,
not automatic server-address changes.

**Completed server setup (earlier validation):** all three server/engine/watcher services tested active,
enabled at boot. User lingering enabled; system Wi-Fi autoconnect verified.
Desktop and Applications entry **Stremio TV** opens scripts/tv_control_panel.py
(GTK3, already installed). Real off/on shortcut and boot-preference tests passed;
server stayed online through shortcut-off. UI rendered/visually reviewed; desktop
entry validated and launched. No full reboot test performed. See DESKTOP-CONTROL.md.

WatchFree physical observation: SMARTCAST + namespace4/app3014 (transient1/51
ignored), followed by watcher launch to browser4/3001. Owner confirmed Stremio
opens. Home redirect=false; watchfree-shortcut.enabled=true; startup.screen=stremio.
WatchFree detection is an app-state redirect, so opening WatchFree by other routes
also redirects. Initial state, HDMI/native-app exclusions, pause, cooldown and
legacy behavior checked in10 isolated scenarios +5 config transitions. Commands:
configure_home.py enable-watchfree / disable-watchfree. WatchFree toggle off in
the desktop panel also stops/disables observer, preventing wake automation too.

**Torrentio:** copied only its existing configured descriptor from the local PC
profile using import_addons.py --only-torrentio. New TV browser client verified1
installed descriptor and acknowledged completion. Old1031 add-on records preserved
under private replacement/retired-1031-addon-import/. New pre-import TV backup and
completion in private root. No credentials/account copied; URLs not printed.

**No sleep:** server_awake.py apply disabled GNOME inactivity sleep, set installed
Xfce4.18 inactivity alarms to never, and enabled vizio-stremio-awake.service with
sleep:idle block inhibitor. Verified active inhibitor and readbacks. Prior settings
in private server-power-before.json; restore helper documented. Desktop chassis3;
no lid policy changed. Boot service retries not rate-limited while LAN starts.

Validation reports: research/reviews/{replacement-watchfree-shortcut,
desktop-control-validation}.json. Earlier statuses online/enabled (now manually stopped per above); no reboot,
firmware or native Home-registry write. DHCP changes remain outside this setup:
addresses currently fixed in prepared units/allowlists/TV server preference.
PC-connected HDMI port unconfirmed; previous1031 HDMI-2 must not be claimed for
replacement (photo/API selected HDMI-3). Launcher now gives generic physical Input
instructions. Do not power-cycle TV/PC just to repeat successful tests.

Following native investigation sections are retained historical evidence, not
the active work plan. Mainboard underside inspection is no longer requested.

## Latest observation — mainboard photos, UART unidentified

Owner opened the rear cover and supplied ten interior photos. PCB reads
**715GF461-M0B-T01-004I** (0/O glyph ambiguous). No UART pinout or voltage
established. CN8601 is unidentified; nearby C7xx pads are component footprints.
Bounded exact-board searches found no matching schematic. Originals and hashes
retained privately; see docs/MAINBOARD-IDENTIFICATION.md. No powered-open test,
hookup, removal or TV writes. Actual Home acquisition remains unresolved.

## Latest follow-up — Qterics implementation and21-key trial

Read docs/QTERICS-DECRYPTOR-FOLLOWUP.md first. Found unixtract at commit
aadba866ea47ed9506ffe130a8558bb9147ee968: RSA-OAEP-SHA1 unwrap44bytes and
AES128-GCM with16-byte tags, consistent with supplied UTV framing arithmetic.
Tested21 distinct published keys through reviewed local Python reader: zero match,
no actual GCM/plaintext output. Synthetic matching-key success and damaged-tag
rejection passed. Do not repeat unchanged. No upstream binary built/run or package
install; ordinary source analysis required no REA/native engine this pass.

Source/key identities and reviewed files in.private/unixtract/. Keys are public
upstream material, never owner credentials. Public provenance and fingerprints in
research/reviews/unixtract-{qterics-review,key-trial-verified}.json; initial trial
also retained. Maintainer issue5 names id.json/idpwe on a different Novatek
platform: not a verified owner-MediaTek path. Seven existing archive indexes have
no relevant named material; no archive scans repeated. Asset x509_pub.bin is a
PEM public-key file, not an X509 cert object; exact-byte hash matters. No key file
acquired. No guessed native paths, embedded credentials or native decrypt writes.

Current blocker: native file read/export, matching key or already-unpacked Home.
No software-only route established. Owner now confirms relevant mains-electronics
experience. Mainboard photos are now reviewed; see docs/MAINBOARD-IDENTIFICATION.md. No measurements, powered-open testing,
connections, shield removal or writes. No connector/voltage/shell/readout/recovery
fixture known. No generic UART promise or adapter purchase.
No TV operations, service changes or native writes; previous service state is
historical, not rechecked. Need new evidence before another acquisition attempt.

## Supplied USB firmware inspection

Read docs/UTV-FIRMWARE-REVIEW.md and research/reviews/utv-mg1352-inspection.json.
Rootmg1352-86.910.19.2-1F.utv is533,546,571bytes; SHA256
5eccf0374f7d89fb8f33ed763338095a7d58ccd202dde95abb198d9f78b1e9a1.
JWT/leaf-to-intermediate signatures verify, but no independent root/source trust,
plaintext verification or Home extraction. Owner explicitly confirms compatibility;
source URL not supplied. Version differs from installed86.920.9.3-2 and audience
does not include it; don't claim newest, incompatible, or safe downgrade from
those facts alone. USB instructions are reference, not permission to install.

REA entropy covers whole file (8142blocks); saved4-record bundle
.private/rea-utv-inspection-evidence.json. Header in.private/utv-mg1352/. No engine,
Ghidra, Binwalk install, code execution, TV request or service change. Avoid repeating
analysis unchanged. Payload layout arithmetic differs from repo's other UTV:
actual-minus-declared=1632=102×16bytes, not verified32-byte headers. Cipher/framing
unknown. No speculative decrypt or plaintext claim.

Manufacturer source's certificate-derived AES-CBC asset decryptor is a different
envelope, not a demonstrated UTV unwrap. Existing archive indexes have no exact
x509_pub.bin artifact. Need an evidenced decryptor/key or unpacked Home resource;
no source credentials, TV decrypt writes or guessed certificate trials performed.

## Exterior hardware identification

Owner has now removed the TV from the wall and supplied a rear-label photo.
**Actual label model65S4V1** supersedes the earlier listing-based65S4V4 assumption.
Internal model remainsW4K65M-1031. Transmitter FCC ID2AJVQ-MWH647B is for a Wi-Fi/
Bluetooth module; its public documents do not identify the TV mainboard/UART.
See docs/RETAIL-HARDWARE-IDENTIFICATION.md and private hardware-identification/
photo + identity.json. Never transcribe/delegate serial/barcodes/raw photo.
No adapter owned. Interior photos now identify the PCB, but no pin map or usable
readout procedure is established. Rear cover is open; no TV operations or service changes.

Actual installed Home acquisition remains unresolved. Resume only with a specific
new software artifact/export reference or model-matched hardware evidence;
do not repeat completed scans or treat the prototype as native Home editing.

Remaining SDK/software pass is now complete. Read docs/SDK-INTERFACE-REVIEW.md and
research/reviews/vendor-sdk-interface-search.json before further work. All4explicit
compiler/relink archives inventoried. ACR includes real Loki/registry headers and
libvsl.so; compiler archives had no targeted headers. No typed Home/file-export
operation found in reviewed interfaces; this is not a proof about all server APIs.
REA portable ELF exports on SDK libvsl.so found1396exports; complete evidence is
.private/rea-sdk-interface-evidence.json (2records). No engine opened, code run,
Ghidra install, native setting write or package install. Prior REA evidence bundles
remain separately preserved. Library/header version equality with TV is unproven.

One source-defined log-status key read returned empty string. Reviewed source
interprets this as disabled. Logging was not enabled, no logs collected and no
Loki session/update command invoked. Public research issues offered no export
route (one returned issue about pre-auth). All3normal helper services restored;
vizio-sdk-log-status-recovery.timer canceled. No TV physical feedback needed.

**Hardware constraint:** rear label acquired (65S4V1; transmitter2AJVQ-MWH647B),
no adapter owned. Mainboard photos have since been reviewed; no UART pinout
identified. Connect nothing from these findings. Assess matching service evidence for a
read-only console/export acquisition route. UART availability, voltage, unlocked
shell and flash readability are unknown. No generic3.3V/115200 instructions or
bootloader/write experiments without exact board evidence and appropriate approval.

Do not repeat completed SDK scans. The1.32L member is gzip despite .tar.xz name;
its initially empty failed inventory was resumed with magic detection. Source
indexes, headers and two inert libraries live under
.private/vendor-oss-5586l-fur92/sdk-archives/. All identities retained.

## Latest investigation — November 2

The four-read Home-resource metadata probe completed on the owner TV. No bundle
locator returned: deployer/active empty string; apps children are list/order
fields; catalog-services children are URL-type settings; live-hero has no children.
A separate three-read catalog test found default=340 string entries; apps/all
exceeded the200000-character report cap and was stopped without raising it;
catalog-url-type was empty. No resource consumer or writable Home edit established.
See research/reviews/native-home-resource-discovery.json.

## Manufacturer archive inspected — latest state

Owner supplied project-root5586L_FUR9.2.tar.gz (6,738,959,096bytes). Both published
checksums match. SHA2565bc7e3646fa6130ce8538cab26046427770560a7c5025d20de75ecb8a6234ea5.
Read docs/OSS-ARCHIVE-REVIEW.md and research/reviews/vendor-5586l-fur92-review.json.
Outer296members, nested ViziOS183,533members and firmware OSS452,384members fully
inventoried. Outer LOKI contains only five fonts. ViziOS has actual OSUpdater
source; selected577files copied inertly, hashes retained. No real Home renderer,
BundleRoot.xml or installed Loki-bundles snap acquired. That initial review left embedded archives unsearched; the subsequent SDK pass
completed three toolchain inventories and the ACR relink inventory. Other nested
dependencies remain unsearched; negative scope stays bounded.

OSUpdater source fixtures separately name Loki engine and Loki-bundles snaps.
Those examples are not installed owner filenames. Source-defined OSU keys led to
seven bounded registry reads: hash/version populated, activeFolder matches a
source path, manifest branch only url, dlm branch only updates whose value empty.
No package URL or full native manifest body. Source/runtime correspondence is
partial, not exact build identity (archive labels mix F/L and9.1/9.2). No updater
commands, source credentials, cloud-manifest POST, build/Docker scripts, Ghidra,
package installs, registry writes or firmware changes used.

**Next acquisition blocker:** actual owner-build Home/Loki-bundles package or
manifest through a confirmed export/read interface, supplied native filesystem
artifact, or explicit download reference. Native file/SSH access not established;
do not guess file-server paths, use fixture URLs or treat GPL build output as a
recovery image. This source review is complete within the stated scope; don't
rehash/reinventory unchanged archives. See saved indexes and source pointers.

Archive stays at original path (git-ignored). Private analysis directory:
.private/vendor-oss-5586l-fur92/; inventory-result.json, nested-identities.json,
{vizios,firmware}-inventory/result.json and selected-source-identities.json map
all retained files. selected-source/rootfs/OSUpdater is ordinary C++ source, not
the actual Home source. Never delegate anything under .private to workers.

All3helper services restored active and health200 verified; vizio-oss-osu-recovery
timer canceled. Native Home unchanged. Recovery scripts/source archives remain
saved. No physical feedback needed for these metadata reads.

External1030 report describes ZIP/XML Loki bundles (BundleRoot.xml); this is not
owner1031 format/path verification. Existing owner SDK command enum exposes
bundle/clearScene/deepLink/registerSessionProvider, not an evidenced export API.
No arbitrary commands or guessed filesystem paths tried.

Do not run the prepared home_provider write experiment as the next step; it
remains secondary, requires specific approval and cannot establish appearance
changes. Rollback was only preflighted against unchanged state.

Current pass rechecked HTTPS capabilities and HDMI-2 state, paused watcher with
independent10-minute recovery, ran the two read-only probes, restored all3helpers
active, checked HTTP health200 and canceled recovery timer. No native registry
write, Home resource replacement or Stremio/launcher development. No live worker
used. Local isolated four-operation harness passed after correcting its missing
mock location variable; actual browser has location and all4reports arrived.

Owner requested no readiness questions for routine tests. Ask when physical
interaction, feedback or missing information is needed. TV is the PC monitor:
**Input → HDMI-2** returns here; switching inputs interrupts diagnostic pages.

CodexSaver: owner reports unsafe direct verifier command execution and private
workspace copying. Do not use affected live paths until demonstrably fixed;
no fixes established in this pass. Continue directly, do not repeatedly attempt
provider calls. Keep active TV investigation/private evidence/native decisions
in Codex. Tooling repair is separate. See docs/codexsaver.md.

TV W4K65M-1031, firmware 86.920.9.3-2, software 86.920.9.3-2.12.
TV 192.0.2.30:7345; Linux PC 192.0.2.24. Actual ViziOS/Conjure/Chromium Linux
stack observed. Android/APK/ADB is not established. No root or bootloader unlock.

Original boundary: concrete change and recovery method, plus approval, before
flashing, reset, bootloader changes or potentially unrecoverable writes. No
arbitrary configuration keys. Owner requested continued experimentation;
no specific firmware write reviewed.

## Preserved browser prototype evidence — not the current product

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
4. A separate self-contained eleven-app browser launcher is saved in the TV's browser sandbox.
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
Deprioritized by the November2 objective clarification; it does not establish
appearance edits or custom-app registration. See docs/NATIVE-HOME-EXPERIMENT.md. No native registry writes have occurred.

`native_home_policy.py preflight` completed twice through independent launches:
first read baseline and save private backup, then execute restore path with
original value already present, so no set call. Both reported vizios-home. Six
isolated mock scenarios verified read-only modes, refusal on baseline drift or
missing permit, and guarded apply/rollback. Native setter permissions remain
unknown. The first preflight attempt hit our own JS routing error and sent no
policy report; corrected routing then passed. No TV write in either attempt.

## Existing tools — use only when relevant to the active Home question

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

Last observed November1, not rechecked in the clarification pass: all three
normal helper services restored active; direct-file test
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
