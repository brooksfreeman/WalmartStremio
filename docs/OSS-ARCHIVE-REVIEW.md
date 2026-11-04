# Manufacturer FUR9.2 archive review — November 2, 2026

Question: does the owner's downloaded manufacturer source archive supply the
actual Home renderer, Loki bundle loader, or an evidenced package acquisition path?

## Identity and inspected scope

Owner supplied `5586L_FUR9.2.tar.gz` in the project root: 6,738,959,096 bytes.
Published SHA1 and MD5 both match Vizio's repository checksums. Recorded SHA256:
`5bc7e3646fa6130ce8538cab26046427770560a7c5025d20de75ecb8a6234ea5`.
See research/reviews/vendor-5586l-fur92-archive-identity.json.

The archive remains at the supplied path and is excluded from git. Selected
inert files, complete member indexes and nested archive identities remain under
ignored `.private/vendor-oss-5586l-fur92/`. No worker received this directory.

- Outer archive: complete inventory of296 members.
- Referenced ViziOS GPL archive: complete inventory of183,533 members.
- Referenced MediaTek firmware OSS archive: complete inventory of452,384 members.
-577 small, relevant source/documentation files copied as non-executable files,
  1,744,493 bytes total, with per-file hashes and guarded path handling.
- In this initial review, remaining embedded third-party/toolchain/ACR archives
  were not recursively searched. Subsequent toolchain/ACR inventories and native
  interface findings are recorded separately in SDK-INTERFACE-REVIEW.md. Filename inventories and selected-source review are bounded evidence,
  not a proof about every byte of every embedded dependency.

No build scripts, Dockerfiles, native programs, updater commands, remote manifest
requests or firmware installation actions ran. No dependencies/Ghidra installed.

## Findings

1. The outer `LOKI/` directory contains exactly five fonts. It supplies neither
   Loki engine source nor Home templates at that location.
2. `CONJURE/README.md` describes FFmpeg dependencies. `SCPL/README.md` describes
   Python dependencies, not the proprietary control service implementation.
3. The ViziOS archive contains actual C++ OSUpdater source, registry adapters,
   manifest parser, package cleanup/validation support, and Loki command handling.
   These provide useful platform leads, not the Home renderer.
4. Updater production code recognizes the `vizio-app-{name}_{version}_armhf.snap`
   artifact convention. Its test fixtures separately name `vizio-app-loki` and
   `vizio-app-loki-bundles`. Fixture versions/names are **not** confirmed installed
   filenames on this TV. No matching Home snap or bundle body was acquired.
5. The scanned member names contain no `BundleRoot.xml`, `vizios-home` or
   `bundles/home`. Selected updater source does not supply the Home layout,
   Home-key handler or home_provider consumer. Broad candidate matches in Boost,
   compression tools and compiler/kernel sysreg tests are unrelated names.
6. Root build documentation/scripts produce partial GPL/rootfs/storaged outputs.
   They do not establish a complete build of the retail TV, a signing bypass,
   an install route or a recovery image. Developer README instructions assume
   root SSH/SCP access that has not been established on the owner TV.
7. Release-label consistency is imperfect: outer directory is5586L FUR9.2,
   root README says5586F, and the referenced ViziOS archive/SCPL notes sayFUR9.1.
   Valid vendor checksums do not resolve exact source-to-running-build equivalence.

Useful source references, relative to retained `selected-source/`:

- `rootfs/OSUpdater/osu/src/osu_path_cleaner/impl/osu_path_cleaner.cpp:19`
  artifact naming convention; corresponding tests name separate Loki packages.
- `rootfs/OSUpdater/osu/src/manifest/impl/manifest_parser.cpp:22`
  JSON manifest content and SC-CONFIG/SC-ASSETS references. This parser alone
  does not establish the complete integrity/signature-validation chain.
- `rootfs/OSUpdater/osu/src/osu_path_manager/impl/osu_path_manager.cpp:18`
  A/B OSU storage paths and current-path selection.
- `rootfs/OSUpdater/osu/src/manifest/impl/manifest_info_storage.cpp:7`
  manifestInfo is summary/status data, not a full downloadable package manifest.
- `rootfs/OSUpdater/osu/src/commands/loki_command_handler.cpp:19`
  even a Loki value-read callback can perform an update check; generic Loki
  commands must not be treated as harmless registry getters. None invoked.

## Source-guided owner-TV cross-check

Question: do the updater's published keys exist on this TV and expose an exact
installed package/manifest locator? Evidence: cached owner `/app` enumeration
includes `osu`, plus explicit key definitions in reviewed source.

Smallest tests completed, using the fixed read-only registry probe:

- Enumerate `/app/osu`; get source-defined manifestHash and manifestVersion.
- Get activeFolder; enumerate discovered manifest and dlm children.
- Get the one discovered `/app/osu/dlm/updates` value.

All seven reports arrived without errors. Hash/version are populated, and the
active folder matches a source-defined OSU storage location. `manifest` exposes
only `url`; `dlm` exposes only `updates`, whose value is empty. Raw version/hash/
path responses remain private. These corroborate source/runtime relationships,
not complete build equality. The `manifest/url` source is an environment selector;
it is not a direct package URL. No updater command, registry setter or request
using embedded source credentials was made.

Stopping condition reached: seven bounded reads returned no package locator or
manifest body. No guessed native filesystem paths were fetched and no flags
were changed. Normal helper services restored active, HTTP health200 verified,
independent diagnostic recovery timer canceled.

## Remaining acquisition blocker

We need the actual installed Home/Loki-bundles package, its entry resources, or
an owner-build manifest that provides exact artifact references. Current access
demonstrates registry reads and browser storage; it does not demonstrate reading
arbitrary native files, replacing snaps or root SSH access.

The next acquisition investigation must start from a concrete export/read
interface, a supplied native package/filesystem dump, or an evidenced artifact
reference. This archive did not establish one. Do not substitute launchers,
guess file-server paths, use example package URLs as owner artifacts, enable
debugging blindly or infer recovery from the developer README. The prepared
home_provider routing experiment remains deprioritized and separately gated.

Recoverable appearance editing remains unresolved until the real Home consumer
and storage/validation/restore path are acquired. No Home modification claimed.
