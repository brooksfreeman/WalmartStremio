# Remaining SDK/interface search — November 2, 2026

## Question and boundary

Can the remaining vendor compiler/relink archives supply the Loki/platform
headers referenced by OSUpdater, and document a read-only package/manifest or
native-file export interface? This is an acquisition investigation for actual
installed Home, not another launcher or a firmware modification.

Support: reviewed OSUpdater includes `loki.hpp`, `sysreg_wrap.h`,
`platformorchestrator.h`, and `ipc/connection.h`. Initial source inventories did
not supply these complete interfaces. Four explicit, previously uninspected
archive members were selected. No vendor scripts or compiled code ran.

## Completed inventories

| Selected component | Complete member inventory | Interface candidates |
| --- | ---: | --- |
| ACR relink archive |18,410| Nine matching headers |
| Toolchain2.50 |6,286| None matching the targeted names/paths |
| Fancyplayer toolchain |6,281| None matching the targeted names/paths |
| Toolchain1.32L |5,109| None matching the targeted names/paths |

The1.32L archive is named `.tar.xz` in the outer release but has gzip magic.
The first suffix-selected decoder rejected it before reading any member. The
scanner was corrected to inspect magic, and only this unfinished component was
resumed. Completed inventories were not repeated. Nested identities and indexes
remain under `.private/vendor-oss-5586l-fur92/sdk-archives/`; public summaries are
`research/reviews/vendor-sdk-*-inventory.json`.

Targeted interfaces were found under ACR's `_vsl_libs`:

- `include/vsl/sysreg_wrap.h` supplies a registry client wrapper.
- `loki_datasession/include/vsl/private/loki_datasession/Loki.hpp` declares
  generic messages/connections and provider-side sessions, including value-read,
  value-write and data-event callbacks. It describes itself as a modified form
  of `sysroot-vizio/loki-ipc/loki.hpp`.
- The other LokiDataSession/LokiProxy headers describe provider wrappers and
  callbacks. Their interface declarations do not supply a typed Home/file export
  operation or prove a server's entire command vocabulary.

## Native artifact evidence

Two ARM32 shared libraries were copied as non-executable analysis inputs from
the relink archive. The analyzed SDK copy is1,044,252bytes:
SHA256 `24a0ee81f80a4f8a1064abfaddd97ea181cdd8d2f61f1124191e18e32d004d5a`.
Both libraries contain debug information/symbols; no execution or attachment.

REA portable export inspection found1,396 defined dynamic exports, complete
within that table, without Ghidra. Parent Evidence:
`ev_ae438f32c9ecf49bdf7e594e7566d1cc0ad8c52ddf57fb2fdbb91b249a96accf`.
Summary Evidence:
`ev_2cd7188c86cc9387e195cb9ec15e26343b49a599b17eff749447cb0ba26b7c06`.
Complete two-record bundle saved as `.private/rea-sdk-interface-evidence.json`.
Earlier REA exports remain separate and unchanged.

Local demangled-symbol and exact-string review corroborates the declared Loki
message/session/provider interfaces. Protocol strings include newSession,
valueRead, valueWrite, dataEvent, setData and registerSessionProvider. These are
static observations, not a demonstrated safe client command or file-read API.
No decompilation or live Loki command was performed. No native engine session
was opened, and no Ghidra/dependency installation was needed for this question.

Limitations: only one of the two library variants received REA export analysis;
local/hidden/undefined symbols are outside the export table. Matching headers,
symbols or strings do not prove those versions are installed on the owner TV or
that an operation is reachable/safe. Absence of a typed export is not absence of
every possible server-side read interface. No Home renderer/bundle recovered.

## Existing-log route checked and stopped

Reviewed OSUpdater registers `/osu/logs`; `onValueRead("log")` returns its existing
buffer. Its constructor starts the reader only if
`/app/osu/ui-logging/enabled` is1, true or on. Default is disabled. It filters
`journalctl` to the OSUpdater service, not arbitrary Home logs.

Smallest useful owner-TV test: one SystemRegistry get of that source-defined
flag, five-second timeout, existing report cap. Expected outcome: if enabled,
validate exact consumer protocol before considering private log retrieval; if
empty/disabled/error, stop without enabling anything.

Result: fresh report arrived with no error and empty string. This does not meet
the reviewed source's enabled condition. No logging flag changed, logger started,
session opened, logs collected or update request made. Normal PC helpers restored
and diagnostic recovery timer canceled.

The research repository's public issues were checked once (up to30 requested;
one issue returned, about pre-authentication). No file-read/export route was
documented in that issue. No contact/message sent to its author.

## Next stage: identify hardware before any readout proposal

The bounded software check is complete. We still require actual owner-build Home
files or an evidenced export interface. Board identification is now a possible
next acquisition investigation; UART availability, voltage, accessible pins,
unlocked shell and readable flash are all unknown.

Follow-up: owner subsequently removed the TV from the wall and supplied its
rear-label photo: **65S4V1**, correcting the Walmart listing's65S4V4. Internal1031
remains unchanged. LabelFCC ID2AJVQ-MWH647B identifies a wireless module, not a
verified mainboard/pin map. No USB-to-TTL adapter owned. See
[the retail investigation](RETAIL-HARDWARE-IDENTIFICATION.md). Physical readout
remains deferred; no connection or case opening requested by this pass.

After identifying the hardware, assess actual manufacturer/regulatory/board
evidence for a read-only console or export route. Do not assume3.3V/115200 or an
unlocked UART from another model's report. Console output, if later acquired,
stays private. A boot log may identify resources but does not itself grant file
access. No bootloader interruption, command, flash probing, soldering, reset or
write is authorized merely by this identification step. Potentially unrecoverable
changes still need the exact proposal, recovery method/limits and owner approval.
