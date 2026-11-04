# Mainboard identification — photos reviewed

Updated November 2, 2026. Owner opened the rear cover and supplied ten interior
photos. Originals and SHA256 identities remain in
`.private/hardware-identification/mainboard/`. They contain serial/barcodes:
never publish or delegate them. Owner confirmed relevant electronics experience.
No USB-to-TTL adapter is owned.

## Findings

- PCB reads **715GF461-M0B-T01-004I**. Printed zero/O in M0B is visually
  ambiguous; final character read as uppercase I.
- Secondary label appears to read `Y3M650A04`, with `7505867 M9456`;
  these visual readings do not establish part compatibility.
- No confirmed UART/TX/RX/GND/DEBUG labels or pinout in the visible component-side
  photos. Owner also found no UART labels.
- Empty **CN8601** below the left-side harness is an unidentified optional
  connector footprint. Shape does not establish UART or signal directions.
- **C750/C748/C749/C751** pads are component footprints. Neighboring C/R/L/U/ZD
  designators are not evidence of a serial header.
- Installed aluminum heatsink hides chip markings. Storage type/location remains
  unconfirmed. Underside not photographed; no readout fixture identified.

Bounded exact-board and assembly web searches found no usable matching schematic
or pin map. Exact identifier searches in saved outer, ViziOS and firmware source
indexes found no matches. Generic UART kernel files do not identify physical
pads on this PCB. Negative scope is bounded; UART absence is not established.
See `research/reviews/mainboard-identification.json`.

## Limits and next evidence

No measurements, powered-open test, probing, hookup, soldering, board/heatsink or
shield removal, bootloader interaction or native write was performed. Do not
assign pins, voltage or baud from another board or promise an unlocked shell.
Matching service documentation or another evidenced acquisition route is needed
before a connection proposal. No removal request is justified merely to repeat
the uncertainty.

Actual Home plaintext and native file access remain missing; the 21 published
Qterics keys did not unwrap the supplied image. See
[Qterics follow-up](QTERICS-DECRYPTOR-FOLLOWUP.md).
