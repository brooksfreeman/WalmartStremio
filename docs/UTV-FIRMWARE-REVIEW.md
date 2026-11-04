# Supplied USB firmware — November 2, 2026

Follow-up: [the concrete Qterics implementation and key trial](QTERICS-DECRYPTOR-FOLLOWUP.md)
identified an AES-GCM recipe consistent with the16-byte per-block difference.
All21 published keys failed to unwrap this UTV; no plaintext. That later source
review supersedes the initial lack of a candidate cipher implementation below.

## Result

The supplied UTV is a signed-metadata container with an opaque payload. Its JWT
and leaf-certificate signatures are internally consistent. **No filesystem,
installed Home bundle, native executable or plaintext was extracted.** Nothing
was sent to the TV, installed, flashed, downgraded or executed from the image.
The pasted USB installation instructions were treated as reference, not a request
to perform an update.

Owner supplied root file `mg1352-86.910.19.2-1F.utv`, 533,546,571bytes.
SHA256 `5eccf0374f7d89fb8f33ed763338095a7d58ccd202dde95abb198d9f78b1e9a1`.
The input is git-ignored and preserved unchanged. Owner subsequently explicitly
confirmed compatibility. Its download source/vendor checksum was not supplied;
independent model compatibility and download provenance remain unverified here.

## Local observations

`scripts/inspect_utv.py` is an offline bounded-header parser and streaming digest
reader. It uses the existing Python cryptography installation; no dependency
installation, firmware code execution or certificate URL fetching. Public report:
`research/reviews/utv-mg1352-inspection.json`.

| Field | Observed |
| --- | --- |
| Prefix | Big-endian32-bit JWT length7367 |
| JWT algorithm | RS512 |
| Subject/update name |86.910.19.2-1F |
| Internal package name |mt5586_upgrade_image_ota.pkg |
| Package identifier |82113; opd00199D1352, interpretation not established |
| Declared block size |5,242,880bytes |
| Declared size |533,537,568bytes |
| Actual bytes after JWT |533,539,200bytes, at offset7371 |
| Key field |256decoded bytes; no unwrapped key obtained |
| Download URL claim |Empty |
| JWT signature with included leaf |Valid |
| Leaf signature with included intermediate |Valid; issuer/subject match |

Leaf: Qterics `updates.support.supportview.com`, RSA2048, valid2018–2038.
Intermediate: Qterics Production CA-1, RSA4096, valid2014–2044. No independently
trusted root or external provenance was established. Signature consistency does
not authenticate the entire opaque payload; its plaintext digest is unverified.
The SHA256 of the bytes after the JWT does not equal the declared `hsh`; this
comparison alone is **not** evidence of corruption because the report describes
`hsh` as a plaintext digest. No plaintext was available to test that meaning.

The JWT audience has seven versions from86.804 through86.910.19.1-2. Installed
owner version86.920.9.3-2 is absent. The file identifies86.910.19.2-1F, not the
installed86.920.9.3-2. Do not call this the latest owner-build firmware, infer a
safe downgrade, or reject the owner's compatibility confirmation solely from
this list; the complete updater policy/model mapping is unavailable.

## REA inspection and layout limit

REA `inspect_byte_entropy` read the entire file at65,536-byte blocks:8142blocks,
file entropy8.0000bits/byte rounded, one high-entropy run. Entropy cannot distinguish
compression from encryption. This supports only opaque/high-entropy classification.

Parent Evidence `ev_63b3dc44ba2a51e16f07382c0f49390fe4f9dbb0ff874c87ae9dd51cb84677db`;
summary `ev_852901569c341962279f3ce0345a3b5c26537efdca583caa12e947808f7c34cb`.
Complete retained bundle `.private/rea-utv-inspection-evidence.json` has4records
(including earlier SDK records). Header bytes retained in `.private/utv-mg1352/`.
No native engine session opened. No Ghidra needed: no executable recovered.
REA's advertised Binwalk firmware route caps input at128MiB and Binwalk is not
installed; this533MB file was not submitted to that incompatible route. No
signature-scan or filesystem-absence claim is made from entropy alone.

There are101full declared blocks plus one tail. Actual payload minus `siz` is
1632bytes =102×16. This is **16bytes per declared block if distributed uniformly**.
It differs from the research README's32-byte per-chunk description for a different
file. It does not prove what those bytes mean (IV, padding, other framing), where
they occur, or which AES mode is used. No speculative stripping/decryption was
presented as extraction.

## External research versus this artifact

[Original research Appendix A](https://github.com/vindeckyy/smartcast-backdoor#appendix-a-ota-firmware-container-format)
describes a different image, `mg1359-86.920.9.3-2F.utv`, size533,808,696 and
SHA256ea0b66768ee6ba8a4ca06e0aaf7a3b2722b2ec7fa0c92c35d1187443938cc0c7.
That file was not supplied/downloaded in this pass; none of its hash/length/layout
facts are substituted for the owner-supplied1352 artifact.

The author reports an RSA-wrapped AES key and requires device-side private
material for decryption, which they did not obtain. This is an external report,
not recovered cipher code or proof of key location/access on the owner's1031.
Their proposed UART voltage/baud and 'guaranteed' key-access wording remain
unverified and are not instructions for this owner unit.

## Source-guided alternative checked

The already-extracted manufacturer OSUpdater source was queried, not rebuilt or
executed. Its `unpacker/src/decrypt.cpp` hashes the configured PEM public-key
file bytes and splits SHA256 into IV/key; `data_stream_decryptor_proxy.cpp` uses AES128
CBC and `decrypt.cpp` treats a trailing256bytes as a signature. This is a
**different asset envelope**, not evidence that a certificate can unwrap this
UTV's key. Reviewed selected source had no RS512/JWT/Qterics unwrap match.

`osu/src/common/common.cpp` names `x509_pub.bin` at source-defined platform paths.
Queries of the two existing full archive indexes found only unrelated OpenSSL/
kernel x509 source names, no exact `x509_pub.bin` artifact. No archive rescans,
guessed certificate decryption, vendor embedded-credential use, TV native decrypt
command or filesystem write occurred. An exact matching asset certificate could
make the previously retained localassets envelope a separate offline lead; no
such certificate was acquired and actual Home inclusion remains unknown.

## Next acquisition requirement and recovery

Retain this UTV for comparison. A candidate decryptor recipe is now available;
necessary matching key material, an already-unpacked image or an evidenced readable
Home bundle is still needed before Home resource analysis. A public signing certificate is not
the private unwrap key. Do not flash or downgrade to try to obtain file access.

Source/docs/public report are checkpointed, while the original533MB input, private
header and REA evidence remain local with recorded identities. This is not an
owner-TV firmware backup, installable custom image or guaranteed recovery method.
No TV state was changed, so no TV rollback is required for this offline pass.
