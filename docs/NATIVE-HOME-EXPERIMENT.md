# Prepared Home-provider routing experiment — not run, deprioritized

November2 objective clarification prioritizes understanding and modifying the
real installed Home implementation. This experiment remains a **secondary
routing hypothesis**, not the next investigation. It does not establish Home
appearance editing or custom-app registration. See NATIVE-HOME-INVESTIGATION.md.

The original specific approval requirement remains. No native write has occurred;
rollback was only preflighted against an unchanged value, not after rerouting
Home. Browser-file and Netflix results do not validate this experiment.

Exact proposed change:

- Key: `/app/platformorchestrator/appsdatabase/home_provider`
- Original, read on this TV and privately backed up: `vizios-home`
- Temporary value: `netflix`, an existing app ID from this TV's app database
- Trigger SmartCast and observe app state for ten seconds, then restore original.
- Do not reboot, change startup/last-input settings, replace app maps, or delete OEM files.

The field may be a diagnostic mirror. No recovered source proves it controls
Home, and native setter permissions have not been tested. A successful set/get
alone will not establish that Home routing works.

## Recovery

Before any write, the controller arms a separate user-systemd timer to invoke
the recovery script after 75 seconds, even if the main process stops. The main
process also restores in `finally`. The page has a secondary 45-second timer,
which is insufficient by itself because switching apps can destroy the page.

Recovery launches a browser page through the already paired control API, then
sets this same key to `vizios-home` only if its value is `netflix`. An unexpected
value is left alone. It reads the original value back before claiming restoration.
The recovery transport has been preflighted while the original value was already
present; that path performed reads only. It has **not** been proven after changing
native routing. If the TV's browser/control services stop responding, this method
may fail. No firmware dump or guaranteed hardware recovery is available.

Manual recovery, with this PC and lab service available:

```bash
python3 scripts/native_home_policy.py --bind 192.0.2.24 restore
```

The test has a separate explicit CLI guard and is awaiting the owner's approval
under the original boundary for potentially unrecoverable writes. Do not invoke
the `test` operation until that specific approval has been received. Preflight is
read-only and safe to repeat after pausing the Home watcher.

## Validation already completed

- TV preflight: current `vizios-home` backed up locally.
- Independent recovery page: same value read; no setter invoked.
- CLI refuses test without its explicit approval flag, before issuing a write.
- Six isolated JavaScript checks passed: preflight and no-op restore do not set;
  unexpected baseline and missing permit do not set; apply touches only the fixed
  key/value; both rollback paths restore the original in the mock environment.
- HTTP permit requires the TV IP, local TV origin, current operation, nonce and
  unexpired local permit. A PC request spoofing that origin was rejected403.

No native registry writes have been executed. Results belong in
`research/reviews/native-home-policy-read-results.json`; raw reports/backup remain
ignored under `.private/`.
