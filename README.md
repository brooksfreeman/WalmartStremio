# WalmartStremio

Linux-hosted Stremio for Vizio TVs, with a WatchFree remote-button shortcut,
desktop server controls, add-on management, and bandwidth monitoring.

**Experimental, model-specific project:** tested on the owner’s W4K65M-1030.
Windows support and compatibility with other models are not established.
This is not a turnkey installer. A Linux PC is required for hosting.

**Public source copy:** local paths and LAN addresses below are examples.
Replace `/path/to/WalmartStremio`, `/home/your-user`, and `192.0.2.*` with
your own values before setup. Existing service files are templates; do not
install them unchanged. Credentials, paired-device identity, add-on URLs,
raw captures, firmware archives, and compiled Stremio builds are excluded.
Historical validation reports describe the original setup, not your machine.

Start with [build notes](docs/stremio-build.md) and
[desktop controls](docs/DESKTOP-CONTROL.md).
See [third-party notices](THIRD_PARTY_NOTICES.md) and [GPLv2](LICENSE).

Owner-authorized setup for replacement **W4K65M-1030**. Original research began
November 1, 2026 on a different W4K65M-1031.

**Current setup:** the replacement TV's **WatchFree button opens PC-hosted
Stremio**. Owner physically verified it. Home stays normal. Native Home editing
and hardware work are parked.

Double-click **Stremio TV** on the PC desktop to check server status, toggle the
WatchFree shortcut, control startup at boot, restart hosting, or open Stremio on
the TV. Its **Overview** tab has a live server bandwidth graph; **Add-ons** lets
you paste an Install link/manifest URL, install it, refresh the TV list and remove
selected add-ons. Configured URLs remain private. All three hosting services are configured to start at boot using
user lingering. Wi-Fi autoconnect is enabled and system-wide. Automatic sleep is
disabled with a persistent sleep/idle blocker. Torrentio was transferred from the
owner's existing PC configuration and verified present by the replacement TV.

Replacement W4K65M-1030 is separately PIN-paired at192.0.2.57. Old1031 evidence
and credentials remain private and historical. See
[desktop/server controls](docs/DESKTOP-CONTROL.md) and
[WatchFree setup](docs/PC-STREMIO-HOME.md).

Start with [the current handoff](docs/RESUME-HERE.md) and
[the Home evidence and bounded investigation plan](docs/NATIVE-HOME-INVESTIGATION.md).
Follow [AGENTS.md](AGENTS.md) and preserve its private-context boundary.

## Preserved native Home investigation on the retired 1031 (parked)

Owner-TV runtime app definitions and app-manager state identify `vizios-home`,
Loki controller, `app=home`, `bundle=bundles/home`. Deployer and Loki metadata
report Home version `v26.08.28.9`. This identifies the managed Home app, **not its
implementation language or renderer**. Physical Home dispatch and startup's
consumer are not yet traced.

The highest-value missing evidence is the matching Home deployment descriptor,
entry resources and loader relationship. No actual Loki Home bundle/source has
been acquired. The four-read metadata investigation completed without a bundle locator.
The manufacturer5586L FUR9.2 archive was supplied and verified. Its LOKI folder
contains fonts; the nested ViziOS source includes OSUpdater, but no matching
Home renderer or bundle has been acquired in the inspected scope. Seven
source-guided owner-TV metadata reads provided no artifact download reference.
Exact build matching remains unproven. See [the archive review](docs/OSS-ARCHIVE-REVIEW.md).
No Home settings were written and no launcher work resumed. The subsequent
[SDK/interface pass](docs/SDK-INTERFACE-REVIEW.md) recovered Loki headers and a
native client library, but no confirmed Home-file export route. External hardware
identification now confirms rear-label model **65S4V1**, correcting the supplied
Walmart listing's65S4V4. The label identifies transmitter module2AJVQ-MWH647B,
not the mainboard. No USB-to-TTL adapter is owned and no exact1031 board/readout
procedure is established. See [the retail check](docs/RETAIL-HARDWARE-IDENTIFICATION.md).
UART/root access is not established; actual Home acquisition remains unresolved.

Owner subsequently supplied a533MB USB UTV image. Its signed metadata identifies
86.910.19.2-1F; internal signatures verify, but the payload remains opaque and no
Home files were extracted. Owner confirms compatibility; download provenance,
exact model policy and current-build equivalence were not independently verified.
See [the offline firmware review](docs/UTV-FIRMWARE-REVIEW.md). No flashing or TV
operations occurred. Decryption/unpacked-resource acquisition remains necessary.
The [Qterics follow-up](docs/QTERICS-DECRYPTOR-FOLLOWUP.md) found a concrete
open-source format implementation and tested21 published keys: none matched.
No native file access or owner Home plaintext established. Mainboard/readout
feasibility remains unknown. Owner confirms relevant electronics experience;
[interior photos](docs/MAINBOARD-IDENTIFICATION.md) now identify PCB
**715GF461-M0B-T01-004I** (0/O glyph ambiguous). No UART pinout, voltage or
usable console has been identified; visible empty footprints are insufficient.

The [home_provider experiment](docs/NATIVE-HOME-EXPERIMENT.md) is preserved as an
untested, secondary routing hypothesis. It is deprioritized and still requires
specific approval. Its rollback was preflighted only against an unchanged value;
it does not establish appearance editing or custom-app registration.

Before persistent native changes, present the exact modification, backup and
restore method, and recovery limits. Obtain approval before potentially
unrecoverable writes. No arbitrary flashing, erasure or bootloader changes are
authorized by the clarified objective.

## Preserved prototype results and superseded assumptions

A separate eleven-app browser launcher and adapted Stremio playback were tested.
Its own browser-sandbox file survived power loss, and Netflix launched through
local REST with PC helpers stopped. These results are preserved; browser storage
is not an installed Home bundle. They did not meet the former native-editing objective.

Legacy SCTV/System UI web assets were captured. Earlier text treating SCTV as the
active Home source is superseded by the stronger Loki app-manager evidence.
Readable resources do not establish permission to replace them. Accepted launch
responses or app-state changes do not establish visible success.

Viewing Data Off and Limited Ad Tracking On were read back. Hidden advertising
or absence of an ad in a short test does not establish that background tracking
has stopped. No OEM Home resource, native registry value, firmware or bootloader
has been changed in the native investigation.

Historical work remains in [the findings ledger](docs/findings.md),
[earlier installation research](docs/native-installation.md),
[launcher notes](docs/home-launcher.md), and [Stremio notes](docs/stremio-build.md).
Pre-clarification README and handoff are preserved under `docs/history/`.

## Project and recovery

- `research/reviews/`: sanitized findings, artifact identities and REA evidence references.
- `.private/`: credentials, raw device captures, account/add-on configuration and
  full evidence; ignored, directory0700/files0600. Never worker context.
- `scripts/`, `web/`, `client/`: existing diagnostic/prototype tools, not a Home redesign.
- [Recovery instructions](docs/recovery.md) and [REA setup](docs/rea-setup.md).
- [CodexSaver status](docs/codexsaver.md): affected live delegation paths must not
  run until the reported command-execution/context-isolation issues are demonstrably resolved.

The TV also displays this PC. Physical **Input → the PC-connected HDMI port** returns to the desktop.
HDMI-2 was the old TV; replacement photo/API show HDMI-3 selected, but its PC
cable connection has not been confirmed.
Do not infer current helper-service or TV state from old saved observations.
Credentials and pinned TV identity remain local; do not paste private responses
or credential files into chats, worker context, issues or public repositories.

`scripts/save_checkpoint.py` saves source/docs/public reports and a private
artifact hash manifest. `.private/checkpoints/latest.json` points to the latest
local checkpoint. Raw private artifacts remain in place; this is not a firmware
backup, whole-machine backup or guaranteed hardware recovery image.
