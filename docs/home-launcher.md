# Stremio tile on Vizio Home

## Clean start-screen follow-up

The owner subsequently requested a stripped-down screen with only app launchers
and no ads or data collection. A separate local clean launcher is implemented at
`/launcher.html` with eleven buttons: Stremio, Netflix, Hulu, HBO Max, Disney+,
YouTube TV, YouTube, Prime Video, Paramount+, Peacock, and Apple TV. TV / HDMI
provides recovery. Browser preview and navigation across the three rows passed.
Opening Stremio and its new Home-link return passed in the browser. The owner
reported that the initial two-app TV screen, remote navigation, Netflix launch,
and physical Home/Input exit seemed to work, but correctly noted there was no
easy return to our launcher. After adding the Home redirect, the owner replied
“everything seems to work” to the app-launch / Home-return / TV-HDMI test.
This verifies the overall flow by owner report; the reply did not enumerate
each app tried, so an exhaustive per-app test is not claimed.

Startup now selects the clean launcher. A PC-side Home redirect is also enabled
and owner verified, described below. This is not a tile installed in
stock Vizio Home and does not replace its firmware or remove its Home app.

The clean page loads only local HTML, CSS, and JavaScript. Its CSP prohibits
third-party resources and connections. It has no analytics, activity beacons,
browser-storage writes, ads, recommendations, or external fonts. Server page/media
event logging is now disabled by default; `--diagnostics` explicitly opts in.
The app-launch endpoint requires the local Origin and existing LAN allowlist,
and accepts only the ten reviewed native app actions or HDMI-exit action. It never accepts arbitrary
URLs, app IDs, namespaces, or settings from a client.

Native descriptors are pinned from Vizio's public app-name/availability feeds;
hashes, selections, and per-app limits are in `research/reviews/launcher-app-catalog.json`.
No catalog download or remote image request occurs during normal launcher use.
The TV reports SOC 1 / chipset 9. The author's companion artifact maps this to
MTK 5586; Prime uses the feed's MT5586 override (firmware minimum 86.700.0.0),
rather than the older wildcard payload. Mapping is static evidence, not a new
native dump. Netflix uses namespace 3 / app 1; the initial successful owner test
used an empty MESSAGE, while the expanded catalog uses canonical null MESSAGE.
Stremio opens the tested local full client in the same webview.

### Physical Home return: observed state and opt-in redirect

A read-only, owner-coordinated observation recorded:

| Visible state in the test | Current input | Current app |
| --- | --- | --- |
| PC HDMI | HDMI-2 | namespace 0 / app 2 |
| Vizio Home | SMARTCAST | namespace 4 / app 1 |
| Returned to PC | HDMI-2 | namespace 0 / app 2 |

The owner confirmed Vizio Home appeared. Earlier app 0/2 alone was ambiguous;
the combined Home state provides a narrower match. The observer made only GETs.

`watch_power.py` now optionally redirects only a newly observed SMARTCAST +
namespace 4 / app 1 state to `/launcher.html`. It excludes HDMI, running native
apps, and our modal app 4/3001. It never launches from the process's initial
sample, has a five-second cooldown, and does not infer Home or power-off from a
failed read. Matching was checked against HDMI, custom page, Netflix, and HBO
states. The owner initially estimated roughly three seconds of Vizio Home,
then about two seconds in the follow-up app/return test, before our screen.
The watcher accepted Home launches at
17:04:09 and 17:04:23 America/New_York on November 1, 2026. This verifies the
redirect, not prevention of the initial Vizio Home display. No claim of removing
its ads or underlying activity applies. The owner reported that the subsequent
app-launch / Home-return / TV-HDMI flow seemed to work, without itemizing apps.

TV / HDMI now pauses redirects for 12 seconds, closes the modal through the
reviewed Home descriptor, and selects the observed HDMI-2 using the normal input
API with a fresh hash and read-back. The input was validated in the TV's input
list; the owner reported the overall return flow worked. Physical Input remains independent.
See `docs/recovery.md` for immediate disable commands. No TV app registry,
bootloader, or firmware was changed for this redirect.

### Privacy settings actually changed

Normal menu reads found Viewing Data **On**, Limited Ad Tracking **Off**.
`scripts/privacy_settings.py apply` changed only those observed `T_LIST_V1`
toggles using fresh hash values, then read back Viewing Data **Off**, Limited
Ad Tracking **On**. Results: `research/reviews/privacy-settings-result.json`.
Original values are saved privately for an explicit restore. No advertiser-ID
reset, arbitrary store write, account change, DNS change, or firewall rule was used.

Vizio's [Viewing Data Supplement](https://www.vizio.com/en/terms/privacy-policy/viewing-data-privacy-policy)
says disabling Viewing Data does not disable Activity Data collection. Its
[Ads & Privacy FAQ](https://www.vizio.com/en/terms/privacy-policy/ads-and-privacy-faq)
describes Limited Ad Tracking as a targeted-ad preference, not removal of ads.
There has been no traffic capture proving zero TV telemetry. Native apps such as
Netflix retain their own network behavior and data collection. A clean visual
launcher is therefore not proof of a telemetry-free TV.

## Stock Home tile investigation

Investigated November 1, 2026 for the owner's W4K65M-1031, firmware
86.920.9.3-2. A native Home tile has **not been created**. No app registry,
app registrations, or firmware were changed. Normal privacy toggle changes
are recorded separately above.

## Evidence and limits

- Vizio's current [Home Screen FAQ](https://www.vizio.com/en/home-screen)
  describes adding apps from its Apps menu and arranging them. It does not
  document pinning an arbitrary URL or importing a local app manifest.
- Stremio's current [download list](https://www.stremio.com/downloads) lists
  supported TV platforms but no Vizio build. Our working app is the locally
  adapted Stremio Web client, not an app registered in Vizio's catalog.
- The pinned smartcast-backdoor README explicitly says the modal URL launch
  does not register a Home-screen app and ends on Home, reboot, or app switching
  (README line 318 at commit aea6dec77bf3c6613c46b2ef45de5444e5f3dccc).
- Static inspection of the author's extracted companion-lib.js found separate
  app-launch/current-app helpers and a `vizioAppsList` reader that obtains
  `VIZIOApps` through the configuration property reader. This is not evidence
  of a user-install API, a custom Home-row schema, or a safe registration write.
  No values were written. These artifacts came from the research repository;
  they are not a dump of this owner's Home application.
- The available extracted artifacts are companion-lib.js, uml-bundle.js, and
  apiTestApp.js. They do not establish how the current TV's Home catalog can
  be extended. A bounded inspection cannot prove that every possible private
  mechanism is absent.

## Current usable route

PC-assisted automatic launch after remote off/on is already owner verified.
It remains enabled. A genuine, manually selectable Stremio tile on the stock
Vizio Home screen remains unresolved; the transient page launch should not
be described as one.

Further registration work would need evidence of the Home app's registration
format and a reversible, validated write path before modifying it. Guessing a
configuration key or repurposing another app's ID is not a demonstrated method.

The earlier REA graph was not retained on the current MCP connection. A local
REA CLI trace reused the exported complete Evidence inline. Its exact `VIZIOApps`
seed had no match in the partial graph; this does not prove feature absence.
The trace summary is `research/reviews/home-launcher-trace-summary.json`; the
direct inert-text observations above are separate evidence.

## HDMI shortcut correction

Follow-up read-back tests on November 1 found the normal current_input setting
read-only and the setter rejected. TV / HDMI now displays physical Input → HDMI-2
instructions; it does not claim to switch automatically. App launch/Home feedback
earlier was broad and does not override this specific failed switch test.
