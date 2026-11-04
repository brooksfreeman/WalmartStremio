# PC-hosted Stremio with the WatchFree remote shortcut

Current November2,2026 setup is **WatchFree → Stremio**, physically verified by
owner on replacement W4K65M-1030. This supersedes the earlier Home-button choice.
Home redirect is disabled. See [desktop controls](DESKTOP-CONTROL.md).

PC serves frontend8099 and engine11470. Watcher detects SMARTCAST namespace4/app3014,
the stable state observed after owner pressed WatchFree and confirmed its screen.
It opens `/stremio/#/`; owner confirmed the physical-button flow. Opening WatchFree
by another route also redirects. Initial state never launches by itself; cooldown,
pause and HDMI/other-app guards remain. No firmware or remote-key rewrite.

All three normal user services are running/enabled at boot. Desktop **Stremio TV**
provides persistent on/off control and health checks. Normal input selection can
return to the PC; its HDMI port on the replacement has not been confirmed. Do not
reuse the old TV's HDMI-2 assumption. Current replacement reported HDMI-3 selected.

CLI configuration alternatives:

```bash
python3 scripts/configure_home.py enable-watchfree
python3 scripts/configure_home.py disable-watchfree
```

These change local configuration only. The desktop toggle additionally starts/
stops and enables/disables the watcher for persistent behavior. Stop observer
immediately using `systemctl --user stop vizio-stremio-watch.service`.

Historical `enable` selects clean-launcher Home/wake behavior, `enable-stremio`
selects Home/wake direct Stremio, and `disable-redirect` disables both app-state
shortcuts. These are alternatives, not the active WatchFree configuration.

Replacement pairing and original identity are stored separately privately.
Owner confirmed Stremio appears and works after completing TV setup. Server setup
was accepted. Torrentio-only transfer was acknowledged by its TV browser client.
This does not establish compatibility of every stream format or provider.
