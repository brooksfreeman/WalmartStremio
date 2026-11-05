# WalmartStremio

**Use Stremio on a compatible Vizio TV, with your Linux PC doing the hosting.**
Press the TV remote’s **WatchFree** button to open Stremio. Use the remote to
browse, search and control playback. A desktop app on the PC lets you start or
stop the server, manage add-ons and view streaming bandwidth.

The PC must stay on, awake and connected to the same network as the TV while
you watch. This project does not install Stremio directly into the TV’s firmware.

**[Installation guide](docs/INSTALLATION.md)** ·
**[Which files do what?](docs/FILE-GUIDE.md)** ·
**[Troubleshooting](docs/INSTALLATION.md#troubleshooting)**

## What you get

- Stremio in the TV’s built-in browser, adapted for remote-control navigation.
- A WatchFree shortcut that opens it without typing a web address.
- An on-screen search keyboard and remote-friendly playback controls.
- A **Stremio TV** desktop panel with server controls, add-on installation/removal,
  automatic-startup settings and a live bandwidth graph.
- Optional background hosting that starts when the PC boots.

You supply your own add-ons and any accounts they require. This repository does
not provide a movie library, subscriptions or anyone else’s add-on configuration.

## How it works

1. **Your PC runs the app and streaming server.** It hosts an adapted version of
   Stremio Web and the Stremio media engine.
2. **Your TV displays the app.** The TV opens the PC-hosted page in its browser;
   an HDMI connection is not required for this streaming setup.
3. **A small background program watches for WatchFree.** When the TV enters the
   WatchFree app, the PC asks it to open Stremio instead. There may be a brief delay.
4. **The desktop panel controls the PC services.** Closing the panel leaves
   hosting running; choosing **Stop server** stops it.

The shortcut detects the WatchFree app opening, rather than changing the remote’s
firmware. Opening WatchFree another way also triggers it. Turn the shortcut off
to use WatchFree normally. The physical Home button still opens the normal TV
Home screen. No rooting, TV disassembly or firmware flashing is part of setup.

## Will it work with my setup?

| Requirement | Current support |
| --- | --- |
| TV | Tested on Vizio internal model **W4K65M-1030**, firmware `86.920.9.3-2` |
| PC | Tested on **Linux Mint 22.3, x86-64, Xfce 4.18**, with systemd and GTK 3 |
| Network | PC and TV must reach each other on the same LAN; stable IP addresses needed |
| Windows / macOS | No supported installation path yet |
| Other Vizio models | Unverified; the same brand or screen size does not guarantee compatibility |

This is an experimental source project, not a one-click installer. Setup involves
a terminal, pairing the TV, building the frontend and installing background
services. Playback, the WatchFree shortcut and desktop controls have worked on
the existing setup. **A fresh installation on a second PC and a complete reboot
of that installation have not been verified.** The latest playback-overlay fix
passed browser checks; final TV visual confirmation is still pending.

## Start here

Follow the **[installation guide](docs/INSTALLATION.md)** in order. It covers:

1. Installing the Linux tools and downloading this project.
2. Finding the PC and TV addresses and pairing with the TV’s PIN.
3. Building Stremio and starting the media server.
4. Opening it on the TV and enabling the WatchFree shortcut.
5. Installing the desktop panel, adding add-ons and enabling boot startup.
6. Troubleshooting, updating and uninstalling.

You do not need the firmware research or diagnostic experiments to install the
working app.

## Working software versus research

The folders contain both current software and earlier experiments. **Do not run
every script in `scripts/`; use only the commands in the installation guide.**

| Location | What it contains |
| --- | --- |
| [`client/`](client/) | Working TV interface additions: remote controls, search keyboard and add-on integration |
| [`scripts/`](scripts/) | Server, pairing, desktop and setup tools **mixed with research utilities**; see the file guide for the distinction |
| [`web/`](web/) | Shared player library, optional browser launcher and diagnostic pages; not the complete Stremio frontend |
| [`config/`](config/) | Desktop icon and service files; setup regenerates the three host-service files for your PC |
| [`tests/`](tests/) | Local regression tests for add-on management and bandwidth measurement |
| [`research/reviews/`](research/reviews/) | Research summaries, earlier validation results and saved source patches; not an installer |
| [`docs/`](docs/) | The installation/file guides plus technical notes and historical investigation records |
| `.private/` (created locally) | Your pairing credentials, downloaded source/build, engine, settings and logs; excluded from GitHub |

**[The full file guide](docs/FILE-GUIDE.md)** lists the current tools and identifies
the experimental ones. Some older documents discuss native Home replacement,
firmware inspection or a Home-button shortcut. Those describe earlier work,
not the current WatchFree installation procedure.

## Research background

The project also preserves investigations into ViziOS, TV app launching and
native Home behavior. Native Home replacement and hardware/firmware work are
not completed features. Those records are optional reading:

- [Research findings](docs/findings.md)
- [Native Home investigation](docs/NATIVE-HOME-INVESTIGATION.md)
- [Technical build notes](docs/stremio-build.md)

The [maintainer handoff](docs/RESUME-HERE.md) is for continuing development, not
for first-time installation. Historical reports may contain example paths,
addresses and observations that do not apply to your TV.

## License and private data

See [GPLv2](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md).
This is an independent project, unaffiliated with Vizio, Walmart or Stremio.

Keep `.private/`, `.env`, `.tv_auth`, PINs, tokens and configured add-on URLs out
of public uploads. When asking for help, include your model, firmware, Linux
version and a redacted error message—not private logs or account configuration.
