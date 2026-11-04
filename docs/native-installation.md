# Earlier native installation investigation — historical context

The November2 objective now prioritizes modifying actual installed Vizio Home,
not installing a separate launcher or resuming playback work. The current
evidence/plan is in NATIVE-HOME-INVESTIGATION.md. The dated findings below are
preserved history; later Loki runtime evidence supersedes assumptions that the
legacy SCTV entry was the active Home renderer. A Loki controller does not by
itself establish implementation language or a machine-code-only UI.

## Earlier installation questions — superseded as the active plan

1. Obtain the relevant native service binaries/filesystem from the owner build,
   or find a supported installation route. Existing readable web assets do not
   include the native app installer, native Home bundle loader or boot policy.
2. Analyze storage permissions, package verification, registry persistence,
   physical Home handling and startup using those actual artifacts.
3. Establish an independent recovery route and backup before changing persistent
   native state. Do not guess store keys or treat accepted writes as proof of use.
4. Install and test with PC helpers unavailable, then test Home and cold start.
   Torrent/codec independence and DRM/native-app behavior require their own tests.
5. Verify ads/login avoidance and network behavior; a clean page is insufficient
   evidence of removed telemetry.

## November 1 native investigation

Using the normal paired credential, vendor ApplicationFramework reads succeeded.
Actual ChromiumSettings: DebugEnabled=false, DebugPort=9555. PlatformDebugSettings:
SSHServer=false, Journald=false. ViziOSPlatformSettings environment=production.
No setting was changed. Neither documented debugger port, 9555 nor 9222,
accepted a connection. Device KV debug values were null; this is a separate
namespace from the successful vendor-root reads.

Read-only GETs of /install and /scpl/install returned identical HTTP 500 bodies;
/static/install.html returned 404. This does not prove POST functionality absent.
No package, command injection, service enablement or debug override was submitted.
The reviewed updater's metadata GET returned IS_AVAILABLE=0; ULI metadata timed
out. No start-update, override-group, reboot or firmware-write request ran.

A complete 11,398,288-byte localassets .enc object, referenced by this TV's
configuration, was downloaded directly from the vendor CDN onto the PC. SHA-256:
7b333214c507651d8e73724fe9898a3a3dd2214bbf3fd92a4138a31d3c7c2a87.
It is opaque/high entropy and not a valid ZIP or an ELF at offset zero. Entropy
alone is not proof of encryption. No decryption or native-code extraction
succeeded, so installing Ghidra solely for this opaque file would not yet help.

The owner completed an ordinary unplug/reconnect cycle. After activating the
SMARTCAST input, the native source capture arrived; the owner confirmed it
appeared and saved. An accepted launch while HDMI is active is not evidence
that the page executed. Dedicated remote key CODESET=4/CODE=3 switched to
SMARTCAST with readback; no persistent setting changed.

The full findings/limits are in
`research/reviews/native-installation-investigation.json`.

## External-source limits

The published [1030 research](https://github.com/vindeckyy/smartcast-backdoor)
provides no demonstrated native shell, filesystem dump, installer write path or
bootloader unlock for the owner's 1031. Its report of a UART is not proof of an
unlocked shell or firmware-signing bypass on this board.

Another [firmware research plan](https://github.com/noktirnal42/VizioRemote/blob/main/VIZIO_FIRMWARE_RE_PLAN.md)
concerns WHD32M-1030 and contains assumed Android partitions/ADB commands.
Those assumptions are not evidence for this TV and were not acted on.
The [published 5583 source candidate](https://github.com/opensource-vizio/5583_FUR5.0_OpenSourceSoftware)
is a different platform release and is not a model-matched build/install recipe.

No persistent native installation or OEM removal is claimed.

## Control-service diagnostic follow-up

Owner reports the PC desktop and confirms physical Home opens OEM Home normally.
Power, version and device-info reads succeed, while app/current has returned a
generic HTTP 500. current_input VALUE was sometimes an integer or app descriptor,
and state_extended APP_CURRENT sometimes an integer, all violating expected
schemas. Capture/launch acceptance therefore cannot be trusted as execution.

Pausing the PC watcher and allowing a quiet interval briefly restored a correct
N0:A2 HDMI app descriptor. Another launch attempt was accepted but did not produce
a source report, and malformed state recurred. This is not proof of a race or a
specific cause. The watcher was paused again with an independent ten-minute
restore timer. The owner was asked to perform a normal menu Restart TV (no factory
reset). No reboot, install, service-enable or persistent-write API was sent.

The next source capture has opt-in, private page/script access markers to tell
whether the TV actually fetched the probe. They omit query strings and normal
launcher/media activity and remain disabled unless native-capture.pending exists.

## Native bridge and next diagnostic

The owner completed the ordinary power cycle and source capture. In the
LAN-origin modal `navigator.vizioConnection` was undefined. The installed Conjure
spinner accepts an `offlineAppUrl` and redirects without a scheme check in the
captured source. Direct SCPL URLs embedding our bootstrap were rejected with
HTTP 400. A LAN diagnostic navigating to the spinner successfully ran our
bounded probe in `http://127.0.0.1:12345`, verified by a TV-only exact-Origin
report. There the bridge is an object, secure context is true, and browser
storage APIs are available. This is actual local-origin execution, not root.

A disposable file was exclusively created in Chromium's PERSISTENT browser
sandbox, written and read back exactly. It executed when read into the local
page. Direct top-level filesystem URL navigation did not unload the page.
After closing the app, an inline loader using only the TV's local file API
reopened the stored page and produced a fresh execution report. This is a
persistent-browser-file result; no full power-loss persistence or TV-side
Home/startup hook has been established.

The SDK's local token bootstrap and capabilities GET were then tested. The
short-lived credential stayed in a TV-only closure, was not stored or returned
to the PC, and was used only for that read. Native navigator.vizio connection
factories and vizioSystemRegistry methods exist, but no registry/native method
has been invoked and their actual call contracts remain unknown. No firmware,
bootloader, worker registration, native setting or installed OEM file changed.
See `research/reviews/owner-local-origin-results.json` and
`research/reviews/owner-local-storage-results.json` for exact observations.

REA reanalyzed the same pinned SDK with a larger semantic allowance for this
question. Parent Evidence:
ev_1aef65f978ba894463c609f0a3d70721231961e6a5d421e448bbef8bd444ffb2.
No per-file semantic node truncation is reported in that result, but alias
selection and semantic unknowns remain. The exact vendor API seed had no graph
match; this is a tool coverage limitation, not absence of the directly observed
source call. The analysis did not recover a native implementation or demonstrate
installation, file access or a Home override. See
research/reviews/native-ipc-source-analysis.json.

## Saved launcher trials (latest)

Two self-contained launcher files now exist in our Chromium sandbox directories
`owner-tv-home-v1` (WAMP) and `owner-tv-home-rest-v1` (local REST). Both read back
with matching build hashes. The WAMP test stopped all three PC helpers and
closed their ports; API state became Netflix N3:A1, but owner saw a black screen.
Original paired HTTPS launch visibly opened Netflix, so WAMP API state alone
is not a working native-app UI result. An uninterrupted local REST trial then visibly opened Netflix, confirmed by
the owner. All three helpers and both ports were verified off before launch,
and remained off through the loading interval. No Home/startup/registry/OEM changes made.
Source, findings and exact next steps are in docs/RESUME-HERE.md and checkpoint
archives under ignored .private/checkpoints/.
