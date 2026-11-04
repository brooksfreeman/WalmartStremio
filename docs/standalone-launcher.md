# Standalone launcher investigation

Requested November 1, 2026: keep the custom Home usable with no PC, even if
Stremio playback still needs another device. Model W4K65M-1031, firmware
86.920.9.3-2. This remains an open investigation, not a demonstrated installation.


**Latest November 1 update:** TV-local Chromium sandbox files have now been
written, read back exactly, and executed. A real eleven-app launcher is saved
there. Direct WAMP launch changed API state to Netflix but owner saw black;
original paired HTTPS method still visibly works. A TV-local REST launcher is
saved and Netflix visibly opened in its uninterrupted helper-off trial. No
physical Home, boot entry, native firmware or registry value has changed.
See [current handoff](RESUME-HERE.md) for the newest state; earlier negative
storage observations below apply to the original LAN-origin prototype.

## Established observations

- The interface executes in the TV's Chromium webview; it is not mirrored HDMI.
  The current implementation fetches files from Linux, sends native-app actions
  to the Linux HTTP helper, and relies on a Linux watcher for Home/wake launch.
- Owner device information reports ViziOS, Conjure, Chromium libraries, SCPL,
  LOKI, local bundles, systemregistry, and storaged. The observed stack supports
  the Vizio Linux/Chromium interpretation; no Android TV launcher, APK installer,
  or ADB modification path has been established. A reported binary name such
  as sshd is not proof that a service is accessible or that we have login access.
- The research repository provides extracted JavaScript, not a complete source
  tree and installation/recovery method for this TV's firmware. Modifying a copy
  of JavaScript on this PC does not replace the installed TV files.
- Its LOKI bundle research identifies local ZIP/XML bundles and a filename hash
  check, but explicitly did not identify a writable installation path. Arbitrary
  KV configuration persistence is not proof of a local app or boot-time entry.

## Required tests and missing evidence

1. **Completed on owner TV:** read browser feature availability and the two known local scfs resources
   (`/scfs/manifest.json`, `/scfs/cl/js/vizio-companion-lib.js`) from the owner TV.
   `web/local-runtime.*` fetched both with HTTP 200 as inert text only. It did not
   load/execute the SDK, fetch an internal credential, register a worker, write
   browser storage, or call a privileged API. The report endpoint admits only
   the TV with the exact local Origin and saves under ignored `.private`.
2. **Partially reviewed:** owner-specific code/resources for storage, normal native app control,
   local installation, Home binding, and boot entry. Do not confuse source
   readability, transient page execution, browser storage, or installation.
3. **Completed: current PC dependency confirmed.** A repeat used a red OFFLINE
   banner, explicit closed-port checks for 8099/11470, and all three helpers
   inactive. The owner reported that no app opened and physical Home stayed on
   OEM Vizio Home. The independent recovery timer restored the helpers; health
   and service status passed. The first ambiguous pause is superseded by this
   result (`research/reviews/pc-disconnect-repeat.json`).
4. Cold-start operation requires separate evidence: a locally retained app and
   a TV-side launch path that runs without Linux after reboot/Home. A surviving
   in-memory screen is not sufficient. No such boot entry has been established.

Normal offline-web caching is also a separate hypothesis. Service workers
require a secure context, as described by [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API).
The current page is plain HTTP on a LAN address. Measure the actual TV's feature
availability rather than assuming it can install a PWA or retain an origin.
Even working offline caching would not itself intercept physical Home.

## Owner-TV runtime and source results

The probe observed `secureContext=false`, service worker unavailable, Cache
Storage unavailable, IndexedDB available, filesystem picker undefined, and no
preloaded `window.VIZIO` or `window.VIZIO.launchApp`. These are properties of
this current LAN-HTTP page, not a claim that the entire TV lacks storage.
Results and hashes are in `research/reviews/owner-tv-local-runtime.json`.

Both known resources were readable cross-origin. Manifest bytes: 1,507;
companion SDK bytes: 299,679. The local manifest advertises companion library
6.0.2-2636.9999. Actual captured SDK SHA-256 is
`f946f440d9c3baf57121e364677d636bb559623457441b0ff3f41f061b610ef3`.
The manifest's CL hash identifies its bundle, not necessarily this one JS file;
do not compare those unlike objects as an integrity check.

REA analyzed the captured owner SDK as inert source. Parent Evidence:
`ev_90ee4c8e260a93d5846bf89e8febdda686430a24ee6419d273373f484ac8a082`.
All selected JavaScript parsed, but semantic coverage is partial at the retained
node ceiling, with 14,716 semantic unknowns. Summary is in
`research/reviews/rea-owner-sdk-summary.json`; the complete exported bundle and
owner source remain private. Partial static coverage cannot prove a feature absent.

Direct inspection found `launchApp` calling the authorized SCPL client. That
client obtains an internal auth/session token, including a fallback request to
`app/get_auth_token`, then calls `app/launch`. The SDK also exposes store reads
and writes, but no demonstrated local app installation or cold-start write path
was found in this bounded inspection. The SDK has **not** been executed or its
internal credential requested. Executing it would be a distinct credential/access
boundary review, not merely a harmless replacement for the existing PC endpoint.
Even local native-app launch control would leave persistent storage and Home/boot
launch unresolved.

## Change boundary

Read-only inspection and reversible page tests continue within the requested
scope. Enabling privileged TV services or debug modes, changing credential/access
boundaries, or weakening browser/network protections requires a concrete plan,
scope/exposure, recovery method, and user approval first. Firmware flashing,
bootloader changes, resets, and potentially unrecoverable writes retain the
original approval requirement. No such changes were made in this pass.

## Wallpaper

The owner-selected `/home/your-user/Pictures/wallpaper.jpg` is copied unchanged to
`.private/launcher-wallpaper.jpg` and served only by an exact allowlisted route.
It is not uploaded, committed, or served as part of a Pictures directory.
CSS initially used a cover crop, a contrast overlay, and translucent tiles. The
source hash is recorded in `research/reviews/launcher-wallpaper.json`. Browser
preview passed. After the helper-pause test, the owner reported delay specifically
when arrows moved between tiles and asked to remove the image for comparison.
The stylesheet now uses a solid background and no image reference; other
navigation behavior is unchanged. The original and private copy remain untouched.
The owner then confirmed arrows were responsive with the plain background.
Removing the image resolved the observed lag in this comparison; the precise
decoder/compositor bottleneck was not profiled. The wallpaper remains disabled.

## Repeat dependency test

The first pause was inconclusive. The completed repeat used
`?dependencyTest=1`, a visible helper health indicator, four-second app-request
limits, and verified closed listeners while all helpers were inactive. The owner
reported no native app opening and no custom Home return during the red OFFLINE
window. Recovery completed automatically. This proves the current implementation
requires the helpers; it does not prove every TV-local implementation impossible.

## Owner configuration and updater source

Using only the existing normal PIN-paired credential, read-only
`PUT /app/config/get_properties` requests succeeded. Device KV reads via
`/app/store/get` are a separate API; null KV values do not indicate missing vendor
configuration roots. No store/configuration writes or internal-token requests ran.

`VIZIOApps` lists `sctv` as namespace 2/app 1, with entry
`http://127.0.0.1:12345/scfs/sctv/main.html`. `AppMigration` maps N2:A1 to namespace
4/app 1, matching the observed OEM Home. The System UI entry is
`/scfs/system-ui-app/index.html`; the earlier main.html 404 used a different path.
`SmartCastHome` also points at the sctv entry, declares prod mode, and identifies
an encrypted vendor local-assets artifact. Its private response includes sensitive
fields and must not be shared. No config value was changed.

The captured SCU `js/dlm.js` is an updater UI, not an established custom-app
installer. It references update-start/status and reboot calls. Those actions
were only read as text and never executed. REA parent Evidence:
`ev_5c9b411a976c8340ca9b9712766d64447d08b8814ca09e0c67e8df80f266c010`.
REA parsed its JavaScript; inline scripts in the entry HTML were not analyzed by
REA and were inspected manually. The configured sctv entry and referenced application script were subsequently captured as text; see below.

## Firmware/source inspection boundary

The captured owner companion SDK is byte-identical to the author's extracted
companion-lib.js (299,679 bytes, SHA-256 above). This validates that one shared
component, not whole-firmware or bootloader compatibility between 1030 and 1031.

The upstream [OTA appendix](https://github.com/vindeckyy/smartcast-backdoor#appendix-a-ota-firmware-container-format)
describes an RS512-signed, AES-encrypted update container. It reports parsing
and signature verification, not decrypted firmware, an extracted device key,
or acceptance of modified firmware. These remain author-reported findings,
not an owner-TV flash test. Even obtaining decrypted contents would not itself
prove a modified image could pass signature checks. No reviewed, model-specific
custom image or recovery method is available in this project. No update image
was flashed and no firmware key or privileged credential was requested.

## Follow-up Home source capture

Owner authorized continuing read-only tests without readiness prompts on November
1. Ask when feedback/physical interaction is needed; the original approval boundary
for firmware/reset/bootloader/unrecoverable writes still applies.

The configured sctv entry, System UI index, and their main JS files returned HTTP
200. Their exact paths, sizes and hashes are in
`research/reviews/owner-home-source-capture.json`. The sctv source-map URL returned
404. AppMigration ties N2:A1 to N4:A1, but is not proof that the legacy sctv JS
renders the current native LOKI Home bundle. The distinction remains unresolved.

REA parent Evidence for the two main JS files:
`ev_f9297eacf59f1aef51ebd6362f15c9fc4b4257fc7f6c6d19167132a3dc78f748`.
Both parsed; semantic coverage is partial at configured ceilings, with 30,259
retained semantic unknowns. Full Evidence is private; summary is in
`research/reviews/rea-owner-home-summary.json`. The separately captured worker was
manually inspected. It handles data messages and IndexedDB and has install/activate
handlers; no fetch event handler was found in that file. A service worker's
presence therefore does not demonstrate an offline cached Home implementation.
No worker or downloaded TV script was executed or registered by our probe.

[Vizio's public Conjure launcher](https://vizio-pm.s3-us-west-1.amazonaws.com/conjure-launcher.html)
was fetched as inert source. It pairs, then requests a URL launch with namespace
4/app 17. It contains no ZIP installation flow. We did not test app 17 on this TV.
[TV Labs](https://docs.tvlabs.ai/platform/platforms/smartcast) documents ZIP
sideloading on its developer sessions. The reference app's
[developer instructions](https://github.com/socialvibe/truex-ctv-web-reference-app/blob/develop/platforms/Vizio/README.md)
distinguish retail URL launch from vendor-enabled debugging. These documents do
not establish local installation or Home replacement on this owner's retail set.

Current result: no validated writable executable location, persistent custom-app
registration, or TV-side cold-start/physical Home override. Readable source is
useful evidence but does not grant an installed-file write path. The PC-dependent
launcher remains usable; an on-TV replacement has not been achieved. This is a
bounded result, not proof that every private mechanism is impossible.

## HDMI recovery correction

Follow-up tests found current_input marked ENABLED=FALSE/HIDDEN=TRUE. The ordinary
menu setter returned FAILURE, as did launching the observed N0:A2 HDMI descriptor.
Legacy Input key mapping (7,1) was accepted but did not select HDMI-2; after Home
it reached WatchFree. No additional input-code guessing is built into recovery.
The launcher TV/HDMI button now gives explicit physical Input → HDMI-2 steps
without attempting a misleading switch. The helper checks the read-only flag
before Home or a menu write. Earlier broad owner feedback did not individually
verify this shortcut and is superseded by this observed failure.
