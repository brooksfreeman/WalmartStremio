# Retail hardware identification — November 2, 2026

## Current owner-unit identification

The owner subsequently removed the TV from the wall and supplied an exterior
rear-label photograph. The case has not been opened as part of this investigation.
The actual label supersedes the earlier Walmart-listing-based model assumption:

| Evidence | Identifier | Meaning/limit |
| --- | --- | --- |
| Owner rear label | **65S4V1** | Actual exterior model marking |
| Owner runtime/settings | **W4K65M-1031** | Internal software identity |
| Owner rear label | **2AJVQ-MWH647B** | Explicitly a contained transmitter-module FCC ID |
| Owner rear label | Intertek4002603, UL62368-1 | Safety marking; not a mainboard or debug-pin identification |
| Supplied Walmart item16109363845 | **65S4V4** | Current listing title; does not override owner label |

Settings photo confirms firmware86.920.9.3-2 and software86.920.9.3-2.12.
Owner still has no USB-to-TTL adapter. Rear photo is preserved privately at
`.private/hardware-identification/owner-rear-label.jpg`, with private digest/size
in `identity.json`. It contains serial/barcodes; none are transcribed here or
used in searches. No raw image is included in public documentation/checkpoints.

## Public reference check

- [Supplied Walmart listing](https://www.walmart.com/ip/16109363845) currently
  names65S4V4. Its account requirement is a retailer statement, not a new test
  of the owner's login state or proof of bypass.
- [Original research](https://github.com/vindeckyy/smartcast-backdoor) reports
  retail65S4V4/internalW4K65M-1030. The owner is now label65S4V1/internal1031.
  Neither identical retail model nor identical board should be asserted.
- [Applicant's MWH647B user-manual exhibit metadata](https://fccid.io/2AJVQ-MWH647B/User-Manual/User-Manual-7910007)
  identifies a WiFi/BT module; FCC attachment7910007.
- [Applicant manual text mirror](https://device.report/manual/15292677) describes
  the TV Wi-Fi module and the required external host label stating that it
  contains the transmitter. This aligns with the owner's label. The module's
  manufacturer is not evidence of the TV mainboard's manufacturer.
- [Internal-photo exhibit metadata](https://fccid.io/2AJVQ-MWH647B/Internal-Photos/Internal-Photo-7910005)
  is for this module, not an identified owner-TV mainboard. Its PDF contents
  were not acquired. The manual PDF link also timed out; no PDF analysis claimed.

Bounded searches of65S4V1 for manuals, service/mainboard and manufacturer support
references did not acquire an exact owner-board diagram or readout procedure.
Other search results included reseller/import/AI repair pages; these were not
adopted as technical or hardware-provenance evidence. The earlier65S4V4 public
lookup likewise provided no exact1031 board. No support form was submitted.

## Consequence and next acquisition question

The exterior identity is now known. The photo does not establish a mainboard
part number, UART availability/pins/voltage, unlocked console, flash readability
or native Home resource access. No adapter purchase or connection is recommended
without a demonstrated acquisition procedure. Case opening, probing, soldering,
bootloader interruption and native writes were not requested or performed here.

Actual installed Home bundle/source remains missing. Further acquisition must
start from a specific new artifact, documented export interface, observed resource
reference or model-matched board evidence. Do not repeat completed archive scans
or log-status tests. Preserve successful owner-TV prototype tests as their own
scope; they do not establish modification of installed Home.

This pass made no TV-control requests, service changes or native writes. Service
state was not rechecked and previous service observations remain historical.
