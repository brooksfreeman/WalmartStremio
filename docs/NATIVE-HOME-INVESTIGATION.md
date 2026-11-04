# Actual Vizio Home: evidence and investigation plan

Objective clarified by the owner on November 2, 2026: reverse engineer and modify
the real installed Vizio Home, preserving a recoverable route. Prioritize the
existing implementation over creating another OS. Modifying HTML/JavaScript
actually used by installed Home can qualify; an unrelated browser page, overlay
or PC redirect cannot. Stremio is deferred.

## What the owner TV establishes

Target: W4K65M-1031, firmware86.920.9.3-2, software86.920.9.3-2.12. These are
retained observations from November1, not a fresh November2 version check.

| Question | Evidence from this TV | Remaining boundary |
| --- | --- | --- |
| Which Home is selected? | PlatformOrchestrator app map identifies `vizios-home`, alias `spock://homePage`, controller `loki`, parameters `app=home`, `bundle=bundles/home`; legacy descriptor N4:A1. `home_provider` reads `vizios-home`. | A registry name/value alone does not prove how a consumer interprets writes. |
| Is this only an unused definition? | App manager debug state shows the same Home as an actual managed app, suspended while a browser diagnostic is active. It records a Spock request with comment `Target app closed, going to Home`. | This corroborates runtime participation and fallback lifecycle, not the full physical Home-key or startup call chain. |
| Which Home version? | Deployer appVersionMap and Loki bundle_version both report `v26.08.28.9`. | No corresponding bundle archive, manifest, entry source or loader implementation acquired. |
| What language/rendering system? | Home uses the Loki controller. The separate `sctv` definition uses browser controller and `/scfs/sctv/main.html`. Actual browser-side JavaScript WAMP wrappers were recovered. | Neither controller name nor JS bridge proves Home is entirely machine code, HTML/JS or declarative UI. Bridge source is not Home source. |
| What handles Home/startup? | Physical Home visibly opens OEM Home. The state machine exposes Spock/app-manager involvement in fallback; alias and provider are observed. Owner configured startup to last HDMI. | Physical key dispatch, boot selection, authoritative settings consumer and Home entry execution are not traced. No startup setting changed. |
| Where do layout/content/ads come from? | Enumerated branches include `/loki/home/catalog-services`, `/loki/home/live-hero`, `/app/loki/home/apps`, and named partner rows. | Names are leads only. No actual renderer, layout model, recommendation/advertising data contract or telemetry path identified. |
| What can we change? | Our own browser-sandbox files are writable and survive power loss. Normal Viewing Data/Limit Ad Tracking settings were read back. | No installed Home resource replacement, native registry write, package re-signing, native filesystem write or persistent Home edit demonstrated. Browser persistence is separate. |

Evidence index:

- `research/reviews/native-home-policy-read-results.json`: runtime/version reads;
  precise raw state-machine report remains private at
  `.private/loopback-registry-debug_platformorchestrator_appmanager_state_machine-get.json`.
- `research/reviews/owner-runtime-bridge-results.json`: source identities and REA
  bridge parent `ev_b1fd97073600b8e97e3968bb60e5ab66685d89d9b1d3491a379fc374554ce80e`;
  graph partial, referenced WAMP implementation missing. Reuse rather than
  repeat unchanged analysis.
- `.private/owner-app-database.json` and version reports are retained owner
  evidence; never worker context. No raw private maps reproduced in public docs.
- `research/reviews/owner-home-source-capture.json`: readable legacy SCTV/System
  UI assets, explicitly not proof of the current Loki Home implementation.
- `research/reviews/native-localassets-acquisition.json`: opaque vendor object;
  not identified as the matching Loki Home bundle or decrypted firmware.

## Highest-value missing evidence

The deployment descriptor/manifest and actual entry resources for
`bundles/home` version `v26.08.28.9`, including their loader relationship. These
could identify code format, resource paths, data consumers and validation rules.
A native service binary is needed only if the relevant consumer is compiled and
cannot be established from accessible bundle/loader resources. Do not assume
machine code or install Ghidra before acquiring an appropriate artifact.

The present blocker is **missing matching Home bundle/loader artifacts and an
evidenced acquisition locator**. Signing and native write access are additional
unknowns, not demonstrated obstacles with known checks. Root, shell, ADB,
bootloader unlock and a hardware recovery interface are not established.

## Completed bounded investigation: deployment metadata (November 2)

**Question:** do already-discovered owner-build deployment/content metadata
expose a real Home resource locator or manifest, rather than just version/status?

**Supporting evidence:** exact runtime app identity, matching version reports,
and successful read-only SystemRegistry operations on this TV. Existing captured
enumerations establish each path below. Cached vendor AppConfigs review did not
yield an authoritative Home source; do not repeat that unchanged search.

**Smallest useful test, completed November2:** a single read-only local-origin
probe, using the browser solely as an investigation tool:

1. Get `/app/loki/deployer/active`.
2. Enumerate `/app/loki/home/apps`.
3. Enumerate `/loki/home/catalog-services`.
4. Enumerate `/loki/home/live-hero`.

Use the existing read-only registry transport with a fixed path/method allowlist,
five-second per-read deadline and200KiB per-result cap. No guessed paths, generic
Loki messages, debug enablement, registry setters, bundle execution, service
worker registration or update calls. Keep raw results private and report only
sanitized structure, artifact identities and conclusions. If the TV surface is
needed, pause the PC redirect with its independent recovery timer and restore it
afterward. No readiness question is necessary for routine work; ask only for
physical interaction/feedback if required. This plan itself changes no services.

**Distinguishing outcomes:**

- A concrete descriptor/path/URL is returned: first check its relation to Home
  and this version. Follow at most three explicit metadata references. Acquire
  at most one descriptor (512KiB) and one selected entry resource (16MiB), as
  inert bytes, with identity hashes and content-type/magic checks. A read does
  not establish replacement permission or that the resource executes.
- Only booleans, app IDs, row state or configuration child names appear: record
  this scope as metadata-only. Content branch names may inform a later focused
  question but do not establish a renderer or a modification path.
- Timeout/access denial/oversized response: retain the bounded result and stop
  that path. Do not turn a failed read into a write/debug/install attempt.

**Stopping condition:** after these four reads and, only if supported, the three
reference follow-ups. If no locator emerges, state the unresolved blocker:
we need a matching bundle/manifest export, readable loader/filesystem artifact,
or an evidenced recovery/debug acquisition interface. Do not invent a bundle URL,
repeat broad enumeration, or substitute a new browser launcher.


**Observed outcome:** all four reports arrived without errors. Deployment active
returned an empty string. Apps enumerated seven list/order fields. Catalog-services
enumerated seven URL-type fields. Live-hero returned no children. No concrete
Home descriptor/path/URL. This path stopped as metadata-only. A subsequent
three-read question found default app list=340 strings; full app record exceeded
the report cap and was stopped; catalog-url-type was empty. No renderer or
modification consumer established. See native-home-resource-discovery.json.

## New acquisition lead: manufacturer FUR9.2 source archive

Archive supplied and inspected November2. Published SHA1/MD5 match. The outer
LOKI directory has five fonts; referenced ViziOS source includes OSUpdater and
its package/manifest code, not a matching Home renderer. Two nested inventories
completed. Seven source-guided owner-TV metadata reads returned no artifact URL.
Exact source/build equality is not proven. See docs/OSS-ARCHIVE-REVIEW.md and
research/reviews/vendor-5586l-fur92-review.json for identities, inspected scope,
source references, runtime evidence and unsearched embedded archives.

The acquisition blocker remains an actual Home/Loki-bundles package or manifest
through an evidenced read/export interface or supplied native artifact. No native
filesystem read, signing capability or independent hardware recovery is established.
Do not repeat unchanged archive scans, guess paths or substitute a browser UI.

## Remaining SDK pass completed; hardware identification pending

See SDK-INTERFACE-REVIEW.md. Four explicit remaining archives were inventoried;
ACR relink material supplies Loki/registry headers and a native services library.
Static interface/export review found no typed Home-file export. A source-defined
logging flag read on the owner TV was empty, so that route stopped without
logging enablement or collection. No destructive/live Loki command sent.

Next is external hardware identification, with case closed and no connections.
Owner has been asked for rear-label product/hardware/FCC identifiers (excluding
serial/MAC) and adapter availability. Board/pin/voltage/console/recovery facts must
be established before any physical readout proposal. No UART/root assumption.

## Subsequent investigations, gated by evidence

| Investigation/question | Supporting evidence | Smallest useful test and outcomes | Stop condition |
| --- | --- | --- | --- |
| What receives physical Home and selects startup? | Runtime Home alias/provider; Spock fallback request; last-HDMI owner setting. | Trace exact entry references in acquired loader/controller source. If runtime correlation is needed, one bounded observation around a physical Home press, with redirects paused, can distinguish the requested app transition; it cannot alone identify the handler code. Separate boot policy from Home-key dispatch. | If the handler is in an unavailable service, name that service/artifact rather than inferring a writable binding. No cold-boot/setting changes solely to fill a source gap. |
| What renders layout, apps, recommendations and ads? | Matching entry resources once acquired; current branch names are only leads. | Trace one actual UI element/row to its resource/config consumer and referenced data source. If necessary inspect one relevant response privately; show code consumer plus runtime correlation. Server data versus bundled UI versus a compiled consumer are distinct outcomes. | Stop at unavailable code/data contracts; do not reuse SCTV behavior as Loki proof or collect unrelated personal traffic. |
| What modification is accepted and recoverable? | A demonstrated consumer plus actual resource storage/validation implementation. None yet. | Determine permissions, integrity/signature checks, backup scope and independent restore method from actual artifacts. Propose one appearance-only change to an existing element, such as its color, only after locating the real resource. No write merely to probe arbitrary keys. | Before any persistent native change, present exact byte/key change, backup/restore and recovery limits; obtain approval for potentially unrecoverable writes. If signing, write access or recovery is missing, identify precisely which capability is absent. |
| Does a minimal real-Home change persist? | An approved, visibly confirmed modification with verified restoration. None yet. | Compare hashes and visible behavior after normal restart, then cold boot; investigate update replacement rules from the package loader. Future ordinary updates need separate evidence; do not force a firmware update for this test. | Claim only tested lifecycle scope. A retained file or accepted API response is insufficient. |
| Does removing ads also stop tracking? | Actual Home ad and telemetry consumers/data flows, not just UI state. | Evaluate appearance and background requests separately after a confirmed Home modification. | No claim of tracking elimination from hidden rows or existing privacy-menu values alone. |

## Superseded assumptions and preserved work

- Installing a separate launcher, solving its cold-start path or resuming
  Stremio is no longer the target. Those prototypes and test evidence remain
  useful diagnostics and historical functional results.
- Earlier text calling SCTV the actual Home source is superseded by the stronger
  owner app-manager/Loki evidence. Legacy files remain genuine captured bytes.
- Calling Loki Home “native” means the installed system app in this project;
  it does **not** establish a machine-code-only implementation.
- A73-app registry map is not proof of the visible catalog's renderer/data feed.
- `home_provider` is a secondary, untested routing hypothesis. It does not
  establish appearance editing or custom-app registration. The prepared
  experiment is deprioritized and still needs specific approval. Rollback was
  only preflighted against the unchanged original value; see
  `docs/NATIVE-HOME-EXPERIMENT.md`.
- No OEM Home resource has been replaced. Hiding advertisements, disabling a
  menu option, or seeing no ad during a short test does not prove tracking stopped.

## Worker boundary

Keep live investigation, native/security decisions, private capture review and
device/network/service operations in Codex. The owner reports unsafe installed
CodexSaver paths: direct verification may run worker commands with `shell=True`
in the real workspace; work-packet copying may include private paths. These have
not been demonstrated fixed. Do not use affected live paths or treat prompts,
gitignore, forbidden patch paths, Pi tools-disabled mode or dry runs as enforced
isolation. Continue directly; tooling repair is separate work.
