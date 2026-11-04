# Findings ledger

Updated November 1, 2026. Full Stremio playback now works in an adapted local
build, including a licensed torrent through the Linux service. Full-player
controls, remote search, Torrentio playback, and PC-assisted standby/wake startup
passed owner tests. The TV also serves as this Linux PC's monitor. Independent
TV operation and removal of vendor account/advertising components are not claimed.

## Target identity

| Field | Value | Evidence |
|---|---|---|
| Model | W4K65M-1031 | Owner report, TV User-Agent, authenticated `/state/device/deviceinfo` |
| Firmware | 86.920.9.3-2 | Owner report and deviceinfo `SYSTEM_INFO.VERSION` |
| Software | 86.920.9.3-2.12 | Owner report; not independently queried |
| Last update | October 22, 2026 | Owner report |
| SmartCast | 1.8.1768.1 | TV page User-Agent |
| Webview | Chrome 128.0.6613.194; Conjure 128.1.8 | TV page User-Agent |
| Control API | 3.7.3-2640.0001 | Authenticated deviceinfo |
| Page viewport | 1280 × 720 | TV-side `innerWidth` / `innerHeight` |

Private network address, certificate, identifiers, tokens, and full device
responses remain in `.private/`.

## Stages and evidence

| Question | Status on this TV | Evidence / limit |
|---|---|---|
| Can this chat reach the home LAN? | Verified | Initial HTTPS GET `/system/capabilities` on 7345 returned 403 `REQUIRES_PAIRING` |
| Does normal onscreen-PIN pairing work? | Verified | Owner entered PIN in local Linux dialog; TV confirmed connection; token saved 0600 |
| Authenticated capabilities/device info | Verified | Read-only GETs returned SUCCESS |
| Does NS 4 / app 3001 accept a custom HTTP page? | Verified | API success, page requests and JS beacon from TV, owner saw page |
| Remote arrows and OK | Verified | DOM ArrowLeft/Right and Enter events, color-selection beacons, owner confirmation |
| Leave custom page | Verified | Owner confirmed Home/Return Home works. API returned NS 0 / app 2. This identifier alone does not distinguish TV Home from the PC HDMI display |
| Diagnostic MP4 over remote HTTPS | Failed | W3C-hosted URL produced media error 4 `Format error` immediately, before metadata/frames |
| Identical MP4 over LAN HTTP | Verified | 33.002667s duration; decoded frames and audio bytes; owner confirmed video/sound and controls |
| Seeking | Verified in diagnostic player | Seeking/seeked events and owner report |
| Diagnostic test subtitles | Owner reported working | Track loaded and toggled; authored cues, not embedded subtitle extraction |
| Native Fullscreen API | Failed to complete | `fullscreenEnabled=true`; request callable; no resolution/fullscreenchange observed |
| Fill-TV-viewport CSS layout | Verified | Owner confirmed; local phone photos IMG_4106/4107 show expanded and diagnostic layouts. This is CSS, not native Fullscreen API |
| Unmodified official Stremio Web | Failed playback and remote test | Owner saw “Video is not supported”; Up/Down adjusted volume and other remote controls were ineffective. MIME-hint retry also failed |
| Adapted full Stremio app | Playback verified | Owner confirmed moving video/audio; TV events show HLS decoding up to 1920×1080, audio bytes and no media error. Normal full Stremio interface, not the small diagnostic page |
| Stremio Back from Captions | Fixed and owner verified | Back closes the menu and keeps video onscreen |
| Full Stremio torrent-player controls | Owner verified | Pause/resume, +10-second seeking, visible English test captions, Back, and screen-filling playback all passed after fixes |
| Stremio Browse | First failed; fixed and owner verified | First blank/frozen screen. Works with Vizio view transitions disabled; TV-only JS error also captured, precise relation unproven |
| Stremio setup-dialog navigation | Fixed and owner verified | Explicit spatial focus works. Owner confirmed the server prompt and reported much better navigation; open setup dialogs separately |
| Stremio-format add-on installation | Verified | Owner installed licensed sample; TV fetched meta/stream/catalog resources and played its torrent |
| Existing user add-ons / Torrentio installation | Verified | Imported 11 cached addon descriptors from owner's existing Linux Flatpak profile via standard core InstallAddon actions. TV app state verified all transport URLs present; owner confirmed Torrentio in UI. Account auth and settings were not copied |
| Torrentio's own stream playback | Owner verified on TV | Owner searched “living dead”, selected Night of the Living Dead (1968) / Torrentio, and confirmed video/audio. Direct tool requests remained blocked; no network proxy was built. Import used existing locally cached configuration |
| Remote Search keyboard | Owner verified after focus fix | Initial TV provided no keypad. Added arrow/OK keyboard; typing and Search worked. Fixed reappearance on Down by making OK/click reopen it and keeping the field navigable; owner confirmed result navigation and playback |
| Linux Stremio torrent engine | Bytes verified | Official Service 0.1.22 / engine 4.21.0 parsed the legal BBB torrent; media Range request returned 206 and MP4 bytes. This alone is not TV playback |
| Full app legal-torrent TV playback | Verified after fixes | Owner confirmed moving video and sound with HLS workers disabled and an AAC-stereo service profile. Original MP3 HLS attempt failed; details below |
| No PC required | Not achieved | Current UI is served by Linux. Direct HLS reaches internet media without the Linux engine; raw torrent operation uses an external engine. No native TV torrent engine established |
| PC-assisted automatic startup | Verified on remote standby/wake | Three enabled user services. Watcher saw 0→1, launch API accepted, and owner confirmed Stremio opened automatically |
| Stremio tile on stock Vizio Home | Unresolved; no tile created | Current modal launch does not register an app. Catalog customization is documented, arbitrary-URL pinning is not. See [Home launcher investigation](home-launcher.md); no registry or firmware changes made |
| Separate clean app launcher | Owner reports overall app-launch / Home-return / TV-HDMI flow works | Local-only assets, no ads/analytics. Eleven buttons from pinned official app descriptors. Netflix individually confirmed; follow-up “everything seems to work” did not enumerate each app tried |
| Physical Home → clean launcher | Owner verified PC redirect | Read-only observation distinguished SMARTCAST + app 4/1 from HDMI-2. Watcher redirects only the Home state. Owner estimates about two to three seconds of Vizio/Walmart Home before our page; Vizio Home is still installed |
| Viewing Data / Limited Ad Tracking | Changed and API read-back verified | Normal privacy menu: Viewing Data On → Off; Limited Ad Tracking Off → On. Original values privately backed up; does not establish zero telemetry or system ad removal |
| Walmart prompt / TV ads during tested startup | Neither observed by owner | No sign-in prompt or TV advertisement appeared during the tested remote off/on cycles. Current account state, fresh setup, cold AC boot, and broader daily-use avoidance remain unverified |

## Sample and delivery diagnosis

Big Buck Bunny is © 2008 Blender Foundation, licensed CC BY 3.0.
License source: <https://peach.blender.org/about/>.

First sample: <https://media.w3.org/2010/05/bunny/trailer.mp4>.
SHA-256: `b2ded9ae5a20fa36ca8cec49ef923bffb5e1a51d9e8c1f8336273d2fa9d35ff0`.
ffprobe: H.264 Main level 3.0, yuv420p, 853×480; AAC-LC, 48 kHz,
six channels; 33.002667 seconds. The byte-identical LAN copy worked. This
narrows the first failure to delivery/origin behavior; it does not prove a
particular TLS, CORS, or codec cause. The W3C response lacks
`Access-Control-Allow-Origin`; whether that caused this TV's failure remains
unverified.

Second sample verified in the diagnostic HLS player and adapted full Stremio:
<https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8>.
The playlist has `Access-Control-Allow-Origin: *`; its renditions advertise
H.264/AAC. TV playback was confirmed separately by the owner and TV-peer event
records. The upstream player selects its HLS engine for one exact MIME string;
the local build normalizes HLS MIME variants and uses the tested HLS.js 1.7.4.
The MIME response hint in an otherwise unmodified official app was insufficient.

Raw torrent sample: <https://webtorrent.io/torrents/big-buck-bunny.torrent>.
Info hash `dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c`; MP4 file index 1,
276134947 bytes. Only freely licensed samples are used in these tests.

ffprobe of the torrent's actual MP4: 1920×1080 H.264 High level 4.1,
yuv420p, one stereo MP3 track and one six-channel AC-3 track, 634.533333s.
Those audio tracks differ from the working direct HLS sample's AAC.
The adapted full app initially retained `enableWorker: true`, while the working
diagnostic used `false`. A worker crash was recorded in a blob script; a
source map located the subsequent null-trigger error inside bundled HLS.js.
Disabling workers removed that crash but the Linux reproduction still failed.
Detailed HLS reporting identified `bufferAddCodecError`: SourceBuffer rejected
`audio/mp4;codecs=mp4a`. The owner build now asks the engine for AAC, at most
two channels. ffprobe verified the converted HLS's AAC-LC stereo tracks and
1080p H.264. It then played in the full Linux app without player errors, and
the owner separately confirmed video and sound on the TV. This is not proof
that every native MP3/AC-3 delivery method fails; it fixes this tested path.
Compatible video can be copied while audio is converted by Linux.

## Local application changes and dependencies

Pinned versions: `research/reviews/stremio-versions.json`. The complete frontend
is built from official Stremio source, with a small remote player bar, HLS MIME
normalization, the tested HLS.js version, local URL-redacted error reporting,
and Vizio view transitions disabled. Service workers and unnecessary Cast/Apple
script tags are disabled. The owner's build omits the seasonal promo modal;
this does not remove Vizio system ads. Scripts and patches retain the changes.

The webview has no demonstrated Node/native runtime or TCP torrent engine.
Stremio-format streams containing `infoHash` need the Linux service in this
setup. Direct compatible HTTP(S) streams can play without that engine, but
the current frontend host must still be running. No claim is made that every
codec, container, multichannel format, DRM stream, or subtitle format works.
The Linux service detected no usable hardware transcoding profile; CPU
transcoding performance and 4K playback have not been established.

The initial foreground servers have been replaced by three enabled Linux user
services: `vizio-stremio-lab`, `vizio-stremio-engine`, and `vizio-stremio-watch`.
HTTP health/version checks pass and all three are active. Their logs are local
under `.private/service-logs`, not the shared system journal. The server
allowlists remain in effect. No TV flash, TV startup key, router change, DNS
filter, or firewall change has been made.

## Startup, login and ads

Read-only native Power menu inspection found “Input at Power On” set to
“Last Used TV Input”, with “SmartCast” as the other offered value. No custom
URL startup option was observed there. No setting was changed. This does not
prove that every possible startup hook is absent.

A dry-run observer saw explicit power values 1→0 at 16:08:58 local and 0→1 at
16:09:15 on November 1. Owner reported the PC desktop appeared first after
wake and Vizio Home looked normal. The live watcher is now enabled as a Linux
user service; owner confirmed the next remote off/on cycle opened Stremio
automatically. The log observed wake at 16:12:09 and accepted launch at 16:12:11
local time. It requires
an awake, logged-in Linux session and the same reachable addresses. Starting
the watcher does not launch. Network loss alone is never treated as standby.
Cold AC boot, Linux reboot/login behavior, and boot without an observed value
0 have not been validated. Native persistent startup remains unestablished.
The TV webview launch itself remains a transient method.

The owner reported that neither a Walmart sign-in prompt nor a TV advertisement
appeared during the tested remote off/on cycles. The owner is unsure whether
the TV is signed into Walmart. The custom app covers the normal interface while
open. Fresh account-free setup, account-free cold boot, and advertising behavior
across a complete daily-use cycle have not been verified; neither Walmart login
removal nor system ad removal is claimed.

Vizio's current [OS FAQ](https://www.vizio.com/en/vizio-os) states that a customer
account is required for Vizio OS. That general vendor statement is not proof
of this TV's current account state. Stremio's current
[download list](https://www.stremio.com/downloads) does not list a Vizio build.
Its Android launch-on-boot APK is not a demonstrated Vizio solution.

A browser-only WebTorrent alternative would not automatically solve raw
Torrentio streams: browser WebTorrent connects to WebRTC-capable peers rather
than ordinary TCP/uTP peers, per its [official FAQ](https://webtorrent.io/faq).
No broad independent-on-TV torrent path has been established by this work.

## Final user tests

The owner separately confirmed all of these on W4K65M-1031:

- Full Stremio legal-torrent video and sound after the worker/AAC fixes.
- Pause/resume, +10-second seek, English authored captions visibly rendered,
  Back closing the menu, and screen-filling video.
- Stremio opening automatically after remote standby/wake with Linux running.
- All eleven imported add-ons including Torrentio visible in the TV app.
- Remote keyboard entry, Search, Down reaching results with the keyboard closed.
- Torrentio video and sound for the original Night of the Living Dead (1968).

The original 1968 film's public-domain status is documented by
[Carnegie Mellon Libraries](https://www.library.cmu.edu/about/news/2018-10/all-ghouls-day-screening-carnival-souls-night-living-dead).
No stream from a different film or later remake was requested for this test.
Provider selection and audible output rely on the owner's report; the local
TV-peer beacons independently verify decoded video/audio, not the provider's
catalog identity. This is brief functional testing, not certification of every
source, full-length file, codec, resolution, or subtitle format.

Stremio documents that standalone Web lacks torrent downloading and conversion
of unsupported formats: <https://blog.stremio.com/using-stremio-service/>.
Those features require an external service unless a suitable on-TV runtime is
independently established. No such runtime is established here.

## Upstream research review

Repository: <https://github.com/vindeckyy/smartcast-backdoor>.
Reviewed commit: `aea6dec77bf3c6613c46b2ef45de5444e5f3dccc`.

- Author's TV is W4K65M-1030, SmartCast 1.8.1767.1. Firmware string matches
  the owner's set; model and SmartCast version differ.
- `pwn.py` performs normal pairing and NS 4 / app 3001 URL launch, but then
  requests an internal loopback token, sends that token to its beacon server,
  reads selected store keys, writes a marker, and restores Home. It also prints
  the pairing token when pairing. **That script was not executed.**
- This project's helper reimplements only the needed pairing, read-only
  control queries, page launch, and Home recovery. No internal token bootstrap,
  arbitrary config-store writes, namespace sweep, debug-console unlock, legacy
  `/install` payload, or firmware writes have been performed.
- The README's persistent-store claims concern surviving page/app lifecycle;
  its own footnote leaves reboot persistence untested. Store persistence does
  not establish automatic code startup.
- The URL launch reportedly ends on Home, app switching, or reboot. Home exit
  is confirmed here; app switching and reboot remain untested on this TV.
- The research does not establish root, a bootloader unlock, or a replacement
  operating system. Its firmware appendix describes encrypted/signed packaging,
  not an installation method. No replacement OS is assumed feasible.
- The README describes `tvapp/` and lifecycle wrapper files not present in the
  checked-out commit. Its claimed HLS app cannot be reviewed or reproduced
  from those absent files.
- The three bundled extracted JS files match the repository's advertised
  SHA-256 values. They are author-supplied artifacts, not owner-TV dumps.
- REA's static summary is in `research/reviews/rea-artifact-summary.json`.
  Partial semantic graph coverage is retained explicitly; no static result is
  being treated as a live TV observation.

Official Stremio source inspected at development commit
`c34935cc36e28c00ec15f066c38bbc6f6f59f716`. The direct-player route and
stream encoding were checked against upstream code; the running website may
use a different build. Public sample URLs encode only public test metadata,
never TV credentials.

## Standalone Home follow-up

The clear OFFLINE test confirmed current native-app launching and Home redirection
fail with all PC helpers stopped. Recovery succeeded. See
`research/reviews/pc-disconnect-repeat.json`. Wallpaper removal restored responsive
arrows according to the owner.

Normal PIN-paired read-only vendor configuration queries succeeded. They identify
the actual Home as local sctv/main.html (N2:A1 migrated to N4:A1). The previously
captured SCU loader manages updates, not proven custom-app installation. It was
never executed. Actual Home source, local installation, and boot registration
remain separate unresolved questions; see `standalone-launcher.md`.

The configured sctv entry and scripts and System UI index/scripts were captured
successfully. No supported executable-file write or persistent custom Home
registration emerged in this bounded inspection. REA semantic coverage is partial.
The service worker reviewed is a data worker, not demonstrated offline page
installation. See `research/reviews/owner-home-source-capture.json` and
`standalone-launcher.md`.

The HDMI API shortcut failed a specific follow-up test despite earlier broad
feedback. The current input setting is read-only. TV / HDMI now displays physical
Input → HDMI-2 instructions. Netflix/native-app launching and PC Home redirect
remain separate from that failed shortcut.

## November 1: TV-local storage and native registry progress

Runtime local-origin execution is verified. A disposable browser-sandbox file was
written, read back exactly, executed, and reopened with a TV-only inline file
loader after closing the test app. This is browser storage, not root/native
installation or a cold-start/Home hook. Direct filesystem URL navigation did not
unload the page; reading and rendering our own stored HTML worked.

Actual JavaScript WAMP bridge classes were recovered from runtime function source.
Registry hierarchy enumeration reached the platform orchestrator's app database,
and its read-only home_provider is `vizios-home`. This is a promising specific
lead, not proof that editing it would safely replace Home. No registry writes or
new native app-launch calls have been made. See owner-local-origin-results,
owner-local-storage-results, and owner-runtime-bridge-results review JSON.

Resume state, private evidence pointers and recovery are in docs/RESUME-HERE.md.
Source/docs archives and artifact hash manifests are private local checkpoints;
there has been no git publication or credential export.


## November 2: clarified actual-Home objective and evidence correction

The current objective is modification of the real installed Home implementation;
Stremio and separate launcher development are deferred. Browser techniques may
support investigation but do not satisfy the product goal. See
NATIVE-HOME-INVESTIGATION.md for bounded questions/tests and exact evidence limits.

The earlier statement in “Standalone Home follow-up” identifying sctv/main.html
as actual Home is superseded. That is a genuine legacy configuration/source
observation; the stronger app database and debug state-machine evidence identifies
vizios-home, Loki controller, app=home, bundles/home, reported v26.08.28.9. The
separate sctv definition uses browser controller. The language, renderer, loader
and real Home resources remain unknown; “native Home” does not mean all machine code.

No Home-provider write has run. It remains a secondary hypothesis with specific
approval required; rollback was only preflighted against unchanged state. No
appearance consumer, custom registration, real Home file replacement, signing
capability or persistence of a Home modification is established. Prototype file
retention/Netflix launch results remain valid within their original boundaries.

This pass reviewed retained evidence and changed docs only. No new device reads,
service changes, native writes, live worker calls or repeated REA analysis.


## November2: manufacturer archive and source-guided updater reads

Owner-provided5586L_FUR9.2.tar.gz matches both vendor checksums. Complete outer
and two relevant nested filename inventories are retained. Outer LOKI is fonts
only. Actual OSUpdater source was found and selected for static review; Home
renderer/templates and installed Loki-bundles package remain unacquired. Its
fixture filenames are format evidence only. Internal labels mix F/L and9.1/9.2,
so this is not proven identical to the owner build. Seven owner registry reads
corroborate selected updater keys/storage paths but returned no package locator.
No updater/rollback command, source credential, build/installer or native write
was executed. See OSS-ARCHIVE-REVIEW.md and vendor-5586l-fur92-review.json.


## November2: remaining SDK interfaces and log-status check

Three compiler and one ACR relink archive inventories completed. ACR supplied real
registry/Loki headers and two non-executable ARM32 library copies. REA portable
export inspection recorded1396dynamic exports on one library. No typed Home-file
export found in reviewed interfaces; generic message APIs do not establish server
command completeness or owner-build equality. Source-defined OSU logging flag read
was empty; no logging enabled/collected or live Loki command sent. No Ghidra needed
for this export/interface question. Next owner input is external-label hardware
identification only, case closed/no connections. See SDK-INTERFACE-REVIEW.md.


## November 2, 2026 — retail identification and hardware constraints

Owner supplied Walmart item16109363845, whose listing names retail65S4V4.
Research author reports same retail identifier but internal1030; owner remains1031.
No exact board/FCC/pin evidence obtained. Owner cannot access the rear label and
has no USB-to-TTL adapter; physical acquisition deferred. No TV requests, service
changes or native writes. See [retail review](RETAIL-HARDWARE-IDENTIFICATION.md).


## November 2, 2026 — owner rear-label correction

Owner removed TV from wall and supplied an exterior-label photo: actual model
**65S4V1**, superseding the prior listing-based65S4V4 assumption. Internal1031
unchanged. Contained transmitterFCC ID2AJVQ-MWH647B maps to a Wi-Fi/Bluetooth
module; no TV mainboard/UART identified. Raw photo stays private; no serial
transcribed. No case opening, TV requests, service changes or writes. See
[retail review](RETAIL-HARDWARE-IDENTIFICATION.md).


## November 2, 2026 — supplied USB firmware offline inspection

Suppliedmg1352-86.910.19.2-1F.utv(533,546,571bytes) has internally valid
RS512 JWT and leaf/intermediate signatures. No plaintext or Home bundle recovered.
REA whole-file entropy retained; chunk-size arithmetic gives16bytes difference
per declared block, unlike repo32-byte description. Owner confirms compatibility;
source/current-build equivalence not independently established. No update, TV
request or service change. Separate asset-decryptor source reviewed; matching
x509_pub.bin not acquired. See [UTV review](UTV-FIRMWARE-REVIEW.md).


## November 2, 2026 — concrete Qterics extractor and published-key trial

Found and reviewed unixtract commit aadba866ea47ed9506ffe130a8558bb9147ee968.
Source specifies RSA-OAEP-SHA1 and AES128-GCM with16-byte tags, consistent with
UTV size arithmetic. All21 distinct published keys fail on supplied MG1352.
Synthetic successful unwrap/GCM and corrupted-tag rejection verify local trial
reader. Maintainer names id.json/idpwe on another platform; no owner path/access
established. Seven existing archive indexes lack relevant named artifacts.
Asset verifier uses a PEM public-key file; earlier certificate shorthand corrected.
No TV operations/services/writes. Owner electronics experience asked before any
internal hardware proposal. See [follow-up](QTERICS-DECRYPTOR-FOLLOWUP.md).


## November 2, 2026 — interior photos, UART unidentified

Owner supplied ten interior photos and found no UART pinout visible. PCB reads
715GF461-M0B-T01-004I (0/O glyph ambiguous). No confirmed UART labels/pins/voltage;
CN8601 unidentified and C7xx pads are component footprints. Bounded exact-board
web searches and three saved source inventories found no exact identifier match
or usable schematic. Originals/hashes private. No measurements, powered-open test,
hookup, removal or TV changes. See [mainboard assessment](MAINBOARD-IDENTIFICATION.md).


## November 2, 2026 — return to PC hosting, direct Stremio shortcut

Owner parked native Home/hardware work and chose direct Stremio on physical Home.
PC frontend/engine healthy HTTP200. Watcher now honors startup screen for Home
as well as wake; enable-stremio config added. Eight isolated checks passed.
Configuration applied; watcher paused pending TV reassembled/on confirmation.
No live launch or new visual result yet. See [setup](PC-STREMIO-HOME.md).


## November 2, 2026 — replacement 1030 paired for PC-hosted Stremio

Replacement photo identifies W4K65M-1030 with
same firmware/software. SSDP matching Living Room at192.0.2.57; fresh certificate
and normal PIN pairing succeeded. Old credentials/identity saved privately;
never sent to replacement. Host/engine allowlists updated; authenticated GETs
and HTTP health checks pass. Input reads HDMI-3; PC port unconfirmed. Server-setup
launch accepted, visual feedback pending. Watcher paused. No new Home/playback
success claim or native Home/firmware write. Photo/serial retained privately.


## November 2, 2026 — WatchFree route, Torrentio, desktop controls and server power

Owner corrected remote target to WatchFree. Physical press observed stable
SMARTCAST4/3014 (transient1/51 ignored); enabled PC app-state redirect to Stremio.
Owner confirmed it opens. Home redirect disabled. Ten isolated scenarios and five
configuration transitions passed. All normal services active.

Torrentio-only transfer from owner's existing PC descriptor acknowledged by new
TV browser client; pre-import TV add-ons backed up. Old1031 records preserved.
Desktop Stremio TV panel installed/validated/visually reviewed/launched. Real
shortcut off/on and boot preference off/on passed; hosting stayed online.
User lingering enabled; Wi-Fi system autoconnect checked; all three units enabled
at boot with failure retries. Actual PC reboot not tested. Automatic sleep disabled
in Xfce/GNOME and persistent sleep:idle block inhibitor verified. Exact former
power settings saved privately; restore helper supplied. All hosting/shortcut
settings left online/enabled. See DESKTOP-CONTROL.md and validation reports.


## November 3, 2026 — player Home link, URL add-ons and bandwidth graph

Owner reported persistent bottom-right Home during playback and requested desktop
URL-based add-on management plus server bandwidth monitoring. Removed browse Home
link from DOM on player routes; retained auto-hiding player Home control. Five
Chrome checks passed, including author CSS overriding hidden. Prepared/rebuilt
frontend. TV list/install/remove verified with own sample add-on; original7
add-ons preserved. Desktop Add-ons tab masks URLs and checks TV confirmation;
nonce/expiry/Origin/source/identity protections tested. Overview chart uses only
server-process TCP counters with no persistent peer/media log, explicitly excluding
UDP. Actual traffic measured. Six local regression tests and GUI visual review
passed. No packages/firmware installed or GitHub upload. See DESKTOP-CONTROL.md and
research/reviews/controls-v2-live-validation.json. Full TV overlay visual follow-up
not yet reported. Hosting initially started for validation. Owner then explicitly requested it
remain stopped while testing controls. Clean stop actions confirmed, not crashes.
Services intentionally stopped; boot enablement and power prevention remain on.

## November 3 — floating Home removal follow-up (build12)

Owner reported the standalone Home box persists. Reproduced build11 failure
with isolated actual Chrome: history.pushState changes the player hash without
hashchange, so the catalog link stays mounted. Removed the standalone anchor
entirely, preserving the auto-hiding player-bar Home action. Webpack passed and
the compiled main.js contains no tv-clean-home; five updated Chrome route checks
show no floating Home. Server kept stopped pending owner response to reload
question. Existing live TV page needs reopening for new JavaScript; no claim of
TV visual success. See research/reviews/home-overlay-removal-validation.json.
