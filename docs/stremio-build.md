# Reproduce the local TV build

November3 / logical tvbuild12: standalone floating Home link removed entirely.
Owner still saw it with build11; isolated Chrome reproduced the gap when React
Router navigated using pushState without a hashchange event. All five updated
Chrome route checks show no floating link; compiled main.js has no tv-clean-home.
Auto-hiding player controls retain their Home action. Reopen Stremio to load the
updated bundle; rebuilding does not modify a page already running on the TV.

November3 / logical tvbuild11: Home browse link is removed entirely on player
routes, preventing author CSS from overriding hidden. TVAddonManager adds desktop
URL-based installation/list/removal with TV verification. Tests and private URL
handling are documented in [desktop controls](DESKTOP-CONTROL.md).

November 2: owner resumed PC hosting and chose physical Home → direct Stremio.
See [current shortcut setup](PC-STREMIO-HOME.md). Historical launcher behavior
below remains context; Home redirection now follows the configured startup screen.

The current private working tree is `.private/stremio-tv-src`; the pinned
upstream checkout is `research/upstream/stremio-web`. Versions and public
source URLs are in `research/reviews/stremio-versions.json`.

With Node from `/home/your-user/.local/bin` available in PATH, install the locked
dependencies in the private tree:

```bash
npx --yes pnpm@11.8.0 install --frozen-lockfile --ignore-scripts
```

From the project directory, apply the owner adaptations:

```bash
python3 scripts/prepare_stremio_tv.py
```

Then run `npx --yes pnpm@11.8.0 run build` **inside the private Stremio source
directory**. The lab server serves its `build` child at `/stremio/`; it never
serves the source, node_modules, or the rest of `.private`.

The preparation script checks each expected patch location and fails rather
than guessing against a different source version. It copies `client/TVRemoteBar.js`
and `client/TVRuntime.js`. Dependency-file changes replace the inode to avoid
modifying pnpm's shared package store. Existing source patches are retained in
`research/reviews/`. A new upstream version requires a fresh review.

Launch the app at `http://<PC_IP>:8099/stremio/#/`. Put route/query parameters
after `#`, for example `#/settings?streamingServerUrl=...`. The upstream
SearchParamsHandler concatenates document-level search onto route-level search;
mixing both can accidentally append a document query to the server URL.

## Remote behavior

- During playback, Up/Down shows the purple control bar; Left/Right moves
  focus; OK activates. With the bar hidden, OK toggles playback.
- Back first closes an open player menu, then hides the purple bar. Browse
  leaves playback for the catalog. In build 10, Home opens the clean local
  launcher; the physical Home/Input buttons remain the TV escape.
- On pages and setup dialogs, arrows move among visible focusable controls;
  a white outline marks focus. OK activates. Native text fields retain their
  own editing behavior.
- Open server configuration and add-on installation as separate steps: their
  independent focus locks compete when both are requested simultaneously.
- The TV supplies no keypad for Stremio's text input. The owner build adds a
  search keyboard: enter Search to open it, arrows move, OK types, Space and
  Backspace edit, Search submits, and Back/Close dismisses it. After submitting,
  Down moves toward results; OK on the search field reopens the keyboard.
  Owner verified typing, submission and result navigation on TV after fixing
  an initial focus-reopening bug. It does not log entered text in lab events.

## Existing add-on import

Eleven cached add-on descriptors, including Torrentio, were read from the
owner's existing Linux Flatpak local-storage profile in read-only SQLite mode.
Only `manifest`, `transportUrl`, and `flags` were copied. No auth, password,
account settings, library, streams, search history, or watched history was
copied. Existing TV add-ons were backed up privately first. The import uses
the same `Ctx / InstallAddon` core action as Stremio's normal UI.

The one-use import endpoint admits only the TV IP and exact local page Origin,
requires POST, and is not exposed through the static asset server. A negative
test verified that even this PC with the correct Origin receives 403. The TV
client verified all eleven descriptor URLs in app state before acknowledging;
the server then moved the pending private file to completed. Only counts were
logged. Owner also saw Torrentio listed on the TV. Replaying the import URL
after completion does not expose or reinstall the private payload.

`scripts/import_addons.py` can prepare another import from that same profile,
but do not run it casually: addon transport URLs may contain credentials.
All import/backup files are 0600 under the 0700 ignored `.private` directory.
Frontend route analytics calls are disabled in this owner build. This does
not disable third-party add-on network requests needed for ordinary use.

Direct requests to Torrentio from this session were blocked. The import used
existing local metadata, not a proxy around that block. Torrentio stream
playback was separately verified by the owner through normal TV use with the
original Night of the Living Dead (1968): video and sound worked. This result
does not imply that every Torrentio provider or file format works.

## PC-assisted startup services

Build 10 adds an on-screen Home link outside playback and a player Home button
that open `/launcher.html`. Back from the root catalog also opens that page.
The previous owner-verified build is retained in
`.private/stremio-build-before-clean-home` for rollback. These new return paths
still require owner TV verification; prior playback/control results apply to
build 9. Startup is now configured for the clean launcher, and the owner verified
a PC-assisted redirect from physical Home to that launcher after roughly three
seconds. Vizio Home remains the initial destination; it was not replaced.

The page host no longer records routine page/media events by default.
`--diagnostics` opts in to private local event logging when troubleshooting.

`scripts/watch_power.py` has been installed as a Linux user service after a
dry run observed explicit TV values 1→0→1. A subsequent live off/on cycle
automatically opened Stremio, confirmed by the owner. Cold AC boot remains untested.
It launches only after explicitly observing value 0 followed by 1. It never
treats network loss as power-off and does not launch when first started.
Standby returned 0 in the remote off/on test. If a different power-loss case
becomes unreachable without returning 0, this observer will not relaunch.

```bash
python3 scripts/watch_power.py --bind <PC_IP> --dry-run
```

Three units live in `~/.config/systemd/user/` and are enabled for the user's
default target: `vizio-stremio-lab.service`, `vizio-stremio-engine.service`, and
`vizio-stremio-watch.service`. Prepared copies are in `config/systemd`.
`scripts/install_services.py` reproduces them and backs up any same-name
existing units privately before replacement; it does not itself enable them.
`service_entry.py` sends output only to private local logs. No root service or
user lingering was enabled. Operation requires the user session, awake PC,
and known LAN addresses; logout, suspension, IP changes, or cold power loss
without a reported 0 have not been solved by this setup.

The optional Home redirect now launches the clean page when the observed
SMARTCAST + Home-app state appears, excluding running apps and HDMI. This was
owner verified. A new off→on transition also launches the configured start page.
This can cover the PC HDMI desktop after TV wake; stop only the watcher
for monitor use, leaving manual launches available:

```bash
systemctl --user stop vizio-stremio-watch.service
systemctl --user start vizio-stremio-watch.service
```

See `docs/recovery.md` for disabling all user services. This is external
automation, not native persistent installation on the TV.
