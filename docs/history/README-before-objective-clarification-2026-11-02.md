# Vizio OS / Stremio investigation

Owner-authorized work on W4K65M-1031. Started November 1, 2026.

**Resume later:** [current handoff and next tests](docs/RESUME-HERE.md).
Newest TV-local storage results: [evidence](research/reviews/owner-local-storage-results.json).
A self-contained launcher is now saved in the TV browser sandbox. The owner
confirmed Netflix opens through its TV-local REST path in a helper-off test.
Physical Home, startup, and Stremio still depend on the earlier PC setup.
See [latest launch evidence](research/reviews/tv-local-rest-native-launch-test.json).

**CodexSaver:** [project setup and private DeepSeek key entry](docs/codexsaver.md).

**Active objective:** install everything on the TV and replace OEM Home without
the PC. The current PC-assisted prototype does not achieve it. Native service /
installation investigation is the priority: see [native installation](docs/native-installation.md).

The TV has loaded a custom page and played licensed video with sound in an
adapted **full Stremio Web app**. Player Back and Browse now work after local
fixes. Normal add-on installation and licensed torrent-backed TV video/audio
are also verified through the Linux streaming service.
The owner's eleven existing add-ons, including Torrentio, are imported. Remote
search, Torrentio video/audio, captions, seeking, and pause/resume passed owner
tests on the TV.
**This currently requires the Linux PC to host the app. Native installation,
independent torrent operation, and native startup have not been established.
PC-assisted automatic launch after remote off/on is verified and enabled.**
The owner saw neither a Walmart sign-in prompt nor a TV advertisement during
those off/on tests. Account-free setup and permanent ad removal remain unverified.

A [clean local start screen](docs/home-launcher.md) now has all eleven requested
app buttons. The owner verified that pressing physical Home shows Vizio Home
for about two to three seconds, then our launcher. The owner reported the
app-launch / Home-return / TV-HDMI test seemed to work, without listing every
app tried. Netflix was also confirmed in the initial test.
Startup is configured for the clean launcher. Vizio Home remains installed;
the PC performs the redirect.
Viewing Data is now Off and Limited Ad Tracking On, verified by normal-menu
read-back. This does not stop all Vizio or streaming-app data collection.
Routine local page/media event logging is disabled by default.

The owner's wallpaper was applied, then removed from the page at their request
to compare arrow responsiveness. The owner confirmed arrows are responsive
again; the image remains disabled and its original is untouched. A
[standalone launcher investigation](docs/standalone-launcher.md) is open:
owner-TV runtime inspection completed; the explicit helper-disconnect test
confirmed that app launching and Home redirection currently require the PC.
The current setup still depends on Linux; Android installation and a native
local Home replacement have not been demonstrated.

See [the findings ledger](docs/findings.md), [setup record](docs/rea-setup.md),
[architecture](docs/architecture.md), and [recovery instructions](docs/recovery.md).
These distinguish measurements
on this TV from claims made by upstream research.

## Project layout

- `scripts/tvctl.py`: certificate-pinned control requests, normal PIN pairing,
  explicit webview launch, and Home recovery. No configuration-store writes.
- `scripts/serve_lab.py`: allowlisted lab assets and media; admits only this PC
  and the selected TV. It never serves the project directory.
- `web/`: remote-navigation and playback diagnostics; authored test captions.
- `client/` and `scripts/prepare_stremio_tv.py`: reproducible Stremio adaptations.
- `scripts/stremio_service.py`: verified official Linux streaming engine,
  extracted privately with an IP allowlist; optional for direct HLS playback.
- `research/reviews/`: retained source identities and REA analysis summary.
- `research/upstream/`: unmodified upstream checkouts, ignored by git.
- `.private/`: credentials, TV identity, detailed responses, events, media,
  setup diagnostics, and complete REA evidence. Ignored by git; directory 0700.

## Routine commands

Run these from this project directory:

```bash
python3 scripts/tvctl.py capabilities
python3 scripts/tvctl.py current
python3 scripts/tvctl.py home
python3 scripts/open_stremio.py --bind <LINUX_LAN_IP>
python3 scripts/open_stremio.py --bind <LINUX_LAN_IP> --screen sample
systemctl --user stop vizio-stremio-watch.service
systemctl --user start vizio-stremio-watch.service
```

The current paired address and pinned certificate live in `.private/tv.json`.
Do not paste `.private/credentials.json` or other private files into a chat,
issue, or public repository. Pairing credentials are not placed in HTML,
JavaScript, command-line arguments, or HTTP access logs.

The page host, Linux engine, and wake observer now run as enabled user services.
Local pages and raw-torrent playback require this PC to remain awake and
reachable. Launching a remotely hosted application is a separate
test and does not establish persistence through Home or reboot.

See [the Stremio build and controls guide](docs/stremio-build.md) for reproducing
the frontend, configuring the Linux engine, and the installed power observer.
The TV is also this PC's monitor: read test
instructions before launching, because the TV app temporarily covers HDMI.
The page server is already running as a user service; stop that unit before
starting a foreground `serve_lab.py` instance for diagnosis. Keep this project
at its current path, or regenerate/reinstall the units after moving it.
